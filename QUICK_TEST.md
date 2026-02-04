# 🧪 QUICK TEST GUIDE - Video Downloader

## ✅ Status: Server Running
**URL**: http://localhost:8000

---

## 🎯 Test the Features (5 minutes)

### Step 1: Open Browser Console
1. Go to http://localhost:8000
2. Press **F12** (or Cmd+Option+I on Mac)
3. Click **Console** tab
4. Keep it open while testing

### Step 2: Submit First Download
```
URL: https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3
Type: Audio
Quality: Good
```
- **Expected**: 
  - ✅ Queue item appears immediately
  - ✅ Console shows: `✅ Added download:`
  - ✅ Status changes to "📥 Downloading"

### Step 3: Wait 8-10 seconds
- Watch the queue for download to complete
- **Expected**:
  - ✅ Console shows: `🔄 Updated ...: SUCCESS`
  - ✅ Console shows: `📊 Playable files: 1`
  - ✅ Console shows: `🎵 Creating media player for audio`
  - ✅ **PLAYER APPEARS** with audio controls 🔊

### Step 4: Test Multiple Downloads
While watching first download:
```
Submit Download 2:
URL: https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3
Type: Audio
Quality: Excellent
```
- **Expected**:
  - ✅ Second item appears in queue
  - ✅ Both show "📥 Downloading"
  - ✅ Can submit while first is still downloading

### Step 5: Test Media Player
When player appears:
- ✅ Click Play button → audio plays
- ✅ Click Pause button → stops
- ✅ Drag progress bar → seeks
- ✅ Adjust volume → works

### Step 6: Test Playlist
When multiple downloads complete:
- ✅ Playlist appears on right side
- ✅ Click playlist item → plays that file
- ✅ Click Previous/Next buttons → switches between tracks
- ✅ Current track highlighted in playlist

---

## 📊 What You Should See

### Queue Section (appears after first download):
```
📥 Active Downloads
├─ 🎵 AUDIO - ABC12 (🟡 Queued)
│  Quality: 🎧 Good (192kbps) - 1MB/min
│  ❌ Remove
│
└─ 🎵 AUDIO - DEF34 (📥 Downloading)
   Quality: 🎧 Excellent (320kbps) - 1.5MB/min
   ❌ Remove
```

### Player Section (appears when first download completes):
```
🎬 Media Player
┌─────────────────────────────────┐
│  [🔊 AUDIO PLAYER]             │
│  |----●--------|              │
│  0:00          3:45            │
└─────────────────────────────────┘
⏮️ Previous | ▶️ Play | ⏭️ Next

🎶 Playlist
├─ 🎵 ABC12 (currently playing)
└─ 🎵 DEF34 (click to play)
```

---

## 🐛 Troubleshooting

### Player doesn't appear after download completes

**Check 1**: Open DevTools Console (F12)
- Should see: `🎵 Creating media player for audio`
- Should see: `✅ Player section displayed`
- If not → Check browser errors (red text)

**Check 2**: Verify download completed
- In queue, should show: `✅ Ready`
- File should be visible in queue item

**Check 3**: Refresh page
- Sometimes takes a moment to render
- Refresh page → player should appear

### Multiple downloads not working

**Check 1**: Can you submit the form twice?
- First submit → should create task
- Second submit → should create different task
- Each should appear in queue with different ID

**Check 2**: Look at queue
- Should show multiple items
- Each should have independent status
- Each should have its own status badge

### Queue not showing

**Check 1**: Did you submit a download?
- Submit form → should show queue immediately
- If no queue appears → check browser console for errors

**Check 2**: Is JavaScript running?
- Check DevTools Console for logs
- Should see messages as you interact

---

## 📝 Console Messages Explained

```
✅ Added download: {taskId}
→ Download added to queue, polling started

🔄 Updated {taskId}: DOWNLOADING
→ Download is active, in progress

📊 Playable files: 1
→ System found 1 completed download ready to play

🎵 Creating media player for audio
→ Player being created with audio element

✅ Player section displayed
→ Player made visible on page

🔊 Audio player created
→ Audio HTML element successfully created
```

---

## ✅ Success Criteria

You'll know everything is working when:

1. ✅ Can submit download form
2. ✅ Queue appears with download item
3. ✅ Download progresses to completion
4. ✅ **Player appears automatically**
5. ✅ Can submit another download
6. ✅ Queue shows multiple items
7. ✅ Each download tracked independently
8. ✅ Player plays audio/video correctly
9. ✅ Playlist shows completed files
10. ✅ Can navigate with Previous/Next buttons

---

## 🚀 Ready to Test!

**Start here**: http://localhost:8000

**Open DevTools**: F12 → Console

**Submit download** and watch the magic happen! ✨
