import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import App from './App.jsx'
import './index.css'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <App />
  </StrictMode>,
)

console.log('%c⬡ NEXUS v3.0 — AI Agent Dashboard', 'color:#00ffe0;font-size:14px;font-weight:bold')
