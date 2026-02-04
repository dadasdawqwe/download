# 🎬 Media Player & Multiple Downloads - Feature Guide

## Visual Layout

```
┌─────────────────────────────────────────────────────────────┐
│                     DOWNLOAD FORM                           │
│  📍 URL Input                                               │
│  [📺 Video / 🎵 Audio]  [⚙️ Quality Selector]              │
│                    [⬇️ Download]                            │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                   ACTIVE DOWNLOADS QUEUE                     │
│  Item 1: 📺 VIDEO - A1B2C3D4                               │
│  Status: 📥 Downloading    [❌ Remove]                      │
│  Quality: 720p HD          Size: calculating...             │
│                                                              │
│  Item 2: 🎵 AUDIO - E5F6G7H8                                │
│  Status: ✅ Ready          [▶️ Play] [📥 Download]          │
│  Quality: 🎧 Excellent (320kbps)  Size: 45.2 MB            │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                    MEDIA PLAYER                             │
│  ┌─────────────────────────────────────────────────────────┐│
│  │ [████████░░░░] Current: Song.mp3                       ││
│  │ 00:45 / 03:20                                           ││
│  └─────────────────────────────────────────────────────────┘│
│                                                              │
│  [⏮️ Previous] [▶️ Play] [⏭️ Next]                           │
│                                                              │
│         PLAYLIST                                            │
│  🎵 Song1.mp3  [Active]                                     │
│  🎬 Video.mp4                                               │
│  🎵 Song2.mp3                                               │
│  🎬 Video2.mp4                                              │
└─────────────────────────────────────────────────────────────┘
```

## Key Features

### 1️⃣ **Download Form** (Unchanged but Enhanced)
- Single form for submitting downloads
- Auto-clears after submission
- Submit multiple times for batch downloads
- All downloads process simultaneously

### 2️⃣ **Active Downloads Queue** (NEW!)
Status indicators:
- ⏳ **Queued** - Waiting to start
- 📥 **Downloading** - In progress
- ✅ **Ready** - Complete, ready to play/download
- ❌ **Failed** - Error occurred

Quick actions per download:
- **▶️ Play** - Start media player
- **📥 Download** - Save file locally
- **❌ Remove** - Remove from queue

Info displayed:
- Task ID (first 8 characters)
- Media type (Audio/Video)
- Quality setting
- File name (when complete)
- File size (when complete)

### 3️⃣ **Media Player** (NEW!)
HTML5 native player with:
- **Play/Pause Control** - Click play button or use browser controls
- **Seek Bar** - Drag to jump to any point
- **Volume Control** - Adjust audio level
- **Full Audio Controls** - Auto-generated based on format
- **Full Video Controls** (video only):
  - Picture-in-Picture mode
  - Fullscreen toggle
  - Playback speed adjustment

Navigation buttons:
- **⏮️ Previous** - Play previous file in playlist
- **▶️ Play** - Toggle play/pause
- **⏭️ Next** - Play next file in playlist

### 4️⃣ **Interactive Playlist** (NEW!)
Features:
- Auto-populated when downloads complete
- Click any item to play it
- Shows media type icon (🎵 audio, 🎬 video)
- Highlights active/currently playing file
- Filenames truncated if too long
- Max-height with scrolling for many files

## Color Coding

### Status Badge Colors
| Status | Color | Meaning |
|--------|-------|---------|
| ⏳ Queued | 🟡 Amber | Waiting or initializing |
| 📥 Downloading | 🔵 Blue | Download in progress |
| ✅ Ready | 🟢 Green | Complete and playable |
| ❌ Failed | 🔴 Red | Error or failed |

