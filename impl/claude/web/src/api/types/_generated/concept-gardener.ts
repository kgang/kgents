/**
 * Generated types for AGENTESE path: concept.gardener
 * DO NOT EDIT - regenerate with: npm run sync-types
 *
 * The 7th Crown Jewel - Development session orchestrator.
 * Implements SENSE -> ACT -> REFLECT polynomial state machine.
 */

/**
 * Gardener phase type (polynomial states).
 */
export type GardenerPhase = 'SENSE' | 'ACT' | 'REFLECT';

/**
 * Gardener health status manifest response.
 */
export interface ConceptGardenerManifestResponse {
  active_session_id: string | null;
  active_session_name: string | null;
  active_phase: GardenerPhase | null;
  total_sessions: number;
  polynomial_ascii: string;
}

/**
 * Active session status response.
 */
export interface ConceptGardenerSessionManifestResponse {
  status: string; // "active" | "no_session"
  session_id?: string | null;
  name?: string | null;
  phase?: GardenerPhase | null;
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
  status: string; // "created" | "error"
  session_id?: string | null;
  name?: string | null;
  phase?: GardenerPhase | null;
  polynomial?: string;
  message?: string;
}

/**
 * Request to advance to the next phase.
 */
export interface ConceptGardenerSessionAdvanceRequest {
  session_id?: string | null; // Optional, uses active session if not provided
}

/**
 * Response after advancing phase.
 */
export interface ConceptGardenerSessionAdvanceResponse {
  status: string; // "advanced" | "error"
  phase?: GardenerPhase | null;
  phase_emoji?: string;
  phase_label?: string;
  phase_desc?: string;
  polynomial?: string;
  message?: string;
}

/**
 * Full polynomial state visualization.
 */
export interface ConceptGardenerPolynomialResponse {
  current_phase: GardenerPhase;
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
export interface ConceptGardenerSessionsListResponse {
  sessions: Array<{
    id: string;
    name: string;
    phase: GardenerPhase;
    created_at: string;
    updated_at: string;
    is_active: boolean;
  }>;
  count: number;
  active_id: string | null;
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
  method: string; // "exact" | "pattern" | "llm" | "fallback"
  alternatives?: string[];
  explanation?: string;
}

/**
 * Proactive suggestions for what to do next.
 */
export interface ConceptGardenerProposeResponse {
  suggestion_count: number;
  suggestions: Array<{
    path: string;
    description: string;
    priority: string;
    reasoning: string;
  }>;
}
