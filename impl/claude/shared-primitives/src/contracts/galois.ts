/**
 * Galois API Contracts
 *
 * CANONICAL SOURCE OF TRUTH for Galois loss computation API.
 * Implements the Galois Modularization principle: L(P) = d(P, C(R(P)))
 *
 * @layer L4 (Specification)
 * @backend protocols/api/galois.py
 * @see pilots/CONTRACT_COHERENCE.md
 * @see plans/enlightened-synthesis/00-master-synthesis.md (A3 GALOIS)
 */

// =============================================================================
// Request Types
// =============================================================================

/**
 * POST /api/galois/loss request
 */
export interface GaloisLossRequest {
  /** Content to analyze (3-100,000 chars) */
  content: string;
  /** Use cached results if available (default: true) */
  use_cache?: boolean;
}

/**
 * POST /api/galois/contradiction request
 */
export interface ContradictionRequest {
  /** First content (3-100,000 chars) */
  content_a: string;
  /** Second content (3-100,000 chars) */
  content_b: string;
  /** Tau tolerance for super-additivity detection (default: 0.1, range [0,1]) */
  tolerance?: number;
}

/**
 * POST /api/galois/fixed-point request
 */
export interface FixedPointRequest {
  /** Content to analyze (3-100,000 chars) */
  content: string;
  /** Maximum iterations to try (default: 7, range [1,20]) */
  max_iterations?: number;
  /** Loss variance threshold for stability (default: 0.05, range [0,1]) */
  stability_threshold?: number;
}

/**
 * POST /api/layer/assign request
 */
export interface LayerAssignRequest {
  /** Content to assign layer (3-100,000 chars) */
  content: string;
}

// =============================================================================
// Response Types
// =============================================================================

/**
 * POST /api/galois/loss response
 *
 * Returns the Galois loss: how much semantic information is lost
 * when content is restructured and reconstituted.
 */
export interface GaloisLossResponse {
  /** Galois loss value [0,1]. Lower = more axiomatic. */
  loss: number;
  /** Computation method: 'llm' or 'fallback' */
  method: string;
  /** Name of semantic distance metric used */
  metric_name: string;
  /** Whether result was from cache */
  cached: boolean;
  /** Evidence tier: 'categorical' (<0.1), 'empirical' (<0.3), 'aesthetic' (<0.6), 'somatic' (>=0.6) */
  evidence_tier: EvidenceTier;
}

/**
 * Evidence tier based on Galois loss thresholds
 */
export type EvidenceTier = 'categorical' | 'empirical' | 'aesthetic' | 'somatic';

/**
 * POST /api/galois/contradiction response
 *
 * Detects contradiction via super-additive loss:
 * L(A U B) > L(A) + L(B) + tau
 */
export interface ContradictionResponse {
  /** True if super-additive loss detected */
  is_contradiction: boolean;
  /** Super-additive excess (positive = contradiction) */
  strength: number;
  /** Galois loss of content A [0,1] */
  loss_a: number;
  /** Galois loss of content B [0,1] */
  loss_b: number;
  /** Galois loss of combined content [0,1] */
  loss_combined: number;
  /** Type: 'none' | 'weak' | 'moderate' | 'strong' */
  contradiction_type: ContradictionType;
  /** Ghost alternative suggestion for synthesis (if contradiction detected) */
  synthesis_hint?: string;
}

/**
 * Contradiction severity type
 */
export type ContradictionType = 'none' | 'weak' | 'moderate' | 'strong';

/**
 * POST /api/galois/fixed-point response
 *
 * Finds fixed point through R/C iteration.
 * A fixed point with loss < 0.01 is considered axiomatic.
 */
export interface FixedPointResponse {
  /** Whether content converges to fixed point */
  is_fixed_point: boolean;
  /** Whether it's an axiom (fixed point with loss < 0.01) */
  is_axiom: boolean;
  /** Final loss value [0,1] */
  final_loss: number;
  /** Iterations needed to converge (-1 if not converged) */
  iterations_to_converge: number;
  /** Loss at each iteration */
  loss_history: number[];
  /** Whether loss variance is below threshold */
  stability_achieved: boolean;
}

/**
 * POST /api/layer/assign response
 *
 * Assigns content to the layer (1-7) where it has minimal loss.
 */
export interface LayerAssignResponse {
  /** Assigned layer (1-7) */
  layer: number;
  /** Layer name: 'Axiom', 'Value', 'Goal', 'Spec', 'Execution', 'Reflection', 'Representation' */
  layer_name: LayerName;
  /** Loss at assigned layer [0,1] */
  loss: number;
  /** Assignment confidence [0,1] */
  confidence: number;
  /** Loss at each layer (1-7) */
  loss_by_layer: Record<number, number>;
  /** Insight about the layer assignment */
  insight: string;
  /** Detailed rationale */
  rationale: string;
}

/**
 * Epistemic layer names (L1-L7)
 */
export type LayerName =
  | 'Axiom'
  | 'Value'
  | 'Goal'
  | 'Spec'
  | 'Execution'
  | 'Reflection'
  | 'Representation';

// =============================================================================
// Constants (match Python backend)
// =============================================================================

/** Maximum content length (100KB) */
export const MAX_CONTENT_LENGTH = 100_000;

/** Minimum content length */
export const MIN_CONTENT_LENGTH = 3;

/** Axiom threshold (L < 0.05 = axiom) */
export const AXIOM_THRESHOLD = 0.05;

/** Fixed point threshold (variance < 0.01) */
export const FIXED_POINT_THRESHOLD = 0.01;

/** Default contradiction tolerance (tau) */
export const CONTRADICTION_TOLERANCE = 0.1;

