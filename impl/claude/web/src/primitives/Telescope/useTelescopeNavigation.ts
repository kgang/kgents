/**
 * useTelescopeNavigation Hook
 *
 * Loss-guided navigation logic for telescope traversal.
 */

import { useCallback } from 'react';
import type { NodeProjection, NavigationDirection } from './types';
import {
  findLowestLossNode,
  findHighestLossNode,
  followGradient,
} from './utils';

interface UseTelescopeNavigationProps {
  nodes: NodeProjection[];
  gradients: Map<string, { x: number; y: number; magnitude: number }>;
  onNavigate?: (nodeId: string, direction: NavigationDirection) => void;
}

/**
 * Provides navigation helpers for telescope traversal.
 */
export function useTelescopeNavigation({
  nodes,
  gradients,
  onNavigate,
}: UseTelescopeNavigationProps) {
  /**
   * Navigate to node with lowest loss (most stable).
   */
  const goLowestLoss = useCallback(() => {
    const nodeId = findLowestLossNode(nodes);
    if (nodeId && onNavigate) {
      onNavigate(nodeId, 'lowest');
    }
    return nodeId;
  }, [nodes, onNavigate]);

  /**
   * Navigate to node with highest loss (needs attention).
   */
  const goHighestLoss = useCallback(() => {
    const nodeId = findHighestLossNode(nodes);
    if (nodeId && onNavigate) {
      onNavigate(nodeId, 'highest');
    }
    return nodeId;
  }, [nodes, onNavigate]);

  /**
   * Follow gradient from current node toward stability.
   */
  const followGradientFrom = useCallback(
    (currentNodeId: string) => {
      const nextNodeId = followGradient(currentNodeId, gradients, nodes);
      if (nextNodeId && onNavigate) {
        onNavigate(nextNodeId, 'gradient');
      }
      return nextNodeId;
    },
    [nodes, gradients, onNavigate]
  );

  return {
    goLowestLoss,
    goHighestLoss,
    followGradientFrom,
  };
}
