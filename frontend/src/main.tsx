import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import './index.css'

// StrictMode removed: lightweight-charts doesn't survive double-invoke in dev
ReactDOM.createRoot(document.getElementById('root')!).render(
  <App />
)

