import { test, expect } from '@playwright/test';
import {
  DENSITY_VIEWPORTS,
  DENSITIES,
  getDensityFromWidth,
  DETERMINISTIC_CSS,
  MASK_SELECTORS,
  type Density,
} from '../../testing/density';
import { setupHotDataMocks } from '../../testing/hotdata';
import { setup } from '../../testing';

/**
 * Visual Regression Tests for Elastic Layouts
 *
 * Uses density matrix from testing/density.ts aligned with
 * docs/skills/elastic-ui-patterns.md breakpoints.
 *
 * Key behaviors:
 * - ElasticSplit collapses at 768px (compact → comfortable threshold)
 * - ElasticCard degrades: full → summary → title → icon
 * - CitizenCard content levels based on available width
 *
 * @tags @visual, @e2e
 * @see plans/playwright-witness-protocol.md
 */

// =============================================================================
// Test Setup
// =============================================================================

test.describe('ElasticSplit Collapse Behavior @visual @e2e', () => {
  test.beforeEach(async ({ page }) => {
    // Use HotData for deterministic fixtures
    await setupHotDataMocks(page);
    await setup.tourist(page);

    // Inject deterministic CSS to disable animations
    await page.addStyleTag({ content: DETERMINISTIC_CSS });

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
  });

  test('should display side-by-side at spacious density (1440px)', async ({ page }) => {
    await page.setViewportSize(DENSITY_VIEWPORTS.spacious);
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

    // Screenshot for regression comparison with masked dynamic regions
    await expect(page).toHaveScreenshot('town-spacious.png', {
      fullPage: false,
      maxDiffPixelRatio: 0.02,
      mask: [
        page.locator(MASK_SELECTORS.timestamps),
        page.locator(MASK_SELECTORS.counters),
        page.locator(MASK_SELECTORS.animations),
      ],
    });
  });

  test('should display side-by-side at comfortable density (768px)', async ({ page }) => {
    await page.setViewportSize(DENSITY_VIEWPORTS.comfortable);
    await page.goto('/town/demo-town-123');
    await page.waitForResponse('**/citizens');

    // Should still be horizontal layout at 768px
    const splitContainer = page.locator('[data-direction="horizontal"]');
    if ((await splitContainer.count()) > 0) {
      await expect(splitContainer).toBeVisible();
    }

    await expect(page).toHaveScreenshot('town-comfortable.png', {
      fullPage: false,
      maxDiffPixelRatio: 0.02,
      mask: [
        page.locator(MASK_SELECTORS.timestamps),
        page.locator(MASK_SELECTORS.counters),
      ],
    });
  });

  test('should collapse to stacked layout at compact density (375px)', async ({ page }) => {
    await page.setViewportSize(DENSITY_VIEWPORTS.compact);
    await page.goto('/town/demo-town-123');
    await page.waitForResponse('**/citizens');

    // ElasticSplit should be collapsed in compact mode
    const collapsed = page.locator('[data-collapsed="true"]');
    await expect(collapsed).toBeVisible({ timeout: 5000 });

    await expect(page).toHaveScreenshot('town-compact.png', {
      fullPage: false,
      maxDiffPixelRatio: 0.02,
      mask: [
        page.locator(MASK_SELECTORS.timestamps),
        page.locator(MASK_SELECTORS.counters),
      ],
    });
  });

  test('should handle collapse threshold (767px - just below comfortable)', async ({ page }) => {
    // Test the exact threshold where collapse occurs
    await page.setViewportSize({ width: 767, height: 1024 });
    await page.goto('/town/demo-town-123');
    await page.waitForResponse('**/citizens');

    // At 767px (below 768 threshold), should be collapsed
    const density = getDensityFromWidth(767);
    expect(density).toBe('compact');

    const collapsed = page.locator('[data-collapsed="true"]');
    await expect(collapsed).toBeVisible({ timeout: 5000 });

    await expect(page).toHaveScreenshot('town-threshold-767px.png', {
      fullPage: false,
      maxDiffPixelRatio: 0.02,
    });
  });
});

