import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import fs from 'fs'
import path from 'path'
import os from 'os'

// ═══════════════════════════════════════════════════════════════
// VITE CONFIG & AUTH MIDDLEWARE
// Middleware ini membaca api-keys.json untuk memvalidasi login
// ═══════════════════════════════════════════════════════════════

export default defineConfig({
  plugins: [
    react(),
    {
      name: 'nexus-auth-api',
      configureServer(server) {
        server.middlewares.use('/api/auth', (req, res, next) => {
          if (req.method === 'POST') {
            let body = ''
            req.on('data', chunk => body += chunk)
            req.on('end', () => {
              try {
                const { key } = JSON.parse(body)
                const keyFile = process.env.NEXUS_KEY_FILE || path.join(os.homedir(), '.nexus-agent', 'api-keys.json')
                
                if (fs.existsSync(keyFile)) {
                  const data = JSON.parse(fs.readFileSync(keyFile, 'utf-8'))
                  const found = data.keys.find(k => k.key === key && k.active)
                  if (found) {
                    res.writeHead(200, { 'Content-Type': 'application/json' })
                    res.end(JSON.stringify({ success: true }))
                    return
                  }
                }
                res.writeHead(401, { 'Content-Type': 'application/json' })
                res.end(JSON.stringify({ success: false, error: 'Invalid or Revoked API Key' }))
              } catch (e) {
                res.writeHead(500, { 'Content-Type': 'application/json' })
                res.end(JSON.stringify({ success: false, error: 'Server error' }))
              }
            })
          } else {
            next()
          }
        })
      }
    }
  ]
})
