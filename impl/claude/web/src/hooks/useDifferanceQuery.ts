/**
 * Differance Data Fetching Hooks (AGENTESE Contract-Driven)
 *
 * Hooks for Differance Engine AGENTESE endpoints using generated contract types.
 * Uses useAsyncState pattern (the project's standard data fetching approach).
 *
 * The Ghost Heritage Graph: seeing what almost was alongside what is.
 *
 * AGENTESE Paths:
 * - time.differance.manifest  - Engine status
 * - time.differance.heritage  - Build GhostHeritageDAG for an output
 * - time.differance.why       - "Why did this happen?" (the crown jewel!)
 * - time.differance.ghosts    - List all unexplored alternatives
 * - time.differance.at        - Navigate to specific trace
 * - time.differance.replay    - Re-execute from trace point
 *
 * Branch Paths:
 * - time.branch.manifest - View active branches
 * - time.branch.create   - Create speculative branch
 * - time.branch.explore  - Execute a ghost alternative
 * - time.branch.compare  - Side-by-side comparison
 *
 * @see agents/differance/contracts.py - Python contract definitions
 * @see spec/protocols/differance.md - The specification
 * @see plans/differance-cultivation.md - Phase 5: FRUITING
 */

import { useEffect, useCallback, useState } from 'react';
import { apiClient } from '../api/client';
import { useAsyncState } from './useAsyncState';

// =============================================================================
// Type Definitions (Mirror Python contracts)
// =============================================================================

// --- Recent Traces Types ---

export interface RecentTracesRequest {
  limit?: number;
  jewel_filter?: string;
}

export interface TracePreview {
  id: string;
  operation: string;
  context: string;
  timestamp: string;
  ghost_count: number;
  output_preview?: string;
  jewel?: string;
}

export interface RecentTracesResponse {
  traces: TracePreview[];
  total: number;
  buffer_size: number;
  store_connected: boolean;
}

// --- Manifest Types ---

export interface DifferanceManifestResponse {
  trace_count: number;
  store_connected: boolean;
  monoid_available: boolean;
  route: string;
}

export interface BranchManifestResponse {
  branch_count: number;
  branch_ids: string[];
}

// --- Heritage Types (the crown jewel) ---

export interface HeritageRequest {
  output_id: string;
  depth?: number;
}

export interface HeritageNodeResponse {
  id: string;
  type: 'chosen' | 'ghost' | 'deferred' | 'spec' | 'impl';
  operation: string;
  timestamp: string;
  depth: number;
  output?: unknown;
  reason?: string;
  explorable: boolean;
  inputs: string[];
}

export interface HeritageEdgeResponse {
  source: string;
  target: string;
  type: 'produced' | 'ghosted' | 'deferred' | 'concretized';
}

export interface HeritageResponse {
  output_id: string;
  root_id: string;
  chosen_path: string[];
  ghost_paths: string[][];
  node_count: number;
  edge_count: number;
  max_depth: number;
  nodes: Record<string, HeritageNodeResponse>;
  edges: HeritageEdgeResponse[];
}

// --- Why Types (explainability) ---

export interface WhyRequest {
  output_id: string;
  format?: 'summary' | 'full' | 'cli';
}

export interface WhyChosenStep {
  id: string;
  operation: string;
  inputs: string[];
  output?: unknown;
  ghosts: Array<{
    operation: string;
    reason: string;
    explorable: boolean;
  }>;
}

export interface WhyResponse {
  output_id: string;
  lineage_length: number;
  decisions_made: number;
  alternatives_considered: number;
  summary?: string;
  cli_output?: string;
  chosen_path?: WhyChosenStep[];
  error?: string;
}

// --- Ghosts Types ---

export interface GhostsRequest {
  explorable_only?: boolean;
  limit?: number;
}

export interface GhostItem {
  operation: string;
  inputs: string[];
  reason_rejected: string;
  could_revisit: boolean;
}

export interface GhostsResponse {
  ghosts: GhostItem[];
  count: number;
  explorable_only: boolean;
}

// --- At (Navigate) Types ---

export interface AtRequest {
  trace_id: string;
}

export interface AtAlternative {
  operation: string;
  inputs: string[];
  reason: string;
  could_revisit: boolean;
}

export interface AtResponse {
  trace_id: string;
  timestamp: string;
  operation: string;
  inputs: string[];
  output: unknown;
  context: string;
  alternatives: AtAlternative[];
  parent_trace_id: string | null;
  positions_before: Record<string, string[]>;
  positions_after: Record<string, string[]>;
}

// --- Replay Types ---

export interface ReplayRequest {
  from_id: string;
  include_ghosts?: boolean;
}

export interface ReplayStep {
  trace_id: string;
  operation: string;
  inputs: string[];
  output: unknown;
  context: string;
  alternatives?: Array<{
    operation: string;
    reason: string;
    explorable: boolean;
  }>;
}

export interface ReplayResponse {
  from_id: string;
  steps: ReplayStep[];
  step_count: number;
}

