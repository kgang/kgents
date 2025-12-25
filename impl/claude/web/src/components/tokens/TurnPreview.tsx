/**
 * TurnPreview — Preview of a chat turn (user + assistant pair)
 *
 * Shows a compact preview of a single turn from a chat session.
 * Used when expanding turn: resources in portal tokens.
 *
 * See spec/protocols/portal-resource-system.md §5.1
 */

import './tokens.css';

// =============================================================================
// Types
// =============================================================================

export interface TurnContent {
  user_message: string;
  assistant_response: string;
}

export interface TurnPreviewProps {
  /** Turn content */
  turn: TurnContent;
  /** Turn number (optional) */
  turnNumber?: number;
  /** Compact mode (shorter preview) */
  compact?: boolean;
}

// =============================================================================
// Component
// =============================================================================

/**
 * TurnPreview — User/Assistant message pair preview
 */
export function TurnPreview({ turn, turnNumber, compact = false }: TurnPreviewProps) {
  const maxLength = compact ? 100 : 300;

  const truncate = (text: string, max: number): string => {
    if (text.length <= max) return text;
    return text.slice(0, max) + '...';
  };

  return (
    <div className="turn-preview">
      {turnNumber !== undefined && (
        <div className="turn-preview__header">
          <span className="turn-preview__number">Turn {turnNumber}</span>
        </div>
      )}

      <div className="turn-preview__messages">
        {/* User message */}
        <div className="turn-preview__message turn-preview__message--user">
          <div className="turn-preview__role">User</div>
          <div className="turn-preview__content">
            {truncate(turn.user_message, maxLength)}
          </div>
        </div>

        {/* Assistant response */}
        <div className="turn-preview__message turn-preview__message--assistant">
          <div className="turn-preview__role">Assistant</div>
          <div className="turn-preview__content">
            {truncate(turn.assistant_response, maxLength)}
          </div>
        </div>
      </div>
    </div>
  );
}

export default TurnPreview;
