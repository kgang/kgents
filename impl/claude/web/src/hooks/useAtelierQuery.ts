/**
 * Atelier Data Fetching Hooks (AGENTESE Contract-Driven)
 *
 * Hooks for Atelier AGENTESE endpoints using generated contract types.
 * Uses useAsyncState pattern (the project's standard data fetching approach).
 *
 * AGENTESE Path: world.atelier
 * Theme: Orisinal.com aesthetic - whimsical, minimal, melancholic but hopeful.
 *
 * @see services/atelier/contracts.py - Python contract definitions
 * @see api/types/_generated/world-atelier.ts - Generated TypeScript types
 * @see docs/skills/crown-jewel-patterns.md - Pattern 13: Contract-First Types
 */

import { useEffect, useCallback, useState } from 'react';
import { apiClient } from '../api/client';
import { useAsyncState } from './useAsyncState';
import type {
  // Manifest
  WorldAtelierManifestResponse,
  // Workshop types
  WorldAtelierWorkshopListResponse,
  WorldAtelierWorkshopGetRequest,
  WorldAtelierWorkshopGetResponse,
  WorldAtelierWorkshopCreateRequest,
  WorldAtelierWorkshopCreateResponse,
  WorldAtelierWorkshopEndRequest,
  WorldAtelierWorkshopEndResponse,
  // Artisan types
  WorldAtelierArtisanListRequest,
  WorldAtelierArtisanListResponse,
  WorldAtelierArtisanJoinRequest,
  WorldAtelierArtisanJoinResponse,
  // Contribution types
  WorldAtelierContributeRequest,
  WorldAtelierContributeResponse,
  WorldAtelierContributionListResponse,
  // Exhibition types
  WorldAtelierExhibitionCreateRequest,
  WorldAtelierExhibitionCreateResponse,
  WorldAtelierExhibitionOpenRequest,
  WorldAtelierExhibitionOpenResponse,
  WorldAtelierExhibitionViewRequest,
  WorldAtelierExhibitionViewResponse,
  // Gallery types
  WorldAtelierGalleryListRequest,
  WorldAtelierGalleryListResponse,
  WorldAtelierGalleryAddRequest,
  WorldAtelierGalleryAddResponse,
  // Festival types
  WorldAtelierFestivalListResponse,
  WorldAtelierFestivalCreateRequest,
  WorldAtelierFestivalCreateResponse,
  WorldAtelierFestivalEnterRequest,
  WorldAtelierFestivalEnterResponse,
  // Token/Bid types
  WorldAtelierTokensManifestResponse,
  WorldAtelierBidSubmitRequest,
  WorldAtelierBidSubmitResponse,
} from '../api/types/_generated/world-atelier';

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
 * Node path: world.atelier
 * Aspects: workshop.list, artisan.list, contribute, exhibition.*, gallery.*, festival.*
 */
