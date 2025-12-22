/**
 * Generated types for AGENTESE path: self.foundry
 * DO NOT EDIT - regenerate with: npm run sync-types
 */

/**
 * Status manifest for the Foundry Crown Jewel.
 */
export interface SelfFoundryManifestResponse {
  cache_size: number;
  cache_max_size: number;
  total_forges: number;
  cache_hits: number;
  cache_hit_rate: number;
  recent_forges: Record<string, unknown>[];
  status: string;
}

/**
 * Request to forge a new ephemeral agent.

The Foundry will:
1. Classify intent (DETERMINISTIC, PROBABILISTIC, CHAOTIC)
2. Generate source if PROBABILISTIC
3. Validate stability via Chaosmonger
4. Select projection target
5. Compile to artifact
6. Cache for reuse
 */
export interface SelfFoundryForgeRequest {
  intent: string;
  context?: Record<string, unknown>;
  target_override?: string | null;
  entropy_budget?: number;
}

/**
 * Response from forge operation.

Contains the compiled artifact and metadata for inspection/promotion.
 */
export interface SelfFoundryForgeResponse {
  success: boolean;
  cache_key: string | null;
  target: string;
  artifact_type: string;
  artifact: string | Record<string, unknown>[] | null;
  reality: string;
  stability_score: number | null;
  agent_source: string | null;
  forced?: boolean;
  reason?: string | null;
  error?: string | null;
}

/**
 * Request to inspect a registered or cached agent.
 */
export interface SelfFoundryInspectRequest {
  agent_name: string;
  include_source?: boolean;
}

/**
 * Response from inspect operation.
 */
export interface SelfFoundryInspectResponse {
  found: boolean;
  agent_name: string | null;
  halo: Record<string, unknown>[] | null;
  polynomial: Record<string, unknown> | null;
  aspects: string[] | null;
  source: string | null;
  is_ephemeral?: boolean;
  cache_metrics?: Record<string, unknown> | null;
}

/**
 * Request for cache operations.
 */
export interface SelfFoundryCacheRequest {
  action: string;
  key?: string | null;
}

/**
 * Response from cache operations.
 */
export interface SelfFoundryCacheResponse {
  success: boolean;
  action: string;
  entries?: Record<string, unknown>[] | null;
  entry?: Record<string, unknown> | null;
  evicted_count?: number | null;
  error?: string | null;
}

/**
 * Request to promote an ephemeral agent to permanent.
 */
export interface SelfFoundryPromoteRequest {
  cache_key: string;
  agent_name: string;
  description?: string | null;
}

/**
 * Response from promote operation.
 */
export interface SelfFoundryPromoteResponse {
  success: boolean;
  agent_name: string | null;
  spec_path: string | null;
  error?: string | null;
}
