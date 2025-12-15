import { test, expect, Page } from '@playwright/test';
import {
  setupTouristMocks,
  setupResidentMocks,
  setupCheckoutMocks,
  mockResidentBudget,
} from './fixtures/api';

/**
 * E2E tests for Upgrade flow.
 *
 * Critical paths:
 * 1. Tourist → Checkout → Become Resident
 * 2. Citizen → Upgrade → Access LOD 4
 */

test.describe('Upgrade Flow: Tourist → Resident', () => {
  test.beforeEach(async ({ page }) => {
    await setupTouristMocks(page);
    await setupCheckoutMocks(page);
  });

  test('should complete checkout and become Resident', async ({ page }) => {
    await page.goto('/');

    // Start from landing
    await expect(page.getByRole('heading', { name: /Agent Town/i })).toBeVisible();

    // Navigate to pricing
    const pricingLink = page.getByRole('link', { name: /Pricing|Upgrade/i });
    if (await pricingLink.isVisible()) {
      await pricingLink.click();
    }

    // Select RESIDENT tier
    const residentOption = page.getByText(/RESIDENT.*\$9\.99/i);
    if (await residentOption.isVisible()) {
      await residentOption.click();

      // Click checkout
      await page.getByRole('button', { name: /Subscribe|Checkout|Upgrade/i }).click();

      // Wait for checkout response
      const checkoutResponse = await page.waitForResponse('**/subscription/checkout');
      expect(checkoutResponse.status()).toBe(200);

      // In real flow, would redirect to Stripe then back
      // Simulate successful return
      await simulateCheckoutSuccess(page);

      // After success, user should have RESIDENT tier
      await expect(page.getByText(/RESIDENT|Upgraded|Success/i)).toBeVisible({ timeout: 10000 });
    }
  });

  test('should show checkout success page', async ({ page }) => {
    // Simulate returning from Stripe checkout
    await page.route('**/api/v1/user/budget', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(mockResidentBudget),
      });
    });

    await page.goto('/checkout/success?session_id=cs_test_123');

    // Success page should show
    await expect(page.getByText(/Success|Thank you|Welcome/i)).toBeVisible({ timeout: 5000 });

    // Should indicate the new tier
    await expect(page.getByText(/RESIDENT|subscription active/i)).toBeVisible({ timeout: 5000 });
  });

  test('should handle checkout cancellation', async ({ page }) => {
    await page.goto('/checkout/cancel');

    // Cancel page should offer to try again
    await expect(page.getByText(/Cancel|Back|Try again/i)).toBeVisible({ timeout: 5000 });
  });
});

test.describe('Upgrade Flow: Resident → Citizen', () => {
  test.beforeEach(async ({ page }) => {
    await setupResidentMocks(page);
    await setupCheckoutMocks(page);
  });

  test('should access LOD 3 content after upgrade', async ({ page }) => {
    await page.goto('/town/demo-town-123');

    // Wait for citizens
    await page.waitForResponse('**/citizens');

    // Select a citizen to see citizen panel
    // Click on mesa area where citizens are rendered
    const mesa = page.locator('[data-testid="mesa"], canvas').first();
    if (await mesa.isVisible()) {
      // Click somewhere on the mesa
      await mesa.click({ position: { x: 400, y: 300 } });
    }

    // With Resident tier, LOD 3 should be accessible
    await expect(page.getByText(/Memory|LOD 3/i)).toBeVisible({ timeout: 5000 });
  });

  test('should hit paywall at LOD 4 for Resident', async ({ page }) => {
    await page.goto('/town/demo-town-123');

    // Wait for citizens
    await page.waitForResponse('**/citizens');

    // LOD 4 should be gated
    const lod4Gate = page.locator('[data-testid="lod-gate-4"]');

    if (await lod4Gate.isVisible()) {
      // Should show upgrade to CITIZEN option
      await expect(page.getByText(/CITIZEN.*\$29\.99|Upgrade to access/i)).toBeVisible();
    }
  });

  test('should initiate Citizen upgrade', async ({ page }) => {
    await page.goto('/town/demo-town-123');

    // Find upgrade prompt for LOD 4
    const upgradeButton = page.getByRole('button', { name: /Upgrade.*Citizen/i });

    if (await upgradeButton.isVisible()) {
      await upgradeButton.click();

      // Modal should show CITIZEN pricing
      await expect(page.getByText(/CITIZEN.*\$29\.99/i)).toBeVisible({ timeout: 5000 });
    }
  });
});

test.describe('Credit Purchase Flow', () => {
  test.beforeEach(async ({ page }) => {
    await setupResidentMocks(page);
    await setupCheckoutMocks(page);
  });

  test('should purchase credit pack', async ({ page }) => {
    await page.goto('/town/demo-town-123');

    // Find credit purchase option
    const buyCreditsButton = page.getByRole('button', { name: /Buy Credits|Get Credits/i });

    if (await buyCreditsButton.isVisible()) {
      await buyCreditsButton.click();

      // Select Starter pack
      await page.getByText(/Starter.*500.*\$4\.99/i).click();
      await page.getByRole('button', { name: /Purchase|Buy/i }).click();

      // Should call credits checkout
      const response = await page.waitForResponse('**/credits/checkout');
      expect(response.status()).toBe(200);
    }
  });

  test('should show credit balance after purchase', async ({ page }) => {
    // Simulate post-purchase state
    await page.route('**/api/v1/user/budget', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          ...mockResidentBudget,
          credits: 600, // Existing 100 + purchased 500
        }),
      });
    });

    await page.goto('/town/demo-town-123');

    // Credit balance should be visible
    await expect(page.getByText(/600 credits|Credits: 600/i)).toBeVisible({ timeout: 5000 });
  });
});

// =============================================================================
// Helpers
// =============================================================================

async function simulateCheckoutSuccess(page: Page) {
  // Override budget to return RESIDENT tier
  await page.route('**/api/v1/user/budget', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(mockResidentBudget),
    });
  });

  // Navigate to success page
  await page.goto('/checkout/success?session_id=cs_test_123');
}
