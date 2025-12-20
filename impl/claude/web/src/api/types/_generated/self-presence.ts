/**
 * Generated types for AGENTESE path: self.presence
 * DO NOT EDIT - regenerate with: npm run sync-types
 */

/**
 * Response for presence manifest aspect.
 */
export interface SelfPresenceManifestResponse {
  active_count: number;
  cursors: Record<string, unknown>[];
  phase: string;
  tempo_modifier: number;
  subscriber_count: number;
}

/**
 * Response for presence snapshot.
 */
export interface SelfPresenceSnapshotResponse {
  cursors: Record<string, unknown>[];
  count: number;
  phase: string;
  tempo_modifier: number;
}

/**
 * Response listing all cursor states.
 */
export interface SelfPresenceStatesResponse {
  states: Record<string, unknown>[];
}

/**
 * Response for circadian phase info.
 */
export interface SelfPresenceCircadianResponse {
  phase: string;
  tempo_modifier: number;
  warmth: number;
  hour: number;
}

/**
 * Request to get a specific cursor.
 */
export interface SelfPresenceCursorRequest {
  agent_id: string;
}

/**
 * Response for cursor get.
 */
export interface SelfPresenceCursorResponse {
  found: boolean;
  cursor?: Record<string, unknown> | null;
  error?: string | null;
}

/**
 * Request to join presence channel.
 */
export interface SelfPresenceJoinRequest {
  agent_id: string;
  display_name: string;
  initial_state?: string;
  activity?: string;
}

/**
 * Response for join request.
 */
export interface SelfPresenceJoinResponse {
  success: boolean;
  cursor?: Record<string, unknown> | null;
  active_count?: number;
  error?: string | null;
}

/**
 * Request to leave presence channel.
 */
export interface SelfPresenceLeaveRequest {
  agent_id: string;
}

/**
 * Response for leave request.
 */
export interface SelfPresenceLeaveResponse {
  success: boolean;
  was_present?: boolean;
  active_count?: number;
}

/**
 * Request to update cursor state.
 */
export interface SelfPresenceUpdateRequest {
  agent_id: string;
  state?: string | null;
  activity?: string | null;
  focus_path?: string | null;
}

/**
 * Response for cursor update.
 */
export interface SelfPresenceUpdateResponse {
  success: boolean;
  cursor?: Record<string, unknown> | null;
  error?: string | null;
}

/**
 * Request to start/stop demo mode with simulated cursors.
 */
export interface SelfPresenceDemoRequest {
  action?: string;
  agent_count?: number;
  update_interval?: number;
}

/**
 * Response for demo mode.
 */
export interface SelfPresenceDemoResponse {
  success: boolean;
  action: string;
  message: string;
  agent_ids?: string[];
}
