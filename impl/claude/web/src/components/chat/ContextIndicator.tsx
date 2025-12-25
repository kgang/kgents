/**
 * ContextIndicator — Real-time context display for chat sessions
 *
 * From spec/protocols/chat-web.md Part X.3:
 * - Progress bar (visual fill with gradient)
 * - Percentage (numeric)
 * - Token count (absolute: used/total)
 * - Estimated cost (USD based on Claude pricing)
 * - Compression status indicator (Active/Idle/Warning)
 * - Evidence confidence from ChatEvidence (Bayesian posterior)
 * - Click to expand for detailed breakdown
 */

import { useState } from 'react';
import { lossToHue } from '../../hooks/useLoss';
import { ChatSession, ChatEvidence } from './store';
import './ContextIndicator.css';

// =============================================================================
// Types
// =============================================================================

export interface ContextIndicatorProps {
  /** Chat session to display metrics for */
  session: ChatSession;
  /** Compact mode (hide some details) */
  compact?: boolean;
}

export type { ChatEvidence };

// =============================================================================
// Constants
// =============================================================================

/** Claude Opus 4.5 pricing (per 1M tokens) */
const PRICING = {
  input: 15.0,   // $15 per 1M input tokens
  output: 75.0,  // $75 per 1M output tokens
} as const;

/** Context window size for Claude Opus 4.5 */
const CONTEXT_WINDOW = 200_000;

/** Compression thresholds */
const COMPRESS_AT = 0.80;  // Start compression at 80%
const WARNING_AT = 0.95;   // Warning at 95%

// =============================================================================
// Helper Functions
// =============================================================================

function deriveMetrics(session: ChatSession) {
  const tokensUsed = session.context_size;
  const tokensTotal = CONTEXT_WINDOW;
  const percentage = tokensUsed / tokensTotal;

  // Determine compression status
  let compression: 'idle' | 'active' | 'warning';
  if (percentage >= WARNING_AT) {
    compression = 'warning';
  } else if (percentage >= COMPRESS_AT) {
    compression = 'active';
  } else {
    compression = 'idle';
  }

  // Estimate cost (simplified - assumes 50/50 input/output split)
  const inputTokens = tokensUsed * 0.5;
  const outputTokens = tokensUsed * 0.5;
  const estimatedCost =
    (inputTokens / 1_000_000) * PRICING.input +
    (outputTokens / 1_000_000) * PRICING.output;

  return {
    tokensUsed,
    tokensTotal,
    percentage,
    compression,
    estimatedCost,
    turnCount: session.turns?.length ?? 0,
    evidence: session.evidence,
  };
}

// =============================================================================
// Component
// =============================================================================

