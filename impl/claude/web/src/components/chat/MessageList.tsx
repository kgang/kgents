/**
 * MessageList — Renders conversation turns with proper scrolling
 *
 * Displays:
 * - User messages (with @mentions rendered)
 * - Assistant messages (with confidence + actions)
 * - Streaming indicator during generation
 *
 * Follows elastic-ui-patterns for responsive message bubbles.
 */

import { memo } from 'react';
import type { ChatSession } from './store';
import { UserMessage } from './UserMessage';
import { AssistantMessage } from './AssistantMessage';
import { useChatStore } from './store';
import './MessageList.css';

// =============================================================================
// Types
// =============================================================================

export interface MessageListProps {
  session: ChatSession;
  isStreaming: boolean;
  onEditPortal?: (portalId: string, content: string) => Promise<void>;
  onNavigatePortal?: (path: string) => void;
}

// =============================================================================
// Main Component
// =============================================================================

/**
 * MessageList — Scrollable list of conversation turns
 */
export const MessageList = memo(function MessageList({
  session,
  isStreaming,
  onEditPortal,
  onNavigatePortal,
}: MessageListProps) {
  const { streamingContent } = useChatStore();

  if (!session.turns || session.turns.length === 0) {
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
      {session.turns.map((turn) => (
        <div key={turn.turn_number} className="message-list__turn">
          {/* User message */}
          <UserMessage message={turn.user_message} />

          {/* Assistant message */}
          <AssistantMessage
            message={turn.assistant_response}
            tools={turn.tools_used}
            confidence={turn.confidence}
            evidenceDelta={turn.evidence_delta}
            portalEmissions={turn.portal_emissions}
            onEditPortal={onEditPortal}
            onNavigatePortal={onNavigatePortal}
          />
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

          {streamingContent && (
            <AssistantMessage
              message={{
                role: 'assistant',
                content: streamingContent,
                mentions: [],
                linearity_tag: 'preserved',
              }}
              tools={[]}
              confidence={0}
              evidenceDelta={{
                tools_executed: 0,
                tools_succeeded: 0,
                confidence_change: 0,
              }}
              isStreaming
            />
          )}
        </div>
      )}
    </div>
  );
});

export default MessageList;
