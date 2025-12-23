/**
 * Brain API Client — Extended operations for BrainPage
 *
 * Extends the base brainApi in client.ts with additional operations:
 * - search: Semantic search through memories
 * - listCaptures: List recent memories
 * - surface: Serendipitous memory surfacing
 * - recall: Direct lookup by ID
 *
 * "The proof IS the decision. The mark IS the witness."
 */

import { apiClient } from './client';

// =============================================================================
// Types
// =============================================================================

export interface BrainStatusResponse {
  total_captures: number;
  vector_count: number;
  has_semantic: boolean;
  coherency_rate: number;
  ghosts_healed: number;
  storage_path: string;
  storage_backend: 'sqlite' | 'postgres';
}

export interface SearchResult {
  concept_id: string;
  content: string;
  similarity: number;
  captured_at: string;
  is_stale: boolean;
}

export interface CaptureItem {
  concept_id: string;
  content: string;
  captured_at: string;
}

export interface TopologyNode {
  id: string;
  label: string;
  x: number;
  y: number;
  z: number;
  resolution: number;
  is_hot: boolean;
  access_count: number;
  age_seconds: number;
  content_preview: string | null;
}

export interface TopologyEdge {
  source: string;
  target: string;
  similarity: number;
}

export interface TopologyResponse {
  nodes: TopologyNode[];
  edges: TopologyEdge[];
  gaps: Array<{ x: number; y: number; z: number; radius: number }>;
  hub_ids: string[];
  stats: {
    concept_count: number;
    edge_count: number;
    hub_count: number;
    gap_count: number;
    avg_resolution: number;
  };
}

// =============================================================================
// AGENTESE Response Wrapper
// =============================================================================

interface AgenteseResponse<T> {
  path: string;
  aspect: string;
  result: T;
  error?: string;
}

function unwrap<T>(response: { data: AgenteseResponse<T> }): T {
  if (response.data.error) {
    throw new Error(response.data.error);
  }
  return response.data.result;
}

// =============================================================================
// Extended Brain API
// =============================================================================

export const brainApiExtended = {
  /**
   * Get brain status via AGENTESE: self.memory.manifest
   */
  getStatus: async (): Promise<BrainStatusResponse> => {
    const response = await apiClient.get<AgenteseResponse<BrainStatusResponse>>(
      '/agentese/self/memory/manifest'
    );
    return unwrap(response);
  },

  /**
   * Semantic search via AGENTESE: self.memory.search
   */
  search: async (query: string, limit = 20): Promise<SearchResult[]> => {
    const response = await apiClient.post<AgenteseResponse<{ results: SearchResult[] }>>(
      '/agentese/self/memory/search',
      { query, limit }
    );
    return unwrap(response).results || [];
  },

  /**
   * List recent captures via AGENTESE: self.memory.recent
   */
  listCaptures: async (limit = 50, offset = 0): Promise<CaptureItem[]> => {
    const response = await apiClient.post<AgenteseResponse<{ captures: CaptureItem[] }>>(
      '/agentese/self/memory/recent',
      { limit, offset }
    );
    return unwrap(response).captures || [];
  },

  /**
   * Surface serendipitous memory via AGENTESE: self.memory.surface
   *
   * The Accursed Share: Pull a random-ish relevant memory.
   */
  surface: async (context?: string, entropy = 0.7): Promise<SearchResult | null> => {
    const response = await apiClient.post<AgenteseResponse<SearchResult | null>>(
      '/agentese/self/memory/surface',
      { context, entropy }
    );
    return unwrap(response);
  },

  /**
   * Direct recall by ID via AGENTESE: self.memory.get
   */
  recall: async (conceptId: string): Promise<CaptureItem | null> => {
    const response = await apiClient.post<AgenteseResponse<CaptureItem | null>>(
      '/agentese/self/memory/get',
      { crystal_id: conceptId }
    );
    return unwrap(response);
  },

  /**
   * Capture content to brain via AGENTESE: self.memory.capture
   */
  capture: async (content: string, tags?: string[]): Promise<{ crystal_id: string }> => {
    const response = await apiClient.post<AgenteseResponse<{ crystal_id: string }>>(
      '/agentese/self/memory/capture',
      { content, tags }
    );
    return unwrap(response);
  },

  /**
   * Get topology for 3D visualization via AGENTESE: self.memory.topology
   */
  getTopology: async (similarityThreshold = 0.3): Promise<TopologyResponse> => {
    const response = await apiClient.post<AgenteseResponse<TopologyResponse>>(
      '/agentese/self/memory/topology',
      { similarity_threshold: similarityThreshold }
    );
    return unwrap(response);
  },
};

export default brainApiExtended;
