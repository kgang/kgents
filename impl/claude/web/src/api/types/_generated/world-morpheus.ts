/**
 * Generated types for AGENTESE path: world.morpheus
 * DO NOT EDIT - regenerate with: npm run sync-types
 */

/**
 * Response for world.morpheus.manifest.

Teaching:
    gotcha: These contract types are for AGENTESE OpenAPI schema generation.
            They are NOT the same as the internal types in types.py/persistence.py.
            (Evidence: node.py uses MorpheusManifestRendering, not this)
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

Teaching:
    gotcha: The `filter` field indicates which filter was applied based on
            observer archetype: "all" (admin), "enabled" (dev), "public" (guest).
            (Evidence: test_node.py::TestMorpheusNodeProviders)
 */
export interface WorldMorpheusProvidersResponse {
  filter: string;
  count: number;
  providers?: Record<string, unknown>[];
}

/**
 * Response for world.morpheus.metrics.

Teaching:
    gotcha: This aspect requires "developer" or "admin" archetype. Guests
            calling metrics get a Forbidden error.
            (Evidence: test_node.py::TestMorpheusNodeMetrics)
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

Teaching:
    gotcha: "healthy" means at least one provider is available—not that all are.
            "degraded" = some providers down, "unhealthy" = all providers down.
            (Evidence: test_node.py::TestMorpheusNodeHealth)
 */
export interface WorldMorpheusHealthResponse {
  status: unknown;
  providers?: Record<string, unknown>[];
}

/**
 * Response for world.morpheus.rate_limit.

Teaching:
    gotcha: `reset_at` is a timestamp hint, not a guarantee. Sliding window
            limits may clear earlier as old requests age out.
            (Evidence: gateway.py RateLimitState uses 60s sliding window)
 */
export interface WorldMorpheusRate_limitResponse {
  archetype: string;
  requests_remaining: number;
  reset_at?: string | null;
}

/**
 * Request for world.morpheus.complete.

Teaching:
    gotcha: `messages` is a list of dicts, not ChatMessage objects.
            The node converts these to ChatMessage internally.
            (Evidence: node.py::_handle_complete converts dicts)
 */
export interface WorldMorpheusCompleteRequest {
  model: string;
  messages: Record<string, string>[];
  temperature?: number;
  max_tokens?: number;
}

/**
 * Response for world.morpheus.complete.

Teaching:
    gotcha: `response` is the extracted text, not the full ChatResponse.
            Use world.morpheus.manifest to see detailed response metadata.
            (Evidence: node.py::_handle_complete extracts response_text)
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

Teaching:
    gotcha: Same structure as CompleteRequest, but the node sets stream=True
            internally and returns an async generator instead of a response.
            (Evidence: node.py::_handle_stream sets request.stream = True)
 */
export interface WorldMorpheusStreamRequest {
  model: string;
  messages: Record<string, string>[];
  temperature?: number;
  max_tokens?: number;
}

/**
 * Response metadata for world.morpheus.stream (actual data is SSE).

Teaching:
    gotcha: The actual content is delivered via SSE, not in this response.
            This is just metadata confirming the stream started.
            (Evidence: node.py::_handle_stream returns stream generator)
 */
export interface WorldMorpheusStreamResponse {
  type?: unknown;
  model?: string;
}

/**
 * Request for world.morpheus.route.

Teaching:
    gotcha: This is a query aspect, not a mutation. It tells you WHERE a model
            would route without actually making a request.
            (Evidence: test_node.py::TestMorpheusNodeRoute)
 */
export interface WorldMorpheusRouteRequest {
  model: string;
}

/**
 * Response for world.morpheus.route.

Teaching:
    gotcha: `available` is false if no provider matches the model prefix.
            Check `available` before making a complete/stream request.
            (Evidence: test_node.py::test_route_for_unknown_model)
 */
export interface WorldMorpheusRouteResponse {
  model: string;
  provider: string;
  available: boolean;
  rate_limited?: boolean;
}
