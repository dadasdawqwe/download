#!/bin/bash
# Start the Video Downloader web server locally
# Usage: ./start.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="${SCRIPT_DIR}/.venv311"
BACKEND_DIR="${SCRIPT_DIR}/backend"
PID_FILE="${SCRIPT_DIR}/server.pid"
LOG_FILE="${SCRIPT_DIR}/server.log"

# Check if .venv311 exists, if not create it
if [ ! -d "$VENV_DIR" ]; then
    echo "🔧 Creating Python 3.11 virtualenv..."
    if ! command -v python3.11 &> /dev/null; then
        echo "⚠️  python3.11 not found. Trying to install via homebrew..."
        if command -v brew &> /dev/null; then
            brew install python@3.11
        else
            echo "❌ python3.11 not found and brew is not available. Please install Python 3.11 manually."
            exit 1
        fi
    fi
    python3.11 -m venv "$VENV_DIR"
fi

# Activate venv and install dependencies if needed
echo "📦 Installing dependencies..."
"$VENV_DIR/bin/pip" install -q -U pip setuptools wheel
"$VENV_DIR/bin/pip" install -q fastapi==0.100.0 "uvicorn[standard]==0.22.0" yt-dlp python-multipart==0.0.6 aiofiles==23.2.1 pydantic==1.10.12 requests

# Kill any existing server on port 8000
echo "🔄 Clearing port 8000..."
if command -v lsof &> /dev/null; then
    pids=$(lsof -tiTCP:8000 -sTCP:LISTEN 2>/dev/null) || true
    if [ -n "$pids" ]; then
        kill -9 $pids 2>/dev/null || true
    fi
fi
sleep 1

# Start the server
echo "🚀 Starting Video Downloader on http://localhost:8000"
cd "$BACKEND_DIR"
nohup "$VENV_DIR/bin/uvicorn" app.main:app --host 127.0.0.1 --port 8000 --log-level info > "$LOG_FILE" 2>&1 </dev/null &
SERVER_PID=$!
echo $SERVER_PID > "$PID_FILE"

# Wait for server to start
sleep 2

# Verify server is running
if kill -0 $SERVER_PID 2>/dev/null; then
    PID_VAL=$(cat "$PID_FILE")
    echo "✅ Server started successfully (PID: $SERVER_PID)"
    echo "📂 Open http://localhost:8000 in your browser"
    echo "📋 Logs: tail -f \"$LOG_FILE\""
    echo "🛑 To stop: ./stop.sh"
else
    echo "❌ Server failed to start. Check logs:"
    cat "$LOG_FILE"
    exit 1
fi
