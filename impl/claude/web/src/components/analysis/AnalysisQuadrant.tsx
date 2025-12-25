/**
 * AnalysisQuadrant — Four-panel analysis visualization
 *
 * "Analysis is not one thing but four: verification of laws, grounding of claims,
 *  resolution of tensions, and regeneration from axioms."
 *
 * Displays all four modes of the Analysis Operad simultaneously in a 2x2 grid:
 *
 * ┌─────────────────┬─────────────────┐
 * │  CATEGORICAL    │  EPISTEMIC      │
 * │  Laws Hold? ✓   │  Grounded? ✓    │
 * ├─────────────────┼─────────────────┤
 * │  DIALECTICAL    │  GENERATIVE     │
 * │  Tensions: 2    │  Regenerable? ✓ │
 * └─────────────────┴─────────────────┘
 */

import { memo } from 'react';
import {
  useAnalysis,
  type CategoricalReport,
  type EpistemicReport,
  type DialecticalReport,
  type GenerativeReport,
} from './useAnalysis';
import CategoricalPanel from './CategoricalPanel';
import EpistemicPanel from './EpistemicPanel';
import DialecticalPanel from './DialecticalPanel';
import GenerativePanel from './GenerativePanel';
import './AnalysisQuadrant.css';

// =============================================================================
// Types
// =============================================================================

interface AnalysisQuadrantProps {
  /** Node ID to analyze */
  nodeId: string;

  /** Close handler */
  onClose?: () => void;

  /** Additional CSS class */
  className?: string;
}

// =============================================================================
// Component
// =============================================================================

export const AnalysisQuadrant = memo(function AnalysisQuadrant({
  nodeId,
  onClose,
  className = '',
}: AnalysisQuadrantProps) {
  const { categorical, epistemic, dialectical, generative, loading, error } =
    useAnalysis(nodeId);

  if (error) {
    return (
      <div className={`analysis-quadrant analysis-quadrant--error ${className}`}>
        <div className="analysis-quadrant__header">
          <h2 className="analysis-quadrant__title">Analysis</h2>
          {onClose && (
            <button
              className="analysis-quadrant__close"
              onClick={onClose}
              aria-label="Close"
            >
              ✕
            </button>
          )}
        </div>
        <div className="analysis-quadrant__error">
          <span className="analysis-quadrant__error-icon">△</span>
          <span className="analysis-quadrant__error-message">
            Failed to load analysis: {error.message}
          </span>
        </div>
      </div>
    );
  }

  return (
    <div className={`analysis-quadrant ${className}`}>
      {/* Header */}
      <div className="analysis-quadrant__header">
        <h2 className="analysis-quadrant__title">
          Analysis <span className="analysis-quadrant__node-id">{nodeId}</span>
        </h2>
        {onClose && (
          <button className="analysis-quadrant__close" onClick={onClose} aria-label="Close">
            ✕
          </button>
        )}
      </div>

      {/* 2x2 Grid */}
      <div className="analysis-quadrant__grid">
        {/* Top Left: Categorical */}
        <CategoricalPanel report={categorical} loading={loading} />

        {/* Top Right: Epistemic */}
        <EpistemicPanel report={epistemic} loading={loading} />

        {/* Bottom Left: Dialectical */}
        <DialecticalPanel report={dialectical} loading={loading} />

        {/* Bottom Right: Generative */}
        <GenerativePanel report={generative} loading={loading} />
      </div>

      {/* Overall Status */}
      {!loading && categorical && epistemic && dialectical && generative && (
        <div className="analysis-quadrant__footer">
          {isValid(categorical, epistemic, dialectical, generative) ? (
            <div className="analysis-status analysis-status--valid">
              <span className="analysis-status__icon">✓</span>
              <span className="analysis-status__text">All modes passed</span>
            </div>
          ) : (
            <div className="analysis-status analysis-status--invalid">
              <span className="analysis-status__icon">✗</span>
              <span className="analysis-status__text">Some modes failed</span>
            </div>
          )}
        </div>
      )}
    </div>
  );
});

// =============================================================================
// Helpers
// =============================================================================

function isValid(
  categorical: CategoricalReport,
  epistemic: EpistemicReport,
  dialectical: DialecticalReport,
  generative: GenerativeReport
): boolean {
  const categoricalValid =
    !categorical.law_verifications.some((v) => v.status === 'FAILED');
  const epistemicValid = epistemic.grounding.terminates_at_axiom;
  const dialecticalValid =
    dialectical.tensions.filter((t) => t.classification === 'PROBLEMATIC').length === 0;
  const generativeValid = generative.regeneration.passed;

  return categoricalValid && epistemicValid && dialecticalValid && generativeValid;
}

export default AnalysisQuadrant;
