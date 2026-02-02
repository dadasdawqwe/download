#!/bin/bash

# Curl-based format selection test

echo "========================================================================"
echo "CURL-BASED FORMAT SELECTION TEST"
echo "========================================================================"

# Test 1: Submit audio download
echo ""
echo "[TEST 1] Submitting audio download (quality=ok)..."
TASK_RESPONSE=$(curl -s -X POST http://localhost:8000/download \
  -H "Content-Type: application/json" \
  -d '{"url":"https://www.youtube.com/watch?v=dQw4w9WgXcQ","media_type":"audio","quality":"ok"}')

echo "Response: $TASK_RESPONSE"
TASK_ID=$(echo "$TASK_RESPONSE" | grep -o '"task_id":"[^"]*' | cut -d'"' -f4)
echo "Task ID: $TASK_ID"

if [ -z "$TASK_ID" ]; then
  echo "ERROR: Could not extract task ID"
  exit 1
fi

# Wait and check status
echo ""
echo "Waiting 12 seconds for download..."
sleep 12

echo ""
echo "[TEST 2] Checking download status..."
STATUS_RESPONSE=$(curl -s "http://localhost:8000/status/$TASK_ID")
echo "Status Response:"
echo "$STATUS_RESPONSE" | head -20

# Extract filename
FILENAME=$(echo "$STATUS_RESPONSE" | grep -o '"filename":"[^"]*' | cut -d'"' -f4)
echo ""
echo "Downloaded file: $FILENAME"

if [ -n "$FILENAME" ]; then
  FILEPATH="/Users/rajatsable/Documents/web development/video downloader/downloads/$FILENAME"
  if [ -f "$FILEPATH" ]; then
    echo "✅ File exists: $FILEPATH"
    echo "File size: $(ls -lh "$FILEPATH" | awk '{print $5}')"
    
    echo ""
    echo "[TEST 3] Checking bitrate with ffprobe..."
    ffprobe -v error -select_streams a:0 -show_entries stream=bit_rate -of json "$FILEPATH" 2>&1 | grep bit_rate
  else
    echo "❌ File not found at $FILEPATH"
  fi
else
  echo "⚠️  Could not extract filename from response"
fi

echo ""
echo "========================================================================"
