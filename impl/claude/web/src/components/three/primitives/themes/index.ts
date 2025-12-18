/**
 * Theme System for 3D Projections
 *
 * Exports all themes and theme utilities for the THREE_PROJECTION_OPERAD.
 *
 * @see plans/3d-projection-consolidation.md
 */

// Core types
export type {
  ThemePalette,
  NodeTierColors,
  EdgeColors,
  ParticleColors,
  AtmosphereConfig,
  TierCalculator,
  SizeCalculator,
  Density,
  LabelConfig,
} from './types';

export { LABEL_CONFIGS, validateThemeTiers, getTierColors } from './types';

// Crystal theme (Brain)
export { CRYSTAL_THEME, CRYSTAL_TIERS, getCrystalTier, calculateCrystalSize } from './crystal';
export type { CrystalTier } from './crystal';

// Forest theme (Gestalt)
export {
  FOREST_THEME,
  FOREST_TIERS,
  getForestTier,
  calculateOrganicSize,
  generateGrowthRings,
  calculateRingCount,
} from './forest';
export type { ForestTier } from './forest';

// Theme harmony (cross-jewel compatibility)
export {
  checkThemeHarmony,
  areThemesCompatible,
  getThemeBlendColor,
  areKnownCompatible,
  KNOWN_COMPATIBLE_PAIRS,
} from './harmony';
export type { HarmonyResult, HarmonyIssue } from './harmony';

// Theme registry for runtime theme selection
export const THEMES = {
  crystal: async () => (await import('./crystal')).CRYSTAL_THEME,
  forest: async () => (await import('./forest')).FOREST_THEME,
} as const;

export type ThemeName = keyof typeof THEMES;
