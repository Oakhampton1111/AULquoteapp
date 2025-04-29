import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'
import { visualizer } from 'rollup-plugin-visualizer'
import viteCompression from 'vite-plugin-compression'

// https://vite.dev/config/
export default defineConfig(({ command, mode }) => {
  // Load environment variables
  const env = loadEnv(mode, process.cwd(), '')
  const appEnv = process.env.APP_ENV || 'development'

  // Load shared environment variables
  const sharedEnv = loadEnv(mode, path.resolve(process.cwd(), '../config/shared'), '')

  // Load environment-specific variables
  const envSpecific = loadEnv(mode, path.resolve(process.cwd(), `../config/${appEnv}`), '')

  // Merge environment variables with priority
  const mergedEnv = {
    ...sharedEnv,
    ...envSpecific,
    ...env, // Local .env overrides everything
  }

  return {
    plugins: [
      react(),
      // Add bundle visualization in analyze mode
      mode === 'analyze' && visualizer({
        open: true,
        filename: 'dist/stats.html',
        gzipSize: true,
        brotliSize: true,
      }),
      // Add compression for production builds
      mode === 'production' && viteCompression({
        algorithm: 'gzip',
        ext: '.gz',
      }),
      // Add brotli compression for production builds
      mode === 'production' && viteCompression({
        algorithm: 'brotliCompress',
        ext: '.br',
      }),
    ].filter(Boolean),

    // Environment variable configuration
    define: {
      __APP_ENV__: JSON.stringify(appEnv),
      __APP_VERSION__: JSON.stringify(process.env.npm_package_version),
    },

    // Development server configuration
    server: {
      host: mergedEnv.HOST || 'localhost',
      port: parseInt(mergedEnv.PORT || '3000'),
      proxy: {
        '/api': {
          target: mergedEnv.VITE_API_URL || 'http://localhost:8000',
          changeOrigin: true,
        },
        '/ws': {
          target: mergedEnv.VITE_WS_URL || 'ws://localhost:8000',
          ws: true,
        },
      },
    },

    // Build configuration
    build: {
      outDir: 'dist',
      sourcemap: appEnv !== 'production',
      // Minification options
      minify: 'terser',
      terserOptions: {
        compress: {
          drop_console: mode === 'production',
          drop_debugger: mode === 'production',
        },
      },
      // Optimize chunks
      rollupOptions: {
        output: {
          manualChunks: {
            vendor: ['react', 'react-dom', 'react-router-dom'],
            ui: ['antd', '@ant-design/icons'],
            query: ['@tanstack/react-query'],
          },
          // Optimize chunk size
          chunkFileNames: (chunkInfo) => {
            const facadeModuleId = chunkInfo.facadeModuleId
              ? path.basename(chunkInfo.facadeModuleId).split('.')[0]
              : '';
            return `assets/[name]-[hash].js`;
          },
        },
      },
      // Increase the warning limit for chunk size
      chunkSizeWarningLimit: 1000,
    },

    // Resolve configuration
    resolve: {
      alias: {
        '@': path.resolve(__dirname, './src'),
        '@components': path.resolve(__dirname, './src/components'),
        '@hooks': path.resolve(__dirname, './src/hooks'),
        '@utils': path.resolve(__dirname, './src/utils'),
        '@services': path.resolve(__dirname, './src/services'),
      },
    },
  }
})
