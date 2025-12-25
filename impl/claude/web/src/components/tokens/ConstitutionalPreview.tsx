/**
 * ConstitutionalPreview — Preview of constitutional scores
 *
 * Shows mini radar or score summary.
 * Used when expanding constitutional: resources in portal tokens.
 *
 * See spec/protocols/portal-resource-system.md §5.3
 */

import { ConstitutionalRadar } from '../chat/ConstitutionalRadar';
import type { PrincipleScore } from '../../types/chat';
import './tokens.css';

// =============================================================================
// Types
// =============================================================================

export interface ConstitutionalContent {
  scores: PrincipleScore | null;
  radar_data?: Array<{ axis: string; value: number }>;
}

export interface ConstitutionalPreviewProps {
  /** Constitutional data */
  data: ConstitutionalContent;
  /** Show full radar vs compact summary */
  compact?: boolean;
}

// =============================================================================
// Component
// =============================================================================

/**
 * ConstitutionalPreview — Scores with optional radar
 */
export function ConstitutionalPreview({
  data,
  compact = false,
}: ConstitutionalPreviewProps) {
  if (!data.scores) {
    return (
      <div className="constitutional-preview">
        <div className="constitutional-preview__empty">No scores available</div>
      </div>
    );
  }

  // Calculate weighted average
  const weightedScore =
    (data.scores.tasteful +
      data.scores.curated +
      data.scores.ethical +
      data.scores.joy_inducing +
      data.scores.composable +
      data.scores.heterarchical +
      data.scores.generative) /
    7;

  return (
    <div className="constitutional-preview">
      {/* Overall score */}
      <div className="constitutional-preview__header">
        <span className="constitutional-preview__label">Overall Score</span>
        <span className="constitutional-preview__total">
          {(weightedScore * 100).toFixed(0)}%
        </span>
      </div>

      {/* Compact mode: score grid */}
      {compact ? (
        <div className="constitutional-preview__scores-compact">
          {Object.entries(data.scores).map(([key, value]) => (
            <div key={key} className="constitutional-preview__score-item">
              <span className="constitutional-preview__score-name">
                {formatPrincipleName(key)}
              </span>
              <span className="constitutional-preview__score-value">
                {(value * 100).toFixed(0)}
              </span>
            </div>
          ))}
        </div>
      ) : (
        /* Full mode: radar chart */
        <div className="constitutional-preview__radar">
          <ConstitutionalRadar scores={data.scores} size="sm" showLabels={true} />
        </div>
      )}
    </div>
  );
}

// =============================================================================
// Helpers
// =============================================================================

/**
 * Format principle name from snake_case to Title Case
 */
function formatPrincipleName(name: string): string {
  return name
    .split('_')
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
}

export default ConstitutionalPreview;
