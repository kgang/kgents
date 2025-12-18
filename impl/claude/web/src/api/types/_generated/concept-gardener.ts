/**
 * Generated types for AGENTESE path: concept.gardener
 * DO NOT EDIT - regenerate with: npm run sync-types
 */

/**
 * Gardener health status manifest.
 */
export interface ConceptGardenerManifestResponse {
  active_session_id: string | null;
  active_session_name: string | null;
  active_phase: unknown;
  total_sessions: number;
  polynomial_ascii: string;
}

/**
 * Active session status response.
 */
export interface ConceptGardenerSessionManifestResponse {
  status: string;
  session_id?: string | null;
  name?: string | null;
  phase?: unknown;
  phase_emoji?: string;
  phase_label?: string;
  phase_desc?: string;
  sense_count?: number;
  act_count?: number;
  reflect_count?: number;
  intent?: string | null;
  plan_path?: string | null;
  polynomial?: string;
  message?: string | null;
}

/**
 * Full polynomial state visualization.
 */
export interface ConceptGardenerSessionPolynomialResponse {
  current_phase: unknown;
  polynomial_ascii: string;
  diagram: string;
  valid_transitions?: string[];
  sense_count?: number;
  act_count?: number;
  reflect_count?: number;
}

/**
 * List of recent sessions.
 */
export interface ConceptGardenerSessionsManifestResponse {
  sessions?: unknown[];
  count?: number;
  active_id?: string | null;
}

/**
 * Proactive suggestions for what to do next.
 */
export interface ConceptGardenerProposeResponse {
  suggestion_count: number;
  suggestions?: unknown[];
}

/**
 * Request to start a new polynomial session.
 */
export interface ConceptGardenerSessionDefineRequest {
  name?: string | null;
  plan_path?: string | null;
  intent_description?: string | null;
  intent_priority?: string;
}

/**
 * Response after creating a new session.
 */
export interface ConceptGardenerSessionDefineResponse {
  status: string;
  session_id?: string | null;
  name?: string | null;
  phase?: unknown;
  polynomial?: string;
  message?: string;
}

/**
 * Request to advance to the next phase.
 */
export interface ConceptGardenerSessionAdvanceRequest {
  session_id?: string | null;
}

/**
 * Response after advancing phase.
 */
export interface ConceptGardenerSessionAdvanceResponse {
  status: string;
  phase?: unknown;
  phase_emoji?: string;
  phase_label?: string;
  phase_desc?: string;
  polynomial?: string;
  message?: string;
}

/**
 * Request to route natural language to AGENTESE path.
 */
export interface ConceptGardenerRouteRequest {
  input: string;
  use_llm?: boolean;
}

/**
 * Route result with resolved path.
 */
export interface ConceptGardenerRouteResponse {
  original_input: string;
  resolved_path: string;
  confidence: number;
  method: string;
  alternatives?: string[];
  explanation?: string;
}
