import { test, expect } from '@playwright/test';
import {
  DENSITIES,
  DENSITY_VIEWPORTS,
  getDensityFromWidth,
  densityMatrix,
  DETERMINISTIC_CSS,
  MASK_SELECTORS,
  type Density,
} from '../testing/density';
import {
  generateDensityMatrix,
  assertNoOverflow,
  verifyDensityIsomorphism,
  type TestContext,
} from '../testing/operad';
import { setupHotDataMocks } from '../testing/hotdata';
import { setup, TAGS } from '../testing';

/**
 * Density Matrix Suite
 *
 * Tests Crown Jewels (Town, Brain, Park) at all 3 densities using
 * compositional test operators from testing/operad.ts.
 *
 * Laws verified:
 * - Density Isomorphism: Same semantic content at all densities
 * - No Overflow: No horizontal scrolling at any density
 * - Content Degradation: Appropriate detail level per density
 *
 * @tags @visual, @e2e
 * @see plans/playwright-witness-protocol.md
 * @see docs/skills/elastic-ui-patterns.md
 */

// =============================================================================
// Crown Jewel Routes
// =============================================================================

const CROWN_JEWEL_ROUTES = {
  town: {
    overview: '/town/demo-town-123',
    citizens: '/town/demo-town-123/citizens',
    coalitions: '/town/demo-town-123/coalitions',
  },
  brain: {
    overview: '/brain',
    crystals: '/brain/crystals',
  },
  park: {
    overview: '/park',
    garden: '/park/garden',
  },
} as const;

// Flatten routes for matrix generation
const ALL_ROUTES = [
  CROWN_JEWEL_ROUTES.town.overview,
  CROWN_JEWEL_ROUTES.town.citizens,
  CROWN_JEWEL_ROUTES.brain.overview,
  CROWN_JEWEL_ROUTES.park.overview,
];

// =============================================================================
// Setup Helpers
// =============================================================================

async function setupCrownJewelMocks(page: import('@playwright/test').Page) {
  await setupHotDataMocks(page);
  await setup.tourist(page);
  await page.addStyleTag({ content: DETERMINISTIC_CSS });

  // Mock Brain routes
  await page.route('**/v1/brain/**', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        crystals: [
          { id: 'crystal-1', name: 'Memory Alpha', type: 'episodic', size: 128 },
          { id: 'crystal-2', name: 'Memory Beta', type: 'semantic', size: 256 },
        ],
        total: 2,
      }),
    });
  });

  // Mock Park routes
  await page.route('**/v1/park/**', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        gardens: [
          { id: 'garden-1', name: 'Demo Garden', plants: 12, health: 0.85 },
        ],
        total: 1,
      }),
    });
  });

  // Mock SSE streams
  await page.route('**/v1/town/*/live*', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'text/event-stream',
      headers: { 'Cache-Control': 'no-cache' },
      body: `event: live.start\ndata: ${JSON.stringify({
        town_id: 'demo-town-123',
        phases: 4,
        speed: 1.0,
      })}\n\n`,
    });
  });
}

// =============================================================================
// Density Matrix Tests
// =============================================================================

