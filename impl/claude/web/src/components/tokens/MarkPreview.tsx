/**
 * MarkPreview — Preview of a ChatMark with constitutional scores
 *
 * Shows turn content plus constitutional scores inline.
 * Used when expanding mark: resources in portal tokens.
 *
 * See spec/protocols/portal-resource-system.md §5.2
 */

import { TurnPreview, type TurnContent } from './TurnPreview';
import './tokens.css';

// =============================================================================
// Types
// =============================================================================

export interface ConstitutionalScores {
  tasteful: number;
  curated: number;
  ethical: number;
  joy_inducing: number;
  composable: number;
  heterarchical: number;
  generative: number;
}

export interface MarkContent {
  user_message: string;
  assistant_response: string;
  constitutional_scores: ConstitutionalScores | null;
  tools_used?: string[];
  reasoning?: string;
}

export interface MarkPreviewProps {
  /** Mark content */
  mark: MarkContent;
  /** Turn number (optional) */
  turnNumber?: number;
  /** Show full details vs compact */
  compact?: boolean;
}

// =============================================================================
// Component
// =============================================================================

/**
 * MarkPreview — ChatMark with scores
 */
export function MarkPreview({ mark, turnNumber, compact = false }: MarkPreviewProps) {
  const turnContent: TurnContent = {
    user_message: mark.user_message,
    assistant_response: mark.assistant_response,
  };

  // Calculate weighted average if scores exist
  const weightedScore = mark.constitutional_scores
    ? (
        mark.constitutional_scores.tasteful +
        mark.constitutional_scores.curated +
        mark.constitutional_scores.ethical +
        mark.constitutional_scores.joy_inducing +
        mark.constitutional_scores.composable +
        mark.constitutional_scores.heterarchical +
        mark.constitutional_scores.generative
      ) / 7
    : null;

  return (
    <div className="mark-preview">
      {/* Turn content */}
      <TurnPreview turn={turnContent} turnNumber={turnNumber} compact={compact} />

      {/* Constitutional scores */}
      {mark.constitutional_scores && (
        <div className="mark-preview__scores">
          <div className="mark-preview__scores-header">
            <span className="mark-preview__scores-label">Constitutional Scores</span>
            {weightedScore !== null && (
              <span className="mark-preview__scores-total">
                {(weightedScore * 100).toFixed(0)}%
              </span>
            )}
          </div>

          {!compact && (
            <div className="mark-preview__scores-grid">
              {Object.entries(mark.constitutional_scores).map(([key, value]) => (
                <div key={key} className="mark-preview__score-item">
                  <span className="mark-preview__score-name">
                    {formatPrincipleName(key)}
                  </span>
                  <span className="mark-preview__score-value">
                    {(value * 100).toFixed(0)}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Tools used */}
      {mark.tools_used && mark.tools_used.length > 0 && !compact && (
        <div className="mark-preview__tools">
          <span className="mark-preview__tools-label">Tools:</span>
          <span className="mark-preview__tools-list">
            {mark.tools_used.join(', ')}
          </span>
        </div>
      )}

      {/* Reasoning */}
      {mark.reasoning && !compact && (
        <div className="mark-preview__reasoning">
          <div className="mark-preview__reasoning-label">Reasoning:</div>
          <div className="mark-preview__reasoning-text">{mark.reasoning}</div>
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

export default MarkPreview;
