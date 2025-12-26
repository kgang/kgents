/**
 * Witness Primitive Types
 *
 * "Every state change is a morphism that returns (newState, witnessMark)"
 */

// =============================================================================
// WitnessMark Types
// =============================================================================

/**
 * A mark in the Witness ledger.
 */
export interface WitnessMark {
  /** Unique mark identifier */
  id: string;

  /** What was done */
  action: string;

  /** Why it was done */
  reasoning?: string;

  /** Which principles were honored */
  principles: string[];

  /** Who created the mark */
  author: 'kent' | 'claude' | 'system';

  /** When the mark was created */
  timestamp: string;

  /** Parent mark for causal lineage */
  parent_mark_id?: string;

  /** Whether this was automatically witnessed */
  automatic?: boolean;

  /** Additional metadata */
  metadata?: Record<string, unknown>;
}

// =============================================================================
// State Morphism Types
// =============================================================================

/**
 * A morphism that transforms state and produces a witness mark.
 *
 * The key insight: Every state change should be witnessed.
 * Instead of setState(newState), we use setState(morphism) where
 * morphism returns both the new state AND the witness mark.
 */
export type StateMorphism<S> = (state: S) => [S, Omit<WitnessMark, 'id' | 'timestamp' | 'author'>];

/**
 * A witnessed state setter.
 * Takes a morphism that returns both new state and witness mark.
 */
export type WitnessedStateSetter<S> = (morphism: StateMorphism<S>) => Promise<void>;

// =============================================================================
// Witness Configuration
// =============================================================================

/**
 * Configuration for automatic witnessing.
 */
export interface WitnessConfig {
  /** Base action name (will be prefixed with component name) */
  action: string;

  /** Default principles for this action */
  principles?: string[];

  /** Whether to witness automatically (fire-and-forget) */
  automatic?: boolean;

  /** Whether to enable witnessing (can be disabled) */
  enabled?: boolean;

  /** Custom mark metadata */
  metadata?: Record<string, unknown>;
}

// =============================================================================
// Display Variants
// =============================================================================

/**
 * Display variant for witness marks.
 */
export type WitnessMarkVariant = 'inline' | 'card' | 'minimal' | 'badge';

/**
 * Orientation for witness trail.
 */
export type WitnessTrailOrientation = 'horizontal' | 'vertical';

// =============================================================================
// Witness Trail Types
// =============================================================================

/**
 * A sequence of witness marks forming a causal chain.
 */
export interface WitnessTrail {
  /** Trail identifier */
  id: string;

  /** Marks in chronological order */
  marks: WitnessMark[];

  /** Root mark (if this is a lineage trail) */
  rootMarkId?: string;

  /** Whether the trail is complete or ongoing */
  complete: boolean;
}

// =============================================================================
// Principle Constants
// =============================================================================

/**
 * The seven kgents principles.
 */
export const PRINCIPLES = [
  'tasteful',
  'curated',
  'ethical',
  'joy_inducing',
  'composable',
  'heterarchical',
  'generative',
] as const;

export type Principle = typeof PRINCIPLES[number];

/**
 * Principle colors for visual distinction.
 */
export const PRINCIPLE_COLORS: Record<Principle, string> = {
  tasteful: '#8b5cf6',      // Purple
  curated: '#3b82f6',       // Blue
  ethical: '#10b981',       // Green
  joy_inducing: '#f59e0b',  // Amber
  composable: '#06b6d4',    // Cyan
  heterarchical: '#ec4899', // Pink
  generative: '#f97316',    // Orange
};

/**
 * Principle icons (emoji or unicode).
 */
export const PRINCIPLE_ICONS: Record<Principle, string> = {
  tasteful: '✨',
  curated: '🎯',
  ethical: '⚖️',
  joy_inducing: '🎉',
  composable: '🔗',
  heterarchical: '🌊',
  generative: '🌱',
};
