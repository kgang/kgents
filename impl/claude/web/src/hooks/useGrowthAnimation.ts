/**
 * useGrowthAnimation - Differential growth animation hook
 *
 * Manages organic edge growth animations for visualizations like BrainTopology.
 * Edges don't teleport into existence—they grow from source to target.
 *
 * Philosophy:
 *   "The structure is not designed—it emerges from rules.
 *    We do not design the flower; we design the soil and the season."
 *
 * @see impl/claude/agents/i/reactive/animation/growth.py (Python isomorphism)
 * @see impl/claude/web/src/components/three/GrowingEdge.tsx
 */

import { useState, useCallback, useEffect, useRef, useMemo } from 'react';
import type {
  GrowthRules,
  GrowthEdge,
  GrowthAnimationState,
  EdgeGrowthConfig,
} from '../types/emergence';
import { GROWTH_PRESETS, DEFAULT_EDGE_GROWTH_CONFIG } from '../types/emergence';

// =============================================================================
// Types
// =============================================================================

export interface GrowthAnimationOptions {
  /** Growth configuration */
  config?: Partial<EdgeGrowthConfig>;
  /** Called when an edge completes growth */
  onEdgeComplete?: (edgeId: string) => void;
  /** Called when all edges complete */
  onAllComplete?: () => void;
  /** Time step for simulation (ms) */
  timeStep?: number;
}

export interface UseGrowthAnimationReturn {
  /** Current animation state */
  state: GrowthAnimationState;
  /** Start growing an edge */
  startEdge: (
    edgeId: string,
    sourcePosition: [number, number, number],
    targetPosition: [number, number, number],
    options?: { growthRate?: number }
  ) => void;
  /** Start growing multiple edges */
  startEdges: (
    edges: Array<{
      id: string;
      source: [number, number, number];
      target: [number, number, number];
      growthRate?: number;
      delay?: number;
    }>
  ) => void;
  /** Stop a specific edge */
  stopEdge: (edgeId: string) => void;
  /** Stop all edges */
  stopAll: () => void;
  /** Get current edge path for rendering */
  getEdgePath: (edgeId: string, segments?: number) => Array<[number, number, number]>;
  /** Get edge progress (0-1) */
  getEdgeProgress: (edgeId: string) => number;
  /** Whether any edges are currently animating */
  isAnimating: boolean;
  /** Active edge IDs */
  activeEdgeIds: string[];
  /** Update growth rules */
  setRules: (rules: Partial<GrowthRules>) => void;
  /** Current growth rules */
  rules: GrowthRules;
}

// =============================================================================
// Helper Functions
// =============================================================================

/**
 * Generate organic waypoints between two points.
 * Adds slight perpendicular offset based on edge ID for determinism.
 */
function generateWaypoints(
  source: [number, number, number],
  target: [number, number, number],
  edgeId: string,
  count: number = 3
): Array<[number, number, number]> {
  const waypoints: Array<[number, number, number]> = [];

  // Direction vector
  const dx = target[0] - source[0];
  const dy = target[1] - source[1];
  const dz = target[2] - source[2];

  // Perpendicular vector in XY plane
  const length = Math.sqrt(dx * dx + dy * dy + dz * dz);
  const perpX = -dy / length;
  const perpY = dx / length;

  for (let i = 1; i <= count; i++) {
    const t = i / (count + 1);

    // Base interpolated position
    const x = source[0] + dx * t;
    const y = source[1] + dy * t;
    const z = source[2] + dz * t;

    // Deterministic offset based on edge ID
    const seed = (hash(edgeId + i.toString()) % 1000) / 1000;
    const offset = Math.sin(t * Math.PI) * 0.03 * (seed - 0.5);

    waypoints.push([
      x + perpX * offset,
      y + perpY * offset,
      z,
    ]);
  }

  return waypoints;
}

/**
 * Simple string hash for deterministic randomness.
 */
function hash(str: string): number {
  let h = 0;
  for (let i = 0; i < str.length; i++) {
    h = ((h << 5) - h + str.charCodeAt(i)) | 0;
  }
  return Math.abs(h);
}

