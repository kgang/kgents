/**
 * UserMessage — User message bubble with rendered @mentions
 *
 * Displays user input with:
 * - Formatted message content
 * - Rendered mentions (collapsed cards)
 * - Timestamp
 *
 * Stark biome: clean, minimal, vim-inspired.
 */

import { memo } from 'react';
import type { Message } from './store';
import './UserMessage.css';

// =============================================================================
// Types
// =============================================================================

export interface UserMessageProps {
  message: Message;
}

// =============================================================================
// Main Component
// =============================================================================

/**
 * UserMessage — User input bubble
 */
export const UserMessage = memo(function UserMessage({
  message,
}: UserMessageProps) {
  return (
    <div className="user-message">
      <div className="user-message__bubble">
        {/* Mentions (if any) */}
        {message.mentions && message.mentions.length > 0 && (
          <div className="user-message__mentions">
            {message.mentions.map((mention, idx) => (
              <div key={idx} className="user-message__mention">
                <span className="user-message__mention-type">
                  @{mention.type}:
                </span>
                <span className="user-message__mention-query">
                  {mention.query}
                </span>
              </div>
            ))}
          </div>
        )}

        {/* Content */}
        <div className="user-message__content">
          {message.content}
        </div>
      </div>

      {/* Metadata indicator (if required) */}
      {message.linearity_tag === 'required' && (
        <div
          className="user-message__pin"
          title="Pinned to context"
        >
          ◈
        </div>
      )}
    </div>
  );
});

export default UserMessage;
