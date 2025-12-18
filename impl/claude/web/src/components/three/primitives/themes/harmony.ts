/**
 * Theme Harmony - Cross-jewel visual compatibility checker
 *
 * When multiple Crown Jewels render in the same scene (e.g., Brain + Gestalt
 * showing memory and code together), their themes must be harmonious.
 *
 * Philosophy:
 *   "Themes are not just colors—they are visual languages that must not clash."
 *
 * Harmony rules:
 * 1. Edge colors must have sufficient contrast
 * 2. Selection indicators should be distinguishable
 * 3. Background atmospheres should blend gracefully
 *
 * @see plans/3d-projection-consolidation.md
 */

import type { ThemePalette, EdgeColors } from './types';

// =============================================================================
// Types
// =============================================================================

/**
 * Harmony check result.
 */
export interface HarmonyResult {
  /** Whether themes are harmonious */
  harmonious: boolean;
  /** Specific issues found (if not harmonious) */
  issues: HarmonyIssue[];
  /** Harmony score (0-1, higher = more harmonious) */
  score: number;
  /** Recommendations for improvement */
  recommendations: string[];
}

/**
 * A specific harmony issue.
 */
export interface HarmonyIssue {
  /** Issue type */
  type: 'edge_clash' | 'selection_ambiguity' | 'atmosphere_conflict' | 'label_readability';
  /** Severity (0-1, higher = more severe) */
  severity: number;
  /** Human-readable description */
  description: string;
}

/**
 * RGB color representation.
 */
interface RGB {
  r: number;
  g: number;
  b: number;
}

// =============================================================================
// Color Utilities
// =============================================================================

/**
 * Parse hex color to RGB.
 */
function hexToRgb(hex: string): RGB {
  const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
  if (!result) {
    return { r: 128, g: 128, b: 128 }; // Fallback gray
  }
  return {
    r: parseInt(result[1], 16),
    g: parseInt(result[2], 16),
    b: parseInt(result[3], 16),
  };
}

/**
 * Calculate relative luminance (WCAG formula).
 */
function getLuminance(rgb: RGB): number {
  const [rs, gs, bs] = [rgb.r / 255, rgb.g / 255, rgb.b / 255].map((c) =>
    c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4)
  );
  return 0.2126 * rs + 0.7152 * gs + 0.0722 * bs;
}

/**
 * Calculate contrast ratio between two colors.
 * Returns ratio from 1:1 (no contrast) to 21:1 (max contrast).
 */
function getContrastRatio(color1: string, color2: string): number {
  const lum1 = getLuminance(hexToRgb(color1));
  const lum2 = getLuminance(hexToRgb(color2));
  const lighter = Math.max(lum1, lum2);
  const darker = Math.min(lum1, lum2);
  return (lighter + 0.05) / (darker + 0.05);
}

/**
 * Calculate color distance in RGB space (Euclidean).
 * Returns 0 (identical) to ~442 (max distance).
 */
function getColorDistance(color1: string, color2: string): number {
  const rgb1 = hexToRgb(color1);
  const rgb2 = hexToRgb(color2);
  return Math.sqrt(
    Math.pow(rgb1.r - rgb2.r, 2) +
    Math.pow(rgb1.g - rgb2.g, 2) +
    Math.pow(rgb1.b - rgb2.b, 2)
  );
}

/**
 * Get dominant hue category (0-6) from hex color.
 */
function getHueCategory(hex: string): number {
  const rgb = hexToRgb(hex);
  const r = rgb.r / 255;
  const g = rgb.g / 255;
  const b = rgb.b / 255;
  const max = Math.max(r, g, b);
  const min = Math.min(r, g, b);

  if (max === min) return 0; // Achromatic (gray)

  let h = 0;
  const d = max - min;
  if (max === r) h = ((g - b) / d + (g < b ? 6 : 0)) / 6;
  else if (max === g) h = ((b - r) / d + 2) / 6;
  else h = ((r - g) / d + 4) / 6;

  // Categorize into: red, orange, yellow, green, cyan, blue, purple
  return Math.floor(h * 7);
}

// =============================================================================
// Harmony Checks
// =============================================================================

/**
 * Minimum contrast ratio for distinguishable edges.
 */
const MIN_EDGE_CONTRAST = 1.5;

/**
 * Minimum color distance for distinguishable selection.
 */
const MIN_SELECTION_DISTANCE = 100;

/**
 * Check edge color harmony.
 */
function checkEdgeHarmony(edges1: EdgeColors, edges2: EdgeColors): HarmonyIssue[] {
  const issues: HarmonyIssue[] = [];

  // Check if base edges are distinguishable when both visible
  const baseContrast = getContrastRatio(edges1.base, edges2.base);
  if (baseContrast < MIN_EDGE_CONTRAST) {
    issues.push({
      type: 'edge_clash',
      severity: 0.6,
      description: `Base edge colors have low contrast (${baseContrast.toFixed(2)}:1)`,
    });
  }

  // Check highlight edges
  const highlightContrast = getContrastRatio(edges1.highlight, edges2.highlight);
  if (highlightContrast < MIN_EDGE_CONTRAST) {
    issues.push({
      type: 'edge_clash',
      severity: 0.8,
      description: `Highlighted edge colors may clash (${highlightContrast.toFixed(2)}:1)`,
    });
  }

  return issues;
}

/**
 * Check selection indicator harmony.
 */
function checkSelectionHarmony(theme1: ThemePalette, theme2: ThemePalette): HarmonyIssue[] {
  const issues: HarmonyIssue[] = [];

  const distance = getColorDistance(theme1.selectionColor, theme2.selectionColor);
  if (distance < MIN_SELECTION_DISTANCE) {
    issues.push({
      type: 'selection_ambiguity',
      severity: 0.7,
      description: `Selection colors are too similar (distance: ${distance.toFixed(0)})`,
    });
  }

  return issues;
}

