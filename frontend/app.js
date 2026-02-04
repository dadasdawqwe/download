// Read API URL from environment or fall back to same origin
// Netlify: set environment variable VITE_API_URL to your backend URL.
// If unset, `env.js` will set an empty string and we use the page origin.
console.log('🚀 App.js loading...')
const defaultApi = window.location.protocol + '//' + window.location.host
const API = (window.__API_URL__ && window.__API_URL__.length) ? window.__API_URL__ : defaultApi
console.log('API URL:', API)

const form = document.getElementById('downloadForm')
const statusEl = document.getElementById('status')
const statusSection = document.getElementById('statusSection')
const mediaSelect = document.getElementById('media_type')
const qualitySelect = document.getElementById('quality')
const qualityLabel = document.getElementById('qualityLabel')

// Media player elements
const playerSection = document.getElementById('playerSection')
const mediaPlayer = document.getElementById('mediaPlayer')
const playlistSection = document.getElementById('playlistItems')
const playPauseBtn = document.getElementById('playPauseBtn')
const prevBtn = document.getElementById('prevBtn')
const nextBtn = document.getElementById('nextBtn')

// Queue elements
const queueSection = document.getElementById('queueSection')
const downloadQueue = document.getElementById('downloadQueue')

// Format descriptions
const formats = {
  video: {
    '1080p': '📺 1080p (Full HD) - 500MB+/hour',
    '720p': '📺 720p (HD) - 250MB/hour',
    '360p': '📺 360p (SD) - 100MB/hour'
  },
  audio: {
    'excellent': '🎧 Excellent (320kbps) - 1.5MB/min',
    'good': '🎧 Good (192kbps) - 1MB/min',
    'ok': '🎧 OK (128kbps) - 0.8MB/min'
  }
}

