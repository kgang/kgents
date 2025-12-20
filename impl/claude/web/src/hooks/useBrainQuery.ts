/**
 * Brain Data Fetching Hooks (AGENTESE Contract-Driven)
 *
 * Hooks for Brain/Memory AGENTESE endpoints using generated contract types.
 * Uses useAsyncState pattern (the project's standard data fetching approach).
 * These are for REST API calls (point-in-time data fetching).
 * For real-time streaming, use useBrainStream.
 *
 * @see services/brain/contracts.py - Python contract definitions
 * @see api/types/_generated/self-memory.ts - Generated TypeScript types
 * @see docs/skills/crown-jewel-patterns.md - Pattern: Contract-First Integration
 */

import { useEffect, useCallback, useState } from 'react';
import { apiClient } from '../api/client';
import { useAsyncState } from './useAsyncState';
import type {
  // Manifest
  SelfMemoryManifestResponse,
  // Capture types
  SelfMemoryCaptureRequest,
  SelfMemoryCaptureResponse,
  // Search types
  SelfMemorySearchRequest,
  SelfMemorySearchResponse,
  // Surface types
  SelfMemorySurfaceRequest,
  SelfMemorySurfaceResponse,
  // Get types
  SelfMemoryGetRequest,
  SelfMemoryGetResponse,
  // Recent types
  SelfMemoryRecentRequest,
  SelfMemoryRecentResponse,
  // ByTag types
  SelfMemoryBytagRequest,
  SelfMemoryBytagResponse,
  // Delete types
  SelfMemoryDeleteRequest,
  SelfMemoryDeleteResponse,
  // Heal types
  SelfMemoryHealResponse,
  // Topology types
  SelfMemoryTopologyRequest,
  SelfMemoryTopologyResponse,
} from '../api/types/_generated/self-memory';

// =============================================================================
// AGENTESE Response Wrapper
// =============================================================================

interface AgenteseResponse<T> {
  path: string;
  aspect: string;
  result: T;
  error?: string;
}

/**
 * Fetch from AGENTESE gateway.
 *
 * Gateway routing rules:
 * - GET  /{path}/manifest - manifest aspect only
 * - POST /{path}/{aspect} - all other aspects
 *
 * Node path: self.memory
 * Aspects: capture, search, surface, get, recent, bytag, delete, heal, topology
 */
async function fetchAgentese<T>(path: string, body?: unknown): Promise<T> {
  // Known node paths for Brain
  const NODE_PATHS = ['self.memory'];

  // Find the matching node path
  let nodePath = '';
  let aspect = '';

  for (const np of NODE_PATHS) {
    if (path === np) {
      nodePath = np;
      aspect = 'manifest';
      break;
    } else if (path.startsWith(np + '.')) {
      nodePath = np;
      aspect = path.slice(np.length + 1);
      break;
    }
  }

  if (!nodePath) {
    // Fallback: assume last segment is aspect
    const parts = path.split('.');
    aspect = parts.pop() ?? 'manifest';
    nodePath = parts.join('.');
  }

  const urlPath = nodePath.replace(/\./g, '/');

  // Only manifest and affordances are GET, everything else is POST
  if (aspect === 'manifest' || aspect === 'affordances') {
    const response = await apiClient.get<AgenteseResponse<T>>(
      `/agentese/${urlPath}/${aspect}`
    );
    if (response.data.error) {
      throw new Error(response.data.error);
    }
    return response.data.result;
  } 
    const response = await apiClient.post<AgenteseResponse<T>>(
      `/agentese/${urlPath}/${aspect}`,
      body ?? {}
    );
    if (response.data.error) {
      throw new Error(response.data.error);
    }
    return response.data.result;
  
}

// =============================================================================
// Query Result Types
// =============================================================================

export interface QueryResult<T> {
  data: T | null;
  isLoading: boolean;
  error: Error | null;
  refetch: () => void;
}

