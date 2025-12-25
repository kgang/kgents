/**
 * Document Director API Client
 *
 * Frontend client for the Document Director system.
 *
 * Philosophy:
 *   "Upload → Analyze → Generate → Execute → Capture → Verify"
 */

// =============================================================================
// Types
// =============================================================================

export type DocumentStatus =
  | 'uploaded'
  | 'processing'
  | 'ready'
  | 'executed'
  | 'stale'
  | 'failed'
  | 'ghost';

/**
 * How a ghost document came into existence.
 *
 * Ghosts are the negative space of the document graph — entities that
 * SHOULD exist based on references but DON'T yet.
 */
export type GhostOrigin = 'parsed_reference' | 'anticipated' | 'user_created';

/**
 * Metadata for a ghost document.
 *
 * Philosophy: "The file is a lie. There is only the graph."
 */
export interface GhostMetadata {
  origin: GhostOrigin;
  created_by_path: string; // Which spec created this ghost
  created_at: string; // ISO timestamp
  context: string; // Why this ghost exists
  user_content: string; // User-contributed content (if any)
  is_empty: boolean; // True if ghost has no user content yet
  has_draft_content: boolean; // True if user has started adding content
}

/**
 * Strategy for reconciling ghost content with uploaded "real" document.
 *
 * When a user uploads a document that matches a ghost path, we decide
 * what to do with any content that was in the ghost:
 */
export type ReconciliationStrategy =
  | 'replace' // Use uploaded content, discard ghost
  | 'merge_uploaded_wins' // Zero-Seed merge, conflicts resolved by uploaded
  | 'merge_ghost_wins' // Zero-Seed merge, conflicts resolved by ghost
  | 'interactive'; // Present both for manual merge

export interface ReconciliationRequest {
  ghost_path: string;
  uploaded_content: string;
  strategy: ReconciliationStrategy;
}

export interface ReconciliationResult {
  path: string;
  final_content: string;
  strategy_used: ReconciliationStrategy;
  had_conflicts: boolean;
  conflict_summary: string;
  mark_id: string | null;
}

export interface DocumentEntry {
  path: string;
  title: string;
  status: DocumentStatus;
  version: number;
  word_count: number | null;
  claim_count: number | null;
  impl_count: number | null;
  test_count: number | null;
  placeholder_count: number | null;
  analyzed_at: string | null;
  uploaded_at: string | null;
  // Ghost-specific fields (only present if status === 'ghost')
  ghost_metadata?: GhostMetadata;
  is_ghost?: boolean;
}

/**
 * Check if a document is a ghost (empty placeholder).
 */
export function isGhostDocument(doc: DocumentEntry): boolean {
  return doc.status === 'ghost' || doc.is_ghost === true;
}

/**
 * Check if a ghost has user-contributed content.
 */
export function ghostHasDraft(doc: DocumentEntry): boolean {
  return doc.ghost_metadata?.has_draft_content === true;
}

// Helper to compute ref_count for backwards compatibility
export function getRefCount(doc: DocumentEntry): number {
  return (doc.impl_count ?? 0) + (doc.test_count ?? 0);
}

export interface DocumentListResponse {
  success: boolean;
  total: number;
  documents: DocumentEntry[];
}

export interface MetricsSummary {
  total: number;
  by_status: Record<DocumentStatus, number>;
}

export interface ClaimDetail {
  type: string;
  subject: string;
  predicate: string;
  line: number;
}

export interface AnticipatedImpl {
  path: string;
  type: string;
  spec_line: number;
  context: string;
  owner: string | null;
  phase: string | null;
}

export interface AnalysisCrystal {
  entity_path: string;
  analyzed_at: string;
  title: string;
  word_count: number;
  heading_count: number;
  claims: ClaimDetail[];
  discovered_refs: string[];
  implementations: string[];
  tests: string[];
  spec_refs: string[];
  placeholder_paths: string[];
  anticipated: AnticipatedImpl[];
  status: string;
  error: string | null;
}

export interface DocumentDetail {
  path: string;
  title: string;
  status: DocumentStatus;
  uploaded_at: string;
  analyzed_at: string | null;
  analysis: AnalysisCrystal | null;
  evidence_marks: EvidenceMark[];
}

export interface EvidenceMark {
  mark_id: string;
  action: string;
  reasoning: string | null;
  author: string;
  timestamp: string | null;
  tags: string[];
}

export interface ExecutionPrompt {
  spec_path: string;
  spec_content: string;
  targets: string[];
  context: {
    claims: ClaimDetail[];
    existing_refs: string[];
  };
  mark_id: string | null;
}

export interface AnalyzeResponse {
  success: boolean;
  path: string;
  message: string;
  analysis: AnalysisCrystal;
}

