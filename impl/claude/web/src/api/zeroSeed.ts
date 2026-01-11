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

/**
 * Normalize a node ID for API calls.
 *
 * Converts file paths back to K-Block IDs:
 * - spec/genesis/L0/entity.md -> genesis:L0:entity
 * - kblock/genesis:L0:entity -> genesis:L0:entity
 *
 * Passes through K-Block IDs unchanged:
 * - genesis:L0:entity -> genesis:L0:entity
 */
export function normalizeNodeId(nodeId: NodeId): NodeId {
  // Convert genesis file paths to K-Block IDs
  // Format: spec/genesis/L{layer}/{name}.md -> genesis:L{layer}:{name}
  const genesisMatch = nodeId.match(/^spec\/genesis\/L(\d)\/(\w+)\.md$/);
  if (genesisMatch) {
    const [, layer, name] = genesisMatch;
    return `genesis:L${layer}:${name}`;
  }

  // Strip kblock/ prefix if present
  if (nodeId.startsWith('kblock/')) {
    return nodeId.slice('kblock/'.length);
  }

  // Already a K-Block ID
  return nodeId;
}

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
  // Witness integration fields
  mark_id?: string | null;
  proof?: ToulminProof | null;
  evidence_tier?: 'categorical' | 'empirical' | 'aesthetic' | 'somatic' | null;
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

// =============================================================================
// Request Cache (prevents duplicate API calls for same node)
// =============================================================================

interface CacheEntry<T> {
  data: T;
  timestamp: number;
}

const nodeCache = new Map<string, CacheEntry<unknown>>();
const CACHE_TTL_MS = 5000; // 5 second TTL

function getCached<T>(key: string): T | null {
  const entry = nodeCache.get(key);
  if (!entry) return null;

  // Check if expired
  if (Date.now() - entry.timestamp > CACHE_TTL_MS) {
    nodeCache.delete(key);
    return null;
  }

  return entry.data as T;
}

function setCache<T>(key: string, data: T): void {
  nodeCache.set(key, { data, timestamp: Date.now() });

  // Limit cache size (LRU-ish: just clear old entries periodically)
  if (nodeCache.size > 100) {
    const now = Date.now();
    for (const [k, v] of nodeCache.entries()) {
      if (now - v.timestamp > CACHE_TTL_MS) {
        nodeCache.delete(k);
      }
    }
  }
}

// In-flight request deduplication
const inFlightRequests = new Map<string, Promise<unknown>>();

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
 * Cached for 5 seconds with in-flight deduplication.
 */
export async function getAxiomExplorer(): Promise<AxiomExplorerResponse> {
  const cacheKey = 'axioms';

  // Check cache first
  const cached = getCached<AxiomExplorerResponse>(cacheKey);
  if (cached) {
    return cached;
  }

  // Check if there's already an in-flight request
  const inFlight = inFlightRequests.get(cacheKey);
  if (inFlight) {
    return inFlight as Promise<AxiomExplorerResponse>;
  }

  // Make the request
  const promise = fetchJson<AxiomExplorerResponse>(`${API_BASE}/axioms`);
  inFlightRequests.set(cacheKey, promise);

  try {
    const result = await promise;
    setCache(cacheKey, result);
    return result;
  } finally {
    inFlightRequests.delete(cacheKey);
  }
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
 *
 * Accepts either K-Block IDs or file paths.
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
  const normalizedId = normalizeNodeId(nodeId);
  return fetchJson(`${API_BASE}/navigate`, {
    method: 'POST',
    body: JSON.stringify({ node_id: normalizedId, action }),
  });
}

/**
 * Get a single node's details.
 *
 * Accepts either K-Block IDs or file paths:
 * - genesis:L0:entity (K-Block ID)
 * - spec/genesis/L0/entity.md (file path, converted automatically)
 *
 * Features:
 * - Caches responses for 5 seconds to prevent duplicate requests
 * - Deduplicates in-flight requests (same node requested multiple times concurrently)
 */
export async function getNode(nodeId: NodeId): Promise<{
  node: ZeroNode;
  loss: NodeLoss;
  proof: ToulminProof | null;
  incoming_edges: ZeroEdge[];
  outgoing_edges: ZeroEdge[];
}> {
  type NodeResponse = {
    node: ZeroNode;
    loss: NodeLoss;
    proof: ToulminProof | null;
    incoming_edges: ZeroEdge[];
    outgoing_edges: ZeroEdge[];
  };

  const normalizedId = normalizeNodeId(nodeId);
  const cacheKey = `node:${normalizedId}`;

  // Check cache first
  const cached = getCached<NodeResponse>(cacheKey);
  if (cached) {
    return cached;
  }

  // Check if there's already an in-flight request for this node
  const inFlight = inFlightRequests.get(cacheKey);
  if (inFlight) {
    return inFlight as Promise<NodeResponse>;
  }

  // Make the request and cache it
  const promise = fetchJson<NodeResponse>(`${API_BASE}/nodes/${encodeURIComponent(normalizedId)}`);

  // Track in-flight request
  inFlightRequests.set(cacheKey, promise);

  try {
    const result = await promise;
    setCache(cacheKey, result);
    return result;
  } finally {
    // Remove from in-flight map
    inFlightRequests.delete(cacheKey);
  }
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

// =============================================================================
// Four-Mode Analysis
// =============================================================================

export interface AnalysisItem {
  label: string;
  value: string;
  status: 'pass' | 'warning' | 'fail' | 'info';
}

export interface AnalysisQuadrant {
  status: 'pass' | 'issues' | 'unknown';
  summary: string;
  items: AnalysisItem[];
}

export interface NodeAnalysisResponse {
  nodeId: string;
  categorical: AnalysisQuadrant;
  epistemic: AnalysisQuadrant;
  dialectical: AnalysisQuadrant;
  generative: AnalysisQuadrant;
}

/**
 * Get four-mode analysis for a Zero Seed node.
 *
 * Accepts either K-Block IDs or file paths.
 */
export async function getNodeAnalysis(nodeId: NodeId): Promise<NodeAnalysisResponse> {
  const normalizedId = normalizeNodeId(nodeId);
  return fetchJson(`${API_BASE}/nodes/${encodeURIComponent(normalizedId)}/analysis`);
}

// =============================================================================
// Witnessed Edge Operations
// =============================================================================

export interface CreateWitnessedEdgeRequest {
  mark_id: string;
  source_node_id: string;
  target_node_id: string;
  context?: string | null;
}

/**
 * Create a Zero Seed edge from a Witness mark.
 *
 * The edge inherits proof and confidence from the mark.
 */
export async function createWitnessedEdge(request: CreateWitnessedEdgeRequest): Promise<ZeroEdge> {
  return fetchJson<ZeroEdge>(`${API_BASE}/edges/from-mark`, {
    method: 'POST',
    body: JSON.stringify(request),
  });
}
