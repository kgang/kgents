/**
 * Generated types for AGENTESE path: self.memory
 * DO NOT EDIT - regenerate with: npm run sync-types
 */

/**
 * Brain health status manifest response.
 */
export interface SelfMemoryManifestResponse {
  total_crystals: number;
  vector_count: number;
  has_semantic: boolean;
  coherency_rate: number;
  ghosts_healed: number;
  storage_path: string;
  storage_backend: string;
}

/**
 * Request to capture content to holographic memory.
 */
export interface SelfMemoryCaptureRequest {
  content: string;
  tags?: string[];
  source_type?: string;
  source_ref?: string | null;
  metadata?: Record<string, unknown> | null;
}

/**
 * Response after capturing content.
 */
export interface SelfMemoryCaptureResponse {
  crystal_id: string;
  content: string;
  summary: string;
  captured_at: string;
  has_embedding: boolean;
  storage: string;
  datum_id: string | null;
  tags: string[];
}

/**
 * Request for semantic search.
 */
export interface SelfMemorySearchRequest {
  query: string;
  limit?: number;
  tags?: string[] | null;
}

/**
 * Response for semantic search.
 */
export interface SelfMemorySearchResponse {
  query: string;
  count: number;
  results: {
    crystal_id: string;
    summary: string;
    similarity: number;
    captured_at: string;
  }[];
}

/**
 * Request for serendipitous surface from the void.
 */
export interface SelfMemorySurfaceRequest {
  context?: string | null;
  entropy?: number;
}

/**
 * Response for surface operation.
 */
export interface SelfMemorySurfaceResponse {
  /** Surfaced crystal item. */
  surface: {
    crystal_id: string;
    content: string;
    summary: string;
    similarity: number;
  } | null;
  entropy: number;
  message?: string | null;
}

/**
 * Request to get specific crystal by ID.
 */
export interface SelfMemoryGetRequest {
  crystal_id: string;
}

/**
 * Response for get crystal operation.
 */
export interface SelfMemoryGetResponse {
  crystal_id: string;
  content: string;
  summary: string;
  captured_at: string;
}

/**
 * Request for recent crystals.
 */
export interface SelfMemoryRecentRequest {
  limit?: number;
}

/**
 * Response for semantic search.
 */
export interface SelfMemoryRecentResponse {
  query: string;
  count: number;
  results: {
    crystal_id: string;
    summary: string;
    similarity: number;
    captured_at: string;
  }[];
}

/**
 * Request for crystals by tag.
 */
export interface SelfMemoryBytagRequest {
  tag: string;
  limit?: number;
}

/**
 * Response for semantic search.
 */
export interface SelfMemoryBytagResponse {
  query: string;
  count: number;
  results: {
    crystal_id: string;
    summary: string;
    similarity: number;
    captured_at: string;
  }[];
}

/**
 * Request to delete a crystal.
 */
export interface SelfMemoryDeleteRequest {
  crystal_id: string;
}

/**
 * Response after deleting a crystal.
 */
export interface SelfMemoryDeleteResponse {
  deleted: boolean;
  crystal_id: string;
}

/**
 * Response after healing ghost memories.
 */
export interface SelfMemoryHealResponse {
  healed: number;
  message: string;
}

/**
 * Request for brain topology.
 */
export interface SelfMemoryTopologyRequest {
  similarity_threshold?: number;
}

/**
 * Response for brain topology visualization.
 */
export interface SelfMemoryTopologyResponse {
  nodes: {
    id: string;
    label: string;
    x: number;
    y: number;
    z: number;
    resolution: number;
    content: string;
    summary: string;
    captured_at: string;
    tags: string[];
  }[];
  edges: {
    source: string;
    target: string;
    similarity: number;
  }[];
  gaps: Record<string, unknown>[];
  hub_ids: string[];
  /** Statistics for brain topology. */
  stats: {
    concept_count: number;
    edge_count: number;
    hub_count: number;
    gap_count: number;
    avg_resolution: number;
  };
}
