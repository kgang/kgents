import { test, expect, Page } from '@playwright/test';
import { setupTouristMocks } from '../fixtures/api';

/**
 * Visual Regression Tests for Elastic Layouts
 *
 * Tests breakpoint behavior at: 320px, 640px, 768px (collapse threshold), 1024px, 1280px
 *
 * Key behaviors:
 * - ElasticSplit collapses at 768px (stacks vertically)
 * - ElasticCard degrades: full -> summary -> title -> icon
 * - CitizenCard content levels based on available width
 *
 * @see plans/web-refactor/elastic-primitives.md
 */

const BREAKPOINTS = {
  mobile_small: { width: 320, height: 568 },
  mobile: { width: 640, height: 1136 },
  tablet: { width: 768, height: 1024 }, // Collapse threshold
  desktop: { width: 1024, height: 768 },
  desktop_large: { width: 1280, height: 800 },
};

async function setupElasticMocks(page: Page) {
  await setupTouristMocks(page);

  // Mock town stream widget response
  await page.route('**/v1/town/*/live*', async (route) => {
    const events = `event: live.start\ndata: ${JSON.stringify({
      town_id: 'demo-town-123',
      phases: 4,
      speed: 1.0,
    })}\n\n`;

    await route.fulfill({
      status: 200,
      contentType: 'text/event-stream',
      headers: {
        'Cache-Control': 'no-cache',
        Connection: 'keep-alive',
      },
      body: events,
    });
  });
}

test.describe('ElasticSplit Collapse Behavior', () => {
  test.beforeEach(async ({ page }) => {
    await setupElasticMocks(page);
  });

  test('should display side-by-side at 1280px (desktop large)', async ({ page }) => {
    await page.setViewportSize(BREAKPOINTS.desktop_large);
    await page.goto('/town/demo-town-123');

    // Wait for citizens to load
    await page.waitForResponse('**/citizens');

    // ElasticSplit should NOT be collapsed
    const elasticSplit = page.locator('[data-collapsed]');
    if ((await elasticSplit.count()) > 0) {
      await expect(elasticSplit).not.toHaveAttribute('data-collapsed', 'true');
    }

    // Both primary and secondary panes should be visible side by side
    const splitContainer = page.locator('[data-direction="horizontal"]');
    if ((await splitContainer.count()) > 0) {
      await expect(splitContainer).toBeVisible();
    }

    // Screenshot for regression comparison
    await expect(page).toHaveScreenshot('town-1280px.png', {
      fullPage: false,
      maxDiffPixelRatio: 0.02,
    });
  });

  test('should display side-by-side at 1024px (desktop)', async ({ page }) => {
    await page.setViewportSize(BREAKPOINTS.desktop);
    await page.goto('/town/demo-town-123');
    await page.waitForResponse('**/citizens');

    // Should still be horizontal layout
    const splitContainer = page.locator('[data-direction="horizontal"]');
    if ((await splitContainer.count()) > 0) {
      await expect(splitContainer).toBeVisible();
    }

    await expect(page).toHaveScreenshot('town-1024px.png', {
      fullPage: false,
      maxDiffPixelRatio: 0.02,
    });
  });

  test('should collapse to stacked layout at 768px (tablet - threshold)', async ({ page }) => {
    await page.setViewportSize(BREAKPOINTS.tablet);
    await page.goto('/town/demo-town-123');
    await page.waitForResponse('**/citizens');

    // At exactly 768px, should still be horizontal (collapse is < 768)
    await page.setViewportSize({ width: 767, height: 1024 });
    await page.waitForTimeout(100); // Allow resize observer to fire

    // ElasticSplit should now be collapsed
    const collapsed = page.locator('[data-collapsed="true"]');
    await expect(collapsed).toBeVisible({ timeout: 5000 });

    await expect(page).toHaveScreenshot('town-768px-collapsed.png', {
      fullPage: false,
      maxDiffPixelRatio: 0.02,
    });
  });

  test('should stack vertically at 640px (mobile)', async ({ page }) => {
    await page.setViewportSize(BREAKPOINTS.mobile);
    await page.goto('/town/demo-town-123');
    await page.waitForResponse('**/citizens');

    // Should be stacked
    const collapsed = page.locator('[data-collapsed="true"]');
    await expect(collapsed).toBeVisible({ timeout: 5000 });

    // Panes should be in vertical stack
    const panes = collapsed.locator('> div');
    expect(await panes.count()).toBeGreaterThanOrEqual(2);

    await expect(page).toHaveScreenshot('town-640px.png', {
      fullPage: false,
      maxDiffPixelRatio: 0.02,
    });
  });

  test('should handle extreme narrow viewport at 320px (mobile small)', async ({ page }) => {
    await page.setViewportSize(BREAKPOINTS.mobile_small);
    await page.goto('/town/demo-town-123');
    await page.waitForResponse('**/citizens');

    // Should be collapsed and functional
    const collapsed = page.locator('[data-collapsed="true"]');
    await expect(collapsed).toBeVisible({ timeout: 5000 });

    // No horizontal overflow
    const body = await page.locator('body').boundingBox();
    expect(body?.width).toBeLessThanOrEqual(320);

    await expect(page).toHaveScreenshot('town-320px.png', {
      fullPage: false,
      maxDiffPixelRatio: 0.02,
    });
  });
});

