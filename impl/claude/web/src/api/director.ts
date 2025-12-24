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
  | 'failed';

export interface DocumentEntry {
  path: string;
  title: string;
  status: DocumentStatus;
  claim_count: number;
  ref_count: number;
  placeholder_count: number;
  analyzed_at: string | null;
  uploaded_at: string;
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
 */
export async function getMetrics(): Promise<MetricsSummary> {
  const list = await listDocuments({ limit: 1000 });
  const by_status: Record<DocumentStatus, number> = {
    uploaded: 0,
    processing: 0,
    ready: 0,
    executed: 0,
    stale: 0,
    failed: 0,
  };
  for (const doc of list.documents) {
    by_status[doc.status] = (by_status[doc.status] || 0) + 1;
  }
  return { total: list.total, by_status };
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
