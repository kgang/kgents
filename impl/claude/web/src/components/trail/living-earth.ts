/**
 * Living Earth Design Tokens
 *
 * Crown Jewels Genesis Moodboard implementation.
 * "The aesthetic is the structure perceiving itself. Beauty is not revealed—it breathes."
 *
 * Visual Energy: Alive Workshop (organic, breathing, growing)
 * Target Emotion: Awe + Understanding + Playful Mastery + Creative Flow
 *
 * @see creative/crown-jewels-genesis-moodboard.md
 */

// =============================================================================
// "Bare Edge" Corner System
// Philosophy: The container is humble; the content glows.
// =============================================================================

export const CORNERS = {
  none: '0px', // Panels, canvas — invisible frame
  bare: '2px', // Cards, containers — just enough to not cut
  subtle: '3px', // Interactive surfaces — softened for touch
  soft: '4px', // Accent elements — use sparingly
  pill: '9999px', // Badges, tags — finite, precious
} as const;

// =============================================================================
// "Tight Frame" Spacing System
// Philosophy: Structure is compact; content has room to glow.
// =============================================================================

export const SPACING = {
  xs: 3, // Micro gaps, inline elements
  sm: 6, // Tight groupings
  md: 10, // Standard gaps between elements
  lg: 16, // Comfortable section spacing
  xl: 24, // Spacious area padding
} as const;

/** Get spacing as px string */
export function spacing(size: keyof typeof SPACING): string {
  return `${SPACING[size]}px`;
}

// =============================================================================
// Color Palette: "Living Earth"
// =============================================================================

export const LIVING_EARTH = {
  // PRIMARY (Warm Earth) - boosted text contrast
  soil: '#2D1B14',
  bark: '#4A3728',
  wood: '#6B4E3D',
  clay: '#B8A090', // Boosted from #8B6F5C for better contrast
  sand: '#D4C4B4', // Boosted from #AB9080 for readable body text

  // SECONDARY (Living Green)
  moss: '#1A2E1A',
  fern: '#2E4A2E',
  sage: '#4A6B4A',
  mint: '#6B8B6B',
  sprout: '#8BAB8B',

  // ACCENT (Ghibli Glow) - lantern brightened for headings
  lantern: '#FFF8F0', // Boosted from #F5E6D3 for crisp headings
  honey: '#E8C4A0',
  amber: '#D4A574',
  copper: '#C08552',
  bronze: '#8B5A2B',

  // SEMANTIC (Status)
  healthy: '#4A6B4A', // Sage
  growing: '#D4A574', // Amber
  warning: '#C08552', // Copper
  urgent: '#8B4513', // Sienna
  dormant: '#6B4E3D', // Wood
} as const;

// =============================================================================
// Trail Edge Colors (Living Earth Edition)
// =============================================================================

/**
 * Edge type colors mapped to Living Earth palette.
 * Replaces the tech-bright colors with organic tones.
 */
export const EDGE_COLORS = {
  // Structural edges - warm earth tones
  imports: LIVING_EARTH.copper, // Was blue - now warm copper
  contains: LIVING_EARTH.amber, // Was amber - stays amber
  calls: LIVING_EARTH.bronze, // Was pink - now bronze

  // Semantic edges - living greens
  tests: LIVING_EARTH.sage, // Was green - now organic sage
  implements: LIVING_EARTH.fern, // Was purple - now deep fern
  similar_to: LIVING_EARTH.mint, // Was cyan - now living mint
  type_of: LIVING_EARTH.sprout, // Was purple - now sprout green

  // Meta edges - honey glow
  semantic: LIVING_EARTH.honey, // Semantic similarity
  pattern: LIVING_EARTH.lantern, // Pattern matching

  // Default
  default: LIVING_EARTH.clay, // Neutral clay
} as const;

/**
 * Get edge color with Living Earth fallback.
 */
export function getEdgeColor(edgeType: string | null): string {
  if (!edgeType) return EDGE_COLORS.default;
  return (EDGE_COLORS as Record<string, string>)[edgeType] || EDGE_COLORS.default;
}

// =============================================================================
// Background Colors
// =============================================================================

export const BACKGROUNDS = {
  // Panel backgrounds - layered depth
  base: LIVING_EARTH.soil, // Deepest layer
  surface: LIVING_EARTH.bark, // Panel surface
  elevated: LIVING_EARTH.wood, // Elevated elements
  highlight: LIVING_EARTH.clay, // Highlighted areas

  // Canvas backgrounds
  canvas: '#1f1814', // Slightly warmer than pure dark
  canvasGrid: LIVING_EARTH.bark, // Grid lines

  // Interactive states
  hover: `${LIVING_EARTH.wood}40`, // 25% opacity
  selected: `${LIVING_EARTH.copper}30`, // Selection glow
} as const;

// =============================================================================
// Animation Philosophy: "Everything Breathes"
// =============================================================================

/**
 * Breathing animation parameters.
 * "All living elements have subtle scale/opacity pulse"
 *
 * Tuned 1.5x more subtle: slower period, gentler variation.
 */
export const BREATHING = {
  duration: 5, // 5s period (was 3.5s) - slower, more meditative
  amplitude: {
    scale: 0.012, // 1.2% scale variation (was 2%)
    opacity: 0.05, // 5% opacity variation (was 8%)
  },
  ease: 'easeInOut',
} as const;

