import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import path from 'path'


// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), tailwindcss()],
  base: "./", // in built index.html use paths starting at . instead of /
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src/ui"),
    },
  },
  build: {
    outDir: 'dist-react' // change from default build dir of dist
  },
  server: {
    port: 5123,
    strictPort: true
  }
})
