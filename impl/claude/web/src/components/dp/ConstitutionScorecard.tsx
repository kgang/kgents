/**
 * ConstitutionScorecard — Dashboard showing per-principle scores
 *
 * Displays all 7 principles with:
 * - Score bar (0-100%)
 * - Health indicator (color-coded)
 * - Evidence text (expandable)
 * - Weight indicator
 *
 * Stark table layout. No decoration, pure information.
 */

import { useState } from 'react';
import type { ValueScore, Principle, PrincipleScore } from './types';
import { PRINCIPLE_LABELS, PRINCIPLE_DESCRIPTIONS } from './types';
import './ConstitutionScorecard.css';

// =============================================================================
// Types
// =============================================================================

export interface ConstitutionScorecardProps {
  /** Value score to visualize */
  valueScore: ValueScore | null;
  /** Compact mode (hide evidence) */
  compact?: boolean;
  /** Show weights */
  showWeights?: boolean;
  /** Threshold for warnings (default 0.5) */
  warningThreshold?: number;
}

// =============================================================================
// Helpers
// =============================================================================

function getHealthColor(score: number): string {
  if (score >= 0.8) return 'var(--health-healthy)';
  if (score >= 0.6) return 'var(--health-degraded)';
  if (score >= 0.4) return 'var(--health-warning)';
  return 'var(--health-critical)';
}

function getHealthLabel(score: number): string {
  if (score >= 0.8) return 'Healthy';
  if (score >= 0.6) return 'Degraded';
  if (score >= 0.4) return 'Warning';
  return 'Critical';
}

// =============================================================================
// PrincipleRow Component
// =============================================================================

interface PrincipleRowProps {
  principleScore: PrincipleScore;
  compact: boolean;
  showWeights: boolean;
  isBelowThreshold: boolean;
}

function PrincipleRow({
  principleScore,
  compact,
  showWeights,
  isBelowThreshold,
}: PrincipleRowProps) {
  const [expanded, setExpanded] = useState(false);

  const { principle, score, evidence, weight, weighted_score } = principleScore;
  const percentage = Math.round(score * 100);
  const healthColor = getHealthColor(score);
  const healthLabel = getHealthLabel(score);

  return (
    <div
      className="constitution-scorecard-row"
      data-warning={isBelowThreshold}
      data-compact={compact}
      onClick={() => !compact && evidence && setExpanded(!expanded)}
      role={!compact && evidence ? 'button' : undefined}
      tabIndex={!compact && evidence ? 0 : undefined}
      onKeyDown={(e) => {
        if ((!compact && evidence) && (e.key === 'Enter' || e.key === ' ')) {
          e.preventDefault();
          setExpanded(!expanded);
        }
      }}
    >
      {/* Principle name */}
      <div className="constitution-scorecard-row__name">
        <div className="constitution-scorecard-row__label">
          {PRINCIPLE_LABELS[principle]}
        </div>
        {!compact && (
          <div className="constitution-scorecard-row__description">
            {PRINCIPLE_DESCRIPTIONS[principle]}
          </div>
        )}
      </div>

      {/* Score bar */}
      <div className="constitution-scorecard-row__score-container">
        <div className="constitution-scorecard-row__bar">
          <div
            className="constitution-scorecard-row__bar-fill"
            style={{
              width: `${percentage}%`,
              backgroundColor: healthColor,
            }}
          />
        </div>
        <div className="constitution-scorecard-row__percentage" style={{ color: healthColor }}>
          {percentage}%
        </div>
      </div>

      {/* Health indicator */}
      <div className="constitution-scorecard-row__health" style={{ color: healthColor }}>
        {healthLabel}
      </div>

      {/* Weight */}
      {showWeights && (
        <div className="constitution-scorecard-row__weight">
          w={weight.toFixed(1)}
          {weight !== 1.0 && (
            <span className="constitution-scorecard-row__weighted">
              ({weighted_score.toFixed(2)})
            </span>
          )}
        </div>
      )}

      {/* Evidence (expandable) */}
      {!compact && evidence && expanded && (
        <div className="constitution-scorecard-row__evidence">
          <div className="constitution-scorecard-row__evidence-label">Evidence:</div>
          <div className="constitution-scorecard-row__evidence-text">{evidence}</div>
        </div>
      )}
    </div>
  );
}

// =============================================================================
// Main Component
// =============================================================================

export function ConstitutionScorecard({
  valueScore,
  compact = false,
  showWeights = true,
  warningThreshold = 0.5,
}: ConstitutionScorecardProps) {
  if (!valueScore) {
    return (
      <div className="constitution-scorecard constitution-scorecard--empty">
        <div className="constitution-scorecard__placeholder">No value score</div>
      </div>
    );
  }

  // Sort principles in canonical order
  const principleOrder: Principle[] = [
    'TASTEFUL',
    'CURATED',
    'ETHICAL',
    'JOY_INDUCING',
    'COMPOSABLE',
    'HETERARCHICAL',
    'GENERATIVE',
  ] as Principle[];

  const scoreMap = new Map<Principle, PrincipleScore>();
  valueScore.principle_scores.forEach((ps) => {
    scoreMap.set(ps.principle, ps);
  });

  const sortedScores = principleOrder
    .map((p) => scoreMap.get(p))
    .filter((ps): ps is PrincipleScore => ps !== undefined);

  const violationCount = sortedScores.filter((ps) => ps.score < warningThreshold).length;

  return (
    <div className="constitution-scorecard" data-compact={compact}>
      {/* Header */}
      <div className="constitution-scorecard__header">
        <h3 className="constitution-scorecard__title">Constitution Scorecard</h3>
        <div className="constitution-scorecard__summary">
          <span className="constitution-scorecard__agent">{valueScore.agent_name}</span>
          {violationCount > 0 && (
            <span className="constitution-scorecard__violations">
              {violationCount} violation{violationCount > 1 ? 's' : ''}
            </span>
          )}
        </div>
      </div>

      {/* Overall score */}
      <div className="constitution-scorecard__overall">
        <div className="constitution-scorecard__overall-label">Overall Score</div>
        <div
          className="constitution-scorecard__overall-value"
          style={{ color: getHealthColor(valueScore.total_score) }}
        >
          {Math.round(valueScore.total_score * 100)}%
        </div>
        <div className="constitution-scorecard__overall-min">
          (min: {Math.round(valueScore.min_score * 100)}%)
        </div>
      </div>

      {/* Principle rows */}
      <div className="constitution-scorecard__rows">
        {sortedScores.map((ps) => (
          <PrincipleRow
            key={ps.principle}
            principleScore={ps}
            compact={compact}
            showWeights={showWeights}
            isBelowThreshold={ps.score < warningThreshold}
          />
        ))}
      </div>

      {/* Footer hint */}
      {!compact && (
        <div className="constitution-scorecard__footer">
          Click rows to view evidence
        </div>
      )}
    </div>
  );
}
