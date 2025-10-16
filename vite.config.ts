import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import electron from 'vite-plugin-electron'
import renderer from 'vite-plugin-electron-renderer'
import path from 'path'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    react(),
    electron([
      {
        // Main process entry file
        entry: 'electron/main.ts',
        onstart(args) {
          args.startup()
        },
        vite: {
          build: {
            outDir: 'dist/electron',
            rollupOptions: {
              external: ['electron']
            }
          }
        }
      },
      {
        // Preload script
        entry: 'electron/preload.ts',
        onstart(args) {
          args.reload()
        },
        vite: {
          build: {
            outDir: 'dist/electron'
          }
        }
      }
    ]),
    renderer()
  ],
  
  // Path aliases
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
      '@components': path.resolve(__dirname, './src/components'),
      '@hooks': path.resolve(__dirname, './src/hooks'),
      '@stores': path.resolve(__dirname, './src/stores'),
      '@types': path.resolve(__dirname, './src/types'),
      '@utils': path.resolve(__dirname, './src/utils')
    }
  },
  
  // Server configuration
  server: {
    port: 5173,
    strictPort: true
  },
  
  // Build configuration
  build: {
    outDir: 'dist/web',
    emptyOutDir: true,
    target: 'esnext',
    minify: 'esbuild',
    sourcemap: true
  },
  
  // Optimization
  optimizeDeps: {
    include: ['react', 'react-dom', 'motion', 'zustand']
  }
})
