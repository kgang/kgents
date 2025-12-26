import { useCallback } from 'react';
import type { GraphNode } from './state/types';

interface UseDerivationNavigationProps {
  currentNode: GraphNode | null;
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
}

interface UseDerivationNavigationReturn {
  handleGoDerivationParent: () => void;
}

export function useDerivationNavigation({
  currentNode,
  loadNode,
  focusNode,
  onNavigate,
  onNodeFocus,
  witnessNavigation,
}: UseDerivationNavigationProps): UseDerivationNavigationReturn {

  /**
   * gD - Navigate to derivation parent.
   * Follows the derives_from edge to the parent in the derivation DAG.
   */
  const handleGoDerivationParent = useCallback(() => {
    if (!currentNode) return;

    // First, try explicit derivationParent field
    if (currentNode.derivationParent && loadNode) {
      onNavigate?.(currentNode.derivationParent);
      loadNode(currentNode.derivationParent).then((parentNode) => {
        if (parentNode) {
          // Witness the navigation (fire-and-forget)
          witnessNavigation('derivation', currentNode, parentNode, {
            keySequence: 'gD',
            viaEdge: 'derives_from',
          });
          focusNode(parentNode);
          onNodeFocus?.(parentNode);
        }
      });
      return;
    }

    // Fall back to derives_from edge
    const derivesFromEdge = currentNode.incomingEdges.find((e) => e.type === 'derives_from');
    if (derivesFromEdge && loadNode) {
      const parentPath = derivesFromEdge.source;
      onNavigate?.(parentPath);
      loadNode(parentPath).then((parentNode) => {
        if (parentNode) {
          // Witness the navigation (fire-and-forget)
          witnessNavigation('derivation', currentNode, parentNode, {
            keySequence: 'gD',
            viaEdge: 'derives_from',
          });
          focusNode(parentNode);
          onNodeFocus?.(parentNode);
        }
      });
    }
  }, [currentNode, loadNode, focusNode, onNavigate, onNodeFocus, witnessNavigation]);

  return {
    handleGoDerivationParent,
  };
}
