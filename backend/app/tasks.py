import os
import uuid
from celery import Celery
from yt_dlp import YoutubeDL
import boto3
from botocore.client import Config
import botocore

REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
DOWNLOAD_DIR = os.getenv('DOWNLOAD_DIR', './downloads')
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

S3_ENDPOINT = os.getenv('S3_ENDPOINT')
S3_ACCESS_KEY = os.getenv('S3_ACCESS_KEY')
S3_SECRET_KEY = os.getenv('S3_SECRET_KEY')
S3_BUCKET = os.getenv('S3_BUCKET')
S3_SECURE = os.getenv('S3_SECURE', 'false').lower() in ('1', 'true', 'yes')

celery_app = Celery('worker', broker=REDIS_URL, backend=REDIS_URL)


def s3_client():
    if not S3_ENDPOINT:
        return None
    cfg = Config(signature_version='s3v4')
    return boto3.client(
        's3',
        endpoint_url=S3_ENDPOINT,
        aws_access_key_id=S3_ACCESS_KEY,
        aws_secret_access_key=S3_SECRET_KEY,
        config=cfg,
        region_name=None,
    )


@celery_app.task(bind=True)
def download_task(self, url, media_type, quality):
    ydl_opts = {
        'outtmpl': os.path.join(DOWNLOAD_DIR, '%(id)s.%(ext)s'),
        'noplaylist': True,
        'quiet': True,
        'no_warnings': True,
    }

    if media_type == 'video':
        if quality == '1080p':
            fmt = 'bestvideo[height<=1080]+bestaudio/best[height<=1080]'
        elif quality == '720p':
            fmt = 'bestvideo[height<=720]+bestaudio/best[height<=720]'
        else:
            fmt = 'bestvideo[height<=360]+bestaudio/best[height<=360]'
        ydl_opts['format'] = fmt
    else:
        # audio quality mapping
        mapping = {'excellent': '256', 'good': '192', 'ok': '64'}
        pref = mapping.get(quality, '192')
        ydl_opts['format'] = 'bestaudio/best'
        ydl_opts['postprocessors'] = [
            {
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': pref,
            }
        ]

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)

        # return the newest file in DOWNLOAD_DIR
        files = [os.path.join(DOWNLOAD_DIR, f) for f in os.listdir(DOWNLOAD_DIR)]
        files = [f for f in files if os.path.isfile(f)]
        if not files:
            return {'error': 'no file produced'}
        newest = max(files, key=os.path.getmtime)

        result = {'file_path': newest, 'filename': os.path.basename(newest)}

        # If S3 configured, upload and generate presigned URL
        client = s3_client()
        if client and S3_BUCKET:
            key = f"downloads/{uuid.uuid4().hex}_{os.path.basename(newest)}"
            try:
                # ensure bucket exists
                try:
                    client.head_bucket(Bucket=S3_BUCKET)
                except botocore.exceptions.ClientError:
                    client.create_bucket(Bucket=S3_BUCKET)

                client.upload_file(newest, S3_BUCKET, key)
                presigned = client.generate_presigned_url(
                    'get_object', Params={'Bucket': S3_BUCKET, 'Key': key}, ExpiresIn=86400
                )
                result.update({'s3_key': key, 's3_url': presigned})
            except Exception as e:
                result.update({'s3_error': str(e)})

        return result

    except Exception as e:
        return {'error': str(e)}