### UI Elements
- **Primary**: Purple/Blue (#6366f1) - Main actions
- **Success**: Green (#10b981) - Playable/completed
- **Warning**: Amber (#f59e0b) - Processing
- **Danger**: Red (#ef4444) - Errors

## Workflow Examples

### Example 1: Download and Play Single File
```
1. Enter YouTube URL → Select Video 720p → Click Download
2. Status shows "⏳ Queued"
3. Switches to "📥 Downloading" 
4. After 2-5 min: Status shows "✅ Ready"
5. Media player auto-appears with video
6. Use browser controls to play/pause/seek
```

### Example 2: Queue Multiple Downloads
```
1. URL 1 → 1080p Video → Click Download ✓
2. Form clears, ready for next
3. URL 2 → Excellent Audio → Click Download ✓
4. URL 3 → 720p Video → Click Download ✓
5. All 3 appear in Active Downloads queue
6. Each processes independently
7. Queue shows progress for each
8. As they complete, they auto-add to playlist
```

### Example 3: Create Mixed Playlist
```
1. Download multiple songs (MP3)
2. Download movie clip (MP4)
3. All appear in playlist
4. Click on any song → plays in player
5. Use Previous/Next to navigate
6. Mix audio and video in same playlist
```

## Status Updates

The interface updates in real-time:
- **Queue**: Updates every 2 seconds
- **Status badges**: Reflect latest state
- **Playlist**: Updates when downloads complete
- **Player**: Responds instantly to button clicks

## Download Limits & Performance

### Simultaneous Downloads
- **Unlimited**: Add as many as needed
- **Backend threading**: Each uses separate thread
- **Frontend polling**: Checks status every 2 seconds
- **Storage**: Limited by disk space

### Typical Speeds
- **Video 1080p**: 1-10 MB/s (depends on source)
- **Video 720p**: 0.5-5 MB/s
- **Audio MP3**: 0.1-1 MB/s
- **Total time**: 2 min to 1 hour+ depending on file size

## Responsive Design

### Desktop (>1024px)
- Full layout with all elements visible
- Media player at full width
- Playlist beside player controls
- Queue displays in grid

### Tablet (768-1024px)
- Stacked layout
- Player at full width
- Playlist below player
- Touch-friendly buttons

### Mobile (<768px)
- Single column layout
- Large touch targets
- Player controls in column
- Simplified queue view
- Landscape mode optimized

## Browser Requirements

### Minimum Support
- Chrome 55+ / Firefox 49+
- Safari 11+ / Edge 79+

### Required Features
- HTML5 `<audio>` and `<video>` elements
- Fetch API for downloads
- Modern CSS Grid/Flexbox
- JavaScript ES6+ features

### Media Format Support
Depends on browser:
- **MP3 audio**: All modern browsers ✓
- **MP4 video (H.264)**: All modern browsers ✓
- Codecs confirmed: H.264 video, AAC audio

## Keyboard Shortcuts

### Browser Native (Media Player)
- **Space**: Play/Pause
- **→**: Forward 5 seconds
- **←**: Rewind 5 seconds
- **M**: Mute/Unmute
- **F**: Fullscreen (video)
- **↑/↓**: Volume up/down
- **0-9**: Jump to percentage

### App Shortcuts (Planned)
- **Enter**: Submit download form
- **Escape**: Clear status messages
- **1-9**: Quick play playlist item N

## Troubleshooting Common Issues

### Player doesn't appear
**Problem**: Downloaded file but no player
**Solution**:
1. Check if status shows ✅ Ready
2. Click [▶️ Play] button manually
3. Refresh page if stuck

### Media won't play
**Problem**: Player shows but file won't play
**Solution**:
1. Check file format (MP3/MP4)
2. Download file directly to verify
3. Check browser console for errors

### Queue not updating
**Problem**: Downloaded but queue status frozen
**Solution**:
1. Wait 2 seconds for poll update
2. Refresh page to sync state
3. Check API connectivity

### Multiple downloads failing
**Problem**: Some downloads fail, others work
**Solution**:
1. Try one at a time
2. Check if URL is still valid
3. Verify backend is running
4. Check disk space on server

## Performance Tips

### For Better Experience
1. **Close old downloads**: Remove completed files from queue
2. **Limit simultaneous**: 3-5 concurrent downloads recommended
3. **Use high bandwidth**: Some sources throttle
4. **Off-peak times**: Download during low-traffic hours
5. **Stable connection**: Wired > WiFi for large files

### Storage Management
1. **Check disk space**: Large 1080p files use 500MB+/hour
2. **Archive old files**: Move completed downloads
3. **Use quality selector**: Choose appropriate quality
4. **Monitor queue size**: Keep under 100 items
