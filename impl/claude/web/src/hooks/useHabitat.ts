/**
 * useHabitat - Hook for Concept Home Protocol (AD-010)
 *
 * Provides habitat information for any AGENTESE path using the existing
 * /agentese/discover endpoint. No new backend required.
 *
 * The Habitat Guarantee: Every path deserves a home.
 *
 * @see spec/principles.md - AD-010: The Habitat Guarantee
 * @see plans/concept-home-implementation.md
 */

import { useState, useEffect, useCallback, useMemo } from 'react';
import { apiClient } from '@/api/client';
import {
  determineTier,
  extractContext,
  getPlayground,
  type HabitatTier,
  type AGENTESEContext,
} from '@/lib/habitat';

// =============================================================================
// Types
// =============================================================================

/**
 * Example invocation from discovery endpoint.
 */
export interface NodeExample {
  aspect: string;
  kwargs: Record<string, unknown>;
  label: string;
}

/**
 * Node metadata from discovery endpoint.
 */
interface NodeMetadata {
  path: string;
  description?: string | null;
  aspects?: string[];
  effects?: string[];
  examples?: NodeExample[];
}

/**
 * Discovery endpoint response structure.
 */
interface DiscoveryResponse {
  paths: string[];
  stats: {
    registered_nodes: number;
    contexts: string[];
  };
  metadata?: Record<string, NodeMetadata>;
}

/**
 * Complete habitat information for a path.
 */
export interface HabitatInfo {
  /** Full AGENTESE path */
  path: string;
  /** Extracted context (world, self, concept, void, time) */
  context: AGENTESEContext;
  /** Computed tier (minimal, standard, rich) */
  tier: HabitatTier;
  /** Human-readable description */
  description: string | null;
  /** Available aspects for this path */
  aspects: string[];
  /** Declared effects */
  effects: string[];
  /** Pre-seeded examples (Habitat 2.0) */
  examples: NodeExample[];
  /** Custom playground component name (if rich tier) */
  playground: string | null;
  /** Route for custom playground (if rich tier) */
  playgroundRoute: string | null;
}

// =============================================================================
// Discovery Cache
// =============================================================================

/**
 * Module-level cache for discovery data.
 * Shared across all useHabitat instances for efficiency.
 */
interface DiscoveryCache {
  data: DiscoveryResponse;
  timestamp: number;
}

let discoveryCache: DiscoveryCache | null = null;
const CACHE_TTL = 5 * 60 * 1000; // 5 minutes

function isCacheValid(): boolean {
  if (!discoveryCache) return false;
  return Date.now() - discoveryCache.timestamp < CACHE_TTL;
}

// =============================================================================
// Hook
// =============================================================================

/**
 * Hook to get habitat information for an AGENTESE path.
 *
 * Uses the existing /agentese/discover endpoint - tier is computed
 * at render time, not stored in backend (AD-009: Metaphysical Fullstack).
 *
 * @param path - The AGENTESE path to get habitat for
 * @returns Habitat info, loading state, and error
 *
 * @example
 * ```tsx
 * const { habitat, loading, error } = useHabitat('world.town.citizen');
 *
 * if (loading) return <Spinner />;
 * if (habitat?.tier === 'rich') return <Navigate to={habitat.playgroundRoute} />;
 *
 * return <ConceptHome habitat={habitat} />;
 * ```
 */
