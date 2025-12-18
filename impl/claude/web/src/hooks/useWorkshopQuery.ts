/**
 * Workshop Data Fetching Hooks (AGENTESE Contract-Driven)
 *
 * Hooks for Town Workshop AGENTESE endpoints using generated contract types.
 * Uses useAsyncState pattern (the project's standard data fetching approach).
 *
 * @see services/town/contracts.py - Python contract definitions
 * @see api/types/_generated/world-town-workshop.ts - Generated TypeScript types
 * @see docs/skills/crown-jewel-patterns.md - Pattern: Contract-First Integration
 */

import { useEffect, useCallback, useState } from 'react';
import { apiClient } from '../api/client';
import { useAsyncState } from './useAsyncState';
import type {
  // Manifest
  WorldTownWorkshopManifestResponse,
  // Builders
  WorldTownWorkshopBuildersResponse,
  // Assign
  WorldTownWorkshopAssignRequest,
  WorldTownWorkshopAssignResponse,
  // Advance
  WorldTownWorkshopAdvanceResponse,
  // Complete
  WorldTownWorkshopCompleteResponse,
} from '../api/types/_generated/world-town-workshop';

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
 * Node path: world.town.workshop
 * Aspects: manifest, builders, assign, advance, complete
 */
async function fetchAgentese<T>(path: string, body?: unknown): Promise<T> {
  // Known node paths for Workshop
  const NODE_PATHS = ['world.town.workshop'];

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
    aspect = parts.pop()!;
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
  } else {
    const response = await apiClient.post<AgenteseResponse<T>>(
      `/agentese/${urlPath}/${aspect}`,
      body ?? {}
    );
    if (response.data.error) {
      throw new Error(response.data.error);
    }
    return response.data.result;
  }
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
// Workshop Query Hooks
// =============================================================================

/**
 * Fetch Workshop status manifest.
 * AGENTESE: world.town.workshop.manifest
 */
export function useWorkshopManifest(): QueryResult<WorldTownWorkshopManifestResponse> {
  const { state, execute } = useAsyncState<WorldTownWorkshopManifestResponse>();

  const refetch = useCallback(() => {
    execute(fetchAgentese<WorldTownWorkshopManifestResponse>('world.town.workshop.manifest'));
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
 * Fetch available builders in the workshop.
 * AGENTESE: world.town.workshop.builders
 */
export function useWorkshopBuilders(
  options?: { enabled?: boolean }
): QueryResult<WorldTownWorkshopBuildersResponse> {
  const { state, execute, reset } = useAsyncState<WorldTownWorkshopBuildersResponse>();
  const enabled = options?.enabled !== false;

  const refetch = useCallback(() => {
    if (!enabled) return;
    execute(fetchAgentese<WorldTownWorkshopBuildersResponse>('world.town.workshop.builders', {}));
  }, [execute, enabled]);

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
// Workshop Mutation Hooks
// =============================================================================

/**
 * Assign a task to workshop builders.
 * AGENTESE: world.town.workshop.assign
 */
export function useAssignWorkshopTask(): MutationResult<WorldTownWorkshopAssignResponse, WorldTownWorkshopAssignRequest> {
  const { state, execute } = useAsyncState<WorldTownWorkshopAssignResponse>();
  const [isPending, setIsPending] = useState(false);

  const mutateAsync = useCallback(async (data: WorldTownWorkshopAssignRequest) => {
    setIsPending(true);
    try {
      const result = await execute(fetchAgentese<WorldTownWorkshopAssignResponse>('world.town.workshop.assign', data));
      if (!result) throw new Error('Failed to assign task');
      return result;
    } finally {
      setIsPending(false);
    }
  }, [execute]);

  const mutate = useCallback((data: WorldTownWorkshopAssignRequest) => {
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
 * Advance the workshop to next phase.
 * AGENTESE: world.town.workshop.advance
 */
export function useAdvanceWorkshop(): MutationResult<WorldTownWorkshopAdvanceResponse, void> {
  const { state, execute } = useAsyncState<WorldTownWorkshopAdvanceResponse>();
  const [isPending, setIsPending] = useState(false);

  const mutateAsync = useCallback(async () => {
    setIsPending(true);
    try {
      const result = await execute(fetchAgentese<WorldTownWorkshopAdvanceResponse>('world.town.workshop.advance', {}));
      if (!result) throw new Error('Failed to advance workshop');
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

/**
 * Complete the current workshop task.
 * AGENTESE: world.town.workshop.complete
 */
export function useCompleteWorkshop(): MutationResult<WorldTownWorkshopCompleteResponse, void> {
  const { state, execute } = useAsyncState<WorldTownWorkshopCompleteResponse>();
  const [isPending, setIsPending] = useState(false);

  const mutateAsync = useCallback(async () => {
    setIsPending(true);
    try {
      const result = await execute(fetchAgentese<WorldTownWorkshopCompleteResponse>('world.town.workshop.complete', {}));
      if (!result) throw new Error('Failed to complete workshop');
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

export const workshopQueryKeys = {
  all: ['workshop'] as const,
  manifest: () => [...workshopQueryKeys.all, 'manifest'] as const,
  builders: () => [...workshopQueryKeys.all, 'builders'] as const,
};

// =============================================================================
// Re-export types for convenience
// =============================================================================

export type {
  WorldTownWorkshopManifestResponse,
  WorldTownWorkshopBuildersResponse,
  WorldTownWorkshopAssignRequest,
  WorldTownWorkshopAssignResponse,
  WorldTownWorkshopAdvanceResponse,
  WorldTownWorkshopCompleteResponse,
};
