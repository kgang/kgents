/**
 * DialoguePane — The co-thinking interface
 *
 * Where Kent and K-gent think together. Not a chatbot — a collaborative space.
 *
 * "The proof IS the decision."
 */

import { useCallback, useRef, useState } from 'react';

import { DialogueMessage } from './DialogueMessage';
import type {
  CrystallizeResult,
  DialogueMessage as DialogueMessageData,
  FocusType,
} from './useMembrane';
import type { IsolationState } from './useKBlock';

import './DialoguePane.css';

// =============================================================================
// Types
// =============================================================================

interface DialoguePaneProps {
  dialogueHistory: DialogueMessageData[];
  onAppendDialogue: (role: 'user' | 'assistant', content: string) => Promise<void>;
  onFocusChange: (type: FocusType, path?: string) => void;
  onCrystallize: (reasoning?: string) => Promise<CrystallizeResult>;
  // K-Block state (Option C)
  kblockIsolation?: IsolationState;
  kblockIsDirty?: boolean;
}

// =============================================================================
// Component
// =============================================================================

export function DialoguePane({
  dialogueHistory,
  onAppendDialogue,
  onFocusChange,
  onCrystallize,
  kblockIsolation = 'PRISTINE',
  kblockIsDirty = false,
}: DialoguePaneProps) {
  const [input, setInput] = useState('');
  const [isThinking, setIsThinking] = useState(false);
  const [isCrystallizing, setIsCrystallizing] = useState(false);
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

  // Crystallize = harness.save() — thoughts escape to cosmos
  const handleCrystallize = useCallback(async () => {
    if (!kblockIsDirty || isCrystallizing) return;

    setIsCrystallizing(true);
    try {
      const lastMessage = dialogueHistory[dialogueHistory.length - 1];
      const reasoning = lastMessage
        ? `Crystallized dialogue ending with: "${lastMessage.content.slice(0, 50)}..."`
        : 'Crystallized dialogue session';

      const result = await onCrystallize(reasoning);

      if (result.success) {
        console.log(`Crystallized ${result.messageCount || 0} messages (block: ${result.blockId})`);
      } else {
        console.error('Crystallize failed:', result.error);
      }
    } finally {
      setIsCrystallizing(false);
    }
  }, [dialogueHistory, kblockIsDirty, isCrystallizing, onCrystallize]);

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

          {/* K-Block state indicator */}
          {kblockIsDirty && (
            <span
              className={`dialogue-pane__kblock-state dialogue-pane__kblock-state--${kblockIsolation.toLowerCase()}`}
              title={`K-Block: ${kblockIsolation} (isolated until crystallized)`}
            >
              {kblockIsolation === 'DIRTY' ? '◇' : '◆'}
            </span>
          )}

          {/* Crystallize = harness.save() */}
          {dialogueHistory.length > 0 && (
            <button
              className={`dialogue-pane__crystallize ${isCrystallizing ? 'dialogue-pane__crystallize--loading' : ''}`}
              onClick={handleCrystallize}
              disabled={!kblockIsDirty || isCrystallizing}
              title={
                kblockIsDirty
                  ? 'Crystallize thoughts → escape to cosmos'
                  : 'No changes to crystallize'
              }
            >
              {isCrystallizing ? 'Crystallizing...' : 'Crystallize ⬡'}
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
