/**
 * ConfidenceIndicator — Per-response confidence display
 *
 * From spec/protocols/chat-web.md Part X.3:
 * - 🟢 High (P > 0.80): Green
 * - 🟡 Medium (0.50-0.80): Yellow
 * - 🔴 Low (< 0.50): Red
 * - Shows Bayesian calculation: P(success) from prior
 */

import { ChatEvidence } from './store';
import type { EvidenceDelta } from './store';
import './ConfidenceIndicator.css';

// =============================================================================
// Types
// =============================================================================

export interface ConfidenceIndicatorProps {
  /** Confidence value (0-1) */
  confidence: number;
  /** Evidence delta for this turn (optional) */
  evidenceDelta?: EvidenceDelta;
  /** Full evidence object (optional, for detailed view) */
  evidence?: ChatEvidence;
  /** Show detailed breakdown */
  showDetails?: boolean;
  /** Size variant */
  size?: 'sm' | 'md' | 'lg';
  /** Streaming indicator */
  isStreaming?: boolean;
}

// =============================================================================
// Component
// =============================================================================

export function ConfidenceIndicator({
  confidence,
  evidenceDelta,
  evidence,
  showDetails = false,
  size = 'md',
  isStreaming = false,
}: ConfidenceIndicatorProps) {
  // Don't show during streaming
  if (isStreaming || confidence === 0) {
    return null;
  }

  // Determine confidence level
  const level =
    confidence > 0.8 ? 'high' : confidence >= 0.5 ? 'medium' : 'low';

  // Icon and color
  const icon = level === 'high' ? '●' : level === 'medium' ? '◐' : '◯';
  const label = level === 'high' ? 'High' : level === 'medium' ? 'Medium' : 'Low';

  // Bayesian calculation explanation (if full evidence available)
  const totalTrials = evidence
    ? evidence.prior_alpha + evidence.prior_beta
    : 0;
  const successRate =
    totalTrials > 0 && evidence
      ? ((evidence.prior_alpha / totalTrials) * 100).toFixed(0)
      : 'N/A';

  return (
    <div
      className={`confidence-indicator confidence-indicator--${level} confidence-indicator--${size}`}
      role="status"
      aria-label={`Confidence: ${label} (${(confidence * 100).toFixed(0)}%)`}
    >
      {/* Main badge */}
      <div className="confidence-indicator__badge">
        <span className="confidence-indicator__icon" aria-hidden="true">
          {icon}
        </span>
        <span className="confidence-indicator__label">{label} Confidence</span>
        <span className="confidence-indicator__value">
          (P={confidence.toFixed(2)})
        </span>
      </div>

      {/* Detailed breakdown */}
      {showDetails && evidence && (
        <div className="confidence-indicator__details">
          <div className="confidence-indicator__detail-row">
            <span className="confidence-indicator__detail-label">Bayesian:</span>
            <span className="confidence-indicator__detail-value">
              {evidence.prior_alpha} successes, {evidence.prior_beta} failures
            </span>
          </div>
          <div className="confidence-indicator__detail-row">
            <span className="confidence-indicator__detail-label">Success Rate:</span>
            <span className="confidence-indicator__detail-value">{successRate}%</span>
          </div>
          {evidence.ashc_equivalence !== undefined && (
            <div className="confidence-indicator__detail-row">
              <span className="confidence-indicator__detail-label">ASHC:</span>
              <span className="confidence-indicator__detail-value">
                {(evidence.ashc_equivalence * 100).toFixed(0)}% equivalence
              </span>
            </div>
          )}
          {evidence.should_stop && (
            <div className="confidence-indicator__stop-suggestion">
              ⊢ Goal appears achieved (stopping criterion met)
            </div>
          )}
        </div>
      )}
      {showDetails && !evidence && evidenceDelta && (
        <div className="confidence-indicator__details">
          <div className="confidence-indicator__detail-row">
            <span className="confidence-indicator__detail-label">Tools Executed:</span>
            <span className="confidence-indicator__detail-value">{evidenceDelta.tools_executed}</span>
          </div>
          <div className="confidence-indicator__detail-row">
            <span className="confidence-indicator__detail-label">Tools Succeeded:</span>
            <span className="confidence-indicator__detail-value">{evidenceDelta.tools_succeeded}</span>
          </div>
          <div className="confidence-indicator__detail-row">
            <span className="confidence-indicator__detail-label">Confidence Change:</span>
            <span className="confidence-indicator__detail-value">
              {evidenceDelta.confidence_change > 0 ? '+' : ''}{(evidenceDelta.confidence_change * 100).toFixed(1)}%
            </span>
          </div>
        </div>
      )}
    </div>
  );
}

export default ConfidenceIndicator;
