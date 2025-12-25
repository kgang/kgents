/**
 * ASHCEvidence — Display ASHC compilation evidence in chat
 *
 * Shows:
 * - Equivalence score as progress bar
 * - Runs completed/passed/total
 * - Bayesian confidence
 * - Stopping state (CONTINUE | STOP_SUCCESS | STOP_FAILURE)
 *
 * Brutalist styling — no decoration, just data.
 */

import { memo } from 'react';
import './ASHCEvidence.css';

// =============================================================================
// Types
// =============================================================================

export interface ASHCEvidenceData {
  equivalence_score: number;  // 0.0-1.0
  is_verified: boolean;
  runs_completed: number;
  runs_passed: number;
  runs_total: number;
  pass_rate: number;  // 0.0-1.0
  confidence: number;  // 0.0-1.0 (Bayesian posterior mean)
  prior_alpha: number;
  prior_beta: number;
  stopping_decision: 'continue' | 'stop_success' | 'stop_failure' | 'stop_uncertain';
  chaos_stability: number | null;
}

export interface ASHCEvidenceProps {
  data: ASHCEvidenceData;
}

// =============================================================================
// Helper Functions
// =============================================================================

function formatPercent(value: number): string {
  return `${(value * 100).toFixed(0)}%`;
}

function getStoppingLabel(decision: string): string {
  switch (decision) {
    case 'stop_success':
      return 'VERIFIED';
    case 'stop_failure':
      return 'FAILED';
    case 'stop_uncertain':
      return 'UNCERTAIN';
    default:
      return 'CONTINUE';
  }
}

function getStoppingClass(decision: string): string {
  switch (decision) {
    case 'stop_success':
      return 'ashc-evidence__stopping--success';
    case 'stop_failure':
      return 'ashc-evidence__stopping--failure';
    case 'stop_uncertain':
      return 'ashc-evidence__stopping--uncertain';
    default:
      return 'ashc-evidence__stopping--continue';
  }
}

// =============================================================================
// Main Component
// =============================================================================

/**
 * ASHCEvidence — Brutalist evidence display
 */
export const ASHCEvidence = memo(function ASHCEvidence({ data }: ASHCEvidenceProps) {
  const {
    equivalence_score,
    is_verified,
    runs_completed,
    runs_passed,
    runs_total,
    pass_rate,
    confidence,
    stopping_decision,
    chaos_stability,
  } = data;

  return (
    <div className="ashc-evidence">
      {/* Header */}
      <div className="ashc-evidence__header">
        <span className="ashc-evidence__title">ASHC Evidence</span>
        <span className={`ashc-evidence__stopping ${getStoppingClass(stopping_decision)}`}>
          {getStoppingLabel(stopping_decision)}
        </span>
      </div>

      {/* Equivalence Score */}
      <div className="ashc-evidence__metric">
        <div className="ashc-evidence__metric-label">
          Equivalence Score
        </div>
        <div className="ashc-evidence__metric-value">
          {formatPercent(equivalence_score)}
          {is_verified && <span className="ashc-evidence__verified"> ●</span>}
        </div>
        <div className="ashc-evidence__progress-bar">
          <div
            className="ashc-evidence__progress-fill"
            style={{ width: formatPercent(equivalence_score) }}
          />
        </div>
      </div>

      {/* Runs Summary */}
      <div className="ashc-evidence__metric">
        <div className="ashc-evidence__metric-label">
          Runs
        </div>
        <div className="ashc-evidence__metric-value">
          {runs_passed}/{runs_completed} passed ({formatPercent(pass_rate)})
        </div>
        <div className="ashc-evidence__runs-detail">
          {runs_completed < runs_total && (
            <span className="ashc-evidence__runs-remaining">
              Stopped early: {runs_total - runs_completed} runs saved
            </span>
          )}
        </div>
      </div>

      {/* Bayesian Confidence */}
      <div className="ashc-evidence__metric">
        <div className="ashc-evidence__metric-label">
          Confidence (Bayesian)
        </div>
        <div className="ashc-evidence__metric-value">
          {formatPercent(confidence)}
        </div>
      </div>

      {/* Chaos Stability (if available) */}
      {chaos_stability !== null && (
        <div className="ashc-evidence__metric">
          <div className="ashc-evidence__metric-label">
            Chaos Stability
          </div>
          <div className="ashc-evidence__metric-value">
            {formatPercent(chaos_stability)}
          </div>
        </div>
      )}

      {/* Interpretation */}
      <div className="ashc-evidence__interpretation">
        {is_verified ? (
          <p>
            High confidence in spec↔impl equivalence. This edit has been empirically verified
            across {runs_completed} runs with {formatPercent(pass_rate)} pass rate.
          </p>
        ) : stopping_decision === 'stop_failure' ? (
          <p>
            Low confidence. Multiple verification runs failed. Consider revising the spec or
            implementation.
          </p>
        ) : stopping_decision === 'stop_uncertain' ? (
          <p>
            Uncertain outcome after {runs_completed} runs. May need manual review or
            additional testing.
          </p>
        ) : (
          <p>
            Evidence accumulating. {runs_completed}/{runs_total} runs completed so far.
          </p>
        )}
      </div>
    </div>
  );
});

export default ASHCEvidence;
