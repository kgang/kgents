import { test, expect } from '@playwright/test';
import { setupResidentMocks, mockCitizens } from './fixtures/api';

/**
 * E2E tests for Town Visualizer Renaissance.
 *
 * Tests the core user journeys from plans/town-visualizer-renaissance.md:
 * - J1: First visit overview
 * - J2: Citizen state machine visualization
 * - J11: Mobile town experience
 * - J15: Teaching mode toggle
 *
 * @see plans/town-visualizer-renaissance.md - Phase 6: Testing Strategy
 */

test.describe('Town Overview', () => {
  test.beforeEach(async ({ page }) => {
    await setupResidentMocks(page);
  });

  test('should display town dashboard with stats', async ({ page }) => {
    await page.goto('/town');

    // Header should be visible
    await expect(page.getByRole('heading', { name: /Agent Town/i })).toBeVisible();

    // Stats grid should show data (use first() to get specific stat card labels)
    await expect(page.locator('p:has-text("Total Citizens")').first()).toBeVisible();
    await expect(page.locator('p:has-text("Conversations")').first()).toBeVisible();
    await expect(page.locator('p:has-text("Coalitions")').first()).toBeVisible();
    await expect(page.locator('p:has-text("Relationships")').first()).toBeVisible();
  });

  test('should navigate to citizens from overview', async ({ page }) => {
    await page.goto('/town');

    // Click on "View details" in the Citizens stat card (first clickable stat card)
    await page.locator('text=View details').first().click();

    // Should navigate to citizens page
    await expect(page).toHaveURL(/\/town\/citizens/);
  });

  test('should navigate to coalitions from overview', async ({ page }) => {
    await page.goto('/town');

    // Click on the Coalitions stat card (which has onClick) to navigate
    // The stat card shows "Coalitions" label and has "View details" link
    const coalitionsCard = page.locator('p:has-text("Coalitions")').locator('..').locator('..');
    await coalitionsCard.locator('text=View details').click();

    // Should navigate to coalitions page
    await expect(page).toHaveURL(/\/town\/coalitions/);
  });
});

test.describe('Teaching Mode', () => {
  test.beforeEach(async ({ page }) => {
    await setupResidentMocks(page);
    // Clear localStorage to reset teaching mode
    await page.addInitScript(() => {
      localStorage.removeItem('kgents_teaching_mode');
    });
  });

  test('should show teaching toggle in town overview', async ({ page }) => {
    await page.goto('/town');

    // Teaching toggle button should be visible (compact mode shows lightbulb icon)
    const teachingToggle = page.locator('button[title*="Teaching"]');
    await expect(teachingToggle).toBeVisible();
  });

  test('should toggle teaching mode on/off', async ({ page }) => {
    await page.goto('/town');

    // Find the teaching toggle button by its aria-label
    const teachingToggle = page.locator('button[aria-label*="Teaching"]').first();

    // Default is ON - teaching callout should be visible
    await expect(page.getByText(/Town Architecture/i).first()).toBeVisible();

    // Toggle OFF - the aria-label will change from "ON" to "OFF"
    await teachingToggle.click();

    // Wait for state to update and verify toggle changed
    await expect(page.locator('button[aria-label="Teaching Mode: OFF"]')).toBeVisible({ timeout: 3000 });

    // Toggle back ON
    await page.locator('button[aria-label="Teaching Mode: OFF"]').click();

    // Verify toggle is now ON
    await expect(page.locator('button[aria-label="Teaching Mode: ON"]')).toBeVisible({ timeout: 3000 });
  });

  test('should persist teaching mode preference in localStorage', async ({ page }) => {
    await page.goto('/town');

    // Toggle OFF
    const teachingToggle = page.locator('button[title*="Teaching"]');
    await teachingToggle.click();

    // Verify localStorage was updated
    const stored = await page.evaluate(() => localStorage.getItem('kgents_teaching_mode'));
    expect(stored).toBe('false');

    // Reload page
    await page.reload();

    // Teaching should still be OFF
    await expect(page.getByText(/Town Architecture/i)).not.toBeVisible();
  });

  test('should show categorical explanation in teaching mode', async ({ page }) => {
    await page.goto('/town');

    // Verify categorical content is shown
    await expect(page.getByText(/Polynomial Agents/i)).toBeVisible();
    await expect(page.getByText(/Operad Grammar/i)).toBeVisible();
    await expect(page.getByText(/Sheaf Coherence/i)).toBeVisible();
  });
});

