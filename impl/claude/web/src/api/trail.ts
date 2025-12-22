/**
 * Trail API - AGENTESE Universal Protocol
 *
 * "Bush's Memex realized: Force-directed graph showing exploration trails."
 *
 * Routes:
 *   self.trail.manifest - List saved trails
 *   self.trail.load - Load trail by ID
 *   self.trail.graph - Get trail as react-flow graph data
 *   self.trail.fork - Fork a trail
 *   self.trail.status - Storage health status
 *
 * @see spec/protocols/trail-protocol.md Section 8
 */

import { apiClient, AgenteseError } from './client';

// =============================================================================
// Types
// =============================================================================

/**
 * Evidence strength levels for trails.
 * From spec/protocols/trail-protocol.md Section 5.2
 */
export type EvidenceStrength = 'weak' | 'moderate' | 'strong' | 'definitive';

/**
 * A step in an exploration trail.
 */
export interface TrailStep {
  /** Index in the trail */
  index: number;
  /** Source path visited */
  source_path: string;
  /** Edge type followed (null for start) */
  edge: string | null;
  /** Destinations reached */
  destination_paths: string[];
  /** LLM reasoning for this step */
  reasoning: string | null;
  /** Loop detection status */
  loop_status: string;
  /** When this step was taken */
  created_at: string | null;
}

/**
 * A persisted exploration trail.
 */
export interface Trail {
  /** Unique trail ID */
  trail_id: string;
  /** Human-readable name */
  name: string;
  /** Steps in this trail */
  steps: TrailStep[];
  /** Step annotations */
  annotations: Record<number, string>;
  /** Trail version (for conflict detection) */
  version: number;
  /** When created */
  created_at: string | null;
  /** When last updated */
  updated_at: string | null;
  /** Parent trail if forked */
  forked_from_id: string | null;
  /** Extracted topics */
  topics: string[];
}

/**
 * Trail evidence analysis.
 */
export interface TrailEvidence {
  /** Number of steps taken */
  step_count: number;
  /** Number of unique paths visited */
  unique_paths: number;
  /** Number of unique edge types used */
  unique_edges: number;
  /** Overall evidence strength */
  evidence_strength: EvidenceStrength;
}

/**
 * Trail summary for listing.
 */
export interface TrailSummary {
  trail_id: string;
  name: string;
  step_count: number;
  version: number;
  created_at: string | null;
  updated_at: string | null;
  forked_from_id: string | null;
  topics: string[];
}

/**
 * Node in the react-flow graph.
 * Represents a context node visited in the trail.
 */
export interface TrailGraphNode {
  /** Unique node ID */
  id: string;
  /** Node type for react-flow */
  type: 'context' | 'branch';
  /** Position in the graph */
  position: { x: number; y: number };
  /** Node data */
  data: {
    /** Full path of this node */
    path: string;
    /** Holon name (last segment of path) */
    holon: string;
    /** Step index in the trail */
    step_index: number;
    /** Parent step index for branching (null = root) */
    parent_index: number | null;
    /** Edge type that led here */
    edge_type: string | null;
    /** LLM reasoning annotation */
    reasoning: string | null;
    /** Whether this is the current position */
    is_current: boolean;
  };
}

/**
 * Edge in the react-flow graph.
 * Represents navigation between context nodes.
 */
export interface TrailGraphEdge {
  /** Unique edge ID */
  id: string;
  /** Source node ID */
  source: string;
  /** Target node ID */
  target: string;
  /** Edge label (edge type) */
  label: string;
  /** Edge type for styling */
  type: 'structural' | 'semantic';
  /** Whether to animate this edge */
  animated: boolean;
  /** Style overrides */
  style?: {
    strokeDasharray?: string;
  };
}

/**
 * Trail storage status.
 */
export interface TrailStatus {
  total_trails: number;
  total_steps: number;
  active_trails: number;
  forked_trails: number;
  storage_backend: string;
}

/**
 * Response wrapper from AGENTESE gateway.
 */
interface AgenteseResponse<T> {
  path: string;
  aspect: string;
  result: T;
  error?: string;
}

/**
 * Response from self.trail.manifest
 */
interface TrailManifestResponse {
  summary: string;
  content: string;
  metadata: {
    trails: TrailSummary[];
    count: number;
    route?: string;
  };
}

/**
 * Response from self.trail.load
 */
interface TrailLoadResponse {
  summary: string;
  content: string;
  metadata: {
    trail?: Trail;
    evidence?: TrailEvidence;
    error?: string;
    trail_id?: string;
    route?: string;
  };
}

/**
 * Response from self.trail.graph
 */