export interface CaptureRequest {
  spec_path: string;
  generated_files: Record<string, string>;
  test_results: {
    passed: string[];
    failed: string[];
    by_file: Record<string, { passed: number; failed: number }>;
  };
}

export interface CaptureResponse {
  success: boolean;
  spec_path: string;
  captured_count: number;
  evidence_marks_created: number;
}

export interface DeleteItemRequest {
  item_type: 'claim' | 'evidence' | 'reference';
  item_id: string;
  reason?: string;
}

export interface DeleteItemResponse {
  success: boolean;
  message: string;
  mark_id: string | null;
}

export interface DocumentHistoryEntry {
  id: string;
  action: string;
  author: string;
  timestamp: string;
  details?: string;
  item_type?: string;
  item_id?: string;
}

export interface DocumentHistoryResponse {
  success: boolean;
  path: string;
  entries: DocumentHistoryEntry[];
  uploaded_at: string;
  analyzed_at: string | null;
}

// =============================================================================
// API Client
// =============================================================================

const API_BASE = '/api/director/documents';

async function fetchJson<T>(url: string, options?: RequestInit): Promise<T> {
  const response = await fetch(url, {
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
    ...options,
  });

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`API error: ${response.status} - ${error}`);
  }

  return response.json();
}

/**
 * List all documents with status.
 */
export async function listDocuments(options?: {
  status?: DocumentStatus;
  limit?: number;
  offset?: number;
}): Promise<DocumentListResponse> {
  const params = new URLSearchParams();
  if (options?.status) params.set('status', options.status);
  if (options?.limit) params.set('limit', String(options.limit));
  if (options?.offset) params.set('offset', String(options.offset));

  const queryString = params.toString();
  const url = queryString ? `${API_BASE}?${queryString}` : API_BASE;

  return fetchJson<DocumentListResponse>(url);
}

/**
 * Get metrics summary.
 * Computed from document list since backend doesn't have dedicated endpoint.
 *
 * Note: Paginates through all documents to compute accurate totals.
 * Backend limit is 500 per request.
 */
export async function getMetrics(): Promise<MetricsSummary> {
  const BACKEND_LIMIT = 500;
  const by_status: Record<DocumentStatus, number> = {
    uploaded: 0,
    processing: 0,
    ready: 0,
    executed: 0,
    stale: 0,
    failed: 0,
    ghost: 0,
  };

  let offset = 0;
  let totalDocuments = 0;

  // Paginate through all documents
  while (true) {
    const list = await listDocuments({ limit: BACKEND_LIMIT, offset });

    for (const doc of list.documents) {
      by_status[doc.status] = (by_status[doc.status] || 0) + 1;
    }

    totalDocuments = list.total;
    offset += list.documents.length;

    // Stop when we've fetched all documents or no more returned
    if (list.documents.length < BACKEND_LIMIT || offset >= list.total) {
      break;
    }
  }

  return { total: totalDocuments, by_status };
}

/**
 * Get document detail with analysis.
 * Backend: GET /api/director/documents/{path}
 */
export async function getDocument(path: string): Promise<DocumentDetail> {
  const encodedPath = encodeURIComponent(path);
  return fetchJson<DocumentDetail>(`${API_BASE}/${encodedPath}`);
}

/**
 * Trigger or re-trigger analysis for a document.
 * Backend: POST /api/director/documents/{path}/analyze
 */
export async function analyzeDocument(
  path: string,
  force = false
): Promise<AnalyzeResponse> {
  const encodedPath = encodeURIComponent(path);
  return fetchJson<AnalyzeResponse>(`${API_BASE}/${encodedPath}/analyze`, {
    method: 'POST',
    body: JSON.stringify({ force }),
  });
}

/**
 * Generate execution prompt for a document.
 * Backend: POST /api/director/documents/{path}/prompt
 */
export async function generatePrompt(path: string): Promise<ExecutionPrompt> {
  const encodedPath = encodeURIComponent(path);
  return fetchJson<ExecutionPrompt>(`${API_BASE}/${encodedPath}/prompt`, {
    method: 'POST',
    body: JSON.stringify({ include_context: true, include_tests: true }),
  });
}

/**
 * Capture execution results.
 * Backend: POST /api/director/documents/{path}/capture
 */
export async function captureExecution(
  request: CaptureRequest
): Promise<CaptureResponse> {
  const encodedPath = encodeURIComponent(request.spec_path);
  return fetchJson<CaptureResponse>(`${API_BASE}/${encodedPath}/capture`, {
    method: 'POST',
    body: JSON.stringify(request),
  });
}

/**
 * Delete a claim, evidence, or reference from a document.
 * Creates a witness mark tracking the deletion.
 * Backend: POST /api/director/documents/{path}/delete-item
 */
