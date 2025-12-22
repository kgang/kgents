/**
 * DialogueMessage — Single message in the dialogue pane
 *
 * Renders user and assistant messages with different styling.
 * Parses content for focus links (file paths, spec references).
 */

import type { DialogueMessage as DialogueMessageData, FocusType } from './useMembrane';

// Simple relative time formatter (native, no date-fns dependency)
function formatTimeAgo(date: Date): string {
  const now = new Date();
  const seconds = Math.floor((now.getTime() - date.getTime()) / 1000);

  if (seconds < 60) return 'just now';
  const minutes = Math.floor(seconds / 60);
  if (minutes < 60) return `${minutes}m ago`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours}h ago`;
  const days = Math.floor(hours / 24);
  return `${days}d ago`;
}

import './DialogueMessage.css';

// =============================================================================
// Types
// =============================================================================

interface DialogueMessageProps {
  message: DialogueMessageData;
  onFocusRequest: (type: FocusType, path?: string) => void;
}

interface ParsedSegment {
  type: 'text' | 'focus-link';
  content: string;
  focusType?: FocusType;
  path?: string;
  label?: string;
}

// =============================================================================
// Component
// =============================================================================

export function DialogueMessage({ message, onFocusRequest }: DialogueMessageProps) {
  const segments = parseContent(message.content);
  const timeAgo = formatTimeAgo(message.timestamp);

  return (
    <div className={`dialogue-message dialogue-message--${message.role}`}>
      <div className="dialogue-message__header">
        <span className="dialogue-message__role">{message.role === 'user' ? 'You' : 'K-gent'}</span>
        <span className="dialogue-message__time">{timeAgo}</span>
      </div>

      <div className="dialogue-message__content">
        {segments.map((seg, i) =>
          seg.type === 'text' ? (
            <span key={i}>{seg.content}</span>
          ) : (
            <button
              key={i}
              className="dialogue-message__focus-link"
              onClick={() => seg.focusType && onFocusRequest(seg.focusType, seg.path)}
            >
              {seg.label || seg.path}
            </button>
          )
        )}
      </div>
    </div>
  );
}

// =============================================================================
// Content Parser
// =============================================================================

/**
 * Parse message content to find focus links.
 *
 * Patterns recognized:
 * - File paths: `/path/to/file.py` or `path/to/file.tsx`
 * - Spec references: `spec/...`
 * - Concept references: `concept:name`
 */
function parseContent(content: string): ParsedSegment[] {
  const segments: ParsedSegment[] = [];

  // Pattern for file paths and spec references
  const pattern = /(`[^`]+`|(?:spec\/|impl\/|src\/)[^\s,)]+\.[a-z]+|concept:\w+)/g;

  let lastIndex = 0;
  let match: RegExpExecArray | null;

  while ((match = pattern.exec(content)) !== null) {
    // Add text before this match
    if (match.index > lastIndex) {
      segments.push({
        type: 'text',
        content: content.slice(lastIndex, match.index),
      });
    }

    const matched = match[0];
    const cleanMatch = matched.replace(/`/g, '');

    // Determine focus type
    let focusType: FocusType = 'file';
    let path = cleanMatch;

    if (cleanMatch.startsWith('spec/')) {
      focusType = 'spec';
    } else if (cleanMatch.startsWith('concept:')) {
      focusType = 'concept';
      path = cleanMatch.replace('concept:', '');
    }

    segments.push({
      type: 'focus-link',
      content: matched,
      focusType,
      path,
      label: path.split('/').pop() || path,
    });

    lastIndex = match.index + matched.length;
  }

  // Add remaining text
  if (lastIndex < content.length) {
    segments.push({
      type: 'text',
      content: content.slice(lastIndex),
    });
  }

  // If no segments, return the whole content as text
  if (segments.length === 0) {
    segments.push({ type: 'text', content });
  }

  return segments;
}