export function ContextIndicator({
  session,
  compact = false,
}: ContextIndicatorProps) {
  const [expanded, setExpanded] = useState(false);
  const [isHovered, setIsHovered] = useState(false);

  const metrics = deriveMetrics(session);
  const percentage = metrics.percentage * 100;
  const isNearLimit = metrics.percentage >= COMPRESS_AT;
  const isCritical = metrics.percentage >= WARNING_AT;

  // Use viridis gradient based on context fill
  const fillHue = lossToHue(metrics.percentage);

  // Format numbers
  const tokensUsedK = (metrics.tokensUsed / 1000).toFixed(0);
  const tokensTotalK = (metrics.tokensTotal / 1000).toFixed(0);
  const costFormatted = `$${metrics.estimatedCost.toFixed(2)}`;

  // Confidence display
  const evidence = metrics.evidence;
  const hasEvidence = evidence && evidence.confidence > 0;
  const confidenceLevel = hasEvidence
    ? evidence.confidence > 0.8
      ? 'high'
      : evidence.confidence > 0.5
        ? 'medium'
        : 'low'
    : null;

  const confidenceIcon = confidenceLevel === 'high' ? '●' : confidenceLevel === 'medium' ? '◐' : '◯';

  const handleClick = () => {
    if (!compact) {
      setExpanded(!expanded);
    }
  };

  // Don't show if compact mode
  if (compact) {
    return null;
  }

  return (
    <div
      className={`context-indicator ${expanded ? 'context-indicator--expanded' : ''} context-indicator--clickable`}
      onClick={handleClick}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      style={{ '--fill-hue': fillHue } as React.CSSProperties}
      role="button"
      tabIndex={0}
      aria-label={`Context: ${percentage.toFixed(0)}% used (${tokensUsedK}k of ${tokensTotalK}k tokens), Cost: ${costFormatted}`}
    >
      {/* Main display */}
      <div className="context-indicator__main">
        {/* Progress bar */}
        <div className="context-indicator__bar-container">
          <div className="context-indicator__label">Context:</div>
          <div className="context-indicator__bar">
            <div
              className={`context-indicator__fill ${isNearLimit ? 'context-indicator__fill--warning' : ''} ${isCritical ? 'context-indicator__fill--critical' : ''}`}
              style={{ width: `${percentage}%` }}
            />
          </div>
          <div className="context-indicator__percentage">
            {percentage.toFixed(0)}%
          </div>
          <div className="context-indicator__tokens">
            ({tokensUsedK}k/{tokensTotalK}k)
          </div>
        </div>

        {/* Metadata row */}
        <div className="context-indicator__metadata">
          <div className="context-indicator__cost">
            Cost: {costFormatted}
          </div>
          <div className="context-indicator__separator">|</div>
          <div className="context-indicator__turns">
            Turns: {metrics.turnCount}
          </div>
          <div className="context-indicator__separator">|</div>
          <div
            className={`context-indicator__compression context-indicator__compression--${metrics.compression}`}
          >
            Compression: {metrics.compression.charAt(0).toUpperCase() + metrics.compression.slice(1)}
          </div>
        </div>

        {/* Evidence row (if available) */}
        {hasEvidence && evidence && (
          <div className="context-indicator__evidence">
            <div className="context-indicator__evidence-label">
              Evidence: {confidenceIcon} {confidenceLevel === 'high' ? 'High' : confidenceLevel === 'medium' ? 'Medium' : 'Low'}
            </div>
            <div className="context-indicator__confidence">
              (P={evidence.confidence.toFixed(2)})
            </div>
            {evidence.ashc_equivalence !== undefined && (
              <div className="context-indicator__ashc">
                ASHC: {(evidence.ashc_equivalence * 100).toFixed(0)}% equivalence
              </div>
            )}
          </div>
        )}
      </div>

      {/* Expanded details */}
      {expanded && (
        <div className="context-indicator__details">
          <div className="context-indicator__detail-section">
            <h4 className="context-indicator__detail-title">Token Breakdown</h4>
            <div className="context-indicator__detail-row">
              <span>Used:</span>
              <span>{metrics.tokensUsed.toLocaleString()} tokens</span>
            </div>
            <div className="context-indicator__detail-row">
              <span>Available:</span>
              <span>{(metrics.tokensTotal - metrics.tokensUsed).toLocaleString()} tokens</span>
            </div>
            <div className="context-indicator__detail-row">
              <span>Total:</span>
              <span>{metrics.tokensTotal.toLocaleString()} tokens</span>
            </div>
          </div>

          {evidence && (
            <div className="context-indicator__detail-section">
              <h4 className="context-indicator__detail-title">Evidence</h4>
              <div className="context-indicator__detail-row">
                <span>Confidence:</span>
                <span>{(evidence.confidence * 100).toFixed(1)}%</span>
              </div>
              <div className="context-indicator__detail-row">
                <span>Bayesian Prior:</span>
                <span>α={evidence.prior_alpha}, β={evidence.prior_beta}</span>
              </div>
              <div className="context-indicator__detail-row">
                <span>Tools Succeeded:</span>
                <span>{evidence.tools_succeeded}</span>
              </div>
              <div className="context-indicator__detail-row">
                <span>Tools Failed:</span>
                <span>{evidence.tools_failed}</span>
              </div>
              {evidence.ashc_equivalence !== undefined && (
                <div className="context-indicator__detail-row">
                  <span>ASHC Equivalence:</span>
                  <span>{(evidence.ashc_equivalence * 100).toFixed(1)}%</span>
                </div>
              )}
            </div>
          )}

          <div className="context-indicator__detail-section">
            <h4 className="context-indicator__detail-title">Cost Breakdown</h4>
            <div className="context-indicator__detail-row">
              <span>Estimated Total:</span>
              <span>{costFormatted}</span>
            </div>
            <div className="context-indicator__detail-note">
              Based on Claude Opus 4.5 pricing: ${PRICING.input}/1M input, ${PRICING.output}/1M output
            </div>
          </div>
        </div>
      )}

      {/* Expand hint */}
      {!expanded && !compact && isHovered && (
        <div className="context-indicator__hint">
          Click to expand
        </div>
      )}
    </div>
  );
}

export default ContextIndicator;
