/**
 * DialoguePane — The co-thinking interface
 *
 * Where Kent and K-gent think together. Not a chatbot — a collaborative space.
 *
 * "The proof IS the decision."
 */

import { useCallback, useRef, useState } from 'react';

import { DialogueMessage } from './DialogueMessage';
import type { DialogueMessage as DialogueMessageData, FocusType } from './useMembrane';

import './DialoguePane.css';

// =============================================================================
// Types
// =============================================================================

interface DialoguePaneProps {
  dialogueHistory: DialogueMessageData[];
  onAppendDialogue: (role: 'user' | 'assistant', content: string) => void;
  onFocusChange: (type: FocusType, path?: string) => void;
  onCrystallize: (content: string) => Promise<void>;
}

// =============================================================================
// Component
// =============================================================================

export function DialoguePane({
  dialogueHistory,
  onAppendDialogue,
  onFocusChange,
  onCrystallize,
}: DialoguePaneProps) {
  const [input, setInput] = useState('');
  const [isThinking, setIsThinking] = useState(false);
  const inputRef = useRef<HTMLTextAreaElement>(null);
  const historyRef = useRef<HTMLDivElement>(null);

  const handleSubmit = useCallback(async () => {
    const trimmed = input.trim();
    if (!trimmed || isThinking) return;

    // Add user message
    onAppendDialogue('user', trimmed);
    setInput('');

    // Focus input for next message
    inputRef.current?.focus();

    // Scroll to bottom
    setTimeout(() => {
      historyRef.current?.scrollTo({
        top: historyRef.current.scrollHeight,
        behavior: 'smooth',
      });
    }, 100);

    // Simulate thinking (TODO: wire to real backend)
    setIsThinking(true);
    await new Promise<void>((resolve) => {
      setTimeout(resolve, 1000);
    });

    // Add assistant response (placeholder)
    onAppendDialogue(
      'assistant',
      `I understand you're thinking about: "${trimmed}"\n\nThis is a placeholder response. Soon I'll be wired to the real K-gent backend.`
    );
    setIsThinking(false);

    // Scroll again after response
    setTimeout(() => {
      historyRef.current?.scrollTo({
        top: historyRef.current.scrollHeight,
        behavior: 'smooth',
      });
    }, 100);
  }, [input, isThinking, onAppendDialogue]);

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        handleSubmit();
      }
    },
    [handleSubmit]
  );

  const handleCrystallize = useCallback(async () => {
    const lastMessage = dialogueHistory[dialogueHistory.length - 1];
    if (lastMessage) {
      await onCrystallize(lastMessage.content);
    }
  }, [dialogueHistory, onCrystallize]);

  return (
    <div className="dialogue-pane">
      {/* History */}
      <div className="dialogue-pane__history" ref={historyRef}>
        {dialogueHistory.length === 0 ? (
          <div className="dialogue-pane__empty">
            <p className="dialogue-pane__prompt">What are you thinking about?</p>
            <p className="dialogue-pane__hint">Type a thought, question, or file path to begin</p>
          </div>
        ) : (
          dialogueHistory.map((msg) => (
            <DialogueMessage key={msg.id} message={msg} onFocusRequest={onFocusChange} />
          ))
        )}

        {isThinking && (
          <div className="dialogue-pane__thinking">
            <span className="dialogue-pane__thinking-dot" />
            <span className="dialogue-pane__thinking-dot" />
            <span className="dialogue-pane__thinking-dot" />
          </div>
        )}
      </div>

      {/* Input */}
      <div className="dialogue-pane__input-container">
        <textarea
          ref={inputRef}
          className="dialogue-pane__input"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="What are you thinking about?"
          rows={1}
          disabled={isThinking}
        />

        <div className="dialogue-pane__actions">
          <button
            className="dialogue-pane__send"
            onClick={handleSubmit}
            disabled={!input.trim() || isThinking}
          >
            Send
          </button>

          {dialogueHistory.length > 0 && (
            <button
              className="dialogue-pane__crystallize"
              onClick={handleCrystallize}
              title="Crystallize the last message to witness"
            >
              Crystallize
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
