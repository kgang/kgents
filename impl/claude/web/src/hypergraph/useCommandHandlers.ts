import { useCallback } from 'react';
import type { GraphNode } from './state/types';
import type { FeedbackMessage } from './useFeedbackMessage';

interface UseCommandHandlersProps {
  dispatch: (action: { type: string; [key: string]: any }) => void;
  currentNode: GraphNode | null;
  kblockHook: {
    kblock: { isDirty: boolean } | null;
    checkpoint: (name: string) => Promise<string | null>;
    rewind: (checkpointId: string) => Promise<void>;
  };
  handleWrite: (message?: string) => Promise<boolean>;
  handleQuit: (force: boolean) => Promise<boolean>;
  loadNode?: (path: string) => Promise<GraphNode | null>;
  focusNode: (node: GraphNode) => void;
  onNavigate?: (path: string) => void;
  onNodeFocus?: (node: GraphNode) => void;
  showFeedback: (message: FeedbackMessage) => void;
  clearFeedback: () => void;
}

interface UseCommandHandlersReturn {
  handleCommand: (command: string) => Promise<void>;
}

export function useCommandHandlers({
  dispatch,
  currentNode: _currentNode, // Reserved for future :goto command
  kblockHook,
  handleWrite,
  handleQuit,
  loadNode: _loadNode, // Reserved for future :e command
  focusNode: _focusNode, // Reserved for future navigation
  onNavigate: _onNavigate, // Reserved for future navigation
  onNodeFocus: _onNodeFocus, // Reserved for future navigation
  showFeedback,
  clearFeedback,
}: UseCommandHandlersProps): UseCommandHandlersReturn {
  // Suppress unused warnings - these are reserved for future commands
  void _currentNode;
  void _loadNode;
  void _focusNode;
  void _onNavigate;
  void _onNodeFocus;
  const handleCommand = useCallback(
    async (command: string) => {
      dispatch({ type: 'EXIT_COMMAND' });

      const rawCmd = command.trim();
      const [cmd, ...args] = rawCmd.split(/\s+/);

      if (cmd === 'w' || cmd === 'write') {
        const message = args.join(' ') || undefined;
        await handleWrite(message);
      } else if (cmd === 'wq') {
        const success = await handleWrite();
        if (success) {
          await handleQuit(false);
        }
      } else if (cmd === 'q!' || rawCmd === 'q!') {
        await handleQuit(true);
      } else if (cmd === 'q' || cmd === 'quit') {
        await handleQuit(false);
      } else if (cmd === 'checkpoint' || cmd === 'cp') {
        const name = args.join(' ') || `checkpoint-${Date.now()}`;
        const cpId = await kblockHook.checkpoint(name);
        if (cpId) {
          dispatch({ type: 'KBLOCK_CHECKPOINT', id: cpId, message: name });
          console.info('[useCommandHandlers] Created checkpoint:', cpId, name);
        }
      } else if (cmd === 'rewind') {
        const checkpointId = args[0];
        if (!checkpointId) {
          console.warn('[useCommandHandlers] :rewind requires checkpoint ID');
          return;
        }
        await kblockHook.rewind(checkpointId);
        console.info('[useCommandHandlers] Rewound to checkpoint:', checkpointId);
      } else if (cmd === 'ag') {
        const agentesePath = args[0];
        const agentArgs = args.slice(1).join(' ');

        if (!agentesePath) {
          showFeedback({ type: 'warning', text: ':ag requires a path' });
          setTimeout(clearFeedback, 3000);
          return;
        }

        try {
          const response = await fetch('/api/agentese/invoke', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              path: agentesePath,
              args: agentArgs || undefined,
              observer: 'kent',
            }),
          });

          if (response.ok) {
            const result = await response.json();
            console.info('[useCommandHandlers] AGENTESE result:', result);
            showFeedback({ type: 'success', text: `✓ ${agentesePath}` });
          } else {
            const error = await response.text();
            console.error('[useCommandHandlers] AGENTESE error:', error);
            showFeedback({ type: 'error', text: `AGENTESE: ${error}` });
          }
          setTimeout(clearFeedback, 3000);
        } catch (err) {
          console.error('[useCommandHandlers] AGENTESE invoke failed:', err);
          showFeedback({ type: 'error', text: 'AGENTESE invoke failed' });
          setTimeout(clearFeedback, 4000);
        }
      } else if (cmd === 'crystallize' || cmd === 'crystal') {
        const notes = args.join(' ') || undefined;

        try {
          const response = await fetch('/api/witness/crystallize', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ notes }),
          });

          if (response.ok) {
            const result = await response.json();
            console.info('[useCommandHandlers] Crystallization result:', result);
            showFeedback({
              type: 'success',
              text: `✓ Session crystallized (${result.crystal?.level || 'SESSION'})`,
            });
          } else {
            const error = await response.text();
            console.error('[useCommandHandlers] Crystallization error:', error);
            showFeedback({ type: 'error', text: `Crystallization: ${error}` });
          }
          setTimeout(clearFeedback, 3000);
        } catch (err) {
          console.error('[useCommandHandlers] Crystallization failed:', err);
          showFeedback({ type: 'error', text: 'Crystallization failed' });
          setTimeout(clearFeedback, 4000);
        }
      }
    },
    [dispatch, handleWrite, handleQuit, kblockHook, showFeedback, clearFeedback]
  );

  return { handleCommand };
}
