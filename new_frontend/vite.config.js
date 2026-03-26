import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// The proxy rewrites /api/... → http://localhost:8000/...
// So your React code calls /api/brightness/absolute
// and Vite forwards it to http://localhost:8000/brightness/absolute
// This means no CORS errors in development and no hardcoded URLs in components.

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
    },
  },
})
