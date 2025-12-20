/**
 * Generated types for AGENTESE path: world.file
 * DO NOT EDIT - regenerate with: npm run sync-types
 */

/**
 * Response from reading a file.

Contains the file content and metadata needed for edit validation.
 */
export interface WorldFileReadResponse {
  path: string;
  content: string;
  size: number;
  mtime: number;
  encoding: string;
  cached_at: number;
  lines: number;
  truncated?: boolean;
}

/**
 * Request to edit a file using exact string replacement.

Claude Code pattern: old_string must be unique unless replace_all=True.
 */
export interface WorldFileEditRequest {
  path: string;
  old_string: string;
  new_string: string;
  replace_all?: boolean;
}

/**
 * Response from editing a file.

Includes diff preview for verification.
 */
export interface WorldFileEditResponse {
  success: boolean;
  path: string;
  replacements: number;
  diff_preview: string;
  error?: 'not_read' | 'not_found' | 'not_unique' | 'file_changed' | 'permission_denied' | null;
  error_message?: string | null;
  suggestion?: string | null;
}

/**
 * Request to write a new file (overwrite semantics).

This is for new files. For existing files, use edit.
 */
export interface WorldFileWriteRequest {
  path: string;
  content: string;
  encoding?: string;
  create_dirs?: boolean;
}

/**
 * Response from writing a file.
 */
export interface WorldFileWriteResponse {
  success: boolean;
  path: string;
  size: number;
  created_dirs?: string[];
  error?: string | null;
}

/**
 * Request to glob for files by pattern.
 */
export interface WorldFileGlobRequest {
  pattern: string;
  root?: string;
  max_results?: number;
}

/**
 * Response from glob operation.
 */
export interface WorldFileGlobResponse {
  pattern: string;
  matches: string[];
  total: number;
  truncated?: boolean;
}

/**
 * Request to grep for content.
 */
export interface WorldFileGrepRequest {
  pattern: string;
  path?: string;
  glob?: string | null;
  max_results?: number;
  context_lines?: number;
}

/**
 * Response from grep operation.
 */
export interface WorldFileGrepResponse {
  pattern: string;
  matches: {
    path: string;
    line_number: number;
    content: string;
    context_before: string[];
    context_after: string[];
  }[];
  total: number;
  files_searched: number;
  truncated?: boolean;
}
