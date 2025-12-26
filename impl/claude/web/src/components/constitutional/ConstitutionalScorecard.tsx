/**
 * ConstitutionalScorecard — Table showing per-principle scores
 *
 * Displays all 7 principles with:
 * - Score bar (0-100%)
 * - Health indicator (color-coded)
 * - Trust capital contribution
 *
 * Stark table layout. No decoration, pure information.
 */

import type { ConstitutionalAlignment, ConstitutionalTrustResult, Principle } from './types';
import { PRINCIPLE_LABELS, PRINCIPLE_DESCRIPTIONS } from './types';
import './ConstitutionalScorecard.css';

// =============================================================================
// Types
// =============================================================================

export interface ConstitutionalScorecardProps {
  /** Alignment scores */
  alignment: ConstitutionalAlignment | null;
  /** Trust result (optional) */
  trust?: ConstitutionalTrustResult | null;
  /** Compact mode (hide descriptions) */
  compact?: boolean;
  /** Warning threshold (default 0.5) */
  warningThreshold?: number;
}

// =============================================================================
// Helpers — STARK BIOME Edition
// =============================================================================

/**
 * STARK BIOME: Health color mapping
 * Good (>0.8): life-sage (#4A6B4A) - healthy green
 * Degraded (0.6-0.8): glow-spore (#C4A77D) - earned gold
 * Warning (0.4-0.6): accent-error (#A65D4A) - muted rust
 * Critical (<0.4): accent-error darker - sympathetic, not alarming
 */
function getHealthColor(score: number): string {
  if (score >= 0.8) return 'var(--color-life-sage)';
  if (score >= 0.6) return 'var(--color-glow-spore)';
  if (score >= 0.4) return 'var(--accent-error)';
  return 'var(--accent-error)';
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
  principle: Principle;
  score: number;
  avgScore?: number;
  compact: boolean;
  isBelowThreshold: boolean;
}

function PrincipleRow({
  principle,
  score,
  avgScore,
  compact,
  isBelowThreshold,
}: PrincipleRowProps) {
  const percentage = Math.round(score * 100);
  const healthColor = getHealthColor(score);
  const healthLabel = getHealthLabel(score);

  return (
    <div
      className="constitutional-scorecard-row"
      data-warning={isBelowThreshold}
      data-compact={compact}
    >
      {/* Principle name */}
      <div className="constitutional-scorecard-row__name">
        <div className="constitutional-scorecard-row__label">
          {PRINCIPLE_LABELS[principle]}
        </div>
        {!compact && (
          <div className="constitutional-scorecard-row__description">
            {PRINCIPLE_DESCRIPTIONS[principle]}
          </div>
        )}
      </div>

      {/* Score bar */}
      <div className="constitutional-scorecard-row__score-container">
        <div className="constitutional-scorecard-row__bar">
          <div
            className="constitutional-scorecard-row__bar-fill"
            style={{
              width: `${percentage}%`,
              backgroundColor: healthColor,
            }}
          />
        </div>
        <div className="constitutional-scorecard-row__percentage" style={{ color: healthColor }}>
          {percentage}%
        </div>
      </div>

      {/* Health indicator */}
      <div className="constitutional-scorecard-row__health" style={{ color: healthColor }}>
        {healthLabel}
      </div>

      {/* Average (if trust data available) */}
      {avgScore !== undefined && (
        <div className="constitutional-scorecard-row__average">
          Avg: {Math.round(avgScore * 100)}%
        </div>
      )}
    </div>
  );
}

// =============================================================================
// Main Component
// =============================================================================

export function ConstitutionalScorecard({
  alignment,
  trust,
  compact = false,
  warningThreshold = 0.5,
}: ConstitutionalScorecardProps) {
  if (!alignment) {
    return (
      <div className="constitutional-scorecard constitutional-scorecard--empty">
        <div className="constitutional-scorecard__placeholder">No alignment data</div>
      </div>
    );
  }

  // Canonical principle order
  const principleOrder: Principle[] = Object.values({
    TASTEFUL: 'TASTEFUL',
    CURATED: 'CURATED',
    ETHICAL: 'ETHICAL',
    JOY_INDUCING: 'JOY_INDUCING',
    COMPOSABLE: 'COMPOSABLE',
    HETERARCHICAL: 'HETERARCHICAL',
    GENERATIVE: 'GENERATIVE',
  }) as Principle[];

  const violationCount = alignment.violation_count;

  return (
    <div className="constitutional-scorecard" data-compact={compact}>
      {/* Header */}
      <div className="constitutional-scorecard__header">
        <h3 className="constitutional-scorecard__title">Constitutional Scorecard</h3>
        {violationCount > 0 && (
          <span className="constitutional-scorecard__violations">
            {violationCount} violation{violationCount > 1 ? 's' : ''}
          </span>
        )}
      </div>

      {/* Overall score */}
      <div className="constitutional-scorecard__overall">
        <div className="constitutional-scorecard__overall-label">Overall Score</div>
        <div
          className="constitutional-scorecard__overall-value"
          style={{ color: getHealthColor(alignment.weighted_total) }}
        >
          {Math.round(alignment.weighted_total * 100)}%
        </div>
        <div className="constitutional-scorecard__overall-tier">
          Tier: {alignment.tier}
        </div>
      </div>

      {/* Principle rows */}
      <div className="constitutional-scorecard__rows">
        {principleOrder.map((principle) => {
          const score = alignment.principle_scores[principle] || 0;
          const avgScore = trust?.principle_averages[principle];
          return (
            <PrincipleRow
              key={principle}
              principle={principle}
              score={score}
              avgScore={avgScore}
              compact={compact}
              isBelowThreshold={score < warningThreshold}
            />
          );
        })}
      </div>

      {/* Dominant/Weakest principles */}
      {!compact && (
        <div className="constitutional-scorecard__insights">
          <div className="constitutional-scorecard__insight">
            <span className="constitutional-scorecard__insight-label">Dominant:</span>
            <span className="constitutional-scorecard__insight-value">
              {PRINCIPLE_LABELS[alignment.dominant_principle as Principle]}
            </span>
          </div>
          <div className="constitutional-scorecard__insight">
            <span className="constitutional-scorecard__insight-label">Weakest:</span>
            <span className="constitutional-scorecard__insight-value">
              {PRINCIPLE_LABELS[alignment.weakest_principle as Principle]}
            </span>
          </div>
        </div>
      )}
    </div>
  );
}