export interface MutationResult<TData, TVariables> {
  data: TData | null;
  isLoading: boolean;
  isPending: boolean;
  error: Error | null;
  mutate: (variables: TVariables) => void;
  mutateAsync: (variables: TVariables) => Promise<TData>;
}

// =============================================================================
// Brain Manifest Hook
// =============================================================================

/**
 * Fetch Brain health/status manifest.
 * AGENTESE: self.memory.manifest
 */
export function useBrainManifest(): QueryResult<SelfMemoryManifestResponse> {
  const { state, execute } = useAsyncState<SelfMemoryManifestResponse>();

  const refetch = useCallback(() => {
    execute(fetchAgentese<SelfMemoryManifestResponse>('self.memory.manifest'));
  }, [execute]);

  useEffect(() => {
    refetch();
  }, [refetch]);

  return {
    data: state.data,
    isLoading: state.isLoading,
    error: state.error ? new Error(state.error) : null,
    refetch,
  };
}

// =============================================================================
// Memory Search Hooks
// =============================================================================

/**
 * Search memories semantically.
 * AGENTESE: self.memory.search
 */
export function useMemorySearch(
  query: string,
  options?: { enabled?: boolean; limit?: number; tags?: string[] }
): QueryResult<SelfMemorySearchResponse> {
  const { state, execute, reset } = useAsyncState<SelfMemorySearchResponse>();
  const enabled = options?.enabled !== false && !!query;

  const refetch = useCallback(() => {
    if (!enabled) return;
    const request: SelfMemorySearchRequest = {
      query,
      limit: options?.limit ?? 10,
      tags: options?.tags ?? null,
    };
    execute(fetchAgentese<SelfMemorySearchResponse>('self.memory.search', request));
  }, [execute, query, enabled, options?.limit, options?.tags]);

  useEffect(() => {
    if (enabled) {
      refetch();
    } else {
      reset();
    }
  }, [enabled, refetch, reset]);

  return {
    data: state.data,
    isLoading: state.isLoading,
    error: state.error ? new Error(state.error) : null,
    refetch,
  };
}

/**
 * Surface a serendipitous memory from the void.
 * AGENTESE: self.memory.surface
 */
export function useMemorySurface(
  options?: { enabled?: boolean; context?: string; entropy?: number }
): QueryResult<SelfMemorySurfaceResponse> {
  const { state, execute, reset } = useAsyncState<SelfMemorySurfaceResponse>();
  const enabled = options?.enabled !== false;

  const refetch = useCallback(() => {
    if (!enabled) return;
    const request: SelfMemorySurfaceRequest = {
      context: options?.context ?? null,
      entropy: options?.entropy ?? 0.5,
    };
    execute(fetchAgentese<SelfMemorySurfaceResponse>('self.memory.surface', request));
  }, [execute, enabled, options?.context, options?.entropy]);

  useEffect(() => {
    if (enabled) {
      refetch();
    } else {
      reset();
    }
  }, [enabled, refetch, reset]);

  return {
    data: state.data,
    isLoading: state.isLoading,
    error: state.error ? new Error(state.error) : null,
    refetch,
  };
}

/**
 * Get a specific crystal by ID.
 * AGENTESE: self.memory.get
 */
export function useMemoryCrystal(
  crystalId: string,
  options?: { enabled?: boolean }
): QueryResult<SelfMemoryGetResponse> {
  const { state, execute, reset } = useAsyncState<SelfMemoryGetResponse>();
  const enabled = options?.enabled !== false && !!crystalId;

  const refetch = useCallback(() => {
    if (!enabled) return;
    const request: SelfMemoryGetRequest = { crystal_id: crystalId };
    execute(fetchAgentese<SelfMemoryGetResponse>('self.memory.get', request));
  }, [execute, crystalId, enabled]);

  useEffect(() => {
    if (enabled) {
      refetch();
    } else {
      reset();
    }
  }, [enabled, refetch, reset]);

  return {
    data: state.data,
    isLoading: state.isLoading,
    error: state.error ? new Error(state.error) : null,
    refetch,
  };
}