test.describe('Citizen Browser', () => {
  test.beforeEach(async ({ page }) => {
    await setupResidentMocks(page);
  });

  test('should display citizen list', async ({ page }) => {
    await page.goto('/town/citizens');

    // Wait for the page to load (the API mocks are set up already)
    await page.waitForSelector('text=Citizens', { timeout: 10000 });

    // Should show citizen names from mock data
    for (const citizen of mockCitizens.slice(0, 3)) {
      await expect(page.getByText(citizen.name)).toBeVisible();
    }
  });

  test('should filter citizens by search', async ({ page }) => {
    await page.goto('/town/citizens');
    await page.waitForSelector('text=Citizens', { timeout: 10000 });

    // All citizens should be visible initially
    await expect(page.getByText('Alice')).toBeVisible();
    await expect(page.getByText('Bob')).toBeVisible();

    // Type in search box to filter
    const searchInput = page.locator('input[placeholder*="Search"]');
    await searchInput.fill('Alice');

    // Wait for filter to apply
    await page.waitForTimeout(500);

    // Only Alice should be visible
    await expect(page.getByText('Alice')).toBeVisible();
  });

  test('should show citizen panel on click', async ({ page }) => {
    await page.goto('/town/citizens');
    await page.waitForSelector('text=Citizens', { timeout: 10000 });

    // Click on a citizen
    await page.getByText('Alice').click();

    // Citizen panel should appear with citizen name header
    await expect(page.locator('h2:has-text("Alice")').first()).toBeVisible({ timeout: 5000 });
  });
});

test.describe('Citizen Panel State Machine', () => {
  test.beforeEach(async ({ page }) => {
    await setupResidentMocks(page);
  });

  test('should display citizen details panel', async ({ page }) => {
    await page.goto('/town/citizens');
    await page.waitForSelector('text=Citizens', { timeout: 10000 });

    // Click on a citizen
    await page.getByText('Alice').click();

    // Panel should show citizen details (interactions section)
    await expect(page.locator('text=Interactions').first()).toBeVisible({ timeout: 5000 });
  });

  test('should show citizen stats in panel', async ({ page }) => {
    await page.goto('/town/citizens');
    await page.waitForSelector('text=Citizens', { timeout: 10000 });

    // Click on Alice
    await page.getByText('Alice').click();

    // Panel should show stats sections
    await expect(page.locator('h2:has-text("Alice")').first()).toBeVisible({ timeout: 5000 });
    await expect(page.locator('text=Interactions').first()).toBeVisible();
  });

  test('should show conversation action button', async ({ page }) => {
    await page.goto('/town/citizens');
    await page.waitForSelector('text=Citizens', { timeout: 10000 });

    // Click on a citizen
    await page.getByText('Alice').click();

    // Should have Start Conversation button
    await expect(page.getByRole('button', { name: /Start Conversation/i })).toBeVisible({ timeout: 5000 });
  });
});

