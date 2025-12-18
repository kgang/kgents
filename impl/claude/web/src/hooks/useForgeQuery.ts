/**
 * Forge Data Fetching Hooks (AGENTESE Contract-Driven)
 *
 * Hooks for Forge AGENTESE endpoints using generated contract types.
 * Uses useAsyncState pattern (the project's standard data fetching approach).
 *
 * AGENTESE Path: world.forge
 * Theme: Orisinal.com aesthetic - whimsical, minimal, melancholic but hopeful.
 *
 * @see services/atelier/contracts.py - Python contract definitions
 * @see api/types/_generated/world-atelier.ts - Generated TypeScript types
 * @see docs/skills/crown-jewel-patterns.md - Pattern 13: Contract-First Types
 */

import { useEffect, useCallback, useState } from 'react';
import { apiClient } from '../api/client';
import { useAsyncState } from './useAsyncState';
// Import the generated types (still named WorldAtelier*)
// Re-export as WorldForge* aliases for forward compatibility
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

// Type aliases for Forge naming (forward compatibility)
export type WorldForgeManifestResponse = WorldAtelierManifestResponse;
export type WorldForgeWorkshopListResponse = WorldAtelierWorkshopListResponse;
export type WorldForgeWorkshopGetRequest = WorldAtelierWorkshopGetRequest;
export type WorldForgeWorkshopGetResponse = WorldAtelierWorkshopGetResponse;
export type WorldForgeWorkshopCreateRequest = WorldAtelierWorkshopCreateRequest;
export type WorldForgeWorkshopCreateResponse = WorldAtelierWorkshopCreateResponse;
export type WorldForgeWorkshopEndRequest = WorldAtelierWorkshopEndRequest;
export type WorldForgeWorkshopEndResponse = WorldAtelierWorkshopEndResponse;
export type WorldForgeArtisanListRequest = WorldAtelierArtisanListRequest;
export type WorldForgeArtisanListResponse = WorldAtelierArtisanListResponse;
export type WorldForgeArtisanJoinRequest = WorldAtelierArtisanJoinRequest;
export type WorldForgeArtisanJoinResponse = WorldAtelierArtisanJoinResponse;
export type WorldForgeContributeRequest = WorldAtelierContributeRequest;
export type WorldForgeContributeResponse = WorldAtelierContributeResponse;
export type WorldForgeContributionListResponse = WorldAtelierContributionListResponse;
export type WorldForgeExhibitionCreateRequest = WorldAtelierExhibitionCreateRequest;
export type WorldForgeExhibitionCreateResponse = WorldAtelierExhibitionCreateResponse;
export type WorldForgeExhibitionOpenRequest = WorldAtelierExhibitionOpenRequest;
export type WorldForgeExhibitionOpenResponse = WorldAtelierExhibitionOpenResponse;
export type WorldForgeExhibitionViewRequest = WorldAtelierExhibitionViewRequest;
export type WorldForgeExhibitionViewResponse = WorldAtelierExhibitionViewResponse;
export type WorldForgeGalleryListRequest = WorldAtelierGalleryListRequest;
export type WorldForgeGalleryListResponse = WorldAtelierGalleryListResponse;
export type WorldForgeGalleryAddRequest = WorldAtelierGalleryAddRequest;
export type WorldForgeGalleryAddResponse = WorldAtelierGalleryAddResponse;
export type WorldForgeFestivalListResponse = WorldAtelierFestivalListResponse;
export type WorldForgeFestivalCreateRequest = WorldAtelierFestivalCreateRequest;
export type WorldForgeFestivalCreateResponse = WorldAtelierFestivalCreateResponse;
export type WorldForgeFestivalEnterRequest = WorldAtelierFestivalEnterRequest;
export type WorldForgeFestivalEnterResponse = WorldAtelierFestivalEnterResponse;
export type WorldForgeTokensManifestResponse = WorldAtelierTokensManifestResponse;
export type WorldForgeBidSubmitRequest = WorldAtelierBidSubmitRequest;
export type WorldForgeBidSubmitResponse = WorldAtelierBidSubmitResponse;

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
 * Node path: world.forge
 * Aspects: workshop.list, artisan.list, contribute, exhibition.*, gallery.*, festival.*
 */