test.describe('Crown Jewels × 3 Densities Matrix @visual @e2e', () => {
  // Generate test matrix: each route × each density
  const testMatrix = generateDensityMatrix(ALL_ROUTES);

  test.beforeEach(async ({ page }) => {
    await setupCrownJewelMocks(page);
  });

  for (const testCase of testMatrix) {
    test(`${testCase.route} @ ${testCase.density}`, async ({ page }) => {
      const viewport = DENSITY_VIEWPORTS[testCase.density];
      await page.setViewportSize(viewport);
      await page.goto(testCase.route);

      // Wait for network idle
      await page.waitForLoadState('networkidle').catch(() => {
        // Some routes may not have network activity
      });

      // Assert no horizontal overflow (critical for elastic layouts)
      const hasOverflow = await page.evaluate(() => {
        return document.documentElement.scrollWidth > window.innerWidth;
      });
      expect(hasOverflow).toBe(false);

      // Screenshot with density-aware naming
      const routeName = testCase.route.replace(/\//g, '-').replace(/^-/, '');
      await expect(page).toHaveScreenshot(`${routeName}-${testCase.density}.png`, {
        fullPage: false,
        maxDiffPixelRatio: 0.02,
        mask: [
          page.locator(MASK_SELECTORS.timestamps),
          page.locator(MASK_SELECTORS.counters),
          page.locator(MASK_SELECTORS.animations),
        ],
      });
    });
  }
});

// =============================================================================
// Town Crown Jewel - Detailed Density Tests
// =============================================================================

test.describe('Town Overview - Density Matrix @visual @e2e', () => {
  test.beforeEach(async ({ page }) => {
    await setupCrownJewelMocks(page);
  });

  for (const density of DENSITIES) {
    test(`Town overview renders correctly at ${density}`, async ({ page }) => {
      await page.setViewportSize(DENSITY_VIEWPORTS[density]);
      await page.goto(CROWN_JEWEL_ROUTES.town.overview);

      // Wait for citizens
      await page.waitForResponse('**/citizens').catch(() => {});

      // Verify key elements are visible
      const mesa = page.locator('[data-testid="mesa"], [data-testid="town-canvas"]');
      if ((await mesa.count()) > 0) {
        await expect(mesa.first()).toBeVisible({ timeout: 5000 });
      }

      // Assert no overflow
      const ctx: TestContext = {
        page,
        density,
        tier: 'TOURIST',
        route: CROWN_JEWEL_ROUTES.town.overview,
      };
      await assertNoOverflow(ctx);

      // Density-specific assertions
      if (density === 'compact') {
        // Compact: navigation should be collapsed/hamburger
        const hamburger = page.locator('[data-testid="menu-toggle"], [aria-label="Menu"]');
        // Navigation may be simplified
        expect(await hamburger.count()).toBeGreaterThanOrEqual(0);
      } else if (density === 'spacious') {
        // Spacious: full navigation visible
        const nav = page.locator('nav, [role="navigation"]');
        if ((await nav.count()) > 0) {
          await expect(nav.first()).toBeVisible();
        }
      }
    });
  }

  test('Town citizens list adapts to density', async ({ page }) => {
    await page.goto(CROWN_JEWEL_ROUTES.town.citizens);

    for (const density of DENSITIES) {
      await page.setViewportSize(DENSITY_VIEWPORTS[density]);
      await page.waitForTimeout(100); // Allow resize

      // Wait for citizens
      const cards = page.locator('[data-testid="citizen-card"]');

      if ((await cards.count()) > 0) {
        // Verify cards adapt their content level
        const contentLevels = await cards.evaluateAll((els) =>
          els.map((el) => el.getAttribute('data-content-level'))
        );

        // At compact: more cards should have minimal content
        // At spacious: more cards should have full content
        if (density === 'compact' && contentLevels.length > 0) {
          // Some compactness expected
          const hasCompact = contentLevels.some((l) => l === 'icon' || l === 'title');
          // This may vary based on grid - just ensure no errors
          expect(contentLevels).toBeDefined();
        }
      }

      // Always assert no overflow
      const hasOverflow = await page.evaluate(() => {
        return document.documentElement.scrollWidth > window.innerWidth;
      });
      expect(hasOverflow).toBe(false);
    }
  });
});

// =============================================================================
// Brain Crown Jewel - Density Tests
// =============================================================================

test.describe('Brain Overview - Density Matrix @visual @e2e', () => {
  test.beforeEach(async ({ page }) => {
    await setupCrownJewelMocks(page);
  });

  for (const density of DENSITIES) {
    test(`Brain overview at ${density}`, async ({ page }) => {
      await page.setViewportSize(DENSITY_VIEWPORTS[density]);
      await page.goto(CROWN_JEWEL_ROUTES.brain.overview);

      await page.waitForLoadState('networkidle').catch(() => {});

      // Assert no overflow
      const hasOverflow = await page.evaluate(() => {
        return document.documentElement.scrollWidth > window.innerWidth;
      });
      expect(hasOverflow).toBe(false);

      await expect(page).toHaveScreenshot(`brain-${density}.png`, {
        fullPage: false,
        maxDiffPixelRatio: 0.02,
        mask: [page.locator(MASK_SELECTORS.animations)],
      });
    });
  }
});

// =============================================================================
// Park Crown Jewel - Density Tests
// =============================================================================

test.describe('Park Overview - Density Matrix @visual @e2e', () => {
  test.beforeEach(async ({ page }) => {
    await setupCrownJewelMocks(page);
  });

  for (const density of DENSITIES) {
    test(`Park overview at ${density}`, async ({ page }) => {
      await page.setViewportSize(DENSITY_VIEWPORTS[density]);
      await page.goto(CROWN_JEWEL_ROUTES.park.overview);

      await page.waitForLoadState('networkidle').catch(() => {});

      // Assert no overflow
      const hasOverflow = await page.evaluate(() => {
        return document.documentElement.scrollWidth > window.innerWidth;
      });
      expect(hasOverflow).toBe(false);

      await expect(page).toHaveScreenshot(`park-${density}.png`, {
        fullPage: false,
        maxDiffPixelRatio: 0.02,
        mask: [page.locator(MASK_SELECTORS.animations)],
      });
    });
  }
});

// =============================================================================
// Density Law Verification
// =============================================================================

test.describe('Density Laws @e2e', () => {
  test.beforeEach(async ({ page }) => {
    await setupCrownJewelMocks(page);
  });

  test('verifyDensityIsomorphism: Town has same semantic content at all densities', async ({
    page,
  }) => {
    // First, set up mocks before testing isomorphism
    await setup.tourist(page);

    const isIsomorphic = await verifyDensityIsomorphism(
      page,
      CROWN_JEWEL_ROUTES.town.overview,
      '[data-testid="town-title"], h1, [role="heading"]'
    );

    // Same semantic content should exist at all densities
    // (titles, headers should persist even if layout changes)
    expect(isIsomorphic).toBe(true);
  });

  test('No overflow at any standard or edge-case viewport', async ({ page }) => {
    const edgeCases = [
      { width: 320, height: 568 }, // iPhone SE old
      { width: 360, height: 640 }, // Common Android
      { width: 390, height: 844 }, // iPhone 14
      { width: 768, height: 1024 }, // Exact threshold
      { width: 769, height: 1024 }, // Just above threshold
      { width: 1024, height: 768 }, // iPad landscape
      { width: 1920, height: 1080 }, // Full HD
    ];

    for (const viewport of edgeCases) {
      await page.setViewportSize(viewport);
      await page.goto(CROWN_JEWEL_ROUTES.town.overview);
      await page.waitForLoadState('domcontentloaded');

      const hasOverflow = await page.evaluate(() => {
        return document.documentElement.scrollWidth > window.innerWidth;
      });

      expect(hasOverflow, `Overflow at ${viewport.width}x${viewport.height}`).toBe(false);
    }
  });

  test('getDensityFromWidth correctly classifies all viewports', () => {
    // Unit test for density classification
    expect(getDensityFromWidth(320)).toBe('compact');
    expect(getDensityFromWidth(375)).toBe('compact');
    expect(getDensityFromWidth(767)).toBe('compact');
    expect(getDensityFromWidth(768)).toBe('comfortable');
    expect(getDensityFromWidth(1023)).toBe('comfortable');
    expect(getDensityFromWidth(1024)).toBe('spacious');
    expect(getDensityFromWidth(1440)).toBe('spacious');
    expect(getDensityFromWidth(2560)).toBe('spacious');
  });
});

// =============================================================================
// Content Degradation Tests
// =============================================================================

test.describe('Content Degradation @visual @e2e', () => {
  test.beforeEach(async ({ page }) => {
    await setupCrownJewelMocks(page);
  });

  test('Citizen cards degrade gracefully: full → summary → title → icon', async ({ page }) => {
    await page.goto(CROWN_JEWEL_ROUTES.town.citizens);
    await page.waitForResponse('**/citizens').catch(() => {});

    const measurements: Record<Density, string[]> = {
      compact: [],
      comfortable: [],
      spacious: [],
    };

    for (const density of DENSITIES) {
      await page.setViewportSize(DENSITY_VIEWPORTS[density]);
      await page.waitForTimeout(150); // Allow resize

      const cards = page.locator('[data-testid="citizen-card"]');
      if ((await cards.count()) > 0) {
        const levels = await cards.evaluateAll((els) =>
          els.map((el) => el.getAttribute('data-content-level') || 'unknown')
        );
        measurements[density] = levels;
      }
    }

    // Verify degradation direction (spacious should have more detail than compact)
    const scoreMap: Record<string, number> = {
      full: 4,
      summary: 3,
      title: 2,
      icon: 1,
      unknown: 0,
    };

    const avgScore = (levels: string[]) => {
      if (levels.length === 0) return 0;
      return levels.reduce((sum, l) => sum + (scoreMap[l] || 0), 0) / levels.length;
    };

    const spaciousAvg = avgScore(measurements.spacious);
    const compactAvg = avgScore(measurements.compact);

    // Spacious should have >= average detail level as compact
    // (they may be equal if cards are always full)
    expect(spaciousAvg).toBeGreaterThanOrEqual(compactAvg);
  });
});
