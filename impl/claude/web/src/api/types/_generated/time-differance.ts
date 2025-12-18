/**
 * Generated types for AGENTESE path: time.differance
 * DO NOT EDIT - regenerate with: npm run sync-types
 */

/**
 * Differance Engine status manifest.
 */
export interface TimeDifferanceManifestResponse {
  trace_count: number;
  store_connected: boolean;
  monoid_available: boolean;
  route?: string;
}

/**
 * Request for ghost heritage DAG.
 */
export interface TimeDifferanceHeritageRequest {
  output_id: string;
  depth?: number;
}

/**
 * Complete ghost heritage DAG response.
 */
export interface TimeDifferanceHeritageResponse {
  output_id: string;
  root_id: string;
  chosen_path: string[];
  ghost_paths: string[][];
  node_count: number;
  edge_count: number;
  max_depth: number;
  nodes: Record<string, {
    id: string;
    type: unknown;
    operation: string;
    timestamp: string;
    depth: number;
    output?: unknown;
    reason?: string | null;
    explorable?: boolean;
    inputs?: string[];
  }>;
  edges: {
    source: string;
    target: string;
    type: unknown;
  }[];
}

/**
 * Request for 'why did this happen?' explanation.
 */
export interface TimeDifferanceWhyRequest {
  output_id: string;
  format?: unknown;
}

/**
 * Explanation of why an output exists.
 */
export interface TimeDifferanceWhyResponse {
  output_id: string;
  lineage_length: number;
  decisions_made: number;
  alternatives_considered: number;
  summary?: string | null;
  cli_output?: string | null;
  chosen_path?: {
    id: string;
    operation: string;
    inputs: string[];
    output: unknown;
    ghosts: Record<string, unknown>[];
  }[] | null;
  error?: string | null;
}

/**
 * Request for unexplored alternatives (ghosts).
 */
export interface TimeDifferanceGhostsRequest {
  explorable_only?: boolean;
  limit?: number;
}

/**
 * List of ghost alternatives.
 */
export interface TimeDifferanceGhostsResponse {
  ghosts: {
    operation: string;
    inputs: string[];
    reason_rejected: string;
    could_revisit: boolean;
  }[];
  count: number;
  explorable_only: boolean;
}

/**
 * Request to navigate to specific trace.
 */
export interface TimeDifferanceAtRequest {
  trace_id: string;
}

/**
 * Full trace details response.
 */
export interface TimeDifferanceAtResponse {
  trace_id: string;
  timestamp: string;
  operation: string;
  inputs: string[];
  output: unknown;
  context: string;
  alternatives: {
    operation: string;
    inputs: string[];
    reason: string;
    could_revisit: boolean;
  }[];
  parent_trace_id: string | null;
  positions_before: Record<string, string[]>;
  positions_after: Record<string, string[]>;
}

/**
 * Request to replay from trace point.
 */
export interface TimeDifferanceReplayRequest {
  from_id: string;
  include_ghosts?: boolean;
}

/**
 * Replay sequence response.
 */
export interface TimeDifferanceReplayResponse {
  from_id: string;
  steps: {
    trace_id: string;
    operation: string;
    inputs: string[];
    output: unknown;
    context: string;
    alternatives?: Record<string, unknown>[] | null;
  }[];
  step_count: number;
}
