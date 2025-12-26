/**
 * ConstitutionalSummary - Compact overview of constitutional scores
 *
 * Displays overall constitutional score with optional breakdown.
 * Used for quick assessments and dashboard widgets.
 *
 * Design: STARK biome with tier-based color coding
 */

import { memo } from 'react';
import type { ConstitutionalScores } from './types';
import { calculateOverallScore, getScoreTier, formatScore } from './types';
import { AllPrincipleScores } from './PrincipleScore';
import './ConstitutionalSummary.css';

// =============================================================================
// Types
// =============================================================================

export interface ConstitutionalSummaryProps {
  /** All principle scores */
  scores: ConstitutionalScores;

  /** Display variant */
  variant?: 'compact' | 'expanded';

  /** Show individual principle breakdown (expanded only) */
  showBreakdown?: boolean;

  /** Size variant */
  size?: 'sm' | 'md' | 'lg';
}

// =============================================================================
// Component
// =============================================================================

/**
 * ConstitutionalSummary - Overall constitutional score display
 *
 * Compact: Just overall score badge
 * Expanded: Overall score + individual principle breakdown
 */
export const ConstitutionalSummary = memo(function ConstitutionalSummary({
  scores,
  variant = 'compact',
  showBreakdown = true,
  size = 'md',
}: ConstitutionalSummaryProps) {
  const overallScore = calculateOverallScore(scores);
  const tier = getScoreTier(overallScore);
  const formattedScore = formatScore(overallScore);

  // Compact variant: just badge
  if (variant === 'compact') {
    return (
      <div
        className={`constitutional-summary constitutional-summary--compact constitutional-summary--${size} constitutional-summary--${tier}`}
      >
        <div className="constitutional-summary__badge">
          <span className="constitutional-summary__label">Constitutional</span>
          <span className="constitutional-summary__score">{formattedScore}</span>
        </div>
      </div>
    );
  }

  // Expanded variant: badge + breakdown
  return (
    <div
      className={`constitutional-summary constitutional-summary--expanded constitutional-summary--${size} constitutional-summary--${tier}`}
    >
      {/* Overall score */}
      <div className="constitutional-summary__header">
        <div className="constitutional-summary__title">
          <span className="constitutional-summary__label">
            Constitutional Score
          </span>
          <span
            className="constitutional-summary__tier"
            title={getTierDescription(tier)}
          >
            {getTierLabel(tier)}
          </span>
        </div>
        <div className="constitutional-summary__score">{formattedScore}</div>
      </div>

      {/* Individual principle breakdown */}
      {showBreakdown && (
        <div className="constitutional-summary__breakdown">
          <AllPrincipleScores scores={scores} size={size} layout="grid" />
        </div>
      )}
    </div>
  );
});

// =============================================================================
// Helpers
// =============================================================================

function getTierLabel(tier: 'high' | 'medium' | 'low'): string {
  switch (tier) {
    case 'high':
      return 'High Adherence';
    case 'medium':
      return 'Moderate Adherence';
    case 'low':
      return 'Low Adherence';
  }
}

function getTierDescription(tier: 'high' | 'medium' | 'low'): string {
  switch (tier) {
    case 'high':
      return 'Strong adherence to constitutional principles (>80%)';
    case 'medium':
      return 'Moderate adherence to constitutional principles (50-80%)';
    case 'low':
      return 'Low adherence to constitutional principles (<50%)';
  }
}

export default ConstitutionalSummary;
