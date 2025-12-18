/**
 * Forest Theme - Gestalt Code Visualization
 *
 * The forest theme represents code modules as plant-like organisms.
 * Health → Vitality: healthy code is lush green, troubled code withers.
 *
 * Color philosophy:
 *   - Natural spectrum (green → lime → yellow → orange → red)
 *   - Growth rings like tree rings
 *   - Organic, living quality
 *
 * @see impl/claude/web/src/components/gestalt/OrganicNode.tsx
 * @see plans/3d-projection-consolidation.md
 */

import type { ThemePalette } from './types';

/**
 * Forest tier names, ordered by code health.
 */
export const FOREST_TIERS = ['healthy', 'good', 'fair', 'poor', 'critical'] as const;
export type ForestTier = (typeof FOREST_TIERS)[number];

/**
 * The Forest Theme Palette
 *
 * Used by Gestalt visualization for code topology.
 */
export const FOREST_THEME: ThemePalette = {
  name: 'forest',
  description: 'Code as living organisms breathing in a forest',

  nodeTiers: {
    healthy: {
      core: '#22C55E',   // Rich green - health >= 0.9
      glow: '#4ADE80',   // Bright green
      ring: '#166534',   // Deep forest green
    },
    good: {
      core: '#84CC16',   // Lime green - health >= 0.7
      glow: '#A3E635',   // Bright lime
      ring: '#365314',   // Dark lime
    },
    fair: {
      core: '#FACC15',   // Golden yellow - health >= 0.5
      glow: '#FDE047',   // Bright yellow
      ring: '#854D0E',   // Bark brown
    },
    poor: {
      core: '#F97316',   // Orange - health >= 0.3
      glow: '#FB923C',   // Bright orange
      ring: '#9A3412',   // Rust
    },
    critical: {
      core: '#EF4444',   // Red - health < 0.3
      glow: '#FCA5A5',   // Light red
      ring: '#7F1D1D',   // Dark red
    },
  },

  edgeColors: {
    base: '#4A5568',     // Muted gray-green
    highlight: '#68D391', // Bright green when active
    glow: '#48BB78',     // Medium green glow
    violation: '#C53030', // Dark red for violations
  },

  particleColors: {
    normal: '#9AE6B4',   // Light green (dependency flow)
    active: '#FEB2B2',   // Light red (violation particles)
  },

  atmosphere: {
    fog: {
      color: '#0A1612',
      near: 15,
      far: 60,
    },
    background: '#0A1612',  // Dark forest night
    ambientTint: '#1A3A2A', // Deep green tint
  },

  selectionColor: '#FFFFFF', // White selection ring
  hoverColor: '#4ADE80',     // Bright green hover

  labelColor: '#FFFFFF',
  labelOutlineColor: '#1A3A1A',
};

// =============================================================================
// Forest-Specific Utilities
// =============================================================================

/**
 * Get health tier from score.
 * Maps health_score (0-1) to forest tier.
 *
 * @param healthScore - Health score (0-1)
 */
export function getForestTier(healthScore: number): ForestTier {
  // Defensive: treat undefined/NaN as critical
  const safeScore = typeof healthScore === 'number' && !isNaN(healthScore) ? healthScore : 0;

  if (safeScore >= 0.9) return 'healthy';
  if (safeScore >= 0.7) return 'good';
  if (safeScore >= 0.5) return 'fair';
  if (safeScore >= 0.3) return 'poor';
  return 'critical';
}

/**
 * Calculate organic size based on module metrics.
 * Uses logarithmic scaling for natural distribution.
 *
 * @param linesOfCode - Lines of code in the module
 * @param healthScore - Health score (0-1)
 * @param density - Layout density
 */
export function calculateOrganicSize(
  linesOfCode: number,
  healthScore: number,
  density: 'compact' | 'comfortable' | 'spacious'
): number {
  const baseSize = density === 'compact' ? 0.15 : density === 'comfortable' ? 0.2 : 0.25;

  // Defensive: ensure valid numbers
  const safeLoc = typeof linesOfCode === 'number' && !isNaN(linesOfCode) ? linesOfCode : 10;
  const safeHealth = typeof healthScore === 'number' && !isNaN(healthScore) ? healthScore : 0.5;

  // Logarithmic scale for lines of code (prevents giant nodes)
  const locFactor = Math.log10(Math.max(safeLoc, 10)) / 5;

  // Health affects fullness (healthier = fuller)
  const healthFactor = 0.7 + safeHealth * 0.3;

  return baseSize * (1 + locFactor) * healthFactor;
}

/**
 * Generate growth ring geometry parameters.
 * Creates concentric rings like tree rings.
 *
 * @param baseSize - Base node size
 * @param ringCount - Number of rings (based on module size/age)
 */
export function generateGrowthRings(
  baseSize: number,
  ringCount: number
): Array<{ inner: number; outer: number; opacity: number }> {
  const rings: Array<{ inner: number; outer: number; opacity: number }> = [];
  for (let i = 0; i < ringCount; i++) {
    const innerRadius = baseSize * (1 + i * 0.15);
    const outerRadius = innerRadius + baseSize * 0.1;
    // Outer rings are more transparent
    const opacity = 0.4 - i * 0.08;
    rings.push({ inner: innerRadius, outer: outerRadius, opacity: Math.max(opacity, 0.1) });
  }
  return rings;
}

/**
 * Calculate ring count from lines of code.
 * More code = more rings (like tree rings showing age).
 */
export function calculateRingCount(linesOfCode: number): number {
  const safeLoc = typeof linesOfCode === 'number' && !isNaN(linesOfCode) ? linesOfCode : 10;
  return Math.min(Math.floor(Math.log10(safeLoc + 1)), 4);
}

export default FOREST_THEME;
