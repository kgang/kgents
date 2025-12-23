/**
 * Generated types for AGENTESE path: self.editor
 * DO NOT EDIT - regenerate with: npm run sync-types
 */

/**
 * Response for editor state aspect.
 */
export interface SelfEditorStateResponse {
  mode: string;
  focus_path: string;
  trail_length: number;
  has_kblock: boolean;
  selection_count: number;
  kblock_id?: string | null;
  command_buffer?: string;
}

/**
 * Request to navigate via edge type.
 */
export interface SelfEditorNavigateRequest {
  edge_type: string;
  from_path?: string | null;
}

/**
 * Response from navigation operation.
 */
export interface SelfEditorNavigateResponse {
  success: boolean;
  new_focus?: string | null;
  message?: string;
  edge_type?: string;
  error?: string | null;
}

/**
 * Request to focus a specific node by AGENTESE path.
 */
export interface SelfEditorFocusRequest {
  path: string;
}

/**
 * Response from focus operation.
 */
export interface SelfEditorFocusResponse {
  success: boolean;
  focused_path?: string | null;
  message?: string;
  error?: string | null;
}

/**
 * Request for available affordances from current focus.
 */
export interface SelfEditorAffordancesRequest {
  from_path?: string | null;
}

/**
 * Response with available edge types and counts.
 */
export interface SelfEditorAffordancesResponse {
  affordances: Record<string, number>;
  focus_path: string;
}

/**
 * Request to enter a mode.
 */
export interface SelfEditorModeRequest {
  mode: string;
}

/**
 * Response from mode change.
 */
export interface SelfEditorModeResponse {
  success: boolean;
  mode: string;
  message?: string;
  error?: string | null;
}

/**
 * Request to execute an editor command.
 */
export interface SelfEditorCommandRequest {
  command: string;
  args?: Record<string, unknown> | null;
}

/**
 * Response from command execution.
 */
export interface SelfEditorCommandResponse {
  success: boolean;
  output?: string;
  result?: Record<string, unknown> | null;
  error?: string | null;
}
