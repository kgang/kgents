/**
 * WitnessTrail Component
 *
 * Displays a sequence of witness marks as a causal trail.
 *
 * "The trail IS the proof. The proof IS the trail."
 */

import { memo, useMemo } from 'react';
import type { WitnessMark, WitnessTrailOrientation } from './types';
import { WitnessMarkComponent } from './WitnessMark';

// =============================================================================
// Props
// =============================================================================

export interface WitnessTrailProps {
  /** Marks in the trail (chronological order) */
  marks: WitnessMark[];

  /** Maximum number of marks to show (default: all) */
  maxVisible?: number;

  /** Orientation of the trail */
  orientation?: WitnessTrailOrientation;

  /** Whether to show connections between marks */
  showConnections?: boolean;

  /** Whether to show principles */
  showPrinciples?: boolean;

  /** Whether to show reasoning */
  showReasoning?: boolean;

  /** Click handler for individual marks */
  onMarkClick?: (mark: WitnessMark, index: number) => void;

  /** Additional CSS classes */
  className?: string;
}

// =============================================================================
// Component
// =============================================================================

export const WitnessTrailComponent = memo(function WitnessTrailComponent({
  marks,
  maxVisible,
  orientation = 'vertical',
  showConnections = true,
  showPrinciples = true,
  showReasoning = false,
  onMarkClick,
  className = '',
}: WitnessTrailProps) {
  // Determine visible marks
  const visibleMarks = useMemo(() => {
    if (maxVisible === undefined) {
      return marks;
    }
    return marks.slice(0, maxVisible);
  }, [marks, maxVisible]);

  // Check if there are hidden marks
  const hasMore = maxVisible !== undefined && marks.length > maxVisible;
  const hiddenCount = hasMore ? marks.length - maxVisible : 0;

  if (marks.length === 0) {
    return (
      <div className={`witness-trail witness-trail--empty ${className}`}>
        <div className="witness-trail__empty-message">No marks yet</div>
      </div>
    );
  }

  return (
    <div
      className={`witness-trail witness-trail--${orientation} ${className}`}
      data-mark-count={marks.length}
    >
      {/* Trail container */}
      <div className="witness-trail__marks">
        {visibleMarks.map((mark, index) => (
          <div key={mark.id} className="witness-trail__mark-wrapper">
            {/* Connection line (before mark, except for first) */}
            {showConnections && index > 0 && (
              <div className="witness-trail__connection" />
            )}

            {/* The mark */}
            <WitnessMarkComponent
              mark={mark}
              variant="card"
              showPrinciples={showPrinciples}
              showReasoning={showReasoning}
              showTimestamp={true}
              showAuthor={true}
              onClick={onMarkClick ? () => onMarkClick(mark, index) : undefined}
            />
          </div>
        ))}

        {/* Show more indicator */}
        {hasMore && (
          <div className="witness-trail__more">
            <div className="witness-trail__more-text">
              +{hiddenCount} more {hiddenCount === 1 ? 'mark' : 'marks'}
            </div>
          </div>
        )}
      </div>

      {/* Trail metadata */}
      {marks.length > 0 && (
        <div className="witness-trail__metadata">
          <div className="witness-trail__count">
            {marks.length} {marks.length === 1 ? 'mark' : 'marks'}
          </div>
          {marks[0] && (
            <div className="witness-trail__start-time">
              Started {formatTrailTime(marks[0].timestamp)}
            </div>
          )}
        </div>
      )}
    </div>
  );
});

// =============================================================================
// Utility Functions
// =============================================================================

/**
 * Format trail start time.
 */
function formatTrailTime(timestamp: string): string {
  const date = new Date(timestamp);
  const now = new Date();

  // Same day - show time
  if (
    date.getFullYear() === now.getFullYear() &&
    date.getMonth() === now.getMonth() &&
    date.getDate() === now.getDate()
  ) {
    return date.toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
    });
  }

  // Different day - show date
  return date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: date.getFullYear() !== now.getFullYear() ? 'numeric' : undefined,
  });
}

export default WitnessTrailComponent;
