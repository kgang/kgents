/**
 * useWalkDashboard - Fetch Walks as SceneGraph for TerrariumView.
 *
 * WARP Phase 2: Session 7 TerrariumView Foundation.
 *
 * Fetches from AGENTESE `time.walk.list` which returns SceneGraph JSON
 * ready for ServoSceneRenderer.
 *
 * @example
 * const { scene, isLoading, error, refetch } = useWalkDashboard();
 *
 * if (isLoading) return <Loading />;
 * if (!scene) return <EmptyState />;
 *
 * return <ServoSceneRenderer scene={scene} />;
 */

import { useEffect, useCallback, useState, useRef } from 'react';
import { apiClient } from '../api/client';
import type { SceneGraph } from '../components/servo/ServoSceneRenderer';

// =============================================================================
// Types
// =============================================================================

export interface UseWalkDashboardOptions {
  /** Max walks to fetch (default: 20) */
  limit?: number;
  /** Only fetch active walks */
  activeOnly?: boolean;
  /** Auto-refresh interval in ms (0 = disabled) */
  refreshInterval?: number;
}

export interface UseWalkDashboardReturn {
  /** SceneGraph data for ServoSceneRenderer */
  scene: SceneGraph | null;
  /** Loading state */
  isLoading: boolean;
  /** Error if fetch failed */
  error: Error | null;
  /** Refetch data */
  refetch: () => void;
  /** Number of walks in scene */
  walkCount: number;
}

// =============================================================================
// API Constants
// =============================================================================

const API_PATH = 'time/walk';

// =============================================================================
// Hook Implementation
// =============================================================================

export function useWalkDashboard(
  options: UseWalkDashboardOptions = {}
): UseWalkDashboardReturn {
  const { limit = 20, activeOnly = false, refreshInterval = 0 } = options;

  const [scene, setScene] = useState<SceneGraph | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);
  const [walkCount, setWalkCount] = useState(0);

  // Stable ref for interval cleanup
  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  // Fetch function
  const fetchData = useCallback(async () => {
    setError(null);

    try {
      const response = await apiClient.post<{
        path: string;
        aspect: string;
        result: SceneGraph;
        error?: string;
      }>(`/agentese/${API_PATH}/list`, {
        limit,
        active_only: activeOnly,
      });

      if (response.data.error) {
        throw new Error(response.data.error);
      }

      const sceneData = response.data.result;

      // Validate scene structure
      if (!sceneData || !Array.isArray(sceneData.nodes)) {
        throw new Error('Invalid scene data from API');
      }

      setScene(sceneData);

      // Count WALK nodes
      const walks = sceneData.nodes.filter((n) => n.kind === 'WALK');
      setWalkCount(walks.length);
    } catch (e) {
      const err = e instanceof Error ? e : new Error('Unknown error');
      setError(err);
      console.error('[useWalkDashboard] Fetch error:', err);
    } finally {
      setIsLoading(false);
    }
  }, [limit, activeOnly]);

  // Initial fetch
  useEffect(() => {
    fetchData();
  }, [fetchData]);

  // Auto-refresh
  useEffect(() => {
    if (refreshInterval > 0) {
      intervalRef.current = setInterval(fetchData, refreshInterval);
      return () => {
        if (intervalRef.current) {
          clearInterval(intervalRef.current);
        }
      };
    }
    return undefined;
  }, [refreshInterval, fetchData]);

  // Refetch function
  const refetch = useCallback(() => {
    setIsLoading(true);
    fetchData();
  }, [fetchData]);

  return {
    scene,
    isLoading,
    error,
    refetch,
    walkCount,
  };
}

export default useWalkDashboard;
