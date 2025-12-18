/**
 * Testing Utilities Index
 *
 * Playwright Witness Protocol testing infrastructure.
 *
 * @see plans/playwright-witness-protocol.md
 */

// =============================================================================
// Density Matrix
// =============================================================================

export {
  DENSITIES,
  DENSITY_VIEWPORTS,
  EXTENDED_VIEWPORTS,
  getDensityFromWidth,
  getContentLevelFromWidth,
  densityMatrix,
  extendedViewportMatrix,
  DETERMINISTIC_CSS,
  MASK_SELECTORS,
  type Density,
  type ContentLevel,
} from './density';

// =============================================================================
// Observer Umwelts
// =============================================================================

export {
  OBSERVER_TIERS,
  OBSERVER_CONFIGS,
  MOCK_BUDGETS,
  setupObserverMocks,
  tierHasFeature,
  getExclusiveFeatures,
  type ObserverTier,
  type ObserverConfig,
} from './observers';

// =============================================================================
// Saboteurs (Chaos)
// =============================================================================

export {
  createSeededRandom,
  viewportFlicker,
  latencyRoute,
  flakyRoute,
  networkFlap,
  slowNetwork,
  malformedJsonRoute,
  emptyRoute,
  unexpectedShapeRoute,
  chaosSSEStream,
  fullChaos,
  createChaosSession,
  type ChaosReport,
} from './saboteurs';

// =============================================================================
// HotData Fixtures
// =============================================================================

export {
  hotdata,
  HOT_CITIZENS,
  HOT_DIALOGUES,
  HOT_MANIFESTS,
  setupHotDataMocks,
  type HotCitizen,
  type HotDialogue,
  type HotManifest,
} from './hotdata';

// =============================================================================
// Operad (Composition)
// =============================================================================

export {
  // Atomic ops
  navigate,
  setDensity,
  setupTier,
  waitNetworkIdle,
  waitForApi,
  assertVisible,
  assertNotVisible,
  assertText,
  click,
  fill,
  screenshot,
  assertNoOverflow,
  assertNoConsoleErrors,
  // Composition
  composeTest,
  parallel,
  when,
  repeat,
  // Composed flows
  standardSetup,
  fullPageLoad,
  visualRegression,
  tierGating,
  // Matrix generators
  generateTestMatrix,
  generateDensityMatrix,
  generateTierMatrix,
  // Law verification
  verifyDensityIsomorphism,
  verifyProjectionDeterminism,
  type TestContext,
  type TestOp,
  type TestCase,
} from './operad';

// =============================================================================
// Convenience Re-exports
// =============================================================================

/**
 * Quick setup for common test scenarios.
 */
export const setup = {
  tourist: (page: import('@playwright/test').Page) =>
    import('./observers').then((m) => m.setupObserverMocks(page, 'TOURIST')),
  resident: (page: import('@playwright/test').Page) =>
    import('./observers').then((m) => m.setupObserverMocks(page, 'RESIDENT')),
  citizen: (page: import('@playwright/test').Page) =>
    import('./observers').then((m) => m.setupObserverMocks(page, 'CITIZEN')),
  hotdata: (page: import('@playwright/test').Page) =>
    import('./hotdata').then((m) => m.setupHotDataMocks(page)),
};

/**
 * Tags for test filtering.
 * Use with: npx playwright test --grep @tag
 */
export const TAGS = {
  contract: '@contract',
  chaos: '@chaos',
  spy: '@spy',
  visual: '@visual',
  e2e: '@e2e',
  smoke: '@smoke',
} as const;
