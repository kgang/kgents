/**
 * Generated types for AGENTESE path: self.repl
 * DO NOT EDIT - regenerate with: npm run sync-types
 */

/**
 * REPL manifest response.
 */
export interface SelfReplManifestResponse {
  turn_count: number;
  max_turns: number;
  utilization: number;
  current_path: string;
  observer: string;
  has_summary: boolean;
  command_history_length: number;
}

/**
 * Conversation memory response.
 */
export interface SelfReplMemoryResponse {
  turns: Record<string, string>[];
  total: number;
  has_summary: boolean;
  summary: string | null;
}

/**
 * Command history response.
 */
export interface SelfReplHistoryResponse {
  commands: string[];
  total: number;
}
