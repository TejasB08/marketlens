import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        configure(proxy) {
          proxy.prependListener('error', (_error, request) => {
            const path = request.url?.split('?', 1)[0]
            if (path?.startsWith('/api/v1/auth/')) request.url = path
          })
        },
      },
    },
  },
})
