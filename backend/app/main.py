import os
import uuid
import threading
import subprocess
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from app.schemas import DownloadRequest
from yt_dlp import YoutubeDL
from urllib.parse import urlparse

app = FastAPI(title="Video/Audio Downloader", description="Download videos and audio from any URL with quality selection")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

# Use a writable temp directory by default for container friendliness
DOWNLOAD_DIR = os.getenv('DOWNLOAD_DIR', '/tmp/downloads')
if not os.path.isabs(DOWNLOAD_DIR):
    DOWNLOAD_DIR = os.path.abspath(DOWNLOAD_DIR)
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# Storage backend: 'local' (default) or 'gcs' for Google Cloud Storage
STORAGE_TYPE = os.getenv('STORAGE_TYPE', 'local').lower()
GCS_BUCKET = os.getenv('GCS_BUCKET')

# In-memory task storage
tasks = {}
tasks_lock = threading.Lock()

def validate_url(url: str) -> bool:
    """Validate URL is properly formed"""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

def download_worker(task_id, url, media_type, quality):
    """Download video/audio with correct format selection"""
    try:
        with tasks_lock:
            tasks[task_id]['state'] = 'DOWNLOADING'
        
        ydl_opts = {
            'outtmpl': os.path.join(DOWNLOAD_DIR, '%(id)s_%(height)sp.%(ext)s') if media_type == 'video' else os.path.join(DOWNLOAD_DIR, '%(id)s.%(ext)s'),
            'noplaylist': True,
            'quiet': False,
            'no_warnings': False,
            'socket_timeout': 30,
            'retries': 3,
            'skip_unavailable_fragments': True,
            'fragment_retries': 3,
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
        }

        # Performance tuning: enable concurrent fragment downloads and resume
        ydl_opts.update({
            'noprogress': True,
            'continuedl': True,
            # Increased concurrent fragment downloads for higher throughput
            # (keep reasonable to avoid fragment storm)
            'concurrent_fragment_downloads': 16,
            # Allow more retries for fragments
            'fragment_retries': 8,
        })

        # No external segmented downloader configured (aria2 removed)
        
        if media_type == 'video':
            # Proper video format selection with fallback
            if quality == '1080p':
                # Prefer combined best video+audio up to 1080p, fallback to best under 1080p
                ydl_opts['format'] = 'bestvideo[height<=1080]+bestaudio/best[height<=1080]'
            elif quality == '720p':
                ydl_opts['format'] = 'bestvideo[height<=720]+bestaudio/best[height<=720]'
            else:  # 360p
                ydl_opts['format'] = 'bestvideo[height<=360]+bestaudio/best[height<=360]'
            
            # Merge video and audio
            ydl_opts['postprocessors'] = [
                {
                    'key': 'FFmpegVideoConvertor',
                    'preferedformat': 'mp4'
                }
            ]
        else:
            # Audio format selection - extract and convert to MP3 with specific bitrate
            bitrate_map = {'excellent': '320', 'good': '192', 'ok': '128'}
            target_bitrate = bitrate_map.get(quality, '192')
            
            ydl_opts['format'] = 'bestaudio/best'
            ydl_opts['postprocessors'] = [
                {
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': target_bitrate,  # Use bitrate without 'k' suffix
                }
            ]
        
        # Download with yt-dlp
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            downloaded_file = ydl.prepare_filename(info)
        
        # Find the most recently created file (the actual output)
        files = [os.path.join(DOWNLOAD_DIR, f) for f in os.listdir(DOWNLOAD_DIR)
                 if os.path.isfile(os.path.join(DOWNLOAD_DIR, f)) and not f.startswith('.')]

        if not files:
            with tasks_lock:
                tasks[task_id] = {'state': 'FAILURE', 'error': 'Download completed but file not found'}
            return

        newest = max(files, key=os.path.getmtime)
        file_size = os.path.getsize(newest)

        result = {
            'file_path': newest,
            'filename': os.path.basename(newest),
            'size': file_size,
            'quality': quality,
            'type': media_type
        }

        # If configured, upload to Google Cloud Storage and return a signed URL
        if STORAGE_TYPE == 'gcs' and GCS_BUCKET:
            try:
                from google.cloud import storage
                client = storage.Client()
                bucket = client.bucket(GCS_BUCKET)
                dest_name = os.path.basename(newest)
                blob = bucket.blob(dest_name)
                blob.upload_from_filename(newest)
                # Try to generate a signed URL for 1 hour; fallback to gs:// path
                try:
                    signed = blob.generate_signed_url(expiration=3600)
                except Exception:
                    signed = f'gs://{GCS_BUCKET}/{dest_name}'

                result['gcs_url'] = signed
                # Optionally remove local file to keep container stateless
                try:
                    os.remove(newest)
                except Exception:
                    pass
            except Exception as e:
                # On failure, include the error but still mark as success with local file
                result['gcs_error'] = str(e)

        with tasks_lock:
            tasks[task_id] = {'state': 'SUCCESS', 'result': result}
                
    except Exception as e:
        error_msg = str(e)
        # Provide helpful error messages
        if 'available' in error_msg.lower():
            error_msg = f"Content not available: {quality} quality may not be available for this source"
        elif 'cloudflare' in error_msg.lower():
            error_msg = "Source is protected by Cloudflare. Try a different URL."
        elif 'copyright' in error_msg.lower():
            error_msg = "This content is copyright protected and cannot be downloaded."
        elif 'http error 404' in error_msg.lower():
            error_msg = "Video URL not found (404). Try a different URL."
        elif 'unsupported url' in error_msg.lower():
            error_msg = "URL format not supported by this service."
        
        with tasks_lock:
            tasks[task_id] = {'state': 'FAILURE', 'error': error_msg}

