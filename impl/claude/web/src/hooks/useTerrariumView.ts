/**
 * useTerrariumView - Lens-based view management for TerrariumView.
 *
 * WARP Phase 2: React Projection Layer.
 *
 * Provides:
 * - View creation and management
 * - Lens mode switching (timeline, graph, summary, detail)
 * - Selection query building
 * - Projection through view to SceneGraph
 *
 * @example
 * const { scene, lens, setLensMode, selection, addFilter } = useTerrariumView({
 *   defaultLens: 'timeline',
 * });
 */

import { useState, useCallback } from 'react';
import type {
  SceneGraph,
  TerrariumView,
  LensMode,
  SelectionPredicate,
  WorldSceneryCreateViewResponse,
  WorldSceneryProjectResponse,
} from '../api/types/_generated/world-scenery';

// =============================================================================
// Types
// =============================================================================

export interface UseTerrariumViewOptions {
  /** Initial view ID to load */
  viewId?: string;
  /** Default lens mode */
  defaultLens?: LensMode;
  /** Default origin filter */
  originFilter?: string;
  /** Default trace limit */
  limit?: number;
  /** Auto-project on filter changes */
  autoProject?: boolean;
}

export interface UseTerrariumViewReturn {
  /** Current view configuration */
  view: TerrariumView | null;
  /** Projected SceneGraph */
  scene: SceneGraph | null;

  // Lens controls
  lens: LensMode;
  setLensMode: (mode: LensMode) => void;

  // Selection controls
  predicates: SelectionPredicate[];
  addPredicate: (predicate: SelectionPredicate) => void;
  removePredicate: (field: string) => void;
  clearPredicates: () => void;

  // View lifecycle
  createView: (name: string) => Promise<TerrariumView | null>;
  project: () => Promise<SceneGraph | null>;

  // Status
  isProjecting: boolean;
  error: string | null;
}

// =============================================================================
// Constants
// =============================================================================

const API_BASE = import.meta.env.VITE_API_URL || '';

// =============================================================================
// Hook Implementation
// =============================================================================

export function useTerrariumView(options: UseTerrariumViewOptions = {}): UseTerrariumViewReturn {
  const { defaultLens = 'TIMELINE', originFilter, limit = 50, autoProject = false } = options;

  // State
  const [view, setView] = useState<TerrariumView | null>(null);
  const [scene, setScene] = useState<SceneGraph | null>(null);
  const [lens, setLens] = useState<LensMode>(defaultLens);
  const [predicates, setPredicates] = useState<SelectionPredicate[]>(() => {
    // Initialize with origin filter if provided
    if (originFilter) {
      return [{ field: 'origin', op: 'EQ', value: originFilter }];
    }
    return [];
  });
  const [isProjecting, setIsProjecting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // ==========================================================================
  // Lens Controls
  // ==========================================================================

  const setLensMode = useCallback(
    (mode: LensMode) => {
      setLens(mode);
      if (autoProject && view) {
        // Trigger re-projection with new lens
        // This would call the project endpoint
      }
    },
    [autoProject, view]
  );

  // ==========================================================================
  // Selection Controls
  // ==========================================================================

  const addPredicate = useCallback((predicate: SelectionPredicate) => {
    setPredicates((prev) => {
      // Remove existing predicate for same field
      const filtered = prev.filter((p) => p.field !== predicate.field);
      return [...filtered, predicate];
    });
  }, []);

  const removePredicate = useCallback((field: string) => {
    setPredicates((prev) => prev.filter((p) => p.field !== field));
  }, []);

  const clearPredicates = useCallback(() => {
    setPredicates([]);
  }, []);

  // ==========================================================================
  // View Lifecycle
  // ==========================================================================

  const createView = useCallback(
    async (name: string): Promise<TerrariumView | null> => {
      setError(null);

      try {
        const response = await fetch(`${API_BASE}/agentese/world/scenery/create_view`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            name,
            lens_mode: lens.toLowerCase(),
            origin_filter: predicates.find((p) => p.field === 'origin')?.value ?? null,
            limit,
          }),
        });

        if (!response.ok) {
          throw new Error(`HTTP ${response.status}`);
        }

        const data = await response.json();
        const result = data.result as WorldSceneryCreateViewResponse;

        if (result.created && result.view) {
          setView(result.view);
          return result.view;
        }

        return null;
      } catch (e) {
        const message = e instanceof Error ? e.message : 'Failed to create view';
        setError(message);
        console.error('[useTerrariumView] Create view error:', e);
        return null;
      }
    },
    [lens, predicates, limit]
  );

  const project = useCallback(async (): Promise<SceneGraph | null> => {
    setIsProjecting(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE}/agentese/world/scenery/project`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          view_id: view?.id ?? null,
          traces: null, // Use demo traces
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();
      const result = data.result as WorldSceneryProjectResponse;

      if (result.scene) {
        setScene(result.scene);
        return result.scene;
      }

      return null;
    } catch (e) {
      const message = e instanceof Error ? e.message : 'Projection failed';
      setError(message);
      console.error('[useTerrariumView] Project error:', e);
      return null;
    } finally {
      setIsProjecting(false);
    }
  }, [view?.id]);

  return {
    view,
    scene,
    lens,
    setLensMode,
    predicates,
    addPredicate,
    removePredicate,
    clearPredicates,
    createView,
    project,
    isProjecting,
    error,
  };
}

export default useTerrariumView;
