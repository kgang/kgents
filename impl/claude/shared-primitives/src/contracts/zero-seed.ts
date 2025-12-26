/**
 * Zero Seed API Contracts
 *
 * CANONICAL SOURCE OF TRUTH for Zero Seed epistemic graph and
 * personal governance API.
 *
 * @layer L4 (Specification)
 * @backend protocols/api/zero_seed.py
 * @see pilots/CONTRACT_COHERENCE.md
 * @see pilots/zero-seed-personal-governance-lab/PROTO_SPEC.md
 * @see plans/enlightened-synthesis/00-master-synthesis.md (A1-A5)
 */

// Re-export Galois types used by Zero Seed
export {
  type GaloisLossResponse,
  type ContradictionResponse,
  type FixedPointResponse,
  type EvidenceTier,
  type ContradictionType,
} from './galois';

// =============================================================================
// Core Data Models
// =============================================================================

/**
 * Components of Galois loss for a node
 */
export interface GaloisLossComponents {
  content_loss: number;
  proof_loss: number;
  edge_loss: number;
  metadata_loss: number;
  total: number;
}

/**
 * Loss information for a node
 */
export interface NodeLoss {
  node_id: string;
  loss: number;
  components: GaloisLossComponents;
  health_status: 'healthy' | 'warning' | 'critical';
}

/**
 * A node in the Zero Seed epistemic graph
 *
 * Represents a unit of knowledge at a specific epistemic layer (L1-L7).
 */
export interface ZeroNode {
  /** Unique identifier */
  id: string;
  /** AGENTESE path */
  path: string;
  /** Epistemic layer (1-7) */
  layer: EpistemicLayer;
  /** Node kind (axiom, value, goal, etc.) */
  kind: NodeKind;
  /** Human-readable title */
  title: string;
  /** Full content */
  content: string;
  /** Confidence in this node [0,1] */
  confidence: number;
  /** ISO timestamp of creation */
  created_at: string;
  /** Creator identifier */
  created_by: string;
  /** Tags for categorization */
  tags: string[];
  /** Parent node IDs (derivation chain) */
  lineage: string[];
  /** Whether node has a Toulmin proof */
  has_proof: boolean;
}

/**
 * Epistemic layer number (1-7)
 */
export type EpistemicLayer = 1 | 2 | 3 | 4 | 5 | 6 | 7;

/**
 * Node kinds corresponding to epistemic layers
 */
export type NodeKind =
  | 'axiom' // L1
  | 'value' // L2
  | 'goal' // L3
  | 'spec' // L4
  | 'execution' // L5
  | 'reflection' // L6
  | 'representation'; // L7

/**
 * Toulmin argument structure for proofs
 */
export interface ToulminProof {
  /** Grounding data/evidence */
  data: string;
  /** Connection between data and claim */
  warrant: string;
  /** The claim being made */
  claim: string;
  /** Support for the warrant */
  backing: string;
  /** Degree of certainty */
  qualifier: string;
  /** Potential counter-arguments */
  rebuttals: string[];
  /** Evidence tier */
  tier: string;
  /** Constitutional principles this supports */
  principles: string[];
}

/**
 * An edge in the epistemic graph
 */
export interface ZeroEdge {
  /** Unique identifier */
  id: string;
  /** Source node ID */
  source: string;
  /** Target node ID */
  target: string;
  /** Edge kind (derives, supports, contradicts, etc.) */
  kind: EdgeKind;
  /** Context explaining the relationship */
  context: string;
  /** Confidence in this edge [0,1] */
  confidence: number;
  /** ISO timestamp of creation */
  created_at: string;
  /** Witness mark ID (if edge was created from a mark) */
  mark_id?: string;
  /** Proof for this edge */
  proof?: ToulminProof;
  /** Evidence tier */
  evidence_tier?: string;
}

/**
 * Edge relationship types
 */
export type EdgeKind =
  | 'derives'
  | 'supports'
  | 'contradicts'
  | 'refines'
  | 'grounds'
  | 'witnesses';

/**
 * A ghost alternative (unchosen path preserved for inspection)
 */
export interface GhostAlternative {
  id: string;
  warrant: string;
  confidence: number;
  reasoning: string;
}

/**
 * Proof quality assessment
 */
