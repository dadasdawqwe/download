#!/usr/bin/env python3
"""
Final verification test - Check actual format selection with multiple sources
"""
import requests
import json
import time
import subprocess
from pathlib import Path

BASE_URL = "http://localhost:8000"
DOWNLOADS_DIR = Path("/Users/rajatsable/Documents/web development/video downloader/downloads")

def get_audio_bitrate(file_path):
    """Get actual audio bitrate using ffprobe"""
    try:
        result = subprocess.run(
            ['ffprobe', '-v', 'error', '-select_streams', 'a:0',
             '-show_entries', 'stream=bit_rate', '-of', 'json',
             str(file_path)],
            capture_output=True, text=True, timeout=10
        )
        data = json.loads(result.stdout)
        if data.get('streams') and data['streams'][0].get('bit_rate'):
            return int(data['streams'][0]['bit_rate']) // 1000
    except:
        pass
    return None

def get_video_resolution(file_path):
    """Get actual video resolution using ffprobe"""
    try:
        result = subprocess.run(
            ['ffprobe', '-v', 'error', '-select_streams', 'v:0',
             '-show_entries', 'stream=width,height', '-of', 'json',
             str(file_path)],
            capture_output=True, text=True, timeout=10
        )
        data = json.loads(result.stdout)
        if data.get('streams') and data['streams'][0].get('height'):
            return data['streams'][0]['height']
    except:
        pass
    return None

def submit_and_wait(url, media_type, quality, timeout=120):
    """Submit download and wait for completion"""
    # Submit
    response = requests.post(
        f"{BASE_URL}/download",
        json={"url": url, "media_type": media_type, "quality": quality},
        timeout=30
    )
    
    if response.status_code != 200:
        return None, f"Submit failed: {response.status_code}"
    
    task_id = response.json()["task_id"]
    
    # Wait for completion
    start = time.time()
    while time.time() - start < timeout:
        status_response = requests.get(f"{BASE_URL}/status/{task_id}", timeout=30)
        status_data = status_response.json()
        
        if status_data.get('state') == 'SUCCESS':
            file_path = DOWNLOADS_DIR / status_data['result']['filename']
            return file_path if file_path.exists() else None, None
        elif status_data.get('state') == 'FAILURE':
            return None, status_data.get('error', 'Unknown error')
        
        time.sleep(2)
    
    return None, "Timeout"

print("\n" + "="*80)
print("FINAL DEBUG VERIFICATION - FORMAT SELECTION TEST")
print("="*80)

# Test 1: Audio with different qualities
print("\n[TEST 1] AUDIO FORMAT SELECTION")
print("-" * 80)

youtube_audio_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
audio_tests = [
    ("excellent", 320),
    ("good", 192),
    ("ok", 128),
]

audio_results = []
for quality, expected_bitrate in audio_tests:
    print(f"\nDownloading audio ({quality}, target={expected_bitrate}kbps)...", end=" ", flush=True)
    
    file_path, error = submit_and_wait(youtube_audio_url, "audio", quality)
    
    if not file_path:
        print(f"❌ FAILED: {error}")
        audio_results.append((quality, expected_bitrate, None, error))
        continue
    
    actual_bitrate = get_audio_bitrate(file_path)
    status = "✅" if actual_bitrate else "⚠️"
    print(f"{status} Downloaded")
    
    if actual_bitrate:
        match = "✅ MATCH" if actual_bitrate == expected_bitrate else f"(expected {expected_bitrate}kbps)"
        print(f"  File: {file_path.name}")
        print(f"  Size: {file_path.stat().st_size / (1024*1024):.2f}MB")
        print(f"  Bitrate: {actual_bitrate}kbps {match}")
        audio_results.append((quality, expected_bitrate, actual_bitrate, "success"))
    else:
        print(f"  ⚠️  Could not read bitrate")
        audio_results.append((quality, expected_bitrate, None, "couldn't read"))

# Test 2: Video with different qualities
print("\n\n[TEST 2] VIDEO FORMAT SELECTION")
print("-" * 80)

youtube_video_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
video_tests = [
    ("1080p", 1080),
    ("720p", 720),
    ("360p", 360),
]

video_results = []
for quality, expected_height in video_tests:
    print(f"\nDownloading video ({quality}, max={expected_height}p)...", end=" ", flush=True)
    
    file_path, error = submit_and_wait(youtube_video_url, "video", quality, timeout=300)
    
    if not file_path:
        print(f"❌ FAILED: {error}")
        video_results.append((quality, expected_height, None, error))
        continue
    
    actual_height = get_video_resolution(file_path)
    status = "✅" if actual_height else "⚠️"
    print(f"{status} Downloaded")
    
    if actual_height:
        match = "✅ PASS" if actual_height <= expected_height else f"(exceeds {expected_height}p)"
        print(f"  File: {file_path.name}")
        print(f"  Size: {file_path.stat().st_size / (1024*1024):.2f}MB")
        print(f"  Resolution: {actual_height}p {match}")
        video_results.append((quality, expected_height, actual_height, "success"))
    else:
        print(f"  ⚠️  Could not read resolution")
        video_results.append((quality, expected_height, None, "couldn't read"))

# Summary
print("\n\n" + "="*80)
print("SUMMARY")
print("="*80)

print("\nAUDIO RESULTS:")
for quality, expected, actual, status in audio_results:
    if actual:
        match_str = "✅ MATCH" if actual == expected else f"Got {actual}kbps"
        print(f"  {quality:15} | Expected: {expected:3}kbps | {match_str}")
    else:
        print(f"  {quality:15} | {status}")

print("\nVIDEO RESULTS:")
for quality, expected, actual, status in video_results:
    if actual:
        match_str = "✅ PASS" if actual <= expected else f"Exceeds limit"
        print(f"  {quality:15} | Max: {expected:4}p | Got: {actual:4}p | {match_str}")
    else:
        print(f"  {quality:15} | {status}")

print("\n" + "="*80)
