#!/usr/bin/env python3
import time, os, json, subprocess
from yt_dlp import YoutubeDL

ROOT = os.path.abspath(os.path.dirname(__file__))
DL_DIR = os.path.join(ROOT, 'downloads')
os.makedirs(DL_DIR, exist_ok=True)

URL = 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'
FORMAT = 'bestvideo[height<=1080]+bestaudio/best[height<=1080]'


def clean_files(prefix):
    for f in os.listdir(DL_DIR):
        if f.startswith(prefix):
            try:
                os.remove(os.path.join(DL_DIR, f))
            except:
                pass


def filesize_kb(path):
    return os.path.getsize(path) / 1024.0


def run_download(label, ydl_opts, out_prefix):
    clean_files(out_prefix)
    opts = ydl_opts.copy()
    opts['format'] = FORMAT
    opts['outtmpl'] = os.path.join(DL_DIR, out_prefix + '.%(ext)s')
    print(f"Running {label}...")
    start = time.time()
    with YoutubeDL(opts) as ydl:
        info = ydl.extract_info(URL, download=True)
        filename = ydl.prepare_filename(info)
    elapsed = time.time() - start
    # find downloaded file
    files = [os.path.join(DL_DIR, f) for f in os.listdir(DL_DIR) if f.startswith(out_prefix)]
    if not files:
        print("No output file found")
        return None
    file = max(files, key=os.path.getmtime)
    size_kb = filesize_kb(file)
    print(f"{label} complete: {file} — {size_kb/1024:.2f} MB in {elapsed:.2f}s ({(size_kb/elapsed):.2f} KB/s)")
    return {'label':label, 'file':file, 'mb':size_kb/1024.0, 'secs':elapsed, 'kbps':size_kb/elapsed}


def main():
    # Baseline opts (minimal concurrency)
    baseline_opts = {
        'noplaylist': True,
        'quiet': True,
        'no_warnings': True,
        'socket_timeout': 30,
        'retries': 3,
    }
    # Tuned opts
    tuned_opts = baseline_opts.copy()
    tuned_opts.update({
        'noprogress': True,
        'continuedl': True,
        'concurrent_fragment_downloads': 16,
        'fragment_retries': 8,
    })
    # aria2 removed: do not use external downloader
    print('ARIA2 enabled: False')

    r1 = run_download('baseline', baseline_opts, 'bench_base')
    r2 = run_download('tuned', tuned_opts, 'bench_tuned')

    print('\nRESULTS')
    print('-------')
    if r1:
        print(f"Baseline: {r1['mb']:.2f} MB in {r1['secs']:.2f}s — {r1['kbps']:.2f} KB/s")
    if r2:
        print(f"Tuned:    {r2['mb']:.2f} MB in {r2['secs']:.2f}s — {r2['kbps']:.2f} KB/s")
    if r1 and r2:
        improvement = (r2['kbps'] - r1['kbps']) / r1['kbps'] * 100.0
        print(f"Improvement: {improvement:.1f}%")

if __name__ == '__main__':
    main()