async function fetchAgentese<T>(path: string, body?: unknown): Promise<T> {
  // Known node paths for Atelier
  const NODE_PATHS = ['world.forge.tokens', 'world.forge'];

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
// Forge Manifest Hook
// =============================================================================

/**
 * Fetch Forge health/status manifest.
 * AGENTESE: world.forge.manifest
 */
export function useForgeManifest(): QueryResult<WorldForgeManifestResponse> {
  const { state, execute } = useAsyncState<WorldForgeManifestResponse>();

  const refetch = useCallback(() => {
    execute(fetchAgentese<WorldForgeManifestResponse>('world.forge.manifest'));
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
 * AGENTESE: world.forge.workshop.list
 */
export function useWorkshops(): QueryResult<WorldForgeWorkshopListResponse> {
  const { state, execute } = useAsyncState<WorldForgeWorkshopListResponse>();

  const refetch = useCallback(() => {
    execute(fetchAgentese<WorldForgeWorkshopListResponse>('world.forge.workshop.list'));
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
 * AGENTESE: world.forge.workshop.get
 */
export function useWorkshop(
  workshopId: string,
  options?: { enabled?: boolean }
): QueryResult<WorldForgeWorkshopGetResponse> {
  const { state, execute, reset } = useAsyncState<WorldForgeWorkshopGetResponse>();
  const enabled = options?.enabled !== false && !!workshopId;

  const refetch = useCallback(() => {
    if (!enabled) return;
    const request: WorldForgeWorkshopGetRequest = { workshop_id: workshopId };
    execute(fetchAgentese<WorldForgeWorkshopGetResponse>('world.forge.workshop.get', request));
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
 * AGENTESE: world.forge.workshop.create
 */
export function useCreateWorkshop(): MutationResult<
  WorldForgeWorkshopCreateResponse,
  WorldForgeWorkshopCreateRequest
> {
  const { state, execute } = useAsyncState<WorldForgeWorkshopCreateResponse>();
  const [isPending, setIsPending] = useState(false);

  const mutateAsync = useCallback(
    async (data: WorldForgeWorkshopCreateRequest) => {
      setIsPending(true);
      try {
        const result = await execute(
          fetchAgentese<WorldForgeWorkshopCreateResponse>('world.forge.workshop.create', data)
        );
        if (!result) throw new Error('Failed to create workshop');
        return result;
      } finally {
        setIsPending(false);
      }
    },
    [execute]
  );

  const mutate = useCallback(
    (data: WorldForgeWorkshopCreateRequest) => {
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
 * End a workshop.
 * AGENTESE: world.forge.workshop.end
 */
export function useEndWorkshop(): MutationResult<
  WorldForgeWorkshopEndResponse,
  WorldForgeWorkshopEndRequest
> {
  const { state, execute } = useAsyncState<WorldForgeWorkshopEndResponse>();
  const [isPending, setIsPending] = useState(false);

  const mutateAsync = useCallback(
    async (data: WorldForgeWorkshopEndRequest) => {
      setIsPending(true);
      try {
        const result = await execute(
          fetchAgentese<WorldForgeWorkshopEndResponse>('world.forge.workshop.end', data)
        );
        if (!result) throw new Error('Failed to end workshop');
        return result;
      } finally {
        setIsPending(false);
      }
    },
    [execute]
  );

  const mutate = useCallback(
    (data: WorldForgeWorkshopEndRequest) => {
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
// Artisan Hooks
// =============================================================================

/**
 * Fetch list of artisans in a workshop.
 * AGENTESE: world.forge.artisan.list
 */
export function useArtisans(
  workshopId: string,
  options?: { enabled?: boolean; specialty?: string; activeOnly?: boolean }
): QueryResult<WorldForgeArtisanListResponse> {
  const { state, execute, reset } = useAsyncState<WorldForgeArtisanListResponse>();
  const enabled = options?.enabled !== false && !!workshopId;

  const refetch = useCallback(() => {
    if (!enabled) return;
    const request: WorldForgeArtisanListRequest = {
      workshop_id: workshopId,
      specialty: options?.specialty,
      active_only: options?.activeOnly ?? true,
    };
    execute(fetchAgentese<WorldForgeArtisanListResponse>('world.forge.artisan.list', request));
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
 * AGENTESE: world.forge.artisan.join
 */
export function useJoinWorkshop(): MutationResult<
  WorldForgeArtisanJoinResponse,
  WorldForgeArtisanJoinRequest
> {
  const { state, execute } = useAsyncState<WorldForgeArtisanJoinResponse>();
  const [isPending, setIsPending] = useState(false);

  const mutateAsync = useCallback(
    async (data: WorldForgeArtisanJoinRequest) => {
      setIsPending(true);
      try {
        const result = await execute(
          fetchAgentese<WorldForgeArtisanJoinResponse>('world.forge.artisan.join', data)
        );
        if (!result) throw new Error('Failed to join workshop');
        return result;
      } finally {
        setIsPending(false);
      }
    },
    [execute]
  );

  const mutate = useCallback(
    (data: WorldForgeArtisanJoinRequest) => {
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
// Contribution Hooks
// =============================================================================

/**
 * Submit a contribution.
 * AGENTESE: world.forge.contribute
 */
export function useContribute(): MutationResult<
  WorldForgeContributeResponse,
  WorldForgeContributeRequest
> {
  const { state, execute } = useAsyncState<WorldForgeContributeResponse>();
  const [isPending, setIsPending] = useState(false);

  const mutateAsync = useCallback(
    async (data: WorldForgeContributeRequest) => {
      setIsPending(true);
      try {
        const result = await execute(
          fetchAgentese<WorldForgeContributeResponse>('world.forge.contribute', data)
        );
        if (!result) throw new Error('Failed to submit contribution');
        return result;
      } finally {
        setIsPending(false);
      }
    },
    [execute]
  );

  const mutate = useCallback(
    (data: WorldForgeContributeRequest) => {
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
 * Fetch list of contributions.
 * AGENTESE: world.forge.contribution.list
 */
export function useContributions(options?: {
  artisanId?: string;
  workshopId?: string;
  contributionType?: string;
  limit?: number;
}): QueryResult<WorldForgeContributionListResponse> {
  const { state, execute } = useAsyncState<WorldForgeContributionListResponse>();

  const refetch = useCallback(() => {
    execute(
      fetchAgentese<WorldForgeContributionListResponse>('world.forge.contribution.list', {
        artisan_id: options?.artisanId,
        workshop_id: options?.workshopId,
        contribution_type: options?.contributionType,
        limit: options?.limit ?? 50,
      })
    );
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
 * AGENTESE: world.forge.exhibition.create
 */
export function useCreateExhibition(): MutationResult<
  WorldForgeExhibitionCreateResponse,
  WorldForgeExhibitionCreateRequest
> {
  const { state, execute } = useAsyncState<WorldForgeExhibitionCreateResponse>();
  const [isPending, setIsPending] = useState(false);

  const mutateAsync = useCallback(
    async (data: WorldForgeExhibitionCreateRequest) => {
      setIsPending(true);
      try {
        const result = await execute(
          fetchAgentese<WorldForgeExhibitionCreateResponse>('world.forge.exhibition.create', data)
        );
        if (!result) throw new Error('Failed to create exhibition');
        return result;
      } finally {
        setIsPending(false);
      }
    },
    [execute]
  );

  const mutate = useCallback(
    (data: WorldForgeExhibitionCreateRequest) => {
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
 * Open an exhibition to public viewing.
 * AGENTESE: world.forge.exhibition.open
 */
export function useOpenExhibition(): MutationResult<
  WorldForgeExhibitionOpenResponse,
  WorldForgeExhibitionOpenRequest
> {
  const { state, execute } = useAsyncState<WorldForgeExhibitionOpenResponse>();
  const [isPending, setIsPending] = useState(false);

  const mutateAsync = useCallback(
    async (data: WorldForgeExhibitionOpenRequest) => {
      setIsPending(true);
      try {
        const result = await execute(
          fetchAgentese<WorldForgeExhibitionOpenResponse>('world.forge.exhibition.open', data)
        );
        if (!result) throw new Error('Failed to open exhibition');
        return result;
      } finally {
        setIsPending(false);
      }
    },
    [execute]
  );

  const mutate = useCallback(
    (data: WorldForgeExhibitionOpenRequest) => {
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
 * View an exhibition (increments view count).
 * AGENTESE: world.forge.exhibition.view
 */
export function useViewExhibition(
  exhibitionId: string,
  options?: { enabled?: boolean }
): QueryResult<WorldForgeExhibitionViewResponse> {
  const { state, execute, reset } = useAsyncState<WorldForgeExhibitionViewResponse>();
  const enabled = options?.enabled !== false && !!exhibitionId;

  const refetch = useCallback(() => {
    if (!enabled) return;
    const request: WorldForgeExhibitionViewRequest = { exhibition_id: exhibitionId };
    execute(
      fetchAgentese<WorldForgeExhibitionViewResponse>('world.forge.exhibition.view', request)
    );
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
 * AGENTESE: world.forge.gallery.list
 */
export function useGalleryItems(
  exhibitionId: string,
  options?: { enabled?: boolean }
): QueryResult<WorldForgeGalleryListResponse> {
  const { state, execute, reset } = useAsyncState<WorldForgeGalleryListResponse>();
  const enabled = options?.enabled !== false && !!exhibitionId;

  const refetch = useCallback(() => {
    if (!enabled) return;
    const request: WorldForgeGalleryListRequest = { exhibition_id: exhibitionId };
    execute(fetchAgentese<WorldForgeGalleryListResponse>('world.forge.gallery.list', request));
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
 * AGENTESE: world.forge.gallery.add
 */
export function useAddToGallery(): MutationResult<
  WorldForgeGalleryAddResponse,
  WorldForgeGalleryAddRequest
> {
  const { state, execute } = useAsyncState<WorldForgeGalleryAddResponse>();
  const [isPending, setIsPending] = useState(false);

  const mutateAsync = useCallback(
    async (data: WorldForgeGalleryAddRequest) => {
      setIsPending(true);
      try {
        const result = await execute(
          fetchAgentese<WorldForgeGalleryAddResponse>('world.forge.gallery.add', data)
        );
        if (!result) throw new Error('Failed to add to gallery');
        return result;
      } finally {
        setIsPending(false);
      }
    },
    [execute]
  );

  const mutate = useCallback(
    (data: WorldForgeGalleryAddRequest) => {
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
// Festival Hooks
// =============================================================================

/**
 * Fetch list of festivals.
 * AGENTESE: world.forge.festival.list
 */
export function useFestivals(): QueryResult<WorldForgeFestivalListResponse> {
  const { state, execute } = useAsyncState<WorldForgeFestivalListResponse>();

  const refetch = useCallback(() => {
    execute(fetchAgentese<WorldForgeFestivalListResponse>('world.forge.festival.list'));
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
 * AGENTESE: world.forge.festival.create
 */
export function useCreateFestival(): MutationResult<
  WorldForgeFestivalCreateResponse,
  WorldForgeFestivalCreateRequest
> {
  const { state, execute } = useAsyncState<WorldForgeFestivalCreateResponse>();
  const [isPending, setIsPending] = useState(false);

  const mutateAsync = useCallback(
    async (data: WorldForgeFestivalCreateRequest) => {
      setIsPending(true);
      try {
        const result = await execute(
          fetchAgentese<WorldForgeFestivalCreateResponse>('world.forge.festival.create', data)
        );
        if (!result) throw new Error('Failed to create festival');
        return result;
      } finally {
        setIsPending(false);
      }
    },
    [execute]
  );

  const mutate = useCallback(
    (data: WorldForgeFestivalCreateRequest) => {
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
 * Enter a festival.
 * AGENTESE: world.forge.festival.enter
 */
export function useEnterFestival(): MutationResult<
  WorldForgeFestivalEnterResponse,
  WorldForgeFestivalEnterRequest
> {
  const { state, execute } = useAsyncState<WorldForgeFestivalEnterResponse>();
  const [isPending, setIsPending] = useState(false);

  const mutateAsync = useCallback(
    async (data: WorldForgeFestivalEnterRequest) => {
      setIsPending(true);
      try {
        const result = await execute(
          fetchAgentese<WorldForgeFestivalEnterResponse>('world.forge.festival.enter', data)
        );
        if (!result) throw new Error('Failed to enter festival');
        return result;
      } finally {
        setIsPending(false);
      }
    },
    [execute]
  );

  const mutate = useCallback(
    (data: WorldForgeFestivalEnterRequest) => {
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
// Token/Bid Hooks
// =============================================================================

/**
 * Fetch token balance manifest.
 * AGENTESE: world.forge.tokens.manifest
 */
export function useTokenBalance(): QueryResult<WorldForgeTokensManifestResponse> {
  const { state, execute } = useAsyncState<WorldForgeTokensManifestResponse>();

  const refetch = useCallback(() => {
    execute(fetchAgentese<WorldForgeTokensManifestResponse>('world.forge.tokens.manifest'));
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
 * AGENTESE: world.forge.bid.submit
 */
export function useSubmitBid(): MutationResult<
  WorldForgeBidSubmitResponse,
  WorldForgeBidSubmitRequest
> {
  const { state, execute } = useAsyncState<WorldForgeBidSubmitResponse>();
  const [isPending, setIsPending] = useState(false);

  const mutateAsync = useCallback(
    async (data: WorldForgeBidSubmitRequest) => {
      setIsPending(true);
      try {
        const result = await execute(
          fetchAgentese<WorldForgeBidSubmitResponse>('world.forge.bid.submit', data)
        );
        if (!result) throw new Error('Failed to submit bid');
        return result;
      } finally {
        setIsPending(false);
      }
    },
    [execute]
  );

  const mutate = useCallback(
    (data: WorldForgeBidSubmitRequest) => {
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

export const forgeQueryKeys = {
  all: ['forge'] as const,
  manifest: () => [...forgeQueryKeys.all, 'manifest'] as const,
  workshops: () => [...forgeQueryKeys.all, 'workshops'] as const,
  workshopsList: () => [...forgeQueryKeys.workshops(), 'list'] as const,
  workshopDetail: (id: string) => [...forgeQueryKeys.workshops(), 'detail', id] as const,
  artisans: (workshopId: string) => [...forgeQueryKeys.all, 'artisans', workshopId] as const,
  contributions: () => [...forgeQueryKeys.all, 'contributions'] as const,
  exhibitions: () => [...forgeQueryKeys.all, 'exhibitions'] as const,
  exhibitionDetail: (id: string) => [...forgeQueryKeys.exhibitions(), 'detail', id] as const,
  gallery: (exhibitionId: string) => [...forgeQueryKeys.all, 'gallery', exhibitionId] as const,
  festivals: () => [...forgeQueryKeys.all, 'festivals'] as const,
  tokens: () => [...forgeQueryKeys.all, 'tokens'] as const,
};

// Types are already exported via type aliases at the top of this file
