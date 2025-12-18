import { defineConfig, devices } from '@playwright/test';

/**
 * Playwright E2E test configuration for Agent Town web UI.
 *
 * Implements Playwright Witness Protocol:
 * - Density matrix projects (compact/comfortable/spacious)
 * - Determinism settings (animations, timezone)
 * - CI-optimized artifact collection
 *
 * @see plans/playwright-witness-protocol.md
 * @see https://playwright.dev/docs/test-configuration
 */

// Density viewport configurations aligned with elastic-ui-patterns.md
const DENSITY_VIEWPORTS = {
  compact: { width: 375, height: 667 }, // Mobile (iPhone SE)
  comfortable: { width: 768, height: 1024 }, // Tablet (iPad)
  spacious: { width: 1440, height: 900 }, // Desktop
};

export default defineConfig({
  testDir: './e2e',
  /* Run tests in files in parallel */
  fullyParallel: true,
  /* Fail the build on CI if you accidentally left test.only in the source code */
  forbidOnly: !!process.env.CI,
  /* Retry on CI only */
  retries: process.env.CI ? 2 : 0,
  /* Opt out of parallel tests on CI */
  workers: process.env.CI ? 1 : undefined,
  /* Reporter to use. See https://playwright.dev/docs/test-reporters */
  reporter: process.env.CI
    ? [['github'], ['html', { open: 'never' }]]
    : [['html', { open: 'on-failure' }]],

  /* Global timeout */
  timeout: 30000,
  expect: {
    timeout: 10000,
    toHaveScreenshot: {
      maxDiffPixelRatio: 0.02,
      animations: 'disabled',
    },
  },

  /* Shared settings for all the projects below. See https://playwright.dev/docs/api/class-testoptions. */
  use: {
    /* Base URL to use in actions like `await page.goto('/')`. */
    baseURL: 'http://localhost:3000',

    /* Collect trace when retrying the failed test. See https://playwright.dev/docs/trace-viewer */
    trace: process.env.CI ? 'on-first-retry' : 'retain-on-failure',

    /* Video on failure for debugging */
    video: process.env.CI ? 'retain-on-failure' : 'off',

    /* Screenshot on failure */
    screenshot: 'only-on-failure',

    /* Determinism: reduce motion for consistent screenshots */
    reducedMotion: 'reduce',

    /* Determinism: consistent timezone */
    timezoneId: 'UTC',

    /* Determinism: consistent locale */
    locale: 'en-US',
  },

  /* Configure projects for density matrix + browsers */
  projects: [
    // ==========================================================================
    // Density Matrix Projects (Chromium)
    // Run with: npx playwright test --project density-compact
    // ==========================================================================
    {
      name: 'density-compact',
      use: {
        ...devices['iPhone SE'],
        viewport: DENSITY_VIEWPORTS.compact,
      },
      grep: [/@e2e/, /@visual/, /@smoke/],
    },
    {
      name: 'density-comfortable',
      use: {
        ...devices['iPad (gen 7)'],
        viewport: DENSITY_VIEWPORTS.comfortable,
      },
      grep: [/@e2e/, /@visual/, /@smoke/],
    },
    {
      name: 'density-spacious',
      use: {
        ...devices['Desktop Chrome'],
        viewport: DENSITY_VIEWPORTS.spacious,
      },
      grep: [/@e2e/, /@visual/, /@smoke/],
    },

    // ==========================================================================
    // Default Chromium (all tests)
    // ==========================================================================
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },

    // ==========================================================================
    // Contract Tests (API-only, faster)
    // Run with: npx playwright test --project contracts
    // ==========================================================================
    {
      name: 'contracts',
      use: { ...devices['Desktop Chrome'] },
      grep: /@contract/,
      testMatch: '**/agentese-contracts.spec.ts',
    },

    // ==========================================================================
    // Chaos Suite (isolated, deterministic seeds)
    // Run with: npx playwright test --project chaos
    // ==========================================================================
    {
      name: 'chaos',
      use: {
        ...devices['Desktop Chrome'],
        viewport: DENSITY_VIEWPORTS.spacious,
      },
      grep: /@chaos/,
      testMatch: '**/chaos/**/*.spec.ts',
      // Chaos tests may be slower
      timeout: 60000,
    },

    // ==========================================================================
    // Visual Regression (screenshots baseline)
    // Run with: npx playwright test --project visual
    // ==========================================================================
    {
      name: 'visual',
      use: {
        ...devices['Desktop Chrome'],
        viewport: DENSITY_VIEWPORTS.spacious,
      },
      grep: /@visual/,
    },

    // ==========================================================================
    // Smoke Tests (quick sanity check)
    // Run with: npx playwright test --project smoke
    // ==========================================================================
    {
      name: 'smoke',
      use: { ...devices['Desktop Chrome'] },
      grep: /@smoke/,
      // Smoke should be fast
      timeout: 15000,
    },

    // ==========================================================================
    // Cross-Browser (Firefox/WebKit) - Weekly CI only
    // Run with: npx playwright test --project firefox
    // ==========================================================================
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
      grep: /@smoke/, // Only smoke tests for cross-browser
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
      grep: /@smoke/, // Only smoke tests for cross-browser
    },
  ],

  /* Run your local dev server before starting the tests */
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
    timeout: 120 * 1000, // 2 minutes for server startup
  },
});
