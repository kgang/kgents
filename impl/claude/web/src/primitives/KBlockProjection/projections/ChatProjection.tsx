/**
 * ChatProjection — Conversation Message Bubble
 *
 * Renders K-Block as a chat message.
 * Shows: content (markdown), author, timestamp.
 */

import { memo } from 'react';
import type { ProjectionComponentProps } from '../types';
import './ChatProjection.css';

export const ChatProjection = memo(function ChatProjection({
  kblock,
  observer,
  className = '',
}: ProjectionComponentProps) {
  // Determine if this is from the current observer
  const isOwn = kblock.createdBy === observer.id;

  // Format timestamp
  const timestamp = kblock.updatedAt.toLocaleTimeString('en-US', {
    hour: 'numeric',
    minute: '2-digit',
  });

  return (
    <div
      className={`chat-projection ${isOwn ? 'chat-projection--own' : 'chat-projection--other'} ${className}`}
    >
      {/* Author (only for others) */}
      {!isOwn && (
        <div className="chat-projection__author">{kblock.createdBy}</div>
      )}

      {/* Message bubble */}
      <div className="chat-projection__bubble">
        <div className="chat-projection__content">{kblock.content}</div>
        <div className="chat-projection__timestamp">{timestamp}</div>
      </div>
    </div>
  );
});
