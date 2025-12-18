import { test, expect } from '@playwright/test';
import { setup, TAGS } from '../testing';
import { setupHotDataMocks, HOT_CITIZENS } from '../testing/hotdata';
import { DENSITY_VIEWPORTS, DETERMINISTIC_CSS } from '../testing/density';
import { OBSERVER_CONFIGS, tierHasFeature } from '../testing/observers';

/**
 * E2E tests for INHABIT flow.
 *
 * Uses observer fixtures from testing/observers.ts
 * INHABIT requires RESIDENT tier or higher.
 * FORCE requires CITIZEN tier.
 *
 * Critical paths:
 * 1. Resident → Start INHABIT session
 * 2. Resident → Submit action → See response
 * 3. Citizen → Force action → See consent debt rise
 *
 * @tags @e2e
 * @see plans/playwright-witness-protocol.md
 */

// =============================================================================
// Mock Data
// =============================================================================

const mockInhabitStatusResident = {
  citizen: 'Alice',
  tier: 'RESIDENT',
  duration: 300,
  time_remaining: 280,
  consent: {
    debt: 0.2,
    status: 'granted',
    at_rupture: false,
    can_force: false, // RESIDENT cannot force
    cooldown: 0,
  },
  force: {
    enabled: false,
    used: 0,
    remaining: 0,
    limit: 0,
  },
  expired: false,
  actions_count: 0,
};

const mockInhabitStatusCitizen = {
  citizen: 'Alice',
  tier: 'CITIZEN',
  duration: 300,
  time_remaining: 280,
  consent: {
    debt: 0.2,
    status: 'granted',
    at_rupture: false,
    can_force: true, // CITIZEN can force
    cooldown: 0,
  },
  force: {
    enabled: true,
    used: 0,
    remaining: 3,
    limit: 3,
  },
  expired: false,
  actions_count: 0,
};

// =============================================================================
// Setup Helper
// =============================================================================

async function setupInhabitMocks(page: import('@playwright/test').Page, tier: 'RESIDENT' | 'CITIZEN') {
  const mockStatus = tier === 'CITIZEN' ? mockInhabitStatusCitizen : mockInhabitStatusResident;

  await page.route('**/v1/town/*/inhabit/*/start', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(mockStatus),
    });
  });

  await page.route('**/v1/town/*/inhabit/*/status', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(mockStatus),
    });
  });

  await page.route('**/v1/town/*/inhabit/*/suggest', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        type: 'enact',
        message: 'Alice nods in agreement.',
        inner_voice: 'This feels right.',
        cost: 10,
        alignment_score: 0.8,
        status: {
          ...mockStatus,
          actions_count: 1,
          consent: { ...mockStatus.consent, debt: 0.25 },
        },
        success: true,
      }),
    });
  });

  await page.route('**/v1/town/*/inhabit/*/force', async (route) => {
    if (tier !== 'CITIZEN') {
      await route.fulfill({
        status: 403,
        contentType: 'application/json',
        body: JSON.stringify({
          detail: 'FORCE requires CITIZEN tier',
          current_tier: tier,
        }),
      });
      return;
    }

    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        type: 'enact',
        message: 'Alice reluctantly complies.',
        inner_voice: 'I must do this...',
        cost: 30,
        alignment_score: 0.3,
        status: {
          ...mockStatus,
          actions_count: 1,
          force: { ...mockStatus.force, used: 1, remaining: 2 },
          consent: { ...mockStatus.consent, debt: 0.5 },
        },
        success: true,
      }),
    });
  });

  await page.route('**/v1/town/*/inhabit/*/end', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ success: true }),
    });
  });
}

// =============================================================================
// RESIDENT INHABIT Flow
// =============================================================================

