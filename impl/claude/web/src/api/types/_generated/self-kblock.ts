/**
 * Generated types for AGENTESE path: self.kblock
 * DO NOT EDIT - regenerate with: npm run sync-types
 */

/**
 * Response for K-Block manifest.
 */
export interface SelfKblockManifestResponse {
  active_blocks: number;
  blocks: Record<string, unknown>[];
}

/**
 * Request to get K-Block content.
 */
export interface SelfKblockGetRequest {
  block_id: string;
}

/**
 * Response with full K-Block content.
 */
export interface SelfKblockGetResponse {
  block_id: string;
  path: string;
  content: string;
  base_content: string;
  isolation: string;
  is_dirty: boolean;
  active_views: string[];
  checkpoints: Record<string, unknown>[];
  // Genesis feed fields
  galois_loss: number;
  created_by: string | null;
  tags: string[];
}

/**
 * Request to create a K-Block.
 */
export interface SelfKblockCreateRequest {
  path: string;
}

/**
 * Response from K-Block creation.
 */
export interface SelfKblockCreateResponse {
  block_id: string;
  path: string;
  isolation: string;
}

/**
 * Request to save a K-Block.
 */
export interface SelfKblockSaveRequest {
  block_id: string;
  reasoning?: string | null;
}

/**
 * Response from K-Block save.
 */
export interface SelfKblockSaveResponse {
  success: boolean;
  path: string;
  version_id?: string | null;
  no_changes?: boolean;
  error?: string | null;
}

/**
 * Request to edit a K-Block via any view (Phase 3 bidirectional).
 */
export interface SelfKblockView_editRequest {
  block_id: string;
  source_view: string;
  content: string;
  reasoning?: string | null;
}

/**
 * Response from view edit operation.
 */
export interface SelfKblockView_editResponse {
  success: boolean;
  block_id: string;
  source_view: string;
  semantic_deltas: Record<string, unknown>[];
  content_changed: boolean;
  trace?: Record<string, unknown> | null;
  error?: string | null;
}

/**
 * Request to get K-Block references.
 */
export interface SelfKblockReferencesRequest {
  block_id: string;
}

/**
 * Response with discovered references.
 */
export interface SelfKblockReferencesResponse {
  references: Record<string, unknown>[];
}

/**
 * Request to create a thought K-Block (for Membrane).
 */
export interface SelfKblockThoughtRequest {
  content: string;
  session_id?: string | null;
}

/**
 * Response from thought K-Block operations.
 */
export interface SelfKblockThoughtResponse {
  block_id: string;
  content: string;
  isolation: string;
  message_count: number;
}
