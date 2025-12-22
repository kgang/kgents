/**
 * Umwelt Types - Observer Reality Shift
 *
 * "Umwelt" (German: "environment" / "surrounding world") is a concept from
 * biosemiotics coined by Jakob von Uexküll. Different observers perceive
 * the same world in fundamentally different ways.
 *
 * A tick perceives: butyric acid → warmth → tactile sensation → blood.
 * A human perceives: colors, sounds, abstract concepts, social relationships.
 * Same world. Different realities.
 *
 * This is the heart of AGENTESE: different observers don't just have different
 * *permissions*—they have different *perceptions*.
 *
 * @see plans/umwelt-visualization.md
 */

import type { Observer } from '../ObserverPicker';
// PathMetadata is used in UmweltContext.tsx for triggerTransition signature
export type { PathMetadata } from '../useAgenteseDiscovery';

// =============================================================================
// Core Types
// =============================================================================

/**
 * Information about an aspect's availability and requirements.
 */
export interface AspectInfo {
  /** The aspect name (e.g., 'manifest', 'create', 'admin') */
  aspect: string;
  /** The AGENTESE path this aspect belongs to */
  path: string;
  /** Capability required to access this aspect (if any) */
  requiredCapability: string | null;
  /** Whether this aspect has a typed contract */
  hasContract: boolean;
  /** Whether this is a streaming aspect */
  isStreaming: boolean;
}

/**
 * The result of computing what changed between two observer states.
 * This is the core data structure that drives all animations.
 */
export interface UmweltDiff {
  /** Aspects that are now visible (weren't before) */
  revealed: AspectInfo[];
  /** Aspects that are now hidden (were visible before) */
  hidden: AspectInfo[];
  /** Aspects that remain visible */
  unchanged: AspectInfo[];
  /** The observer transition */
  observer: {
    from: Observer;
    to: Observer;
  };
}

// =============================================================================
// Animation Configuration
// =============================================================================

/**
 * Motion tokens for umwelt transitions.
 * Inspired by Linear's motion language—snappy but intentional.
 *
 * Design principle: "Tasteful > feature-complete"
 * These values are deliberately subtle. The animation should feel
 * like a gentle acknowledgment, not a celebration.
 */
export const UMWELT_MOTION = {
  // Transition durations (ms) - snappy, almost imperceptible
  instant: 50, // Color shift
  quick: 120, // Ripple expand
  standard: 200, // Aspect fade (was 300)
  deliberate: 350, // Full cascade (was 500)

  // Easing curves (responsive, not bouncy)
  enter: [0.25, 0.1, 0.25, 1] as const, // Subtle ease-out
  exit: [0.4, 0, 0.6, 1] as const, // Gentle fade

  // Scale factors - very subtle, almost imperceptible
  revealScale: { from: 0.95, to: 1 }, // Gentle grow (was 0.85)
  hideScale: { from: 1, to: 0.97 }, // Gentle shrink (was 0.92)

  // Opacity levels
  ghostOpacity: 0.4, // Hidden but visible
  activeOpacity: 1,

  // Rapid switch threshold (ms) - skip intermediate animations
  rapidSwitchThreshold: 150,

  // Ripple intensity - lower = more subtle
  rippleOpacity: 0.15, // Max opacity for ripple (was implicit 0.25)
  rippleScale: 2, // Max scale for ripple (was 3)
} as const;

/**
 * Density-aware configuration for umwelt animations.
 * Following elastic-ui-patterns skill.
 */
export interface UmweltDensityConfig {
  /** Show the ripple effect */
  ripple: boolean;
  /** Stagger aspect animations */
  stagger: boolean;
  /** Delay between each aspect animation (ms) */
  staggerDelay: number;
  /** Toast message format */
  toast: 'minimal' | 'standard' | 'detailed';
}

export const UMWELT_DENSITY_CONFIG: Record<
  'compact' | 'comfortable' | 'spacious',
  UmweltDensityConfig
> = {
  compact: {
    ripple: false, // Skip ripple in compact mode for speed
    stagger: false,
    staggerDelay: 0,
    toast: 'minimal', // "+3 -2"
  },
  comfortable: {
    ripple: true,
    stagger: true,
    staggerDelay: 20, // 20ms between each aspect (was 30)
    toast: 'standard', // "3 aspects revealed, 2 faded"
  },
  spacious: {
    ripple: true,
    stagger: true,
    staggerDelay: 30, // 30ms - still snappy (was 50)
    toast: 'detailed', // "Revealed: manifest, invoke, admin. Hidden: govern, void."
  },
} as const;

// =============================================================================
// Observer Colors
// =============================================================================

/**
 * Observer archetype colors for the spectrum shift effect.
 * Each observer has a chromatic signature.
 */
export const OBSERVER_COLORS: Record<string, string> = {
  guest: '#9CA3AF', // Gray
  user: '#22D3EE', // Cyan
  developer: '#22C55E', // Green
  mayor: '#F59E0B', // Amber
  coalition: '#8B5CF6', // Violet
  void: '#EC4899', // Pink
} as const;

/**
 * Get color for an observer archetype with fallback.
 */
export function getObserverColor(archetype: string): string {
  return OBSERVER_COLORS[archetype] ?? OBSERVER_COLORS.guest;
}

// =============================================================================
// History/Trace Types
// =============================================================================

/**
 * A trace entry recording an observer switch in the exploration history.
 * Used by HistoryDrawer to show where the user has been.
 */
export interface UmweltTrace {
  /** Unique identifier for this trace entry */
  id: string;
  /** The observer we switched from */
  from: { archetype: string };
  /** The observer we switched to */
  to: { archetype: string };
  /** Summary of what changed */
  diff: {
    revealedCount: number;
    hiddenCount: number;
  };
  /** When this switch occurred */
  timestamp: number;
  /** The AGENTESE path that was active during the switch (optional) */
  activePath?: string;
}
