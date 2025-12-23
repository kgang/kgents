/**
 * Living Earth Palette - Crown Jewels Genesis
 *
 * Ground-up color system from Crown Jewels Genesis Moodboard.
 * "Warm earth tones, gentle greens, motion with personality."
 * — Studio Ghibli UI Principles
 *
 * @see plans/crown-jewels-genesis.md - Phase 1: Foundation
 * @see docs/creative/crown-jewels-genesis-moodboard.md
 */

// =============================================================================
// PRIMARY: Warm Earth (Soil to Sand)
// =============================================================================

/**
 * Primary palette: Warm earth tones
 * From deepest soil to lightest sand
 */
export const EARTH = {
  soil: '#2D1B14', // Deepest background
  bark: '#4A3728', // Card surfaces
  wood: '#6B4E3D', // Elevated surfaces
  clay: '#8B6F5C', // Borders, muted elements
  sand: '#AB9080', // Secondary text
} as const;

export type EarthShade = keyof typeof EARTH;

// =============================================================================
// SECONDARY: Living Green (Moss to Sprout)
// =============================================================================

/**
 * Secondary palette: Living greens
 * From deep forest moss to fresh sprouts
 */
export const GREEN = {
  moss: '#1A2E1A', // Deep forest
  fern: '#2E4A2E', // Forest mid-tone
  sage: '#4A6B4A', // Nature accent
  mint: '#6B8B6B', // Available/ready state
  sprout: '#8BAB8B', // Fresh growth
} as const;

export type GreenShade = keyof typeof GREEN;

// =============================================================================
// ACCENT: Ghibli Glow (Lantern to Bronze)
// =============================================================================

/**
 * Accent palette: Ghibli glow
 * From soft lantern light to deep bronze
 */
export const GLOW = {
  lantern: '#F5E6D3', // Warm white, highlights
  honey: '#E8C4A0', // Soft glow
  amber: '#D4A574', // Primary accent (collaboration)
  copper: '#C08552', // Warm mid-accent
  bronze: '#8B5A2B', // Deep accent
} as const;

export type GlowShade = keyof typeof GLOW;

// =============================================================================
// DARK MODE VARIANTS
// =============================================================================

/**
 * Dark mode earth tones
 * Cooler, deeper earth for dark mode backgrounds
 */
export const DARK_EARTH = {
  soil: '#1A1210', // Deepest night
  bark: '#2D2118', // Dark card
  wood: '#3D2E25', // Dark elevated
  clay: '#5A483D', // Dark borders
  sand: '#7A6655', // Dark muted
} as const;

export type DarkEarthShade = keyof typeof DARK_EARTH;

/**
 * Dark mode greens
 * Deeper, more saturated greens for dark backgrounds
 */
export const DARK_GREEN = {
  moss: '#0F1A0F', // Deep night forest
  fern: '#1A2E1A', // Dark forest
  sage: '#2E4A2E', // Dark nature
  mint: '#4A6B4A', // Dark ready
  sprout: '#6B8B6B', // Dark growth
} as const;

export type DarkGreenShade = keyof typeof DARK_GREEN;

// =============================================================================
// JEWEL IDENTITY COLORS
// =============================================================================

/**
 * Each Crown Jewel has a primary identity color from Living Earth
 */
export const JEWEL_IDENTITY = {
  town: '#6B4E3D', // Wood - Grounded, community, reliable
  coalition: '#D4A574', // Amber - Collaboration glow
  forge: '#C08552', // Copper - Creative fire
  brain: '#2E4A2E', // Fern - Deep thought
  garden: '#4A6B4A', // Sage - Cultivation, growth
  domain: '#8B5A2B', // Bronze - Integration, grounding
} as const;

export type JewelName = keyof typeof JEWEL_IDENTITY;

// =============================================================================
// SEMANTIC MAPPINGS
// =============================================================================

/**
 * Semantic mappings from existing color tokens to Living Earth
 *
 * These map common design tokens to the Living Earth palette,
 * enabling gradual migration from existing color system.
 */
export const SEMANTIC_MAPPINGS = {
  // Primary UI colors
  primary: GREEN.sage, // Main brand color
  accent: GLOW.amber, // Accent/highlight color

  // State colors
  warning: GLOW.copper, // Warning states
  error: GLOW.bronze, // Error states
  success: GREEN.mint, // Success states
  info: GLOW.honey, // Informational states

  // Surface colors (light mode)
  surface: EARTH.sand, // Base surface
  surfaceElevated: EARTH.clay, // Elevated surface
  background: GLOW.lantern, // Page background

  // Surface colors (dark mode)
  surfaceDark: DARK_EARTH.wood, // Dark surface
  surfaceElevatedDark: DARK_EARTH.clay, // Dark elevated
  backgroundDark: DARK_EARTH.soil, // Dark background

  // Text colors (light mode)
  textPrimary: EARTH.soil, // Primary text
  textSecondary: EARTH.wood, // Secondary text
  textMuted: EARTH.clay, // Muted text

  // Text colors (dark mode)
  textPrimaryDark: GLOW.lantern, // Dark mode primary text
  textSecondaryDark: GLOW.honey, // Dark mode secondary text
  textMutedDark: EARTH.sand, // Dark mode muted text

  // Borders
  border: EARTH.clay, // Light border
  borderDark: DARK_EARTH.clay, // Dark border
} as const;