// --- Branch Types ---

export interface BranchCreateRequest {
  from_trace_id: string;
  name?: string;
  hypothesis?: string;
}

export interface BranchCreateResponse {
  branch_id: string;
  name: string;
  from_trace_id: string;
  status: string;
}

export interface BranchExploreRequest {
  ghost_id: string;
  branch_id?: string;
}

export interface BranchExploreResponse {
  ghost_id: string;
  branch_id: string | null;
  status: string;
  note: string;
}

export interface BranchCompareRequest {
  a: string;
  b: string;
}

export interface BranchCompareResponse {
  a: string;
  b: string;
  a_info: Record<string, unknown> | null;
  b_info: Record<string, unknown> | null;
  comparison: Record<string, unknown>;
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

/**
 * Fetch from AGENTESE gateway.
 *
 * Gateway routing rules:
 * - GET  /{path}/manifest - manifest aspect only
 * - POST /{path}/{aspect} - all other aspects
 *
 * Node paths: time.differance, time.branch
 */
async function fetchAgentese<T>(path: string, body?: unknown): Promise<T> {
  // Known node paths for Differance
  const NODE_PATHS = ['time.differance', 'time.branch'];

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
    const response = await apiClient.get<AgenteseResponse<T>>(`/agentese/${urlPath}/${aspect}`);
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
// Differance Query Hooks
// =============================================================================

/**
 * Fetch Differance Engine status manifest.
 * AGENTESE: time.differance.manifest
 */
export function useDifferanceManifest(): QueryResult<DifferanceManifestResponse> {
  const { state, execute } = useAsyncState<DifferanceManifestResponse>();

  const refetch = useCallback(() => {
    execute(fetchAgentese<DifferanceManifestResponse>('time.differance.manifest'));
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
 * Fetch recent traces from buffer/store.
 * AGENTESE: time.differance.recent
 *
 * Powers the RecentTracesPanel in the Cockpit with real trace data.
 */
export function useRecentTraces(options?: {
  enabled?: boolean;
  limit?: number;
  jewelFilter?: string;
}): QueryResult<RecentTracesResponse> {
  const { state, execute, reset } = useAsyncState<RecentTracesResponse>();
  const enabled = options?.enabled !== false;

  const refetch = useCallback(() => {
    if (!enabled) return;
    const request: RecentTracesRequest = {
      limit: options?.limit ?? 10,
      jewel_filter: options?.jewelFilter,
    };
    execute(fetchAgentese<RecentTracesResponse>('time.differance.recent', request));
  }, [execute, enabled, options?.limit, options?.jewelFilter]);

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
 * Fetch Ghost Heritage DAG for an output.
 * AGENTESE: time.differance.heritage
 *
 * This is the crown jewel visualization data.
 */
export function useHeritageDAG(
  outputId: string,
  options?: { enabled?: boolean; depth?: number }
): QueryResult<HeritageResponse> {
  const { state, execute, reset } = useAsyncState<HeritageResponse>();
  const enabled = options?.enabled !== false && !!outputId;

  const refetch = useCallback(() => {
    if (!enabled) return;
    const request: HeritageRequest = {
      output_id: outputId,
      depth: options?.depth ?? 10,
    };
    execute(fetchAgentese<HeritageResponse>('time.differance.heritage', request));
  }, [execute, outputId, enabled, options?.depth]);

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
 * Fetch "Why did this happen?" explanation.
 * AGENTESE: time.differance.why
 *
 * The key explainability path - shows lineage of decisions.
 */
export function useWhyExplain(
  outputId: string,
  options?: { enabled?: boolean; format?: 'summary' | 'full' | 'cli' }
): QueryResult<WhyResponse> {
  const { state, execute, reset } = useAsyncState<WhyResponse>();
  const enabled = options?.enabled !== false && !!outputId;

  const refetch = useCallback(() => {
    if (!enabled) return;
    const request: WhyRequest = {
      output_id: outputId,
      format: options?.format ?? 'summary',
    };
    execute(fetchAgentese<WhyResponse>('time.differance.why', request));
  }, [execute, outputId, enabled, options?.format]);

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
 * Fetch unexplored alternatives (ghosts).
 * AGENTESE: time.differance.ghosts
 */
export function useGhosts(options?: {
  enabled?: boolean;
  explorableOnly?: boolean;
  limit?: number;
}): QueryResult<GhostsResponse> {
  const { state, execute, reset } = useAsyncState<GhostsResponse>();
  const enabled = options?.enabled !== false;

  const refetch = useCallback(() => {
    if (!enabled) return;
    const request: GhostsRequest = {
      explorable_only: options?.explorableOnly ?? true,
      limit: options?.limit ?? 50,
    };
    execute(fetchAgentese<GhostsResponse>('time.differance.ghosts', request));
  }, [execute, enabled, options?.explorableOnly, options?.limit]);

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
 * Navigate to specific trace.
 * AGENTESE: time.differance.at
 */
export function useTraceAt(
  traceId: string,
  options?: { enabled?: boolean }
): QueryResult<AtResponse> {
  const { state, execute, reset } = useAsyncState<AtResponse>();
  const enabled = options?.enabled !== false && !!traceId;

  const refetch = useCallback(() => {
    if (!enabled) return;
    const request: AtRequest = { trace_id: traceId };
    execute(fetchAgentese<AtResponse>('time.differance.at', request));
  }, [execute, traceId, enabled]);

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
 * Replay from trace point.
 * AGENTESE: time.differance.replay
 */
export function useReplay(
  fromId: string,
  options?: { enabled?: boolean; includeGhosts?: boolean }
): QueryResult<ReplayResponse> {
  const { state, execute, reset } = useAsyncState<ReplayResponse>();
  const enabled = options?.enabled !== false && !!fromId;

  const refetch = useCallback(() => {
    if (!enabled) return;
    const request: ReplayRequest = {
      from_id: fromId,
      include_ghosts: options?.includeGhosts ?? true,
    };
    execute(fetchAgentese<ReplayResponse>('time.differance.replay', request));
  }, [execute, fromId, enabled, options?.includeGhosts]);

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
// Branch Query Hooks
// =============================================================================

/**
 * Fetch branch operations status.
 * AGENTESE: time.branch.manifest
 */
export function useBranchManifest(): QueryResult<BranchManifestResponse> {
  const { state, execute } = useAsyncState<BranchManifestResponse>();

  const refetch = useCallback(() => {
    execute(fetchAgentese<BranchManifestResponse>('time.branch.manifest'));
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
// Branch Mutation Hooks
// =============================================================================

/**
 * Create speculative branch.
 * AGENTESE: time.branch.create
 */
export function useCreateBranch(): MutationResult<BranchCreateResponse, BranchCreateRequest> {
  const { state, execute } = useAsyncState<BranchCreateResponse>();
  const [isPending, setIsPending] = useState(false);

  const mutateAsync = useCallback(
    async (data: BranchCreateRequest) => {
      setIsPending(true);
      try {
        const result = await execute(
          fetchAgentese<BranchCreateResponse>('time.branch.create', data)
        );
        if (!result) throw new Error('Failed to create branch');
        return result;
      } finally {
        setIsPending(false);
      }
    },
    [execute]
  );

  const mutate = useCallback(
    (data: BranchCreateRequest) => {
      mutateAsync(data).catch(() => {});
    },
    [mutateAsync]
  );

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
 * Explore a ghost alternative.
 * AGENTESE: time.branch.explore
 */
export function useExploreBranch(): MutationResult<BranchExploreResponse, BranchExploreRequest> {
  const { state, execute } = useAsyncState<BranchExploreResponse>();
  const [isPending, setIsPending] = useState(false);

  const mutateAsync = useCallback(
    async (data: BranchExploreRequest) => {
      setIsPending(true);
      try {
        const result = await execute(
          fetchAgentese<BranchExploreResponse>('time.branch.explore', data)
        );
        if (!result) throw new Error('Failed to explore ghost');
        return result;
      } finally {
        setIsPending(false);
      }
    },
    [execute]
  );

  const mutate = useCallback(
    (data: BranchExploreRequest) => {
      mutateAsync(data).catch(() => {});
    },
    [mutateAsync]
  );

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
 * Compare two branches.
 * AGENTESE: time.branch.compare
 */
export function useCompareBranches(): MutationResult<BranchCompareResponse, BranchCompareRequest> {
  const { state, execute } = useAsyncState<BranchCompareResponse>();
  const [isPending, setIsPending] = useState(false);

  const mutateAsync = useCallback(
    async (data: BranchCompareRequest) => {
      setIsPending(true);
      try {
        const result = await execute(
          fetchAgentese<BranchCompareResponse>('time.branch.compare', data)
        );
        if (!result) throw new Error('Failed to compare branches');
        return result;
      } finally {
        setIsPending(false);
      }
    },
    [execute]
  );

  const mutate = useCallback(
    (data: BranchCompareRequest) => {
      mutateAsync(data).catch(() => {});
    },
    [mutateAsync]
  );

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

export const differanceQueryKeys = {
  all: ['differance'] as const,
  manifest: () => [...differanceQueryKeys.all, 'manifest'] as const,
  recent: (limit?: number, jewelFilter?: string) =>
    [...differanceQueryKeys.all, 'recent', limit, jewelFilter] as const,
  heritage: (outputId: string) => [...differanceQueryKeys.all, 'heritage', outputId] as const,
  why: (outputId: string) => [...differanceQueryKeys.all, 'why', outputId] as const,
  ghosts: () => [...differanceQueryKeys.all, 'ghosts'] as const,
  at: (traceId: string) => [...differanceQueryKeys.all, 'at', traceId] as const,
  replay: (fromId: string) => [...differanceQueryKeys.all, 'replay', fromId] as const,
};

export const branchQueryKeys = {
  all: ['branch'] as const,
  manifest: () => [...branchQueryKeys.all, 'manifest'] as const,
};