export function useHabitat(path: string): {
  habitat: HabitatInfo | null;
  loading: boolean;
  error: Error | null;
  refetch: () => void;
} {
  const [discoveryData, setDiscoveryData] = useState<DiscoveryResponse | null>(
    discoveryCache?.data ?? null
  );
  const [loading, setLoading] = useState(!isCacheValid());
  const [error, setError] = useState<Error | null>(null);

  // Fetch discovery data
  const fetchDiscovery = useCallback(async () => {
    // Use cache if valid
    if (isCacheValid() && discoveryCache) {
      setDiscoveryData(discoveryCache.data);
      setLoading(false);
      return;
    }

    setLoading(true);
    setError(null);

    try {
      // Try to get metadata-enriched discovery
      const response = await apiClient.get<DiscoveryResponse>('/agentese/discover', {
        params: { include_metadata: true },
      });

      // Build metadata map if not provided by endpoint
      const data = response.data;
      if (!data.metadata) {
        data.metadata = {};
        for (const p of data.paths) {
          data.metadata[p] = {
            path: p,
            aspects: ['manifest'], // Default aspect
          };
        }
      }

      // Update cache (intentional module-level cache pattern)
      // eslint-disable-next-line require-atomic-updates
      discoveryCache = {
        data,
        timestamp: Date.now(),
      };

      setDiscoveryData(data);
    } catch (e) {
      setError(e as Error);
    } finally {
      setLoading(false);
    }
  }, []);

  // Fetch on mount
  useEffect(() => {
    fetchDiscovery();
  }, [fetchDiscovery]);

  // Compute habitat from discovery data
  const habitat = useMemo((): HabitatInfo | null => {
    if (!path) return null;
    if (!discoveryData) return null;

    // Get metadata for this path
    const meta = discoveryData.metadata?.[path];

    // Check if path exists in discovery
    const pathExists = discoveryData.paths.includes(path);

    // Get playground info for rich paths
    const playground = getPlayground(path);

    // Compute habitat info
    const context = extractContext(path);
    const tier = determineTier(
      path,
      meta?.description,
      meta?.aspects
    );

    return {
      path,
      context,
      tier,
      description: meta?.description ?? null,
      aspects: meta?.aspects ?? (pathExists ? ['manifest'] : []),
      effects: meta?.effects ?? [],
      examples: meta?.examples ?? [],
      playground: playground?.component ?? null,
      playgroundRoute: playground?.route ?? null,
    };
  }, [path, discoveryData]);

  return {
    habitat,
    loading,
    error,
    refetch: fetchDiscovery,
  };
}

// =============================================================================
// Utility Hook: All Habitats
// =============================================================================

/**
 * Hook to get habitat info for all discovered paths.
 * Useful for NavigationTree or path browsers.
 */
export function useAllHabitats(): {
  habitats: HabitatInfo[];
  loading: boolean;
  error: Error | null;
} {
  const [discoveryData, setDiscoveryData] = useState<DiscoveryResponse | null>(
    discoveryCache?.data ?? null
  );
  const [loading, setLoading] = useState(!isCacheValid());
  const [error, setError] = useState<Error | null>(null);

  // Fetch discovery data
  useEffect(() => {
    if (isCacheValid() && discoveryCache) {
      setDiscoveryData(discoveryCache.data);
      setLoading(false);
      return;
    }

    const fetchData = async () => {
      setLoading(true);
      try {
        const response = await apiClient.get<DiscoveryResponse>('/agentese/discover');
        const data = response.data;
        if (!data.metadata) {
          data.metadata = {};
          for (const p of data.paths) {
            data.metadata[p] = { path: p, aspects: ['manifest'] };
          }
        }
        discoveryCache = { data, timestamp: Date.now() };
        setDiscoveryData(data);
      } catch (e) {
        setError(e as Error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  // Compute all habitats
  const habitats = useMemo((): HabitatInfo[] => {
    if (!discoveryData) return [];

    return discoveryData.paths.map((path) => {
      const meta = discoveryData.metadata?.[path];
      const playground = getPlayground(path);
      const context = extractContext(path);
      const tier = determineTier(path, meta?.description, meta?.aspects);

      return {
        path,
        context,
        tier,
        description: meta?.description ?? null,
        aspects: meta?.aspects ?? ['manifest'],
        effects: meta?.effects ?? [],
        examples: meta?.examples ?? [],
        playground: playground?.component ?? null,
        playgroundRoute: playground?.route ?? null,
      };
    });
  }, [discoveryData]);

  return { habitats, loading, error };
}
