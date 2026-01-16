/**
 * Personal Constitution Builder Types
 *
 * TypeScript types for the Axiom Discovery Pipeline and Personal Constitution.
 *
 * Key Insight:
 *   "Kent discovers his personal axioms. The system shows him:
 *    'You've made 147 decisions this month. Here are the 3 principles
 *     you never violated - your L0 axioms.' He didn't write them; he *discovered* them."
 *
 * @see services/zero_seed/axiom_discovery_pipeline.py
 * @see spec/protocols/zero-seed.md
 */

// =============================================================================
// Axiom Candidate Types
// =============================================================================

/**
 * A candidate axiom discovered from decision history.
 *
 * Candidates are recurring patterns in decisions that exhibit
 * low Galois loss (L < 0.05) and stability under R-C cycles.
 */
export interface AxiomCandidate {
  /** The axiom text (normalized) */
  content: string;

  /** Galois loss (< 0.05 for true axioms, < 0.20 for values, < 0.40 for goals) */
  loss: number;

  /** How stable over repeated R-C cycles (std dev, lower is better) */
  stability: number;

  /** Mark IDs supporting this axiom */
  evidence: string[];

  /** The recurring pattern that suggests this axiom */
  sourcePattern: string;

  /** Computed confidence: (1 - loss) * stability_factor */
  confidence: number;

  /** How often this pattern appears */
  frequency: number;

  /** Earliest decision with this pattern */
  firstSeen: string;

  /** Latest decision with this pattern */
  lastSeen: string;

  /** True if loss < 0.05 (axiom threshold) */
  isAxiom: boolean;

  /** Stability score (0-1, higher is better) */
  stabilityScore: number;
}

/**
 * Classification of axiom by Galois loss threshold.
 *
 * - L0 Axiom: L < 0.05 (near-fixed point, never violated)
 * - L1 Value: L < 0.20 (strong preference, rarely violated)
 * - L2 Goal: L < 0.40 (guiding principle, sometimes traded off)
 */
export type AxiomLayer = 'L0' | 'L1' | 'L2';

/**
 * Status of an axiom in the personal constitution.
 */
export type AxiomStatus = 'discovered' | 'accepted' | 'rejected' | 'edited';

/**
 * An axiom with its acceptance status and layer classification.
 */
export interface ConstitutionalAxiom extends AxiomCandidate {
  /** Unique ID for this axiom in the constitution */
  id: string;

  /** User-assigned status */
  status: AxiomStatus;

  /** Derived layer based on loss threshold */
  layer: AxiomLayer;

  /** User's edited version (if status === 'edited') */
  editedContent?: string;

  /** When the axiom was added to constitution */
  addedAt: string;

  /** Notes or reasoning for acceptance/rejection */
  notes?: string;
}

// =============================================================================
// Contradiction Types
// =============================================================================

/**
 * Severity of a contradiction between axioms.
 *
 * Based on super-additive loss strength:
 * - WEAK: strength < 0.1
 * - MODERATE: 0.1 <= strength < 0.3
 * - STRONG: 0.3 <= strength < 0.5
 * - IRRECONCILABLE: strength >= 0.5
 */
export type ContradictionSeverity = 'weak' | 'moderate' | 'strong' | 'irreconcilable';

/**
 * A detected contradiction between two axiom candidates.
 *
 * Contradiction exists when L(A U B) > L(A) + L(B) + tau (super-additive loss).
 */
export interface ContradictionPair {
  /** First axiom content */
  axiomA: string;

  /** Second axiom content */
  axiomB: string;

  /** Galois loss of A */
  lossA: number;

  /** Galois loss of B */
  lossB: number;

  /** Galois loss of A U B */
  lossCombined: number;

  /** Super-additive excess: L(A U B) - L(A) - L(B) - tau */
  strength: number;

  /** Classification based on strength */
  type: ContradictionSeverity;

  /** Potential resolution suggested by ghost alternatives */
  synthesisHint: string | null;
}

// =============================================================================
// Discovery Result Types
// =============================================================================

/**
 * Progress state during axiom discovery.
 */
export interface DiscoveryProgress {
  /** Current stage of the pipeline */
  stage: 'surfacing' | 'extracting' | 'computing' | 'detecting' | 'complete';

  /** Human-readable description of current activity */
  message: string;

  /** Progress percentage (0-100) */
  percent: number;

  /** Number of decisions analyzed so far */
  decisionsAnalyzed: number;

  /** Number of patterns found so far */
  patternsFound: number;
}

/**
 * Complete result of axiom discovery pipeline.
 */
export interface AxiomDiscoveryResult {
  /** All axiom candidates, sorted by loss (lowest first) */
  candidates: AxiomCandidate[];

  /** Total decisions analyzed */
  totalDecisionsAnalyzed: number;

  /** Time window in days */
  timeWindowDays: number;

  /** Detected contradictions between candidates */
  contradictionsDetected: ContradictionPair[];

  /** Number of recurring patterns found */
  patternsFound: number;

  /** Number of candidates qualifying as axioms (L < 0.05) */
  axiomsDiscovered: number;

  /** Pipeline duration in milliseconds */
  durationMs: number;

