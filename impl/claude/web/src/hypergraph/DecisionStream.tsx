/**
 * DecisionStream — Scrollable decision list
 *
 * Shows all dialectic decisions with filtering.
 * Click to view full dialectic in DialogueView.
 */

import { memo, useCallback, useState } from 'react';
import type { DialecticDecision } from './types/dialectic';
import { useDialecticDecisions } from './useDialecticDecisions';

import './DecisionStream.css';

// =============================================================================
// Types
// =============================================================================

interface DecisionStreamProps {
  /** Called when decision is clicked */
  onDecisionClick?: (decision: DialecticDecision) => void;

  /** Called when stream is closed */
  onClose?: () => void;

  /** Polling interval (default: 30s) */
  pollInterval?: number;
}

// Common tags for filtering
const FILTER_TAGS = ['eureka', 'gotcha', 'taste', 'friction', 'joy', 'veto'] as const;

// =============================================================================
// Component
// =============================================================================

export const DecisionStream = memo(function DecisionStream({
  onDecisionClick,
  onClose,
  pollInterval = 30000,
}: DecisionStreamProps) {
  const [selectedTags, setSelectedTags] = useState<string[]>([]);
  const [dateFilter, setDateFilter] = useState<'all' | 'today' | 'week' | 'month'>('all');

  const { decisions, loading, error, refresh } = useDialecticDecisions({
    pollInterval,
    autoFetch: true,
  });

  // Toggle tag filter
  const toggleTag = useCallback((tag: string) => {
    setSelectedTags((prev) => {
      if (prev.includes(tag)) {
        return prev.filter((t) => t !== tag);
      }
      return [...prev, tag];
    });
  }, []);

  // Filter decisions
  const filteredDecisions = decisions.filter((decision) => {
    // Tag filter
    if (selectedTags.length > 0) {
      const hasTag = selectedTags.some((tag) => decision.tags.includes(tag));
      if (!hasTag) return false;
    }

    // Date filter
    if (dateFilter !== 'all') {
      const decisionDate = new Date(decision.timestamp);
      const now = new Date();
      const diffDays = Math.floor(
        (now.getTime() - decisionDate.getTime()) / (1000 * 60 * 60 * 24)
      );

      if (dateFilter === 'today' && diffDays > 0) return false;
      if (dateFilter === 'week' && diffDays > 7) return false;
      if (dateFilter === 'month' && diffDays > 30) return false;
    }

    return true;
  });

  // Handle decision click
  const handleDecisionClick = useCallback(
    (decision: DialecticDecision) => {
      onDecisionClick?.(decision);
    },
    [onDecisionClick]
  );

  return (
    <div className="decision-stream__overlay" onClick={onClose}>
      <div className="decision-stream" onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className="decision-stream__header">
          <h2 className="decision-stream__title">DECISION STREAM</h2>
          <button
            className="decision-stream__refresh"
            onClick={refresh}
            disabled={loading}
            title="Refresh"
          >
            ↻
          </button>
          {onClose && (
            <button
              className="decision-stream__close"
              onClick={onClose}
              title="Close (Esc)"
            >
              ×
            </button>
          )}
        </div>

        {/* Filters */}
        <div className="decision-stream__filters">
          {/* Date filter */}
          <div className="decision-stream__filter-group">
            <label className="decision-stream__filter-label">Time:</label>
            <div className="decision-stream__filter-buttons">
              {(['all', 'today', 'week', 'month'] as const).map((filter) => (
                <button
                  key={filter}
                  className={`decision-stream__filter-button ${dateFilter === filter ? 'decision-stream__filter-button--active' : ''}`}
                  onClick={() => setDateFilter(filter)}
                >
                  {filter}
                </button>
              ))}
            </div>
          </div>

          {/* Tag filter */}
          <div className="decision-stream__filter-group">
            <label className="decision-stream__filter-label">Tags:</label>
            <div className="decision-stream__filter-tags">
              {FILTER_TAGS.map((tag) => (
                <button
                  key={tag}
                  className={`decision-stream__tag ${selectedTags.includes(tag) ? 'decision-stream__tag--selected' : ''}`}
                  onClick={() => toggleTag(tag)}
                >
                  {tag}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* List */}
        <div className="decision-stream__list">
          {loading && decisions.length === 0 && (
            <div className="decision-stream__empty">Loading decisions...</div>
          )}

          {error && (
            <div className="decision-stream__error">
              Error: {error}
            </div>
          )}

          {!loading && !error && filteredDecisions.length === 0 && (
            <div className="decision-stream__empty">
              {decisions.length === 0 ? (
                <div className="decision-stream__welcome">
                  <div className="decision-stream__welcome-icon">⊢</div>
                  <h3>No dialectic decisions yet</h3>
                  <p>
                    Dialectic decisions capture the fusion of Kent's thesis and Claude's antithesis
                    into a synthesis—a third thing, better than either alone.
                  </p>
                  <p className="decision-stream__hint-text">
                    Press <kbd>g</kbd><kbd>w</kbd> to enter witness mode and create a mark,
                    or use <code>kg decide</code> from the CLI.
                  </p>
                </div>
              ) : (
                'No decisions match filters'
              )}
            </div>
          )}

          {filteredDecisions.map((decision) => (
            <DecisionCard
              key={decision.id}
              decision={decision}
              onClick={handleDecisionClick}
            />
          ))}
        </div>

        {/* Footer */}
        <div className="decision-stream__footer">
          <span className="decision-stream__count">
            {filteredDecisions.length} of {decisions.length} decisions
          </span>
          <span className="decision-stream__hint">
            <kbd>Esc</kbd> Close
          </span>
        </div>
      </div>
    </div>
  );
});

// =============================================================================
// DecisionCard Component
// =============================================================================

interface DecisionCardProps {
  decision: DialecticDecision;
  onClick: (decision: DialecticDecision) => void;
}

const DecisionCard = memo(function DecisionCard({
  decision,
  onClick,
}: DecisionCardProps) {
  const handleClick = useCallback(() => {
    onClick(decision);
  }, [decision, onClick]);

  const timestamp = new Date(decision.timestamp);
  const timeStr = timestamp.toLocaleString(undefined, {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });

  return (
    <div
      className="decision-card"
      onClick={handleClick}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          handleClick();
        }
      }}
    >
      {/* Header */}
      <div className="decision-card__header">
        <span className="decision-card__timestamp">{timeStr}</span>
        {decision.vetoed && (
          <span className="decision-card__veto-badge">VETOED</span>
        )}
      </div>

      {/* Synthesis preview */}
      <div className="decision-card__synthesis">
        {truncate(decision.synthesis, 120)}
      </div>

      {/* Tags */}
      {decision.tags.length > 0 && (
        <div className="decision-card__tags">
          {decision.tags.map((tag) => (
            <span key={tag} className="decision-card__tag">
              {tag}
            </span>
          ))}
        </div>
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

export default DecisionStream;
