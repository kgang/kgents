import { useCallback, useState } from 'react';
import type { DialecticDecision, QuickDecisionInput, FullDialecticInput } from './types/dialectic';

interface FeedbackMessage {
  type: 'success' | 'warning' | 'error';
  text: string;
}

interface UseDialecticHandlersProps {
  dialectic: {
    refresh: () => Promise<void>;
  };
  onSetDialecticModalOpen: (open: boolean) => void;
  onSetDialogueViewOpen: (open: boolean) => void;
  onSetDecisionStreamOpen: (open: boolean) => void;
  onSetVetoPanelOpen: (open: boolean) => void;
  onSetSelectedDecision: (decision: DialecticDecision | null) => void;
  onSetFeedbackMessage: (message: FeedbackMessage | null) => void;
  selectedDecision: DialecticDecision | null;
}

interface UseDialecticHandlersReturn {
  dialecticLoading: boolean;
  handleDecisionSave: (input: QuickDecisionInput | FullDialecticInput) => Promise<void>;
  handleVeto: (reason?: string) => Promise<void>;
  handleDecisionClick: (decision: DialecticDecision) => void;
}

export function useDialecticHandlers({
  dialectic,
  onSetDialecticModalOpen,
  onSetDialogueViewOpen,
  onSetDecisionStreamOpen,
  onSetVetoPanelOpen,
  onSetSelectedDecision,
  onSetFeedbackMessage,
  selectedDecision,
}: UseDialecticHandlersProps): UseDialecticHandlersReturn {
  const [dialecticLoading, setDialecticLoading] = useState(false);

  const handleDecisionSave = useCallback(
    async (input: QuickDecisionInput | FullDialecticInput) => {
      setDialecticLoading(true);
      try {
        const response = await fetch('/api/witness/fusion', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(input),
        });

        if (!response.ok) {
          throw new Error(`Failed to save decision: ${response.statusText}`);
        }

        const decision = await response.json();
        console.info('[useDialecticHandlers] Decision saved:', decision);

        await dialectic.refresh();
        onSetDialecticModalOpen(false);

        onSetFeedbackMessage({ type: 'success', text: 'Decision saved' });
        setTimeout(() => onSetFeedbackMessage(null), 3000);
      } catch (error) {
        console.error('[useDialecticHandlers] Failed to save decision:', error);
        onSetFeedbackMessage({ type: 'error', text: 'Failed to save decision' });
        setTimeout(() => onSetFeedbackMessage(null), 4000);
      } finally {
        setDialecticLoading(false);
      }
    },
    [dialectic, onSetDialecticModalOpen, onSetFeedbackMessage]
  );

  const handleVeto = useCallback(
    async (reason?: string) => {
      if (!selectedDecision) return;

      setDialecticLoading(true);
      try {
        const response = await fetch(`/api/witness/fusion/${selectedDecision.id}/veto`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ reason }),
        });

        if (!response.ok) {
          throw new Error(`Failed to veto decision: ${response.statusText}`);
        }

        console.info('[useDialecticHandlers] Decision vetoed:', selectedDecision.id);

        await dialectic.refresh();
        onSetVetoPanelOpen(false);
        onSetDialogueViewOpen(false);

        onSetFeedbackMessage({ type: 'success', text: 'Decision vetoed' });
        setTimeout(() => onSetFeedbackMessage(null), 3000);
      } catch (error) {
        console.error('[useDialecticHandlers] Failed to veto decision:', error);
        onSetFeedbackMessage({ type: 'error', text: 'Failed to veto decision' });
        setTimeout(() => onSetFeedbackMessage(null), 4000);
      } finally {
        setDialecticLoading(false);
      }
    },
    [selectedDecision, dialectic, onSetVetoPanelOpen, onSetDialogueViewOpen, onSetFeedbackMessage]
  );

  const handleDecisionClick = useCallback(
    (decision: DialecticDecision) => {
      onSetSelectedDecision(decision);
      onSetDialogueViewOpen(true);
      onSetDecisionStreamOpen(false);
    },
    [onSetSelectedDecision, onSetDialogueViewOpen, onSetDecisionStreamOpen]
  );

  return {
    dialecticLoading,
    handleDecisionSave,
    handleVeto,
    handleDecisionClick,
  };
}
