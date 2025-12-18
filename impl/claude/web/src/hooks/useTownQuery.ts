/**
 * Town Data Fetching Hooks (AGENTESE Contract-Driven)
 *
 * Hooks for Town AGENTESE endpoints using generated contract types.
 * Uses useAsyncState pattern (the project's standard data fetching approach).
 * These are for REST API calls (point-in-time data fetching).
 * For real-time streaming, use useTownStreamWidget.
 *
 * @see services/town/contracts.py - Python contract definitions
 * @see api/types/_generated/world-town.ts - Generated TypeScript types
 * @see docs/skills/crown-jewel-patterns.md - Pattern: Contract-First Integration
 */

import { useEffect, useCallback, useState } from 'react';
import { apiClient } from '../api/client';
import { useAsyncState } from './useAsyncState';
import type {
  // Town manifest
  WorldTownManifestResponse,
  // Citizen types
  WorldTownCitizenListResponse,
  WorldTownCitizenGetResponse,
  WorldTownCitizenCreateRequest,
  WorldTownCitizenCreateResponse,
  WorldTownCitizenUpdateRequest,
  WorldTownCitizenUpdateResponse,
  // Conversation types
  WorldTownConverseRequest,
  WorldTownConverseResponse,
  WorldTownTurnRequest,
  WorldTownTurnResponse,
  WorldTownHistoryRequest,
  WorldTownHistoryResponse,
  // Relationship types
  WorldTownRelationshipsRequest,
  WorldTownRelationshipsResponse,
} from '../api/types/_generated/world-town';
import type {
  // Coalition types
  WorldTownCoalitionManifestResponse,
  WorldTownCoalitionListResponse,
  WorldTownCoalitionGetResponse,
  WorldTownCoalitionDetectRequest,
  WorldTownCoalitionDetectResponse,
  WorldTownCoalitionBridgesResponse,
  WorldTownCoalitionDecayResponse,
} from '../api/types/_generated/world-town-coalition';

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
 * Node paths are registered at specific levels (e.g., "world.town").
 * Aspects can be simple ("manifest") or compound ("citizen.list").
 *
 * For "world.town.citizen.list":
 * - Node is at "world.town"
 * - Aspect is "citizen.list" (compound)
 * - URL: POST /agentese/world/town/citizen.list
 *
 * @param path - AGENTESE path (e.g., "world.town.citizen.list")
 * @param body - Request body for POST requests
 * @param observer - Observer umwelt for observer-dependent rendering (Phase 3)
 */
