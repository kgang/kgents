/**
 * Conversation — Unified chat primitive
 *
 * "Chat is not a feature. Chat is an affordance that collapses discrete into continuous."
 *
 * Consolidates the chat system into a single coherent primitive:
 * - Core: MessageList, InputArea, BranchTree
 * - Safety: Pre-execution gating + post-execution acknowledgment
 * - State: Streaming, errors, trailing sessions
 *
 * Replaces the fragmented ChatPanel architecture with a clean interface.
 *
 * @see spec/protocols/chat-web.md
 */

import { useCallback, useRef } from 'react';
import type { ConversationProps } from './types';
import { InputArea } from './InputArea';
import { BranchTree } from './BranchTree';
import { SafetyGate } from './SafetyGate';
import { useBranching } from './useBranching';
import './Conversation.css';

// =============================================================================
// Main Component
// =============================================================================

/**
 * Conversation — The unified chat interface
 *
 * Component tree:
 * - BranchTree (optional: if branching enabled)
 * - MessageList (turn display with streaming)
 * - SafetyGate mode="post" (post-execution acknowledgment)
 * - SafetyGate mode="pre" (pre-execution approval)
 * - InputArea (message input)
 */
export function Conversation({
  turns,
  onMessage,
  onBranch,
  onRewind,
  safetyMode,
  isStreaming = false,
  error = null,
  pendingMutations = [],
  pendingApprovals = [],
  onAcknowledgeMutation,
  onApproveExecution,
  onDenyExecution,
  compact = false,
  className = '',
}: ConversationProps) {
  const messageListRef = useRef<HTMLDivElement>(null);

  // Branching system (optional - only if onBranch provided)
  const sessionId = 'current'; // TODO: Pass from props or context
  const branching = useBranching(
    sessionId,
    (branchId) => {
      console.log('Switched to branch:', branchId);
    }
  );

  // Message send handler
  const handleSend = useCallback(
    async (content: string) => {
      if (!content.trim() || isStreaming) return;
      onMessage(content);
    },
    [onMessage, isStreaming]
  );

  // Rewind handler
  const handleRewindClick = useCallback(
    async (turns: number) => {
      if (onRewind) {
        onRewind(turns.toString());
      }
    },
    [onRewind]
  );

  // Fork handler (placeholder)
  const handleFork = useCallback(
    async (branchName: string, forkPoint?: number) => {
      console.log('Fork:', branchName, forkPoint);
      // TODO: Implement fork logic
    },
    []
  );

  // Build classes
  const conversationClasses = [
    'conversation',
    compact ? 'conversation--compact' : '',
    className,
  ]
    .filter(Boolean)
    .join(' ');

  // Error state
  if (error) {
    return (
      <div className={conversationClasses}>
        <div className="conversation__error">
          <div className="conversation__error-icon">◆</div>
          <h3 className="conversation__error-title">Conversation Error</h3>
          <p className="conversation__error-message">{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className={conversationClasses}>
      {/* Branch tree visualization */}
      {onBranch && !compact && branching.tree && (
        <div className="conversation__branches">
          <BranchTree
            tree={branching.tree}
            branches={branching.branches}
            currentBranch={branching.currentBranch}
            canFork={branching.canFork}
            onSwitchBranch={branching.switchBranch}
            onMergeBranch={branching.merge}
            compact={compact}
          />
        </div>
      )}

      {/* Message list with scrolling */}
      <div ref={messageListRef} className="conversation__messages">
        <MessageList turns={turns} isStreaming={isStreaming} />
      </div>

      {/* Safety gates */}
      {safetyMode === 'acknowledge' && pendingMutations.length > 0 && (
        <div className="conversation__safety-post">
          {pendingMutations.map((mutation) => (
            <SafetyGate
              key={mutation.id}
              mode="post"
              mutation={mutation}
              onAcknowledge={onAcknowledgeMutation}
            />
          ))}
        </div>
      )}

      {safetyMode === 'gate' && pendingApprovals.length > 0 && (
        <div className="conversation__safety-pre">
          {pendingApprovals.map((approval) => (
            <SafetyGate
              key={approval.request_id}
              mode="pre"
              approval={approval}
              onApprove={onApproveExecution}
              onDeny={onDenyExecution}
            />
          ))}
        </div>
      )}

      {/* Input area */}
      <div className="conversation__input">
        <InputArea
          onSend={handleSend}
          onRewind={handleRewindClick}
          onFork={handleFork}
          disabled={isStreaming}
          compact={compact}
          currentTurn={turns.length}
          existingBranches={branching.branches.map((b) => b.branch_name)}
        />
      </div>
    </div>
  );
}

// =============================================================================
// MessageList Component
// =============================================================================

interface MessageListProps {
  turns: ConversationProps['turns'];
  isStreaming: boolean;
}

/**
 * MessageList — Scrollable list of conversation turns
 *
 * Displays user messages and assistant responses with evidence indicators.
 */
function MessageList({ turns, isStreaming }: MessageListProps) {
  if (!turns || turns.length === 0) {
    return (
      <div className="message-list message-list--empty">
        <div className="message-list__empty-state">
          <div className="message-list__empty-icon">∴</div>
          <h3 className="message-list__empty-title">Start a conversation</h3>
          <p className="message-list__empty-text">
            Type a message below or use @mentions to inject context.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="message-list">
      {turns.map((turn) => (
        <div key={turn.turn_number} className="message-list__turn">
          {/* User message */}
          <div className="message message--user">
            <div className="message__content">{turn.user_message.content}</div>
          </div>

          {/* Assistant message */}
          <div className="message message--assistant">
            <div className="message__content">{turn.assistant_response.content}</div>
            {turn.confidence > 0 && (
              <div className="message__confidence">
                Confidence: {Math.round(turn.confidence * 100)}%
              </div>
            )}
          </div>
        </div>
      ))}

      {/* Streaming indicator */}
      {isStreaming && (
        <div className="message-list__turn message-list__turn--streaming">
          <div className="message-list__streaming-indicator">
            <div className="message-list__streaming-dots">
              <span />
              <span />
              <span />
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default Conversation;