export interface ProofQuality {
  node_id: string;
  proof: ToulminProof;
  coherence_score: number;
  warrant_strength: number;
  backing_coverage: number;
  rebuttal_count: number;
  quality_tier: 'strong' | 'moderate' | 'weak';
  ghost_alternatives: GhostAlternative[];
}

/**
 * A contradiction between nodes
 */
export interface Contradiction {
  id: string;
  node_a: string;
  node_b: string;
  edge_id: string;
  description: string;
  severity: 'low' | 'medium' | 'high';
  is_resolved: boolean;
  resolution_id?: string;
}

/**
 * Instability indicator in the graph
 */
export interface InstabilityIndicator {
  type:
    | 'orphan'
    | 'weak_proof'
    | 'edge_drift'
    | 'layer_skip'
    | 'contradiction';
  node_id: string;
  description: string;
  severity: number; // [0,1]
  suggested_action: string;
}

/**
 * Overall graph health metrics
 */
export interface GraphHealth {
  total_nodes: number;
  total_edges: number;
  by_layer: Record<number, number>;
  healthy_count: number;
  warning_count: number;
  critical_count: number;
  contradictions: Contradiction[];
  instability_indicators: InstabilityIndicator[];
  super_additive_loss_detected: boolean;
}

// =============================================================================
// Telescope (Navigation) Models
// =============================================================================

/**
 * Telescope state for graph navigation
 */
export interface TelescopeState {
  /** Focus distance [0,1] (0 = zoomed in, 1 = zoomed out) */
  focal_distance: number;
  /** Currently focused node ID */
  focal_point?: string;
  /** Show loss overlay */
  show_loss: boolean;
  /** Show gradient vectors */
  show_gradient: boolean;
  /** Loss threshold for visibility */
  loss_threshold: number;
  /** Visible layers */
  visible_layers: EpistemicLayer[];
  /** Preferred layer for navigation */
  preferred_layer: EpistemicLayer;
}

/**
 * Gradient vector for loss-based navigation
 */
export interface GradientVector {
  x: number;
  y: number;
  magnitude: number;
  target_node: string;
}

/**
 * Navigation suggestion from the telescope
 */
export interface NavigationSuggestion {
  target: string;
  action: 'focus' | 'follow_gradient' | 'investigate';
  value_score: number;
  reasoning: string;
}

/**
 * Policy arrow for value-based navigation
 */
export interface PolicyArrow {
  from: string;
  to: string;
  value: number;
  is_optimal: boolean;
}

// =============================================================================
// API Response Models
// =============================================================================

/**
 * GET /api/zero-seed/axioms response
 */
export interface AxiomExplorerResponse {
  /** L1 axiom nodes */
  axioms: ZeroNode[];
  /** L2 value nodes */
  values: ZeroNode[];
  /** Loss information for all nodes */
  losses: NodeLoss[];
  total_axiom_count: number;
  total_value_count: number;
  /** IDs of true fixed points (L < 0.05) */
  fixed_points: string[];
}

/**
 * GET /api/zero-seed/proofs response
 */
export interface ProofDashboardResponse {
  proofs: ProofQuality[];
  average_coherence: number;
  by_quality_tier: Record<string, number>;
  needs_improvement: string[];
}

/**
 * GET /api/zero-seed/health response
 */
export interface GraphHealthResponse {
  health: GraphHealth;
  timestamp: string;
  trend: 'improving' | 'stable' | 'degrading';
}

/**
 * GET /api/zero-seed/telescope response
 */
export interface TelescopeResponse {
  state: TelescopeState;
  gradients: Record<string, GradientVector>;
  suggestions: NavigationSuggestion[];
  visible_nodes: ZeroNode[];
  policy_arrows: PolicyArrow[];
}

/**
 * POST /api/zero-seed/navigate response
 */
export interface NavigateResponse {
  previous?: string;
  current: string;
  loss: number;
  gradient?: GradientVector;
}

/**
 * GET /api/zero-seed/nodes/{id} response
 */
export interface NodeDetailResponse {
  node: ZeroNode;
  loss: NodeLoss;
  proof?: ToulminProof;
  incoming_edges: ZeroEdge[];
  outgoing_edges: ZeroEdge[];
  witnessed_edges: ZeroEdge[];
}

/**
 * GET /api/zero-seed/layers/{layer} response
 */