/**
 * Fetch recent memories.
 * AGENTESE: self.memory.recent
 */
export function useMemoryRecent(
  options?: { enabled?: boolean; limit?: number }
): QueryResult<SelfMemoryRecentResponse> {
  const { state, execute, reset } = useAsyncState<SelfMemoryRecentResponse>();
  const enabled = options?.enabled !== false;

  const refetch = useCallback(() => {
    if (!enabled) return;
    const request: SelfMemoryRecentRequest = { limit: options?.limit ?? 20 };
    execute(fetchAgentese<SelfMemoryRecentResponse>('self.memory.recent', request));
  }, [execute, enabled, options?.limit]);

  useEffect(() => {
    if (enabled) {
      refetch();
    } else {
      reset();
    }
  }, [enabled, refetch, reset]);

  return {
    data: state.data,
    isLoading: state.isLoading,
    error: state.error ? new Error(state.error) : null,
    refetch,
  };
}

/**
 * Fetch memories by tag.
 * AGENTESE: self.memory.bytag
 */
export function useMemoryByTag(
  tag: string,
  options?: { enabled?: boolean; limit?: number }
): QueryResult<SelfMemoryBytagResponse> {
  const { state, execute, reset } = useAsyncState<SelfMemoryBytagResponse>();
  const enabled = options?.enabled !== false && !!tag;

  const refetch = useCallback(() => {
    if (!enabled) return;
    const request: SelfMemoryBytagRequest = {
      tag,
      limit: options?.limit ?? 20,
    };
    execute(fetchAgentese<SelfMemoryBytagResponse>('self.memory.bytag', request));
  }, [execute, tag, enabled, options?.limit]);

  useEffect(() => {
    if (enabled) {
      refetch();
    } else {
      reset();
    }
  }, [enabled, refetch, reset]);

  return {
    data: state.data,
    isLoading: state.isLoading,
    error: state.error ? new Error(state.error) : null,
    refetch,
  };
}

/**
 * Fetch brain topology for visualization.
 * AGENTESE: self.memory.topology
 */
export function useMemoryTopology(
  options?: { enabled?: boolean; similarityThreshold?: number }
): QueryResult<SelfMemoryTopologyResponse> {
  const { state, execute, reset } = useAsyncState<SelfMemoryTopologyResponse>();
  const enabled = options?.enabled !== false;

  const refetch = useCallback(() => {
    if (!enabled) return;
    const request: SelfMemoryTopologyRequest = {
      similarity_threshold: options?.similarityThreshold ?? 0.3,
    };
    execute(fetchAgentese<SelfMemoryTopologyResponse>('self.memory.topology', request));
  }, [execute, enabled, options?.similarityThreshold]);

  useEffect(() => {
    if (enabled) {
      refetch();
    } else {
      reset();
    }
  }, [enabled, refetch, reset]);

  return {
    data: state.data,
    isLoading: state.isLoading,
    error: state.error ? new Error(state.error) : null,
    refetch,
  };
}

// =============================================================================
// Memory Mutation Hooks
// =============================================================================

/**
 * Capture content to holographic memory.
 * AGENTESE: self.memory.capture
 */
export function useCaptureMemory(): MutationResult<SelfMemoryCaptureResponse, SelfMemoryCaptureRequest> {
  const { state, execute } = useAsyncState<SelfMemoryCaptureResponse>();
  const [isPending, setIsPending] = useState(false);

  const mutateAsync = useCallback(async (data: SelfMemoryCaptureRequest) => {
    setIsPending(true);
    try {
      const result = await execute(fetchAgentese<SelfMemoryCaptureResponse>('self.memory.capture', data));
      if (!result) throw new Error('Failed to capture memory');
      return result;
    } finally {
      setIsPending(false);
    }
  }, [execute]);

  const mutate = useCallback((data: SelfMemoryCaptureRequest) => {
    mutateAsync(data).catch(() => {});
  }, [mutateAsync]);

  return {
    data: state.data,
    isLoading: state.isLoading,
    isPending,
    error: state.error ? new Error(state.error) : null,
    mutate,
    mutateAsync,
  };
}

