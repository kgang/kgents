/**
 * Collapsing Functions Types
 *
 * Grounded in: spec/ui/axioms.md — A2 (Sloppification Axiom), A8 (Understandability)
 *
 * "Formal verification and tests are 'collapsing functions' that make
 * AI capabilities graspable."
 *
 * Four collapsing functions:
 * - TypeScript → Binary (compiles?)
 * - Tests → Binary (passes?)
 * - Constitution → Score (0-7)
 * - Galois → Loss (0-1)
 */

/**
 * Status for binary collapse functions (TypeScript, Tests).
 */
export type CollapseStatus = 'pass' | 'partial' | 'fail' | 'pending';

/**
 * Result from a binary collapse function.
 */
export interface CollapseResult {
  /** Overall status */
  status: CollapseStatus;

  /** Numeric score for partial results */
  score?: number;

  /** Total possible (for partial: 16/20 tests) */
  total?: number;

  /** Human-readable message */
  message?: string;

  /** When was this computed? (optional for pending) */
  timestamp?: string;
}

/**
 * Constitutional scoring result.
 */
export interface ConstitutionalCollapse {
  /** Overall score (0-7, one per principle) */
  score: number;

  /** Per-principle scores (flexible keys for backend compatibility) */
  principles: Record<string, number>;

  /** Dominant principle (highest score) */
  dominant?: string;

  /** Weakest principle (lowest score) */
  weakest?: string;

  /** Is this compliant (all principles ≥ 0.6)? */
  compliant?: boolean;
}

/**
 * Evidence tier from Galois loss.
 */
export type GaloisTier =
  | 'CATEGORICAL' // L < 0.10 — Axiomatic
  | 'EMPIRICAL' // L < 0.38 — Well-evidenced
  | 'AESTHETIC' // L < 0.45 — Taste-based
  | 'SOMATIC' // L < 0.65 — Felt sense
  | 'CHAOTIC'; // L ≥ 0.65 — Needs grounding

/**
 * Galois loss result.
 */
export interface GaloisCollapse {
  /** Loss value (0-1, lower is better) */
  loss: number;

  /** Evidence tier */
  tier: GaloisTier;

  /** Layer assignment (0-7, optional) */
  layer?: number;

  /** Is this grounded (tier < CHAOTIC)? */
  grounded?: boolean;
}

/**
 * Overall sloppification level.
 */
export type SlopLevel = 'low' | 'medium' | 'high';

/**
 * Complete collapse state for a K-Block.
 */
export interface CollapseState {
  /** TypeScript compilation result */
  typescript: CollapseResult;

  /** Test execution result */
  tests: CollapseResult;

  /** Constitutional scoring */
  constitution: ConstitutionalCollapse;

  /** Galois loss measurement */
  galois: GaloisCollapse;

  /** Overall sloppification assessment */
  overallSlop: SlopLevel;

  /** Evidence summary */
  evidence: string[];
}

/**
 * Colors for collapse status.
 */
export const COLLAPSE_COLORS: Record<CollapseStatus, string> = {
  pass: 'var(--collapse-pass)', // Muted green
  partial: 'var(--collapse-partial)', // Muted orange
  fail: 'var(--collapse-fail)', // Muted red
  pending: 'var(--collapse-pending)', // Gray
};

/**
 * Colors for Galois tiers.
 */
export const GALOIS_TIER_COLORS: Record<GaloisTier, string> = {
  CATEGORICAL: 'var(--collapse-pass)', // Grounded — green
  EMPIRICAL: 'var(--collapse-pass)', // Well-evidenced — green
  AESTHETIC: 'var(--collapse-partial)', // Taste-based — orange
  SOMATIC: 'var(--collapse-partial)', // Felt sense — orange
  CHAOTIC: 'var(--collapse-fail)', // Needs grounding — red
};

/**
 * Colors for slop levels.
 */
export const SLOP_COLORS: Record<SlopLevel, string> = {
  low: 'var(--collapse-pass)',
  medium: 'var(--collapse-partial)',
  high: 'var(--collapse-fail)',
};

/**
 * Icons for collapse status.
 */
export const COLLAPSE_ICONS: Record<CollapseStatus, string> = {
  pass: '✓',
  partial: '◐',
  fail: '✗',
  pending: '○',
};

/**
 * Compute slop level from constitutional and Galois results.
 */
export function computeSlopLevel(
  constitution: ConstitutionalCollapse,
  galois: GaloisCollapse
): SlopLevel {
  // High slop if: low constitutional OR high Galois loss
  const constitutionalScore = constitution.score / 7; // Normalize to 0-1
  if (constitutionalScore < 0.6 || galois.loss > 0.5) {
    return 'high';
  }
  if (constitutionalScore < 0.8 || galois.loss > 0.3) {
    return 'medium';
  }
  return 'low';
}

/**
 * Get Galois tier from loss value.
 */
export function getGaloisTier(loss: number): GaloisTier {
  if (loss < 0.1) return 'CATEGORICAL';
  if (loss < 0.38) return 'EMPIRICAL';
  if (loss < 0.45) return 'AESTHETIC';
  if (loss < 0.65) return 'SOMATIC';
  return 'CHAOTIC';
}

/**
 * Create pending collapse result.
 */
export function createPendingResult(): CollapseResult {
  return {
    status: 'pending',
    message: 'Awaiting computation',
    timestamp: new Date().toISOString(),
  };
}

/**
 * Create default collapse state.
 */
export function createDefaultCollapseState(): CollapseState {
  return {
    typescript: createPendingResult(),
    tests: createPendingResult(),
    constitution: {
      score: 0,
      principles: {},
    },
    galois: {
      loss: 1,
      tier: 'CHAOTIC',
    },
    overallSlop: 'high',
    evidence: [],
  };
}

/**
 * Format collapse result for display.
 */
export function formatCollapseResult(result: CollapseResult): string {
  if (result.status === 'pending') return 'Pending...';
  if (result.status === 'pass') return 'PASS';
  if (result.status === 'fail') return 'FAIL';
  if (result.status === 'partial' && result.score !== undefined && result.total !== undefined) {
    return `${result.score}/${result.total}`;
  }
  return result.message ?? result.status.toUpperCase();
}

/**
 * Format Galois loss for display.
 */
export function formatGaloisLoss(galois: GaloisCollapse): string {
  return `${galois.loss.toFixed(2)} (${galois.tier})`;
}

/**
 * Format constitutional score for display.
 */
export function formatConstitutionalScore(constitution: ConstitutionalCollapse): string {
  return `${constitution.score.toFixed(1)}/7`;
}
