/**
 * PrincipleScore - Single constitutional principle indicator
 *
 * Displays a single principle score as a pill/badge with color coding.
 * Used inline or in grids for compact principle displays.
 *
 * Design: STARK biome with tier-based color coding
 */

import { memo } from 'react';
import type { PrincipleKey, ConstitutionalScores } from './types';
import { PRINCIPLES, getScoreColor, formatScore } from './types';
import './PrincipleScore.css';

// =============================================================================
// Types
// =============================================================================

export interface PrincipleScoreProps {
  /** Which principle to display */
  principle: PrincipleKey;

  /** Score value (0-1) */
  score: number;

  /** Show principle label (default: true) */
  showLabel?: boolean;

  /** Size variant */
  size?: 'sm' | 'md' | 'lg';

  /** Click handler */
  onClick?: (principle: PrincipleKey) => void;
}

// =============================================================================
// Component
// =============================================================================

/**
 * PrincipleScore - Single principle badge with color-coded score
 *
 * Color coding:
 * - Green (>0.8): High adherence
 * - Yellow (0.5-0.8): Medium adherence
 * - Red (<0.5): Low adherence
 */
export const PrincipleScore = memo(function PrincipleScore({
  principle,
  score,
  showLabel = true,
  size = 'md',
  onClick,
}: PrincipleScoreProps) {
  const meta = PRINCIPLES[principle];
  const color = getScoreColor(score);
  const formattedScore = formatScore(score);

  const handleClick = () => {
    onClick?.(principle);
  };

  return (
    <div
      className={`principle-score principle-score--${size} ${onClick ? 'principle-score--clickable' : ''}`}
      onClick={onClick ? handleClick : undefined}
      role={onClick ? 'button' : undefined}
      tabIndex={onClick ? 0 : undefined}
      title={`${meta.label}: ${meta.description}`}
    >
      {/* Color indicator dot */}
      <div
        className="principle-score__indicator"
        style={{ backgroundColor: color }}
        aria-hidden="true"
      />

      {/* Label */}
      {showLabel && (
        <span className="principle-score__label">{meta.shortLabel}</span>
      )}

      {/* Score value */}
      <span className="principle-score__value" style={{ color }}>
        {formattedScore}
      </span>
    </div>
  );
});

// =============================================================================
// Compound Component: All Principles
// =============================================================================

export interface AllPrincipleScoresProps {
  /** All principle scores */
  scores: ConstitutionalScores;

  /** Show labels (default: true) */
  showLabels?: boolean;

  /** Size variant */
  size?: 'sm' | 'md' | 'lg';

  /** Click handler */
  onPrincipleClick?: (principle: PrincipleKey) => void;

  /** Layout variant */
  layout?: 'row' | 'grid';
}

export const AllPrincipleScores = memo(function AllPrincipleScores({
  scores,
  showLabels = true,
  size = 'md',
  onPrincipleClick,
  layout = 'grid',
}: AllPrincipleScoresProps) {
  return (
    <div className={`all-principle-scores all-principle-scores--${layout}`}>
      {(Object.keys(PRINCIPLES) as PrincipleKey[]).map((key) => (
        <PrincipleScore
          key={key}
          principle={key}
          score={scores[key]}
          showLabel={showLabels}
          size={size}
          onClick={onPrincipleClick}
        />
      ))}
    </div>
  );
});

export default PrincipleScore;
