/**
 * DecisionFooterWidget — Compact decision display
 *
 * Shows last dialectic decision in status line area.
 * Click to expand to full DialogueView.
 * Animate on new decision.
 */

import { memo, useCallback, useEffect, useState } from 'react';
import type { DialecticDecision } from './types/dialectic';

import './DecisionFooterWidget.css';

// =============================================================================
// Types
// =============================================================================

interface DecisionFooterWidgetProps {
  /** Last decision to display */
  lastDecision?: DialecticDecision | null;

  /** Called when widget is clicked (to expand to full view) */
  onClick?: (decision: DialecticDecision) => void;

  /** Called when close is clicked */
  onClose?: () => void;
}

// =============================================================================
// Component
// =============================================================================

export const DecisionFooterWidget = memo(function DecisionFooterWidget({
  lastDecision,
  onClick,
  onClose,
}: DecisionFooterWidgetProps) {
  const [isNew, setIsNew] = useState(false);
  const [prevDecisionId, setPrevDecisionId] = useState<string | null>(null);

  // Detect new decision and trigger animation
  useEffect(() => {
    if (lastDecision && lastDecision.id !== prevDecisionId) {
      setIsNew(true);
      setPrevDecisionId(lastDecision.id);

      // Clear animation after 2 seconds
      const timer = setTimeout(() => {
        setIsNew(false);
      }, 2000);

      return () => clearTimeout(timer);
    }
  }, [lastDecision, prevDecisionId]);

  // Handle click
  const handleClick = useCallback(() => {
    if (lastDecision && onClick) {
      onClick(lastDecision);
    }
  }, [lastDecision, onClick]);

  // Handle close
  const handleClose = useCallback(
    (e: React.MouseEvent) => {
      e.stopPropagation();
      onClose?.();
    },
    [onClose]
  );

  // Don't render if no decision
  if (!lastDecision) {
    return null;
  }

  // Format timestamp
  const timestamp = new Date(lastDecision.timestamp);
  const timeAgo = getTimeAgo(timestamp);

  return (
    <div
      className={`decision-footer ${isNew ? 'decision-footer--new' : ''}`}
      onClick={handleClick}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          handleClick();
        }
      }}
    >
      {/* Icon */}
      <div className="decision-footer__icon">⊢</div>

      {/* Content */}
      <div className="decision-footer__content">
        <div className="decision-footer__header">
          <span className="decision-footer__label">Last Decision:</span>
          <span className="decision-footer__time">{timeAgo}</span>
        </div>
        <div className="decision-footer__synthesis">
          {truncate(lastDecision.synthesis, 80)}
        </div>
        {lastDecision.tags.length > 0 && (
          <div className="decision-footer__tags">
            {lastDecision.tags.map((tag) => (
              <span key={tag} className="decision-footer__tag">
                {tag}
              </span>
            ))}
          </div>
        )}
      </div>

      {/* Close button */}
      {onClose && (
        <button
          className="decision-footer__close"
          onClick={handleClose}
          title="Hide"
          aria-label="Close decision widget"
        >
          ×
        </button>
      )}
    </div>
  );
});

// =============================================================================
// Utilities
// =============================================================================

function truncate(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text;
  return text.slice(0, maxLength - 3) + '...';
}

function getTimeAgo(timestamp: Date): string {
  const now = new Date();
  const diffMs = now.getTime() - timestamp.getTime();
  const diffSec = Math.floor(diffMs / 1000);
  const diffMin = Math.floor(diffSec / 60);
  const diffHour = Math.floor(diffMin / 60);
  const diffDay = Math.floor(diffHour / 24);

  if (diffSec < 60) return 'just now';
  if (diffMin < 60) return `${diffMin}m ago`;
  if (diffHour < 24) return `${diffHour}h ago`;
  if (diffDay === 1) return 'yesterday';
  if (diffDay < 7) return `${diffDay}d ago`;

  // Format as date for older decisions
  return timestamp.toLocaleDateString(undefined, {
    month: 'short',
    day: 'numeric',
  });
}

export default DecisionFooterWidget;
