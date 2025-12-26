/**
 * useBrowseItems — Fetch all browseable items from K-Blocks API
 *
 * Provides unified item list for BrowseModal:
 * - Zero Seed K-Blocks (from PostgreSQL)
 * - User K-Blocks
 * - Future: filesystem files, docs, specs, conversations
 *
 * Philosophy:
 *   "All UI surfaces query the same source of truth."
 *   "Zero Seed nodes ARE K-Blocks. The derivation IS the lineage."
 */

import { useCallback, useEffect, useState } from 'react';
import { kblocksApi } from '../../../api/client';
import type { BrowseItem } from '../types';

export interface UseBrowseItemsReturn {
  /** All browseable items */
  items: BrowseItem[];
  /** Loading state */
  loading: boolean;
  /** Error state */
  error: Error | null;
  /** Refresh items from API */
  refresh: () => Promise<void>;
}

/**
 * Hook to fetch all browseable items from K-Blocks API.
 * Used by BrowseModal to show unified content.
 */
export function useBrowseItems(): UseBrowseItemsReturn {
  const [items, setItems] = useState<BrowseItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const fetchItems = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      // Fetch K-Blocks from PostgreSQL
      const browseResponse = await kblocksApi.browse();

      // Transform to BrowseItem[]
      const kblockItems = kblocksApi.toBrowseItems(browseResponse);

      // TODO: Add filesystem files, docs, specs from graphApi
      // For now, just K-Blocks from PostgreSQL

      setItems(kblockItems);
    } catch (err) {
      console.error('[useBrowseItems] Failed to fetch items:', err);
      setError(err instanceof Error ? err : new Error(String(err)));
      setItems([]);
    } finally {
      setLoading(false);
    }
  }, []);

  // Fetch on mount
  useEffect(() => {
    void fetchItems();
  }, [fetchItems]);

  return {
    items,
    loading,
    error,
    refresh: fetchItems,
  };
}

export default useBrowseItems;
