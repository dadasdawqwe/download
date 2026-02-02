#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="/Users/rajatsable/Documents/web development/video downloader"
DOWNLOADS_DIR="$ROOT_DIR/downloads"
BASE_URL="http://localhost:8000"

submit() {
  local url=$1; local type=$2; local quality=$3
  resp=$(curl -s -X POST "$BASE_URL/download" -H "Content-Type: application/json" -d "{\"url\":\"$url\",\"media_type\":\"$type\",\"quality\":\"$quality\"}")
  echo "$resp"
}

wait_for() {
  local task=$1; local timeout=${2:-180}
  local start=$(date +%s)
  while true; do
    status=$(curl -s "$BASE_URL/status/$task")
    state=$(echo "$status" | python3 -c "import sys,json;print(json.load(sys.stdin).get('state'))")
    if [ "$state" = "SUCCESS" ] || [ "$state" = "FAILURE" ]; then
      echo "$status"
      return 0
    fi
    now=$(date +%s)
    if [ $((now-start)) -ge $timeout ]; then
      echo "{\"state\":\"TIMEOUT\",\"task\":\"$task\"}"
      return 1
    fi
    sleep 2
  done
}

check_audio_file() {
  local file=$1
  if [ ! -f "$file" ]; then
    echo "MISSING"
    return 1
  fi
  ffprobe -v error -select_streams a:0 -show_entries stream=bit_rate -of json "$file" | python3 -m json.tool
}

check_video_file() {
  local file=$1
  if [ ! -f "$file" ]; then
    echo "MISSING"
    return 1
  fi
  ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of json "$file" | python3 -m json.tool
}

printf "\n=== E2E FORMAT SELECTION TEST ===\n"

YOUTUBE_URL="https://www.youtube.com/watch?v=dQw4w9WgXcQ"

# AUDIO tests
for q in excellent good ok; do
  printf "\n-- Audio test: %s --\n" "$q"
  resp=$(submit "$YOUTUBE_URL" audio "$q")
  echo "submit response: $resp"
  task=$(echo "$resp" | python3 -c "import sys,json;print(json.load(sys.stdin).get('task_id',''))")
  if [ -z "$task" ]; then
    echo "Failed to get task id"
    continue
  fi
  echo "task: $task"
  wait_for "$task" 120 || true
  status=$(curl -s "$BASE_URL/status/$task")
  echo "status: $status"
  filename=$(echo "$status" | python3 -c "import sys,json;print(json.load(sys.stdin).get('result',{}).get('filename',''))")
  if [ -n "$filename" ]; then
    abs="$DOWNLOADS_DIR/$filename"
    echo "Checking file: $abs"
    check_audio_file "$abs" || echo "Audio file missing or check failed"
  else
    echo "No filename returned"
  fi
done

# VIDEO tests
for q in 1080p 720p 360p; do
  printf "\n-- Video test: %s --\n" "$q"
  resp=$(submit "$YOUTUBE_URL" video "$q")
  echo "submit response: $resp"
  task=$(echo "$resp" | python3 -c "import sys,json;print(json.load(sys.stdin).get('task_id',''))")
  if [ -z "$task" ]; then
    echo "Failed to get task id"
    continue
  fi
  echo "task: $task"
  wait_for "$task" 300 || true
  status=$(curl -s "$BASE_URL/status/$task")
  echo "status: $status"
  filename=$(echo "$status" | python3 -c "import sys,json;print(json.load(sys.stdin).get('result',{}).get('filename',''))")
  if [ -n "$filename" ]; then
    abs="$DOWNLOADS_DIR/$filename"
    echo "Checking file: $abs"
    check_video_file "$abs" || echo "Video file missing or check failed"
  else
    echo "No filename returned"
  fi
done

printf "\n=== TEST RUN COMPLETE ===\n"
