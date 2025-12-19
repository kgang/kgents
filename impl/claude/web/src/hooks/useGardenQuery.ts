/**
 * Garden Data Fetching Hooks (self.garden.* AGENTESE paths)
 *
 * These hooks fetch garden STATE (plots, seasons, gestures, health).
 * Distinct from useGardenerQuery.ts which handles SESSION orchestration.
 *
 * The relationship:
 * - concept.gardener.* = Session polynomial (SENSE → ACT → REFLECT)
 * - self.garden.* = Garden state (plots, seasons, gestures)
 *
 * The Gardener2D visualization needs BOTH:
 * - GardenJSON from self.garden.manifest (plots, seasons)
 * - GardenerSessionState from concept.gardener.session.manifest (phase, intent)
 *
 * @see protocols/agentese/contexts/garden.py - Backend node
 * @see reactive/types.ts - GardenJSON type definition
 */

import { useEffect, useCallback, useState } from 'react';
import { apiClient } from '../api/client';
import { useAsyncState } from './useAsyncState';
import type { GardenJSON, TransitionSuggestionJSON } from '../reactive/types';

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
 * BasicRendering from backend wraps the actual data in metadata.
 */
interface BasicRenderingResponse {
  summary: string;
  content: string;
  metadata: Record<string, unknown>;
}

/**
 * Fetch from AGENTESE gateway for self.garden.* paths.
 *
 * Gateway routing:
 * - GET  /self/garden/manifest - garden state
 * - POST /self/garden/{aspect} - mutations
 */
