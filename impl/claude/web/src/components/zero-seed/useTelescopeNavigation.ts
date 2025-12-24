/**
 * useTelescopeNavigation - Hook for telescope navigation logic
 *
 * Provides navigation utilities for loss-guided exploration:
 * - goLowestLoss: Navigate to the node with lowest loss
 * - goHighestLoss: Navigate to the node with highest loss
 * - followGradient: Follow the gradient from current focal point
 */

import { useCallback, useMemo } from 'react';
import type {
  GaloisTelescopeState,
  NodeProjection,
  NodeId,
  NavigationAction,
} from './types';

interface UseTelescopeNavigationProps {
  state: GaloisTelescopeState;
  projections: NodeProjection[];
  onNavigate?: (action: NavigationAction, nodeId?: NodeId) => void;
}

interface TelescopeNavigationResult {
  /** Navigate to the node with the lowest loss */
  goLowestLoss: () => void;
  /** Navigate to the node with the highest loss */
  goHighestLoss: () => void;
  /** Follow the gradient from the current focal point */
  followGradient: () => void;
  /** Get the node with the lowest loss */
  lowestLossNode: NodeProjection | null;
  /** Get the node with the highest loss */
  highestLossNode: NodeProjection | null;
  /** Check if at a local minimum */
  atLocalMinimum: boolean;
}

export function useTelescopeNavigation({
  state,
  projections,
  onNavigate,
}: UseTelescopeNavigationProps): TelescopeNavigationResult {
  // Find node with lowest loss
  const lowestLossNode = useMemo(() => {
    if (projections.length === 0) return null;

    let lowest: NodeProjection | null = null;
    let lowestLoss = Infinity;

    for (const proj of projections) {
      const loss = proj.annotation?.loss ?? 1;
      if (loss < lowestLoss) {
        lowestLoss = loss;
        lowest = proj;
      }
    }

    return lowest;
  }, [projections]);

  // Find node with highest loss
  const highestLossNode = useMemo(() => {
    if (projections.length === 0) return null;

    let highest: NodeProjection | null = null;
    let highestLoss = -Infinity;

    for (const proj of projections) {
      const loss = proj.annotation?.loss ?? 0;
      if (loss > highestLoss) {
        highestLoss = loss;
        highest = proj;
      }
    }

    return highest;
  }, [projections]);

  // Check if current focal point is at a local minimum
  const atLocalMinimum = useMemo(() => {
    if (!state.focal_point) return false;

    const focal = projections.find((p) => p.node_id === state.focal_point);
    if (!focal?.gradient) return true; // No gradient means stable

    // If gradient magnitude is very small, we're at a local minimum
    return focal.gradient.magnitude < 0.01;
  }, [state.focal_point, projections]);

  // Navigate to lowest loss node
  const goLowestLoss = useCallback(() => {
    if (lowestLossNode) {
      onNavigate?.('go_lowest_loss', lowestLossNode.node_id);
    }
  }, [lowestLossNode, onNavigate]);

  // Navigate to highest loss node
  const goHighestLoss = useCallback(() => {
    if (highestLossNode) {
      onNavigate?.('go_highest_loss', highestLossNode.node_id);
    }
  }, [highestLossNode, onNavigate]);

  // Follow the gradient from current position
  const followGradient = useCallback(() => {
    if (!state.focal_point) {
      // If no focal point, go to highest loss as starting point
      if (highestLossNode) {
        onNavigate?.('follow_gradient', highestLossNode.node_id);
      }
      return;
    }

    const focal = projections.find((p) => p.node_id === state.focal_point);
    if (!focal?.gradient) return;

    // Find the node in the direction of the gradient
    // (Simplified: find nearest node in gradient direction with lower loss)
    const focalLoss = focal.annotation?.loss ?? 0;
    const gradientDir = {
      x: focal.gradient.x,
      y: focal.gradient.y,
    };

    let bestCandidate: NodeProjection | null = null;
    let bestScore = -Infinity;

    for (const proj of projections) {
      if (proj.node_id === state.focal_point) continue;

      const projLoss = proj.annotation?.loss ?? 1;
      if (projLoss >= focalLoss) continue; // Only consider lower loss nodes

      // Calculate dot product with gradient direction
      const dx = proj.position.x - focal.position.x;
      const dy = proj.position.y - focal.position.y;
      const dist = Math.sqrt(dx * dx + dy * dy);
      if (dist === 0) continue;

      const dotProduct =
        (dx / dist) * gradientDir.x + (dy / dist) * gradientDir.y;

      // Score based on alignment with gradient and loss reduction
      const lossReduction = focalLoss - projLoss;
      const score = dotProduct * lossReduction;

      if (score > bestScore) {
        bestScore = score;
        bestCandidate = proj;
      }
    }

    if (bestCandidate) {
      onNavigate?.('follow_gradient', bestCandidate.node_id);
    }
  }, [state.focal_point, projections, highestLossNode, onNavigate]);

  return {
    goLowestLoss,
    goHighestLoss,
    followGradient,
    lowestLossNode,
    highestLossNode,
    atLocalMinimum,
  };
}

export default useTelescopeNavigation;