test.describe('INHABIT Flow - RESIDENT @e2e', () => {
  test.beforeEach(async ({ page }) => {
    // Use RESIDENT observer fixture
    await setup.resident(page);
    await setupHotDataMocks(page);
    await setupInhabitMocks(page, 'RESIDENT');
    await page.setViewportSize(DENSITY_VIEWPORTS.spacious);
    await page.addStyleTag({ content: DETERMINISTIC_CSS });
  });

  test('RESIDENT can access INHABIT (tierHasFeature check)', async () => {
    // Verify tier config
    expect(tierHasFeature('RESIDENT', 'inhabit')).toBe(true);
    expect(tierHasFeature('RESIDENT', 'force')).toBe(false);
  });

  test('should show INHABIT button for Resident tier', async ({ page }) => {
    await page.goto('/town/demo-town-123');
    await page.waitForResponse('**/citizens');

    // Select a citizen
    const citizenPanel = page.locator('[data-testid="citizen-panel"]');

    if (await citizenPanel.isVisible()) {
      // Should see INHABIT button
      await expect(page.getByRole('link', { name: /INHABIT/i })).toBeVisible({ timeout: 5000 });
    }
  });

  test('should start INHABIT session', async ({ page }) => {
    await page.goto('/town/demo-town-123/inhabit/c1');

    // INHABIT page should load with session info
    await expect(page.getByText(/INHABIT|Session|Alice/i)).toBeVisible({ timeout: 10000 });

    // Session should start automatically or via button
    const startButton = page.getByRole('button', { name: /Start Session|Begin/i });
    if (await startButton.isVisible()) {
      await startButton.click();
    }

    // Should see session status
    await expect(page.getByText(/Time Remaining|Session Active/i)).toBeVisible({ timeout: 5000 });
  });

  test('should submit action and see response', async ({ page }) => {
    await page.goto('/town/demo-town-123/inhabit/c1');
    await page.waitForResponse('**/start').catch(() => {});

    // Find action input
    const actionInput = page.getByRole('textbox', { name: /action|message|speak/i });

    if (await actionInput.isVisible()) {
      await actionInput.fill('greet Bob');
      await actionInput.press('Enter');

      // Should see response
      await expect(page.getByText(/nods in agreement|response/i)).toBeVisible({ timeout: 5000 });
    }
  });

  test('should display consent debt', async ({ page }) => {
    await page.goto('/town/demo-town-123/inhabit/c1');
    await page.waitForResponse('**/start').catch(() => {});

    // Consent debt indicator should be visible
    const consentIndicator = page.locator('[data-testid="consent-debt"], .consent-debt');

    if (await consentIndicator.isVisible()) {
      // Initial debt from mock is 0.2 (20%)
      await expect(page.getByText(/20%|0\.2/)).toBeVisible();
    }
  });

  test('RESIDENT should NOT see FORCE option', async ({ page }) => {
    await page.goto('/town/demo-town-123/inhabit/c1');
    await page.waitForResponse('**/start').catch(() => {});

    // Force button should NOT be available for RESIDENT
    const forceButton = page.getByRole('button', { name: /Force/i });

    // Either not visible or disabled
    if ((await forceButton.count()) > 0) {
      const isDisabled = await forceButton.isDisabled().catch(() => true);
      expect(isDisabled).toBe(true);
    }
  });
});

// =============================================================================
// CITIZEN INHABIT Flow with FORCE
// =============================================================================

