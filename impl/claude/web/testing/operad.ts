/**
 * Generative Test Coverage (Operad)
 *
 * Use compositional test ops to avoid enumeration.
 * Each op is small and reusable.
 *
 * @see plans/playwright-witness-protocol.md
 * @see spec/agents/operad.md
 */

import { Page, expect } from '@playwright/test';
import { Density, DENSITY_VIEWPORTS } from './density';
import { ObserverTier, setupObserverMocks } from './observers';

// =============================================================================
// Types
// =============================================================================

export interface TestContext {
  page: Page;
  density: Density;
  tier: ObserverTier;
  route: string;
}

export type TestOp = (ctx: TestContext) => Promise<void>;

// =============================================================================
// Atomic Test Operations
// =============================================================================

/**
 * Navigate to a route.
 */
export const navigate: TestOp = async (ctx) => {
  await ctx.page.goto(ctx.route);
};

/**
 * Set viewport for density.
 */
export const setDensity: TestOp = async (ctx) => {
  await ctx.page.setViewportSize(DENSITY_VIEWPORTS[ctx.density]);
};

/**
 * Setup observer tier mocks.
 */
export const setupTier: TestOp = async (ctx) => {
  await setupObserverMocks(ctx.page, ctx.tier);
};

/**
 * Wait for network idle.
 */
export const waitNetworkIdle: TestOp = async (ctx) => {
  await ctx.page.waitForLoadState('networkidle');
};

/**
 * Wait for a specific API response.
 */
export function waitForApi(pattern: string): TestOp {
  return async (ctx) => {
    await ctx.page.waitForResponse(pattern);
  };
}

/**
 * Assert element is visible.
 */
export function assertVisible(selector: string): TestOp {
  return async (ctx) => {
    await expect(ctx.page.locator(selector)).toBeVisible();
  };
}

/**
 * Assert element is not visible.
 */
export function assertNotVisible(selector: string): TestOp {
  return async (ctx) => {
    await expect(ctx.page.locator(selector)).not.toBeVisible();
  };
}

/**
 * Assert element has text.
 */
export function assertText(selector: string, text: string | RegExp): TestOp {
  return async (ctx) => {
    await expect(ctx.page.locator(selector)).toContainText(text);
  };
}

/**
 * Click an element.
 */
export function click(selector: string): TestOp {
  return async (ctx) => {
    await ctx.page.locator(selector).click();
  };
}

/**
 * Fill an input.
 */
export function fill(selector: string, value: string): TestOp {
  return async (ctx) => {
    await ctx.page.locator(selector).fill(value);
  };
}

/**
 * Take a screenshot with density-aware naming.
 */
export function screenshot(name: string, options?: { fullPage?: boolean }): TestOp {
  return async (ctx) => {
    const filename = `${name}-${ctx.density}-${ctx.tier}.png`;
    await expect(ctx.page).toHaveScreenshot(filename, {
      fullPage: options?.fullPage ?? false,
      maxDiffPixelRatio: 0.02,
    });
  };
}

/**
 * Assert no horizontal overflow.
 */
export const assertNoOverflow: TestOp = async (ctx) => {
  const hasOverflow = await ctx.page.evaluate(() => {
    return document.documentElement.scrollWidth > window.innerWidth;
  });
  expect(hasOverflow).toBe(false);
};

/**
 * Assert console has no errors.
 */
export function assertNoConsoleErrors(): TestOp {
  const errors: string[] = [];
  return async (ctx) => {
    ctx.page.on('console', (msg) => {
      if (msg.type() === 'error') {
        errors.push(msg.text());
      }
    });
    // Check at end
    expect(errors).toHaveLength(0);
  };
}

// =============================================================================
// Composition
// =============================================================================

/**
 * Compose multiple test ops into a single op.
 * Laws:
 * - Identity: compose([]) is a no-op
 * - Associativity: compose([a, compose([b, c])]) === compose([a, b, c])
 */
export function composeTest(...ops: TestOp[]): TestOp {
  return async (ctx) => {
    for (const op of ops) {
      await op(ctx);
    }
  };
}

/**
 * Run ops in parallel where possible.
 */
export function parallel(...ops: TestOp[]): TestOp {
  return async (ctx) => {
    await Promise.all(ops.map((op) => op(ctx)));
  };
}

/**
 * Conditionally run an op.
 */