/**
 * Interpolate along a path with waypoints.
 */
function interpolatePath(
  source: [number, number, number],
  target: [number, number, number],
  waypoints: Array<[number, number, number]>,
  progress: number
): [number, number, number] {
  if (progress <= 0) return source;
  if (progress >= 1) return target;

  // Build full path
  const fullPath = [source, ...waypoints, target];
  const segmentCount = fullPath.length - 1;

  // Find which segment we're in
  const scaledProgress = progress * segmentCount;
  const segmentIndex = Math.min(Math.floor(scaledProgress), segmentCount - 1);
  const segmentProgress = scaledProgress - segmentIndex;

  // Interpolate within segment
  const start = fullPath[segmentIndex];
  const end = fullPath[segmentIndex + 1];

  // Ease function for organic feel
  const easedProgress = easeInOutCubic(segmentProgress);

  return [
    start[0] + (end[0] - start[0]) * easedProgress,
    start[1] + (end[1] - start[1]) * easedProgress,
    start[2] + (end[2] - start[2]) * easedProgress,
  ];
}

/**
 * Cubic ease in-out for organic motion.
 */
function easeInOutCubic(t: number): number {
  return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
}

// =============================================================================
// Edge State Management
// =============================================================================

interface InternalEdge extends GrowthEdge {
  sourcePosition: [number, number, number];
  targetPosition: [number, number, number];
  startTime: number;
  delay: number;
}

// =============================================================================
// Main Hook
// =============================================================================

