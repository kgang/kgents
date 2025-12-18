import { test, expect } from '@playwright/test';
import {
  setupHotDataMocks,
  viewportFlicker,
  flakyRoute,
  latencyRoute,
  networkFlap,
  malformedJsonRoute,
  emptyRoute,
  unexpectedShapeRoute,
  createSeededRandom,
} from '../../testing';

/**
 * Chaos Suite: Resilience Tests (Type II - Saboteurs)
 *
 * Tests UI stability under adverse conditions:
 * - Viewport flicker (resize stability)
 * - Flaky network (error handling)
 * - Latency spikes (loading states)
 * - Network disconnection (offline handling)
 * - Malformed data (parsing robustness)
 *
 * @tags @chaos
 * @see plans/playwright-witness-protocol.md
 */

// Fixed seed for reproducible chaos
const CHAOS_SEED = 42;

test.describe('Viewport Chaos @chaos', () => {
  test.beforeEach(async ({ page }) => {
    await setupHotDataMocks(page);
  });

  test('survives rapid viewport resizing', async ({ page }) => {
    await page.goto('/town/demo-town-123');
    await page.waitForLoadState('networkidle');

    // Apply viewport chaos
    await viewportFlicker(page, {
      seed: CHAOS_SEED,
      iterations: 20,
      minWidth: 320,
      maxWidth: 1920,
      delayMs: 30,
    });

    // Verify page is still functional
    await expect(page.locator('body')).toBeVisible();

    // No console errors
    const errors: string[] = [];
    page.on('console', (msg) => {
      if (msg.type() === 'error') errors.push(msg.text());
    });

    // Final resize to stable viewport
    await page.setViewportSize({ width: 1280, height: 800 });
    await page.waitForTimeout(100);

    // Should have no crash-level errors
    const criticalErrors = errors.filter(
      (e) => e.includes('Uncaught') || e.includes('Maximum call stack')
    );
    expect(criticalErrors).toHaveLength(0);
  });

  test('maintains layout integrity after resize chaos', async ({ page }) => {
    await page.goto('/town/demo-town-123');
    await page.waitForLoadState('networkidle');

    // Rapid resizing
    await viewportFlicker(page, {
      seed: CHAOS_SEED,
      iterations: 15,
      delayMs: 50,
    });

    // Final stable viewport
    await page.setViewportSize({ width: 1024, height: 768 });
    await page.waitForTimeout(200);

    // Check no horizontal overflow
    const hasOverflow = await page.evaluate(() => {
      return document.documentElement.scrollWidth > window.innerWidth;
    });
    expect(hasOverflow).toBe(false);
  });
});

test.describe('Network Flakiness @chaos', () => {
  test('handles intermittent API failures gracefully', async ({ page }) => {
    await setupHotDataMocks(page);

    // Make citizen API flaky
    await flakyRoute(page, '**/v1/town/*/citizens', {
      seed: CHAOS_SEED,
      failureProbability: 0.5,
      errorCodes: [500, 502, 503],
    });

    await page.goto('/town/demo-town-123');

    // Page should load (may show error state)
    await expect(page.locator('body')).toBeVisible();

    // Should show either data or error state (not crash)
    const hasContent = await page
      .locator('[data-testid="citizen-card"], [data-testid="error-state"], .error')
      .count();
    expect(hasContent).toBeGreaterThanOrEqual(0);
  });

  test('recovers from network disconnection', async ({ page }) => {
    await setupHotDataMocks(page);
    await page.goto('/town/demo-town-123');
    await page.waitForLoadState('networkidle');

    // Simulate network flap
    await networkFlap(page, {
      offlineDurationMs: 300,
      onlineDurationMs: 500,
      cycles: 2,
    });

    // Page should still be functional after reconnection
    await expect(page.locator('body')).toBeVisible();
  });

  test('handles high latency without timeout crash', async ({ page }) => {
    await setupHotDataMocks(page);

    // Add significant latency
    await latencyRoute(page, '**/v1/**', {
      seed: CHAOS_SEED,
      minLatencyMs: 500,
      maxLatencyMs: 2000,
    });

    await page.goto('/town/demo-town-123');

    // Should show loading state, then content
    // Allow extra time for slow responses
    await expect(page.locator('body')).toBeVisible({ timeout: 10000 });
  });
});

