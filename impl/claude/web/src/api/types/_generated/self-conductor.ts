/**
 * Generated types for AGENTESE path: self.conductor
 * DO NOT EDIT - regenerate with: npm run sync-types
 */

/**
 * Response for conductor manifest aspect.
 */
export interface SelfConductorManifestResponse {
  active_windows: number;
  strategies_available: string[];
  windows: Record<string, string | number | number | boolean>[];
}

/**
 * Request for snapshot aspect.
 */
export interface SelfConductorSnapshotRequest {
  session_id?: string | null;
}

/**
 * Response for snapshot aspect - immutable window state.
 */
export interface SelfConductorSnapshotResponse {
  turn_count: number;
  total_turn_count: number;
  total_tokens: number;
  utilization: number;
  strategy: string;
  has_summary: boolean;
  max_turns: number;
  error?: string | null;
}

/**
 * Request for history aspect.
 */
export interface SelfConductorHistoryRequest {
  session_id?: string | null;
  limit?: number | null;
  include_system?: boolean;
}

/**
 * Response for history aspect - bounded conversation messages.
 */
export interface SelfConductorHistoryResponse {
  messages: {
    role: string;
    content: string;
    tokens: number;
  }[];
  total: number;
  window_turn_count: number;
  window_total_turn_count: number;
  error?: string | null;
}

/**
 * Request for getting conversation summary.
 */
export interface SelfConductorSummaryRequest {
  session_id?: string | null;
}

/**
 * Response for getting conversation summary.
 */
export interface SelfConductorSummaryResponse {
  has_summary: boolean;
  summary: string | null;
  summarized_turn_count: number;
  strategy: string;
  error?: string | null;
}

/**
 * Request for getting window configuration.
 */
export interface SelfConductorConfigRequest {
  session_id?: string | null;
}

/**
 * Response for config aspect - window configuration.
 */
export interface SelfConductorConfigResponse {
  max_turns: number;
  strategy: string;
  context_window_tokens: number;
  summarization_threshold: number;
  has_summarizer: boolean;
  error?: string | null;
}

/**
 * Request for listing sessions.
 */
export interface SelfConductorSessionsRequest {
  node_path?: string | null;
  limit?: number;
}

/**
 * Response for sessions list aspect.
 */
export interface SelfConductorSessionsResponse {
  sessions: {
    session_id: string;
    node_path: string;
    is_active: boolean;
    turn_count: number;
    window?: Record<string, number | number | string | boolean> | null;
  }[];
  total: number;
  error?: string | null;
}

/**
 * Request for resetting conversation window.
 */
export interface SelfConductorResetRequest {
  session_id?: string | null;
  preserve_system?: boolean;
}

/**
 * Response for reset aspect.
 */
export interface SelfConductorResetResponse {
  success: boolean;
  session_id: string | null;
  preserved_system: boolean;
  error?: string | null;
}

/**
 * Request for flux status.
 */
// eslint-disable-next-line @typescript-eslint/no-empty-object-type
export interface SelfConductorFluxRequest {}

/**
 * Response for flux status - event integration state.
 */
export interface SelfConductorFluxResponse {
  running: boolean;
  subscriber_count: number;
  event_types_monitored: string[];
  bridge_active: boolean;
  error?: string | null;
}

/**
 * Request to start flux event integration.
 */
// eslint-disable-next-line @typescript-eslint/no-empty-object-type
export interface SelfConductorFlux_startRequest {}

/**
 * Response for starting flux.
 */
export interface SelfConductorFlux_startResponse {
  success: boolean;
  was_already_running: boolean;
  error?: string | null;
}

/**
 * Request to stop flux event integration.
 */
// eslint-disable-next-line @typescript-eslint/no-empty-object-type
export interface SelfConductorFlux_stopRequest {}

/**
 * Response for stopping flux.
 */
export interface SelfConductorFlux_stopResponse {
  success: boolean;
  was_running: boolean;
  error?: string | null;
}