// Download queue management
const downloadManager = {
  downloads: new Map(), // taskId -> download object
  currentPlayerIndex: 0,
  
  addDownload(taskId, url, mediaType, quality) {
    this.downloads.set(taskId, {
      taskId,
      url,
      mediaType,
      quality,
      state: 'PENDING',
      result: null,
      pollInterval: null
    })
    console.log(`✅ Added download: ${taskId} (${mediaType}/${quality})`)
    this.updateQueueUI()
  },
  
  removeDownload(taskId) {
    const download = this.downloads.get(taskId)
    if (download && download.pollInterval) {
      clearInterval(download.pollInterval)
    }
    this.downloads.delete(taskId)
    this.updateQueueUI()
  },
  
  updateDownloadState(taskId, state, result = null, error = null) {
    const download = this.downloads.get(taskId)
    if (download) {
      download.state = state
      if (result) download.result = result
      if (error) download.error = error
      console.log(`🔄 Updated ${taskId}: ${state}`, { result, error })
      this.updateQueueUI()
      this.updatePlayerIfNeeded()
    }
  },
  
  updateQueueUI() {
    queueSection.style.display = this.downloads.size > 0 ? 'block' : 'none'
    
    downloadQueue.innerHTML = ''
    
    Array.from(this.downloads.entries()).forEach(([taskId, download]) => {
      const shortId = taskId.substring(0, 8).toUpperCase()
      const mediaIcon = download.mediaType === 'audio' ? '🎵' : '🎬'
      const statusBadge = this.getStatusBadge(download.state)
      
      const item = document.createElement('div')
      item.className = 'queue-item'
      item.innerHTML = `
        <div class="queue-item-info">
          <div class="queue-item-title">${mediaIcon} ${download.mediaType.toUpperCase()} - ${shortId}</div>
          <div class="queue-item-details">Quality: ${formats[download.mediaType][download.quality]}</div>
          ${download.result ? `<div class="queue-item-details">📄 ${download.result.filename}</div>` : ''}
        </div>
        <div class="queue-item-status ${statusBadge}">${this.getStatusText(download.state)}</div>
        <div class="queue-item-actions">
          ${download.state === 'SUCCESS' ? `
            <button class="queue-item-btn btn-success" onclick="downloadManager.playDownload('${taskId}')">▶️ Play</button>
            <a href="${API}/file/${taskId}" class="queue-item-btn" download>📥 Download</a>
          ` : `
            <button class="queue-item-btn" onclick="downloadManager.removeDownload('${taskId}')">❌ Remove</button>
          `}
        </div>
      `
      downloadQueue.appendChild(item)
    })
  },
  
  getStatusText(state) {
    const statusMap = {
      'PENDING': '⏳ Queued',
      'DOWNLOADING': '📥 Downloading',
      'SUCCESS': '✅ Ready',
      'FAILURE': '❌ Failed'
    }
    return statusMap[state] || state
  },
  
  getStatusBadge(state) {
    const badgeMap = {
      'PENDING': 'status-pending',
      'DOWNLOADING': 'status-downloading',
      'SUCCESS': 'status-success-badge',
      'FAILURE': 'status-error-badge'
    }
    return badgeMap[state] || ''
  },
  
  getPlayableDownloads() {
    return Array.from(this.downloads.values())
      .filter(d => d.state === 'SUCCESS' && (d.mediaType === 'audio' || d.mediaType === 'video'))
  },
  
  playDownload(taskId) {
    const download = this.downloads.get(taskId)
    if (!download || download.state !== 'SUCCESS') return
    
    // Mark as active playlist item
    document.querySelectorAll('.playlist-item').forEach(item => {
      item.classList.remove('active')
      if (item.dataset.taskId === taskId) {
        item.classList.add('active')
      }
    })
    
    // Create player if needed
    this.createMediaPlayer(download)
  },
  
  createMediaPlayer(download) {
    try {
      const downloadUrl = `${API}/file/${download.taskId}`
      console.log(`🎵 Creating media player for ${download.mediaType}:`, downloadUrl)
      console.log(`Download object:`, download)
      
      // Ensure mediaPlayer element exists
      if (!mediaPlayer) {
        console.error('❌ mediaPlayer element not found in DOM!')
        return
      }
      
      mediaPlayer.innerHTML = ''
      
      if (download.mediaType === 'audio') {
        const audio = document.createElement('audio')
        audio.src = downloadUrl
        audio.controls = true
        audio.style.width = '100%'
        audio.crossOrigin = 'anonymous'
        mediaPlayer.appendChild(audio)
        
        console.log('🔊 Audio player created')
        
        // Sync play/pause button
        audio.addEventListener('play', () => {
          playPauseBtn.textContent = '⏸️ Pause'
        })
        audio.addEventListener('pause', () => {
          playPauseBtn.textContent = '▶️ Play'
        })
      } else {
        const video = document.createElement('video')
        video.src = downloadUrl
        video.controls = true
        video.style.width = '100%'
        video.style.maxHeight = '400px'
        video.crossOrigin = 'anonymous'
        mediaPlayer.appendChild(video)
        
        console.log('🎬 Video player created')
        
        // Sync play/pause button
        video.addEventListener('play', () => {
          playPauseBtn.textContent = '⏸️ Pause'
        })
        video.addEventListener('pause', () => {
          playPauseBtn.textContent = '▶️ Play'
        })
      }
      
      // Make absolutely sure the player section is visible
      if (!playerSection) {
        console.error('❌ playerSection element not found in DOM!')
        return
      }
      playerSection.style.display = 'block'
      console.log('✅ Player section displayed')
      this.updatePlaylistUI()
    } catch (err) {
      console.error('❌ Error creating media player:', err)
    }
  },
  
  updatePlayerIfNeeded() {
    try {
      const playable = this.getPlayableDownloads()
      console.log(`📊 updatePlayerIfNeeded called - Playable files: ${playable.length}`)
      console.log(`   All downloads:`, Array.from(this.downloads.values()).map(d => ({ taskId: d.taskId.substring(0, 8), state: d.state, mediaType: d.mediaType })))
      
      // Always update player if we have playable downloads
      if (playable.length > 0) {
        console.log('🎬 Showing player with first completed file...', playable[0])
        this.createMediaPlayer(playable[0])
      } else {
        console.log('⚠️  No playable downloads found')
      }
    } catch (err) {
      console.error('❌ Error in updatePlayerIfNeeded:', err)
    }
  },
  
  updatePlaylistUI() {
    const playable = this.getPlayableDownloads()
    playlistSection.innerHTML = ''
    
    playable.forEach((download, index) => {
      const shortId = download.taskId.substring(0, 8).toUpperCase()
      const icon = download.mediaType === 'audio' ? '🎵' : '🎬'
      const item = document.createElement('div')
      item.className = 'playlist-item'
      item.dataset.taskId = download.taskId
      item.innerHTML = `
        <span class="playlist-item-icon">${icon}</span>
        <span class="playlist-item-name">${shortId} - ${download.result?.filename || 'Loading...'}</span>
      `
      item.onclick = () => this.playDownload(download.taskId)
      playlistSection.appendChild(item)
    })
  }
}

// Initialize player controls
playPauseBtn.addEventListener('click', () => {
  const player = mediaPlayer.querySelector('audio') || mediaPlayer.querySelector('video')
  if (player) {
    if (player.paused) {
      player.play()
    } else {
      player.pause()
    }
  }
})

prevBtn.addEventListener('click', () => {
  const playable = downloadManager.getPlayableDownloads()
  if (playable.length === 0) return
  downloadManager.currentPlayerIndex = (downloadManager.currentPlayerIndex - 1 + playable.length) % playable.length
  downloadManager.createMediaPlayer(playable[downloadManager.currentPlayerIndex])
})

nextBtn.addEventListener('click', () => {
  const playable = downloadManager.getPlayableDownloads()
  if (playable.length === 0) return
  downloadManager.currentPlayerIndex = (downloadManager.currentPlayerIndex + 1) % playable.length
  downloadManager.createMediaPlayer(playable[downloadManager.currentPlayerIndex])
})

