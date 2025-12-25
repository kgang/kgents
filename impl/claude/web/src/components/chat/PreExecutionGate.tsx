/**
 * PreExecutionGate — Approval gate for destructive operations
 *
 * From spec/protocols/chat-web.md Part VII.2:
 * - DESTRUCTIVE operations require APPROVAL before execution
 * - Timeout = DENY (safe default, unlike MutationAcknowledger)
 * - Three options: Allow / Deny / Always Allow This Tool
 * - Blocks tool execution until user decides
 *
 * Constitutional grounding (Article IV):
 * - DESTRUCTIVE: Approval required (user confirms before irrecoverable action)
 *
 * Differences from MutationAcknowledger:
 * - Runs BEFORE tool execution (not after)
 * - Timeout behavior is DENY (not accept) - safer for destructive ops
 * - Has explicit Allow/Deny buttons (not just acknowledge)
 * - Optional "Always Allow" for trust escalation
 */

import { useState, useEffect } from 'react';
import './PreExecutionGate.css';

// =============================================================================
// Types
// =============================================================================

export interface PendingApproval {
  request_id: string;
  tool_name: string;
  input_preview: string;
  is_destructive: boolean;
  timeout_seconds: number;
  timestamp: string;
}

export interface PreExecutionGateProps {
  /** Approval request to handle */
  approval: PendingApproval;
  /** Callback when user approves */
  onApprove: (requestId: string, alwaysAllow: boolean) => void;
  /** Callback when user denies or timeout */
  onDeny: (requestId: string, reason?: string) => void;
}

// =============================================================================
// Main Component
// =============================================================================

export function PreExecutionGate({
  approval,
  onApprove,
  onDeny,
}: PreExecutionGateProps) {
  const [timeRemaining, setTimeRemaining] = useState(approval.timeout_seconds);
  const [isClosing, setIsClosing] = useState(false);

  // Countdown timer
  useEffect(() => {
    const interval = setInterval(() => {
      setTimeRemaining((prev) => {
        if (prev <= 1) {
          // Timeout reached - DENY (safe default for destructive ops)
          clearInterval(interval);
          handleTimeout();
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  const handleApprove = (alwaysAllow: boolean) => {
    setIsClosing(true);

    // Delay callback to allow exit animation
    setTimeout(() => {
      onApprove(approval.request_id, alwaysAllow);
    }, 200);
  };

  const handleDeny = () => {
    setIsClosing(true);

    setTimeout(() => {
      onDeny(approval.request_id, 'User denied approval');
    }, 200);
  };

  const handleTimeout = () => {
    setIsClosing(true);

    setTimeout(() => {
      onDeny(approval.request_id, 'Approval timeout (auto-denied)');
    }, 200);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    // Enter = approve, Escape = deny
    if (e.key === 'Enter') {
      e.preventDefault();
      handleApprove(false);
    } else if (e.key === 'Escape') {
      e.preventDefault();
      handleDeny();
    }
  };

  // Get icon and severity
  const icon = approval.is_destructive ? '◆' : '◈';
  const severity = approval.is_destructive ? 'destructive' : 'mutation';
  const progressPercentage =
    ((approval.timeout_seconds - timeRemaining) / approval.timeout_seconds) * 100;

  return (
    <div
      className={`pre-execution-gate ${isClosing ? 'pre-execution-gate--closing' : ''}`}
      role="alertdialog"
      aria-live="assertive"
      aria-labelledby="gate-title"
      aria-describedby="gate-description"
      onKeyDown={handleKeyDown}
      tabIndex={0}
      data-severity={severity}
    >
      {/* Progress bar (countdown to auto-deny) */}
      <div className="pre-execution-gate__progress">
        <div
          className="pre-execution-gate__progress-bar"
          style={{ width: `${progressPercentage}%` }}
        />
      </div>

      {/* Content */}
      <div className="pre-execution-gate__content">
        <div className="pre-execution-gate__icon">{icon}</div>

        <div className="pre-execution-gate__text">
          <div id="gate-title" className="pre-execution-gate__title">
            {approval.is_destructive ? 'Destructive Operation' : 'Requires Approval'}
          </div>
          <div id="gate-description" className="pre-execution-gate__description">
            <strong>{approval.tool_name}</strong> wants to execute:
          </div>
          <div className="pre-execution-gate__preview">{approval.input_preview}</div>
        </div>
      </div>

      {/* Actions */}
      <div className="pre-execution-gate__actions">
        <button
          className="pre-execution-gate__button pre-execution-gate__button--deny"
          onClick={handleDeny}
          aria-label="Deny tool execution"
        >
          Deny <kbd className="pre-execution-gate__kbd">Esc</kbd>
        </button>

        <button
          className="pre-execution-gate__button pre-execution-gate__button--approve"
          onClick={() => handleApprove(false)}
          aria-label="Approve tool execution once"
        >
          Allow Once <kbd className="pre-execution-gate__kbd">↵</kbd>
        </button>

        <button
          className="pre-execution-gate__button pre-execution-gate__button--trust"
          onClick={() => handleApprove(true)}
          aria-label="Always allow this tool"
          title="This tool will auto-approve in future"
        >
          Always Allow
        </button>
      </div>

      {/* Timeout indicator */}
      {timeRemaining > 0 && (
        <div className="pre-execution-gate__timeout">
          Auto-denies in {timeRemaining}s (safe default)
        </div>
      )}
    </div>
  );
}

export default PreExecutionGate;
