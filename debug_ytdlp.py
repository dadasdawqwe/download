#!/usr/bin/env python3
"""Debug yt-dlp directly to see what's failing"""

from yt_dlp import YoutubeDL
import os

url = 'https://youtu.be/eVTXPUF4Oz4'
download_dir = os.path.expanduser("/Users/rajatsable/Documents/web development/video downloader/downloads")

print(f"Testing URL: {url}")
print(f"Download dir: {download_dir}")
print()

try:
    ydl_opts = {
        'quiet': False,
        'no_warnings': False,
        'outtmpl': os.path.join(download_dir, 'test_%(title)s.%(ext)s'),
        'format': 'worst[ext=mp4]/worst',
    }
    
    print("Attempting download with yt-dlp...")
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        print(f"✅ Success! Downloaded: {info.get('filename')}")
        
except Exception as e:
    print(f"❌ ERROR: {type(e).__name__}")
    print(f"Message: {str(e)}")
    import traceback
    traceback.print_exc()
