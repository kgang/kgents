/**
 * WitnessMark Component
 *
 * Displays a single witness mark with principles, reasoning, and timestamp.
 */

import { memo, useMemo } from 'react';
import type { WitnessMark, WitnessMarkVariant } from './types';
import { PRINCIPLE_COLORS, PRINCIPLE_ICONS } from './types';

// =============================================================================
// Props
// =============================================================================

export interface WitnessMarkProps {
  /** The mark to display */
  mark: WitnessMark;

  /** Display variant */
  variant?: WitnessMarkVariant;

  /** Whether to show principles */
  showPrinciples?: boolean;

  /** Whether to show reasoning */
  showReasoning?: boolean;

  /** Whether to show timestamp */
  showTimestamp?: boolean;

  /** Whether to show author */
  showAuthor?: boolean;

  /** Click handler */
  onClick?: () => void;

  /** Additional CSS classes */
  className?: string;
}

// =============================================================================
// Component
// =============================================================================

export const WitnessMarkComponent = memo(function WitnessMarkComponent({
  mark,
  variant = 'card',
  showPrinciples = true,
  showReasoning = true,
  showTimestamp = true,
  showAuthor = true,
  onClick,
  className = '',
}: WitnessMarkProps) {
  // Format timestamp
  const formattedTime = useMemo(() => {
    return formatTimestamp(mark.timestamp);
  }, [mark.timestamp]);

  // Get primary principle color (first principle)
  const primaryColor = useMemo(() => {
    if (mark.principles.length === 0) return '#666';
    const principle = mark.principles[0];
    return PRINCIPLE_COLORS[principle as keyof typeof PRINCIPLE_COLORS] || '#666';
  }, [mark.principles]);

  if (variant === 'minimal') {
    return (
      <div
        className={`witness-mark witness-mark--minimal ${className}`}
        onClick={onClick}
        style={{ borderLeftColor: primaryColor }}
      >
        <div className="witness-mark__action">{mark.action}</div>
      </div>
    );
  }

  if (variant === 'badge') {
    return (
      <div
        className={`witness-mark witness-mark--badge ${className}`}
        onClick={onClick}
        style={{ backgroundColor: primaryColor }}
      >
        <div className="witness-mark__badge-text">
          {mark.principles.length > 0 && (
            <span className="witness-mark__badge-icon">
              {PRINCIPLE_ICONS[mark.principles[0] as keyof typeof PRINCIPLE_ICONS]}
            </span>
          )}
          {mark.action}
        </div>
      </div>
    );
  }

  if (variant === 'inline') {
    return (
      <div
        className={`witness-mark witness-mark--inline ${className}`}
        onClick={onClick}
      >
        <div className="witness-mark__inline-content">
          <span className="witness-mark__action">{mark.action}</span>
          {showTimestamp && (
            <span className="witness-mark__time">{formattedTime}</span>
          )}
        </div>
      </div>
    );
  }

  // Card variant (default)
  return (
    <div
      className={`witness-mark witness-mark--card ${className}`}
      onClick={onClick}
      style={{ borderLeftColor: primaryColor }}
    >
      {/* Header */}
      <div className="witness-mark__header">
        <div className="witness-mark__action">{mark.action}</div>
        {mark.automatic && (
          <div className="witness-mark__auto-badge" title="Automatically witnessed">
            auto
          </div>
        )}
      </div>

      {/* Reasoning */}
      {showReasoning && mark.reasoning && (
        <div className="witness-mark__reasoning">{mark.reasoning}</div>
      )}

      {/* Principles */}
      {showPrinciples && mark.principles.length > 0 && (
        <div className="witness-mark__principles">
          {mark.principles.map((principle) => {
            const color = PRINCIPLE_COLORS[principle as keyof typeof PRINCIPLE_COLORS] || '#666';
            const icon = PRINCIPLE_ICONS[principle as keyof typeof PRINCIPLE_ICONS] || '';

            return (
              <div
                key={principle}
                className="witness-mark__principle"
                style={{ backgroundColor: color }}
                title={principle}
              >
                {icon && <span className="witness-mark__principle-icon">{icon}</span>}
                <span className="witness-mark__principle-name">{principle}</span>
              </div>
            );
          })}
        </div>
      )}

      {/* Footer */}
      <div className="witness-mark__footer">
        {showAuthor && (
          <div className="witness-mark__author">{mark.author}</div>
        )}
        {showTimestamp && (
          <div className="witness-mark__time" title={new Date(mark.timestamp).toISOString()}>
            {formattedTime}
          </div>
        )}
      </div>
    </div>
  );
});

// =============================================================================
// Utility Functions
// =============================================================================

/**
 * Format timestamp relative to now.
 */
function formatTimestamp(timestamp: string): string {
  const date = new Date(timestamp);
  const now = new Date();
  const diff = now.getTime() - date.getTime();

  // Less than 1 minute
  if (diff < 60 * 1000) {
    return 'just now';
  }

  // Less than 1 hour
  if (diff < 60 * 60 * 1000) {
    const minutes = Math.floor(diff / (60 * 1000));
    return `${minutes}m ago`;
  }

  // Less than 1 day
  if (diff < 24 * 60 * 60 * 1000) {
    const hours = Math.floor(diff / (60 * 60 * 1000));
    return `${hours}h ago`;
  }

  // Less than 1 week
  if (diff < 7 * 24 * 60 * 60 * 1000) {
    const days = Math.floor(diff / (24 * 60 * 60 * 1000));
    return `${days}d ago`;
  }

  // More than 1 week - show full date
  return date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: date.getFullYear() !== now.getFullYear() ? 'numeric' : undefined,
  });
}

export default WitnessMarkComponent;