export function useGrowthAnimation(
  options: GrowthAnimationOptions = {}
): UseGrowthAnimationReturn {
  const {
    config = {},
    onEdgeComplete,
    onAllComplete,
  } = options;

  // Merge config with defaults
  const fullConfig: EdgeGrowthConfig = {
    ...DEFAULT_EDGE_GROWTH_CONFIG,
    ...config,
  };

  // Get rules from preset or custom
  const [rules, setRulesState] = useState<GrowthRules>(() => {
    const preset = GROWTH_PRESETS[fullConfig.preset];
    return fullConfig.customRules ? { ...preset, ...fullConfig.customRules } : preset;
  });

  // Edge state
  const [edges, setEdges] = useState<Map<string, InternalEdge>>(new Map());
  const [state, setState] = useState<GrowthAnimationState>({
    time: 0,
    kineticEnergy: 0,
    isSettled: true,
    activeEdges: [],
  });

  // Animation refs
  const animationRef = useRef<number | null>(null);
  const lastTimeRef = useRef<number>(0);

  // Computed values
  const isAnimating = edges.size > 0;
  const activeEdgeIds = useMemo(() => Array.from(edges.keys()), [edges]);

  // Animation loop
  useEffect(() => {
    if (!fullConfig.enabled || edges.size === 0) {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
        animationRef.current = null;
      }
      return;
    }

    const animate = (currentTime: number) => {
      if (lastTimeRef.current === 0) {
        lastTimeRef.current = currentTime;
      }

      const deltaTime = currentTime - lastTimeRef.current;
      lastTimeRef.current = currentTime;

      // Calculate progress based on configured duration
      const progressIncrement = deltaTime / fullConfig.duration;

      let completedEdges: string[] = [];
      let hasChanges = false;

      setEdges((prev) => {
        const next = new Map(prev);

        for (const [id, edge] of next) {
          // Check if delay has passed
          const elapsed = currentTime - edge.startTime;
          if (elapsed < edge.delay) {
            continue;
          }

          // Update progress
          const newProgress = Math.min(
            edge.progress + progressIncrement * edge.growthRate,
            1
          );

          if (newProgress !== edge.progress) {
            hasChanges = true;
            next.set(id, { ...edge, progress: newProgress });

            if (newProgress >= 1) {
              completedEdges.push(id);
            }
          }
        }

        // Remove completed edges
        for (const id of completedEdges) {
          next.delete(id);
        }

        return hasChanges || completedEdges.length > 0 ? next : prev;
      });

      // Fire callbacks
      for (const id of completedEdges) {
        onEdgeComplete?.(id);
      }

      // Update state
      setState((prev) => ({
        ...prev,
        time: currentTime,
        activeEdges: Array.from(edges.values()),
        isSettled: edges.size === 0,
      }));

      // Continue animation or fire completion callback
      if (edges.size > 0 || completedEdges.length > 0) {
        animationRef.current = requestAnimationFrame(animate);
      } else {
        onAllComplete?.();
      }
    };

    animationRef.current = requestAnimationFrame(animate);

    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
        animationRef.current = null;
      }
    };
  }, [edges.size, fullConfig.enabled, fullConfig.duration, onEdgeComplete, onAllComplete]);

  // Start a single edge
  const startEdge = useCallback(
    (
      edgeId: string,
      sourcePosition: [number, number, number],
      targetPosition: [number, number, number],
      edgeOptions?: { growthRate?: number }
    ) => {
      const waypoints = generateWaypoints(sourcePosition, targetPosition, edgeId);

      setEdges((prev) => {
        const next = new Map(prev);
        next.set(edgeId, {
          id: edgeId,
          sourceId: '',
          targetId: '',
          progress: 0,
          waypoints,
          growthRate: edgeOptions?.growthRate ?? 1,
          sourcePosition,
          targetPosition,
          startTime: performance.now(),
          delay: 0,
        });
        return next;
      });

      lastTimeRef.current = 0; // Reset time tracking
    },
    []
  );

  // Start multiple edges with optional staggering
  const startEdges = useCallback(
    (
      newEdges: Array<{
        id: string;
        source: [number, number, number];
        target: [number, number, number];
        growthRate?: number;
        delay?: number;
      }>
    ) => {
      const now = performance.now();

      setEdges((prev) => {
        const next = new Map(prev);

        for (const edge of newEdges) {
          const waypoints = generateWaypoints(edge.source, edge.target, edge.id);

          next.set(edge.id, {
            id: edge.id,
            sourceId: '',
            targetId: '',
            progress: 0,
            waypoints,
            growthRate: edge.growthRate ?? 1,
            sourcePosition: edge.source,
            targetPosition: edge.target,
            startTime: now,
            delay: edge.delay ?? 0,
          });
        }

        return next;
      });

      lastTimeRef.current = 0;
    },
    []
  );

  // Stop a specific edge
  const stopEdge = useCallback((edgeId: string) => {
    setEdges((prev) => {
      const next = new Map(prev);
      next.delete(edgeId);
      return next;
    });
  }, []);

  // Stop all edges
  const stopAll = useCallback(() => {
    setEdges(new Map());
    if (animationRef.current) {
      cancelAnimationFrame(animationRef.current);
      animationRef.current = null;
    }
  }, []);

  // Get edge path for rendering
  const getEdgePath = useCallback(
    (edgeId: string, segments = 20): Array<[number, number, number]> => {
      const edge = edges.get(edgeId);
      if (!edge) return [];

      const path: Array<[number, number, number]> = [];

      for (let i = 0; i <= segments; i++) {
        const t = (i / segments) * edge.progress;
        path.push(
          interpolatePath(
            edge.sourcePosition,
            edge.targetPosition,
            edge.waypoints,
            t / edge.progress // Normalize to current progress
          )
        );
      }

      return path;
    },
    [edges]
  );

  // Get edge progress
  const getEdgeProgress = useCallback(
    (edgeId: string): number => {
      return edges.get(edgeId)?.progress ?? 0;
    },
    [edges]
  );

  // Update rules
  const setRules = useCallback((newRules: Partial<GrowthRules>) => {
    setRulesState((prev) => ({ ...prev, ...newRules }));
  }, []);

  return {
    state,
    startEdge,
    startEdges,
    stopEdge,
    stopAll,
    getEdgePath,
    getEdgeProgress,
    isAnimating,
    activeEdgeIds,
    setRules,
    rules,
  };
}

// =============================================================================
// Exports
// =============================================================================

export default useGrowthAnimation;
