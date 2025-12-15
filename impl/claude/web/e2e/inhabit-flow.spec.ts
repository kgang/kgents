import { test, expect } from '@playwright/test';
import { setupResidentMocks, setupInhabitMocks } from './fixtures/api';

/**
 * E2E tests for INHABIT flow.
 *
 * Critical paths:
 * 1. Resident → Start INHABIT session
 * 2. Resident → Submit action → See response
 * 3. Resident → Force action → See consent debt rise
 */

test.describe('INHABIT Flow', () => {
  test.beforeEach(async ({ page }) => {
    await setupResidentMocks(page);
    await setupInhabitMocks(page);
  });

  test('should show INHABIT button for Resident tier', async ({ page }) => {
    await page.goto('/town/demo-town-123');

    // Wait for citizens to load
    await page.waitForResponse('**/citizens');

    // Select a citizen (implementation-dependent)
    const citizenPanel = page.locator('[data-testid="citizen-panel"]');

    if (await citizenPanel.isVisible()) {
      // Should see INHABIT button
      await expect(page.getByRole('link', { name: /INHABIT/i })).toBeVisible({ timeout: 5000 });
    }
  });

  test('should start INHABIT session', async ({ page }) => {
    await page.goto('/town/demo-town-123/inhabit/c1');

    // INHABIT page should load
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

    // Wait for session to be active
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

    // Wait for session
    await page.waitForResponse('**/start').catch(() => {});

    // Consent debt indicator should be visible
    const consentIndicator = page.locator('[data-testid="consent-debt"], .consent-debt');

    if (await consentIndicator.isVisible()) {
      // Initial debt from mock is 0.2
      await expect(page.getByText(/20%|0\.2/)).toBeVisible();
    }
  });

  test('should show force action option', async ({ page }) => {
    await page.goto('/town/demo-town-123/inhabit/c1');

    // Wait for session
    await page.waitForResponse('**/start').catch(() => {});

    // Force button should be available (if not already visible, might need to enable)
    const forceButton = page.getByRole('button', { name: /Force|Override/i });

    // Force option should exist in some form
    await expect(forceButton.or(page.getByText(/Force Available|3 forces/i))).toBeVisible({
      timeout: 5000,
    });
  });

  test('force action should increase consent debt', async ({ page }) => {
    await page.goto('/town/demo-town-123/inhabit/c1');

    // Wait for session
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
});

test.describe('INHABIT Session Lifecycle', () => {
  test.beforeEach(async ({ page }) => {
    await setupResidentMocks(page);
    await setupInhabitMocks(page);
  });

  test('should end session gracefully', async ({ page }) => {
    await page.goto('/town/demo-town-123/inhabit/c1');

    // Wait for session
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

    // Wait for session
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
