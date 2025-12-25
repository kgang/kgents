/**
 * SafetyGate — Unified safety component for tool execution
 *
 * Merges MutationAcknowledger (post-execution) + PreExecutionGate (pre-execution)
 * into a single component with two modes:
 *
 * - 'pre': Approval gate BEFORE tool execution (destructive ops)
 *   - Timeout = DENY (safe default)
 *   - Three actions: Allow Once / Always Allow / Deny
 *
 * - 'post': Acknowledgment AFTER tool execution (mutation awareness)
 *   - Timeout = ACCEPT (user has been informed)
 *   - One action: Got it (acknowledge)
 *
 * Constitutional grounding (Article IV):
 * - DESTRUCTIVE: Approval required (pre-execution)
 * - MUTATION: Acknowledgment required (post-execution)
 *
 * @see spec/protocols/chat-web.md Part VII.2
 */

import { useState, useEffect } from 'react';
import type { SafetyGateProps } from './types';
import './SafetyGate.css';

// =============================================================================
// Main Component
// =============================================================================

export function SafetyGate({
  mode,
  mutation,
  approval,
  onApprove,
  onDeny,
  onAcknowledge,
}: SafetyGateProps) {
  const timeout = mode === 'pre' ? (approval?.timeout_seconds || 10) : 10;
  const [timeRemaining, setTimeRemaining] = useState(timeout);
  const [isClosing, setIsClosing] = useState(false);

  // Countdown timer
  useEffect(() => {
    const interval = setInterval(() => {
      setTimeRemaining((prev) => {
        if (prev <= 1) {
          clearInterval(interval);
          handleTimeout();
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  const handleTimeout = () => {
    setIsClosing(true);

    setTimeout(() => {
      if (mode === 'pre') {
        // Pre-execution: timeout = DENY (safe default)
        onDeny?.(approval!.request_id, 'Approval timeout (auto-denied)');
      } else {
        // Post-execution: timeout = ACCEPT (user has been informed)
        onAcknowledge?.(mutation!.id, 'timeout_accept');
      }
    }, 200);
  };

  const handleApprove = (alwaysAllow: boolean) => {
    setIsClosing(true);

    setTimeout(() => {
      if (mode === 'pre' && approval) {
        onApprove?.(approval.request_id, alwaysAllow);
      }
    }, 200);
  };

  const handleDeny = () => {
    setIsClosing(true);

    setTimeout(() => {
      if (mode === 'pre' && approval) {
        onDeny?.(approval.request_id, 'User denied approval');
      }
    }, 200);
  };

  const handleAcknowledge = (acknowledgeMode: 'click' | 'keyboard') => {
    setIsClosing(true);

    setTimeout(() => {
      if (mode === 'post' && mutation) {
        onAcknowledge?.(mutation.id, acknowledgeMode);
      }
    }, 200);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (mode === 'pre') {
      // Pre-execution: Enter = approve, Escape = deny
      if (e.key === 'Enter') {
        e.preventDefault();
        handleApprove(false);
      } else if (e.key === 'Escape') {
        e.preventDefault();
        handleDeny();
      }
    } else {
      // Post-execution: Enter or Space = acknowledge
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        handleAcknowledge('keyboard');
      }
    }
  };

  // Determine icon, severity, and progress
  const isDestructive = mode === 'pre' ? approval?.is_destructive : mutation?.is_destructive;
  const icon = isDestructive ? '◆' : mode === 'pre' ? '◈' : '⊛';
  const severity = isDestructive ? 'destructive' : 'mutation';
  const progressPercentage = ((timeout - timeRemaining) / timeout) * 100;

  // Render pre-execution gate
  if (mode === 'pre' && approval) {
    return (
      <div
        className={`safety-gate safety-gate--pre ${isClosing ? 'safety-gate--closing' : ''}`}
        role="alertdialog"
        aria-live="assertive"
        aria-labelledby="gate-title"
        aria-describedby="gate-description"
        onKeyDown={handleKeyDown}
        tabIndex={0}
        data-severity={severity}
      >
        {/* Progress bar (countdown to auto-deny) */}
        <div className="safety-gate__progress">
          <div
            className="safety-gate__progress-bar"
            style={{ width: `${progressPercentage}%` }}
          />
        </div>

        {/* Content */}
        <div className="safety-gate__content">
          <div className="safety-gate__icon">{icon}</div>

          <div className="safety-gate__text">
            <div id="gate-title" className="safety-gate__title">
              {approval.is_destructive ? 'Destructive Operation' : 'Requires Approval'}
            </div>
            <div id="gate-description" className="safety-gate__description">
              <strong>{approval.tool_name}</strong> wants to execute:
            </div>
            <div className="safety-gate__preview">{approval.input_preview}</div>
          </div>
        </div>

        {/* Actions */}
        <div className="safety-gate__actions">
          <button
            className="safety-gate__button safety-gate__button--deny"
            onClick={handleDeny}
            aria-label="Deny tool execution"
          >
            Deny <kbd className="safety-gate__kbd">Esc</kbd>
          </button>

          <button
            className="safety-gate__button safety-gate__button--approve"
            onClick={() => handleApprove(false)}
            aria-label="Approve tool execution once"
          >
            Allow Once <kbd className="safety-gate__kbd">↵</kbd>
          </button>

          <button
            className="safety-gate__button safety-gate__button--trust"
            onClick={() => handleApprove(true)}
            aria-label="Always allow this tool"
            title="This tool will auto-approve in future"
          >
            Always Allow
          </button>
        </div>

        {/* Timeout indicator */}
        {timeRemaining > 0 && (
          <div className="safety-gate__timeout">
            Auto-denies in {timeRemaining}s (safe default)
          </div>
        )}
      </div>
    );
  }

  // Render post-execution acknowledgment
  if (mode === 'post' && mutation) {
    return (
      <div
        className={`safety-gate safety-gate--post ${isClosing ? 'safety-gate--closing' : ''}`}
        role="alert"
        aria-live="assertive"
        onKeyDown={handleKeyDown}
        tabIndex={0}
        data-destructive={mutation.is_destructive}
      >
        {/* Progress bar */}
        <div className="safety-gate__progress">
          <div
            className="safety-gate__progress-bar"
            style={{ width: `${progressPercentage}%` }}
          />
        </div>

        {/* Content */}
        <div className="safety-gate__content">
          <div className="safety-gate__icon">{icon}</div>

          <div className="safety-gate__text">
            <div className="safety-gate__description">
              {mutation.tool_name}: {mutation.description}
            </div>
            {mutation.target && (
              <div className="safety-gate__target">
                {mutation.target}
              </div>
            )}
          </div>

          <button
            className="safety-gate__button"
            onClick={() => handleAcknowledge('click')}
            aria-label="Acknowledge mutation"
          >
            Got it <kbd className="safety-gate__kbd">↵</kbd>
          </button>
        </div>

        {/* Timeout indicator */}
        {timeRemaining > 0 && (
          <div className="safety-gate__timeout">
            Auto-accepts in {timeRemaining}s
          </div>
        )}
      </div>
    );
  }

  return null;
}

export default SafetyGate;