export type SemanticMapping = keyof typeof SEMANTIC_MAPPINGS;

// =============================================================================
// HELPER FUNCTIONS
// =============================================================================

/**
 * Get jewel identity color with fallback
 */
export function getJewelIdentityColor(jewel: string): string {
  const key = jewel.toLowerCase() as JewelName;
  return JEWEL_IDENTITY[key] ?? JEWEL_IDENTITY.town;
}

/**
 * Get earth color with fallback
 */
export function getEarthColor(shade: string): string {
  const key = shade.toLowerCase() as EarthShade;
  return EARTH[key] ?? EARTH.bark;
}

/**
 * Get green color with fallback
 */
export function getGreenColor(shade: string): string {
  const key = shade.toLowerCase() as GreenShade;
  return GREEN[key] ?? GREEN.sage;
}

/**
 * Get glow color with fallback
 */
export function getGlowColor(shade: string): string {
  const key = shade.toLowerCase() as GlowShade;
  return GLOW[key] ?? GLOW.amber;
}

/**
 * Get dark earth color with fallback
 */
export function getDarkEarthColor(shade: string): string {
  const key = shade.toLowerCase() as DarkEarthShade;
  return DARK_EARTH[key] ?? DARK_EARTH.bark;
}

/**
 * Get dark green color with fallback
 */
export function getDarkGreenColor(shade: string): string {
  const key = shade.toLowerCase() as DarkGreenShade;
  return DARK_GREEN[key] ?? DARK_GREEN.sage;
}

/**
 * Get semantic mapping with fallback
 */
export function getSemanticMapping(mapping: string): string {
  const key = mapping as SemanticMapping;
  return SEMANTIC_MAPPINGS[key] ?? SEMANTIC_MAPPINGS.primary;
}

/**
 * Get color based on mode (light/dark)
 */
export function getEarthColorByMode(shade: EarthShade, isDark: boolean): string {
  if (isDark) {
    return getDarkEarthColor(shade);
  }
  return EARTH[shade];
}

/**
 * Get green color based on mode (light/dark)
 */
export function getGreenColorByMode(shade: GreenShade, isDark: boolean): string {
  if (isDark) {
    return getDarkGreenColor(shade);
  }
  return GREEN[shade];
}

// =============================================================================
// FULL PALETTE EXPORT
// =============================================================================

/**
 * Complete Living Earth palette
 * All colors organized by family
 */
export const LIVING_EARTH_PALETTE = {
  earth: EARTH,
  green: GREEN,
  glow: GLOW,
  darkEarth: DARK_EARTH,
  darkGreen: DARK_GREEN,
  jewelIdentity: JEWEL_IDENTITY,
  semantic: SEMANTIC_MAPPINGS,
} as const;

/**
 * All Living Earth colors as a flat object
 * Useful for theme providers and Tailwind config
 */
export const LIVING_EARTH_FLAT = {
  // Earth tones
  'earth-soil': EARTH.soil,
  'earth-bark': EARTH.bark,
  'earth-wood': EARTH.wood,
  'earth-clay': EARTH.clay,
  'earth-sand': EARTH.sand,

  // Living greens
  'green-moss': GREEN.moss,
  'green-fern': GREEN.fern,
  'green-sage': GREEN.sage,
  'green-mint': GREEN.mint,
  'green-sprout': GREEN.sprout,

  // Ghibli glow
  'glow-lantern': GLOW.lantern,
  'glow-honey': GLOW.honey,
  'glow-amber': GLOW.amber,
  'glow-copper': GLOW.copper,
  'glow-bronze': GLOW.bronze,

  // Dark earth
  'dark-earth-soil': DARK_EARTH.soil,
  'dark-earth-bark': DARK_EARTH.bark,
  'dark-earth-wood': DARK_EARTH.wood,
  'dark-earth-clay': DARK_EARTH.clay,
  'dark-earth-sand': DARK_EARTH.sand,

  // Dark greens
  'dark-green-moss': DARK_GREEN.moss,
  'dark-green-fern': DARK_GREEN.fern,
  'dark-green-sage': DARK_GREEN.sage,
  'dark-green-mint': DARK_GREEN.mint,
  'dark-green-sprout': DARK_GREEN.sprout,

  // Jewel identities
  'jewel-town': JEWEL_IDENTITY.town,
  'jewel-coalition': JEWEL_IDENTITY.coalition,
  'jewel-forge': JEWEL_IDENTITY.forge,
  'jewel-brain': JEWEL_IDENTITY.brain,
  'jewel-garden': JEWEL_IDENTITY.garden,
  'jewel-domain': JEWEL_IDENTITY.domain,
} as const;
