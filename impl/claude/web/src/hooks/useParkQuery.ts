/**
 * Park Data Fetching Hooks (AGENTESE Contract-Driven)
 *
 * Hooks for Park AGENTESE endpoints using generated contract types.
 * Uses useAsyncState pattern (the project's standard data fetching approach).
 * These are for REST API calls (point-in-time data fetching).
 * For real-time streaming, a separate useParkStreamWidget would be needed.
 *
 * @see services/park/contracts.py - Python contract definitions
 * @see api/types/_generated/world-park.ts - Generated TypeScript types
 * @see docs/skills/crown-jewel-patterns.md - Pattern: Contract-First Integration
 */

import { useEffect, useCallback, useState } from 'react';
import { apiClient } from '../api/client';
import { useAsyncState } from './useAsyncState';
import type {
  // Park manifest
  WorldParkManifestResponse,
  // Host types
  WorldParkHostListResponse,
  WorldParkHostGetResponse,
  WorldParkHostCreateRequest,
  WorldParkHostCreateResponse,
  WorldParkHostUpdateRequest,
  WorldParkHostUpdateResponse,
  // Interaction types
  WorldParkHostInteractRequest,
  WorldParkHostInteractResponse,
  // Memory types
  WorldParkHostWitnessRequest,
  WorldParkHostWitnessResponse,
  // Episode types
  WorldParkEpisodeListResponse,
  WorldParkEpisodeStartRequest,
  WorldParkEpisodeStartResponse,
  WorldParkEpisodeEndRequest,
  WorldParkEpisodeEndResponse,
  // Location types
  WorldParkLocationListResponse,
  WorldParkLocationCreateRequest,
  WorldParkLocationCreateResponse,
} from '../api/types/_generated/world-park';

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
 * IMPORTANT: Gateway routing rules:
 * - GET  /{path}/manifest - manifest aspect only
 * - POST /{path}/{aspect} - all other aspects
 * - GET  /{path}/affordances - list affordances
 *
 * Node paths are registered at specific levels (e.g., "world.park").
 * Aspects can be simple ("manifest") or compound ("host.list").
 *
 * For "world.park.host.list":
 * - Node is at "world.park"
 * - Aspect is "host.list" (compound)
 * - URL: POST /agentese/world/park/host.list
 */
