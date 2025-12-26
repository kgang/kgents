import { useCallback, useState } from 'react';

interface UseWitnessHandlersProps {
  dispatch: (action: { type: string; [key: string]: any }) => void;
}

interface UseWitnessHandlersReturn {
  witnessLoading: boolean;
  handleWitnessSave: (action: string, reasoning?: string, tags?: string[]) => Promise<void>;
  handleQuickMark: (tag: string) => Promise<void>;
}

export function useWitnessHandlers({ dispatch }: UseWitnessHandlersProps): UseWitnessHandlersReturn {
  const [witnessLoading, setWitnessLoading] = useState(false);

  const handleWitnessSave = useCallback(
    async (action: string, reasoning?: string, tags?: string[]) => {
      setWitnessLoading(true);
      try {
        await fetch('/api/witness/marks', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            action,
            reasoning: reasoning || null,
            principles: tags || [],
            author: 'kent',
          }),
        });
        dispatch({ type: 'EXIT_WITNESS' });
        console.info('[useWitnessHandlers] Witness mark saved:', action);
      } catch (error) {
        console.error('[useWitnessHandlers] Failed to save mark:', error);
      } finally {
        setWitnessLoading(false);
      }
    },
    [dispatch]
  );

  const handleQuickMark = useCallback(
    async (tag: string) => {
      setWitnessLoading(true);
      try {
        const actionTemplates: Record<string, string> = {
          eureka: 'Eureka moment',
          gotcha: 'Gotcha',
          taste: 'Taste decision',
          friction: 'Friction point',
          joy: 'Joy moment',
          veto: 'Veto',
        };

        const action = actionTemplates[tag] || tag;

        await fetch('/api/witness/marks', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            action,
            reasoning: null,
            principles: [tag],
            author: 'kent',
          }),
        });

        dispatch({ type: 'EXIT_WITNESS' });
        console.info('[useWitnessHandlers] Quick mark saved:', tag);
      } catch (error) {
        console.error('[useWitnessHandlers] Failed to save quick mark:', error);
      } finally {
        setWitnessLoading(false);
      }
    },
    [dispatch]
  );

  return {
    witnessLoading,
    handleWitnessSave,
    handleQuickMark,
  };
}
