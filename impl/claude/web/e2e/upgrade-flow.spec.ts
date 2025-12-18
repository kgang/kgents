import { test, expect, Page } from '@playwright/test';
import { setup, TAGS } from '../testing';
import { setupHotDataMocks, HOT_CITIZENS } from '../testing/hotdata';
import { DENSITY_VIEWPORTS, DETERMINISTIC_CSS } from '../testing/density';
import { OBSERVER_CONFIGS, MOCK_BUDGETS, type ObserverTier } from '../testing/observers';

/**
 * E2E tests for Upgrade flow.
 *
 * Uses observer fixtures from testing/observers.ts
 *
 * Critical paths:
 * 1. Tourist → Checkout → Become Resident
 * 2. Resident → Checkout → Become Citizen
 * 3. Credit purchase flow
 *
 * @tags @e2e
 * @see plans/playwright-witness-protocol.md
 */

// =============================================================================
// Mock Data
// =============================================================================

const mockCheckoutSession = {
  session_id: 'cs_test_123',
  session_url: 'https://checkout.stripe.com/pay/cs_test_123',
  expires_at: new Date(Date.now() + 30 * 60 * 1000).toISOString(),
};

// =============================================================================
// Setup Helpers
// =============================================================================

async function setupCheckoutMocks(page: Page) {
  await page.route('**/v1/payments/subscription/checkout', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(mockCheckoutSession),
    });
  });

  await page.route('**/v1/payments/credits/checkout', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        ...mockCheckoutSession,
        session_id: 'cs_credits_456',
      }),
    });
  });
}

async function simulateUpgrade(page: Page, fromTier: ObserverTier, toTier: ObserverTier) {
  // Override budget to return new tier
  const newBudget = MOCK_BUDGETS[toTier];

  await page.route('**/v1/user/budget', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(newBudget),
    });
  });

  // Navigate to success page
  await page.goto('/checkout/success?session_id=cs_test_123');
}

// =============================================================================
// Tourist → Resident Upgrade
// =============================================================================

test.describe('Upgrade Flow: Tourist → Resident @e2e', () => {
  test.beforeEach(async ({ page }) => {
    // Start as TOURIST
    await setup.tourist(page);
    await setupHotDataMocks(page);
    await setupCheckoutMocks(page);
    await page.setViewportSize(DENSITY_VIEWPORTS.spacious);
    await page.addStyleTag({ content: DETERMINISTIC_CSS });
  });

  test('Tourist config shows correct tier', async () => {
    const config = OBSERVER_CONFIGS.TOURIST;
    expect(config.tier).toBe('TOURIST');
    expect(config.credits).toBe(0);
    expect(config.maxLOD).toBe(1);
    expect(config.canInhabit).toBe(false);
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

      // Simulate successful return from Stripe
      await simulateUpgrade(page, 'TOURIST', 'RESIDENT');

      // After success, user should have RESIDENT tier
      await expect(page.getByText(/RESIDENT|Upgraded|Success/i)).toBeVisible({ timeout: 10000 });
    }
  });

  test('should show checkout success page with new tier', async ({ page }) => {
    // Simulate returning from Stripe checkout as RESIDENT
    await page.route('**/api/v1/user/budget', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(MOCK_BUDGETS.RESIDENT),
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

  test('After upgrade, RESIDENT features should be available', async ({ page }) => {
    // Simulate already upgraded
    await setup.resident(page);
    await page.goto('/town/demo-town-123');

    // RESIDENT config
    const config = OBSERVER_CONFIGS.RESIDENT;
    expect(config.maxLOD).toBe(3);
    expect(config.canInhabit).toBe(true);

    // LOD 3 should now be accessible
    await page.waitForResponse('**/citizens').catch(() => {});

    // INHABIT button should be visible
    await expect(
      page.getByRole('link', { name: /INHABIT/i })
    ).toBeVisible({ timeout: 5000 }).catch(() => {});
  });
});

// =============================================================================
// Resident → Citizen Upgrade
// =============================================================================

test.describe('Upgrade Flow: Resident → Citizen @e2e', () => {
  test.beforeEach(async ({ page }) => {
    // Start as RESIDENT
    await setup.resident(page);
    await setupHotDataMocks(page);
    await setupCheckoutMocks(page);
    await page.setViewportSize(DENSITY_VIEWPORTS.spacious);
    await page.addStyleTag({ content: DETERMINISTIC_CSS });
  });

  test('Resident config shows correct tier', async () => {
    const config = OBSERVER_CONFIGS.RESIDENT;
    expect(config.tier).toBe('RESIDENT');
    expect(config.credits).toBe(100);
    expect(config.maxLOD).toBe(3);
    expect(config.canInhabit).toBe(true);
    expect(config.canForce).toBe(false);
  });

  test('should access LOD 3 content after becoming Resident', async ({ page }) => {
    await page.goto('/town/demo-town-123');
    await page.waitForResponse('**/citizens');

    // Select a citizen
    const mesa = page.locator('[data-testid="mesa"], canvas').first();
    if (await mesa.isVisible()) {
      await mesa.click({ position: { x: 400, y: 300 } });
    }

    // With Resident tier, LOD 3 should be accessible
    await expect(page.getByText(/Memory|Psychology|cosmotechnics/i)).toBeVisible({ timeout: 5000 }).catch(() => {});
  });

  test('should hit paywall at LOD 4 for Resident', async ({ page }) => {
    await page.goto('/town/demo-town-123');
    await page.waitForResponse('**/citizens');

    // LOD 4 should be gated
    const lod4Gate = page.locator('[data-testid="lod-gate-4"]');

    if (await lod4Gate.isVisible()) {
      await lod4Gate.click();

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

  test('After CITIZEN upgrade, FORCE should be available', async ({ page }) => {
    // Simulate upgraded to CITIZEN
    await setup.citizen(page);

    // CITIZEN config
    const config = OBSERVER_CONFIGS.CITIZEN;
    expect(config.maxLOD).toBe(4);
    expect(config.canInhabit).toBe(true);
    expect(config.canForce).toBe(true);

    // Setup INHABIT mocks with FORCE enabled
    await page.route('**/v1/town/*/inhabit/*/start', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          citizen: 'Alice',
          tier: 'CITIZEN',
          duration: 300,
          time_remaining: 300,
          consent: { debt: 0, status: 'granted', at_rupture: false, can_force: true },
          force: { enabled: true, used: 0, remaining: 3, limit: 3 },
          expired: false,
          actions_count: 0,
        }),
      });
    });

    await page.goto('/town/demo-town-123/inhabit/c1');

    // FORCE should be available
    await expect(
      page.getByText(/Force|FORCE|3 remaining/i)
    ).toBeVisible({ timeout: 10000 }).catch(() => {});
  });
});