async function fetchAgentese<T>(path: string, body?: unknown): Promise<T> {
  // Known node paths for Atelier
  const NODE_PATHS = [
    'world.atelier.tokens',
    'world.atelier',
  ];

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
// Atelier Manifest Hook
// =============================================================================

/**
 * Fetch Atelier health/status manifest.
 * AGENTESE: world.atelier.manifest
 */
export function useAtelierManifest(): QueryResult<WorldAtelierManifestResponse> {
  const { state, execute } = useAsyncState<WorldAtelierManifestResponse>();

  const refetch = useCallback(() => {
    execute(fetchAgentese<WorldAtelierManifestResponse>('world.atelier.manifest'));
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
// Workshop Hooks
// =============================================================================

/**
 * Fetch list of all workshops.
 * AGENTESE: world.atelier.workshop.list
 */
export function useWorkshops(): QueryResult<WorldAtelierWorkshopListResponse> {
  const { state, execute } = useAsyncState<WorldAtelierWorkshopListResponse>();

  const refetch = useCallback(() => {
    execute(fetchAgentese<WorldAtelierWorkshopListResponse>('world.atelier.workshop.list'));
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
 * Fetch single workshop details.
 * AGENTESE: world.atelier.workshop.get
 */
export function useWorkshop(
  workshopId: string,
  options?: { enabled?: boolean }
): QueryResult<WorldAtelierWorkshopGetResponse> {
  const { state, execute, reset } = useAsyncState<WorldAtelierWorkshopGetResponse>();
  const enabled = options?.enabled !== false && !!workshopId;

  const refetch = useCallback(() => {
    if (!enabled) return;
    const request: WorldAtelierWorkshopGetRequest = { workshop_id: workshopId };
    execute(fetchAgentese<WorldAtelierWorkshopGetResponse>('world.atelier.workshop.get', request));
  }, [execute, workshopId, enabled]);

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
 * Create a new workshop.
 * AGENTESE: world.atelier.workshop.create
 */
export function useCreateWorkshop(): MutationResult<WorldAtelierWorkshopCreateResponse, WorldAtelierWorkshopCreateRequest> {
  const { state, execute } = useAsyncState<WorldAtelierWorkshopCreateResponse>();
  const [isPending, setIsPending] = useState(false);

  const mutateAsync = useCallback(async (data: WorldAtelierWorkshopCreateRequest) => {
    setIsPending(true);
    try {
      const result = await execute(fetchAgentese<WorldAtelierWorkshopCreateResponse>('world.atelier.workshop.create', data));
      if (!result) throw new Error('Failed to create workshop');
      return result;
    } finally {
      setIsPending(false);
    }
  }, [execute]);

  const mutate = useCallback((data: WorldAtelierWorkshopCreateRequest) => {
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
 * End a workshop.
 * AGENTESE: world.atelier.workshop.end
 */
export function useEndWorkshop(): MutationResult<WorldAtelierWorkshopEndResponse, WorldAtelierWorkshopEndRequest> {
  const { state, execute } = useAsyncState<WorldAtelierWorkshopEndResponse>();
  const [isPending, setIsPending] = useState(false);

  const mutateAsync = useCallback(async (data: WorldAtelierWorkshopEndRequest) => {
    setIsPending(true);
    try {
      const result = await execute(fetchAgentese<WorldAtelierWorkshopEndResponse>('world.atelier.workshop.end', data));
      if (!result) throw new Error('Failed to end workshop');
      return result;
    } finally {
      setIsPending(false);
    }
  }, [execute]);

  const mutate = useCallback((data: WorldAtelierWorkshopEndRequest) => {
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
// Artisan Hooks
// =============================================================================

/**
 * Fetch list of artisans in a workshop.
 * AGENTESE: world.atelier.artisan.list
 */
export function useArtisans(
  workshopId: string,
  options?: { enabled?: boolean; specialty?: string; activeOnly?: boolean }
): QueryResult<WorldAtelierArtisanListResponse> {
  const { state, execute, reset } = useAsyncState<WorldAtelierArtisanListResponse>();
  const enabled = options?.enabled !== false && !!workshopId;

  const refetch = useCallback(() => {
    if (!enabled) return;
    const request: WorldAtelierArtisanListRequest = {
      workshop_id: workshopId,
      specialty: options?.specialty,
      active_only: options?.activeOnly ?? true,
    };
    execute(fetchAgentese<WorldAtelierArtisanListResponse>('world.atelier.artisan.list', request));
  }, [execute, workshopId, enabled, options?.specialty, options?.activeOnly]);

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
 * Join a workshop as an artisan.
 * AGENTESE: world.atelier.artisan.join
 */
export function useJoinWorkshop(): MutationResult<WorldAtelierArtisanJoinResponse, WorldAtelierArtisanJoinRequest> {
  const { state, execute } = useAsyncState<WorldAtelierArtisanJoinResponse>();
  const [isPending, setIsPending] = useState(false);

  const mutateAsync = useCallback(async (data: WorldAtelierArtisanJoinRequest) => {
    setIsPending(true);
    try {
      const result = await execute(fetchAgentese<WorldAtelierArtisanJoinResponse>('world.atelier.artisan.join', data));
      if (!result) throw new Error('Failed to join workshop');
      return result;
    } finally {
      setIsPending(false);
    }
  }, [execute]);

  const mutate = useCallback((data: WorldAtelierArtisanJoinRequest) => {
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
// Contribution Hooks
// =============================================================================

/**
 * Submit a contribution.
 * AGENTESE: world.atelier.contribute
 */
export function useContribute(): MutationResult<WorldAtelierContributeResponse, WorldAtelierContributeRequest> {
  const { state, execute } = useAsyncState<WorldAtelierContributeResponse>();
  const [isPending, setIsPending] = useState(false);

  const mutateAsync = useCallback(async (data: WorldAtelierContributeRequest) => {
    setIsPending(true);
    try {
      const result = await execute(fetchAgentese<WorldAtelierContributeResponse>('world.atelier.contribute', data));
      if (!result) throw new Error('Failed to submit contribution');
      return result;
    } finally {
      setIsPending(false);
    }
  }, [execute]);

  const mutate = useCallback((data: WorldAtelierContributeRequest) => {
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
 * Fetch list of contributions.
 * AGENTESE: world.atelier.contribution.list
 */
export function useContributions(options?: {
  artisanId?: string;
  workshopId?: string;
  contributionType?: string;
  limit?: number;
}): QueryResult<WorldAtelierContributionListResponse> {
  const { state, execute } = useAsyncState<WorldAtelierContributionListResponse>();

  const refetch = useCallback(() => {
    execute(fetchAgentese<WorldAtelierContributionListResponse>('world.atelier.contribution.list', {
      artisan_id: options?.artisanId,
      workshop_id: options?.workshopId,
      contribution_type: options?.contributionType,
      limit: options?.limit ?? 50,
    }));
  }, [execute, options?.artisanId, options?.workshopId, options?.contributionType, options?.limit]);

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
// Exhibition Hooks
// =============================================================================

/**
 * Create a new exhibition.
 * AGENTESE: world.atelier.exhibition.create
 */
export function useCreateExhibition(): MutationResult<WorldAtelierExhibitionCreateResponse, WorldAtelierExhibitionCreateRequest> {
  const { state, execute } = useAsyncState<WorldAtelierExhibitionCreateResponse>();
  const [isPending, setIsPending] = useState(false);

  const mutateAsync = useCallback(async (data: WorldAtelierExhibitionCreateRequest) => {
    setIsPending(true);
    try {
      const result = await execute(fetchAgentese<WorldAtelierExhibitionCreateResponse>('world.atelier.exhibition.create', data));
      if (!result) throw new Error('Failed to create exhibition');
      return result;
    } finally {
      setIsPending(false);
    }
  }, [execute]);

  const mutate = useCallback((data: WorldAtelierExhibitionCreateRequest) => {
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
 * Open an exhibition to public viewing.
 * AGENTESE: world.atelier.exhibition.open
 */
export function useOpenExhibition(): MutationResult<WorldAtelierExhibitionOpenResponse, WorldAtelierExhibitionOpenRequest> {
  const { state, execute } = useAsyncState<WorldAtelierExhibitionOpenResponse>();
  const [isPending, setIsPending] = useState(false);

  const mutateAsync = useCallback(async (data: WorldAtelierExhibitionOpenRequest) => {
    setIsPending(true);
    try {
      const result = await execute(fetchAgentese<WorldAtelierExhibitionOpenResponse>('world.atelier.exhibition.open', data));
      if (!result) throw new Error('Failed to open exhibition');
      return result;
    } finally {
      setIsPending(false);
    }
  }, [execute]);

  const mutate = useCallback((data: WorldAtelierExhibitionOpenRequest) => {
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
 * View an exhibition (increments view count).
 * AGENTESE: world.atelier.exhibition.view
 */
export function useViewExhibition(
  exhibitionId: string,
  options?: { enabled?: boolean }
): QueryResult<WorldAtelierExhibitionViewResponse> {
  const { state, execute, reset } = useAsyncState<WorldAtelierExhibitionViewResponse>();
  const enabled = options?.enabled !== false && !!exhibitionId;

  const refetch = useCallback(() => {
    if (!enabled) return;
    const request: WorldAtelierExhibitionViewRequest = { exhibition_id: exhibitionId };
    execute(fetchAgentese<WorldAtelierExhibitionViewResponse>('world.atelier.exhibition.view', request));
  }, [execute, exhibitionId, enabled]);

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
// Gallery Hooks
// =============================================================================

/**
 * Fetch gallery items for an exhibition.
 * AGENTESE: world.atelier.gallery.list
 */
export function useGalleryItems(
  exhibitionId: string,
  options?: { enabled?: boolean }
): QueryResult<WorldAtelierGalleryListResponse> {
  const { state, execute, reset } = useAsyncState<WorldAtelierGalleryListResponse>();
  const enabled = options?.enabled !== false && !!exhibitionId;

  const refetch = useCallback(() => {
    if (!enabled) return;
    const request: WorldAtelierGalleryListRequest = { exhibition_id: exhibitionId };
    execute(fetchAgentese<WorldAtelierGalleryListResponse>('world.atelier.gallery.list', request));
  }, [execute, exhibitionId, enabled]);

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
 * Add item to gallery.
 * AGENTESE: world.atelier.gallery.add
 */
export function useAddToGallery(): MutationResult<WorldAtelierGalleryAddResponse, WorldAtelierGalleryAddRequest> {
  const { state, execute } = useAsyncState<WorldAtelierGalleryAddResponse>();
  const [isPending, setIsPending] = useState(false);

  const mutateAsync = useCallback(async (data: WorldAtelierGalleryAddRequest) => {
    setIsPending(true);
    try {
      const result = await execute(fetchAgentese<WorldAtelierGalleryAddResponse>('world.atelier.gallery.add', data));
      if (!result) throw new Error('Failed to add to gallery');
      return result;
    } finally {
      setIsPending(false);
    }
  }, [execute]);

  const mutate = useCallback((data: WorldAtelierGalleryAddRequest) => {
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
// Festival Hooks
// =============================================================================

/**
 * Fetch list of festivals.
 * AGENTESE: world.atelier.festival.list
 */
export function useFestivals(): QueryResult<WorldAtelierFestivalListResponse> {
  const { state, execute } = useAsyncState<WorldAtelierFestivalListResponse>();

  const refetch = useCallback(() => {
    execute(fetchAgentese<WorldAtelierFestivalListResponse>('world.atelier.festival.list'));
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
 * Create a new festival.
 * AGENTESE: world.atelier.festival.create
 */
export function useCreateFestival(): MutationResult<WorldAtelierFestivalCreateResponse, WorldAtelierFestivalCreateRequest> {
  const { state, execute } = useAsyncState<WorldAtelierFestivalCreateResponse>();
  const [isPending, setIsPending] = useState(false);

  const mutateAsync = useCallback(async (data: WorldAtelierFestivalCreateRequest) => {
    setIsPending(true);
    try {
      const result = await execute(fetchAgentese<WorldAtelierFestivalCreateResponse>('world.atelier.festival.create', data));
      if (!result) throw new Error('Failed to create festival');
      return result;
    } finally {
      setIsPending(false);
    }
  }, [execute]);

  const mutate = useCallback((data: WorldAtelierFestivalCreateRequest) => {
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
 * Enter a festival.
 * AGENTESE: world.atelier.festival.enter
 */
export function useEnterFestival(): MutationResult<WorldAtelierFestivalEnterResponse, WorldAtelierFestivalEnterRequest> {
  const { state, execute } = useAsyncState<WorldAtelierFestivalEnterResponse>();
  const [isPending, setIsPending] = useState(false);

  const mutateAsync = useCallback(async (data: WorldAtelierFestivalEnterRequest) => {
    setIsPending(true);
    try {
      const result = await execute(fetchAgentese<WorldAtelierFestivalEnterResponse>('world.atelier.festival.enter', data));
      if (!result) throw new Error('Failed to enter festival');
      return result;
    } finally {
      setIsPending(false);
    }
  }, [execute]);

  const mutate = useCallback((data: WorldAtelierFestivalEnterRequest) => {
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
// Token/Bid Hooks
// =============================================================================

/**
 * Fetch token balance manifest.
 * AGENTESE: world.atelier.tokens.manifest
 */
export function useTokenBalance(): QueryResult<WorldAtelierTokensManifestResponse> {
  const { state, execute } = useAsyncState<WorldAtelierTokensManifestResponse>();

  const refetch = useCallback(() => {
    execute(fetchAgentese<WorldAtelierTokensManifestResponse>('world.atelier.tokens.manifest'));
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
 * Submit a bid.
 * AGENTESE: world.atelier.bid.submit
 */
export function useSubmitBid(): MutationResult<WorldAtelierBidSubmitResponse, WorldAtelierBidSubmitRequest> {
  const { state, execute } = useAsyncState<WorldAtelierBidSubmitResponse>();
  const [isPending, setIsPending] = useState(false);

  const mutateAsync = useCallback(async (data: WorldAtelierBidSubmitRequest) => {
    setIsPending(true);
    try {
      const result = await execute(fetchAgentese<WorldAtelierBidSubmitResponse>('world.atelier.bid.submit', data));
      if (!result) throw new Error('Failed to submit bid');
      return result;
    } finally {
      setIsPending(false);
    }
  }, [execute]);

  const mutate = useCallback((data: WorldAtelierBidSubmitRequest) => {
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

export const atelierQueryKeys = {
  all: ['atelier'] as const,
  manifest: () => [...atelierQueryKeys.all, 'manifest'] as const,
  workshops: () => [...atelierQueryKeys.all, 'workshops'] as const,
  workshopsList: () => [...atelierQueryKeys.workshops(), 'list'] as const,
  workshopDetail: (id: string) => [...atelierQueryKeys.workshops(), 'detail', id] as const,
  artisans: (workshopId: string) => [...atelierQueryKeys.all, 'artisans', workshopId] as const,
  contributions: () => [...atelierQueryKeys.all, 'contributions'] as const,
  exhibitions: () => [...atelierQueryKeys.all, 'exhibitions'] as const,
  exhibitionDetail: (id: string) => [...atelierQueryKeys.exhibitions(), 'detail', id] as const,
  gallery: (exhibitionId: string) => [...atelierQueryKeys.all, 'gallery', exhibitionId] as const,
  festivals: () => [...atelierQueryKeys.all, 'festivals'] as const,
  tokens: () => [...atelierQueryKeys.all, 'tokens'] as const,
};

// =============================================================================
// Re-export types for convenience
// =============================================================================

export type {
  WorldAtelierManifestResponse,
  WorldAtelierWorkshopListResponse,
  WorldAtelierWorkshopGetRequest,
  WorldAtelierWorkshopGetResponse,
  WorldAtelierWorkshopCreateRequest,
  WorldAtelierWorkshopCreateResponse,
  WorldAtelierWorkshopEndRequest,
  WorldAtelierWorkshopEndResponse,
  WorldAtelierArtisanListRequest,
  WorldAtelierArtisanListResponse,
  WorldAtelierArtisanJoinRequest,
  WorldAtelierArtisanJoinResponse,
  WorldAtelierContributeRequest,
  WorldAtelierContributeResponse,
  WorldAtelierContributionListResponse,
  WorldAtelierExhibitionCreateRequest,
  WorldAtelierExhibitionCreateResponse,
  WorldAtelierExhibitionOpenRequest,
  WorldAtelierExhibitionOpenResponse,
  WorldAtelierExhibitionViewRequest,
  WorldAtelierExhibitionViewResponse,
  WorldAtelierGalleryListRequest,
  WorldAtelierGalleryListResponse,
  WorldAtelierGalleryAddRequest,
  WorldAtelierGalleryAddResponse,
  WorldAtelierFestivalListResponse,
  WorldAtelierFestivalCreateRequest,
  WorldAtelierFestivalCreateResponse,
  WorldAtelierFestivalEnterRequest,
  WorldAtelierFestivalEnterResponse,
  WorldAtelierTokensManifestResponse,
  WorldAtelierBidSubmitRequest,
  WorldAtelierBidSubmitResponse,
};
