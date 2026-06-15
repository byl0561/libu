import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5173,
    proxy: {
      // dev: forward API calls to the local FastAPI server
      '/api': 'http://127.0.0.1:8000',
    },
  },
})
