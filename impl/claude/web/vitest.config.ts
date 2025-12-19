import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';
import path from 'path';

/**
 * Vitest Configuration for AI Agent Development
 *
 * Optimizations:
 * ==============
 * 1. Parallel execution - isolate: true for safe parallelism
 * 2. Fast feedback - bail on first failure in CI
 * 3. Clear output - verbose reporter for debugging
 * 4. Caching - reuse transformed modules
 * 5. Smart watching - only re-run affected tests
 *
 * Test Organization:
 * ==================
 * tests/
 *   unit/          - Fast, isolated unit tests (<100ms each)
 *   integration/   - Tests with real dependencies
 *   e2e/           - End-to-end tests (Playwright)
 *
 * Run Commands:
 * =============
 * npm test                    - Watch mode (development)
 * npm test -- --run           - Single run (CI)
 * npm test -- --run --bail 1  - Stop on first failure
 * npm run test:coverage       - Coverage report
 * npm run test:ui             - Visual UI
 */
export default defineConfig({
  plugins: [react()],
  test: {
    // ==========================================================================
    // Environment
    // ==========================================================================
    environment: 'jsdom',
    globals: true, // Expose describe, it, expect globally
    setupFiles: ['./tests/setup.ts'],

    // ==========================================================================
    // Test Discovery
    // ==========================================================================
    include: ['tests/**/*.{test,spec}.{js,ts,jsx,tsx}'],
    exclude: [
      'node_modules/**',
      'dist/**',
      'e2e/**', // E2E tests run via Playwright
    ],

    // ==========================================================================
    // Execution Optimizations (AI Agent Friendly)
    // ==========================================================================

    // CRITICAL: Limit workers to prevent memory explosion
    // Default spawns workers = CPU cores, each loading ~4GB with heavy deps
    pool: 'forks',
    poolOptions: {
      forks: {
        maxForks: 2, // Max 2 parallel workers (~8GB max)
        minForks: 1,
        isolate: false, // Reuse worker processes between test files
      },
    },

    // Dependency optimization - don't transform heavy deps
    deps: {
      optimizer: {
        web: {
          // Pre-bundle these so they're not re-transformed per worker
          include: ['pixi.js', '@pixi/react', 'framer-motion', 'lucide-react'],
        },
      },
    },

    // Sequential execution for stability (React Testing Library needs this)
    // Enable parallel with `npm run test:run -- --pool=threads` if needed
    sequence: {
      shuffle: false,
    },

    // Timeout settings (generous for AI agent testing)
    testTimeout: 10000, // 10s per test
    hookTimeout: 10000, // 10s for setup/teardown

    // ==========================================================================
    // Reporter Configuration
    // ==========================================================================
    reporters: process.env.CI
      ? ['basic', 'json'] // Minimal output in CI
      : ['verbose'], // Detailed output for development

    // Output directory for reports
    outputFile: {
      json: './coverage/test-results.json',
    },

    // ==========================================================================
    // Watch Mode Optimizations
    // ==========================================================================
    watchExclude: ['node_modules/**', 'dist/**', 'coverage/**'],

    // ==========================================================================
    // Failure Handling
    // ==========================================================================

    // In CI, bail on first failure for faster feedback
    bail: process.env.CI ? 1 : 0,

    // Retry flaky tests (but only in CI)
    retry: process.env.CI ? 2 : 0,

    // ==========================================================================
    // Coverage Configuration
    // ==========================================================================
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html', 'lcov'],
      include: ['src/**/*.{ts,tsx}'],
      exclude: [
        'src/main.tsx',
        'src/vite-env.d.ts',
        'src/**/*.d.ts',
        'src/**/*.test.{ts,tsx}',
        'src/**/*.spec.{ts,tsx}',
      ],
      // Coverage thresholds (warn, don't fail)
      thresholds: {
        statements: 60,
        branches: 50,
        functions: 60,
        lines: 60,
      },
      // Fail on threshold violations in CI
      thresholdAutoUpdate: false,
    },

    // ==========================================================================
    // Mocking
    // ==========================================================================
    // Note: mockReset/restoreMocks/clearMocks disabled to avoid breaking existing tests
    // These are handled in tests/setup.ts instead
    mockReset: false,
    restoreMocks: false,
    clearMocks: false,

    // ==========================================================================
    // Debugging Aids
    // ==========================================================================

    // Show full error output
    logHeapUsage: false,

    // Open browser on UI mode
    open: false,

    // Print slow tests
    slowTestThreshold: 150, // Tests > 150ms are highlighted
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
});