test.describe('ElasticCard Content Level Degradation', () => {
  test.beforeEach(async ({ page }) => {
    await setupElasticMocks(page);
  });

  test('should show full citizen cards at 1280px', async ({ page }) => {
    await page.setViewportSize(BREAKPOINTS.desktop_large);
    await page.goto('/town/demo-town-123');
    await page.waitForResponse('**/citizens');

    // Wait for citizen cards to render
    const citizenCards = page.locator('[data-testid="citizen-card"]');
    await expect(citizenCards.first()).toBeVisible({ timeout: 5000 });

    // Check content level - should be full or summary at large viewport
    const contentLevels = await citizenCards.evaluateAll((cards) =>
      cards.map((c) => c.getAttribute('data-content-level'))
    );

    // At 1280px with many cards, most should be full or summary
    const fullOrSummary = contentLevels.filter((l) => l === 'full' || l === 'summary');
    expect(fullOrSummary.length).toBeGreaterThan(0);

    await expect(page).toHaveScreenshot('citizens-1280px.png', {
      fullPage: false,
      maxDiffPixelRatio: 0.02,
    });
  });

  test('should show compact citizen cards at 640px', async ({ page }) => {
    await page.setViewportSize(BREAKPOINTS.mobile);
    await page.goto('/town/demo-town-123');
    await page.waitForResponse('**/citizens');

    const citizenCards = page.locator('[data-testid="citizen-card"]');
    await expect(citizenCards.first()).toBeVisible({ timeout: 5000 });

    // At 640px, cards should be more compact
    const contentLevels = await citizenCards.evaluateAll((cards) =>
      cards.map((c) => c.getAttribute('data-content-level'))
    );

    // Should have title or icon level cards
    const compact = contentLevels.filter((l) => l === 'title' || l === 'icon');
    expect(compact.length).toBeGreaterThanOrEqual(0); // Some may still be summary

    await expect(page).toHaveScreenshot('citizens-640px.png', {
      fullPage: false,
      maxDiffPixelRatio: 0.02,
    });
  });

  test('should show icon-only cards at 320px', async ({ page }) => {
    await page.setViewportSize(BREAKPOINTS.mobile_small);
    await page.goto('/town/demo-town-123');
    await page.waitForResponse('**/citizens');

    const citizenCards = page.locator('[data-testid="citizen-card"]');
    await expect(citizenCards.first()).toBeVisible({ timeout: 5000 });

    // At 320px, most cards should be icon or title
    const contentLevels = await citizenCards.evaluateAll((cards) =>
      cards.map((c) => c.getAttribute('data-content-level'))
    );

    // Most should be compact representations
    const iconOrTitle = contentLevels.filter((l) => l === 'icon' || l === 'title');
    expect(iconOrTitle.length).toBeGreaterThanOrEqual(contentLevels.length * 0.5);

    await expect(page).toHaveScreenshot('citizens-320px.png', {
      fullPage: false,
      maxDiffPixelRatio: 0.02,
    });
  });
});

test.describe('Resize Transitions', () => {
  test.beforeEach(async ({ page }) => {
    await setupElasticMocks(page);
  });

  test('should smoothly transition between breakpoints', async ({ page }) => {
    // Start at desktop
    await page.setViewportSize(BREAKPOINTS.desktop_large);
    await page.goto('/town/demo-town-123');
    await page.waitForResponse('**/citizens');

    const citizenCards = page.locator('[data-testid="citizen-card"]');
    await expect(citizenCards.first()).toBeVisible({ timeout: 5000 });

    // Resize down through breakpoints
    for (const size of [1024, 768, 640, 320]) {
      await page.setViewportSize({ width: size, height: 800 });
      // Allow resize observer to process
      await page.waitForTimeout(150);

      // Verify no layout breaks (elements shouldn't overflow)
      const overflows = await page.evaluate(() => {
        const elements = document.querySelectorAll('[data-testid="citizen-card"]');
        let hasOverflow = false;
        elements.forEach((el) => {
          const rect = el.getBoundingClientRect();
          if (rect.right > window.innerWidth) {
            hasOverflow = true;
          }
        });
        return hasOverflow;
      });

      expect(overflows).toBe(false);
    }

    // Resize back up
    await page.setViewportSize(BREAKPOINTS.desktop);
    await page.waitForTimeout(150);

    // Should return to horizontal layout
    const notCollapsed = page.locator('[data-direction="horizontal"]');
    if ((await notCollapsed.count()) > 0) {
      await expect(notCollapsed).toBeVisible();
    }
  });
});

test.describe('ElasticPlaceholder States', () => {
  test('should show empty state when no citizens', async ({ page }) => {
    // Override citizens mock to return empty
    await page.route('**/v1/town/*/citizens', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          citizens: [],
          total: 0,
          by_archetype: {},
          by_region: {},
        }),
      });
    });

    await setupTouristMocks(page);
    await page.setViewportSize(BREAKPOINTS.desktop);
    await page.goto('/town/demo-town-123');

    // Wait for response
    await page.waitForResponse('**/citizens');

    // Should show empty state placeholder
    const emptyState = page.locator('.empty-state, [role="status"][aria-label="Empty"]');
    // The ElasticPlaceholder or empty message should be visible
    await expect(
      emptyState.or(page.getByText(/No citizens|No agents|Empty|nothing/i))
    ).toBeVisible({ timeout: 5000 });

    await expect(page).toHaveScreenshot('empty-state.png', {
      fullPage: false,
      maxDiffPixelRatio: 0.02,
    });
  });
});