  /** User ID if filtering was applied */
  userId: string | null;

  /** Candidates that qualify as axioms */
  topAxioms: AxiomCandidate[];

  /** True if any contradictions were detected */
  hasContradictions: boolean;
}

// =============================================================================
// Personal Constitution Types
// =============================================================================

/**
 * The user's personal constitution - their accepted axioms organized by layer.
 */
export interface PersonalConstitution {
  /** L0 Axioms: L < 0.05 - never violated */
  axioms: ConstitutionalAxiom[];

  /** L1 Values: L < 0.20 - strong preferences */
  values: ConstitutionalAxiom[];

  /** L2 Goals: L < 0.40 - guiding principles */
  goals: ConstitutionalAxiom[];

  /** Detected contradictions between accepted axioms */
  contradictions: ContradictionPair[];

  /** When the constitution was last updated */
  lastUpdated: string;

  /** Total number of discoveries that led to this constitution */
  discoveryCount: number;

  /** Amendment history */
  amendments: Amendment[];
}

/**
 * An amendment to the constitution - tracks evolution over time.
 */
export interface Amendment {
  /** Unique amendment ID */
  id: string;

  /** Type of change */
  type: 'add' | 'remove' | 'edit' | 'reorder';

  /** Axiom ID affected */
  axiomId: string;

  /** Description of the change */
  description: string;

  /** Timestamp of the amendment */
  timestamp: string;

  /** Previous state (for undo) */
  previousState?: ConstitutionalAxiom;
}

// =============================================================================
// Export Dialog Types
// =============================================================================

/**
 * Export format options.
 */
export type ExportFormat = 'markdown' | 'json' | 'spec';

/**
 * Export options for the constitution.
 */
export interface ExportOptions {
  /** Format to export as */
  format: ExportFormat;

  /** Include evidence (mark IDs) */
  includeEvidence: boolean;

  /** Include loss/stability metrics */
  includeMetrics: boolean;

  /** Include amendment history */
  includeHistory: boolean;

  /** Include contradictions */
  includeContradictions: boolean;
}

// =============================================================================
// API Request/Response Types
// =============================================================================

/**
 * Request to discover axioms via AGENTESE.
 */
export interface DiscoverAxiomsRequest {
  /** Time window in days (default: 30) */
  days?: number;

  /** Maximum candidates to return (default: 5) */
  maxCandidates?: number;

  /** Minimum pattern occurrences (default: 5) */
  minPatternOccurrences?: number;
}

/**
 * Request to validate a potential axiom.
 */
export interface ValidateAxiomRequest {
  /** The content to validate */
  content: string;
}

/**
 * Response from axiom validation.
 */
export interface ValidateAxiomResponse {
  /** True if L < 0.05 */
  isAxiom: boolean;

  /** The computed loss */
  loss: number;

  /** The stability measure */
  stability: number;

  /** Full candidate details */
  candidate: AxiomCandidate;
}

// =============================================================================
// Helper Functions
// =============================================================================

/**
 * Determine the layer classification for an axiom based on its loss.
 */
export function getAxiomLayer(loss: number): AxiomLayer {
  if (loss < 0.05) return 'L0';
  if (loss < 0.2) return 'L1';
  return 'L2';
}

/**
 * Get a human-readable label for an axiom layer.
 */
export function getLayerLabel(layer: AxiomLayer): string {
  switch (layer) {
    case 'L0':
      return 'Axiom';
    case 'L1':
      return 'Value';
    case 'L2':
      return 'Goal';
  }
}

/**
 * Get a description for an axiom layer.
 */
export function getLayerDescription(layer: AxiomLayer): string {
  switch (layer) {
    case 'L0':
      return 'Fixed point - you never violate this';
    case 'L1':
      return 'Strong value - you rarely trade this off';
    case 'L2':
      return 'Guiding goal - you sometimes adjust this';
  }
}

/**
 * Get the severity classification for a contradiction.
 */
export function getContradictionSeverity(strength: number): ContradictionSeverity {
  if (strength >= 0.5) return 'irreconcilable';
  if (strength >= 0.3) return 'strong';
  if (strength >= 0.1) return 'moderate';
  return 'weak';
}

/**
 * Get a human-readable label for contradiction severity.
 */
export function getSeverityLabel(severity: ContradictionSeverity): string {
  switch (severity) {
    case 'weak':
      return 'Weak Tension';
    case 'moderate':
      return 'Moderate Conflict';
    case 'strong':
      return 'Strong Contradiction';
    case 'irreconcilable':
      return 'Irreconcilable';
  }
}

/**
 * Generate a unique ID for a constitutional axiom.
 */
export function generateAxiomId(): string {
  return `axiom_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
}

/**
 * Convert a discovered candidate to a constitutional axiom.
 */
export function candidateToConstitutional(
  candidate: AxiomCandidate,
  status: AxiomStatus = 'discovered'
): ConstitutionalAxiom {
  return {
    ...candidate,
    id: generateAxiomId(),
    status,
    layer: getAxiomLayer(candidate.loss),
    addedAt: new Date().toISOString(),
  };
}