export interface LayerNodesResponse {
  nodes: ZeroNode[];
  losses: NodeLoss[];
  count: number;
}

// =============================================================================
// Analysis Models (Four-Mode Operad)
// =============================================================================

/**
 * Analysis item from one mode
 */
export interface AnalysisItem {
  label: string;
  value: string;
  status: 'pass' | 'warning' | 'fail' | 'info';
}

/**
 * Analysis quadrant (one of the four modes)
 */
export interface AnalysisQuadrant {
  status: 'pass' | 'issues' | 'unknown';
  summary: string;
  items: AnalysisItem[];
}

/**
 * GET /api/zero-seed/nodes/{id}/analysis response
 */
export interface NodeAnalysisResponse {
  /** Node being analyzed */
  nodeId: string; // Note: aliased from node_id in Python
  /** Categorical analysis (composition laws) */
  categorical: AnalysisQuadrant;
  /** Epistemic analysis (grounding) */
  epistemic: AnalysisQuadrant;
  /** Dialectical analysis (tensions) */
  dialectical: AnalysisQuadrant;
  /** Generative analysis (compression) */
  generative: AnalysisQuadrant;
}

// =============================================================================
// Personal Governance Models
// =============================================================================

/**
 * A discovered axiom from decision patterns
 */
export interface DiscoveredAxiom {
  /** The axiom statement */
  content: string;
  /** Galois loss (< 0.05 for true axiom) */
  loss: number;
  /** Standard deviation across R-C iterations */
  stability: number;
  /** Number of iterations to reach stability */
  iterations: number;
  /** Confidence = 1 - loss */
  confidence: number;
  /** Source decisions that led to discovery */
  source_decisions: string[];
}

/**
 * POST /api/zero-seed/discover-axioms response
 */
export interface DiscoveryReport {
  /** Discovered axioms sorted by loss (best first) */
  discovered_axioms: DiscoveredAxiom[];
  /** Number of patterns analyzed */
  patterns_analyzed: number;
  /** Number of decisions processed */
  decisions_processed: number;
  /** Minimum loss found */
  min_loss: number;
  /** Maximum loss found */
  max_loss: number;
  /** Duration in milliseconds */
  duration_ms: number;
}

/**
 * POST /api/zero-seed/validate-axiom response
 */
export interface ValidationResult {
  /** True if loss < 0.05 */
  is_axiom: boolean;
  /** True if converged to fixed point */
  is_fixed_point: boolean;
  /** Final loss value */
  loss: number;
  /** Stability (std dev of loss across iterations) */
  stability: number;
  /** Iterations to converge */
  iterations: number;
  /** Loss at each iteration */
  losses: number[];
}

/**
 * An axiom in the personal constitution
 */
export interface ConstitutionalAxiom {
  /** Unique ID */
  id: string;
  /** The axiom content */
  content: string;
  /** Galois loss */
  loss: number;
  /** Stability measure */
  stability: number;
  /** Confidence = 1 - loss */
  confidence: number;
  /** Status in constitution */
  status: AxiomStatus;
  /** When added */
  added_at: string;
  /** When retired (if applicable) */
  retired_at?: string;
  /** Reason for retirement (if applicable) */
  retirement_reason?: string;
  /** IDs of conflicting axioms */
  conflicts: string[];
}

/**
 * Axiom status in the constitution
 */
export type AxiomStatus = 'active' | 'suspended' | 'retired' | 'conflicting';

/**
 * Personal constitution
 */
export interface Constitution {
  /** Unique ID */
  id: string;
  /** Name of the constitution */
  name: string;
  /** All axioms (keyed by ID) */
  axioms: Record<string, ConstitutionalAxiom>;
  /** Detected contradictions */
  contradictions: ConstitutionContradiction[];
  /** Evolution snapshots */
  snapshots: ConstitutionSnapshot[];
  /** Count of active axioms */
  active_count: number;
  /** Average loss of active axioms */
  average_loss: number;
  /** When created */
  created_at: string;
  /** When last updated */
  updated_at: string;
}

/**
 * A contradiction between two axioms
 */