// Toggle quality options based on media type
mediaSelect.addEventListener('change', () => {
  const fmt = formats[mediaSelect.value]
  qualitySelect.innerHTML = Object.keys(fmt)
    .map(q => `<option value="${q}">${fmt[q]}</option>`)
    .join('')
  qualityLabel.textContent = mediaSelect.value === 'audio' ? '🎧 Audio Quality' : '⚙️ Video Quality'
})

form.addEventListener('submit', async (e) => {
  e.preventDefault()
  console.log('📝 Form submitted!')
  
  const url = document.getElementById('url').value.trim()
  const mediaType = mediaSelect.value
  const quality = qualitySelect.value
  console.log('📥 Download requested:', { url: url.substring(0, 30) + '...', mediaType, quality })
  
  if (!url) {
    statusSection.style.display = 'block'
    statusEl.innerHTML = '<p class="status-error">❌ Please enter a URL</p>'
    return
  }
  
  statusSection.style.display = 'block'
  statusEl.innerHTML = '<p class="status-pending">⏳ Validating and starting download...</p>'
  
  const payload = { url, media_type: mediaType, quality }

  try {
    const res = await fetch(`${API}/download`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })
    
    if (!res.ok) {
      let errMsg = 'Server error'
      try {
        const errBody = await res.json()
        errMsg = errBody.detail || JSON.stringify(errBody)
      } catch (_) {
        try {
          errMsg = await res.text()
        } catch (_) {}
      }
      throw new Error(errMsg)
    }
    
    const body = await res.json()
    const taskId = body.task_id
    const shortId = taskId.substring(0, 8).toUpperCase()
    
    // Add to download manager
    downloadManager.addDownload(taskId, url, mediaType, quality)
    
    statusEl.innerHTML = `
      <p class="status-info">📋 Task ID: <code>${shortId}</code></p>
      <p class="status-info">📊 Format: ${formats[mediaType][quality]}</p>
      <p class="status-info">✅ Download added to queue. Multiple downloads are supported!</p>
    `
    
    // Clear form
    document.getElementById('url').value = ''
    
    pollStatus(taskId, mediaType, quality)
  } catch (err) {
    // Helpful hint when network-level failure occurs
    const hint = err.message && err.message.toLowerCase().includes('failed to fetch')
      ? `Failed to reach API at ${API}. Check backend URL, CORS, and HTTPS.`
      : err.message
    statusEl.innerHTML = `<p class="status-error">❌ Error: ${hint}</p>`
  }
})

let pollIntervals = new Map()

async function pollStatus(taskId, mediaType, quality) {
  downloadManager.updateDownloadState(taskId, 'PENDING')
  
  let elapsed = 0
  let maxAttempts = 300  // 10 minutes with 2s interval
  let attempts = 0
  
  const pollInterval = setInterval(async () => {
    elapsed++
    attempts++
    
    try {
      const res = await fetch(`${API}/status/${taskId}`)
      if (!res.ok) {
        throw new Error(`HTTP ${res.status}`)
      }
      
      const body = await res.json()
      console.log(`🔍 Poll response for ${taskId.substring(0,8)}: state=${body.state}, has result=${!!body.result}`)
      
      const download = downloadManager.downloads.get(taskId)
      if (!download) {
        clearInterval(pollInterval)
        return
      }
      
      // Handle different states
      if (body.state === 'PENDING' || body.state === 'QUEUED') {
        downloadManager.updateDownloadState(taskId, 'PENDING')
      } else if (body.state === 'DOWNLOADING') {
        downloadManager.updateDownloadState(taskId, 'DOWNLOADING')
      } else if (body.state === 'SUCCESS') {
        clearInterval(pollInterval)
        pollIntervals.delete(taskId)
        // Extract result object - API returns result at top level
        const result = body.result || {}
        console.log('✅ Setting state to SUCCESS with result:', result)
        downloadManager.updateDownloadState(taskId, 'SUCCESS', result)
        console.log('✅ Download complete:', taskId, result)
      } else if (body.state === 'FAILURE') {
        clearInterval(pollInterval)
        pollIntervals.delete(taskId)
        const error = body.error || 'Unknown error'
        downloadManager.updateDownloadState(taskId, 'FAILURE', null, error)
        console.log('❌ Download failed:', taskId, error)
      }
    } catch (err) {
      console.error('Poll error:', err.message)
      if (attempts >= maxAttempts) {
        clearInterval(pollInterval)
        pollIntervals.delete(taskId)
        downloadManager.updateDownloadState(taskId, 'FAILURE', null, `Timeout after ${elapsed}s: ${err.message}`)
      }
    }
  }, 2000)  // Poll every 2 seconds
  
  pollIntervals.set(taskId, pollInterval)
}

