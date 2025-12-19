/**
 * Gardener Data Fetching Hooks (AGENTESE Contract-Driven)
 *
 * Hooks for Gardener AGENTESE endpoints using generated contract types.
 * Uses useAsyncState pattern (the project's standard data fetching approach).
 *
 * The 7th Crown Jewel - Development session orchestrator.
 * Implements SENSE -> ACT -> REFLECT polynomial state machine.
 *
 * @see services/gardener/contracts.py - Python contract definitions
 * @see api/types/_generated/concept-gardener.ts - Generated TypeScript types
 * @see docs/skills/crown-jewel-patterns.md - Pattern: Contract-First Integration
 */

import { useEffect, useCallback, useState } from 'react';
import { apiClient } from '../api/client';
import { useAsyncState } from './useAsyncState';
import type {
  // Manifest
  ConceptGardenerManifestResponse,
  // Session
  ConceptGardenerSessionManifestResponse,
  ConceptGardenerSessionDefineRequest,
  ConceptGardenerSessionDefineResponse,
  ConceptGardenerSessionAdvanceRequest,
  ConceptGardenerSessionAdvanceResponse,
  // Polynomial
  ConceptGardenerSessionPolynomialResponse,
  // Sessions list
  ConceptGardenerSessionsManifestResponse,
  // Route
  ConceptGardenerRouteRequest,
  ConceptGardenerRouteResponse,
  // Propose
  ConceptGardenerProposeResponse,
} from '../api/types/_generated/concept-gardener';

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
 * Node path: concept.gardener
 * Aspects: manifest, session.manifest, session.define, session.advance,
 *          session.polynomial, sessions.manifest, route, propose
 */