async function fetchAgentese<T>(path: string, body?: unknown): Promise<T> {
  // Known node paths - these are the registered @node paths
  const NODE_PATHS = [
    'world.town.coalition',
    'world.town.workshop',
    'world.town.inhabit',
    'world.town.collective',
    'world.town',
    'self.memory',
    'world.codebase',
    'world.atelier',
    'world.park',
    'concept.gardener',
  ];

  // Find the matching node path
  let nodePath = '';
  let aspect = '';

  for (const np of NODE_PATHS) {
    if (path === np) {
      // Exact match - default to manifest
      nodePath = np;
      aspect = 'manifest';
      break;
    } else if (path.startsWith(np + '.')) {
      // Path extends a node - everything after is the aspect
      nodePath = np;
      aspect = path.slice(np.length + 1);
      break;
    }
  }

  if (!nodePath) {
    // Fallback: assume last segment is aspect
    const parts = path.split('.');
    const lastPart = parts.pop();
    aspect = lastPart ?? '';
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

  // All other aspects require POST (even without body)
  // Compound aspects like "host.list" stay as-is in the URL
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
// Park Manifest Hook
// =============================================================================

/**
 * Fetch Park health/status manifest.
 * AGENTESE: world.park.manifest
 */
export function useParkManifest(): QueryResult<WorldParkManifestResponse> {
  const { state, execute } = useAsyncState<WorldParkManifestResponse>();

  const refetch = useCallback(() => {
    execute(fetchAgentese<WorldParkManifestResponse>('world.park.manifest'));
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
// Host Hooks
// =============================================================================

/**
 * Fetch list of all hosts.
 * AGENTESE: world.park.host.list
 */
export function useHosts(): QueryResult<WorldParkHostListResponse> {
  const { state, execute } = useAsyncState<WorldParkHostListResponse>();

  const refetch = useCallback(() => {
    execute(fetchAgentese<WorldParkHostListResponse>('world.park.host.list'));
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

/**
 * Fetch single host details.
 * AGENTESE: world.park.host.get
 */
export function useHost(
  hostId: string,
  options?: { enabled?: boolean }
): QueryResult<WorldParkHostGetResponse> {
  const { state, execute, reset } = useAsyncState<WorldParkHostGetResponse>();
  const enabled = options?.enabled !== false && !!hostId;

  const refetch = useCallback(() => {
    if (!enabled) return;
    execute(fetchAgentese<WorldParkHostGetResponse>('world.park.host.get', { host_id: hostId }));
  }, [execute, hostId, enabled]);

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
 * Create a new host.
 * AGENTESE: world.park.host.create
 */
export function useCreateHost(): MutationResult<WorldParkHostCreateResponse, WorldParkHostCreateRequest> {
  const { state, execute } = useAsyncState<WorldParkHostCreateResponse>();
  const [isPending, setIsPending] = useState(false);

  const mutateAsync = useCallback(async (data: WorldParkHostCreateRequest) => {
    setIsPending(true);
    try {
      const result = await execute(fetchAgentese<WorldParkHostCreateResponse>('world.park.host.create', data));
      if (!result) throw new Error('Failed to create host');
      return result;
    } finally {
      setIsPending(false);
    }
  }, [execute]);

  const mutate = useCallback((data: WorldParkHostCreateRequest) => {
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
 * Update an existing host.
 * AGENTESE: world.park.host.update
 */
export function useUpdateHost(): MutationResult<WorldParkHostUpdateResponse, WorldParkHostUpdateRequest> {
  const { state, execute } = useAsyncState<WorldParkHostUpdateResponse>();
  const [isPending, setIsPending] = useState(false);

  const mutateAsync = useCallback(async (data: WorldParkHostUpdateRequest) => {
    setIsPending(true);
    try {
      const result = await execute(fetchAgentese<WorldParkHostUpdateResponse>('world.park.host.update', data));
      if (!result) throw new Error('Failed to update host');
      return result;
    } finally {
      setIsPending(false);
    }
  }, [execute]);

  const mutate = useCallback((data: WorldParkHostUpdateRequest) => {
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
 * Interact with a host (dialogue, action, etc.).
 * AGENTESE: world.park.host.interact
 */
export function useInteractWithHost(): MutationResult<WorldParkHostInteractResponse, WorldParkHostInteractRequest> {
  const { state, execute } = useAsyncState<WorldParkHostInteractResponse>();
  const [isPending, setIsPending] = useState(false);

  const mutateAsync = useCallback(async (data: WorldParkHostInteractRequest) => {
    setIsPending(true);
    try {
      const result = await execute(fetchAgentese<WorldParkHostInteractResponse>('world.park.host.interact', data));
      if (!result) throw new Error('Failed to interact with host');
      return result;
    } finally {
      setIsPending(false);
    }
  }, [execute]);

  const mutate = useCallback((data: WorldParkHostInteractRequest) => {
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
 * Fetch host memories (witness aspect).
 * AGENTESE: world.park.host.witness
 */
export function useHostMemories(
  hostId: string,
  options?: { enabled?: boolean; memoryType?: string; minSalience?: number; limit?: number }
): QueryResult<WorldParkHostWitnessResponse> {
  const { state, execute, reset } = useAsyncState<WorldParkHostWitnessResponse>();
  const enabled = options?.enabled !== false && !!hostId;

  const refetch = useCallback(() => {
    if (!enabled) return;
    const request: WorldParkHostWitnessRequest = {
      host_id: hostId,
      memory_type: options?.memoryType,
      min_salience: options?.minSalience ?? 0.0,
      limit: options?.limit ?? 20,
    };
    execute(fetchAgentese<WorldParkHostWitnessResponse>('world.park.host.witness', request));
  }, [execute, hostId, enabled, options?.memoryType, options?.minSalience, options?.limit]);

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
// Episode Hooks
// =============================================================================

/**
 * Fetch list of all episodes.
 * AGENTESE: world.park.episode.list
 */
export function useEpisodes(): QueryResult<WorldParkEpisodeListResponse> {
  const { state, execute } = useAsyncState<WorldParkEpisodeListResponse>();

  const refetch = useCallback(() => {
    execute(fetchAgentese<WorldParkEpisodeListResponse>('world.park.episode.list'));
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

/**
 * Start a new park episode.
 * AGENTESE: world.park.episode.start
 */
export function useStartEpisode(): MutationResult<WorldParkEpisodeStartResponse, WorldParkEpisodeStartRequest> {
  const { state, execute } = useAsyncState<WorldParkEpisodeStartResponse>();
  const [isPending, setIsPending] = useState(false);

  const mutateAsync = useCallback(async (data: WorldParkEpisodeStartRequest = {}) => {
    setIsPending(true);
    try {
      const result = await execute(fetchAgentese<WorldParkEpisodeStartResponse>('world.park.episode.start', data));
      if (!result) throw new Error('Failed to start episode');
      return result;
    } finally {
      setIsPending(false);
    }
  }, [execute]);

  const mutate = useCallback((data: WorldParkEpisodeStartRequest = {}) => {
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
 * End a park episode.
 * AGENTESE: world.park.episode.end
 */
export function useEndEpisode(): MutationResult<WorldParkEpisodeEndResponse, WorldParkEpisodeEndRequest> {
  const { state, execute } = useAsyncState<WorldParkEpisodeEndResponse>();
  const [isPending, setIsPending] = useState(false);

  const mutateAsync = useCallback(async (data: WorldParkEpisodeEndRequest) => {
    setIsPending(true);
    try {
      const result = await execute(fetchAgentese<WorldParkEpisodeEndResponse>('world.park.episode.end', data));
      if (!result) throw new Error('Failed to end episode');
      return result;
    } finally {
      setIsPending(false);
    }
  }, [execute]);

  const mutate = useCallback((data: WorldParkEpisodeEndRequest) => {
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

// =============================================================================
// Location Hooks
// =============================================================================

/**
 * Fetch list of all locations.
 * AGENTESE: world.park.location.list
 */
export function useLocations(): QueryResult<WorldParkLocationListResponse> {
  const { state, execute } = useAsyncState<WorldParkLocationListResponse>();

  const refetch = useCallback(() => {
    execute(fetchAgentese<WorldParkLocationListResponse>('world.park.location.list'));
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

/**
 * Create a new location.
 * AGENTESE: world.park.location.create
 */
export function useCreateLocation(): MutationResult<WorldParkLocationCreateResponse, WorldParkLocationCreateRequest> {
  const { state, execute } = useAsyncState<WorldParkLocationCreateResponse>();
  const [isPending, setIsPending] = useState(false);

  const mutateAsync = useCallback(async (data: WorldParkLocationCreateRequest) => {
    setIsPending(true);
    try {
      const result = await execute(fetchAgentese<WorldParkLocationCreateResponse>('world.park.location.create', data));
      if (!result) throw new Error('Failed to create location');
      return result;
    } finally {
      setIsPending(false);
    }
  }, [execute]);

  const mutate = useCallback((data: WorldParkLocationCreateRequest) => {
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

// =============================================================================
// Query Keys (for cache invalidation patterns if needed later)
// =============================================================================

export const parkQueryKeys = {
  all: ['park'] as const,
  manifest: () => [...parkQueryKeys.all, 'manifest'] as const,
  hosts: () => [...parkQueryKeys.all, 'hosts'] as const,
  hostsList: () => [...parkQueryKeys.hosts(), 'list'] as const,
  hostDetail: (id: string) => [...parkQueryKeys.hosts(), 'detail', id] as const,
  hostMemories: (id: string) => [...parkQueryKeys.hosts(), 'memories', id] as const,
  episodes: () => [...parkQueryKeys.all, 'episodes'] as const,
  episodesList: () => [...parkQueryKeys.episodes(), 'list'] as const,
  locations: () => [...parkQueryKeys.all, 'locations'] as const,
  locationsList: () => [...parkQueryKeys.locations(), 'list'] as const,
};

// =============================================================================
// Exports
// =============================================================================

export type {
  WorldParkManifestResponse,
  WorldParkHostListResponse,
  WorldParkHostGetResponse,
  WorldParkHostCreateRequest,
  WorldParkHostCreateResponse,
  WorldParkHostUpdateRequest,
  WorldParkHostUpdateResponse,
  WorldParkHostInteractRequest,
  WorldParkHostInteractResponse,
  WorldParkHostWitnessRequest,
  WorldParkHostWitnessResponse,
  WorldParkEpisodeListResponse,
  WorldParkEpisodeStartRequest,
  WorldParkEpisodeStartResponse,
  WorldParkEpisodeEndRequest,
  WorldParkEpisodeEndResponse,
  WorldParkLocationListResponse,
  WorldParkLocationCreateRequest,
  WorldParkLocationCreateResponse,
};