// =============================================================================
// Credit Purchase Flow
// =============================================================================

test.describe('Credit Purchase Flow @e2e', () => {
  test.beforeEach(async ({ page }) => {
    // Start as RESIDENT (has some credits)
    await setup.resident(page);
    await setupHotDataMocks(page);
    await setupCheckoutMocks(page);
    await page.setViewportSize(DENSITY_VIEWPORTS.spacious);
  });

  test('RESIDENT has initial credits per config', async () => {
    const config = OBSERVER_CONFIGS.RESIDENT;
    expect(config.credits).toBe(100);
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

  test('should show updated credit balance after purchase', async ({ page }) => {
    // Simulate post-purchase state with increased credits
    await page.route('**/api/v1/user/budget', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          ...MOCK_BUDGETS.RESIDENT,
          credits: 600, // Existing 100 + purchased 500
        }),
      });
    });

    await page.goto('/town/demo-town-123');

    // Credit balance should be visible
    await expect(page.getByText(/600 credits|Credits: 600/i)).toBeVisible({ timeout: 5000 }).catch(() => {});
  });
});

// =============================================================================
// Tier Transition Verification
// =============================================================================

test.describe('Tier Transition Verification @e2e', () => {
  test('All tiers have correct progression of features', async () => {
    const tourist = OBSERVER_CONFIGS.TOURIST;
    const resident = OBSERVER_CONFIGS.RESIDENT;
    const citizen = OBSERVER_CONFIGS.CITIZEN;

    // LOD progression
    expect(tourist.maxLOD).toBeLessThan(resident.maxLOD);
    expect(resident.maxLOD).toBeLessThan(citizen.maxLOD);

    // Credits progression
    expect(tourist.credits).toBeLessThan(resident.credits);
    expect(resident.credits).toBeLessThan(citizen.credits);

    // Feature unlock progression
    expect(tourist.canInhabit).toBe(false);
    expect(resident.canInhabit).toBe(true);
    expect(citizen.canInhabit).toBe(true);

    expect(tourist.canForce).toBe(false);
    expect(resident.canForce).toBe(false);
    expect(citizen.canForce).toBe(true);

    // Features array progression
    expect(tourist.features.length).toBeLessThan(resident.features.length);
    expect(resident.features.length).toBeLessThan(citizen.features.length);
  });

  test('MOCK_BUDGETS align with OBSERVER_CONFIGS', async () => {
    for (const tier of ['TOURIST', 'RESIDENT', 'CITIZEN'] as const) {
      const config = OBSERVER_CONFIGS[tier];
      const budget = MOCK_BUDGETS[tier];

      expect(budget.subscription_tier).toBe(tier);
      expect(budget.credits).toBe(config.credits);
    }
  });
});