export interface ConstitutionContradiction {
  /** First axiom ID */
  axiom_a_id: string;
  /** Second axiom ID */
  axiom_b_id: string;
  /** First axiom content (for display) */
  axiom_a_content: string;
  /** Second axiom content (for display) */
  axiom_b_content: string;
  /** Super-additive excess strength */
  strength: number;
  /** Contradiction type */
  type: 'none' | 'weak' | 'moderate' | 'strong';
  /** Synthesis hint (ghost alternative) */
  synthesis_hint?: string;
  /** When detected */
  detected_at: string;
  /** Whether resolved */
  resolved: boolean;
  /** Resolution description (if resolved) */
  resolution?: string;
}

/**
 * Evolution snapshot of the constitution
 */
export interface ConstitutionSnapshot {
  timestamp: string;
  axiom_count: number;
  active_count: number;
  average_loss: number;
  axiom_ids: string[];
}

/**
 * POST /api/zero-seed/detect-contradictions response
 */
export interface ContradictionReport {
  contradictions: ConstitutionContradiction[];
  total_axioms: number;
  pairs_checked: number;
}

// =============================================================================
// Request Models
// =============================================================================

/**
 * POST /api/zero-seed/navigate request
 */
export interface NavigateRequest {
  node_id: string;
  action: 'focus' | 'follow_gradient' | 'go_lowest_loss' | 'go_highest_loss';
}

/**
 * POST /api/zero-seed/edges/from-mark request
 */
export interface CreateWitnessedEdgeRequest {
  mark_id: string;
  source_node_id: string;
  target_node_id: string;
  context?: string;
}

/**
 * POST /api/zero-seed/nodes request
 */
export interface CreateNodeRequest {
  layer: EpistemicLayer;
  title: string;
  content: string;
  lineage?: string[];
  confidence?: number;
  tags?: string[];
  created_by?: string;
}

/**
 * PUT /api/zero-seed/nodes/{id} request
 */
export interface UpdateNodeRequest {
  title?: string;
  content?: string;
  confidence?: number;
  tags?: string[];
}

/**
 * POST /api/zero-seed/discover-axioms request
 */
export interface DiscoverAxiomsRequest {
  /** Mark IDs to analyze (optional, uses all decisions if empty) */
  mark_ids?: string[];
  /** Minimum pattern occurrences */
  min_occurrences?: number;
}

/**
 * POST /api/zero-seed/validate-axiom request
 */
export interface ValidateAxiomRequest {
  /** Content to validate */
  content: string;
  /** Threshold for axiom qualification (default: 0.05) */
  threshold?: number;
}

/**
 * POST /api/zero-seed/constitution/add request
 */
export interface AddAxiomRequest {
  /** Discovered axiom to add */
  axiom: DiscoveredAxiom;
  /** Check for contradictions (default: true) */
  check_contradictions?: boolean;
}

/**
 * POST /api/zero-seed/constitution/retire request
 */
export interface RetireAxiomRequest {
  /** Axiom ID to retire */
  axiom_id: string;
  /** Reason for retirement */
  reason: string;
}

// =============================================================================
// Contract Invariants
// =============================================================================

/**
 * Runtime invariant checks for ZeroNode.
 */
export const ZERO_NODE_INVARIANTS = {
  'has id': (n: ZeroNode) => typeof n.id === 'string' && n.id.length > 0,
  'layer in range': (n: ZeroNode) => n.layer >= 1 && n.layer <= 7,
  'has content': (n: ZeroNode) => typeof n.content === 'string',
  'confidence in range': (n: ZeroNode) => n.confidence >= 0 && n.confidence <= 1,
  'tags is array': (n: ZeroNode) => Array.isArray(n.tags),
  'lineage is array': (n: ZeroNode) => Array.isArray(n.lineage),
} as const;

/**
 * Runtime invariant checks for AxiomExplorerResponse.
 */
export const AXIOM_EXPLORER_INVARIANTS = {
  'axioms is array': (r: AxiomExplorerResponse) => Array.isArray(r.axioms),
  'values is array': (r: AxiomExplorerResponse) => Array.isArray(r.values),
  'losses is array': (r: AxiomExplorerResponse) => Array.isArray(r.losses),
  'counts are numbers': (r: AxiomExplorerResponse) =>
    typeof r.total_axiom_count === 'number' &&
    typeof r.total_value_count === 'number',
} as const;

/**
 * Runtime invariant checks for DiscoveredAxiom.
 */
