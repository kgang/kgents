import { useCallback } from 'react';
import type { GraphNode } from './state/types';
import type { DialecticDecision } from './types/dialectic';
import type { FeedbackMessage } from './useFeedbackMessage';

interface UseWitnessNavigationHandlersProps {
  currentNode: GraphNode | null;
  onSetDecisionStreamOpen: (open: boolean) => void;
  onSetSelectedDecision: (decision: DialecticDecision) => void;
  onSetDialogueViewOpen: (open: boolean) => void;
  showFeedback: (message: FeedbackMessage) => void;
  clearFeedback: () => void;
}

interface UseWitnessNavigationHandlersReturn {
  handleGoToMarks: () => Promise<void>;
  handleGoToWarrant: () => Promise<void>;
  handleGoToDecision: () => Promise<void>;
}

export function useWitnessNavigationHandlers({
  currentNode,
  onSetDecisionStreamOpen,
  onSetSelectedDecision,
  onSetDialogueViewOpen,
  showFeedback,
  clearFeedback,
}: UseWitnessNavigationHandlersProps): UseWitnessNavigationHandlersReturn {

  /**
   * gm - Navigate to witness marks for current node.
   */
  const handleGoToMarks = useCallback(async () => {
    if (!currentNode) return;

    try {
      const response = await fetch(`/api/witness/marks?path=${encodeURIComponent(currentNode.path)}`);
      if (!response.ok) {
        throw new Error(`Failed to fetch marks: ${response.statusText}`);
      }

      const marks = await response.json();
      console.info('[WitnessNav] Marks for node:', currentNode.path, marks);

      onSetDecisionStreamOpen(true);
      showFeedback({
        type: 'success',
        text: `Found ${marks.length || 0} marks for this node`,
      });
      setTimeout(clearFeedback, 3000);
    } catch (error) {
      console.error('[WitnessNav] Failed to fetch marks:', error);
      showFeedback({ type: 'error', text: 'Failed to fetch witness marks' });
      setTimeout(clearFeedback, 4000);
    }
  }, [currentNode, onSetDecisionStreamOpen, showFeedback, clearFeedback]);

  /**
   * gW - Navigate to warrant for current node.
   */
  const handleGoToWarrant = useCallback(async () => {
    if (!currentNode) return;

    try {
      const response = await fetch(`/api/witness/warrant?path=${encodeURIComponent(currentNode.path)}`);
      if (!response.ok) {
        throw new Error(`Failed to fetch warrant: ${response.statusText}`);
      }

      const warrant = await response.json();
      console.info('[WitnessNav] Warrant for node:', currentNode.path, warrant);

      showFeedback({
        type: 'success',
        text: warrant.reasoning || 'Warrant found',
      });
      setTimeout(clearFeedback, 5000);
    } catch (error) {
      console.error('[WitnessNav] Failed to fetch warrant:', error);
      showFeedback({ type: 'error', text: 'Failed to fetch warrant' });
      setTimeout(clearFeedback, 4000);
    }
  }, [currentNode, showFeedback, clearFeedback]);

  /**
   * gf - Navigate to decision (fusion) for current node.
   */
  const handleGoToDecision = useCallback(async () => {
    if (!currentNode) return;

    try {
      const response = await fetch(`/api/witness/fusion?path=${encodeURIComponent(currentNode.path)}`);
      if (!response.ok) {
        throw new Error(`Failed to fetch decision: ${response.statusText}`);
      }

      const decisions = await response.json();
      console.info('[WitnessNav] Decisions for node:', currentNode.path, decisions);

      if (decisions.length > 0) {
        onSetSelectedDecision(decisions[0]);
        onSetDialogueViewOpen(true);
      } else {
        showFeedback({ type: 'warning', text: 'No decisions found for this node' });
        setTimeout(clearFeedback, 3000);
      }
    } catch (error) {
      console.error('[WitnessNav] Failed to fetch decision:', error);
      showFeedback({ type: 'error', text: 'Failed to fetch decision' });
      setTimeout(clearFeedback, 4000);
    }
  }, [currentNode, onSetSelectedDecision, onSetDialogueViewOpen, showFeedback, clearFeedback]);

  return {
    handleGoToMarks,
    handleGoToWarrant,
    handleGoToDecision,
  };
}
