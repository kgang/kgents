/**
 * Zero Seed API Client
 *
 * Frontend client for the Zero Seed epistemic graph system.
 *
 * Philosophy:
 *   "Navigate toward stability. The gradient IS the guide. The loss IS the landscape."
 */

// =============================================================================
// Types
// =============================================================================

export type NodeId = string;
export type EdgeId = string;

// Layer types (L1-L7)
export type ZeroLayer = 1 | 2 | 3 | 4 | 5 | 6 | 7;

export const LAYER_NAMES: Record<ZeroLayer, string> = {
  1: 'Axioms',
  2: 'Values',
  3: 'Goals',
  4: 'Specs',
  5: 'Actions',
  6: 'Reflections',
  7: 'Representations',
};

export interface GaloisLossComponents {
  content_loss: number;
  proof_loss: number;
  edge_loss: number;
  metadata_loss: number;
  total: number;
}

export interface NodeLoss {
  node_id: NodeId;
  loss: number;
  components: GaloisLossComponents;
  health_status: 'healthy' | 'warning' | 'critical';
}

export interface ZeroNode {
  id: NodeId;
  path: string;
  layer: ZeroLayer;
  kind: string;
  title: string;
  content: string;
  confidence: number;
  created_at: string;
  created_by: string;
  tags: string[];
  lineage: NodeId[];
  has_proof: boolean;
}

export interface ZeroEdge {
  id: EdgeId;
  source: NodeId;
  target: NodeId;
  kind: string;
  context: string;
  confidence: number;
  created_at: string;
}

// Toulmin proof structure
export interface ToulminProof {
  data: string;
  warrant: string;
  claim: string;
  backing: string;
  qualifier: string;
  rebuttals: string[];
  tier: 'categorical' | 'empirical' | 'aesthetic' | 'somatic';
  principles: string[];
}

export interface ProofQuality {
  node_id: NodeId;
  proof: ToulminProof;
  coherence_score: number;
  warrant_strength: number;
  backing_coverage: number;
  rebuttal_count: number;
  quality_tier: 'strong' | 'moderate' | 'weak';
  ghost_alternatives: GhostAlternative[];
}

export interface GhostAlternative {
  id: string;
  warrant: string;
  confidence: number;
  reasoning: string;
}

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

export interface Contradiction {
  id: string;
  node_a: NodeId;
  node_b: NodeId;
  edge_id: EdgeId;
  description: string;
  severity: 'low' | 'medium' | 'high';
  is_resolved: boolean;
  resolution_id: NodeId | null;
}

export interface InstabilityIndicator {
  type: 'orphan' | 'weak_proof' | 'edge_drift' | 'layer_skip' | 'contradiction';
  node_id: NodeId;
  description: string;
  severity: number; // 0-1
  suggested_action: string;
}

// Telescope navigation types
export interface TelescopeState {
  focal_distance: number;
  focal_point: NodeId | null;
  show_loss: boolean;
  show_gradient: boolean;
  loss_threshold: number;
  visible_layers: ZeroLayer[];
  preferred_layer: ZeroLayer;
}

export interface GradientVector {
  x: number;
  y: number;
  magnitude: number;
  target_node: NodeId;
}

export interface NavigationSuggestion {
  target: NodeId;
  action: 'focus' | 'follow_gradient' | 'investigate';
  value_score: number;
  reasoning: string;
}

// API Response types
export interface AxiomExplorerResponse {
  axioms: ZeroNode[];
  values: ZeroNode[];
  losses: NodeLoss[];
  total_axiom_count: number;
  total_value_count: number;
  fixed_points: NodeId[];
}

export interface ProofDashboardResponse {
  proofs: ProofQuality[];
  average_coherence: number;
  by_quality_tier: Record<string, number>;
  needs_improvement: NodeId[];
}

export interface GraphHealthResponse {
  health: GraphHealth;
  timestamp: string;
  trend: 'improving' | 'stable' | 'degrading';
}

export interface TelescopeResponse {
  state: TelescopeState;
  gradients: Record<NodeId, GradientVector>;
  suggestions: NavigationSuggestion[];
  visible_nodes: ZeroNode[];
  policy_arrows: PolicyArrow[];
}

export interface PolicyArrow {
  from: NodeId;
  to: NodeId;
  value: number;
  is_optimal: boolean;
}

// =============================================================================
// API Client
// =============================================================================

const API_BASE = '/api/zero-seed';

async function fetchJson<T>(url: string, options?: RequestInit): Promise<T> {
  const response = await fetch(url, {
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
    ...options,
  });

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`API error: ${response.status} - ${error}`);
  }

  return response.json();
}

/**
 * Get axioms and values (L1-L2) with loss information.
 */
export async function getAxiomExplorer(): Promise<AxiomExplorerResponse> {
  return fetchJson<AxiomExplorerResponse>(`${API_BASE}/axioms`);
}

/**
 * Get proof quality dashboard (L3-L4).
 */
export async function getProofDashboard(options?: {
  layer?: ZeroLayer;
  min_coherence?: number;
}): Promise<ProofDashboardResponse> {
  const params = new URLSearchParams();
  if (options?.layer) params.set('layer', String(options.layer));
  if (options?.min_coherence) params.set('min_coherence', String(options.min_coherence));

  const queryString = params.toString();
  const url = queryString ? `${API_BASE}/proofs?${queryString}` : `${API_BASE}/proofs`;

  return fetchJson<ProofDashboardResponse>(url);
}

/**
 * Get graph health status (L5-L6).
 */
export async function getGraphHealth(): Promise<GraphHealthResponse> {
  return fetchJson<GraphHealthResponse>(`${API_BASE}/health`);
}

/**
 * Get telescope navigation state (L7).
 */
export async function getTelescopeState(options?: {
  focal_point?: NodeId;
  focal_distance?: number;
}): Promise<TelescopeResponse> {
  const params = new URLSearchParams();
  if (options?.focal_point) params.set('focal_point', options.focal_point);
  if (options?.focal_distance) params.set('focal_distance', String(options.focal_distance));

  const queryString = params.toString();
  const url = queryString ? `${API_BASE}/telescope?${queryString}` : `${API_BASE}/telescope`;

  return fetchJson<TelescopeResponse>(url);
}

/**
 * Navigate to a specific node.
 */
export async function navigateTo(
  nodeId: NodeId,
  action: 'focus' | 'follow_gradient' | 'go_lowest_loss' | 'go_highest_loss'
): Promise<{
  previous: NodeId | null;
  current: NodeId;
  loss: number;
  gradient: GradientVector | null;
}> {
  return fetchJson(`${API_BASE}/navigate`, {
    method: 'POST',
    body: JSON.stringify({ node_id: nodeId, action }),
  });
}

/**
 * Get a single node's details.
 */
export async function getNode(nodeId: NodeId): Promise<{
  node: ZeroNode;
  loss: NodeLoss;
  proof: ToulminProof | null;
  incoming_edges: ZeroEdge[];
  outgoing_edges: ZeroEdge[];
}> {
  return fetchJson(`${API_BASE}/nodes/${encodeURIComponent(nodeId)}`);
}

/**
 * Get all nodes for a layer.
 */
export async function getLayerNodes(layer: ZeroLayer): Promise<{
  nodes: ZeroNode[];
  losses: NodeLoss[];
  count: number;
}> {
  return fetchJson(`${API_BASE}/layers/${layer}`);
}
