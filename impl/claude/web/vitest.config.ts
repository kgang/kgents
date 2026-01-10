import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';
import path from 'path';

/**
 * Vitest Configuration for AI Agent Development
 *
 * MULTI-AGENT SAFE: This configuration supports concurrent test execution
 * by multiple Claude agents or CI runners.
 *
 * Optimizations (2025-01-10 - Enlightened Enhancement):
 * =====================================================
 * 1. Parallel execution - isolate: true for safe parallelism
 * 2. Fast feedback - bail on first failure in CI
 * 3. Clear output - verbose reporter for debugging
 * 4. Caching - reuse transformed modules
 * 5. Smart watching - only re-run affected tests
 * 6. Adaptive worker count - respects system load and KGENTS_TEST_WORKERS
 * 7. Optional happy-dom - 30-40% faster (KGENTS_FAST_DOM=1)
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
 *
 * Environment Variables:
 * ======================
 * KGENTS_TEST_WORKERS=N  - Override max worker count (default: 2)
 * KGENTS_FAST_DOM=1      - Use happy-dom instead of jsdom (faster)
 * CI=1                   - Enable CI mode (bail on first failure)
 */

// Adaptive worker count: respect KGENTS_TEST_WORKERS or default to 2
const maxWorkers = process.env.KGENTS_TEST_WORKERS
  ? parseInt(process.env.KGENTS_TEST_WORKERS, 10)
  : 2;

// Environment: happy-dom is 30-40% faster but has less browser compatibility
const testEnvironment = process.env.KGENTS_FAST_DOM === '1' ? 'happy-dom' : 'jsdom';

export default defineConfig({
  plugins: [react()],
  test: {
    // ==========================================================================
    // Environment
    // ==========================================================================
    environment: testEnvironment,
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
    // Execution Optimizations (Multi-Agent Safe)
    // ==========================================================================

    // CRITICAL: Limit workers to prevent memory explosion
    // Default spawns workers = CPU cores, each loading ~4GB with heavy deps
    // Multi-agent scenario: multiple agents may run tests simultaneously
    pool: 'forks',
    poolOptions: {
      forks: {
        maxForks: maxWorkers, // Configurable via KGENTS_TEST_WORKERS
        minForks: 1,
        // MUST be true: vi.mock() bleeds between test files when false
        // This was causing 262 test failures from mock contamination
        isolate: true,
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
