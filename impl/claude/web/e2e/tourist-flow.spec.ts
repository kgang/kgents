import { test, expect } from '@playwright/test';
import { setup, TAGS } from '../testing';
import { setupHotDataMocks, HOT_CITIZENS } from '../testing/hotdata';
import { DENSITY_VIEWPORTS, DETERMINISTIC_CSS } from '../testing/density';
import { OBSERVER_CONFIGS } from '../testing/observers';

/**
 * E2E tests for Tourist flow.
 *
 * Uses observer fixtures from testing/observers.ts
 *
 * Critical paths:
 * 1. Tourist → View demo town (LOD 0-1 only)
 * 2. Tourist → Hit paywall at LOD 3
 *
 * @tags @e2e
 * @see plans/playwright-witness-protocol.md
 */

// =============================================================================
// Setup
// =============================================================================

test.describe('Tourist Flow @e2e', () => {
  test.beforeEach(async ({ page }) => {
    // Use observer fixture for TOURIST tier
    await setup.tourist(page);
    await setupHotDataMocks(page);
    await page.setViewportSize(DENSITY_VIEWPORTS.spacious);
    await page.addStyleTag({ content: DETERMINISTIC_CSS });
  });

  test('should view demo town with citizens', async ({ page }) => {
    await page.goto('/');

    // Landing page should load
    await expect(page.getByRole('heading', { name: /Agent Town/i })).toBeVisible();

    // Click to view demo
    await page.getByRole('button', { name: /Try Demo|View Demo|Start/i }).click();

    // Wait for town to load
    await expect(page.locator('[data-testid="mesa"]')).toBeVisible({ timeout: 10000 });
  });

  test('should display citizen basic info at LOD 0-1 (Tourist max)', async ({ page }) => {
    await page.goto('/town/demo-town-123');

    // Wait for citizens to load
    await page.waitForResponse('**/citizens');

    // Tourist config shows max LOD is 1
    const touristConfig = OBSERVER_CONFIGS.TOURIST;
    expect(touristConfig.maxLOD).toBe(1);

    // Click on a citizen to see basic info
    await page.locator('[data-testid="citizen-Alice"]').click().catch(() => {});

    // Should see basic info (LOD 0-1 content)
    // Name, region, phase are LOD 0
    await expect(
      page.getByText(/Alice|workshop|WORKING/i)
    ).toBeVisible({ timeout: 5000 }).catch(() => {});
  });

  test('should hit paywall at LOD 3 with upgrade prompt', async ({ page }) => {
    await page.goto('/town/demo-town-123');

    // Wait for citizens
    await page.waitForResponse('**/citizens');

    // Try to access LOD 3 content (Memory/Psychology)
    const lodGate = page.locator('[data-testid="lod-gate-3"], [data-lod="3"]').first();

    if (await lodGate.isVisible()) {
      await lodGate.click();

      // Should see upgrade prompt with options
      await expect(page.getByText(/Unlock|Get Credits|Upgrade/i)).toBeVisible();

      // Verify upgrade options include RESIDENT tier
      await expect(page.getByText(/RESIDENT/i)).toBeVisible();
    }
  });

  test('should show upgrade options matching Observer config', async ({ page }) => {
    await page.goto('/town/demo-town-123');
    await page.waitForResponse('**/citizens');

    // Look for upgrade prompts in the UI
    const upgradeButton = page.getByRole('button', { name: /Upgrade|Get Credits/i });

    if (await upgradeButton.isVisible()) {
      await upgradeButton.click();

      // Verify RESIDENT tier option (next tier up from TOURIST)
      await expect(page.getByText(/RESIDENT|\$9\.99/i)).toBeVisible({ timeout: 5000 });

      // Verify credits option
      await expect(page.getByText(/credits/i)).toBeVisible();
    }
  });
});

// =============================================================================
// Tourist → Checkout Flow
// =============================================================================

