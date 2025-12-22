/**
 * useAgenteseDiscovery - Fetches AGENTESE registry data for the docs explorer.
 *
 * Uses /agentese/discover?include_metadata=true&include_schemas=true to get
 * the full picture: paths, aspects, examples, and JSON schemas.
 */

import { useState, useEffect, useCallback } from 'react';
import { apiClient } from '@/api/client';

// =============================================================================
// Types
// =============================================================================

/**
 * Per-aspect metadata from the @aspect decorator (Umwelt v2).
 *
 * This is the registry truth - no more heuristic guessing.
 */
export interface AspectMetadataEntry {
  /** Aspect category (e.g., "PERCEPTION", "MUTATION") */
  category: string;
  /** Capability required to invoke (e.g., "write", "admin", null for read) */
  requiredCapability: string | null;
  /** Declared effects (e.g., ["reads:memory", "writes:crystals"]) */
  effects: string[];
  /** Human-readable description */
  description: string;
  /** Whether this aspect streams results */
  streaming: boolean;
  /** Whether repeated calls have same effect */
  idempotent: boolean;
}

export interface PathMetadata {
  aspects: string[];
  effects: string[];
  examples: Array<{
    aspect: string;
    description?: string;
    payload?: Record<string, unknown>;
  }>;
  description?: string;
  /**
   * Per-aspect metadata with requiredCapability (Umwelt v2).
   * Maps aspect name -> metadata from @aspect decorator.
   */
  aspectMetadata?: Record<string, AspectMetadataEntry>;
}

export interface AspectSchema {
  request?: Record<string, unknown>;
  response?: Record<string, unknown>;
}

export interface DiscoveryResponse {
  paths: string[];
  stats: {
    registered_nodes: number;
    contexts: string[];
    total_paths: number;
  };
  metadata?: Record<string, PathMetadata>;
  schemas?: Record<string, Record<string, AspectSchema>>;
}

export interface UseAgenteseDiscoveryReturn {
  paths: string[];
  metadata: Record<string, PathMetadata>;
  schemas: Record<string, Record<string, AspectSchema>>;
  stats: DiscoveryResponse['stats'] | null;
  loading: boolean;
  error: string | null;
  refetch: () => void;
}

// =============================================================================
// Hook
// =============================================================================

/**
 * Fetch AGENTESE discovery data with metadata and schemas.
 */
export function useAgenteseDiscovery(): UseAgenteseDiscoveryReturn {
  const [paths, setPaths] = useState<string[]>([]);
  const [metadata, setMetadata] = useState<Record<string, PathMetadata>>({});
  const [schemas, setSchemas] = useState<Record<string, Record<string, AspectSchema>>>({});
  const [stats, setStats] = useState<DiscoveryResponse['stats'] | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchDiscovery = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await apiClient.get<DiscoveryResponse>(
        '/agentese/discover?include_metadata=true&include_schemas=true'
      );

      const data = response.data;
      setPaths(data.paths || []);
      setMetadata(data.metadata || {});
      setSchemas(data.schemas || {});
      setStats(data.stats || null);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to discover AGENTESE paths';
      setError(message);
      console.error('[useAgenteseDiscovery] Error:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchDiscovery();
  }, [fetchDiscovery]);

  return {
    paths,
    metadata,
    schemas,
    stats,
    loading,
    error,
    refetch: fetchDiscovery,
  };
}
