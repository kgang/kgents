/**
 * Galois API Client
 *
 * Client for Zero Seed Galois backend endpoints.
 * Provides access to loss computation, fixed point detection, and layer assignment.
 *
 * Philosophy:
 *   "The loss IS the layer. The fixed point IS the axiom.
 *    The contradiction IS the super-additive signal."
 */

const API_BASE = '/api';

// =============================================================================
// Types
// =============================================================================

/**
 * Evidence tier classification based on Galois loss.
 */
export type EvidenceTier = 'categorical' | 'empirical' | 'aesthetic' | 'somatic';

/**
 * Response from Galois loss computation.
 */
export interface GaloisLossResponse {
  loss: number;
  method: 'llm' | 'fallback';
  metric_name: string;
  cached: boolean;
  evidence_tier: EvidenceTier;
}

/**
 * Response from fixed point detection.
 */
export interface FixedPointResponse {
  is_fixed_point: boolean;
  is_axiom: boolean;
  final_loss: number;
  iterations_to_converge: number;
  loss_history: number[];
  stability_achieved: boolean;
}

/**
 * Response from layer assignment.
 */
export interface LayerAssignResponse {
  layer: number;
  layer_name: string;
  loss: number;
  confidence: number;
  loss_by_layer: Record<number, number>;
  insight: string;
  rationale: string;
}

/**
 * Response from contradiction detection.
 */
export interface ContradictionResponse {
  is_contradiction: boolean;
  strength: number;
  loss_a: number;
  loss_b: number;
  loss_combined: number;
  contradiction_type: 'none' | 'weak' | 'moderate' | 'strong';
  synthesis_hint: string | null;
}

/**
 * Layer definition for UI display.
 */
export interface Layer {
  number: number;
  name: string;
  description: string;
  lossRange: [number, number];
}

/**
 * The seven epistemic layers.
 */
export const LAYERS: Layer[] = [
  { number: 1, name: 'Axiom', description: 'Self-evident truths, fixed points', lossRange: [0.00, 0.05] },
  { number: 2, name: 'Value', description: 'Core beliefs and principles', lossRange: [0.05, 0.15] },
  { number: 3, name: 'Goal', description: 'Desired outcomes and objectives', lossRange: [0.15, 0.30] },
  { number: 4, name: 'Spec', description: 'Specific requirements and constraints', lossRange: [0.30, 0.45] },
  { number: 5, name: 'Execution', description: 'Concrete actions and implementations', lossRange: [0.45, 0.60] },
  { number: 6, name: 'Reflection', description: 'Observations and learnings', lossRange: [0.60, 0.75] },
  { number: 7, name: 'Representation', description: 'Surface expressions and artifacts', lossRange: [0.75, 1.00] },
];

// =============================================================================
// API Functions
// =============================================================================

/**
 * Compute Galois loss for content.
 *
 * The Galois loss measures how much semantic information is lost when content
 * is restructured and reconstituted: L(P) = d(P, C(R(P)))
 *
 * @param content - Content to analyze
 * @param useCache - Use cached results if available (default: true)
 */
export async function computeGaloisLoss(
  content: string,
  useCache = true
): Promise<GaloisLossResponse> {
  const response = await fetch(`${API_BASE}/galois/loss`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ content, use_cache: useCache }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(`Failed to compute Galois loss: ${error.detail || response.statusText}`);
  }

  return response.json();
}

/**
 * Detect fixed points in content.
 *
 * A fixed point is content that remains stable under restructure-reconstitute cycles.
 * Content with loss < 0.01 is considered axiomatic.
 *
 * @param content - Content to analyze for fixed point status
 * @param maxIterations - Maximum R/C iterations (default: 7)
 * @param stabilityThreshold - Variance threshold for stability (default: 0.05)
 */
export async function detectFixedPoint(
  content: string,
  maxIterations = 7,
  stabilityThreshold = 0.05
): Promise<FixedPointResponse> {
  const response = await fetch(`${API_BASE}/galois/fixed-point`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      content,
      max_iterations: maxIterations,
      stability_threshold: stabilityThreshold,
    }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(`Failed to detect fixed point: ${error.detail || response.statusText}`);
  }

  return response.json();
}

/**
 * Assign layer to content via Galois loss minimization.
 *
 * Assigns content to the layer (1-7) where it has minimal loss.
 * This DERIVES layer assignment rather than requiring manual choice.
 *
 * @param content - Content to assign layer
 */
export async function assignLayer(content: string): Promise<LayerAssignResponse> {
  const response = await fetch(`${API_BASE}/layer/assign`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ content }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(`Failed to assign layer: ${error.detail || response.statusText}`);
  }

  return response.json();
}

/**
 * Detect contradiction between two contents using super-additive loss.
 *
 * A contradiction exists when L(A U B) > L(A) + L(B) + tau.
 *
 * @param contentA - First content
 * @param contentB - Second content
 * @param tolerance - Tau tolerance (default: 0.1)
 */
export async function detectContradiction(
  contentA: string,
  contentB: string,
  tolerance = 0.1
): Promise<ContradictionResponse> {
  const response = await fetch(`${API_BASE}/galois/contradiction`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      content_a: contentA,
      content_b: contentB,
      tolerance,
    }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(`Failed to detect contradiction: ${error.detail || response.statusText}`);
  }

  return response.json();
}

// =============================================================================
// Helper Functions
// =============================================================================

/**
 * Get layer by number.
 */
export function getLayerByNumber(num: number): Layer | undefined {
  return LAYERS.find((l) => l.number === num);
}

/**
 * Get layer by loss value (using absolute bounds).
 */
export function getLayerByLoss(loss: number): Layer {
  for (const layer of LAYERS) {
    const [low, high] = layer.lossRange;
    if (loss >= low && loss < high) {
      return layer;
    }
  }
  // Default to representation for edge cases
  return LAYERS[6];
}

/**
 * Format loss as percentage string.
 */
export function formatLoss(loss: number): string {
  return `${(loss * 100).toFixed(1)}%`;
}

/**
 * Get color class for evidence tier.
 */
export function getEvidenceTierColor(tier: EvidenceTier): string {
  switch (tier) {
    case 'categorical':
      return 'text-sage';
    case 'empirical':
      return 'text-lantern';
    case 'aesthetic':
      return 'text-amber';
    case 'somatic':
      return 'text-clay';
    default:
      return 'text-sand';
  }
}

/**
 * Get background color class for layer.
 */
export function getLayerColor(layer: number): string {
  const colors = [
    'bg-emerald-500/20', // L1 Axiom
    'bg-teal-500/20',    // L2 Value
    'bg-cyan-500/20',    // L3 Goal
    'bg-sky-500/20',     // L4 Spec
    'bg-indigo-500/20',  // L5 Execution
    'bg-violet-500/20',  // L6 Reflection
    'bg-purple-500/20',  // L7 Representation
  ];
  return colors[Math.min(layer - 1, colors.length - 1)] || colors[colors.length - 1];
}

/**
 * Get border color class for layer.
 */
export function getLayerBorderColor(layer: number): string {
  const colors = [
    'border-emerald-500/40', // L1 Axiom
    'border-teal-500/40',    // L2 Value
    'border-cyan-500/40',    // L3 Goal
    'border-sky-500/40',     // L4 Spec
    'border-indigo-500/40',  // L5 Execution
    'border-violet-500/40',  // L6 Reflection
    'border-purple-500/40',  // L7 Representation
  ];
  return colors[Math.min(layer - 1, colors.length - 1)] || colors[colors.length - 1];
}
