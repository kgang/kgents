/**
 * Spec Ledger API Client
 *
 * Frontend client for the Living Spec ledger system.
 *
 * Philosophy:
 *   "Spec = Asset. Evidence = Transactions."
 *   "If proofs valid, supported. If not used, dead."
 */

// =============================================================================
// Types
// =============================================================================

export interface LedgerSummary {
  total_specs: number;
  active: number;
  orphans: number;
  deprecated: number;
  archived: number;
  total_claims: number;
  contradictions: number;
  harmonies: number;
}

export interface SpecEntry {
  path: string;
  title: string;
  status: 'ACTIVE' | 'ORPHAN' | 'DEPRECATED' | 'ARCHIVED' | 'CONFLICTING';
  claim_count: number;
  impl_count: number;
  test_count: number;
  ref_count: number;
  word_count: number;
}

export interface LedgerResponse {
  success: boolean;
  total: number;
  offset: number;
  limit: number;
  summary: LedgerSummary;
  specs: SpecEntry[];
  orphan_paths: string[];
  deprecated_paths: string[];
}

/**
 * AD-015: Response when proxy handle data hasn't been computed yet.
 */
export interface DataNotComputedResponse {
  success: false;
  needs_scan: true;
  message: string;
  hint: string;
}

export interface ClaimDetail {
  type: string;
  subject: string;
  predicate: string;
  line: number;
}

export interface HarmonyDetail {
  spec: string;
  relationship: string;
  strength: number;
}

export interface ContradictionDetail {
  spec: string;
  conflict_type: string;
  severity: string;
}

export interface SpecDetailResponse {
  success: boolean;
  path: string;
  title: string;
  status: string;
  claims: ClaimDetail[];
  implementations: string[];
  tests: string[];
  references: string[];
  harmonies: HarmonyDetail[];
  contradictions: ContradictionDetail[];
  word_count: number;
  heading_count: number;
}

export interface OrphanEntry {
  path: string;
  title: string;
  claim_count: number;
  word_count: number;
}

export interface OrphansResponse {
  success: boolean;
  total: number;
  orphans: OrphanEntry[];
}

export interface ContradictionEntry {
  spec_a: string;
  spec_b: string;
  conflict_type: string;
  severity: string;
  claim_a: { type: string; text: string };
  claim_b: { type: string; text: string };
}

export interface ContradictionsResponse {
  success: boolean;
  total: number;
  contradictions: ContradictionEntry[];
}

export interface HarmonyEntry {
  spec_a: string;
  spec_b: string;
  relationship: string;
  strength: number;
}

export interface HarmoniesResponse {
  success: boolean;
  total: number;
  harmonies: HarmonyEntry[];
}

export interface ScanResponse {
  success: boolean;
  message: string;
  summary: Record<string, number>;
}

export type EvidenceType = 'implementation' | 'test' | 'usage';

export interface EvidenceAddRequest {
  spec_path: string;
  evidence_path: string;
  evidence_type: EvidenceType;
}

export interface EvidenceAddResponse {
  success: boolean;
  message: string;
  spec_path: string;
  evidence_path: string;
  evidence_type: EvidenceType;
  evidence_exists: boolean;
  was_orphan: boolean;
  is_first_evidence: boolean;
  timestamp: string;
  mark_id: string | null;
  note: string | null;
}

// Evidence query types (unified evidence-as-marks)
export interface EvidenceMark {
  mark_id: string;
  action: string;
  reasoning: string | null;
  author: string;
  timestamp: string | null;
  tags: string[];
}

export interface EvidenceByType {
  impl: EvidenceMark[];
  test: EvidenceMark[];
  usage: EvidenceMark[];
}

export interface EvidenceQueryResponse {
  success: boolean;
  spec_path: string;
  total_evidence: number;
  by_type: EvidenceByType;
  marks: EvidenceMark[];
}

export interface EvidenceVerifyResult {
  mark_id: string;
  file_path: string;
  evidence_type: string | null;
  status: 'valid' | 'stale' | 'broken';
  exists: boolean;
}

export interface EvidenceVerifyResponse {
  success: boolean;
  spec_path: string;
  total: number;
  valid: number;
  stale: number;
  broken: number;
  results: EvidenceVerifyResult[];
}

export interface EvidenceSummaryResponse {
  success: boolean;
  total_specs_with_evidence: number;
  total_impl: number;
  total_test: number;
  total_usage: number;
  by_spec: Record<string, { impl: number; test: number; usage: number }>;
}