/**
 * Growing animation parameters.
 * "New elements grow from seed to full size"
 */
export const GROWING = {
  duration: 0.4, // 300-500ms
  ease: [0.34, 1.56, 0.64, 1], // Bouncy overshoot
  initialScale: 0.4, // Start at 40% (seed)
} as const;

/**
 * Unfurling animation parameters.
 * "Panels unfurl like leaves, not slide mechanically"
 */
export const UNFURLING = {
  duration: 0.4, // 400ms
  ease: [0.4, 0, 0.2, 1], // Natural ease
  origin: 'top', // Unfurl from top
} as const;

/**
 * Flowing animation parameters.
 * "Data flows like water through vines"
 */
export const FLOWING = {
  particleSpeed: 45, // 30-60px/s
  trailLength: 30, // 20-40px
  particleSize: 4,
} as const;

// =============================================================================
// Framer Motion Variants
// =============================================================================

/**
 * Breathing animation variant for nodes.
 * Subtle, meditative pulse that suggests life without distraction.
 */
export const breathingVariant = {
  animate: {
    scale: [1, 1 + BREATHING.amplitude.scale, 1],
    opacity: [1, 1 - BREATHING.amplitude.opacity, 1],
  },
  transition: {
    duration: BREATHING.duration,
    repeat: Infinity,
    ease: BREATHING.ease,
  },
};

/**
 * Growing entrance animation variant.
 */
export const growingVariant = {
  initial: {
    scale: GROWING.initialScale,
    opacity: 0,
  },
  animate: {
    scale: 1,
    opacity: 1,
  },
  transition: {
    duration: GROWING.duration,
    ease: GROWING.ease,
  },
};

/**
 * Unfurling panel animation variant.
 */
export const unfurlingVariant = {
  initial: {
    scaleY: 0,
    opacity: 0,
    originY: 0,
  },
  animate: {
    scaleY: 1,
    opacity: 1,
  },
  exit: {
    scaleY: 0,
    opacity: 0,
  },
  transition: {
    duration: UNFURLING.duration,
    ease: UNFURLING.ease,
  },
};

// =============================================================================
// Glow Effects (tuned 40% subtler)
// =============================================================================

/**
 * Generate glow shadow for a given color.
 * Reduced 40% from original for subtler, more organic feel.
 */
export function glowShadow(
  color: string,
  intensity: 'subtle' | 'medium' | 'strong' = 'medium'
): string {
  // Blur and spread reduced 40%
  const blur = { subtle: 7, medium: 12, strong: 19 }[intensity];
  const spread = { subtle: 1, medium: 2, strong: 5 }[intensity];
  // Opacity reduced from 25% (40 hex) to 15% (26 hex)
  return `0 0 ${blur}px ${spread}px ${color}26`;
}

/**
 * Get glow color based on node state.
 * Reduced 40% for subtler presence.
 */
export function nodeGlow(isCurrent: boolean, isSelected: boolean): string {
  // Opacities reduced ~40%: 60→3A (38%→22%), 40→26 (25%→15%)
  if (isCurrent) return `${LIVING_EARTH.lantern}3A`;
  if (isSelected) return `${LIVING_EARTH.copper}26`;
  return 'transparent';
}

// =============================================================================
// Status Glyphs
// =============================================================================

/**
 * Status glyphs for instant recognition.
 * ZenPortal pattern: single-character, scannable at a glance.
 */
export const STATUS_GLYPHS = {
  // Trail states
  root: '◉', // Starting point
  visited: '●', // Visited step
  current: '◆', // Current position
  branch: '◇', // Branch point

  // Edge types (compact)
  imports: '→',
  contains: '⊃',
  tests: '✓',
  implements: '⊳',
  calls: '⤳',
  semantic: '≈',

  // Status
  healthy: '▪',
  growing: '↗',
  warning: '!',
  dormant: '○',
} as const;

// =============================================================================
// CSS Custom Properties (for Tailwind integration)
// =============================================================================

/**
 * Export as CSS custom property format.
 * Can be injected into :root for Tailwind/CSS usage.
 */
export const cssVars = {
  '--living-earth-soil': LIVING_EARTH.soil,
  '--living-earth-bark': LIVING_EARTH.bark,
  '--living-earth-wood': LIVING_EARTH.wood,
  '--living-earth-clay': LIVING_EARTH.clay,
  '--living-earth-sand': LIVING_EARTH.sand,
  '--living-earth-moss': LIVING_EARTH.moss,
  '--living-earth-fern': LIVING_EARTH.fern,
  '--living-earth-sage': LIVING_EARTH.sage,
  '--living-earth-mint': LIVING_EARTH.mint,
  '--living-earth-sprout': LIVING_EARTH.sprout,
  '--living-earth-lantern': LIVING_EARTH.lantern,
  '--living-earth-honey': LIVING_EARTH.honey,
  '--living-earth-amber': LIVING_EARTH.amber,
  '--living-earth-copper': LIVING_EARTH.copper,
  '--living-earth-bronze': LIVING_EARTH.bronze,
} as const;

export default LIVING_EARTH;
