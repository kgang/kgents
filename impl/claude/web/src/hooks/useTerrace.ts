/**
 * useTerrace - Hook for Terrace (curated knowledge) CRUD operations.
 *
 * WARP Phase 2: React Projection Layer.
 *
 * Provides:
 * - List all current knowledge entries
 * - Create new knowledge
 * - Evolve existing knowledge
 * - Search knowledge
 * - Get version history
 *
 * @example
 * const { entries, create, evolve, search } = useTerrace();
 */

import { useState, useCallback, useEffect, useRef } from 'react';

// =============================================================================
// Types
// =============================================================================

export interface TerraceEntry {
  id: string;
  topic: string;
  content: string;
  version: number;
  confidence: number;
  tags: string[];
  age_days: number;
  status: 'CURRENT' | 'SUPERSEDED';
  created_at: string;
  evolution_reason?: string;
}

export interface TerraceManifest {
  path: string;
  description: string;
  total_entries: number;
  topics: string[];
  entries: TerraceEntry[];
  laws: string[];
}

export interface UseTerraceOptions {
  /** Auto-fetch on mount (default: true) */
  autoFetch?: boolean;
}

export interface UseTerraceReturn {
  /** All current entries */
  entries: TerraceEntry[];
  /** All topics */
  topics: string[];
  /** Total entry count */
  totalCount: number;

  // CRUD operations
  create: (
    topic: string,
    content: string,
    options?: { tags?: string[]; source?: string; confidence?: number }
  ) => Promise<TerraceEntry | null>;

  evolve: (
    topic: string,
    content: string,
    options?: { reason?: string; tags?: string[]; confidence?: number }
  ) => Promise<TerraceEntry | null>;

  search: (query: string) => Promise<TerraceEntry[]>;

  history: (topic: string) => Promise<TerraceEntry[]>;

  // Refresh
  refresh: () => Promise<void>;

  // Status
  isLoading: boolean;
  error: string | null;
}

// =============================================================================
// Constants
// =============================================================================

const API_BASE = import.meta.env.VITE_API_URL || '';

// =============================================================================
// Hook Implementation
// =============================================================================

export function useTerrace(options: UseTerraceOptions = {}): UseTerraceReturn {
  const { autoFetch = true } = options;

  // State
  const [entries, setEntries] = useState<TerraceEntry[]>([]);
  const [topics, setTopics] = useState<string[]>([]);
  const [totalCount, setTotalCount] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Refs
  const mountedRef = useRef(true);

  // ==========================================================================
  // Fetch Manifest
  // ==========================================================================

  const refresh = useCallback(async (): Promise<void> => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE}/agentese/brain/terrace/manifest`);

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();
      if (mountedRef.current && data.result) {
        const manifest = data.result as TerraceManifest;
        setEntries(manifest.entries || []);
        setTopics(manifest.topics || []);
        setTotalCount(manifest.total_entries || 0);
      }
    } catch (e) {
      const message = e instanceof Error ? e.message : 'Fetch failed';
      if (mountedRef.current) {
        setError(message);
      }
      console.error('[useTerrace] Fetch error:', e);
    } finally {
      if (mountedRef.current) {
        setIsLoading(false);
      }
    }
  }, []);

  // ==========================================================================
  // Create Entry
  // ==========================================================================

  const create = useCallback(
    async (
      topic: string,
      content: string,
      options?: { tags?: string[]; source?: string; confidence?: number }
    ): Promise<TerraceEntry | null> => {
      setError(null);

      try {
        const response = await fetch(`${API_BASE}/agentese/brain/terrace/create`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            topic,
            content,
            tags: options?.tags ?? [],
            source: options?.source ?? '',
            confidence: options?.confidence ?? 1.0,
          }),
        });

        if (!response.ok) {
          throw new Error(`HTTP ${response.status}`);
        }

        const data = await response.json();
        if (data.result?.error) {
          throw new Error(data.result.message || data.result.error);
        }

        // Refresh to get updated list
        await refresh();

        return data.result?.terrace || null;
      } catch (e) {
        const message = e instanceof Error ? e.message : 'Create failed';
        setError(message);
        console.error('[useTerrace] Create error:', e);
        return null;
      }
    },
    [refresh]
  );

  // ==========================================================================
  // Evolve Entry
  // ==========================================================================

  const evolve = useCallback(
    async (
      topic: string,
      content: string,
      options?: { reason?: string; tags?: string[]; confidence?: number }
    ): Promise<TerraceEntry | null> => {
      setError(null);

      try {
        const response = await fetch(`${API_BASE}/agentese/brain/terrace/evolve`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            topic,
            content,
            reason: options?.reason ?? '',
            tags: options?.tags ?? null,
            confidence: options?.confidence ?? null,
          }),
        });

        if (!response.ok) {
          throw new Error(`HTTP ${response.status}`);
        }

        const data = await response.json();
        if (data.result?.error) {
          throw new Error(data.result.message || data.result.error);
        }

        // Refresh to get updated list
        await refresh();

        return data.result?.terrace || null;
      } catch (e) {
        const message = e instanceof Error ? e.message : 'Evolve failed';
        setError(message);
        console.error('[useTerrace] Evolve error:', e);
        return null;
      }
    },
    [refresh]
  );

  // ==========================================================================
  // Search
  // ==========================================================================

  const search = useCallback(async (query: string): Promise<TerraceEntry[]> => {
    try {
      const response = await fetch(`${API_BASE}/agentese/brain/terrace/search`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query }),
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();
      return data.result?.results || [];
    } catch (e) {
      console.error('[useTerrace] Search error:', e);
      return [];
    }
  }, []);

  // ==========================================================================
  // History
  // ==========================================================================

  const history = useCallback(async (topic: string): Promise<TerraceEntry[]> => {
    try {
      const response = await fetch(`${API_BASE}/agentese/brain/terrace/history`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ topic }),
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();
      return data.result?.versions || [];
    } catch (e) {
      console.error('[useTerrace] History error:', e);
      return [];
    }
  }, []);

  // ==========================================================================
  // Lifecycle
  // ==========================================================================

  useEffect(() => {
    mountedRef.current = true;

    if (autoFetch) {
      refresh();
    }

    return () => {
      mountedRef.current = false;
    };
  }, [autoFetch, refresh]);

  return {
    entries,
    topics,
    totalCount,
    create,
    evolve,
    search,
    history,
    refresh,
    isLoading,
    error,
  };
}

export default useTerrace;