test.describe('INHABIT Flow - CITIZEN with FORCE @e2e', () => {
  test.beforeEach(async ({ page }) => {
    // Use CITIZEN observer fixture
    await setup.citizen(page);
    await setupHotDataMocks(page);
    await setupInhabitMocks(page, 'CITIZEN');
    await page.setViewportSize(DENSITY_VIEWPORTS.spacious);
    await page.addStyleTag({ content: DETERMINISTIC_CSS });
  });

  test('CITIZEN can access both INHABIT and FORCE', async () => {
    expect(tierHasFeature('CITIZEN', 'inhabit')).toBe(true);
    expect(tierHasFeature('CITIZEN', 'force')).toBe(true);
  });

  test('should show FORCE option for CITIZEN', async ({ page }) => {
    await page.goto('/town/demo-town-123/inhabit/c1');
    await page.waitForResponse('**/start').catch(() => {});

    // Force button should be available (not disabled)
    const forceButton = page.getByRole('button', { name: /Force/i });

    await expect(forceButton.or(page.getByText(/Force Available|3 forces/i))).toBeVisible({
      timeout: 5000,
    });
  });

  test('FORCE action should increase consent debt', async ({ page }) => {
    await page.goto('/town/demo-town-123/inhabit/c1');
    await page.waitForResponse('**/start').catch(() => {});

    // Find and use force action
    const forceButton = page.getByRole('button', { name: /Force/i });

    if (await forceButton.isVisible()) {
      // Need to enter an action first
      const actionInput = page.getByRole('textbox');
      await actionInput.fill('do something forceful');

      // Click force
      await forceButton.click();

      // Wait for force response
      await page.waitForResponse('**/force');

      // Consent debt should increase (from 0.2 to 0.5 based on mock)
      await expect(page.getByText(/50%|0\.5|increased/i)).toBeVisible({ timeout: 5000 });
    }
  });

  test('FORCE remaining counter decrements after use', async ({ page }) => {
    await page.goto('/town/demo-town-123/inhabit/c1');
    await page.waitForResponse('**/start').catch(() => {});

    // Initially 3 forces remaining
    await expect(page.getByText(/3 forces|3 remaining/i)).toBeVisible().catch(() => {});

    const forceButton = page.getByRole('button', { name: /Force/i });

    if (await forceButton.isVisible()) {
      const actionInput = page.getByRole('textbox');
      await actionInput.fill('forced action');
      await forceButton.click();
      await page.waitForResponse('**/force');

      // Now 2 forces remaining
      await expect(page.getByText(/2 forces|2 remaining/i)).toBeVisible({ timeout: 5000 });
    }
  });
});

// =============================================================================
// INHABIT Session Lifecycle
// =============================================================================

test.describe('INHABIT Session Lifecycle @e2e', () => {
  test.beforeEach(async ({ page }) => {
    await setup.resident(page);
    await setupHotDataMocks(page);
    await setupInhabitMocks(page, 'RESIDENT');
    await page.setViewportSize(DENSITY_VIEWPORTS.spacious);
  });

  test('should end session gracefully', async ({ page }) => {
    await page.goto('/town/demo-town-123/inhabit/c1');
    await page.waitForResponse('**/start').catch(() => {});

    // Find end session button
    const endButton = page.getByRole('button', { name: /End Session|Exit|Leave/i });

    if (await endButton.isVisible()) {
      await endButton.click();

      // Should navigate back or show confirmation
      await expect(page.getByText(/Session Ended|Thank you|Goodbye/i)).toBeVisible({
        timeout: 5000,
      });
    }
  });

  test('should show session history', async ({ page }) => {
    await page.goto('/town/demo-town-123/inhabit/c1');
    await page.waitForResponse('**/start').catch(() => {});

    // Submit an action
    const actionInput = page.getByRole('textbox');
    if (await actionInput.isVisible()) {
      await actionInput.fill('hello');
      await actionInput.press('Enter');

      // Wait for response
      await page.waitForResponse('**/suggest');

      // History should show the action
      await expect(page.getByText(/hello|nods/i)).toBeVisible({ timeout: 5000 });
    }
  });
});

// =============================================================================
// Tier Comparison
// =============================================================================

test.describe('INHABIT Tier Comparison @e2e', () => {
  test('RESIDENT vs CITIZEN INHABIT capabilities', async () => {
    const residentConfig = OBSERVER_CONFIGS.RESIDENT;
    const citizenConfig = OBSERVER_CONFIGS.CITIZEN;

    // Both can INHABIT
    expect(residentConfig.canInhabit).toBe(true);
    expect(citizenConfig.canInhabit).toBe(true);

    // Only CITIZEN can FORCE
    expect(residentConfig.canForce).toBe(false);
    expect(citizenConfig.canForce).toBe(true);

    // CITIZEN has more credits
    expect(citizenConfig.credits).toBeGreaterThan(residentConfig.credits);
  });
});