/**
 * Delete a memory crystal.
 * AGENTESE: self.memory.delete
 */
export function useDeleteMemory(): MutationResult<SelfMemoryDeleteResponse, SelfMemoryDeleteRequest> {
  const { state, execute } = useAsyncState<SelfMemoryDeleteResponse>();
  const [isPending, setIsPending] = useState(false);

  const mutateAsync = useCallback(async (data: SelfMemoryDeleteRequest) => {
    setIsPending(true);
    try {
      const result = await execute(fetchAgentese<SelfMemoryDeleteResponse>('self.memory.delete', data));
      if (!result) throw new Error('Failed to delete memory');
      return result;
    } finally {
      setIsPending(false);
    }
  }, [execute]);

  const mutate = useCallback((data: SelfMemoryDeleteRequest) => {
    mutateAsync(data).catch(() => {});
  }, [mutateAsync]);

  return {
    data: state.data,
    isLoading: state.isLoading,
    isPending,
    error: state.error ? new Error(state.error) : null,
    mutate,
    mutateAsync,
  };
}

/**
 * Heal ghost memories (regenerate embeddings).
 * AGENTESE: self.memory.heal
 */
export function useHealMemory(): MutationResult<SelfMemoryHealResponse, void> {
  const { state, execute } = useAsyncState<SelfMemoryHealResponse>();
  const [isPending, setIsPending] = useState(false);

  const mutateAsync = useCallback(async () => {
    setIsPending(true);
    try {
      const result = await execute(fetchAgentese<SelfMemoryHealResponse>('self.memory.heal', {}));
      if (!result) throw new Error('Failed to heal memories');
      return result;
    } finally {
      setIsPending(false);
    }
  }, [execute]);

  const mutate = useCallback(() => {
    mutateAsync().catch(() => {});
  }, [mutateAsync]);

  return {
    data: state.data,
    isLoading: state.isLoading,
    isPending,
    error: state.error ? new Error(state.error) : null,
    mutate,
    mutateAsync,
  };
}

// =============================================================================
// Query Keys (for cache invalidation patterns if needed later)
// =============================================================================

export const brainQueryKeys = {
  all: ['brain'] as const,
  manifest: () => [...brainQueryKeys.all, 'manifest'] as const,
  search: (query: string) => [...brainQueryKeys.all, 'search', query] as const,
  surface: () => [...brainQueryKeys.all, 'surface'] as const,
  crystal: (id: string) => [...brainQueryKeys.all, 'crystal', id] as const,
  recent: () => [...brainQueryKeys.all, 'recent'] as const,
  byTag: (tag: string) => [...brainQueryKeys.all, 'bytag', tag] as const,
  topology: () => [...brainQueryKeys.all, 'topology'] as const,
};

// =============================================================================
// Re-export types for convenience
// =============================================================================

export type {
  SelfMemoryManifestResponse,
  SelfMemoryCaptureRequest,
  SelfMemoryCaptureResponse,
  SelfMemorySearchRequest,
  SelfMemorySearchResponse,
  SelfMemorySurfaceRequest,
  SelfMemorySurfaceResponse,
  SelfMemoryGetRequest,
  SelfMemoryGetResponse,
  SelfMemoryRecentRequest,
  SelfMemoryRecentResponse,
  SelfMemoryBytagRequest,
  SelfMemoryBytagResponse,
  SelfMemoryDeleteRequest,
  SelfMemoryDeleteResponse,
  SelfMemoryHealResponse,
  SelfMemoryTopologyRequest,
  SelfMemoryTopologyResponse,
};