interface TrailGraphResponse {
  summary: string;
  content: string;
  metadata: {
    nodes?: TrailGraphNode[];
    edges?: TrailGraphEdge[];
    trail?: Trail;
    evidence?: TrailEvidence;
    error?: string;
    trail_id?: string;
    route?: string;
  };
}

/**
 * Response from self.trail.fork
 */
interface TrailForkResponse {
  summary: string;
  content: string;
  metadata: {
    trail_id?: string;
    name?: string;
    step_count?: number;
    forked_from?: string;
    fork_point?: number;
    error?: string;
    route?: string;
  };
}

/**
 * Response from self.trail.status
 */
interface TrailStatusResponse {
  summary: string;
  content: string;
  metadata: {
    status?: TrailStatus;
    error?: string;
  };
}

/**
 * Response from self.trail.create
 */
interface TrailCreateResponse {
  summary: string;
  content: string;
  metadata: {
    trail_id?: string;
    name?: string;
    step_count?: number;
    route?: string;
    error?: string;
  };
}

/**
 * Input for creating a trail step.
 */
export interface CreateTrailStep {
  /** Path to the file/concept */
  path: string;
  /** Edge type from previous step */
  edge?: string;
  /** Reasoning for this step */
  reasoning?: string;
}

/**
 * Path validation result from world.repo.validate
 * Visual Trail Graph Session 2: Path Validation
 */
export interface PathValidation {
  /** Response status */
  status: 'success' | 'error';
  /** Whether the path exists in the repository */
  exists: boolean;
  /** Suggested similar paths if not found */
  suggestions: string[];
  /** Whether this path can be created (.py, .md, .ts, etc.) */
  can_create: boolean;
  /** The normalized path that was validated */
  path: string;
}

/**
 * Response from world.repo.validate
 */
interface PathValidationResponse {
  summary: string;
  content: string;
  metadata: PathValidation;
}

// =============================================================================
// API Functions
// =============================================================================

/**
 * Unwrap AGENTESE gateway response.
 */
function unwrapAgentese<T>(response: { data: AgenteseResponse<T> }): T {
  if (!response.data) {
    throw new AgenteseError('Trail response missing data envelope', 'self.trail', undefined);
  }
  if (response.data.error) {
    throw new AgenteseError(response.data.error, response.data.path, response.data.aspect);
  }
  return response.data.result;
}

/**
 * List saved trails.
 *
 * @param limit - Maximum trails to return (default: 50)
 */
export async function listTrails(limit = 50): Promise<TrailSummary[]> {
  const response = await apiClient.post<AgenteseResponse<TrailManifestResponse>>(
    '/agentese/self/trail/manifest',
    {
      limit,
      response_format: 'json',
    }
  );
  const result = unwrapAgentese(response);
  return result.metadata.trails || [];
}

/**
 * Get trail by ID.
 *
 * @param trailId - Trail ID to load
 */
export async function getTrail(trailId: string): Promise<Trail | null> {
  const response = await apiClient.post<AgenteseResponse<TrailLoadResponse>>(
    '/agentese/self/trail/load',
    {
      trail_id: trailId,
      response_format: 'json',
    }
  );
  const result = unwrapAgentese(response);
  return result.metadata.trail || null;
}

/**
 * Get trail with evidence analysis.
 *
 * @param trailId - Trail ID to load
 */
export async function getTrailWithEvidence(
  trailId: string
): Promise<{ trail: Trail; evidence: TrailEvidence } | null> {
  const response = await apiClient.post<AgenteseResponse<TrailLoadResponse>>(
    '/agentese/self/trail/load',
    {
      trail_id: trailId,
      response_format: 'json',
    }
  );
  const result = unwrapAgentese(response);
  if (!result.metadata.trail) return null;
  return {
    trail: result.metadata.trail,
    evidence: result.metadata.evidence || {
      step_count: 0,
      unique_paths: 0,
      unique_edges: 0,
      evidence_strength: 'weak',
    },
  };
}

/**
 * Get trail as react-flow graph data.
 *
 * @param trailId - Trail ID to convert to graph
 */
export async function getTrailGraph(
  trailId: string
): Promise<{
  nodes: TrailGraphNode[];
  edges: TrailGraphEdge[];
  trail: Trail;
  evidence: TrailEvidence;
} | null> {
  const response = await apiClient.post<AgenteseResponse<TrailGraphResponse>>(
    '/agentese/self/trail/graph',
    {
      trail_id: trailId,
      response_format: 'json',
    }
  );
  const result = unwrapAgentese(response);

  if (!result.metadata.nodes || !result.metadata.trail) {
    return null;
  }

  return {
    nodes: result.metadata.nodes,
    edges: result.metadata.edges || [],
    trail: result.metadata.trail,
    evidence: result.metadata.evidence || {
      step_count: 0,
      unique_paths: 0,
      unique_edges: 0,
      evidence_strength: 'weak',
    },
  };
}