async function fetchGarden<T>(aspect: string, body?: unknown): Promise<T> {
  const urlPath = 'self/garden';

  // manifest, season, health are GET; everything else is POST
  if (aspect === 'manifest' || aspect === 'season' || aspect === 'health') {
    const response = await apiClient.get<AgenteseResponse<BasicRenderingResponse>>(
      `/agentese/${urlPath}/${aspect}`
    );
    if (response.data.error) {
      throw new Error(response.data.error);
    }
    // GardenNode returns BasicRendering with GardenJSON in metadata
    return response.data.result.metadata as T;
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
// Garden Query Hooks
// =============================================================================

/**
 * Fetch full garden state including plots, seasons, gestures.
 * AGENTESE: self.garden.manifest
 *
 * Returns GardenJSON - the rich garden structure for Gardener2D visualization.
 */
export function useGardenManifest(): QueryResult<GardenJSON> {
  const { state, execute } = useAsyncState<GardenJSON>();

  const refetch = useCallback(() => {
    execute(fetchGarden<GardenJSON>('manifest'));
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
 * Fetch current season information.
 * AGENTESE: self.garden.season
 */
export interface GardenSeasonResponse {
  name: string;
  emoji: string;
  plasticity: number;
  entropy_multiplier: number;
  since: string;
  description: string;
}

export function useGardenSeason(): QueryResult<GardenSeasonResponse> {
  const { state, execute } = useAsyncState<GardenSeasonResponse>();

  const refetch = useCallback(() => {
    execute(fetchGarden<GardenSeasonResponse>('season'));
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
 * Fetch garden health metrics.
 * AGENTESE: self.garden.health
 */
export interface GardenHealthResponse {
  health_score: number;
  total_prompts: number;
  active_plots: number;
  recent_gestures: number;
  session_cycles: number;
  entropy_spent: number;
  entropy_budget: number;
  entropy_remaining: number;
  health_bar: string;
}

export function useGardenHealth(): QueryResult<GardenHealthResponse> {
  const { state, execute } = useAsyncState<GardenHealthResponse>();

  const refetch = useCallback(() => {
    execute(fetchGarden<GardenHealthResponse>('health'));
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
 * Check for auto-inducer transition suggestion.
 * AGENTESE: self.garden.suggest
 */
export interface GardenSuggestResponse {
  status: 'suggestion' | 'no_suggestion';
  from_season?: string;
  to_season?: string;
  confidence?: number;
  reason?: string;
  signals?: Record<string, unknown>;
  should_suggest?: boolean;
  confidence_bar?: string;
  message?: string;
}

export function useGardenSuggest(
  options?: { enabled?: boolean }
): QueryResult<GardenSuggestResponse> {
  const { state, execute, reset } = useAsyncState<GardenSuggestResponse>();
  const enabled = options?.enabled !== false;

  const refetch = useCallback(() => {
    if (!enabled) return;
    execute(fetchGarden<GardenSuggestResponse>('suggest'));
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
// Garden Mutation Hooks
// =============================================================================

/**
 * Transition garden to a new season.
 * AGENTESE: self.garden.transition
 */
export interface GardenTransitionRequest {
  target: string;
  reason?: string;
}

export interface GardenTransitionResponse {
  status: string;
  from_season: string;
  from_emoji: string;
  to_season: string;
  to_emoji: string;
  reason: string;
  old_plasticity: number;
  new_plasticity: number;
}

export function useGardenTransition(): MutationResult<GardenTransitionResponse, GardenTransitionRequest> {
  const { state, execute } = useAsyncState<GardenTransitionResponse>();
  const [isPending, setIsPending] = useState(false);

  const mutateAsync = useCallback(async (data: GardenTransitionRequest) => {
    setIsPending(true);
    try {
      const result = await execute(fetchGarden<GardenTransitionResponse>('transition', data));
      if (!result) throw new Error('Failed to transition season');
      return result;
    } finally {
      setIsPending(false);
    }
  }, [execute]);

  const mutate = useCallback((data: GardenTransitionRequest) => {
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
 * Accept auto-inducer transition suggestion.
 * AGENTESE: self.garden.accept
 */
export interface GardenAcceptResponse {
  status: string;
  from_season?: string;
  to_season?: string;
  reason?: string;
  message?: string;
}

export function useGardenAccept(): MutationResult<GardenAcceptResponse, void> {
  const { state, execute } = useAsyncState<GardenAcceptResponse>();
  const [isPending, setIsPending] = useState(false);

  const mutateAsync = useCallback(async () => {
    setIsPending(true);
    try {
      const result = await execute(fetchGarden<GardenAcceptResponse>('accept', {}));
      if (!result) throw new Error('Failed to accept transition');
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
 * Dismiss auto-inducer transition suggestion (4h cooldown).
 * AGENTESE: self.garden.dismiss
 */
export interface GardenDismissResponse {
  status: string;
  from_season?: string;
  to_season?: string;
  cooldown_hours?: number;
  message?: string;
}

export function useGardenDismiss(): MutationResult<GardenDismissResponse, void> {
  const { state, execute } = useAsyncState<GardenDismissResponse>();
  const [isPending, setIsPending] = useState(false);

  const mutateAsync = useCallback(async () => {
    setIsPending(true);
    try {
      const result = await execute(fetchGarden<GardenDismissResponse>('dismiss', {}));
      if (!result) throw new Error('Failed to dismiss transition');
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
// Convenience: Transform GardenSuggestResponse to TransitionSuggestionJSON
// =============================================================================

/**
 * Convert backend suggest response to frontend TransitionSuggestionJSON.
 * Handles the shape transformation for Gardener2D.
 */
export function toTransitionSuggestion(
  response: GardenSuggestResponse | null
): TransitionSuggestionJSON | null {
  if (!response || response.status !== 'suggestion' || !response.should_suggest) {
    return null;
  }

  return {
    from_season: response.from_season as TransitionSuggestionJSON['from_season'],
    to_season: response.to_season as TransitionSuggestionJSON['to_season'],
    confidence: response.confidence ?? 0,
    reason: response.reason ?? '',
    signals: {
      gesture_frequency: (response.signals?.gesture_frequency as number) ?? 0,
      gesture_diversity: (response.signals?.gesture_diversity as number) ?? 0,
      plot_progress_delta: (response.signals?.plot_progress_delta as number) ?? 0,
      artifacts_created: (response.signals?.artifacts_created as number) ?? 0,
      time_in_season_hours: (response.signals?.time_in_season_hours as number) ?? 0,
      entropy_spent_ratio: (response.signals?.entropy_spent_ratio as number) ?? 0,
      reflect_count: (response.signals?.reflect_count as number) ?? 0,
      session_active: (response.signals?.session_active as boolean) ?? false,
    },
    triggered_at: new Date().toISOString(),
  };
}

// =============================================================================
// Query Keys (for cache invalidation patterns if needed later)
// =============================================================================

export const gardenQueryKeys = {
  all: ['garden'] as const,
  manifest: () => [...gardenQueryKeys.all, 'manifest'] as const,
  season: () => [...gardenQueryKeys.all, 'season'] as const,
  health: () => [...gardenQueryKeys.all, 'health'] as const,
  suggest: () => [...gardenQueryKeys.all, 'suggest'] as const,
};
