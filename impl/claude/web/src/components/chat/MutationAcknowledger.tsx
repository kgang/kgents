/**
 * MutationAcknowledger — Acknowledgment UI for mutations
 *
 * From spec/protocols/chat-web.md Part VII.2:
 * - Mutations MUST be visible and acknowledged
 * - "A toast that can be ignored is a toast that wasn't heard."
 * - Keyboard: Enter or Space to acknowledge
 * - Auto-timeout: 10 seconds (logged as timeout_accept)
 * - Active acknowledgment signals user has registered the change
 *
 * Constitutional grounding (Article IV):
 * - MUTATION: Acknowledgment required (user confirms awareness of change)
 */

import { useState, useEffect } from 'react';
import type { PendingMutation } from './store';
import './MutationAcknowledger.css';

// =============================================================================
// Types
// =============================================================================

export interface MutationAcknowledgerProps {
  /** Mutation to acknowledge */
  mutation: PendingMutation;
  /** Callback when acknowledged */
  onAcknowledge: (id: string, mode: 'click' | 'keyboard' | 'timeout_accept') => void;
  /** Auto-timeout in seconds (default: 10) */
  timeout?: number;
}

// =============================================================================
// Main Component
// =============================================================================

export function MutationAcknowledger({
  mutation,
  onAcknowledge,
  timeout = 10,
}: MutationAcknowledgerProps) {
  const [timeRemaining, setTimeRemaining] = useState(timeout);
  const [isClosing, setIsClosing] = useState(false);

  // Countdown timer
  useEffect(() => {
    const interval = setInterval(() => {
      setTimeRemaining((prev) => {
        if (prev <= 1) {
          // Timeout reached
          clearInterval(interval);
          handleTimeout();
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  const handleAcknowledge = (mode: 'click' | 'keyboard') => {
    setIsClosing(true);

    // Delay callback to allow exit animation
    setTimeout(() => {
      onAcknowledge(mutation.id, mode);
    }, 200);
  };

  const handleTimeout = () => {
    setIsClosing(true);

    setTimeout(() => {
      onAcknowledge(mutation.id, 'timeout_accept');
    }, 200);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      handleAcknowledge('keyboard');
    }
  };

  // Get icon based on mutation type
  const icon = mutation.is_destructive ? '◆' : '⊛';
  const progressPercentage = ((timeout - timeRemaining) / timeout) * 100;

  return (
    <div
      className={`mutation-acknowledger ${isClosing ? 'mutation-acknowledger--closing' : ''}`}
      role="alert"
      aria-live="assertive"
      onKeyDown={handleKeyDown}
      tabIndex={0}
      data-destructive={mutation.is_destructive}
    >
      {/* Progress bar */}
      <div className="mutation-acknowledger__progress">
        <div
          className="mutation-acknowledger__progress-bar"
          style={{ width: `${progressPercentage}%` }}
        />
      </div>

      {/* Content */}
      <div className="mutation-acknowledger__content">
        <div className="mutation-acknowledger__icon">{icon}</div>

        <div className="mutation-acknowledger__text">
          <div className="mutation-acknowledger__description">
            {mutation.tool_name}: {mutation.description}
          </div>
          {mutation.target && (
            <div className="mutation-acknowledger__target">
              {mutation.target}
            </div>
          )}
        </div>

        <button
          className="mutation-acknowledger__button"
          onClick={() => handleAcknowledge('click')}
          aria-label="Acknowledge mutation"
        >
          Got it <kbd className="mutation-acknowledger__kbd">↵</kbd>
        </button>
      </div>

      {/* Timeout indicator */}
      {timeRemaining > 0 && (
        <div className="mutation-acknowledger__timeout">
          Auto-accepts in {timeRemaining}s
        </div>
      )}
    </div>
  );
}

export default MutationAcknowledger;
