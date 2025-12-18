/**
 * Gestalt Data Fetching Hooks (AGENTESE Contract-Driven)
 *
 * Hooks for Gestalt/Codebase AGENTESE endpoints using generated contract types.
 * Uses useAsyncState pattern (the project's standard data fetching approach).
 * These are for REST API calls (point-in-time data fetching).
 * For real-time streaming, use useGestaltStream.
 *
 * @see services/gestalt/contracts.py - Python contract definitions
 * @see api/types/_generated/world-codebase.ts - Generated TypeScript types
 * @see docs/skills/crown-jewel-patterns.md - Pattern: Contract-First Integration
 */

import { useEffect, useCallback, useState } from 'react';
import { apiClient } from '../api/client';
import { useAsyncState } from './useAsyncState';
import type {
  // Manifest
  WorldCodebaseManifestResponse,
  // Health
  WorldCodebaseHealthResponse,
  // Drift
  WorldCodebaseDriftResponse,
  // Topology
  WorldCodebaseTopologyRequest,
  WorldCodebaseTopologyResponse,
  // Module
  WorldCodebaseModuleRequest,
  WorldCodebaseModuleResponse,
  // Scan
  WorldCodebaseScanRequest,
  WorldCodebaseScanResponse,
} from '../api/types/_generated/world-codebase';

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
 * Node path: world.codebase
 * Aspects: manifest, health, drift, topology, module, scan
 */
async function fetchAgentese<T>(path: string, body?: unknown): Promise<T> {
  // Known node paths for Gestalt
  const NODE_PATHS = ['world.codebase'];

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
// Gestalt Manifest Hook
// =============================================================================

/**
 * Fetch Gestalt health/status manifest.
 * AGENTESE: world.codebase.manifest
 */
export function useGestaltManifest(): QueryResult<WorldCodebaseManifestResponse> {
  const { state, execute } = useAsyncState<WorldCodebaseManifestResponse>();

  const refetch = useCallback(() => {
    execute(fetchAgentese<WorldCodebaseManifestResponse>('world.codebase.manifest'));
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
// Codebase Query Hooks
// =============================================================================

/**
 * Fetch codebase health metrics.
 * AGENTESE: world.codebase.health
 */
export function useCodebaseHealth(
  options?: { enabled?: boolean }
): QueryResult<WorldCodebaseHealthResponse> {
  const { state, execute, reset } = useAsyncState<WorldCodebaseHealthResponse>();
  const enabled = options?.enabled !== false;

  const refetch = useCallback(() => {
    if (!enabled) return;
    execute(fetchAgentese<WorldCodebaseHealthResponse>('world.codebase.health', {}));
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

/**
 * Fetch architecture drift violations.
 * AGENTESE: world.codebase.drift
 */
export function useCodebaseDrift(
  options?: { enabled?: boolean }
): QueryResult<WorldCodebaseDriftResponse> {
  const { state, execute, reset } = useAsyncState<WorldCodebaseDriftResponse>();
  const enabled = options?.enabled !== false;

  const refetch = useCallback(() => {
    if (!enabled) return;
    execute(fetchAgentese<WorldCodebaseDriftResponse>('world.codebase.drift', {}));
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

/**
 * Fetch codebase topology for visualization.
 * AGENTESE: world.codebase.topology
 */
export function useCodebaseTopology(
  options?: { enabled?: boolean; maxNodes?: number; minHealth?: number; role?: string }
): QueryResult<WorldCodebaseTopologyResponse> {
  const { state, execute, reset } = useAsyncState<WorldCodebaseTopologyResponse>();
  const enabled = options?.enabled !== false;

  const refetch = useCallback(() => {
    if (!enabled) return;
    const request: WorldCodebaseTopologyRequest = {
      max_nodes: options?.maxNodes ?? 150,
      min_health: options?.minHealth,
      role: options?.role ?? null,
    };
    execute(fetchAgentese<WorldCodebaseTopologyResponse>('world.codebase.topology', request));
  }, [execute, enabled, options?.maxNodes, options?.minHealth, options?.role]);

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
 * Fetch details for a specific module.
 * AGENTESE: world.codebase.module
 */
export function useCodebaseModule(
  moduleName: string,
  options?: { enabled?: boolean }
): QueryResult<WorldCodebaseModuleResponse> {
  const { state, execute, reset } = useAsyncState<WorldCodebaseModuleResponse>();
  const enabled = options?.enabled !== false && !!moduleName;

  const refetch = useCallback(() => {
    if (!enabled) return;
    const request: WorldCodebaseModuleRequest = { module_name: moduleName };
    execute(fetchAgentese<WorldCodebaseModuleResponse>('world.codebase.module', request));
  }, [execute, moduleName, enabled]);

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
// Codebase Mutation Hooks
// =============================================================================

/**
 * Trigger a codebase rescan.
 * AGENTESE: world.codebase.scan
 */
export function useScanCodebase(): MutationResult<WorldCodebaseScanResponse, WorldCodebaseScanRequest> {
  const { state, execute } = useAsyncState<WorldCodebaseScanResponse>();
  const [isPending, setIsPending] = useState(false);

  const mutateAsync = useCallback(async (data: WorldCodebaseScanRequest = {}) => {
    setIsPending(true);
    try {
      const result = await execute(fetchAgentese<WorldCodebaseScanResponse>('world.codebase.scan', data));
      if (!result) throw new Error('Failed to scan codebase');
      return result;
    } finally {
      setIsPending(false);
    }
  }, [execute]);

  const mutate = useCallback((data: WorldCodebaseScanRequest = {}) => {
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

export const gestaltQueryKeys = {
  all: ['gestalt'] as const,
  manifest: () => [...gestaltQueryKeys.all, 'manifest'] as const,
  health: () => [...gestaltQueryKeys.all, 'health'] as const,
  drift: () => [...gestaltQueryKeys.all, 'drift'] as const,
  topology: (maxNodes?: number) => [...gestaltQueryKeys.all, 'topology', maxNodes] as const,
  module: (name: string) => [...gestaltQueryKeys.all, 'module', name] as const,
};

// =============================================================================
// Re-export types for convenience
// =============================================================================

export type {
  WorldCodebaseManifestResponse,
  WorldCodebaseHealthResponse,
  WorldCodebaseDriftResponse,
  WorldCodebaseTopologyRequest,
  WorldCodebaseTopologyResponse,
  WorldCodebaseModuleRequest,
  WorldCodebaseModuleResponse,
  WorldCodebaseScanRequest,
  WorldCodebaseScanResponse,
};