// =============================================================================
// Contract Invariants (for test verification)
// =============================================================================

/**
 * Runtime invariant checks for GaloisLossResponse.
 */
export const GALOIS_LOSS_INVARIANTS = {
  'loss in range': (r: GaloisLossResponse) => r.loss >= 0 && r.loss <= 1,
  'has method': (r: GaloisLossResponse) =>
    typeof r.method === 'string' && r.method.length > 0,
  'has metric_name': (r: GaloisLossResponse) =>
    typeof r.metric_name === 'string',
  'has evidence_tier': (r: GaloisLossResponse) =>
    ['categorical', 'empirical', 'aesthetic', 'somatic'].includes(
      r.evidence_tier
    ),
} as const;

/**
 * Runtime invariant checks for ContradictionResponse.
 */
export const CONTRADICTION_INVARIANTS = {
  'losses in range': (r: ContradictionResponse) =>
    r.loss_a >= 0 &&
    r.loss_a <= 1 &&
    r.loss_b >= 0 &&
    r.loss_b <= 1 &&
    r.loss_combined >= 0 &&
    r.loss_combined <= 1,
  'has type': (r: ContradictionResponse) =>
    ['none', 'weak', 'moderate', 'strong'].includes(r.contradiction_type),
  'strength consistency': (r: ContradictionResponse) =>
    r.is_contradiction === r.strength > 0,
} as const;

/**
 * Runtime invariant checks for FixedPointResponse.
 */
export const FIXED_POINT_INVARIANTS = {
  'final_loss in range': (r: FixedPointResponse) =>
    r.final_loss >= 0 && r.final_loss <= 1,
  'loss_history is array': (r: FixedPointResponse) =>
    Array.isArray(r.loss_history),
  'axiom implies fixed point': (r: FixedPointResponse) =>
    !r.is_axiom || r.is_fixed_point,
} as const;

/**
 * Runtime invariant checks for LayerAssignResponse.
 */
export const LAYER_ASSIGN_INVARIANTS = {
  'layer in range': (r: LayerAssignResponse) => r.layer >= 1 && r.layer <= 7,
  'loss in range': (r: LayerAssignResponse) => r.loss >= 0 && r.loss <= 1,
  'confidence in range': (r: LayerAssignResponse) =>
    r.confidence >= 0 && r.confidence <= 1,
  'has layer_name': (r: LayerAssignResponse) =>
    typeof r.layer_name === 'string' && r.layer_name.length > 0,
} as const;

// =============================================================================
// Type Guards
// =============================================================================

/**
 * Type guard for GaloisLossResponse.
 */
export function isGaloisLossResponse(data: unknown): data is GaloisLossResponse {
  if (!data || typeof data !== 'object') return false;
  const r = data as Record<string, unknown>;
  return (
    typeof r.loss === 'number' &&
    typeof r.method === 'string' &&
    typeof r.metric_name === 'string' &&
    typeof r.cached === 'boolean' &&
    typeof r.evidence_tier === 'string'
  );
}

/**
 * Type guard for ContradictionResponse.
 */
export function isContradictionResponse(
  data: unknown
): data is ContradictionResponse {
  if (!data || typeof data !== 'object') return false;
  const r = data as Record<string, unknown>;
  return (
    typeof r.is_contradiction === 'boolean' &&
    typeof r.strength === 'number' &&
    typeof r.loss_a === 'number' &&
    typeof r.loss_b === 'number' &&
    typeof r.loss_combined === 'number' &&
    typeof r.contradiction_type === 'string'
  );
}

/**
 * Type guard for FixedPointResponse.
 */
export function isFixedPointResponse(data: unknown): data is FixedPointResponse {
  if (!data || typeof data !== 'object') return false;
  const r = data as Record<string, unknown>;
  return (
    typeof r.is_fixed_point === 'boolean' &&
    typeof r.is_axiom === 'boolean' &&
    typeof r.final_loss === 'number' &&
    typeof r.iterations_to_converge === 'number' &&
    Array.isArray(r.loss_history) &&
    typeof r.stability_achieved === 'boolean'
  );
}

/**
 * Type guard for LayerAssignResponse.
 */
export function isLayerAssignResponse(
  data: unknown
): data is LayerAssignResponse {
  if (!data || typeof data !== 'object') return false;
  const r = data as Record<string, unknown>;
  return (
    typeof r.layer === 'number' &&
    typeof r.layer_name === 'string' &&
    typeof r.loss === 'number' &&
    typeof r.confidence === 'number' &&
    typeof r.loss_by_layer === 'object' &&
    typeof r.insight === 'string' &&
    typeof r.rationale === 'string'
  );
}

// =============================================================================
// Normalizers (defensive coding)
// =============================================================================

/**
 * Normalize a potentially malformed GaloisLossResponse.
 */
export function normalizeGaloisLossResponse(
  data: unknown
): GaloisLossResponse {
  const r = data as Partial<GaloisLossResponse>;
  return {
    loss: typeof r.loss === 'number' ? Math.max(0, Math.min(1, r.loss)) : 0.5,
    method: typeof r.method === 'string' ? r.method : 'unknown',
    metric_name: typeof r.metric_name === 'string' ? r.metric_name : 'unknown',
    cached: typeof r.cached === 'boolean' ? r.cached : false,
    evidence_tier: isValidEvidenceTier(r.evidence_tier)
      ? r.evidence_tier
      : 'somatic',
  };
}

/**
 * Check if value is a valid EvidenceTier.
 */
function isValidEvidenceTier(tier: unknown): tier is EvidenceTier {
  return (
    typeof tier === 'string' &&
    ['categorical', 'empirical', 'aesthetic', 'somatic'].includes(tier)
  );
}
