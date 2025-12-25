/**
 * ConfidenceBar — Brutalist numerical confidence display
 *
 * Replaces emoji-based ConfidenceIndicator with pure text/bar visualization.
 *
 * Display format: [████████░░] 82%
 *
 * Principles:
 * - No colors except black/white
 * - Exact percentage shown
 * - Horizontal bar with ASCII-style fill
 * - Minimal decoration
 */

import '../../styles/brutalist.css';

// =============================================================================
// Types
// =============================================================================

export interface ConfidenceBarProps {
  /** Confidence value (0-1) */
  confidence: number;
  /** Show label */
  showLabel?: boolean;
  /** Size of bar */
  size?: 'sm' | 'md' | 'lg';
  /** Show numeric value */
  showValue?: boolean;
}

// =============================================================================
// Component
// =============================================================================

export function ConfidenceBar({
  confidence,
  showLabel = true,
  size = 'md',
  showValue = true,
}: ConfidenceBarProps) {
  // Don't show if confidence is 0
  if (confidence === 0) {
    return null;
  }

  // Calculate percentage
  const percentage = Math.round(confidence * 100);

  // Determine bar width based on size
  const barWidths = {
    sm: 100,
    md: 150,
    lg: 200,
  };
  const barWidth = barWidths[size];

  return (
    <div
      className="brutalist-confidence-bar"
      role="status"
      aria-label={`Confidence: ${percentage}%`}
    >
      {showLabel && (
        <span className="brutalist-confidence-bar__label">CONF</span>
      )}

      <div
        className="brutalist-confidence-bar__track"
        style={{ maxWidth: `${barWidth}px` }}
      >
        <div
          className="brutalist-confidence-bar__fill"
          style={{ width: `${percentage}%` }}
        />
      </div>

      {showValue && (
        <span className="brutalist-confidence-bar__value">
          {percentage}%
        </span>
      )}
    </div>
  );
}

export default ConfidenceBar;
