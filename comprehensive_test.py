#!/usr/bin/env python3
"""
Comprehensive format selection test using YouTube URL
Tests both audio and video format selection with actual quality verification
"""
import requests
import json
import time
import subprocess
from pathlib import Path

BASE_URL = "http://localhost:8000"
DOWNLOADS_DIR = Path(__file__).parent / "downloads"

def get_audio_properties(file_path):
    """Get audio bitrate using ffprobe"""
    try:
        result = subprocess.run(
            ['ffprobe', '-v', 'error', '-select_streams', 'a:0',
             '-show_entries', 'stream=bit_rate', '-of', 'json',
             str(file_path)],
            capture_output=True, text=True, timeout=10
        )
        data = json.loads(result.stdout)
        if data.get('streams'):
            bitrate = int(data['streams'][0].get('bit_rate', 0))
            return bitrate // 1000  # Convert to kbps
    except Exception as e:
        print(f"Error reading audio: {e}")
    return None

def get_video_properties(file_path):
    """Get video resolution using ffprobe"""
    try:
        result = subprocess.run(
            ['ffprobe', '-v', 'error', '-select_streams', 'v:0',
             '-show_entries', 'stream=width,height', '-of', 'json',
             str(file_path)],
            capture_output=True, text=True, timeout=10
        )
        data = json.loads(result.stdout)
        if data.get('streams'):
            height = data['streams'][0].get('height', 0)
            width = data['streams'][0].get('width', 0)
            return f"{width}x{height}", height
    except Exception as e:
        print(f"Error reading video: {e}")
    return None, None

def submit_download(url, media_type, quality):
    """Submit a download request"""
    payload = {
        "url": url,
        "media_type": media_type,
        "quality": quality
    }
    response = requests.post(f"{BASE_URL}/download", json=payload, timeout=30)
    if response.status_code == 200:
        return response.json()["task_id"]
    else:
        print(f"Failed to submit download: {response.text}")
        return None

def check_status(task_id):
    """Check download status"""
    response = requests.get(f"{BASE_URL}/status/{task_id}", timeout=30)
    return response.json()

def wait_for_download(task_id, timeout=300):
    """Wait for download to complete"""
    start = time.time()
    while time.time() - start < timeout:
        status = check_status(task_id)
        state = status.get('state')
        
        if state == 'SUCCESS':
            return True, status
        elif state == 'FAILURE':
            return False, status
        
        time.sleep(2)
    
    return False, {'state': 'TIMEOUT', 'error': 'Download took too long'}

def test_audio_formats():
    """Test audio format selection with YouTube"""
    print("\n" + "="*70)
    print("AUDIO FORMAT SELECTION TESTS (YouTube Source)")
    print("="*70)
    
    # YouTube URL with good audio quality
    youtube_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    
    audio_tests = [
        ("excellent", "320k expected"),
        ("good", "192k expected"),
        ("ok", "128k expected"),
    ]
    
    for quality, expected in audio_tests:
        print(f"\n📥 Testing AUDIO quality: {quality} ({expected})")
        print("-" * 60)
        
        task_id = submit_download(youtube_url, "audio", quality)
        if not task_id:
            print(f"❌ Failed to submit request")
            continue
        
        print(f"   Task ID: {task_id}")
        print(f"   Downloading... ", end="", flush=True)
        
        success, status = wait_for_download(task_id)
        
        if not success:
            print(f"❌ FAILED")
            print(f"   Error: {status.get('error', 'Unknown error')}")
            continue
        
        print(f"✓")
        
        # Find the downloaded file
        files = list(DOWNLOADS_DIR.glob(f"{task_id}*"))
        if not files:
            print(f"   ⚠️  No file found")
            continue
        
        file_path = files[0]
        file_size_mb = file_path.stat().st_size / (1024 * 1024)
        print(f"   File: {file_path.name}")
        print(f"   Size: {file_size_mb:.2f} MB")
        
        # Check bitrate
        bitrate = get_audio_properties(file_path)
        if bitrate:
            print(f"   Bitrate: {bitrate} kbps")
            
            # Verify bitrate matches quality selection
            if quality == "excellent" and bitrate >= 300:
                print(f"   ✅ PASS - Excellent quality (≥300kbps)")
            elif quality == "good" and 150 <= bitrate < 300:
                print(f"   ✅ PASS - Good quality (150-299kbps)")
            elif quality == "ok" and bitrate <= 150:
                print(f"   ✅ PASS - Ok quality (≤150kbps)")
            else:
                print(f"   ⚠️  Quality doesn't match selection (bitrate: {bitrate})")
        else:
            print(f"   ⚠️  Could not read bitrate")

def test_video_formats():
    """Test video format selection with YouTube"""
    print("\n" + "="*70)
    print("VIDEO FORMAT SELECTION TESTS (YouTube Source)")
    print("="*70)
    
    youtube_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    
    video_tests = [
        ("1080p", 1080),
        ("720p", 720),
        ("360p", 360),
    ]
    
    for quality, expected_height in video_tests:
        print(f"\n📥 Testing VIDEO quality: {quality} (≤{expected_height}p)")
        print("-" * 60)
        
        task_id = submit_download(youtube_url, "video", quality)
        if not task_id:
            print(f"❌ Failed to submit request")
            continue
        
        print(f"   Task ID: {task_id}")
        print(f"   Downloading... ", end="", flush=True)
        
        success, status = wait_for_download(task_id, timeout=600)
        
        if not success:
            print(f"❌ FAILED")
            print(f"   Error: {status.get('error', 'Unknown error')}")
            continue
        
        print(f"✓")
        
        # Find the downloaded file
        files = list(DOWNLOADS_DIR.glob(f"{task_id}*"))
        if not files:
            print(f"   ⚠️  No file found")
            continue
        
        file_path = files[0]
        file_size_mb = file_path.stat().st_size / (1024 * 1024)
        print(f"   File: {file_path.name}")
        print(f"   Size: {file_size_mb:.2f} MB")
        
        # Check resolution
        res_str, height = get_video_properties(file_path)
        if res_str and height:
            print(f"   Resolution: {res_str}")
            
            # Verify resolution matches quality selection
            if height <= expected_height:
                print(f"   ✅ PASS - {quality} quality (height={height}p ≤ {expected_height}p)")
            else:
                print(f"   ⚠️  Resolution too high (got {height}p, expected ≤{expected_height}p)")
        else:
            print(f"   ⚠️  Could not read resolution")

def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("COMPREHENSIVE FORMAT SELECTION TEST")
    print("="*70)
    print(f"\nServer: {BASE_URL}")
    print(f"Downloads dir: {DOWNLOADS_DIR}")
    
    # Verify server is running
    try:
        response = requests.get(f"{BASE_URL}/status/test", timeout=5)
    except Exception as e:
        print(f"\n❌ ERROR: Cannot connect to server at {BASE_URL}")
        print(f"   {e}")
        print("\nMake sure the server is running:")
        print("  cd backend && python -m uvicorn app.main:app --port 8000")
        return
    
    # Run audio tests
    test_audio_formats()
    
    # Run video tests  
    test_video_formats()
    
    print("\n" + "="*70)
    print("TEST COMPLETE")
    print("="*70 + "\n")

if __name__ == "__main__":
    main()