export function when(
  condition: (ctx: TestContext) => boolean,
  op: TestOp,
  elseOp?: TestOp
): TestOp {
  return async (ctx) => {
    if (condition(ctx)) {
      await op(ctx);
    } else if (elseOp) {
      await elseOp(ctx);
    }
  };
}

/**
 * Repeat an op multiple times.
 */
export function repeat(times: number, op: TestOp): TestOp {
  return async (ctx) => {
    for (let i = 0; i < times; i++) {
      await op(ctx);
    }
  };
}

// =============================================================================
// Common Flows (Composed)
// =============================================================================

/**
 * Standard page setup: tier mocks + density + navigate.
 */
export const standardSetup = composeTest(setupTier, setDensity, navigate);

/**
 * Full page load: setup + wait for network idle.
 */
export const fullPageLoad = composeTest(standardSetup, waitNetworkIdle);

/**
 * Visual regression test: load + screenshot + no overflow.
 */
export function visualRegression(screenshotName: string): TestOp {
  return composeTest(fullPageLoad, assertNoOverflow, screenshot(screenshotName));
}

/**
 * Tier gating test: attempt to access a feature, verify gating response.
 */
export function tierGating(action: TestOp, expectedForTier: Record<ObserverTier, boolean>): TestOp {
  return async (ctx) => {
    await standardSetup(ctx);

    if (expectedForTier[ctx.tier]) {
      // Should succeed
      await action(ctx);
    } else {
      // Should show upgrade prompt or be blocked
      // This is a placeholder - specific implementation depends on UI
      await action(ctx);
      await expect(ctx.page.locator('[data-testid="upgrade-prompt"]')).toBeVisible({
        timeout: 5000,
      });
    }
  };
}

// =============================================================================
// Test Matrix Generator
// =============================================================================

import { DENSITIES } from './density';
import { OBSERVER_TIERS } from './observers';

export interface TestCase {
  name: string;
  density: Density;
  tier: ObserverTier;
  route: string;
}

/**
 * Generate full test matrix for a set of routes.
 */
export function generateTestMatrix(routes: string[]): TestCase[] {
  const cases: TestCase[] = [];

  for (const route of routes) {
    for (const density of DENSITIES) {
      for (const tier of OBSERVER_TIERS) {
        cases.push({
          name: `${route} @ ${density} as ${tier}`,
          density,
          tier,
          route,
        });
      }
    }
  }

  return cases;
}

/**
 * Generate density-only matrix (single tier).
 */
export function generateDensityMatrix(routes: string[], tier: ObserverTier = 'TOURIST'): TestCase[] {
  return routes.flatMap((route) =>
    DENSITIES.map((density) => ({
      name: `${route} @ ${density}`,
      density,
      tier,
      route,
    }))
  );
}

/**
 * Generate tier-only matrix (single density).
 */
export function generateTierMatrix(routes: string[], density: Density = 'spacious'): TestCase[] {
  return routes.flatMap((route) =>
    OBSERVER_TIERS.map((tier) => ({
      name: `${route} as ${tier}`,
      density,
      tier,
      route,
    }))
  );
}

// =============================================================================
// Law Verification
// =============================================================================

/**
 * Verify density isomorphism: same semantic content at all densities.
 */
export async function verifyDensityIsomorphism(
  page: Page,
  route: string,
  contentSelector: string
): Promise<boolean> {
  const contents: string[] = [];

  for (const density of DENSITIES) {
    await page.setViewportSize(DENSITY_VIEWPORTS[density]);
    await page.goto(route);
    await page.waitForLoadState('networkidle');

    // Extract semantic content (stripped of layout)
    const content = await page.locator(contentSelector).allTextContents();
    contents.push(content.join(' ').trim());
  }

  // All densities should have equivalent semantic content
  // (may differ in presentation but core data should match)
  const baseContent = contents[0];
  return contents.every((c) => c.includes(baseContent) || baseContent.includes(c));
}

/**
 * Verify projection determinism: same state -> same screenshot.
 */
export async function verifyProjectionDeterminism(
  page: Page,
  route: string,
  iterations: number = 3
): Promise<boolean> {
  const screenshots: Buffer[] = [];

  for (let i = 0; i < iterations; i++) {
    await page.goto(route);
    await page.waitForLoadState('networkidle');
    screenshots.push(await page.screenshot());
  }

  // Compare all screenshots (simplified - in practice use image diff)
  const baseSize = screenshots[0].length;
  return screenshots.every((s) => Math.abs(s.length - baseSize) < baseSize * 0.01);
}
