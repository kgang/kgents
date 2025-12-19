import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { visualizer } from 'rollup-plugin-visualizer';
import path from 'path';

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    react(),
    visualizer({
      filename: 'dist/bundle-stats.html',
      gzipSize: true,
      brotliSize: true,
    }),
  ],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
      // Service module aliases (AD-009 Metaphysical Fullstack)
      // These point to future co-located frontend components in services/
      '@brain': path.resolve(__dirname, '../services/brain/web'),
      '@town': path.resolve(__dirname, '../services/town/web'),
      '@atelier': path.resolve(__dirname, '../services/atelier/web'),
      '@park': path.resolve(__dirname, '../services/park/web'),
      '@gardener': path.resolve(__dirname, '../services/gardener/web'),
      '@coalition': path.resolve(__dirname, '../services/coalition/web'),
      '@gestalt': path.resolve(__dirname, '../services/gestalt/web'),
      // Shared components stay central
      '@shared': path.resolve(__dirname, './src/shared'),
    },
  },
  // Optimize heavy deps - pre-bundle to avoid transform time
  optimizeDeps: {
    include: [
      'lucide-react',
      'react',
      'react-dom',
      'react-router-dom',
      'framer-motion',
      'zustand',
      'axios',
      'immer',
      'nanoid',
    ],
    // Exclude pixi.js (lazy-loaded for Town visualization)
    // three.js ecosystem removed entirely for performance
    exclude: ['pixi.js', '@pixi/react'],
  },
  server: {
    port: 3000,
    // Warmup critical files on server start
    warmup: {
      clientFiles: [
        './src/main.tsx',
        './src/App.tsx',
        './src/shell/Shell.tsx',
        './src/shell/ShellProvider.tsx',
        './src/constants/jewels.ts',
        './src/constants/icons.ts',
      ],
    },
    proxy: {
      '/v1': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/agentese': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/health': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/ws': {
        target: 'ws://localhost:8000',
        ws: true,
        changeOrigin: true,
      },
    },
  },
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          pixi: ['pixi.js', '@pixi/react'],
          vendor: ['react', 'react-dom', 'react-router-dom', 'zustand'],
        },
      },
    },
  },
});
