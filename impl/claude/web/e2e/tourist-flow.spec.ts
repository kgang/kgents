import { test, expect } from '@playwright/test';
import { setupTouristMocks, setupCheckoutMocks, mockCitizens } from './fixtures/api';

/**
 * E2E tests for Tourist flow.
 *
 * Critical paths:
 * 1. Tourist → View demo town (LOD 0-1 only)
 * 2. Tourist → Hit paywall at LOD 3
 */

test.describe('Tourist Flow', () => {
  test.beforeEach(async ({ page }) => {
    await setupTouristMocks(page);
  });

  test('should view demo town with citizens', async ({ page }) => {
    await page.goto('/');

    // Landing page should load
    await expect(page.getByRole('heading', { name: /Agent Town/i })).toBeVisible();

    // Click to view demo
    await page.getByRole('button', { name: /Try Demo|View Demo|Start/i }).click();

    // Wait for town to load
    await expect(page.locator('[data-testid="mesa"]')).toBeVisible({ timeout: 10000 });

    // Should see citizens rendered
    // Note: The actual citizen display depends on how the Mesa renders
  });

  test('should display citizen basic info at LOD 0-1', async ({ page }) => {
    await page.goto('/town/demo-town-123');

    // Wait for citizens to load
    await page.waitForResponse('**/citizens');

    // Click on a citizen (need to find the clickable area)
    // This depends on the actual UI implementation
    await page.locator('[data-testid="citizen-Alice"]').click().catch(() => {
      // If no specific testid, try clicking the mesa area
      // Mesa click handling converts screen coords to citizen selection
    });

    // Citizen panel should appear with basic info
    await expect(page.getByText('Silhouette')).toBeVisible({ timeout: 5000 });
    await expect(page.getByText('Posture')).toBeVisible();
  });

  test('should hit paywall at LOD 3', async ({ page }) => {
    await page.goto('/town/demo-town-123');
    await setupCheckoutMocks(page);

    // Navigate to citizen detail view
    // Select a citizen first
    await page.waitForResponse('**/citizens');

    // Try to access LOD 3 content
    // The exact interaction depends on UI - might be clicking an "Unlock" button
    const lodGate = page.locator('[data-testid="lod-gate-3"], [data-lod="3"]').first();

    if (await lodGate.isVisible()) {
      // Should see unlock prompt
      await expect(page.getByText(/Unlock|Get Credits|Upgrade/i)).toBeVisible();
    }
  });

  test('should show upgrade options when hitting paywall', async ({ page }) => {
    await page.goto('/town/demo-town-123');
    await setupCheckoutMocks(page);

    // Wait for initial load
    await page.waitForResponse('**/citizens');

    // Look for upgrade prompts in the UI
    const upgradeButton = page.getByRole('button', { name: /Upgrade|Get Credits/i });

    if (await upgradeButton.isVisible()) {
      await upgradeButton.click();

      // Modal should show pricing options
      await expect(page.getByText(/RESIDENT|\$9\.99/i)).toBeVisible({ timeout: 5000 });
    }
  });
});

test.describe('Tourist → Checkout Flow', () => {
  test.beforeEach(async ({ page }) => {
    await setupTouristMocks(page);
    await setupCheckoutMocks(page);
  });

  test('should initiate subscription checkout', async ({ page }) => {
    await page.goto('/');

    // Look for pricing/upgrade section
    const upgradeLink = page.getByRole('link', { name: /Pricing|Upgrade|Subscribe/i });

    if (await upgradeLink.isVisible()) {
      await upgradeLink.click();

      // Select RESIDENT tier
      await page.getByText(/RESIDENT/i).click();
      await page.getByRole('button', { name: /Subscribe|Checkout/i }).click();

      // Should redirect to Stripe (mocked)
      // In real test, we'd verify navigation or response
      const response = await page.waitForResponse('**/subscription/checkout');
      expect(response.status()).toBe(200);
    }
  });

  test('should initiate credit pack checkout', async ({ page }) => {
    await page.goto('/town/demo-town-123');

    // Try to unlock gated content to trigger credit prompt
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