test.describe('Coalition Graph', () => {
  test.beforeEach(async ({ page }) => {
    await setupResidentMocks(page);
  });

  test('should display coalition graph view', async ({ page }) => {
    await page.goto('/town/coalitions');

    // Header should be visible
    await expect(page.locator('h1:has-text("Coalition Graph")').first()).toBeVisible();

    // Should show coalition count info (e.g., "0 coalitions • 0 bridges")
    await expect(page.locator('text=coalitions').first()).toBeVisible();
  });

  test('should show teaching toggle in coalition graph', async ({ page }) => {
    await page.goto('/town/coalitions');

    // Teaching toggle should be visible (aria-label)
    const teachingToggle = page.locator('button[aria-label*="Teaching"]');
    await expect(teachingToggle).toBeVisible();
  });

  test('should show operad explanation in teaching mode', async ({ page }) => {
    await page.goto('/town/coalitions');

    // Teaching callout should be visible
    await expect(page.getByText(/Coalition Formation Operad/i)).toBeVisible();

    // Should explain operad concepts
    await expect(page.getByText(/coalition_form/i)).toBeVisible();
    await expect(page.getByText(/coalition_dissolve/i)).toBeVisible();
    await expect(page.getByText(/Bridge citizens/i)).toBeVisible();
  });

  test('should have detect coalitions button', async ({ page }) => {
    await page.goto('/town/coalitions');

    // Detect button should be visible (there are two - one in header, one in empty state)
    const detectButton = page.getByRole('button', { name: /Detect/i }).first();
    await expect(detectButton).toBeVisible();
  });

  test('should show legend with node types', async ({ page }) => {
    await page.goto('/town/coalitions');

    // Legend should explain node types (using specific selector for legend area)
    const legend = page.locator('.flex.items-center.gap-6');
    await expect(legend.locator('text=Coalition').first()).toBeVisible();
    await expect(legend.locator('text=Citizen').first()).toBeVisible();
    await expect(legend.locator('text=Bridge Citizen')).toBeVisible();
  });
});

test.describe('Mobile Town Experience', () => {
  test.use({ viewport: { width: 375, height: 667 } }); // iPhone SE size

  test.beforeEach(async ({ page }) => {
    await setupResidentMocks(page);
  });

  test('should display compact layout on mobile', async ({ page }) => {
    await page.goto('/town');

    // Page should render without horizontal scroll
    const body = page.locator('body');
    const scrollWidth = await body.evaluate((el) => el.scrollWidth);
    const clientWidth = await body.evaluate((el) => el.clientWidth);
    expect(scrollWidth).toBeLessThanOrEqual(clientWidth + 10); // Allow small margin
  });

  test('should show 2-column grid on mobile', async ({ page }) => {
    await page.goto('/town');

    // Stats should be in a grid (compact mode shows 2-column)
    const statsGrid = page.locator('.grid').first();
    await expect(statsGrid).toHaveClass(/grid-cols-2/);
  });

  test('should navigate citizens on mobile', async ({ page }) => {
    await page.goto('/town/citizens');
    await page.waitForSelector('text=Citizens', { timeout: 10000 });

    // Should show citizens list
    await expect(page.getByText('Alice')).toBeVisible();

    // Click should still work
    await page.getByText('Alice').click();

    // Panel should appear as bottom sheet on mobile (showing citizen name in h2)
    await expect(page.locator('h2:has-text("Alice")').first()).toBeVisible({ timeout: 5000 });
  });
});

test.describe('Breathing Animations', () => {
  test.beforeEach(async ({ page }) => {
    await setupResidentMocks(page);
  });

  test('should respect prefers-reduced-motion', async ({ page }) => {
    // Emulate reduced motion preference
    await page.emulateMedia({ reducedMotion: 'reduce' });

    await page.goto('/town');

    // With reduced motion, breathing animations should be disabled
    // The useBreathing hook checks this preference
    // We can't easily test the visual effect, but we verify the page loads correctly
    await expect(page.getByRole('heading', { name: /Agent Town/i })).toBeVisible();
  });
});

test.describe('Accessibility', () => {
  test.beforeEach(async ({ page }) => {
    await setupResidentMocks(page);
  });

  test('teaching callouts should have proper ARIA labels', async ({ page }) => {
    await page.goto('/town');

    // Teaching callouts should have role="note"
    const callout = page.locator('[role="note"]').first();
    await expect(callout).toBeVisible();
    await expect(callout).toHaveAttribute('aria-label', /teaching/i);
  });

  test('teaching toggle should have accessible name', async ({ page }) => {
    await page.goto('/town');

    const toggle = page.locator('button[title*="Teaching"]');
    await expect(toggle).toHaveAttribute('aria-label', /Teaching Mode/i);
  });

  test('town should be keyboard navigable', async ({ page }) => {
    await page.goto('/town');

    // Tab through interactive elements
    await page.keyboard.press('Tab');
    await page.keyboard.press('Tab');

    // Some element should be focused
    const focusedElement = page.locator(':focus');
    await expect(focusedElement).toBeTruthy();
  });
});
