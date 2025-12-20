/**
 * Generated types for AGENTESE path: self.presence
 * DO NOT EDIT - regenerate with: npm run sync-types
 */

/**
 * Response for presence manifest.
 */
export interface SelfPresenceManifestResponse {
  cursor_count: number;
  cursors: Record<string, unknown>[];
}

/**
 * Request for all cursors.
 */
export interface SelfPresenceCursorsRequest {
  active_only?: boolean;
}

/**
 * Response with cursor list.
 */
export interface SelfPresenceCursorsResponse {
  cursors: Record<string, unknown>[];
}

/**
 * Request to update cursor state.
 */
export interface SelfPresenceUpdateRequest {
  agent_id: string;
  state: string;
  focus_path?: string | null;
  activity?: string;
}

/**
 * Response after cursor update.
 */
export interface SelfPresenceUpdateResponse {
  success: boolean;
  cursor?: Record<string, unknown> | null;
  error?: string | null;
}
