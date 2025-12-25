/**
 * ChatSessionPreview — Preview of a chat session
 *
 * Shows session metadata and summary.
 * Used when expanding chat: resources in portal tokens.
 *
 * See spec/protocols/portal-resource-system.md §5.1
 */

import './tokens.css';

// =============================================================================
// Types
// =============================================================================

export interface ChatSession {
  session_id: string;
  branch_name?: string;
  turn_count: number;
  flow_state?: string;
  created_at?: string;
  updated_at?: string;
}

export interface ChatSessionPreviewProps {
  /** Session content */
  session: ChatSession;
  /** Show full details vs compact */
  compact?: boolean;
}

// =============================================================================
// Component
// =============================================================================

/**
 * ChatSessionPreview — Session summary
 */
export function ChatSessionPreview({ session, compact = false }: ChatSessionPreviewProps) {
  const formatDate = (isoString?: string): string => {
    if (!isoString) return 'Unknown';
    const date = new Date(isoString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMins / 60);
    const diffDays = Math.floor(diffHours / 24);

    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    return date.toLocaleDateString();
  };

  return (
    <div className="chat-session-preview">
      <div className="chat-session-preview__header">
        <div className="chat-session-preview__title">
          {session.branch_name || session.session_id}
        </div>
        {session.flow_state && (
          <span className="chat-session-preview__state">{session.flow_state}</span>
        )}
      </div>

      <div className="chat-session-preview__stats">
        <div className="chat-session-preview__stat">
          <span className="chat-session-preview__stat-label">Turns</span>
          <span className="chat-session-preview__stat-value">{session.turn_count}</span>
        </div>

        {!compact && session.updated_at && (
          <div className="chat-session-preview__stat">
            <span className="chat-session-preview__stat-label">Updated</span>
            <span className="chat-session-preview__stat-value">
              {formatDate(session.updated_at)}
            </span>
          </div>
        )}

        {!compact && session.created_at && (
          <div className="chat-session-preview__stat">
            <span className="chat-session-preview__stat-label">Created</span>
            <span className="chat-session-preview__stat-value">
              {formatDate(session.created_at)}
            </span>
          </div>
        )}
      </div>

      {!compact && (
        <div className="chat-session-preview__id">
          <span className="chat-session-preview__id-label">ID:</span>
          <code className="chat-session-preview__id-value">{session.session_id}</code>
        </div>
      )}
    </div>
  );
}

export default ChatSessionPreview;
