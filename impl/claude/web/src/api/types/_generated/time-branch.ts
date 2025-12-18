/**
 * Generated types for AGENTESE path: time.branch
 * DO NOT EDIT - regenerate with: npm run sync-types
 */

/**
 * Branch operations manifest.
 */
export interface TimeBranchManifestResponse {
  branch_count: number;
  branch_ids: string[];
}

/**
 * Request to create speculative branch.
 */
export interface TimeBranchCreateRequest {
  from_trace_id: string;
  name?: string | null;
  hypothesis?: string;
}

/**
 * Response after creating branch.
 */
export interface TimeBranchCreateResponse {
  branch_id: string;
  name: string;
  from_trace_id: string;
  status: string;
}

/**
 * Request to explore a ghost alternative.
 */
export interface TimeBranchExploreRequest {
  ghost_id: string;
  branch_id?: string | null;
}

/**
 * Response from exploring ghost.
 */
export interface TimeBranchExploreResponse {
  ghost_id: string;
  branch_id: string | null;
  status: string;
  note: string;
}

/**
 * Request to compare two branches.
 */
export interface TimeBranchCompareRequest {
  a: string;
  b: string;
}

/**
 * Response comparing branches.
 */
export interface TimeBranchCompareResponse {
  a: string;
  b: string;
  a_info: Record<string, unknown> | null;
  b_info: Record<string, unknown> | null;
  comparison: Record<string, unknown>;
}