// =============================================================================
// API Client
// =============================================================================

const API_BASE = '/api/spec';

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
 * Scan the spec corpus.
 */
export async function scanCorpus(force = false): Promise<ScanResponse> {
  return fetchJson<ScanResponse>(`${API_BASE}/scan`, {
    method: 'POST',
    body: JSON.stringify({ force }),
  });
}

/**
 * Get ledger summary and specs.
 */
export async function getLedger(options?: {
  status?: string;
  sortBy?: string;
  limit?: number;
  offset?: number;
}): Promise<LedgerResponse> {
  const params = new URLSearchParams();
  if (options?.status) params.set('status', options.status);
  if (options?.sortBy) params.set('sort_by', options.sortBy);
  if (options?.limit) params.set('limit', String(options.limit));
  if (options?.offset) params.set('offset', String(options.offset));

  const queryString = params.toString();
  const url = queryString ? `${API_BASE}/ledger?${queryString}` : `${API_BASE}/ledger`;

  return fetchJson<LedgerResponse>(url);
}

/**
 * Get single spec detail.
 */
export async function getSpecDetail(path: string): Promise<SpecDetailResponse> {
  const params = new URLSearchParams({ path });
  return fetchJson<SpecDetailResponse>(`${API_BASE}/detail?${params}`);
}

/**
 * Get orphan specs.
 */
export async function getOrphans(limit = 100): Promise<OrphansResponse> {
  const params = new URLSearchParams({ limit: String(limit) });
  return fetchJson<OrphansResponse>(`${API_BASE}/orphans?${params}`);
}

/**
 * Get contradictions.
 */
export async function getContradictions(): Promise<ContradictionsResponse> {
  return fetchJson<ContradictionsResponse>(`${API_BASE}/contradictions`);
}

/**
 * Get harmonies.
 */
export async function getHarmonies(limit = 50): Promise<HarmoniesResponse> {
  const params = new URLSearchParams({ limit: String(limit) });
  return fetchJson<HarmoniesResponse>(`${API_BASE}/harmonies?${params}`);
}

/**
 * Deprecate specs.
 */
export async function deprecateSpecs(
  paths: string[],
  reason: string
): Promise<{ success: boolean; message: string }> {
  return fetchJson(`${API_BASE}/deprecate`, {
    method: 'POST',
    body: JSON.stringify({ paths, reason }),
  });
}

/**
 * Add evidence (implementation/test) to a spec.
 *
 * This is an accounting TRANSACTION:
 * - Creates a witness mark with evidence tags
 * - Emits SPEC_EVIDENCE_ADDED witness event
 * - May transition spec from ORPHAN → ACTIVE if first evidence
 */
export async function addEvidence(
  specPath: string,
  evidencePath: string,
  evidenceType: EvidenceType = 'implementation'
): Promise<EvidenceAddResponse> {
  return fetchJson<EvidenceAddResponse>(`${API_BASE}/evidence/add`, {
    method: 'POST',
    body: JSON.stringify({
      spec_path: specPath,
      evidence_path: evidencePath,
      evidence_type: evidenceType,
    }),
  });
}

/**
 * Query evidence for a spec from the witness mark system.
 *
 * Returns declared evidence (explicit links) and groups by type.
 */
export async function queryEvidence(
  specPath: string,
  options?: {
    evidenceType?: 'impl' | 'test' | 'usage';
    limit?: number;
  }
): Promise<EvidenceQueryResponse> {
  const params = new URLSearchParams({ path: specPath });
  if (options?.evidenceType) params.set('evidence_type', options.evidenceType);
  if (options?.limit) params.set('limit', String(options.limit));

  return fetchJson<EvidenceQueryResponse>(`${API_BASE}/evidence/query?${params}`);
}

/**
 * Verify all evidence for a spec is still valid.
 *
 * Checks if evidence files still exist on disk.
 */
export async function verifyEvidence(specPath: string): Promise<EvidenceVerifyResponse> {
  const params = new URLSearchParams({ path: specPath });
  return fetchJson<EvidenceVerifyResponse>(`${API_BASE}/evidence/verify?${params}`, {
    method: 'POST',
  });
}

/**
 * Get summary of evidence across all specs.
 *
 * Returns counts by spec and evidence type.
 */
export async function getEvidenceSummary(): Promise<EvidenceSummaryResponse> {
  return fetchJson<EvidenceSummaryResponse>(`${API_BASE}/evidence/summary`);
}
