/**
 * usePolynomialState: Hook for managing polynomial visualization state.
 *
 * Foundation 3: Visible Polynomial State
 *
 * This hook manages:
 * - Current position tracking
 * - Transition history
 * - Valid next states calculation
 * - Optimistic updates for transitions
 */

import { useState, useCallback, useMemo } from 'react';
import type {
  PolynomialVisualization,
  PolynomialPosition,
  PolynomialHistoryEntry,
} from '../../api/types';

// =============================================================================
// Types
// =============================================================================

export interface PolynomialStateOptions {
  /** Initial visualization data */
  initial: PolynomialVisualization;
  /** Maximum history entries to keep */
  maxHistory?: number;
  /** Called when a transition is requested */
  onTransitionRequest?: (fromId: string, toId: string) => Promise<boolean>;
}

export interface PolynomialStateReturn {
  /** Current visualization state */
  visualization: PolynomialVisualization;
  /** Whether a transition is in progress */
  isTransitioning: boolean;
  /** Error from last transition attempt */
  transitionError: string | null;
  /** Advance to a new position */
  transition: (toPositionId: string) => Promise<boolean>;
  /** Reset to a specific position */
  reset: (toPositionId: string) => void;
  /** Get a position by ID */
  getPosition: (id: string) => PolynomialPosition | undefined;
  /** Check if a position is reachable from current */
  isReachable: (id: string) => boolean;
  /** Get the current position */
  currentPosition: PolynomialPosition | undefined;
}

// =============================================================================
// Helper Functions
// =============================================================================

/**
 * Create a new visualization with updated current position.
 */
function updateVisualization(
  viz: PolynomialVisualization,
  newCurrentId: string,
  historyEntry?: PolynomialHistoryEntry,
  maxHistory = 10,
): PolynomialVisualization {
  // Update positions to mark new current
  const positions = viz.positions.map((p) => ({
    ...p,
    is_current: p.id === newCurrentId,
  }));

  // Calculate valid directions from new position
  const validDirections = viz.edges
    .filter((e) => e.source === newCurrentId && e.is_valid)
    .map((e) => e.target);

  // Add to history if provided
  let history = viz.history;
  if (historyEntry) {
    history = [...history, historyEntry].slice(-maxHistory);
  }

  return {
    ...viz,
    positions,
    current: newCurrentId,
    valid_directions: validDirections,
    history,
  };
}

// =============================================================================
// Hook Implementation
// =============================================================================

/**
 * Hook for managing polynomial state machine visualization.
 *
 * @example
 * ```tsx
 * const { visualization, transition, isReachable } = usePolynomialState({
 *   initial: gardenerVisualization,
 *   onTransitionRequest: async (from, to) => {
 *     const result = await api.advanceSession(sessionId, to);
 *     return result.success;
 *   },
 * });
 *
 * return (
 *   <PolynomialDiagram
 *     visualization={visualization}
 *     onTransition={transition}
 *   />
 * );
 * ```
 */
export function usePolynomialState({
  initial,
  maxHistory = 10,
  onTransitionRequest,
}: PolynomialStateOptions): PolynomialStateReturn {
  const [visualization, setVisualization] = useState<PolynomialVisualization>(initial);
  const [isTransitioning, setIsTransitioning] = useState(false);
  const [transitionError, setTransitionError] = useState<string | null>(null);

  // Position lookup map
  const positionMap = useMemo(
    () => new Map(visualization.positions.map((p) => [p.id, p])),
    [visualization.positions],
  );

  // Valid directions set for fast lookup
  const validDirectionsSet = useMemo(
    () => new Set(visualization.valid_directions),
    [visualization.valid_directions],
  );

  // Get current position
  const currentPosition = useMemo(
    () => visualization.positions.find((p) => p.is_current),
    [visualization.positions],
  );

  // Get position by ID
  const getPosition = useCallback(
    (id: string) => positionMap.get(id),
    [positionMap],
  );

  // Check if position is reachable
  const isReachable = useCallback(
    (id: string) => validDirectionsSet.has(id),
    [validDirectionsSet],
  );

  // Transition to a new position
  const transition = useCallback(
    async (toPositionId: string): Promise<boolean> => {
      // Validate transition
      if (!validDirectionsSet.has(toPositionId)) {
        setTransitionError(`Cannot transition to ${toPositionId} from current position`);
        return false;
      }

      const fromPosition = currentPosition?.id;
      if (!fromPosition) {
        setTransitionError('No current position');
        return false;
      }

      setIsTransitioning(true);
      setTransitionError(null);

      try {
        // If there's a transition request handler, call it
        if (onTransitionRequest) {
          const success = await onTransitionRequest(fromPosition, toPositionId);
          if (!success) {
            setTransitionError('Transition request failed');
            setIsTransitioning(false);
            return false;
          }
        }

        // Update local state
        const historyEntry: PolynomialHistoryEntry = {
          from_position: fromPosition,
          to_position: toPositionId,
          timestamp: new Date().toISOString(),
        };

        setVisualization((prev) =>
          updateVisualization(prev, toPositionId, historyEntry, maxHistory),
        );

        setIsTransitioning(false);
        return true;
      } catch (err) {
        const message = err instanceof Error ? err.message : 'Unknown error';
        setTransitionError(message);
        setIsTransitioning(false);
        return false;
      }
    },
    [validDirectionsSet, currentPosition, onTransitionRequest, maxHistory],
  );

  // Reset to a specific position (no validation)
  const reset = useCallback(
    (toPositionId: string) => {
      setVisualization((prev) => updateVisualization(prev, toPositionId, undefined, maxHistory));
      setTransitionError(null);
    },
    [maxHistory],
  );

  return {
    visualization,
    isTransitioning,
    transitionError,
    transition,
    reset,
    getPosition,
    isReachable,
    currentPosition,
  };
}

export default usePolynomialState;
