/**
 * Generated types for AGENTESE path: self.chat
 * DO NOT EDIT - regenerate with: npm run sync-types
 */

/**
 * Chat service manifest response.
 */
export interface SelfChatManifestResponse {
  active_sessions: number;
  persisted_sessions: number;
  sessions_by_node: Record<string, number>;
}

/**
 * Response for session list aspect.
 */
export interface SelfChatSessionsResponse {
  query: string;
  count: number;
  sessions: {
    session_id: string;
    node_path: string;
    name: string | null;
    turn_count: number;
    state: string;
    active: boolean;
  }[];
}

/**
 * Request to get session details.
 */
export interface SelfChatSessionRequest {
  session_id?: string | null;
  name?: string | null;
}

/**
 * Response for session detail aspect.
 */
export interface SelfChatSessionResponse {
  session_id: string;
  node_path: string;
  name: string | null;
  turn_count: number;
  state: string;
  entropy: number;
  /** Session metrics. */
  metrics: {
    total_tokens?: number | null;
    updated_at?: string | null;
  };
}

/**
 * Request to create a new chat session.
 */
export interface SelfChatCreateRequest {
  node_path?: string;
  force_new?: boolean;
}

/**
 * Response after creating a session.
 */
export interface SelfChatCreateResponse {
  session_id: string;
  node_path: string;
  state: string;
  created: boolean;
}

/**
 * Request to send a message to a session.
 */
export interface SelfChatSendRequest {
  message: string;
  session_id?: string | null;
  node_path?: string | null;
}

/**
 * Response after sending a message.
 */
export interface SelfChatSendResponse {
  response: string;
  session_id: string;
  turn_number: number;
  tokens_in: number;
  tokens_out: number;
}

/**
 * Request to stream a message response.
 */
export interface SelfChatStreamRequest {
  message: string;
  session_id?: string | null;
  node_path?: string | null;
}

/**
 * A single chunk in a streaming response.

Yielded via SSE as the LLM generates tokens.
 */
export interface SelfChatStreamResponse {
  content: string;
  session_id: string;
  turn_number: number;
  is_complete?: boolean;
  tokens_so_far?: number;
}

/**
 * Request for conversation history.
 */
export interface SelfChatHistoryRequest {
  session_id: string;
  limit?: number;
}

/**
 * Response for conversation history.
 */
export interface SelfChatHistoryResponse {
  session_id: string;
  turn_count: number;
  turns: {
    role: string;
    content: string;
    tokens_in: number;
    tokens_out: number;
    timestamp: string;
  }[];
}

/**
 * Request to save a session.
 */
export interface SelfChatSaveRequest {
  session_id: string;
  name?: string | null;
}

/**
 * Response after saving a session.
 */
export interface SelfChatSaveResponse {
  saved: boolean;
  session_id: string;
  name: string | null;
  datum_id: string | null;
}

/**
 * Request to resume a saved session.
 */
export interface SelfChatResumeRequest {
  session_id?: string | null;
  name?: string | null;
}

/**
 * Response after resuming a session.
 */
export interface SelfChatResumeResponse {
  resumed: boolean;
  session_id: string;
  node_path: string;
  name: string | null;
  previous_turns: number;
}

/**
 * Request to search sessions.
 */
export interface SelfChatSearchRequest {
  query: string;
  limit?: number;
}

/**
 * Response for session list aspect.
 */
export interface SelfChatSearchResponse {
  query: string;
  count: number;
  sessions: {
    session_id: string;
    node_path: string;
    name: string | null;
    turn_count: number;
    state: string;
    active: boolean;
  }[];
}

/**
 * Request for metrics.
 */
export interface SelfChatMetricsRequest {
  session_id?: string | null;
}

/**
 * Response for metrics.
 */
export interface SelfChatMetricsResponse {
  total_sessions?: number | null;
  total_turns?: number | null;
  total_tokens?: number | null;
  avg_turn_tokens?: number | null;
}

/**
 * Request to delete a session.
 */
export interface SelfChatDeleteRequest {
  session_id: string;
}

/**
 * Response after deleting a session.
 */
export interface SelfChatDeleteResponse {
  deleted: boolean;
  session_id: string;
}

/**
 * Request to reset a session.
 */
export interface SelfChatResetRequest {
  session_id: string;
}

/**
 * Response after resetting a session.
 */
export interface SelfChatResetResponse {
  reset: boolean;
  session_id: string;
  state: string;
}