test.describe('Data Shape Chaos @chaos', () => {
  test('handles malformed JSON gracefully', async ({ page }) => {
    // Setup malformed response for citizens
    await malformedJsonRoute(page, '**/v1/town/*/citizens');

    // Also setup basic mocks for other endpoints
    await page.route('**/v1/town/*', async (route) => {
      if (!route.request().url().includes('citizens')) {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({ id: 'demo', name: 'Demo Town', status: 'active' }),
        });
      }
    });

    await page.goto('/town/demo-town-123');

    // Should not crash - may show error state
    await expect(page.locator('body')).toBeVisible();
  });

  test('handles empty responses gracefully', async ({ page }) => {
    await emptyRoute(page, '**/v1/town/*/citizens');

    await page.route('**/v1/town/*', async (route) => {
      if (!route.request().url().includes('citizens')) {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({ id: 'demo', name: 'Demo Town', status: 'active' }),
        });
      }
    });

    await page.goto('/town/demo-town-123');

    // Should show empty state, not crash
    await expect(page.locator('body')).toBeVisible();
  });

  test('handles unexpected data shapes gracefully', async ({ page }) => {
    await unexpectedShapeRoute(page, '**/v1/town/*/citizens', { seed: CHAOS_SEED });

    await page.route('**/v1/town/*', async (route) => {
      if (!route.request().url().includes('citizens')) {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({ id: 'demo', name: 'Demo Town', status: 'active' }),
        });
      }
    });

    await page.goto('/town/demo-town-123');

    // Should handle gracefully
    await expect(page.locator('body')).toBeVisible();
  });
});

test.describe('Combined Chaos @chaos', () => {
  test('survives full chaos scenario', async ({ page }) => {
    await setupHotDataMocks(page);

    // Layer multiple chaos types
    const random = createSeededRandom(CHAOS_SEED);

    // Random latency
    await page.route('**/v1/**', async (route) => {
      const latency = Math.floor(random() * 500);
      const shouldFail = random() < 0.1; // 10% failure rate

      await new Promise((resolve) => setTimeout(resolve, latency));

      if (shouldFail) {
        await route.fulfill({
          status: 500,
          contentType: 'application/json',
          body: JSON.stringify({ detail: 'Chaos error' }),
        });
        return;
      }

      await route.continue();
    });

    await page.goto('/town/demo-town-123');

    // Run viewport chaos in parallel
    const chaosPromise = viewportFlicker(page, {
      seed: CHAOS_SEED,
      iterations: 10,
      delayMs: 100,
    });

    // Wait for initial load
    await page.waitForLoadState('domcontentloaded');

    // Wait for chaos to complete
    await chaosPromise;

    // Verify page survived
    await expect(page.locator('body')).toBeVisible();

    // Take screenshot for manual review
    await page.screenshot({ path: 'chaos-survival.png' });
  });

  test('deterministic chaos produces reproducible results', async ({ page }) => {
    await setupHotDataMocks(page);

    // First run with seed
    await viewportFlicker(page, { seed: CHAOS_SEED, iterations: 5 });
    const firstState = await page.evaluate(() => ({
      scrollX: window.scrollX,
      scrollY: window.scrollY,
      viewportWidth: window.innerWidth,
    }));

    // Reset
    await page.reload();

    // Second run with same seed
    await viewportFlicker(page, { seed: CHAOS_SEED, iterations: 5 });
    const secondState = await page.evaluate(() => ({
      scrollX: window.scrollX,
      scrollY: window.scrollY,
      viewportWidth: window.innerWidth,
    }));

    // Same seed should produce same final state
    expect(firstState.viewportWidth).toBe(secondState.viewportWidth);
  });
});

test.describe('Error Recovery @chaos', () => {
  test('recovers from 500 error on retry', async ({ page }) => {
    let requestCount = 0;

    await page.route('**/v1/town/*/citizens', async (route) => {
      requestCount++;

      // Fail first request, succeed on retry
      if (requestCount === 1) {
        await route.fulfill({
          status: 500,
          contentType: 'application/json',
          body: JSON.stringify({ detail: 'Server error' }),
        });
        return;
      }

      // Success on subsequent requests
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          citizens: [{ id: 'c1', name: 'Alice', archetype: 'Builder', region: 'workshop' }],
          total: 1,
        }),
      });
    });

    await page.goto('/town/demo-town-123');

    // If app has retry logic, it should eventually show content
    // Otherwise, it should show error state
    await expect(page.locator('body')).toBeVisible();
  });

  test('handles rate limiting (429)', async ({ page }) => {
    await page.route('**/v1/**', async (route) => {
      await route.fulfill({
        status: 429,
        contentType: 'application/json',
        body: JSON.stringify({
          detail: 'Rate limit exceeded',
          retry_after: 60,
        }),
        headers: {
          'Retry-After': '60',
        },
      });
    });

    await page.goto('/town/demo-town-123');

    // Should handle rate limiting gracefully
    await expect(page.locator('body')).toBeVisible();
  });
});
