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
  note: string | null;
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
