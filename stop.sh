#!/bin/bash
# Stop the Video Downloader web server
# Usage: ./stop.sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PID_FILE="${SCRIPT_DIR}/server.pid"

if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if kill -0 $PID 2>/dev/null; then
        echo "🛑 Stopping server (PID: $PID)..."
        kill $PID
        sleep 1
        # Force kill if still running
        if kill -0 $PID 2>/dev/null; then
            kill -9 $PID
        fi
        rm -f "$PID_FILE"
        echo "✅ Server stopped"
    else
        echo "⚠️  Server is not running (PID file exists but process not found)"
        rm -f "$PID_FILE"
    fi
else
    echo "⚠️  No PID file found. Server may not be running."
    # Try to kill uvicorn on port 8000 anyway
    if command -v lsof &> /dev/null; then
        pids=$(lsof -tiTCP:8000 -sTCP:LISTEN 2>/dev/null) || true
        if [ -n "$pids" ]; then
            echo "🔍 Found process(es) on port 8000, killing..."
            echo "$pids" | xargs kill -9
            echo "✅ Killed uvicorn process"
        fi
    fi
fi
