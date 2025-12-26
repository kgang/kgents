/**
 * Type definitions for Constitutional Dashboard
 *
 * Mirrors backend structures from:
 * - services/witness/mark.py → ConstitutionalAlignment
 * - services/witness/trust/constitutional_trust.py → ConstitutionalTrustResult
 */

export enum Principle {
  TASTEFUL = 'TASTEFUL',
  CURATED = 'CURATED',
  ETHICAL = 'ETHICAL',
  JOY_INDUCING = 'JOY_INDUCING',
  COMPOSABLE = 'COMPOSABLE',
  HETERARCHICAL = 'HETERARCHICAL',
  GENERATIVE = 'GENERATIVE',
}

export const PRINCIPLE_LABELS: Record<Principle, string> = {
  [Principle.TASTEFUL]: 'Tasteful',
  [Principle.CURATED]: 'Curated',
  [Principle.ETHICAL]: 'Ethical',
  [Principle.JOY_INDUCING]: 'Joy-Inducing',
  [Principle.COMPOSABLE]: 'Composable',
  [Principle.HETERARCHICAL]: 'Heterarchical',
  [Principle.GENERATIVE]: 'Generative',
};

export const PRINCIPLE_DESCRIPTIONS: Record<Principle, string> = {
  [Principle.TASTEFUL]: 'Clear, justified purpose',
  [Principle.CURATED]: 'Intentional selection',
  [Principle.ETHICAL]: 'Augments, never replaces',
  [Principle.JOY_INDUCING]: 'Delight in interaction',
  [Principle.COMPOSABLE]: 'Morphisms in a category',
  [Principle.HETERARCHICAL]: 'Flux, not hierarchy',
  [Principle.GENERATIVE]: 'Spec as compression',
};

/**
 * Constitutional alignment scores from a Mark evaluation.
 */
export interface ConstitutionalAlignment {
  /** Per-principle scores (0.0 to 1.0) */
  principle_scores: Record<string, number>;
  /** Weighted total score */
  weighted_total: number;
  /** Galois loss (if computed) */
  galois_loss: number | null;
  /** Tier: EMPIRICAL, NOETHERIAN, GALOIS */
  tier: string;
  /** Compliance threshold */
  threshold: number;
  /** Is compliant (weighted_total >= threshold) */
  is_compliant: boolean;
  /** Number of violations (principles below threshold) */
  violation_count: number;
  /** Dominant principle (highest score) */
  dominant_principle: string;
  /** Weakest principle (lowest score) */
  weakest_principle: string;
}

/**
 * Trust level computed from constitutional history.
 */
export type TrustLevel = 'L0' | 'L1' | 'L2' | 'L3';

export interface ConstitutionalTrustResult {
  /** Computed trust level */
  trust_level: TrustLevel;
  /** Numeric value for trust level */
  trust_level_value: number;
  /** Total marks analyzed */
  total_marks_analyzed: number;
  /** Average alignment score */
  average_alignment: number;
  /** Violation rate (0.0 to 1.0) */
  violation_rate: number;
  /** Trust capital earned */
  trust_capital: number;
  /** Per-principle averages */
  principle_averages: Record<string, number>;
  /** Top 3 principles */
  dominant_principles: string[];
  /** Reasoning for trust level */
  reasoning: string;
}

/**
 * Combined constitutional dashboard data.
 */
export interface ConstitutionalData {
  /** Latest alignment evaluation */
  alignment: ConstitutionalAlignment | null;
  /** Trust result from history */
  trust: ConstitutionalTrustResult | null;
  /** Agent ID */
  agent_id: string;
  /** Last updated timestamp */
  updated_at: string;
}
