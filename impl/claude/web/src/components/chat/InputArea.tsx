/**
 * InputArea — Message input with @mention support
 *
 * Features:
 * - Textarea with Shift+Enter for newlines
 * - Submit on Enter
 * - @mention picker (placeholder integration)
 * - Fork/rewind controls
 *
 * Vim-inspired: modal editing mentality, keyboard-first.
 *
 * @see spec/protocols/chat-web.md Part X
 */

import { memo, useCallback, useRef, useState, KeyboardEvent } from 'react';
import { ForkModal } from './ForkModal';
import './InputArea.css';

// =============================================================================
// Types
// =============================================================================

export interface InputAreaProps {
  onSend: (message: string) => Promise<void>;
  onRewind: (turns: number) => Promise<void>;
  onFork?: (branchName: string, forkPoint?: number) => Promise<void>;
  disabled?: boolean;
  compact?: boolean;
  currentTurn?: number;
  existingBranches?: string[];
}

// =============================================================================
// Main Component
// =============================================================================

/**
 * InputArea — Message input with mentions and controls
 */
export const InputArea = memo(function InputArea({
  onSend,
  onRewind,
  onFork,
  disabled = false,
  compact = false,
  currentTurn = 0,
  existingBranches = [],
}: InputAreaProps) {
  const [message, setMessage] = useState('');
  const [isSending, setIsSending] = useState(false);
  const [forkModalOpen, setForkModalOpen] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-resize textarea
  const handleInput = useCallback((e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const target = e.target;
    setMessage(target.value);

    // Auto-resize
    target.style.height = 'auto';
    target.style.height = `${Math.min(target.scrollHeight, 200)}px`;
  }, []);

  // Send message
  const handleSend = useCallback(async () => {
    if (!message.trim() || disabled || isSending) return;

    setIsSending(true);
    try {
      await onSend(message);
      setMessage('');

      // Reset textarea height
      if (textareaRef.current) {
        textareaRef.current.style.height = 'auto';
      }
    } finally {
      setIsSending(false);
    }
  }, [message, onSend, disabled, isSending]);

  // Keyboard handling
  const handleKeyDown = useCallback(
    (e: KeyboardEvent<HTMLTextAreaElement>) => {
      // Enter (without Shift) = send
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        handleSend();
      }

      // Ctrl+K = rewind 1 turn (vim-inspired)
      if (e.key === 'k' && (e.ctrlKey || e.metaKey)) {
        e.preventDefault();
        onRewind(1);
      }
    },
    [handleSend, onRewind]
  );

  // Rewind handler
  const handleRewindClick = useCallback(() => {
    // eslint-disable-next-line no-alert
    const turns = window.prompt('Rewind how many turns?', '1');
    if (turns) {
      const n = parseInt(turns, 10);
      if (!isNaN(n) && n > 0) {
        onRewind(n);
      }
    }
  }, [onRewind]);

  // Fork handlers
  const handleForkClick = useCallback(() => {
    setForkModalOpen(true);
  }, []);

  const handleForkConfirm = useCallback(
    async (branchName: string, forkPoint?: number) => {
      if (onFork) {
        await onFork(branchName, forkPoint);
      }
    },
    [onFork]
  );

  const handleForkClose = useCallback(() => {
    setForkModalOpen(false);
  }, []);

  return (
    <div className={`input-area ${compact ? 'input-area--compact' : ''}`}>
      {/* Controls row (fork/rewind) */}
      {!compact && (
        <div className="input-area__controls">
          <button
            className="input-area__control-button"
            onClick={handleRewindClick}
            disabled={disabled}
            title="Rewind conversation (Ctrl+K)"
          >
            ↶ Rewind
          </button>
          {/* Fork button */}
          <button
            className="input-area__control-button"
            onClick={handleForkClick}
            disabled={disabled || !onFork}
            title="Fork conversation"
          >
            ⑂ Fork
          </button>
        </div>
      )}

      {/* Input row */}
      <div className="input-area__input-row">
        <textarea
          ref={textareaRef}
          className="input-area__textarea"
          value={message}
          onChange={handleInput}
          onKeyDown={handleKeyDown}
          placeholder="Type a message... (@mention for context, Enter to send, Shift+Enter for newline)"
          disabled={disabled || isSending}
          rows={1}
        />

        <button
          className="input-area__send-button"
          onClick={handleSend}
          disabled={!message.trim() || disabled || isSending}
          title="Send message (Enter)"
        >
          {isSending ? '⏳' : '↵'}
        </button>
      </div>

      {/* Mention picker placeholder */}
      {message.includes('@') && (
        <div className="input-area__mention-hint">
          <span className="input-area__mention-hint-text">
            Type @file, @symbol, @spec, @witness, or @web
          </span>
        </div>
      )}

      {/* Fork Modal */}
      <ForkModal
        isOpen={forkModalOpen}
        onClose={handleForkClose}
        onConfirm={handleForkConfirm}
        currentTurn={currentTurn}
        existingBranches={existingBranches}
        canFork={existingBranches.length < 3}
      />
    </div>
  );
});

export default InputArea;