/**
 * Check atmosphere compatibility.
 */
function checkAtmosphereHarmony(theme1: ThemePalette, theme2: ThemePalette): HarmonyIssue[] {
  const issues: HarmonyIssue[] = [];

  const bg1 = theme1.atmosphere?.background;
  const bg2 = theme2.atmosphere?.background;

  if (bg1 && bg2) {
    // Backgrounds should either be similar (blend) or have clear demarcation
    const bgDistance = getColorDistance(bg1, bg2);
    const hue1 = getHueCategory(bg1);
    const hue2 = getHueCategory(bg2);

    // If backgrounds are different but not dramatically different = awkward
    if (bgDistance > 30 && bgDistance < 80 && hue1 !== hue2) {
      issues.push({
        type: 'atmosphere_conflict',
        severity: 0.4,
        description: 'Background colors may create visual tension when blended',
      });
    }
  }

  return issues;
}

/**
 * Check label readability in mixed scene.
 */
function checkLabelHarmony(theme1: ThemePalette, theme2: ThemePalette): HarmonyIssue[] {
  const issues: HarmonyIssue[] = [];

  // Labels should be readable against the other theme's background
  const bg2 = theme2.atmosphere?.background ?? '#0D1117';
  const labelContrast = getContrastRatio(theme1.labelColor, bg2);

  if (labelContrast < 4.5) {
    // WCAG AA minimum
    issues.push({
      type: 'label_readability',
      severity: 0.5,
      description: `Labels from ${theme1.name} may be hard to read on ${theme2.name} background`,
    });
  }

  return issues;
}

// =============================================================================
// Main Functions
// =============================================================================

/**
 * Check if two themes are harmonious when rendered together.
 *
 * Usage:
 * ```typescript
 * import { checkThemeHarmony, CRYSTAL_THEME, FOREST_THEME } from './themes';
 *
 * const result = checkThemeHarmony(CRYSTAL_THEME, FOREST_THEME);
 * if (!result.harmonious) {
 *   console.warn('Themes may clash:', result.issues);
 * }
 * ```
 */
export function checkThemeHarmony(theme1: ThemePalette, theme2: ThemePalette): HarmonyResult {
  const issues: HarmonyIssue[] = [
    ...checkEdgeHarmony(theme1.edgeColors, theme2.edgeColors),
    ...checkSelectionHarmony(theme1, theme2),
    ...checkAtmosphereHarmony(theme1, theme2),
    ...checkLabelHarmony(theme1, theme2),
    ...checkLabelHarmony(theme2, theme1), // Check both directions
  ];

  // Calculate score (1 = perfect, 0 = total clash)
  const totalSeverity = issues.reduce((sum, issue) => sum + issue.severity, 0);
  const maxPossibleSeverity = 4; // Rough estimate
  const score = Math.max(0, 1 - totalSeverity / maxPossibleSeverity);

  // Generate recommendations
  const recommendations: string[] = [];
  if (issues.some((i) => i.type === 'edge_clash')) {
    recommendations.push('Consider using different edge width or dash patterns to distinguish themes');
  }
  if (issues.some((i) => i.type === 'selection_ambiguity')) {
    recommendations.push('Use shape differences (ring vs square) for selection indicators');
  }
  if (issues.some((i) => i.type === 'atmosphere_conflict')) {
    recommendations.push('Use a gradient or clear boundary between theme regions');
  }
  if (issues.some((i) => i.type === 'label_readability')) {
    recommendations.push('Add stronger label outlines or backgrounds for mixed scenes');
  }

  return {
    harmonious: issues.every((i) => i.severity < 0.5),
    issues,
    score,
    recommendations,
  };
}

/**
 * Quick check if themes are compatible (boolean result).
 */
export function areThemesCompatible(theme1: ThemePalette, theme2: ThemePalette): boolean {
  return checkThemeHarmony(theme1, theme2).harmonious;
}

/**
 * Get a blend color for use in transition zones between themes.
 */
export function getThemeBlendColor(theme1: ThemePalette, theme2: ThemePalette): string {
  const bg1 = hexToRgb(theme1.atmosphere?.background ?? '#0D1117');
  const bg2 = hexToRgb(theme2.atmosphere?.background ?? '#0D1117');

  // Simple midpoint blend
  const blended = {
    r: Math.round((bg1.r + bg2.r) / 2),
    g: Math.round((bg1.g + bg2.g) / 2),
    b: Math.round((bg1.b + bg2.b) / 2),
  };

  return `#${blended.r.toString(16).padStart(2, '0')}${blended.g.toString(16).padStart(2, '0')}${blended.b.toString(16).padStart(2, '0')}`;
}

// =============================================================================
// Known Theme Pairs
// =============================================================================

/**
 * Pre-checked theme pair compatibility.
 * Cached for performance.
 */
export const KNOWN_COMPATIBLE_PAIRS: Record<string, boolean> = {
  'crystal-forest': true, // Crystal (cyan/purple) + Forest (green/red) = complementary
};

/**
 * Quick lookup for known theme pairs.
 */
export function areKnownCompatible(theme1Name: string, theme2Name: string): boolean | undefined {
  const key1 = `${theme1Name}-${theme2Name}`;
  const key2 = `${theme2Name}-${theme1Name}`;
  return KNOWN_COMPATIBLE_PAIRS[key1] ?? KNOWN_COMPATIBLE_PAIRS[key2];
}

export default checkThemeHarmony;
