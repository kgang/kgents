/**
 * NavigationConstitutionalBadge — Constitutional scoring for navigation context
 *
 * Shows the constitutional alignment of recent navigation decisions.
 * Aggregates principle scores from navigation witness marks.
 *
 * "Every navigation is a decision. Decisions should honor principles."
 *
 * @see spec/synthesis/RADICAL_TRANSFORMATION.md
 */

import { memo, useMemo, useState, useCallback } from 'react';
import { useWitness, type DomainMark } from '../hooks/useWitness';
import type { PrincipleScore } from '../types/chat';
import './NavigationConstitutionalBadge.css';

// =============================================================================
// Types
// =============================================================================

export interface NavigationConstitutionalBadgeProps {
  /** Show radar on click */
  expandable?: boolean;

  /** Badge size */
  size?: 'sm' | 'md' | 'lg';

  /** Number of recent marks to aggregate */
  sampleSize?: number;
}

// =============================================================================
// Principle Score Computation
// =============================================================================

/**
 * Principle weights (from constitutional reward system).
 */
const PRINCIPLE_WEIGHTS: Record<keyof PrincipleScore, number> = {
  tasteful: 1.0,
  curated: 1.0,
  ethical: 2.0,        // Safety is paramount
  joy_inducing: 1.2,   // Kent's aesthetic
  composable: 1.5,     // Architecture matters
  heterarchical: 1.0,
  generative: 1.0,
};

/**
 * Maximum weighted total.
 */
const MAX_WEIGHTED_TOTAL = Object.values(PRINCIPLE_WEIGHTS).reduce((a, b) => a + b, 0);

/**
 * Aggregate principle scores from navigation marks.
 */
function aggregateScores(marks: DomainMark[]): PrincipleScore {
  const counts: Record<keyof PrincipleScore, number> = {
    tasteful: 0,
    curated: 0,
    ethical: 0,
    joy_inducing: 0,
    composable: 0,
    heterarchical: 0,
    generative: 0,
  };

  // Count principle mentions
  for (const mark of marks) {
    for (const principle of mark.principles || []) {
      const key = normalizePrincipleKey(principle);
      if (key && key in counts) {
        counts[key as keyof PrincipleScore] += 1;
      }
    }
  }

  // Normalize to 0-1 (max is mark count)
  const maxCount = Math.max(marks.length, 1);
  const scores: PrincipleScore = {
    tasteful: Math.min(1, counts.tasteful / maxCount),
    curated: Math.min(1, counts.curated / maxCount),
    ethical: Math.min(1, counts.ethical / maxCount),
    joy_inducing: Math.min(1, counts.joy_inducing / maxCount),
    composable: Math.min(1, counts.composable / maxCount),
    heterarchical: Math.min(1, counts.heterarchical / maxCount),
    generative: Math.min(1, counts.generative / maxCount),
  };

  return scores;
}

/**
 * Normalize principle name to PrincipleScore key.
 */
function normalizePrincipleKey(principle: string): keyof PrincipleScore | null {
  const normalized = principle.toLowerCase();
  const mapping: Record<string, keyof PrincipleScore> = {
    tasteful: 'tasteful',
    curated: 'curated',
    ethical: 'ethical',
    joy_inducing: 'joy_inducing',
    joyinducing: 'joy_inducing',
    'joy-inducing': 'joy_inducing',
    composable: 'composable',
    heterarchical: 'heterarchical',
    generative: 'generative',
  };
  return mapping[normalized] ?? null;
}

/**
 * Compute weighted total score.
 */
function computeWeightedTotal(scores: PrincipleScore): number {
  let total = 0;
  for (const [key, weight] of Object.entries(PRINCIPLE_WEIGHTS)) {
    total += scores[key as keyof PrincipleScore] * weight;
  }
  return total;
}

/**
 * Get health level from score.
 */
function getHealthLevel(score: number): 'high' | 'medium' | 'low' {
  if (score >= 0.8) return 'high';
  if (score >= 0.5) return 'medium';
  return 'low';
}