/**
 * Fork a trail at a specific point.
 *
 * @param trailId - Trail to fork
 * @param name - Name for the forked trail
 * @param forkPoint - Step index to fork at (default: current end)
 */
export async function forkTrail(
  trailId: string,
  name: string,
  forkPoint?: number
): Promise<{ trail_id: string; name: string; step_count: number } | null> {
  const response = await apiClient.post<AgenteseResponse<TrailForkResponse>>(
    '/agentese/self/trail/fork',
    {
      trail_id: trailId,
      name,
      fork_point: forkPoint,
      response_format: 'json',
    }
  );
  const result = unwrapAgentese(response);

  if (!result.metadata.trail_id) {
    return null;
  }

  return {
    trail_id: result.metadata.trail_id,
    name: result.metadata.name || name,
    step_count: result.metadata.step_count || 0,
  };
}

/**
 * Get trail storage status.
 */
export async function getTrailStatus(): Promise<TrailStatus | null> {
  const response = await apiClient.post<AgenteseResponse<TrailStatusResponse>>(
    '/agentese/self/trail/status',
    {
      response_format: 'json',
    }
  );
  const result = unwrapAgentese(response);
  return result.metadata.status || null;
}

/**
 * Validate a path exists in the repository.
 * Visual Trail Graph Session 2: Path Validation
 *
 * Used by PathPicker to validate paths before adding to trail.
 *
 * @param path - Path to validate
 * @returns Validation result with exists, suggestions, can_create
 */
export async function validatePath(path: string): Promise<PathValidation> {
  const response = await apiClient.post<AgenteseResponse<PathValidationResponse>>(
    '/agentese/world/repo/validate',
    {
      path,
      response_format: 'json',
    }
  );
  const result = unwrapAgentese(response);
  return result.metadata;
}

/**
 * Create a new trail.
 *
 * Used by Portal.tsx to persist exploration sessions as witnessed trails.
 *
 * @param name - Human-readable trail name
 * @param steps - Steps in the trail (path, edge, reasoning)
 * @param topics - Optional topic tags
 * @returns Created trail ID and metadata
 */
export async function createTrail(
  name: string,
  steps: CreateTrailStep[],
  topics?: string[]
): Promise<{ trail_id: string; name: string; step_count: number }> {
  const response = await apiClient.post<AgenteseResponse<TrailCreateResponse>>(
    '/agentese/self/trail/create',
    {
      name,
      steps,
      topics: topics || [],
      response_format: 'json',
    }
  );
  const result = unwrapAgentese(response);

  if (!result.metadata.trail_id) {
    throw new AgenteseError(
      result.metadata.error || 'Failed to create trail',
      'self.trail',
      'create'
    );
  }

  return {
    trail_id: result.metadata.trail_id,
    name: result.metadata.name || name,
    step_count: result.metadata.step_count || steps.length,
  };
}

// =============================================================================
// Utility Functions
// =============================================================================

/**
 * Compute evidence strength from trail metrics.
 */
export function computeEvidenceStrength(
  stepCount: number,
  uniquePaths: number
): EvidenceStrength {
  if (stepCount >= 10 && uniquePaths >= 8) return 'definitive';
  if (stepCount >= 5 && uniquePaths >= 4) return 'strong';
  if (stepCount >= 3 && uniquePaths >= 2) return 'moderate';
  return 'weak';
}

/**
 * Get color for evidence strength badge.
 */
export function getEvidenceColor(strength: EvidenceStrength): string {
  switch (strength) {
    case 'definitive':
      return '#22c55e'; // green
    case 'strong':
      return '#3b82f6'; // blue
    case 'moderate':
      return '#f59e0b'; // amber
    case 'weak':
      return '#6b7280'; // gray
    default:
      return '#6b7280';
  }
}

/**
 * Format trail step for display.
 */
export function formatTrailStep(step: TrailStep): string {
  const edge = step.edge ? `──[${step.edge}]──>` : '(start)';
  return `${step.source_path} ${edge}`;
}

// =============================================================================
// Exports
// =============================================================================

export type {
  AgenteseResponse,
  TrailManifestResponse,
  TrailLoadResponse,
  TrailGraphResponse,
  TrailForkResponse,
  TrailStatusResponse,
  TrailCreateResponse,
};
