import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  base: "./", // in built index.html use paths starting at . instead of /
  build: {
    outDir: 'dist-react' // change from default build dir of dist
  },
  server: {
    port: 5123,
    strictPort: true
  }
})