// =============================================================================
// Component
// =============================================================================

export const NavigationConstitutionalBadge = memo(function NavigationConstitutionalBadge({
  expandable = true,
  size = 'md',
  sampleSize = 20,
}: NavigationConstitutionalBadgeProps) {
  const [expanded, setExpanded] = useState(false);

  // Get recent navigation marks
  const { recentMarks, pendingCount } = useWitness({
    filterDomain: 'navigation',
    maxRecent: sampleSize,
  });

  // Compute aggregate scores
  const scores = useMemo(() => aggregateScores(recentMarks), [recentMarks]);

  // Compute overall score (normalized 0-100)
  const overallScore = useMemo(() => {
    const weighted = computeWeightedTotal(scores);
    return Math.round((weighted / MAX_WEIGHTED_TOTAL) * 100);
  }, [scores]);

  // Determine health level
  const healthLevel = getHealthLevel(overallScore / 100);

  // Handle click
  const handleClick = useCallback(() => {
    if (expandable) {
      setExpanded((e) => !e);
    }
  }, [expandable]);

  return (
    <div className={`nav-constitutional-badge nav-constitutional-badge--${size}`}>
      <button
        className={`nav-constitutional-badge__button nav-constitutional-badge__button--${healthLevel}`}
        onClick={handleClick}
        title={`Constitutional alignment: ${overallScore}%`}
        aria-expanded={expanded}
      >
        <span className="nav-constitutional-badge__icon">
          {healthLevel === 'high' ? '●' : healthLevel === 'medium' ? '◐' : '○'}
        </span>
        <span className="nav-constitutional-badge__score">{overallScore}</span>
        {pendingCount > 0 && (
          <span className="nav-constitutional-badge__pending" title="Marks pending">
            +{pendingCount}
          </span>
        )}
      </button>

      {expanded && (
        <div className="nav-constitutional-badge__radar">
          <div className="nav-constitutional-badge__radar-content">
            <h4 className="nav-constitutional-badge__radar-title">Navigation Alignment</h4>
            <div className="nav-constitutional-badge__principles">
              {(Object.entries(scores) as [keyof PrincipleScore, number][]).map(
                ([key, value]) => (
                  <div key={key} className="nav-constitutional-badge__principle">
                    <span className="nav-constitutional-badge__principle-name">
                      {formatPrincipleName(key)}
                    </span>
                    <div className="nav-constitutional-badge__principle-bar">
                      <div
                        className="nav-constitutional-badge__principle-fill"
                        style={{
                          width: `${value * 100}%`,
                          backgroundColor: getPrincipleColor(key),
                        }}
                      />
                    </div>
                    <span className="nav-constitutional-badge__principle-value">
                      {Math.round(value * 100)}
                    </span>
                  </div>
                )
              )}
            </div>
            <div className="nav-constitutional-badge__meta">
              <span>Based on {recentMarks.length} recent navigations</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
});

// =============================================================================
// Helpers
// =============================================================================

function formatPrincipleName(key: keyof PrincipleScore): string {
  const names: Record<keyof PrincipleScore, string> = {
    tasteful: 'Tasteful',
    curated: 'Curated',
    ethical: 'Ethical',
    joy_inducing: 'Joy-Inducing',
    composable: 'Composable',
    heterarchical: 'Heterarchical',
    generative: 'Generative',
  };
  return names[key];
}

function getPrincipleColor(key: keyof PrincipleScore): string {
  const colors: Record<keyof PrincipleScore, string> = {
    tasteful: '#8ba98b',      // glow-lichen
    curated: '#c4a77d',       // glow-spore
    ethical: '#4a6b4a',       // life-sage
    joy_inducing: '#d4b88c',  // glow-amber
    composable: '#6b8b6b',    // life-mint
    heterarchical: '#8bab8b', // life-sprout
    generative: '#e5c99d',    // glow-light
  };
  return colors[key];
}

// =============================================================================
// Export
// =============================================================================

export default NavigationConstitutionalBadge;
