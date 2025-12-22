/**
 * useTrail - React hook for trail state management.
 *
 * "Bush's Memex realized: Force-directed graph showing exploration trails."
 *
 * Features:
 * - Load trail by ID with react-flow graph data
 * - Evidence analysis (strength, unique paths, etc.)
 * - Fork trail at specific points
 * - Selected step synchronization with graph
 *
 * @see spec/protocols/trail-protocol.md Section 8
 */

import { useCallback, useEffect, useMemo, useState } from 'react';
import {
  Trail,
  TrailEvidence,
  TrailGraphNode,
  TrailGraphEdge,
  TrailSummary,
  getTrailGraph,
  listTrails,
  forkTrail,
  computeEvidenceStrength,
} from '../api/trail';

// =============================================================================
// Types
// =============================================================================

/**
 * State for the useTrail hook.
 */
export interface UseTrailState {
  /** Loaded trail data */
  trail: Trail | null;
  /** Graph nodes for react-flow */
  nodes: TrailGraphNode[];
  /** Graph edges for react-flow */
  edges: TrailGraphEdge[];
  /** Trail evidence analysis */
  evidence: TrailEvidence | null;
  /** Loading state */
  loading: boolean;
  /** Error message */
  error: string | null;
  /** Currently selected step index */
  selectedStep: number | null;
}

/**
 * Return type for the useTrail hook.
 */
export interface UseTrailReturn extends UseTrailState {
  /** Load a trail by ID */
  loadTrail: (trailId: string) => Promise<void>;
  /** Clear the current trail */
  clearTrail: () => void;
  /** Select a step (syncs with graph) */
  selectStep: (stepIndex: number | null) => void;
  /** Fork the current trail */
  forkCurrentTrail: (name: string, forkPoint?: number) => Promise<string | null>;
  /** Refresh the current trail */
  refresh: () => Promise<void>;
}

/**
 * State for the useTrailList hook.
 */
export interface UseTrailListReturn {
  /** List of trail summaries */
  trails: TrailSummary[];
  /** Loading state */
  loading: boolean;
  /** Error message */
  error: string | null;
  /** Refresh the list */
  refresh: () => Promise<void>;
}

// =============================================================================
// useTrail Hook
// =============================================================================

/**
 * Hook for managing a single trail's state with react-flow graph data.
 *
 * @param initialTrailId - Optional trail ID to load on mount
 *
 * @example
 * ```tsx
 * const { trail, nodes, edges, evidence, loading, error, loadTrail, selectStep } = useTrail();
 *
 * // Load a trail
 * await loadTrail("trail-abc123");
 *
 * // Select a step (highlights in graph)
 * selectStep(3);
 *
 * // Use in react-flow
 * <ReactFlow nodes={nodes} edges={edges} ... />
 * ```
 */
