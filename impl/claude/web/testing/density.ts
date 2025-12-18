/**
 * Density Matrix Testing Utilities
 *
 * Aligns with docs/skills/elastic-ui-patterns.md breakpoints.
 * Provides systematic density testing for all Crown Jewels.
 *
 * @see plans/playwright-witness-protocol.md
 */

// =============================================================================
// Types
// =============================================================================

export const DENSITIES = ['compact', 'comfortable', 'spacious'] as const;
export type Density = (typeof DENSITIES)[number];

export const DENSITY_VIEWPORTS: Record<Density, { width: number; height: number }> = {
  compact: { width: 375, height: 667 }, // Mobile (iPhone SE)
  comfortable: { width: 768, height: 1024 }, // Tablet (iPad)
  spacious: { width: 1440, height: 900 }, // Desktop
};

/**
 * Extended breakpoints for granular testing.
 * Maps to elastic-ui-patterns.md thresholds.
 */
export const EXTENDED_VIEWPORTS = {
  // Mobile sizes
  mobile_xs: { width: 320, height: 568 }, // iPhone SE (old)
  mobile_sm: { width: 375, height: 667 }, // iPhone SE
  mobile_md: { width: 414, height: 896 }, // iPhone 11
  mobile_lg: { width: 428, height: 926 }, // iPhone 14 Pro Max

  // Tablet sizes
  tablet_portrait: { width: 768, height: 1024 }, // iPad portrait
  tablet_landscape: { width: 1024, height: 768 }, // iPad landscape

  // Desktop sizes
  desktop_sm: { width: 1280, height: 800 }, // Small desktop
  desktop_md: { width: 1440, height: 900 }, // Standard desktop
  desktop_lg: { width: 1920, height: 1080 }, // Full HD
  desktop_xl: { width: 2560, height: 1440 }, // QHD
} as const;

// =============================================================================
// Density Mapping Functions
// =============================================================================

/**
 * Get density from viewport width.
 * Mirrors useWindowLayout hook logic.
 */
export function getDensityFromWidth(width: number): Density {
  if (width < 768) return 'compact';
  if (width < 1024) return 'comfortable';
  return 'spacious';
}

/**
 * Get content level from container width.
 * Mirrors elastic-ui-patterns.md content degradation.
 */
export type ContentLevel = 'icon' | 'title' | 'summary' | 'full';

export function getContentLevelFromWidth(width: number): ContentLevel {
  if (width < 60) return 'icon';
  if (width < 150) return 'title';
  if (width < 280) return 'summary';
  return 'full';
}

// =============================================================================
// Test Helpers
// =============================================================================

/**
 * Generate test matrix for all density × route combinations.
 */
export function densityMatrix<T>(
  routes: T[]
): Array<{ density: Density; viewport: { width: number; height: number }; route: T }> {
  return DENSITIES.flatMap((density) =>
    routes.map((route) => ({
      density,
      viewport: DENSITY_VIEWPORTS[density],
      route,
    }))
  );
}

/**
 * Generate extended viewport matrix for thorough testing.
 */
export function extendedViewportMatrix<T>(
  routes: T[]
): Array<{
  name: keyof typeof EXTENDED_VIEWPORTS;
  viewport: { width: number; height: number };
  density: Density;
  route: T;
}> {
  return Object.entries(EXTENDED_VIEWPORTS).flatMap(([name, viewport]) =>
    routes.map((route) => ({
      name: name as keyof typeof EXTENDED_VIEWPORTS,
      viewport,
      density: getDensityFromWidth(viewport.width),
      route,
    }))
  );
}

/**
 * CSS to inject for deterministic visual testing.
 * Disables animations and transitions.
 */
export const DETERMINISTIC_CSS = `
  *,
  *::before,
  *::after {
    animation-duration: 0s !important;
    animation-delay: 0s !important;
    transition-duration: 0s !important;
    transition-delay: 0s !important;
  }
`;

/**
 * Screenshot mask regions for dynamic content.
 * Use these to mask timestamps, counters, etc.
 */
export const MASK_SELECTORS = {
  timestamps: '[data-testid="timestamp"], .timestamp, time',
  counters: '[data-testid="counter"], .live-counter',
  animations: '[data-testid="animation"], .breathing, .pulsing',
  randomContent: '[data-testid="random"], .random-seed',
} as const;
