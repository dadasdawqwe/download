**Video Downloader Service**

Quick scaffold to run a production-ready, scalable downloader using FastAPI + Celery (yt_dlp) with Redis and a static frontend.

Run (development / simple local):

**Video Downloader - Frontend**

Static frontend for downloading videos/audio from any URL with quality selection. Ready to deploy on Netlify.

## Deploy to Netlify

1. Push this repo to GitHub
2. Connect repo to [Netlify](https://netlify.com)
3. Set environment variable in Netlify dashboard:
   ```
   VITE_API_URL = https://your-backend-api.com
   ```
4. Deploy (no build step needed—it's static)

## Local Development

Open `frontend/index.html` in a browser or serve with a simple HTTP server:

```bash
cd frontend
python -m http.server 8001
# Visit http://localhost:8001
```

For local testing with a backend, set your backend API endpoint:
```bash
# In frontend/app.js, the API URL defaults to http://localhost:8000
# Or configure VITE_API_URL environment variable
```

## Backend (Optional)

If you have a backend API service, set its URL in the `VITE_API_URL` environment variable on Netlify.

The backend code is included in the `backend/` directory for reference. It's a FastAPI service that:
- Accepts video/audio download requests
- Supports video qualities: 1080p, 720p, 360p
- Supports audio bitrates: 320kbps, 192kbps, 128kbps
- Returns download status and file links

## API Endpoints (if using the included backend)

- `POST /download` → `{ url, media_type: video|audio, quality }`
- `GET /status/{task_id}`
- `GET /file/{task_id}` → binary file download

## Features

✅ Download videos in multiple qualities (1080p, 720p, 360p)  
✅ Download audio in multiple bitrates (320, 192, 128 kbps)  
✅ Real-time download status polling  
✅ Dark theme responsive UI  
✅ Simple static frontend (no build required)
