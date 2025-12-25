/**
 * ChatPanel — Main container for web-native chat experience
 *
 * "Chat is not a feature. Chat is an affordance that collapses discrete into continuous."
 *
 * Implements the full ChatKBlock pattern with:
 * - Context indicator (tokens, cost, evidence)
 * - Message list with streaming support
 * - Input area with @mention system
 * - Branch tree visualization
 * - Tool transparency
 *
 * Follows elastic-ui-patterns for responsive layout.
 *
 * @see spec/protocols/chat-web.md Part X
 */

import { useCallback, useEffect, useRef, useState } from 'react';
import { useChatStore } from './store';
import { ContextIndicator } from './ContextIndicator';
import { MessageList } from './MessageList';
import { InputArea } from './InputArea';
import { BranchTree } from './BranchTree';
import { TrailingSession } from './TrailingSession';
import { SessionCrystal } from './SessionCrystal';
import { MutationAcknowledger } from './MutationAcknowledger';
import { useBranching } from './useBranching';
import { extractPendingMutations } from './mutationDetector';
import './ChatPanel.css';

// =============================================================================
// Types
// =============================================================================

export interface ChatPanelProps {
  /** Session ID to display. If not provided, creates new session. */
  sessionId?: string;

  /** Project context (optional) */
  projectId?: string;

  /** Compact mode for embedded use */
  compact?: boolean;

  /** Show branch tree */
  showBranching?: boolean;

  /** Custom class name */
  className?: string;
}

// =============================================================================
// Main Component
// =============================================================================

/**
 * ChatPanel — The main chat interface
 *
 * Component tree (from spec):
 * <ChatPanel>
 *   <ContextIndicator />
 *   <MessageList>
 *     <UserMessage />
 *     <AssistantMessage>
 *       <ConfidenceIndicator />
 *       <ActionPanel collapsed />
 *     </AssistantMessage>
 *   </MessageList>
 *   <InputArea>
 *     <MentionPicker />
 *   </InputArea>
 *   <BranchTree />
 * </ChatPanel>
 */
export function ChatPanel({
  sessionId: initialSessionId,
  projectId,
  compact = false,
  showBranching = true,
  className = '',
}: ChatPanelProps) {
  const messageListRef = useRef<HTMLDivElement>(null);
  const [showCrystalPanel, setShowCrystalPanel] = useState(false);

  const {
    currentSession,
    isStreaming,
    error,
    trailingSession,
    pendingMutations,
    initialize,
    sendMessage,
    // fork, // Will be used when ForkModal is implemented
    rewind,
    clearError,
    continueTrailingSession,
    startFreshFromTrailing,
    dismissTrailing,
    acknowledgeMutation,
    addPendingMutation,
  } = useChatStore();

  // Branching system
  const branching = useBranching(
    currentSession?.id || '',
    (branchId) => {
      // Switch branch callback
      console.log('Switched to branch:', branchId);
    }
  );

  // Initialize session on mount
  useEffect(() => {
    initialize(initialSessionId, projectId);
  }, [initialSessionId, projectId, initialize]);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    if (messageListRef.current && currentSession) {
      const shouldScroll =
        messageListRef.current.scrollHeight - messageListRef.current.scrollTop <=
        messageListRef.current.clientHeight + 100;

      if (shouldScroll) {
        messageListRef.current.scrollTo({
          top: messageListRef.current.scrollHeight,
          behavior: 'smooth',
        });
      }
    }
  }, [currentSession?.turns.length]);

  // Detect mutations from completed turns
  useEffect(() => {
    if (!currentSession || currentSession.turns.length === 0) return;

    // Get the most recent turn
    const lastTurn = currentSession.turns[currentSession.turns.length - 1];
    if (!lastTurn || !lastTurn.tools_used) return;

    // Extract mutations from tools used in the last turn
    const mutations = extractPendingMutations(lastTurn.tools_used);

    // Add mutations to pending queue
    mutations.forEach((mutation) => {
      addPendingMutation(mutation);
    });
  }, [currentSession?.turns.length, currentSession, addPendingMutation]);

  // Handlers
  const handleSend = useCallback(
    async (message: string) => {
      if (!message.trim() || isStreaming) return;
      await sendMessage(message);
    },
    [sendMessage, isStreaming]
  );

  // Note: handleFork will be added when ForkModal is implemented
  // See: branching.createFork() for fork functionality

  const handleRewind = useCallback(
    async (turns: number) => {
      if (!currentSession) return;
      await rewind(currentSession.id, turns);
    },
    [rewind, currentSession]
  );

  // Build classes
  const panelClasses = [
    'chat-panel',
    compact ? 'chat-panel--compact' : '',
    className,
  ]
    .filter(Boolean)
    .join(' ');

  // Loading state
  if (!currentSession) {
    return (
      <div className={panelClasses}>
        <div className="chat-panel__loading">
          <div className="chat-panel__loading-spinner" />
          <p className="chat-panel__loading-text">Initializing session...</p>
        </div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className={panelClasses}>
        <div className="chat-panel__error">
          <div className="chat-panel__error-icon">◆</div>
          <h3 className="chat-panel__error-title">Session Error</h3>
          <p className="chat-panel__error-message">{error}</p>
          <button
            className="chat-panel__error-button"
            onClick={clearError}
          >
            Dismiss
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className={panelClasses}>
      {/* Context indicator - tokens, cost, evidence */}
      {!compact && (
        <div className="chat-panel__context">
          <ContextIndicator
            session={currentSession}
            compact={compact}
          />
        </div>
      )}

      {/* Branch tree visualization */}
      {showBranching && !compact && currentSession && (
        <div className="chat-panel__branches">
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
      <div
        ref={messageListRef}
        className="chat-panel__messages"
      >
        <MessageList
          session={currentSession}
          isStreaming={isStreaming}
        />

        {/* Trailing session (crystallized context) */}
        {trailingSession && (
          <TrailingSession
            crystal={trailingSession.crystal}
            trailingTurns={trailingSession.trailingTurns}
            crystallizedAt={trailingSession.crystallizedAt}
            onContinue={continueTrailingSession}
            onStartFresh={startFreshFromTrailing}
            onDismiss={dismissTrailing}
            onViewCrystal={() => setShowCrystalPanel(true)}
          />
        )}
      </div>

      {/* Mutation acknowledgment (sticky above input) */}
      {pendingMutations.length > 0 && (
        <div className="chat-panel__mutations">
          {pendingMutations.map((mutation) => (
            <MutationAcknowledger
              key={mutation.id}
              mutation={mutation}
              onAcknowledge={acknowledgeMutation}
              timeout={10}
            />
          ))}
        </div>
      )}

      {/* Input area with mentions */}
      <div className="chat-panel__input">
        <InputArea
          onSend={handleSend}
          onRewind={handleRewind}
          disabled={isStreaming}
          compact={compact}
        />
      </div>

      {/* Session crystal panel */}
      {trailingSession && (
        <SessionCrystal
          crystal={trailingSession.crystal}
          isOpen={showCrystalPanel}
          onClose={() => setShowCrystalPanel(false)}
          mode="panel"
        />
      )}
    </div>
  );
}

export default ChatPanel;