async function fetchAgentese<T>(path: string, body?: unknown): Promise<T> {
  // Known node paths for Gardener
  const NODE_PATHS = ['concept.gardener'];

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
// Gardener Query Hooks
// =============================================================================

/**
 * Fetch Gardener health/status manifest.
 * AGENTESE: concept.gardener.manifest
 */
export function useGardenerManifest(): QueryResult<ConceptGardenerManifestResponse> {
  const { state, execute } = useAsyncState<ConceptGardenerManifestResponse>();

  const refetch = useCallback(() => {
    execute(fetchAgentese<ConceptGardenerManifestResponse>('concept.gardener.manifest'));
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
 * Fetch active session status.
 * AGENTESE: concept.gardener.session.manifest
 */
export function useGardenerSession(
  options?: { enabled?: boolean }
): QueryResult<ConceptGardenerSessionManifestResponse> {
  const { state, execute, reset } = useAsyncState<ConceptGardenerSessionManifestResponse>();
  const enabled = options?.enabled !== false;

  const refetch = useCallback(() => {
    if (!enabled) return;
    execute(fetchAgentese<ConceptGardenerSessionManifestResponse>('concept.gardener.session.manifest', {}));
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
 * Fetch full polynomial state visualization.
 * AGENTESE: concept.gardener.session.polynomial
 */
export function useGardenerPolynomial(
  options?: { enabled?: boolean }
): QueryResult<ConceptGardenerSessionPolynomialResponse> {
  const { state, execute, reset } = useAsyncState<ConceptGardenerSessionPolynomialResponse>();
  const enabled = options?.enabled !== false;

  const refetch = useCallback(() => {
    if (!enabled) return;
    execute(fetchAgentese<ConceptGardenerSessionPolynomialResponse>('concept.gardener.session.polynomial', {}));
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
 * Fetch list of recent sessions.
 * AGENTESE: concept.gardener.sessions.manifest
 */
export function useGardenerSessions(
  options?: { enabled?: boolean }
): QueryResult<ConceptGardenerSessionsManifestResponse> {
  const { state, execute, reset } = useAsyncState<ConceptGardenerSessionsManifestResponse>();
  const enabled = options?.enabled !== false;

  const refetch = useCallback(() => {
    if (!enabled) return;
    execute(fetchAgentese<ConceptGardenerSessionsManifestResponse>('concept.gardener.sessions.manifest', {}));
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
 * Fetch proactive suggestions for what to do next.
 * AGENTESE: concept.gardener.propose
 */
export function useGardenerPropose(
  options?: { enabled?: boolean }
): QueryResult<ConceptGardenerProposeResponse> {
  const { state, execute, reset } = useAsyncState<ConceptGardenerProposeResponse>();
  const enabled = options?.enabled !== false;

  const refetch = useCallback(() => {
    if (!enabled) return;
    execute(fetchAgentese<ConceptGardenerProposeResponse>('concept.gardener.propose', {}));
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
// Gardener Mutation Hooks
// =============================================================================

/**
 * Start a new gardening session.
 * AGENTESE: concept.gardener.session.define
 */
export function useDefineSession(): MutationResult<ConceptGardenerSessionDefineResponse, ConceptGardenerSessionDefineRequest> {
  const { state, execute } = useAsyncState<ConceptGardenerSessionDefineResponse>();
  const [isPending, setIsPending] = useState(false);

  const mutateAsync = useCallback(async (data: ConceptGardenerSessionDefineRequest) => {
    setIsPending(true);
    try {
      const result = await execute(fetchAgentese<ConceptGardenerSessionDefineResponse>('concept.gardener.session.define', data));
      if (!result) throw new Error('Failed to define session');
      return result;
    } finally {
      setIsPending(false);
    }
  }, [execute]);

  const mutate = useCallback((data: ConceptGardenerSessionDefineRequest) => {
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
 * Advance session to next phase.
 * AGENTESE: concept.gardener.session.advance
 */
export function useAdvanceSession(): MutationResult<ConceptGardenerSessionAdvanceResponse, ConceptGardenerSessionAdvanceRequest> {
  const { state, execute } = useAsyncState<ConceptGardenerSessionAdvanceResponse>();
  const [isPending, setIsPending] = useState(false);

  const mutateAsync = useCallback(async (data: ConceptGardenerSessionAdvanceRequest = {}) => {
    setIsPending(true);
    try {
      const result = await execute(fetchAgentese<ConceptGardenerSessionAdvanceResponse>('concept.gardener.session.advance', data));
      if (!result) throw new Error('Failed to advance session');
      return result;
    } finally {
      setIsPending(false);
    }
  }, [execute]);

  const mutate = useCallback((data: ConceptGardenerSessionAdvanceRequest = {}) => {
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
 * Route natural language to AGENTESE path.
 * AGENTESE: concept.gardener.route
 */
export function useRouteInput(): MutationResult<ConceptGardenerRouteResponse, ConceptGardenerRouteRequest> {
  const { state, execute } = useAsyncState<ConceptGardenerRouteResponse>();
  const [isPending, setIsPending] = useState(false);

  const mutateAsync = useCallback(async (data: ConceptGardenerRouteRequest) => {
    setIsPending(true);
    try {
      const result = await execute(fetchAgentese<ConceptGardenerRouteResponse>('concept.gardener.route', data));
      if (!result) throw new Error('Failed to route input');
      return result;
    } finally {
      setIsPending(false);
    }
  }, [execute]);

  const mutate = useCallback((data: ConceptGardenerRouteRequest) => {
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

export const gardenerQueryKeys = {
  all: ['gardener'] as const,
  manifest: () => [...gardenerQueryKeys.all, 'manifest'] as const,
  session: () => [...gardenerQueryKeys.all, 'session'] as const,
  polynomial: () => [...gardenerQueryKeys.all, 'polynomial'] as const,
  sessions: () => [...gardenerQueryKeys.all, 'sessions'] as const,
  propose: () => [...gardenerQueryKeys.all, 'propose'] as const,
};

// =============================================================================
// Re-export types for convenience
// =============================================================================

export type {
  ConceptGardenerManifestResponse,
  ConceptGardenerSessionManifestResponse,
  ConceptGardenerSessionDefineRequest,
  ConceptGardenerSessionDefineResponse,
  ConceptGardenerSessionAdvanceRequest,
  ConceptGardenerSessionAdvanceResponse,
  ConceptGardenerSessionPolynomialResponse,
  ConceptGardenerSessionsManifestResponse,
  ConceptGardenerRouteRequest,
  ConceptGardenerRouteResponse,
  ConceptGardenerProposeResponse,
};