export function useTrail(initialTrailId?: string): UseTrailReturn {
  const [state, setState] = useState<UseTrailState>({
    trail: null,
    nodes: [],
    edges: [],
    evidence: null,
    loading: false,
    error: null,
    selectedStep: null,
  });

  // Track the current trail ID for refresh
  const [currentTrailId, setCurrentTrailId] = useState<string | null>(
    initialTrailId || null
  );

  /**
   * Load a trail by ID.
   */
  const loadTrail = useCallback(async (trailId: string) => {
    setState((prev) => ({ ...prev, loading: true, error: null }));
    setCurrentTrailId(trailId);

    try {
      const result = await getTrailGraph(trailId);

      if (!result) {
        setState((prev) => ({
          ...prev,
          loading: false,
          error: `Trail not found: ${trailId}`,
          trail: null,
          nodes: [],
          edges: [],
          evidence: null,
        }));
        return;
      }

      setState((prev) => ({
        ...prev,
        trail: result.trail,
        nodes: result.nodes,
        edges: result.edges,
        evidence: result.evidence,
        loading: false,
        selectedStep: null,
      }));
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to load trail';
      setState((prev) => ({
        ...prev,
        loading: false,
        error: message,
        trail: null,
        nodes: [],
        edges: [],
        evidence: null,
      }));
    }
  }, []);

  /**
   * Clear the current trail.
   */
  const clearTrail = useCallback(() => {
    setState({
      trail: null,
      nodes: [],
      edges: [],
      evidence: null,
      loading: false,
      error: null,
      selectedStep: null,
    });
    setCurrentTrailId(null);
  }, []);

  /**
   * Select a step (syncs with graph highlighting).
   */
  const selectStep = useCallback((stepIndex: number | null) => {
    setState((prev) => {
      // Update nodes to reflect selection
      const updatedNodes = prev.nodes.map((node) => ({
        ...node,
        data: {
          ...node.data,
          is_current: stepIndex !== null && node.data.step_index === stepIndex,
        },
      }));

      return {
        ...prev,
        selectedStep: stepIndex,
        nodes: updatedNodes,
      };
    });
  }, []);

  /**
   * Fork the current trail.
   */
  const forkCurrentTrail = useCallback(
    async (name: string, forkPoint?: number): Promise<string | null> => {
      if (!state.trail) return null;

      try {
        const result = await forkTrail(state.trail.trail_id, name, forkPoint);
        if (result) {
          // Optionally load the forked trail
          // await loadTrail(result.trail_id);
          return result.trail_id;
        }
        return null;
      } catch (err) {
        const message = err instanceof Error ? err.message : 'Failed to fork trail';
        setState((prev) => ({ ...prev, error: message }));
        return null;
      }
    },
    [state.trail]
  );

  /**
   * Refresh the current trail.
   */
  const refresh = useCallback(async () => {
    if (currentTrailId) {
      await loadTrail(currentTrailId);
    }
  }, [currentTrailId, loadTrail]);

  // Load initial trail on mount
  useEffect(() => {
    if (initialTrailId) {
      loadTrail(initialTrailId);
    }
  }, [initialTrailId, loadTrail]);

  return {
    trail: state.trail,
    nodes: state.nodes,
    edges: state.edges,
    evidence: state.evidence,
    loading: state.loading,
    error: state.error,
    selectedStep: state.selectedStep,
    loadTrail,
    clearTrail,
    selectStep,
    forkCurrentTrail,
    refresh,
  };
}

// =============================================================================
// useTrailList Hook
// =============================================================================

/**
 * Hook for listing available trails.
 *
 * @param limit - Maximum trails to fetch (default: 50)
 *
 * @example
 * ```tsx
 * const { trails, loading, error, refresh } = useTrailList();
 *
 * // Display trails
 * {trails.map(trail => (
 *   <div key={trail.trail_id}>{trail.name}</div>
 * ))}
 * ```
 */
export function useTrailList(limit = 50): UseTrailListReturn {
  const [trails, setTrails] = useState<TrailSummary[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const result = await listTrails(limit);
      setTrails(result);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to list trails';
      setError(message);
    } finally {
      setLoading(false);
    }
  }, [limit]);

  // Fetch on mount
  useEffect(() => {
    refresh();
  }, [refresh]);

  return {
    trails,
    loading,
    error,
    refresh,
  };
}

// =============================================================================
// Utility Hooks
// =============================================================================

/**
 * Hook for computing derived trail metrics.
 */
export function useTrailMetrics(trail: Trail | null): {
  stepCount: number;
  uniquePaths: number;
  uniqueEdges: number;
  evidenceStrength: 'weak' | 'moderate' | 'strong' | 'definitive';
  duration: string | null;
} {
  return useMemo(() => {
    if (!trail) {
      return {
        stepCount: 0,
        uniquePaths: 0,
        uniqueEdges: 0,
        evidenceStrength: 'weak' as const,
        duration: null,
      };
    }

    const steps = trail.steps;
    const paths = new Set(steps.map((s) => s.source_path));
    const edges = new Set(steps.filter((s) => s.edge).map((s) => s.edge));

    // Compute duration if timestamps available
    let duration: string | null = null;
    const firstCreatedAt = steps[0]?.created_at;
    const lastCreatedAt = steps[steps.length - 1]?.created_at;
    if (steps.length >= 2 && firstCreatedAt && lastCreatedAt) {
      const start = new Date(firstCreatedAt);
      const end = new Date(lastCreatedAt);
      const diffMs = end.getTime() - start.getTime();
      const diffMins = Math.round(diffMs / 60000);
      duration = `${diffMins} min`;
    }

    return {
      stepCount: steps.length,
      uniquePaths: paths.size,
      uniqueEdges: edges.size,
      evidenceStrength: computeEvidenceStrength(steps.length, paths.size),
      duration,
    };
  }, [trail]);
}

// Note: UseTrailState is already exported with the interface declaration
