/**
 * Generated types for AGENTESE path: self.memory.archaeology
 * DO NOT EDIT - regenerate with: npm run sync-types
 */

/**
 * Response for archaeology manifest.
 */
export interface SelfMemoryArchaeologyManifestResponse {
  total_commits: number;
  features_by_status: Record<string, number>;
}

/**
 * Request for mining git history.
 */
export interface SelfMemoryArchaeologyMineRequest {
  max_commits?: number;
}

/**
 * Response for mining git history.
 */
export interface SelfMemoryArchaeologyMineResponse {
  commits_parsed: number;
  total_commits: number;
  commit_types: Record<string, number>;
  authors: Record<string, number>;
}

/**
 * Request for extracting teachings.
 */
export interface SelfMemoryArchaeologyTeachingRequest {
  max_commits?: number;
  category?: string | null;
}

/**
 * Response for teaching extraction.
 */
export interface SelfMemoryArchaeologyTeachingResponse {
  total_teachings: number;
  by_category: Record<string, number>;
  teachings: Record<string, unknown>[];
}

/**
 * Request for crystallizing teachings to Witness.
 */
export interface SelfMemoryArchaeologyCrystallizeRequest {
  max_commits?: number;
  dry_run?: boolean;
}

/**
 * Response for crystallization.
 */
export interface SelfMemoryArchaeologyCrystallizeResponse {
  mode: string;
  total_teachings: number;
  marks_created: number;
  marks_skipped: number;
  errors: string[];
}

/**
 * Request for feature trajectories.
 */
export interface SelfMemoryArchaeologyTrajectoriesRequest {
  active_only?: boolean;
  max_commits?: number;
}

/**
 * Response for feature trajectories.
 */
export interface SelfMemoryArchaeologyTrajectoriesResponse {
  features: number;
  commits_analyzed: number;
  trajectories: Record<string, unknown>[];
}