export const DISCOVERED_AXIOM_INVARIANTS = {
  'has content': (a: DiscoveredAxiom) =>
    typeof a.content === 'string' && a.content.length > 0,
  'loss in range': (a: DiscoveredAxiom) => a.loss >= 0 && a.loss <= 1,
  'confidence in range': (a: DiscoveredAxiom) =>
    a.confidence >= 0 && a.confidence <= 1,
  'source_decisions is array': (a: DiscoveredAxiom) =>
    Array.isArray(a.source_decisions),
} as const;

/**
 * Runtime invariant checks for Constitution.
 */
export const CONSTITUTION_INVARIANTS = {
  'has id': (c: Constitution) => typeof c.id === 'string' && c.id.length > 0,
  'axioms is object': (c: Constitution) =>
    typeof c.axioms === 'object' && c.axioms !== null,
  'contradictions is array': (c: Constitution) =>
    Array.isArray(c.contradictions),
  'average_loss in range': (c: Constitution) =>
    c.average_loss >= 0 && c.average_loss <= 1,
} as const;

// =============================================================================
// Type Guards
// =============================================================================

/**
 * Type guard for ZeroNode.
 */
export function isZeroNode(data: unknown): data is ZeroNode {
  if (!data || typeof data !== 'object') return false;
  const n = data as Record<string, unknown>;
  return (
    typeof n.id === 'string' &&
    typeof n.path === 'string' &&
    typeof n.layer === 'number' &&
    n.layer >= 1 &&
    n.layer <= 7 &&
    typeof n.title === 'string' &&
    typeof n.content === 'string' &&
    typeof n.confidence === 'number' &&
    Array.isArray(n.tags)
  );
}

/**
 * Type guard for DiscoveredAxiom.
 */
export function isDiscoveredAxiom(data: unknown): data is DiscoveredAxiom {
  if (!data || typeof data !== 'object') return false;
  const a = data as Record<string, unknown>;
  return (
    typeof a.content === 'string' &&
    typeof a.loss === 'number' &&
    typeof a.stability === 'number' &&
    typeof a.iterations === 'number' &&
    typeof a.confidence === 'number'
  );
}

/**
 * Type guard for Constitution.
 */
export function isConstitution(data: unknown): data is Constitution {
  if (!data || typeof data !== 'object') return false;
  const c = data as Record<string, unknown>;
  return (
    typeof c.id === 'string' &&
    typeof c.name === 'string' &&
    typeof c.axioms === 'object' &&
    c.axioms !== null &&
    typeof c.active_count === 'number' &&
    typeof c.average_loss === 'number'
  );
}

// =============================================================================
// Normalizers (defensive coding)
// =============================================================================

/**
 * Normalize a potentially malformed DiscoveredAxiom.
 */
export function normalizeDiscoveredAxiom(data: unknown): DiscoveredAxiom {
  const a = data as Partial<DiscoveredAxiom>;
  return {
    content: typeof a.content === 'string' ? a.content : '',
    loss: typeof a.loss === 'number' ? Math.max(0, Math.min(1, a.loss)) : 1,
    stability:
      typeof a.stability === 'number'
        ? Math.max(0, Math.min(1, a.stability))
        : 1,
    iterations: typeof a.iterations === 'number' ? a.iterations : 0,
    confidence:
      typeof a.confidence === 'number'
        ? Math.max(0, Math.min(1, a.confidence))
        : 0,
    source_decisions: Array.isArray(a.source_decisions)
      ? a.source_decisions
      : [],
  };
}

/**
 * Normalize a DiscoveryReport response.
 */
export function normalizeDiscoveryReport(data: unknown): DiscoveryReport {
  const r = data as Partial<DiscoveryReport>;
  return {
    discovered_axioms: Array.isArray(r.discovered_axioms)
      ? r.discovered_axioms.map(normalizeDiscoveredAxiom)
      : [],
    patterns_analyzed:
      typeof r.patterns_analyzed === 'number' ? r.patterns_analyzed : 0,
    decisions_processed:
      typeof r.decisions_processed === 'number' ? r.decisions_processed : 0,
    min_loss: typeof r.min_loss === 'number' ? r.min_loss : 1,
    max_loss: typeof r.max_loss === 'number' ? r.max_loss : 1,
    duration_ms: typeof r.duration_ms === 'number' ? r.duration_ms : 0,
  };
}
