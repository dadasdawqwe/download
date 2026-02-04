// Environment configuration
// This file sets the API URL for the frontend
// For local development: uses same origin (localhost:8000)
// For production: set VITE_API_URL environment variable

window.__API_URL__ = (typeof process !== 'undefined' && process.env && process.env.VITE_API_URL) 
  ? process.env.VITE_API_URL 
  : '';
