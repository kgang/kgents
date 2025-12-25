/**
 * ConstitutionalBadge — Compact constitutional health indicator
 *
 * Shows aggregated constitutional score across all 7 principles.
 * Expands to show ConstitutionalRadar on click.
 *
 * Design: Brutalist, minimal, non-intrusive
 */

import type { PrincipleScore } from '../../types/chat';
import './ConstitutionalBadge.css';

// =============================================================================
// Types
// =============================================================================

export interface ConstitutionalBadgeProps {
  /** Principle scores (0-1 range) */
  scores: PrincipleScore;
  /** Click handler to expand radar view */
  onClick?: () => void;
  /** Size variant */
  size?: 'sm' | 'md' | 'lg';
}

// =============================================================================
// Component
// =============================================================================

/**
 * ConstitutionalBadge — Single-score summary of constitutional health
 *
 * Aggregates 7 principle scores into a single 0-100 value.
 * Color codes: green (>80), yellow (50-80), red (<50)
 */
export function ConstitutionalBadge({
  scores,
  onClick,
  size = 'md',
}: ConstitutionalBadgeProps) {
  // Calculate aggregated score (0-100)
  const aggregated = calculateAggregatedScore(scores);

  // Determine health level
  const level = aggregated > 80 ? 'high' : aggregated >= 50 ? 'medium' : 'low';

  // Label text
  const label = level === 'high' ? 'HIGH' : level === 'medium' ? 'MED' : 'LOW';

  return (
    <button
      className={`constitutional-badge constitutional-badge--${level} constitutional-badge--${size}`}
      onClick={onClick}
      aria-label={`Constitutional health: ${label} (${aggregated}/100)`}
      title="Click to view detailed principle scores"
      type="button"
    >
      <span className="constitutional-badge__label">CONST</span>
      <span className="constitutional-badge__value">{aggregated}</span>
      <span className="constitutional-badge__icon">▸</span>
    </button>
  );
}

// =============================================================================
// Helpers
// =============================================================================

/**
 * Calculate aggregated constitutional score (0-100).
 * Simple average of all 7 principles, scaled to 0-100.
 */
function calculateAggregatedScore(scores: PrincipleScore): number {
  const values = [
    scores.tasteful,
    scores.curated,
    scores.ethical,
    scores.joy_inducing,
    scores.composable,
    scores.heterarchical,
    scores.generative,
  ];

  const sum = values.reduce((acc, val) => acc + val, 0);
  const average = sum / values.length;

  return Math.round(average * 100);
}

export default ConstitutionalBadge;
