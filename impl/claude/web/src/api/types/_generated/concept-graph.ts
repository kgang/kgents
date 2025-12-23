/**
 * Generated types for AGENTESE path: concept.graph
 * DO NOT EDIT - regenerate with: npm run sync-types
 */

/**
 * Response for graph manifest.
 */
export interface ConceptGraphManifestResponse {
  total_edges: number;
  sources: number;
  origin: string;
  by_origin: Record<string, number>;
  by_kind: Record<string, number>;
  // Event-driven update tracking (for UI refresh)
  last_update_at: string; // ISO timestamp
  update_count: number;
}

/**
 * Request for neighbors query.
 */
export interface ConceptGraphNeighborsRequest {
  path: string;
}

/**
 * Response for neighbors query.
 */
export interface ConceptGraphNeighborsResponse {
  path: string;
  incoming: {
    kind: string;
    source_path: string;
    target_path: string;
    origin: string;
    confidence?: number;
    context?: string | null;
    line_number?: number | null;
    mark_id?: string | null;
  }[];
  outgoing: {
    kind: string;
    source_path: string;
    target_path: string;
    origin: string;
    confidence?: number;
    context?: string | null;
    line_number?: number | null;
    mark_id?: string | null;
  }[];
  total: number;
}

/**
 * Request for evidence query.
 */
export interface ConceptGraphEvidenceRequest {
  spec_path: string;
}

/**
 * Response for evidence query.
 */
export interface ConceptGraphEvidenceResponse {
  spec_path: string;
  evidence: {
    kind: string;
    source_path: string;
    target_path: string;
    origin: string;
    confidence?: number;
    context?: string | null;
    line_number?: number | null;
    mark_id?: string | null;
  }[];
  count: number;
  by_kind: Record<string, number>;
}

/**
 * Request for trace query.
 */
export interface ConceptGraphTraceRequest {
  start: string;
  end: string;
  max_depth?: number;
}

/**
 * Response for trace query.
 */
export interface ConceptGraphTraceResponse {
  start: string;
  end: string;
  paths: {
    edges: {
      kind: string;
      source_path: string;
      target_path: string;
      origin: string;
      confidence?: number;
      context?: string | null;
      line_number?: number | null;
      mark_id?: string | null;
    }[];
    length: number;
    nodes: string[];
  }[];
  found: boolean;
}

/**
 * Request for search query.
 */
export interface ConceptGraphSearchRequest {
  query: string;
  limit?: number;
}

/**
 * Response for search query.
 */
export interface ConceptGraphSearchResponse {
  query: string;
  edges: {
    kind: string;
    source_path: string;
    target_path: string;
    origin: string;
    confidence?: number;
    context?: string | null;
    line_number?: number | null;
    mark_id?: string | null;
  }[];
  count: number;
}
