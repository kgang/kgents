/**
 * Crystal Theme - Brain Memory Visualization
 *
 * The crystal theme represents memories as gemstones.
 * Resolution → Clarity: vivid memories sparkle, fading ones become opaque.
 *
 * Color philosophy:
 *   - Cool spectrum (cyan → purple → indigo → gray)
 *   - Warm accent for "hot" frequently-accessed memories
 *   - Ethereal, translucent quality
 *
 * @see impl/claude/web/src/components/brain/OrganicCrystal.tsx
 * @see plans/3d-projection-consolidation.md
 */

import type { ThemePalette } from './types';

/**
 * Crystal tier names, ordered by memory freshness/resolution.
 */
export const CRYSTAL_TIERS = ['vivid', 'fresh', 'recent', 'fading', 'ancient', 'ghost', 'hot'] as const;
export type CrystalTier = (typeof CRYSTAL_TIERS)[number];

/**
 * The Crystal Theme Palette
 *
 * Used by Brain visualization for memory topology.
 */
export const CRYSTAL_THEME: ThemePalette = {
  name: 'crystal',
  description: 'Memories as living crystallizations of thought',

  nodeTiers: {
    vivid: {
      core: '#0891B2',   // Deep cyan - very fresh (resolution > 0.85)
      glow: '#22D3EE',   // Bright cyan
      ring: '#06B6D4',   // Mid cyan
    },
    fresh: {
      core: '#06B6D4',   // Cyan - fresh (resolution > 0.7)
      glow: '#67E8F9',   // Light cyan
      ring: '#22D3EE',   // Bright cyan
    },
    recent: {
      core: '#14B8A6',   // Teal - recent (resolution > 0.55)
      glow: '#5EEAD4',   // Light teal
      ring: '#2DD4BF',   // Mid teal
    },
    fading: {
      core: '#8B5CF6',   // Purple - fading (resolution > 0.4)
      glow: '#A78BFA',   // Bright purple
      ring: '#7C3AED',   // Deep purple
    },
    ancient: {
      core: '#6366F1',   // Indigo - ancient (resolution > 0.25)
      glow: '#818CF8',   // Bright indigo
      ring: '#4F46E5',   // Deep indigo
    },
    ghost: {
      core: '#475569',   // Slate - ghost (resolution <= 0.25)
      glow: '#94A3B8',   // Light slate
      ring: '#64748B',   // Mid slate
    },
    hot: {
      core: '#F59E0B',   // Amber - frequently accessed (warm accent)
      glow: '#FBBF24',   // Bright amber
      ring: '#D97706',   // Deep amber
    },
  },

  edgeColors: {
    base: '#334155',     // Slate - subtle base
    highlight: '#06B6D4', // Cyan when active
    glow: '#22D3EE',     // Bright cyan glow
    // Note: No violation state for crystal edges (Brain doesn't use violations)
  },

  particleColors: {
    normal: '#67E8F9',   // Light cyan (memory echoes)
    active: '#C4B5FD',   // Light purple (strong connections)
  },

  atmosphere: {
    fog: {
      color: '#0D1117',
      near: 10,
      far: 50,
    },
    background: '#0D1117',  // Dark space
    ambientTint: '#1E3A5F', // Deep blue tint
  },

  selectionColor: '#00FFFF',  // Cyan selection ring
  hoverColor: '#67E8F9',      // Light cyan hover

  labelColor: '#FFFFFF',
  labelOutlineColor: '#0D1117',
};

// =============================================================================
// Crystal-Specific Utilities
// =============================================================================

/**
 * Get resolution tier from score.
 * Expanded to 6 tiers for richer color variation (plus 'hot' for frequently accessed).
 *
 * @param resolution - Resolution score (0-1)
 * @param isHot - Whether the memory is frequently accessed
 */
export function getCrystalTier(resolution: number, isHot: boolean = false): CrystalTier {
  if (isHot) return 'hot';

  // Defensive: treat undefined/NaN as ghost
  const safeRes = typeof resolution === 'number' && !isNaN(resolution) ? resolution : 0;

  if (safeRes > 0.85) return 'vivid';
  if (safeRes > 0.7) return 'fresh';
  if (safeRes > 0.55) return 'recent';
  if (safeRes > 0.4) return 'fading';
  if (safeRes > 0.25) return 'ancient';
  return 'ghost';
}

/**
 * Calculate crystal size based on metrics.
 * Uses logarithmic scaling for natural distribution.
 */
export function calculateCrystalSize(
  accessCount: number,
  resolution: number,
  isHub: boolean,
  density: 'compact' | 'comfortable' | 'spacious'
): number {
  // Base sizes - smaller for more elegant appearance
  const baseSize = density === 'compact' ? 0.2 : density === 'comfortable' ? 0.25 : 0.3;

  // Defensive: ensure valid numbers (prevent NaN)
  const safeAccessCount = typeof accessCount === 'number' && !isNaN(accessCount) ? accessCount : 1;
  const safeResolution = typeof resolution === 'number' && !isNaN(resolution) ? resolution : 0.5;

  // Logarithmic scale for access count (subtle variation)
  const accessFactor = Math.log10(Math.max(safeAccessCount, 1) + 1) / 3;

  // Resolution affects fullness
  const resolutionFactor = 0.8 + safeResolution * 0.2;

  // Hub bonus - more prominent for navigation
  const hubBonus = isHub ? 1.5 : 1.0;

  return baseSize * (1 + accessFactor) * resolutionFactor * hubBonus;
}

export default CRYSTAL_THEME;