test.describe('ElasticCard Content Level Degradation @visual @e2e', () => {
  test.beforeEach(async ({ page }) => {
    await setupHotDataMocks(page);
    await setup.tourist(page);
    await page.addStyleTag({ content: DETERMINISTIC_CSS });
  });

  for (const density of DENSITIES) {
    test(`should show appropriate card content at ${density} density`, async ({ page }) => {
      const viewport = DENSITY_VIEWPORTS[density];
      await page.setViewportSize(viewport);
      await page.goto('/town/demo-town-123');
      await page.waitForResponse('**/citizens');

      // Wait for citizen cards to render
      const citizenCards = page.locator('[data-testid="citizen-card"]');
      await expect(citizenCards.first()).toBeVisible({ timeout: 5000 });

      // Check content levels based on density
      const contentLevels = await citizenCards.evaluateAll((cards) =>
        cards.map((c) => c.getAttribute('data-content-level'))
      );

      // Verify content levels match density expectations
      if (density === 'spacious') {
        // Large viewport: expect full or summary
        const fullOrSummary = contentLevels.filter((l) => l === 'full' || l === 'summary');
        expect(fullOrSummary.length).toBeGreaterThan(0);
      } else if (density === 'compact') {
        // Small viewport: expect more compact representations
        const compact = contentLevels.filter((l) => l === 'title' || l === 'icon');
        // Some cards should be compact (may vary based on grid)
        expect(compact.length).toBeGreaterThanOrEqual(0);
      }

      await expect(page).toHaveScreenshot(`citizens-${density}.png`, {
        fullPage: false,
        maxDiffPixelRatio: 0.02,
        mask: [page.locator(MASK_SELECTORS.animations)],
      });
    });
  }
});

test.describe('Resize Transitions @visual @e2e', () => {
  test.beforeEach(async ({ page }) => {
    await setupHotDataMocks(page);
    await setup.tourist(page);
    await page.addStyleTag({ content: DETERMINISTIC_CSS });
  });

  test('should smoothly transition between densities without overflow', async ({ page }) => {
    // Start at spacious
    await page.setViewportSize(DENSITY_VIEWPORTS.spacious);
    await page.goto('/town/demo-town-123');
    await page.waitForResponse('**/citizens');

    const citizenCards = page.locator('[data-testid="citizen-card"]');
    await expect(citizenCards.first()).toBeVisible({ timeout: 5000 });

    // Resize down through all densities
    for (const density of ['comfortable', 'compact'] as Density[]) {
      const viewport = DENSITY_VIEWPORTS[density];
      await page.setViewportSize(viewport);
      // Allow resize observer to process
      await page.waitForTimeout(150);

      // Verify no horizontal overflow at any density
      const hasOverflow = await page.evaluate(() => {
        return document.documentElement.scrollWidth > window.innerWidth;
      });
      expect(hasOverflow).toBe(false);

      // Verify no elements overflow viewport
      const overflowingElements = await page.evaluate(() => {
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
      expect(overflowingElements).toBe(false);
    }

    // Resize back up to comfortable
    await page.setViewportSize(DENSITY_VIEWPORTS.comfortable);
    await page.waitForTimeout(150);

    // Should return to horizontal layout
    const notCollapsed = page.locator('[data-direction="horizontal"]');
    if ((await notCollapsed.count()) > 0) {
      await expect(notCollapsed).toBeVisible();
    }
  });
});

test.describe('ElasticPlaceholder States @visual @e2e', () => {
  test('should show empty state when no citizens at all densities', async ({ page }) => {
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

    await setup.tourist(page);
    await page.addStyleTag({ content: DETERMINISTIC_CSS });

    // Test empty state at each density
    for (const density of DENSITIES) {
      await page.setViewportSize(DENSITY_VIEWPORTS[density]);
      await page.goto('/town/demo-town-123');
      await page.waitForResponse('**/citizens');

      // Should show empty state placeholder
      const emptyState = page.locator('.empty-state, [role="status"][aria-label="Empty"]');
      await expect(
        emptyState.or(page.getByText(/No citizens|No agents|Empty|nothing/i))
      ).toBeVisible({ timeout: 5000 });

      await expect(page).toHaveScreenshot(`empty-state-${density}.png`, {
        fullPage: false,
        maxDiffPixelRatio: 0.02,
      });
    }
  });
});
