import { useCallback, useState } from 'react';
import type { GraphNode } from './state/types';
import type { FeedbackMessage } from './useFeedbackMessage';

interface LossNavigation {
  getNeighborLosses: (node: GraphNode) => Promise<Array<{ nodeId: string; loss: number }>>;
}

interface UseLossNavigationHandlersProps {
  currentNode: GraphNode | null;
  lossNav: LossNavigation;
  loadNode?: (path: string) => Promise<GraphNode | null>;
  focusNode: (node: GraphNode) => void;
  onNavigate?: (path: string) => void;
  onNodeFocus?: (node: GraphNode) => void;
  witnessNavigation: (
    type: string,
    fromNode: GraphNode | null,
    toNode: GraphNode,
    metadata: Record<string, unknown>
  ) => void;
  showFeedback: (message: FeedbackMessage) => void;
  clearFeedback: () => void;
}

interface UseLossNavigationHandlersReturn {
  focalDistance: number;
  handleGoLowestLoss: () => Promise<void>;
  handleGoHighestLoss: () => Promise<void>;
  handleZoomOut: () => void;
  handleZoomIn: () => void;
}

export function useLossNavigationHandlers({
  currentNode,
  lossNav,
  loadNode,
  focusNode,
  onNavigate,
  onNodeFocus,
  witnessNavigation,
  showFeedback,
  clearFeedback,
}: UseLossNavigationHandlersProps): UseLossNavigationHandlersReturn {
  const [focalDistance, setFocalDistance] = useState(1.0);

  const handleGoLowestLoss = useCallback(async () => {
    if (!currentNode) return;

    const neighbors = await lossNav.getNeighborLosses(currentNode);
    if (neighbors.length === 0) {
      showFeedback({ type: 'warning', text: 'No neighbors found' });
      setTimeout(clearFeedback, 3000);
      return;
    }

    const lowest = neighbors[0]; // Already sorted ascending
    const targetId = lowest.nodeId;

    if (!loadNode) return;

    onNavigate?.(targetId);
    loadNode(targetId).then((node) => {
      if (node) {
        witnessNavigation('loss_gradient', currentNode, node, {
          keySequence: 'gl',
          lossValue: lowest.loss,
        });

        focusNode(node);
        onNodeFocus?.(node);

        const lossValue = (lowest.loss * 100).toFixed(1);
        showFeedback({
          type: 'success',
          text: `Navigated to lowest-loss neighbor (loss: ${lossValue}%)`,
        });
        setTimeout(clearFeedback, 3000);
        console.info('[LossNav] Navigated to lowest-loss neighbor:', targetId, lowest.loss);
      }
    });
  }, [currentNode, lossNav, loadNode, focusNode, onNavigate, onNodeFocus, witnessNavigation, showFeedback, clearFeedback]);

  const handleGoHighestLoss = useCallback(async () => {
    if (!currentNode) return;

    const neighbors = await lossNav.getNeighborLosses(currentNode);
    if (neighbors.length === 0) {
      showFeedback({ type: 'warning', text: 'No neighbors found' });
      setTimeout(clearFeedback, 3000);
      return;
    }

    const highest = neighbors[neighbors.length - 1];
    const targetId = highest.nodeId;

    if (!loadNode) return;

    onNavigate?.(targetId);
    loadNode(targetId).then((node) => {
      if (node) {
        witnessNavigation('loss_gradient', currentNode, node, {
          keySequence: 'gh',
          lossValue: highest.loss,
        });

        focusNode(node);
        onNodeFocus?.(node);

        const lossValue = (highest.loss * 100).toFixed(1);
        showFeedback({
          type: 'warning',
          text: `Navigated to highest-loss neighbor (loss: ${lossValue}%)`,
        });
        setTimeout(clearFeedback, 3000);
        console.info('[LossNav] Navigated to highest-loss neighbor:', targetId, highest.loss);
      }
    });
  }, [currentNode, lossNav, loadNode, focusNode, onNavigate, onNodeFocus, witnessNavigation, showFeedback, clearFeedback]);

  const handleZoomOut = useCallback(() => {
    setFocalDistance((prev) => {
      const newDistance = prev * 10;
      showFeedback({
        type: 'success',
        text: `Zoomed out (focal distance: ${newDistance.toFixed(2)})`,
      });
      setTimeout(clearFeedback, 2000);
      console.info('[LossNav] Zoomed out, focal distance:', newDistance);
      return newDistance;
    });
  }, [showFeedback, clearFeedback]);

  const handleZoomIn = useCallback(() => {
    setFocalDistance((prev) => {
      const newDistance = Math.max(0.01, prev / 10);
      showFeedback({
        type: 'success',
        text: `Zoomed in (focal distance: ${newDistance.toFixed(2)})`,
      });
      setTimeout(clearFeedback, 2000);
      console.info('[LossNav] Zoomed in, focal distance:', newDistance);
      return newDistance;
    });
  }, [showFeedback, clearFeedback]);

  return {
    focalDistance,
    handleGoLowestLoss,
    handleGoHighestLoss,
    handleZoomOut,
    handleZoomIn,
  };
}
