/**
 * useGardenState — Hook for garden lifecycle state
 *
 * Grounded in: spec/ui/axioms.md — A4 (No-Shipping Axiom)
 * "There is no shipping. Only continuous iteration."
 *
 * Fetches and manages garden state from the backend API.
 */

import { useState, useEffect, useCallback } from 'react';
import type { GardenState, GardenItem } from '../types';

const API_BASE = '/api/garden';

interface UseGardenStateResult {
  /** Current garden state */
  state: GardenState | null;

  /** Loading status */
  loading: boolean;

  /** Error (if any) */
  error: string | null;

  /** Refresh the garden state */
  refresh: () => Promise<void>;

  /** Mark an item as tended */
  tendItem: (path: string) => Promise<void>;

  /** Mark an item for composting */
  compostItem: (path: string) => Promise<void>;
}

/**
 * Default empty garden state.
 */
const EMPTY_STATE: GardenState = {
  seeds: 0,
  sprouts: 0,
  blooms: 0,
  withering: 0,
  compostedToday: 0,
  health: 1,
  attention: [],
};

/**
 * Hook for managing garden lifecycle state.
 */
export function useGardenState(): UseGardenStateResult {
  const [state, setState] = useState<GardenState | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  /**
   * Fetch garden state from backend.
   */
  const refresh = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await fetch(`${API_BASE}/state`);
      if (!response.ok) {
        throw new Error(`Failed to fetch garden state: ${response.status}`);
      }

      const data = await response.json();

      // Map backend response to frontend types
      const gardenState: GardenState = {
        seeds: data.seeds || 0,
        sprouts: data.sprouts || 0,
        blooms: data.blooms || 0,
        withering: data.withering || 0,
        compostedToday: data.composted_today || 0,
        health: data.health || 1,
        attention: (data.attention || []).map(mapGardenItem),
      };

      setState(gardenState);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      // Use empty state on error
      setState(EMPTY_STATE);
    } finally {
      setLoading(false);
    }
  }, []);

  /**
   * Mark an item as tended.
   */
  const tendItem = useCallback(
    async (path: string) => {
      try {
        const response = await fetch(`${API_BASE}/items/${encodeURIComponent(path)}/tend`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
        });

        if (!response.ok) {
          throw new Error(`Failed to tend item: ${response.status}`);
        }

        // Refresh state after action
        await refresh();
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to tend item');
      }
    },
    [refresh]
  );

  /**
   * Mark an item for composting.
   */
  const compostItem = useCallback(
    async (path: string) => {
      try {
        const response = await fetch(`${API_BASE}/items/${encodeURIComponent(path)}/compost`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
        });

        if (!response.ok) {
          throw new Error(`Failed to compost item: ${response.status}`);
        }

        // Refresh state after action
        await refresh();
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to compost item');
      }
    },
    [refresh]
  );

  // Initial fetch
  useEffect(() => {
    refresh();
  }, [refresh]);

  return {
    state,
    loading,
    error,
    refresh,
    tendItem,
    compostItem,
  };
}

/**
 * Map backend garden item to frontend type.
 */
function mapGardenItem(item: Record<string, unknown>): GardenItem {
  return {
    path: String(item.path || ''),
    title: String(item.title || ''),
    lifecycle: {
      stage: mapStage(String(item.stage || 'seed')),
      lastActivity: String(item.last_activity || new Date().toISOString()),
      daysSinceActivity: Number(item.days_since_activity || 0),
    },
  };
}

/**
 * Map backend stage string to frontend LifecycleStage.
 */
function mapStage(stage: string): 'seed' | 'sprout' | 'bloom' | 'wither' | 'compost' {
  const stageMap: Record<string, 'seed' | 'sprout' | 'bloom' | 'wither' | 'compost'> = {
    seed: 'seed',
    sprout: 'sprout',
    bloom: 'bloom',
    wither: 'wither',
    compost: 'compost',
    // Backend mappings
    unwitnessed: 'seed',
    in_progress: 'sprout',
    active: 'bloom',
    stale: 'wither',
    archived: 'compost',
  };

  return stageMap[stage.toLowerCase()] || 'seed';
}

export default useGardenState;