async function fetchAgentese<T>(path: string, body?: unknown, observer?: string): Promise<T> {
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
    aspect = parts.pop()!;
    nodePath = parts.join('.');
  }

  const urlPath = nodePath.replace(/\./g, '/');

  // Build headers (observer-dependent rendering)
  const headers: Record<string, string> = {};
  if (observer && observer !== 'default') {
    headers['X-Observer-Archetype'] = observer;
  }

  // Only manifest and affordances are GET, everything else is POST
  if (aspect === 'manifest' || aspect === 'affordances') {
    const response = await apiClient.get<AgenteseResponse<T>>(
      `/agentese/${urlPath}/${aspect}`,
      { headers }
    );
    if (response.data.error) {
      throw new Error(response.data.error);
    }
    return response.data.result;
  } else {
    // All other aspects require POST (even without body)
    // Compound aspects like "citizen.list" stay as-is in the URL
    const response = await apiClient.post<AgenteseResponse<T>>(
      `/agentese/${urlPath}/${aspect}`,
      body ?? {},
      { headers }
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
// Town Manifest Hook
// =============================================================================

/**
 * Fetch Town health/status manifest.
 * AGENTESE: world.town.manifest
 */
export function useTownManifest(): QueryResult<WorldTownManifestResponse> {
  const { state, execute } = useAsyncState<WorldTownManifestResponse>();

  const refetch = useCallback(() => {
    execute(fetchAgentese<WorldTownManifestResponse>('world.town.manifest'));
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
// Citizen Hooks
// =============================================================================

/**
 * Fetch list of all citizens.
 * AGENTESE: world.town.citizen.list
 */
export function useCitizens(): QueryResult<WorldTownCitizenListResponse> {
  const { state, execute } = useAsyncState<WorldTownCitizenListResponse>();

  const refetch = useCallback(() => {
    execute(fetchAgentese<WorldTownCitizenListResponse>('world.town.citizen.list'));
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
 * Fetch single citizen details.
 * AGENTESE: world.town.citizen.get
 */
export function useCitizen(
  citizenId: string,
  options?: { enabled?: boolean }
): QueryResult<WorldTownCitizenGetResponse> {
  const { state, execute, reset } = useAsyncState<WorldTownCitizenGetResponse>();
  const enabled = options?.enabled !== false && !!citizenId;

  const refetch = useCallback(() => {
    if (!enabled) return;
    execute(fetchAgentese<WorldTownCitizenGetResponse>('world.town.citizen.get', { citizen_id: citizenId }));
  }, [execute, citizenId, enabled]);

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
 * Create a new citizen.
 * AGENTESE: world.town.citizen.create
 */
export function useCreateCitizen(): MutationResult<WorldTownCitizenCreateResponse, WorldTownCitizenCreateRequest> {
  const { state, execute } = useAsyncState<WorldTownCitizenCreateResponse>();
  const [isPending, setIsPending] = useState(false);

  const mutateAsync = useCallback(async (data: WorldTownCitizenCreateRequest) => {
    setIsPending(true);
    try {
      const result = await execute(fetchAgentese<WorldTownCitizenCreateResponse>('world.town.citizen.create', data));
      if (!result) throw new Error('Failed to create citizen');
      return result;
    } finally {
      setIsPending(false);
    }
  }, [execute]);

  const mutate = useCallback((data: WorldTownCitizenCreateRequest) => {
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
 * Update an existing citizen.
 * AGENTESE: world.town.citizen.update
 */
export function useUpdateCitizen(): MutationResult<WorldTownCitizenUpdateResponse, WorldTownCitizenUpdateRequest> {
  const { state, execute } = useAsyncState<WorldTownCitizenUpdateResponse>();
  const [isPending, setIsPending] = useState(false);

  const mutateAsync = useCallback(async (data: WorldTownCitizenUpdateRequest) => {
    setIsPending(true);
    try {
      const result = await execute(fetchAgentese<WorldTownCitizenUpdateResponse>('world.town.citizen.update', data));
      if (!result) throw new Error('Failed to update citizen');
      return result;
    } finally {
      setIsPending(false);
    }
  }, [execute]);

  const mutate = useCallback((data: WorldTownCitizenUpdateRequest) => {
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
// Relationship Hooks
// =============================================================================

/**
 * Fetch relationships for a citizen.
 * AGENTESE: world.town.relationship.list
 */
export function useCitizenRelationships(
  citizenId: string,
  options?: { enabled?: boolean }
): QueryResult<WorldTownRelationshipsResponse> {
  const { state, execute, reset } = useAsyncState<WorldTownRelationshipsResponse>();
  const enabled = options?.enabled !== false && !!citizenId;

  const refetch = useCallback(() => {
    if (!enabled) return;
    const request: WorldTownRelationshipsRequest = { citizen_id: citizenId };
    execute(fetchAgentese<WorldTownRelationshipsResponse>('world.town.relationship.list', request));
  }, [execute, citizenId, enabled]);

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
// Conversation Hooks
// =============================================================================

/**
 * Fetch conversation history for a citizen.
 * AGENTESE: world.town.conversation.history
 */
export function useConversationHistory(
  citizenId: string,
  options?: { enabled?: boolean; limit?: number }
): QueryResult<WorldTownHistoryResponse> {
  const { state, execute, reset } = useAsyncState<WorldTownHistoryResponse>();
  const enabled = options?.enabled !== false && !!citizenId;

  const refetch = useCallback(() => {
    if (!enabled) return;
    const request: WorldTownHistoryRequest = {
      citizen_id: citizenId,
      limit: options?.limit ?? 50,
    };
    execute(fetchAgentese<WorldTownHistoryResponse>('world.town.conversation.history', request));
  }, [execute, citizenId, enabled, options?.limit]);

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
 * Start a conversation with a citizen.
 * AGENTESE: world.town.conversation.converse
 */
export function useStartConversation(): MutationResult<WorldTownConverseResponse, WorldTownConverseRequest> {
  const { state, execute } = useAsyncState<WorldTownConverseResponse>();
  const [isPending, setIsPending] = useState(false);

  const mutateAsync = useCallback(async (data: WorldTownConverseRequest) => {
    setIsPending(true);
    try {
      const result = await execute(fetchAgentese<WorldTownConverseResponse>('world.town.conversation.converse', data));
      if (!result) throw new Error('Failed to start conversation');
      return result;
    } finally {
      setIsPending(false);
    }
  }, [execute]);

  const mutate = useCallback((data: WorldTownConverseRequest) => {
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
 * Add a turn to a conversation.
 * AGENTESE: world.town.conversation.turn
 */
export function useAddTurn(): MutationResult<WorldTownTurnResponse, WorldTownTurnRequest> {
  const { state, execute } = useAsyncState<WorldTownTurnResponse>();
  const [isPending, setIsPending] = useState(false);

  const mutateAsync = useCallback(async (data: WorldTownTurnRequest) => {
    setIsPending(true);
    try {
      const result = await execute(fetchAgentese<WorldTownTurnResponse>('world.town.conversation.turn', data));
      if (!result) throw new Error('Failed to add turn');
      return result;
    } finally {
      setIsPending(false);
    }
  }, [execute]);

  const mutate = useCallback((data: WorldTownTurnRequest) => {
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
// Coalition Hooks
// =============================================================================

/**
 * Fetch coalition system manifest/health.
 * AGENTESE: world.town.coalition.manifest
 */
export function useCoalitionManifest(): QueryResult<WorldTownCoalitionManifestResponse> {
  const { state, execute } = useAsyncState<WorldTownCoalitionManifestResponse>();

  const refetch = useCallback(() => {
    execute(fetchAgentese<WorldTownCoalitionManifestResponse>('world.town.coalition.manifest'));
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
 * Fetch list of all coalitions.
 * AGENTESE: world.town.coalition.list
 */
export function useCoalitions(): QueryResult<WorldTownCoalitionListResponse> {
  const { state, execute } = useAsyncState<WorldTownCoalitionListResponse>();

  const refetch = useCallback(() => {
    execute(fetchAgentese<WorldTownCoalitionListResponse>('world.town.coalition.list'));
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
 * Fetch single coalition details.
 * AGENTESE: world.town.coalition.get
 */
export function useCoalition(
  coalitionId: string,
  options?: { enabled?: boolean }
): QueryResult<WorldTownCoalitionGetResponse> {
  const { state, execute, reset } = useAsyncState<WorldTownCoalitionGetResponse>();
  const enabled = options?.enabled !== false && !!coalitionId;

  const refetch = useCallback(() => {
    if (!enabled) return;
    execute(fetchAgentese<WorldTownCoalitionGetResponse>('world.town.coalition.get', { coalition_id: coalitionId }));
  }, [execute, coalitionId, enabled]);

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
 * Fetch bridge citizens (those in multiple coalitions).
 * AGENTESE: world.town.coalition.bridges
 */
export function useCoalitionBridges(): QueryResult<WorldTownCoalitionBridgesResponse> {
  const { state, execute } = useAsyncState<WorldTownCoalitionBridgesResponse>();

  const refetch = useCallback(() => {
    execute(fetchAgentese<WorldTownCoalitionBridgesResponse>('world.town.coalition.bridges'));
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
 * Detect coalitions in the citizen graph.
 * AGENTESE: world.town.coalition.detect
 */
export function useDetectCoalitions(): MutationResult<WorldTownCoalitionDetectResponse, WorldTownCoalitionDetectRequest> {
  const { state, execute } = useAsyncState<WorldTownCoalitionDetectResponse>();
  const [isPending, setIsPending] = useState(false);

  const mutateAsync = useCallback(async (data: WorldTownCoalitionDetectRequest = {}) => {
    setIsPending(true);
    try {
      const result = await execute(fetchAgentese<WorldTownCoalitionDetectResponse>('world.town.coalition.detect', data));
      if (!result) throw new Error('Failed to detect coalitions');
      return result;
    } finally {
      setIsPending(false);
    }
  }, [execute]);

  const mutate = useCallback((data: WorldTownCoalitionDetectRequest = {}) => {
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
 * Apply decay to coalitions (prune weak ones).
 * AGENTESE: world.town.coalition.decay
 */
export function useCoalitionDecay(): MutationResult<WorldTownCoalitionDecayResponse, void> {
  const { state, execute } = useAsyncState<WorldTownCoalitionDecayResponse>();
  const [isPending, setIsPending] = useState(false);

  const mutateAsync = useCallback(async () => {
    setIsPending(true);
    try {
      const result = await execute(fetchAgentese<WorldTownCoalitionDecayResponse>('world.town.coalition.decay', {}));
      if (!result) throw new Error('Failed to apply decay');
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

export const townQueryKeys = {
  all: ['town'] as const,
  manifest: () => [...townQueryKeys.all, 'manifest'] as const,
  citizens: () => [...townQueryKeys.all, 'citizens'] as const,
  citizensList: () => [...townQueryKeys.citizens(), 'list'] as const,
  citizenDetail: (id: string) => [...townQueryKeys.citizens(), 'detail', id] as const,
  relationships: (citizenId: string) => [...townQueryKeys.all, 'relationships', citizenId] as const,
  conversations: () => [...townQueryKeys.all, 'conversations'] as const,
  conversationHistory: (citizenId: string) => [...townQueryKeys.conversations(), 'history', citizenId] as const,
  coalitions: () => [...townQueryKeys.all, 'coalitions'] as const,
  coalitionsList: () => [...townQueryKeys.coalitions(), 'list'] as const,
  coalitionDetail: (id: string) => [...townQueryKeys.coalitions(), 'detail', id] as const,
  coalitionManifest: () => [...townQueryKeys.coalitions(), 'manifest'] as const,
  coalitionBridges: () => [...townQueryKeys.coalitions(), 'bridges'] as const,
};

// =============================================================================
// Exports
// =============================================================================

export type {
  WorldTownManifestResponse,
  WorldTownCitizenListResponse,
  WorldTownCitizenGetResponse,
  WorldTownCitizenCreateRequest,
  WorldTownCitizenCreateResponse,
  WorldTownCitizenUpdateRequest,
  WorldTownCitizenUpdateResponse,
  WorldTownConverseRequest,
  WorldTownConverseResponse,
  WorldTownTurnRequest,
  WorldTownTurnResponse,
  WorldTownHistoryRequest,
  WorldTownHistoryResponse,
  WorldTownRelationshipsRequest,
  WorldTownRelationshipsResponse,
  WorldTownCoalitionManifestResponse,
  WorldTownCoalitionListResponse,
  WorldTownCoalitionGetResponse,
  WorldTownCoalitionDetectRequest,
  WorldTownCoalitionDetectResponse,
  WorldTownCoalitionBridgesResponse,
  WorldTownCoalitionDecayResponse,
};
