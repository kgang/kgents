/**
 * ChatInput: Message input with action buttons.
 *
 * Supports:
 * - Suggest (normal interaction)
 * - Force (uses force tokens)
 * - Apologize (reduces consent debt)
 */

import { useState, useRef, useEffect } from 'react';
import { cn } from '@/lib/utils';

export interface ChatInputProps {
  onSuggest: (message: string) => void;
  onForce: (message: string) => void;
  onApologize: () => void;
  canForce?: boolean;
  canApologize?: boolean;
  disabled?: boolean;
  className?: string;
}

type InputMode = 'suggest' | 'force';

const QUICK_ACTIONS = [
  { label: 'Explore', action: 'explore the nearby area' },
  { label: 'Rest', action: 'take a moment to rest' },
  { label: 'Socialize', action: 'strike up a conversation with someone nearby' },
  { label: 'Work', action: 'focus on productive work' },
  { label: 'Reflect', action: 'reflect on recent experiences' },
];

export function ChatInput({
  onSuggest,
  onForce,
  onApologize,
  canForce = false,
  canApologize = false,
  disabled = false,
  className,
}: ChatInputProps) {
  const [message, setMessage] = useState('');
  const [mode, setMode] = useState<InputMode>('suggest');
  const [showQuickActions, setShowQuickActions] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  // Focus input on mount
  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  const handleSubmit = (e?: React.FormEvent) => {
    e?.preventDefault();
    if (!message.trim() || disabled) return;

    if (mode === 'force' && canForce) {
      onForce(message.trim());
    } else {
      onSuggest(message.trim());
    }

    setMessage('');
    setMode('suggest');
  };

  const handleQuickAction = (action: string) => {
    if (disabled) return;

    if (mode === 'force' && canForce) {
      onForce(action);
    } else {
      onSuggest(action);
    }

    setShowQuickActions(false);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
    // Escape to clear
    if (e.key === 'Escape') {
      setMessage('');
      setMode('suggest');
    }
  };

  return (
    <div className={cn('border-t border-town-accent/30 p-4 space-y-3', className)}>
      {/* Quick Actions */}
      {showQuickActions && (
        <div className="flex flex-wrap gap-2">
          {QUICK_ACTIONS.map(({ label, action }) => (
            <button
              key={label}
              onClick={() => handleQuickAction(action)}
              disabled={disabled}
              className={cn(
                'px-3 py-1 text-xs rounded-full transition-colors',
                'bg-town-surface/50 hover:bg-town-accent/30',
                disabled && 'opacity-50 cursor-not-allowed'
              )}
            >
              {label}
            </button>
          ))}
        </div>
      )}

      {/* Input Row */}
      <form onSubmit={handleSubmit} className="flex items-center gap-2">
        {/* Quick actions toggle */}
        <button
          type="button"
          onClick={() => setShowQuickActions(!showQuickActions)}
          className={cn(
            'p-2 rounded-lg transition-colors',
            showQuickActions
              ? 'bg-town-accent/50 text-white'
              : 'text-gray-500 hover:text-gray-300'
          )}
          title="Quick actions"
        >
          ⚡
        </button>

        {/* Text input */}
        <div className="flex-1 relative">
          <input
            ref={inputRef}
            type="text"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={
              mode === 'force' ? 'Force action...' : 'Suggest an action...'
            }
            disabled={disabled}
            className={cn(
              'w-full bg-town-surface/50 border rounded-lg px-4 py-2 pr-20',
              'focus:outline-none focus:ring-2',
              mode === 'force'
                ? 'border-amber-500/50 focus:ring-amber-500/30'
                : 'border-town-accent/30 focus:ring-town-highlight/30',
              disabled && 'opacity-50 cursor-not-allowed'
            )}
          />

          {/* Mode indicator */}
          {mode === 'force' && (
            <span className="absolute right-3 top-1/2 -translate-y-1/2 text-xs text-amber-400 font-medium">
              FORCE
            </span>
          )}
        </div>

        {/* Send button */}
        <button
          type="submit"
          disabled={!message.trim() || disabled}
          className={cn(
            'p-2 rounded-lg transition-colors',
            message.trim() && !disabled
              ? 'bg-town-highlight text-white hover:bg-town-highlight/80'
              : 'bg-town-surface text-gray-600 cursor-not-allowed'
          )}
        >
          →
        </button>
      </form>

      {/* Action Buttons */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          {/* Force toggle */}
          <button
            onClick={() => setMode(mode === 'force' ? 'suggest' : 'force')}
            disabled={!canForce || disabled}
            className={cn(
              'flex items-center gap-1 px-3 py-1 text-xs rounded transition-colors',
              mode === 'force'
                ? 'bg-amber-500/30 text-amber-400'
                : canForce
                  ? 'bg-town-surface/30 text-gray-400 hover:text-amber-400'
                  : 'bg-town-surface/20 text-gray-600 cursor-not-allowed'
            )}
            title={
              canForce
                ? 'Toggle force mode (costs force token)'
                : 'No force tokens remaining'
            }
          >
            <span>⚡</span>
            <span>Force</span>
          </button>

          {/* Apologize */}
          <button
            onClick={onApologize}
            disabled={!canApologize || disabled}
            className={cn(
              'flex items-center gap-1 px-3 py-1 text-xs rounded transition-colors',
              canApologize
                ? 'bg-town-surface/30 text-gray-400 hover:text-green-400'
                : 'bg-town-surface/20 text-gray-600 cursor-not-allowed'
            )}
            title={
              canApologize
                ? 'Apologize to reduce consent debt'
                : 'No consent debt to apologize for'
            }
          >
            <span>🙏</span>
            <span>Apologize</span>
          </button>
        </div>

        {/* Keyboard hint */}
        <span className="text-xs text-gray-600">
          Enter to send · Esc to clear
        </span>
      </div>
    </div>
  );
}

export default ChatInput;