# API Routes (before static mount)
@app.post("/download")
def create_download(req: DownloadRequest):
    """Create a download task for a video or audio URL"""
    # Validate input
    if not validate_url(str(req.url)):
        raise HTTPException(status_code=400, detail='Invalid URL format')
    
    if req.media_type not in ['video', 'audio']:
        raise HTTPException(status_code=400, detail='Invalid media_type')
    
    valid_qualities = {
        'video': ['1080p', '720p', '360p'],
        'audio': ['excellent', 'good', 'ok']
    }
    
    if req.quality not in valid_qualities.get(req.media_type, []):
        raise HTTPException(status_code=400, detail=f'Invalid quality for {req.media_type}')
    
    task_id = str(uuid.uuid4())
    with tasks_lock:
        tasks[task_id] = {
            'state': 'PENDING',
            'url': str(req.url),
            'media_type': req.media_type,
            'quality': req.quality
        }
    
    thread = threading.Thread(
        target=download_worker,
        args=(task_id, str(req.url), req.media_type, req.quality),
        daemon=True
    )
    thread.start()
    
    return {"task_id": task_id, "status": "queued"}

@app.get("/status/{task_id}")
def get_status(task_id: str):
    """Get the status of a download task"""
    with tasks_lock:
        if task_id not in tasks:
            raise HTTPException(status_code=404, detail='Task not found')
        task = tasks[task_id].copy()
    
    # Don't expose URL in response for security
    task.pop('url', None)
    return task

@app.get("/file/{task_id}")
def get_file(task_id: str):
    """Download the completed file"""
    with tasks_lock:
        if task_id not in tasks:
            raise HTTPException(status_code=404, detail='Task not found')
        
        if tasks[task_id].get('state') != 'SUCCESS':
            raise HTTPException(status_code=404, detail='File not ready or download failed')
        
        data = tasks[task_id].get('result', {})
    
    # If object was uploaded to GCS, return the signed URL
    gcs_url = data.get('gcs_url')
    if gcs_url:
        return { 'gcs_url': gcs_url }

    path = data.get('file_path')
    if not path or not os.path.exists(path):
        raise HTTPException(status_code=404, detail='File missing')

    return FileResponse(
        path,
        filename=data.get('filename'),
        media_type='application/octet-stream'
    )

@app.get("/api/formats")
def get_formats():
    """Get available format options"""
    return {
        "video": {
            "formats": ["1080p", "720p", "360p"],
            "descriptions": {
                "1080p": "Full HD - High quality, larger file size (~500MB+ per hour)",
                "720p": "HD - Good quality, medium file size (~250MB per hour)",
                "360p": "Standard - Lower quality, smaller file size (~100MB per hour)"
            }
        },
        "audio": {
            "formats": ["excellent", "good", "ok"],
            "descriptions": {
                "excellent": "320 kbps - Studio quality, larger file (~1.5MB per minute)",
                "good": "192 kbps - High quality, medium file (~1MB per minute)",
                "ok": "128 kbps - Compressed, smaller file (~0.8MB per minute)"
            }
        }
    }

# Serve frontend static files (last)
frontend_path = os.path.join(os.path.dirname(__file__), '..', '..', 'frontend')
if os.path.exists(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="static")