export async function deleteItem(
  path: string,
  request: DeleteItemRequest
): Promise<DeleteItemResponse> {
  const encodedPath = encodeURIComponent(path);
  return fetchJson<DeleteItemResponse>(`${API_BASE}/${encodedPath}/delete-item`, {
    method: 'POST',
    body: JSON.stringify(request),
  });
}

/**
 * Get document edit history/ledger.
 * Backend: GET /api/director/documents/{path}/history
 */
export async function getDocumentHistory(path: string): Promise<DocumentHistoryResponse> {
  const encodedPath = encodeURIComponent(path);
  return fetchJson<DocumentHistoryResponse>(`${API_BASE}/${encodedPath}/history`);
}

/**
 * Mark document as viewed (for first-view tracking).
 * Backend: POST /api/director/documents/{path}/mark-viewed
 */
export async function markDocumentViewed(path: string): Promise<{ success: boolean }> {
  const encodedPath = encodeURIComponent(path);
  return fetchJson<{ success: boolean }>(`${API_BASE}/${encodedPath}/mark-viewed`, {
    method: 'POST',
  });
}

/**
 * Delete a document permanently.
 * Backend: DELETE /api/director/documents/{path}
 *
 * WARNING: This is destructive and cannot be undone.
 */
export async function deleteDocument(path: string): Promise<{ success: boolean; message: string; mark_id: string }> {
  const encodedPath = encodeURIComponent(path);
  return fetchJson<{ success: boolean; message: string; mark_id: string }>(`${API_BASE}/${encodedPath}`, {
    method: 'DELETE',
  });
}

/**
 * Rename a document.
 * Backend: PUT /api/director/documents/{path}/rename
 */
export async function renameDocument(
  oldPath: string,
  newPath: string
): Promise<{ success: boolean; old_path: string; new_path: string; mark_id: string; message: string }> {
  const encodedPath = encodeURIComponent(oldPath);
  return fetchJson<{ success: boolean; old_path: string; new_path: string; mark_id: string; message: string }>(
    `${API_BASE}/${encodedPath}/rename`,
    {
      method: 'PUT',
      body: JSON.stringify({ new_path: newPath }),
    }
  );
}

// =============================================================================
// Ghost Document API
// =============================================================================

/**
 * List all ghost documents.
 *
 * Ghosts are the negative space of the document graph — entities that
 * SHOULD exist based on references but DON'T yet.
 */
export async function listGhosts(): Promise<DocumentListResponse> {
  return listDocuments({ status: 'ghost' });
}

/**
 * Update ghost content (user filling in the placeholder).
 * Backend: PUT /api/director/documents/{path}/ghost-content
 */
export async function updateGhostContent(
  path: string,
  content: string
): Promise<{ success: boolean; path: string; word_count: number }> {
  const encodedPath = encodeURIComponent(path);
  return fetchJson<{ success: boolean; path: string; word_count: number }>(
    `${API_BASE}/${encodedPath}/ghost-content`,
    {
      method: 'PUT',
      body: JSON.stringify({ content }),
    }
  );
}

/**
 * Reconcile a ghost with an uploaded document.
 *
 * When a user uploads a document that matches a ghost path, this endpoint
 * mediates the merge using Zero-Seed if both have content.
 *
 * Backend: POST /api/director/documents/{path}/reconcile
 */
export async function reconcileGhost(
  request: ReconciliationRequest
): Promise<ReconciliationResult> {
  const encodedPath = encodeURIComponent(request.ghost_path);
  return fetchJson<ReconciliationResult>(`${API_BASE}/${encodedPath}/reconcile`, {
    method: 'POST',
    body: JSON.stringify(request),
  });
}

/**
 * Promote a ghost to a real document (when user finishes filling content).
 * Backend: POST /api/director/documents/{path}/promote-ghost
 */
export async function promoteGhost(
  path: string
): Promise<{ success: boolean; path: string; new_status: DocumentStatus; mark_id: string }> {
  const encodedPath = encodeURIComponent(path);
  return fetchJson<{ success: boolean; path: string; new_status: DocumentStatus; mark_id: string }>(
    `${API_BASE}/${encodedPath}/promote-ghost`,
    {
      method: 'POST',
    }
  );
}

/**
 * Get ghost metadata for a document.
 * Backend: GET /api/director/documents/{path}/ghost-metadata
 */
export async function getGhostMetadata(path: string): Promise<GhostMetadata | null> {
  const encodedPath = encodeURIComponent(path);
  try {
    return await fetchJson<GhostMetadata>(`${API_BASE}/${encodedPath}/ghost-metadata`);
  } catch {
    return null;
  }
}
