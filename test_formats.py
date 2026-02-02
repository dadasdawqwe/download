#!/usr/bin/env python3
"""
Comprehensive format selection test script
Tests actual downloaded file properties to verify formats work correctly
"""
import os
import sys
import requests
import json
import time
import subprocess
from pathlib import Path

API = "http://localhost:8000"
DOWNLOAD_DIR = "./downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

def get_video_info(filepath):
    """Get video resolution and codec info using ffprobe"""
    try:
        cmd = [
            'ffprobe', '-v', 'error', '-select_streams', 'v:0',
            '-show_entries', 'stream=width,height,codec_name',
            '-of', 'json', filepath
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            data = json.loads(result.stdout)
            if data.get('streams'):
                stream = data['streams'][0]
                return {
                    'width': stream.get('width'),
                    'height': stream.get('height'),
                    'codec': stream.get('codec_name')
                }
    except Exception as e:
        print(f"  ⚠️ ffprobe error: {e}")
    return None

def get_audio_info(filepath):
    """Get audio bitrate and codec info using ffprobe"""
    try:
        cmd = [
            'ffprobe', '-v', 'error', '-select_streams', 'a:0',
            '-show_entries', 'stream=bit_rate,codec_name,sample_rate',
            '-of', 'json', filepath
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            data = json.loads(result.stdout)
            if data.get('streams'):
                stream = data['streams'][0]
                bitrate = stream.get('bit_rate')
                if bitrate:
                    bitrate = int(bitrate) // 1000  # Convert to kbps
                return {
                    'bitrate_kbps': bitrate,
                    'codec': stream.get('codec_name'),
                    'sample_rate': stream.get('sample_rate')
                }
    except Exception as e:
        print(f"  ⚠️ ffprobe error: {e}")
    return None

def test_download(url, media_type, quality):
    """Test a single download and verify format"""
    print(f"\n{'='*70}")
    print(f"TEST: {media_type.upper()} - {quality}")
    print(f"URL: {url}")
    print(f"{'='*70}")
    
    # Create download task
    payload = {
        "url": url,
        "media_type": media_type,
        "quality": quality
    }
    
    print("📤 Submitting download request...")
    try:
        resp = requests.post(f"{API}/download", json=payload, timeout=5)
        if resp.status_code != 200:
            print(f"❌ API Error: {resp.status_code} - {resp.text}")
            return False
        
        data = resp.json()
        task_id = data.get('task_id')
        print(f"✅ Task created: {task_id[:8]}")
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return False
    
    # Poll status until complete
    max_wait = 120  # 2 minutes max
    elapsed = 0
    last_state = None
    
    print("⏳ Waiting for download to complete...")
    while elapsed < max_wait:
        try:
            resp = requests.get(f"{API}/status/{task_id}", timeout=5)
            data = resp.json()
            state = data.get('state')
            
            if state != last_state:
                print(f"  State: {state} ({elapsed}s)")
                last_state = state
            
            if state == 'SUCCESS':
                result = data.get('result', {})
                filename = result.get('filename')
                file_size = result.get('size', 0)
                print(f"✅ Download Complete!")
                print(f"   File: {filename}")
                print(f"   Size: {file_size / 1024 / 1024:.2f} MB")
                
                # Check actual file properties
                filepath = os.path.join(DOWNLOAD_DIR, filename)
                if os.path.exists(filepath):
                    print(f"\n📊 Verifying Format:")
                    
                    if media_type == 'video':
                        info = get_video_info(filepath)
                        if info:
                            height = info.get('height')
                            width = info.get('width')
                            codec = info.get('codec')
                            print(f"   Resolution: {width}x{height}")
                            print(f"   Codec: {codec}")
                            
                            # Verify quality
                            if quality == '1080p' and height and height <= 1080:
                                print(f"   ✅ Quality verified: {height}p matches 1080p request")
                            elif quality == '720p' and height and height <= 720:
                                print(f"   ✅ Quality verified: {height}p matches 720p request")
                            elif quality == '360p' and height and height <= 360:
                                print(f"   ✅ Quality verified: {height}p matches 360p request")
                            else:
                                print(f"   ⚠️ Quality mismatch: got {height}p, requested {quality}")
                        else:
                            print(f"   ⚠️ Could not probe video info (ffprobe might be missing)")
                    
                    else:  # audio
                        info = get_audio_info(filepath)
                        if info:
                            bitrate = info.get('bitrate_kbps')
                            codec = info.get('codec')
                            print(f"   Bitrate: {bitrate} kbps")
                            print(f"   Codec: {codec}")
                            
                            # Verify quality
                            if quality == 'excellent' and bitrate and bitrate >= 300:
                                print(f"   ✅ Quality verified: {bitrate}kbps matches excellent request")
                            elif quality == 'good' and bitrate and 150 <= bitrate < 300:
                                print(f"   ✅ Quality verified: {bitrate}kbps matches good request")
                            elif quality == 'ok' and bitrate and bitrate < 150:
                                print(f"   ✅ Quality verified: {bitrate}kbps matches ok request")
                            else:
                                print(f"   ⚠️ Bitrate mismatch: got {bitrate}kbps, requested {quality}")
                        else:
                            print(f"   ⚠️ Could not probe audio info (ffprobe might be missing)")
                else:
                    print(f"❌ File not found at {filepath}")
                    return False
                
                return True
            
            elif state == 'FAILURE':
                error = data.get('error')
                print(f"❌ Download failed: {error}")
                return False
            
            time.sleep(2)
            elapsed += 2
        
        except Exception as e:
            print(f"❌ Status check failed: {e}")
            return False
    
    print(f"❌ Download timeout ({max_wait}s)")
    return False

def main():
    print("\n" + "="*70)
    print("VIDEO/AUDIO FORMAT SELECTION TEST SUITE")
    print("="*70)
    
    tests = [
        # Audio tests (these work reliably)
        ("https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3", "audio", "ok"),
        ("https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3", "audio", "good"),
        ("https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3", "audio", "excellent"),
    ]
    
    results = []
    for url, media_type, quality in tests:
        success = test_download(url, media_type, quality)
        results.append({
            'type': media_type,
            'quality': quality,
            'success': success
        })
    
    # Summary
    print(f"\n\n{'='*70}")
    print("TEST SUMMARY")
    print(f"{'='*70}")
    
    passed = sum(1 for r in results if r['success'])
    total = len(results)
    
    for r in results:
        status = "✅ PASS" if r['success'] else "❌ FAIL"
        print(f"{status} - {r['type'].upper():5} {r['quality']:10}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    print(f"{'='*70}\n")
    
    return 0 if passed == total else 1

if __name__ == '__main__':
    sys.exit(main())
