/**
 * useLossNavigation — Loss-gradient navigation helpers
 *
 * "Navigate toward stability. The gradient IS the guide. The loss IS the landscape."
 *
 * Enables gl/gh commands for gradient-based navigation:
 * - gl: Go to lowest-loss neighbor (follow gradient toward stability)
 * - gh: Go to highest-loss neighbor (investigate instability)
 */

import { useState, useCallback } from 'react';
import { getNode } from '../api/zeroSeed';
import type { GraphNode } from './state/types';

// =============================================================================
// Types
// =============================================================================

export interface NeighborLoss {
  nodeId: string;
  loss: number;
  direction: 'incoming' | 'outgoing';
}

export interface LossNavigationResult {
  getNeighborLosses: (currentNode: GraphNode) => Promise<NeighborLoss[]>;
  findLowestLossNeighbor: (currentNode: GraphNode) => Promise<string | null>;
  findHighestLossNeighbor: (currentNode: GraphNode) => Promise<string | null>;
  loading: boolean;
  error: Error | null;
}

// =============================================================================
// Hook
// =============================================================================

/**
 * Hook for loss-based navigation.
 *
 * @returns Functions for navigating based on loss gradients
 *
 * @example
 * ```tsx
 * const { findLowestLossNeighbor, loading } = useLossNavigation();
 *
 * async function goToStability() {
 *   const target = await findLowestLossNeighbor(currentNode);
 *   if (target) navigate(target);
 * }
 * ```
 */
export function useLossNavigation(): LossNavigationResult {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  /**
   * Get loss values for all neighbors of a node.
   */
  const getNeighborLosses = useCallback(async (currentNode: GraphNode): Promise<NeighborLoss[]> => {
    setLoading(true);
    setError(null);

    try {
      // Collect all neighbor IDs (both incoming and outgoing)
      const neighborIds = new Set<string>();
      const directionMap = new Map<string, 'incoming' | 'outgoing'>();

      // Add outgoing edge targets
      currentNode.outgoingEdges.forEach((edge) => {
        neighborIds.add(edge.target);
        directionMap.set(edge.target, 'outgoing');
      });

      // Add incoming edge sources
      currentNode.incomingEdges.forEach((edge) => {
        neighborIds.add(edge.source);
        directionMap.set(edge.source, 'incoming');
      });

      if (neighborIds.size === 0) {
        return [];
      }

      // Fetch loss for each neighbor in parallel
      const lossPromises = Array.from(neighborIds).map(async (nodeId) => {
        try {
          const response = await getNode(nodeId);
          return {
            nodeId,
            loss: response.loss?.loss ?? 1.0, // Default to max loss if unknown
            direction: directionMap.get(nodeId)!,
          };
        } catch (err) {
          // If we can't fetch loss for a neighbor, skip it
          console.warn(`Failed to fetch loss for neighbor ${nodeId}:`, err);
          return null;
        }
      });

      const results = await Promise.all(lossPromises);
      const validResults = results.filter((r): r is NeighborLoss => r !== null);

      return validResults.sort((a, b) => a.loss - b.loss); // Sort by loss (ascending)
    } catch (err) {
      const error = err instanceof Error ? err : new Error(String(err));
      setError(error);
      return [];
    } finally {
      setLoading(false);
    }
  }, []);

  /**
   * Find the neighbor with the lowest loss (gradient toward stability).
   */
  const findLowestLossNeighbor = useCallback(
    async (currentNode: GraphNode): Promise<string | null> => {
      const neighbors = await getNeighborLosses(currentNode);
      if (neighbors.length === 0) return null;

      // Already sorted ascending, so first element is lowest
      return neighbors[0].nodeId;
    },
    [getNeighborLosses]
  );

  /**
   * Find the neighbor with the highest loss (investigate instability).
   */
  const findHighestLossNeighbor = useCallback(
    async (currentNode: GraphNode): Promise<string | null> => {
      const neighbors = await getNeighborLosses(currentNode);
      if (neighbors.length === 0) return null;

      // Already sorted ascending, so last element is highest
      return neighbors[neighbors.length - 1].nodeId;
    },
    [getNeighborLosses]
  );

  return {
    getNeighborLosses,
    findLowestLossNeighbor,
    findHighestLossNeighbor,
    loading,
    error,
  };
}

export default useLossNavigation;
