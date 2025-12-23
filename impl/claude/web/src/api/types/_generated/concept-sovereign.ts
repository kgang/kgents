/**
 * Generated types for AGENTESE path: concept.sovereign
 * DO NOT EDIT - regenerate with: npm run sync-types
 */

/**
 * Response for manifest aspect - sovereign store health.
 */
export interface ConceptSovereignManifestResponse {
  entity_count: number;
  total_versions: number;
  storage_root: string;
  last_ingest?: string | null;
}

/**
 * Request to list sovereign entities.
 */
export interface ConceptSovereignListRequest {
  prefix?: string;
  limit?: number;
}

/**
 * Response with entity paths.
 */
export interface ConceptSovereignListResponse {
  paths: string[];
  total: number;
}

/**
 * Request to query a sovereign entity.
 */
export interface ConceptSovereignQueryRequest {
  path: string;
  version?: number | null;
  include_overlay?: boolean;
}

/**
 * Response with entity content and metadata.
 */
export interface ConceptSovereignQueryResponse {
  path: string;
  version: number;
  content: string;
  content_hash: string;
  ingest_mark_id: string | null;
  overlay?: Record<string, unknown>;
}

/**
 * Request to diff sovereign copy with source.
 */
export interface ConceptSovereignDiffRequest {
  path: string;
  source_content: string;
}

/**
 * Response with diff result.
 */
export interface ConceptSovereignDiffResponse {
  path: string;
  diff_type: string;
  our_hash?: string | null;
  source_hash?: string | null;
}

/**
 * Request to ingest a document.
 */
export interface ConceptSovereignIngestRequest {
  path: string;
  content: string;
  source?: string;
}

/**
 * Response from ingest - the birth certificate.
 */
export interface ConceptSovereignIngestResponse {
  path: string;
  version: number;
  ingest_mark_id: string;
  edge_count: number;
}

/**
 * Request to bootstrap from filesystem.
 */
export interface ConceptSovereignBootstrapRequest {
  root: string;
  pattern?: string;
  dry_run?: boolean;
}

/**
 * Response from bootstrap operation.
 */
export interface ConceptSovereignBootstrapResponse {
  files_found: number;
  files_ingested: number;
  edges_discovered: number;
  duration_seconds: number;
  dry_run: boolean;
}

/**
 * Request to sync a file from source.
 */
export interface ConceptSovereignSyncRequest {
  path: string;
  source?: string;
}

/**
 * Response from sync operation.
 */
export interface ConceptSovereignSyncResponse {
  path: string;
  status: string;
  old_version?: number | null;
  new_version?: number | null;
  message?: string;
}