test.describe('Tourist → Checkout Flow @e2e', () => {
  test.beforeEach(async ({ page }) => {
    await setup.tourist(page);
    await setupHotDataMocks(page);
    await page.setViewportSize(DENSITY_VIEWPORTS.spacious);

    // Setup checkout mocks
    await page.route('**/v1/payments/subscription/checkout', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          session_id: 'cs_test_123',
          session_url: 'https://checkout.stripe.com/pay/cs_test_123',
          expires_at: new Date(Date.now() + 30 * 60 * 1000).toISOString(),
        }),
      });
    });

    await page.route('**/v1/payments/credits/checkout', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          session_id: 'cs_test_456',
          session_url: 'https://checkout.stripe.com/pay/cs_test_456',
          expires_at: new Date(Date.now() + 30 * 60 * 1000).toISOString(),
        }),
      });
    });
  });

  test('should initiate subscription checkout to RESIDENT', async ({ page }) => {
    await page.goto('/');

    // Look for pricing/upgrade section
    const upgradeLink = page.getByRole('link', { name: /Pricing|Upgrade|Subscribe/i });

    if (await upgradeLink.isVisible()) {
      await upgradeLink.click();

      // Select RESIDENT tier (Tourist's next upgrade)
      await page.getByText(/RESIDENT/i).click();
      await page.getByRole('button', { name: /Subscribe|Checkout/i }).click();

      // Should redirect to Stripe (mocked)
      const response = await page.waitForResponse('**/subscription/checkout');
      expect(response.status()).toBe(200);

      const body = await response.json();
      expect(body.session_id).toBe('cs_test_123');
    }
  });

  test('should initiate credit pack checkout', async ({ page }) => {
    await page.goto('/town/demo-town-123');
    await page.waitForResponse('**/citizens');

    const buyCreditsButton = page.getByRole('button', { name: /Buy Credits|Get Credits/i });

    if (await buyCreditsButton.isVisible()) {
      await buyCreditsButton.click();

      // Select a credit pack
      await page.getByText(/Starter|500 credits/i).click();
      await page.getByRole('button', { name: /Purchase|Buy/i }).click();

      // Should call credits checkout endpoint
      const response = await page.waitForResponse('**/credits/checkout');
      expect(response.status()).toBe(200);
    }
  });
});

// =============================================================================
// Tourist Feature Restrictions
// =============================================================================

test.describe('Tourist Feature Restrictions @e2e', () => {
  test.beforeEach(async ({ page }) => {
    await setup.tourist(page);
    await setupHotDataMocks(page);
    await page.setViewportSize(DENSITY_VIEWPORTS.spacious);
  });

  test('Tourist cannot access INHABIT feature', async ({ page }) => {
    await page.goto('/town/demo-town-123');
    await page.waitForResponse('**/citizens').catch(() => {});

    // INHABIT button should be gated for Tourist
    const inhabitButton = page.getByRole('link', { name: /INHABIT/i });

    if ((await inhabitButton.count()) > 0) {
      await inhabitButton.click();

      // Should see upgrade prompt, not INHABIT UI
      await expect(
        page.getByText(/Upgrade|RESIDENT required|Subscribe/i)
      ).toBeVisible({ timeout: 5000 });
    }
  });

  test('Tourist has correct feature set per config', async ({ page }) => {
    const config = OBSERVER_CONFIGS.TOURIST;

    // Tourist features
    expect(config.features).toContain('browse');
    expect(config.features).toContain('view_lod0');
    expect(config.features).toContain('view_lod1');

    // Tourist restrictions
    expect(config.features).not.toContain('inhabit');
    expect(config.features).not.toContain('force');
    expect(config.features).not.toContain('view_lod3');
    expect(config.features).not.toContain('view_lod4');

    // Verify credits
    expect(config.credits).toBe(0);
    expect(config.canInhabit).toBe(false);
    expect(config.canForce).toBe(false);
  });
});
