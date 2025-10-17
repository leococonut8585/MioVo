import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import electron from 'vite-plugin-electron'
import renderer from 'vite-plugin-electron-renderer'
import path from 'path'

// Check if we're in Replit environment (cloud) or local development
const isReplit = process.env.REPL_ID !== undefined
const isElectronMode = process.env.ELECTRON_MODE === 'true'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    react(),
    // Only use Electron plugins when not in Replit or explicitly enabled
    ...(!isReplit || isElectronMode ? [
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
    ] : [])
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
    host: '0.0.0.0',
    port: 5000,
    strictPort: true,
    allowedHosts: true, // Allow all hosts in Replit environment
    hmr: {
      clientPort: 443,
      protocol: 'wss'
    }
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
