// Read API URL from environment or use default
// Netlify: set environment variable VITE_API_URL or REACT_APP_API_URL
const API = window.__API_URL__ || 'http://localhost:8000'

const form = document.getElementById('downloadForm')
const statusEl = document.getElementById('status')
const statusSection = document.getElementById('statusSection')
const mediaSelect = document.getElementById('media_type')
const qualitySelect = document.getElementById('quality')
const qualityLabel = document.getElementById('qualityLabel')

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
  
  const url = document.getElementById('url').value.trim()
  const mediaType = mediaSelect.value
  const quality = qualitySelect.value
  
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
      const errBody = await res.json()
      throw new Error(errBody.detail || JSON.stringify(errBody))
    }
    
    const body = await res.json()
    const taskId = body.task_id
    const shortId = taskId.substring(0, 8).toUpperCase()
    
    statusEl.innerHTML = `
      <p class="status-info">📋 Task ID: <code>${shortId}</code></p>
      <p class="status-info">📊 Format: ${formats[mediaType][quality]}</p>
    `
    
    pollStatus(taskId, mediaType, quality)
  } catch (err) {
    statusEl.innerHTML = `<p class="status-error">❌ Error: ${err.message}</p>`
  }
})

let pollInterval = null

async function pollStatus(taskId, mediaType, quality) {
  statusEl.innerHTML = `<p class="status-pending">⏳ Processing... (0s)</p>`
  
  let elapsed = 0
  
  pollInterval = setInterval(async () => {
    elapsed++
    
    try {
      const res = await fetch(`${API}/status/${taskId}`)
      const body = await res.json()
      
      if (body.state === 'PENDING') {
        statusEl.innerHTML = `<p class="status-pending">⏳ Queued (${elapsed}s)...</p>`
      } else if (body.state === 'DOWNLOADING') {
        statusEl.innerHTML = `<p class="status-pending">📥 Downloading (${elapsed}s)... This may take a while depending on file size.</p>`
      } else if (body.state === 'SUCCESS') {
        clearInterval(pollInterval)
        const result = body.result || {}
        const filename = result.filename
        const fileSize = result.size ? (result.size / 1024 / 1024).toFixed(2) + ' MB' : 'unknown size'
        const downloadUrl = `${API}/file/${taskId}`
        
        statusEl.innerHTML = `
          <p class="status-success">✅ Download Ready!</p>
          <p class="status-info">📄 File: <code>${filename}</code></p>
          <p class="status-info">📊 Size: ${fileSize}</p>
          <p class="status-info">⚙️ Quality: ${formats[mediaType][quality]}</p>
          <a href="${downloadUrl}" class="btn btn-download" download>
            📥 Download File
          </a>
        `
      } else if (body.state === 'FAILURE') {
        clearInterval(pollInterval)
        const error = body.error || 'Unknown error'
        statusEl.innerHTML = `<p class="status-error">❌ Failed: ${error}</p>`
      }
    } catch (err) {
      clearInterval(pollInterval)
      statusEl.innerHTML = `<p class="status-error">❌ Error: ${err.message}</p>`
    }
  }, 2000)
}

