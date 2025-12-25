/**
 * ChatSession Construction - Composing Conversation + Witness
 *
 * "The chat is the canvas. Evidence is the witness."
 *
 * UX TRANSFORMATION (2025-12-25): ValueCompass removed per Kent's decision.
 *
 * This construction unifies the chat experience:
 * 1. Conversation - The primary interaction surface (messages, branching, safety)
 * 2. Witness - Evidence corpus with causal influence (theory panel)
 *
 * Layout:
 * ┌─────────────────────────────────────────────────────────┐
 * │                 Conversation (main)                      │
 * │  ┌───────────────────────────────────────────────────┐  │
 * │  │ Messages                                           │  │
 * │  │ ...                                                │  │
 * │  ├───────────────────────────────────────────────────┤  │
 * │  │ InputArea                                          │  │
 * │  └───────────────────────────────────────────────────┘  │
 * ├─────────────────────────────────────────────────────────┤
 * │ [Witness] (collapsible evidence panel)                  │
 * └─────────────────────────────────────────────────────────┘
 *
 * @see spec/protocols/chat-web.md
 */

import { useState, useCallback } from 'react';
import { Conversation } from '../../primitives/Conversation/Conversation';
import { Witness } from '../../primitives/Witness/Witness';
import type { Turn, SafetyMode, PendingMutation, PendingApproval } from '../../primitives/Conversation/types';
import type { EvidenceCorpus } from '../../types/theory';
import './ChatSession.css';

// =============================================================================
// Types
// =============================================================================

export interface ChatSessionProps {
  /** Session ID */
  sessionId: string;

  /** Chat turns */
  turns: Turn[];

  /** Send message handler */
  onMessage: (content: string) => void;

  /** Branch/fork handler */
  onBranch?: (turnId: string) => void;

  /** Crystallize session handler */
  onCrystallize?: (selection: string[]) => void;

  /** Rewind handler */
  onRewind?: (turnId: string) => void;

  /** Safety mode */
  safetyMode: SafetyMode;

  /** Streaming state */
  isStreaming?: boolean;

  /** Error */
  error?: string | null;

  /** Pending mutations (post-execution acknowledgment) */
  pendingMutations?: PendingMutation[];

  /** Pending approvals (pre-execution gate) */
  pendingApprovals?: PendingApproval[];

  /** Acknowledge mutation callback */
  onAcknowledgeMutation?: (id: string, mode: 'click' | 'keyboard' | 'timeout_accept') => void;

  /** Approve execution callback */
  onApproveExecution?: (requestId: string, alwaysAllow: boolean) => void;

  /** Deny execution callback */
  onDenyExecution?: (requestId: string, reason?: string) => void;

  /** Show theory panel (Witness) */
  showTheory?: boolean;

  /** Evidence for current turn */
  currentEvidence?: EvidenceCorpus;

  /** Compact mode */
  compact?: boolean;

  /** Custom class name */
  className?: string;
}

// =============================================================================
// Main Component
// =============================================================================

/**
 * ChatSession - The composed chat experience
 *
 * Combines:
 * - Conversation primitive (messages, input, branching, safety)
 * - Witness primitive (evidence corpus display)
 *
 * Theory panel is collapsible and only shown when:
 * 1. showTheory=true, OR
 * 2. currentEvidence provided
 */
export function ChatSession({
  sessionId,
  turns,
  onMessage,
  onBranch,
  onCrystallize: _onCrystallize, // Reserved for future crystallization feature
  onRewind,
  safetyMode,
  isStreaming = false,
  error = null,
  pendingMutations = [],
  pendingApprovals = [],
  onAcknowledgeMutation,
  onApproveExecution,
  onDenyExecution,
  showTheory = false,
  currentEvidence,
  compact = false,
  className = '',
}: ChatSessionProps) {
  // Theory panel visibility state
  const [theoryExpanded, setTheoryExpanded] = useState(showTheory);

  // Determine if we should show theory panel at all
  const hasEvidence = currentEvidence && currentEvidence.items.length > 0;
  const shouldShowTheoryPanels = showTheory || hasEvidence;

  // Evidence click handler
  const handleEvidenceClick = useCallback((evidenceId: string) => {
    console.log('Evidence clicked:', evidenceId);
    // TODO: Implement evidence detail view
  }, []);

  // Build classes
  const sessionClasses = [
    'chat-session',
    compact ? 'chat-session--compact' : '',
    shouldShowTheoryPanels ? 'chat-session--with-theory' : '',
    theoryExpanded ? 'chat-session--theory-expanded' : '',
    className,
  ]
    .filter(Boolean)
    .join(' ');

  return (
    <div className={sessionClasses} data-session-id={sessionId}>
      {/* Main conversation area */}
      <div className="chat-session__conversation">
        <Conversation
          turns={turns}
          onMessage={onMessage}
          onBranch={onBranch}
          onRewind={onRewind}
          safetyMode={safetyMode}
          isStreaming={isStreaming}
          error={error}
          pendingMutations={pendingMutations}
          pendingApprovals={pendingApprovals}
          onAcknowledgeMutation={onAcknowledgeMutation}
          onApproveExecution={onApproveExecution}
          onDenyExecution={onDenyExecution}
          compact={compact}
        />
      </div>

      {/* Theory panels (collapsible) */}
      {shouldShowTheoryPanels && (
        <div className="chat-session__theory">
          {/* Toggle button */}
          <button
            className="chat-session__theory-toggle"
            onClick={() => setTheoryExpanded(!theoryExpanded)}
            aria-expanded={theoryExpanded}
            aria-label={theoryExpanded ? 'Collapse theory panels' : 'Expand theory panels'}
          >
            <span className="chat-session__theory-toggle-icon">
              {theoryExpanded ? '▼' : '▲'}
            </span>
            <span className="chat-session__theory-toggle-label">
              Evidence
              {hasEvidence && (
                <span className="chat-session__theory-badge">
                  {currentEvidence?.items.length || 0}
                </span>
              )}
            </span>
          </button>

          {/* Theory content */}
          {theoryExpanded && (
            <div className="chat-session__theory-content">
              {/* Witness panel */}
              {hasEvidence && (
                <div className="chat-session__theory-panel chat-session__theory-panel--witness">
                  <div className="chat-session__theory-panel-header">
                    <span className="chat-session__theory-panel-icon">◆</span>
                    <h3 className="chat-session__theory-panel-title">Evidence Corpus</h3>
                  </div>
                  <Witness
                    evidence={currentEvidence}
                    showCausal={true}
                    compact={compact}
                    onEvidenceClick={handleEvidenceClick}
                    size={compact ? 'sm' : 'md'}
                  />
                </div>
              )}

              {/* ValueCompass removed per UX transformation (2025-12-25) */}
            </div>
          )}
        </div>
      )}

      {/* Session metadata (bottom corner) */}
      {!compact && (
        <div className="chat-session__meta">
          <span className="chat-session__meta-session">{sessionId}</span>
          <span className="chat-session__meta-separator">•</span>
          <span className="chat-session__meta-turns">{turns.length} turns</span>
          {isStreaming && (
            <>
              <span className="chat-session__meta-separator">•</span>
              <span className="chat-session__meta-streaming">streaming</span>
            </>
          )}
        </div>
      )}
    </div>
  );
}

export default ChatSession;
