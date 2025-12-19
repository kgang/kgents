/**
 * Generated types for AGENTESE path: world.morpheus
 * DO NOT EDIT - regenerate with: npm run sync-types
 */

/**
 * Response for world.morpheus.manifest.
 */
export interface WorldMorpheusManifestResponse {
  healthy: boolean;
  providers_healthy: number;
  providers_total: number;
  total_requests: number;
  total_errors: number;
  uptime_seconds: number;
  providers?: Record<string, unknown>[];
}

/**
 * Response for world.morpheus.providers.
 */
export interface WorldMorpheusProvidersResponse {
  filter: string;
  count: number;
  providers?: Record<string, unknown>[];
}

/**
 * Response for world.morpheus.metrics.
 */
export interface WorldMorpheusMetricsResponse {
  total_requests: number;
  total_errors: number;
  error_rate: number;
  uptime_seconds: number;
  providers_healthy: number;
  providers_total: number;
}

/**
 * Response for world.morpheus.health.
 */
export interface WorldMorpheusHealthResponse {
  status: unknown;
  providers?: Record<string, unknown>[];
}

/**
 * Response for world.morpheus.rate_limit.
 */
export interface WorldMorpheusRate_limitResponse {
  archetype: string;
  requests_remaining: number;
  reset_at?: string | null;
}

/**
 * Request for world.morpheus.complete.
 */
export interface WorldMorpheusCompleteRequest {
  model: string;
  messages: Record<string, string>[];
  temperature?: number;
  max_tokens?: number;
}

/**
 * Response for world.morpheus.complete.
 */
export interface WorldMorpheusCompleteResponse {
  response: string;
  model: string;
  provider: string;
  latency_ms: number;
  tokens: number;
}

/**
 * Request for world.morpheus.stream.
 */
export interface WorldMorpheusStreamRequest {
  model: string;
  messages: Record<string, string>[];
  temperature?: number;
  max_tokens?: number;
}

/**
 * Response metadata for world.morpheus.stream (actual data is SSE).
 */
export interface WorldMorpheusStreamResponse {
  type?: unknown;
  model?: string;
}

/**
 * Request for world.morpheus.route.
 */
export interface WorldMorpheusRouteRequest {
  model: string;
}

/**
 * Response for world.morpheus.route.
 */
export interface WorldMorpheusRouteResponse {
  model: string;
  provider: string;
  available: boolean;
  rate_limited?: boolean;
}
