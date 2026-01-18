/**
 * Garden Lifecycle Types
 *
 * Grounded in: spec/ui/axioms.md — A4 (No-Shipping Axiom)
 * "There is no shipping. Only continuous iteration and evolution."
 *
 * The garden metaphor is literal. Every element has a lifecycle:
 * SEED → SPROUT → BLOOM → WITHER → COMPOST
 */

/**
 * Lifecycle stages for garden elements.
 * Maps to backend SpecLifecycle enum.
 */
export type LifecycleStage = 'seed' | 'sprout' | 'bloom' | 'wither' | 'compost';

/**
 * Complete lifecycle state for an element.
 */
export interface LifecycleState {
  /** Current lifecycle stage */
  stage: LifecycleStage;

  /** When was this element created? (optional) */
  planted?: string;

  /** When was this element last tended? (optional) */
  lastTended?: string;

  /** Last activity timestamp (alias for lastTended) */
  lastActivity?: string;

  /** Health score (0-1, optional) */
  health?: number;

  /** What depends on this element? (optional) */
  dependents?: string[];

  /** Days since last activity */
  daysSinceActivity: number;

  /** Evidence count (marks, tests, etc., optional) */
  evidenceCount?: number;
}

/**
 * Garden item for display.
 */
export interface GardenItem {
  /** Path or ID of the item */
  path: string;

  /** Display title */
  title: string;

  /** Current lifecycle state */
  lifecycle: LifecycleState;
}

/**
 * Aggregate garden state for dashboard.
 */
export interface GardenState {
  /** Count of items in each stage */
  seeds: number;
  sprouts: number;
  blooms: number;
  withering: number;

  /** Items composted today */
  compostedToday: number;

  /** Overall garden health (0-1) */
  health: number;

  /** Items needing attention (prioritized) */
  attention: GardenItem[];
}

/**
 * Colors for lifecycle stages.
 */
export const LIFECYCLE_COLORS: Record<LifecycleStage, string> = {
  seed: 'var(--seed)', // Blue-gray — potential
  sprout: 'var(--sprout)', // Green-gray — growing
  bloom: 'var(--bloom)', // Full intensity — mature
  wither: 'var(--wither)', // Fading — deprecated
  compost: 'var(--compost)', // Nearly gone — deleting
};

/**
 * Icons for lifecycle stages.
 */
export const LIFECYCLE_ICONS: Record<LifecycleStage, string> = {
  seed: '●', // Dot — potential
  sprout: '╱│╲', // Sprout shape — growing
  bloom: '✿', // Flower — mature
  wither: '╱', // Leaning — declining
  compost: '░', // Dissolving — deleting
};

/**
 * CSS classes for lifecycle stages.
 */
export const LIFECYCLE_CLASSES: Record<LifecycleStage, string> = {
  seed: 'lifecycle-seed',
  sprout: 'lifecycle-sprout',
  bloom: 'lifecycle-bloom',
  wither: 'lifecycle-wither',
  compost: 'lifecycle-compost',
};

/**
 * Descriptions for lifecycle stages.
 */
export const LIFECYCLE_DESCRIPTIONS: Record<LifecycleStage, string> = {
  seed: 'Idea captured, not started',
  sprout: 'Work in progress',
  bloom: 'Mature and reviewed',
  wither: 'Deprecated, needs attention',
  compost: 'Marked for deletion',
};

/**
 * Map backend lifecycle to frontend stage.
 */
export function mapBackendLifecycle(backendLifecycle: string): LifecycleStage {
  const mapping: Record<string, LifecycleStage> = {
    unwitnessed: 'seed',
    in_progress: 'sprout',
    witnessed: 'bloom',
    contested: 'wither',
    superseded: 'compost',
  };
  return mapping[backendLifecycle] ?? 'seed';
}

/**
 * Map backend health to numeric value.
 */
export function mapBackendHealth(backendHealth: string): number {
  const mapping: Record<string, number> = {
    blooming: 0.95,
    healthy: 0.75,
    wilting: 0.45,
    dead: 0.15,
    seedling: 0.5,
  };
  return mapping[backendHealth] ?? 0.5;
}

/**
 * Determine if item needs attention based on lifecycle.
 */
export function needsAttention(lifecycle: LifecycleState): boolean {
  // Withering items always need attention
  if (lifecycle.stage === 'wither') return true;

  // Seeds older than 30 days need attention
  if (lifecycle.stage === 'seed' && lifecycle.daysSinceActivity > 30) return true;

  // Sprouts stalled for more than 7 days need attention
  if (lifecycle.stage === 'sprout' && lifecycle.daysSinceActivity > 7) return true;

  // Low health items need attention
  if (lifecycle.health !== undefined && lifecycle.health < 0.3) return true;

  return false;
}

/**
 * Get attention priority (higher = more urgent).
 */
export function getAttentionPriority(lifecycle: LifecycleState): number {
  // Withering is most urgent
  if (lifecycle.stage === 'wither') return 100 + lifecycle.daysSinceActivity;

  // Stalled sprouts are next
  if (lifecycle.stage === 'sprout') return 50 + lifecycle.daysSinceActivity;

  // Old seeds are lowest priority
  if (lifecycle.stage === 'seed') return lifecycle.daysSinceActivity;

  // Low health items
  const health = lifecycle.health ?? 0.5;
  return (1 - health) * 40;
}

/**
 * Create default lifecycle state for new items.
 */
export function createSeedLifecycle(): LifecycleState {
  const now = new Date().toISOString();
  return {
    stage: 'seed',
    planted: now,
    lastTended: now,
    health: 0.5,
    dependents: [],
    daysSinceActivity: 0,
    evidenceCount: 0,
  };
}
