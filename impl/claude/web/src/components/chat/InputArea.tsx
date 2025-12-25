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

import { memo, useCallback, useRef, useState, KeyboardEvent, useEffect } from 'react';
import { ForkModal } from './ForkModal';
import { MentionPicker } from './MentionPicker';
import { MentionCard } from './MentionCard';
import { useMentions } from './useMentions';
import { chatContextApi } from '@/api/chatApi';
import type { MentionSuggestion } from './MentionPicker';
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
// Debounce Utility
// =============================================================================

function useDebounce<T>(value: T, delay: number): T {
  const [debouncedValue, setDebouncedValue] = useState(value);
  useEffect(() => {
    const handler = setTimeout(() => setDebouncedValue(value), delay);
    return () => clearTimeout(handler);
  }, [value, delay]);
  return debouncedValue;
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

  // Mention management
  const { activeMentions, addMention, removeMention, recentMentions } = useMentions();
  const [mentionPickerOpen, setMentionPickerOpen] = useState(false);
  const [mentionQuery, setMentionQuery] = useState('');
  const [mentionCursorPos, setMentionCursorPos] = useState({ top: 0, left: 0 });
  const [availableFiles, setAvailableFiles] = useState<string[]>([]);
  const debouncedMentionQuery = useDebounce(mentionQuery, 300);

  // Fetch files when debounced query changes
  useEffect(() => {
    if (!debouncedMentionQuery || !mentionPickerOpen) return;

    const fetchFiles = async () => {
      try {
        // Detect mention type from query
        const isFileSearch = debouncedMentionQuery.startsWith('file:') || !debouncedMentionQuery.includes(':');

        if (isFileSearch) {
          const searchTerm = debouncedMentionQuery.replace(/^file:/, '');
          if (searchTerm) {
            const result = await chatContextApi.searchFiles(searchTerm);
            setAvailableFiles(result.files);
          }
        }
      } catch (error) {
        console.error('Failed to fetch files:', error);
        setAvailableFiles([]);
      }
    };

    void fetchFiles();
  }, [debouncedMentionQuery, mentionPickerOpen]);

  // Auto-resize textarea and detect mentions
  const handleInput = useCallback((e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const target = e.target;
    const value = target.value;
    setMessage(value);

    // Auto-resize
    target.style.height = 'auto';
    target.style.height = `${Math.min(target.scrollHeight, 200)}px`;

    // Detect @ mention trigger
    const cursorPos = target.selectionStart;
    const textBeforeCursor = value.slice(0, cursorPos);
    const lastAtIndex = textBeforeCursor.lastIndexOf('@');

    if (lastAtIndex !== -1) {
      const textAfterAt = textBeforeCursor.slice(lastAtIndex + 1);

      // Check if we're still in a mention (no spaces after @)
      if (!textAfterAt.includes(' ') && !textAfterAt.includes('\n')) {
        // Calculate cursor position for picker
        const rect = target.getBoundingClientRect();

        setMentionQuery(textAfterAt);
        setMentionCursorPos({
          top: rect.bottom + 4,
          left: rect.left + 8,
        });
        setMentionPickerOpen(true);
        return;
      }
    }

    // Close picker if @ is removed or space after @
    if (mentionPickerOpen) {
      setMentionPickerOpen(false);
    }
  }, [mentionPickerOpen]);

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

  // Handle mention selection
  const handleMentionSelect = useCallback(
    async (suggestion: MentionSuggestion) => {
      // Add mention to active mentions
      await addMention(suggestion);

      // Remove @query from message
      const cursorPos = textareaRef.current?.selectionStart || 0;
      const textBeforeCursor = message.slice(0, cursorPos);
      const lastAtIndex = textBeforeCursor.lastIndexOf('@');

      if (lastAtIndex !== -1) {
        const textBeforeAt = message.slice(0, lastAtIndex);
        const textAfterCursor = message.slice(cursorPos);
        setMessage(textBeforeAt + textAfterCursor);
      }

      // Close picker
      setMentionPickerOpen(false);
      setMentionQuery('');

      // Refocus textarea
      textareaRef.current?.focus();
    },
    [message, addMention]
  );

  // Handle mention picker close
  const handleMentionPickerClose = useCallback(() => {
    setMentionPickerOpen(false);
    setMentionQuery('');
  }, []);

  // Keyboard handling
  const handleKeyDown = useCallback(
    (e: KeyboardEvent<HTMLTextAreaElement>) => {
      // If mention picker is open, let it handle navigation keys
      if (mentionPickerOpen && ['ArrowDown', 'ArrowUp', 'Enter', 'Escape'].includes(e.key)) {
        // MentionPicker will handle these via global event listener
        return;
      }

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

      // Escape = close mention picker
      if (e.key === 'Escape' && mentionPickerOpen) {
        e.preventDefault();
        handleMentionPickerClose();
      }
    },
    [handleSend, onRewind, mentionPickerOpen, handleMentionPickerClose]
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

      {/* Active mentions */}
      {activeMentions.length > 0 && (
        <div className="input-area__mentions">
          {activeMentions.map((mention) => (
            <MentionCard
              key={mention.id}
              mention={mention}
              onDismiss={removeMention}
              defaultExpanded={false}
            />
          ))}
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

      {/* Mention picker */}
      <MentionPicker
        isOpen={mentionPickerOpen}
        query={mentionQuery}
        onSelect={handleMentionSelect}
        onClose={handleMentionPickerClose}
        position={mentionCursorPos}
        recentMentions={recentMentions}
        availableFiles={availableFiles}
      />

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
