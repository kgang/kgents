/**
 * EpistemicPanel — Visualize epistemic analysis (grounding & justification)
 *
 * "What layer IS X? How is it justified?"
 */

import { memo } from 'react';
import type { EpistemicReport, EvidenceTier } from './useAnalysis';
import './AnalysisQuadrant.css';

interface EpistemicPanelProps {
  report: EpistemicReport | null;
  loading: boolean;
}

function getTierBadge(tier: EvidenceTier): string {
  switch (tier) {
    case 'SOMATIC':
      return 'Felt';
    case 'AESTHETIC':
      return 'Beauty';
    case 'EMPIRICAL':
      return 'Observed';
    case 'CATEGORICAL':
      return 'Proof';
    case 'DERIVED':
      return 'Derived';
    default:
      return tier;
  }
}

export const EpistemicPanel = memo(function EpistemicPanel({
  report,
  loading,
}: EpistemicPanelProps) {
  if (loading) {
    return (
      <div className="analysis-panel analysis-panel--epistemic">
        <div className="analysis-panel__header">
          <span className="analysis-panel__icon">◉</span>
          <h3 className="analysis-panel__title">EPISTEMIC</h3>
        </div>
        <div className="analysis-panel__body">
          <div className="analysis-panel__loading">Tracing grounding...</div>
        </div>
      </div>
    );
  }

  if (!report) {
    return (
      <div className="analysis-panel analysis-panel--epistemic">
        <div className="analysis-panel__header">
          <span className="analysis-panel__icon">◉</span>
          <h3 className="analysis-panel__title">EPISTEMIC</h3>
        </div>
        <div className="analysis-panel__body">
          <div className="analysis-panel__empty">No analysis available</div>
        </div>
      </div>
    );
  }

  const isGrounded = report.grounding.terminates_at_axiom;

  return (
    <div className="analysis-panel analysis-panel--epistemic">
      <div className="analysis-panel__header">
        <span className="analysis-panel__icon">◉</span>
        <h3 className="analysis-panel__title">EPISTEMIC</h3>
        <span
          className={`analysis-panel__status ${isGrounded ? 'analysis-panel__status--pass' : 'analysis-panel__status--fail'}`}
        >
          {isGrounded ? '✓' : '✗'}
        </span>
      </div>

      <div className="analysis-panel__body">
        {/* Layer */}
        <div className="analysis-metric">
          <span className="analysis-metric__label">Layer</span>
          <span className="analysis-metric__value">L{report.layer}</span>
        </div>

        {/* Evidence Tier */}
        <div className="analysis-metric">
          <span className="analysis-metric__label">Evidence</span>
          <span className="evidence-badge">{getTierBadge(report.toulmin.tier)}</span>
        </div>

        {/* Grounding Chain */}
        <div className="grounding-chain">
          <div className="grounding-chain__label">Grounding Chain:</div>
          <div className="grounding-chain__steps">
            {report.grounding.steps.map(([layer, node], idx) => (
              <div key={idx} className="grounding-step">
                <span className="grounding-step__layer">L{layer}</span>
                <span className="grounding-step__arrow">→</span>
                <span className="grounding-step__node" title={node}>
                  {node.split('/').pop()?.replace('.md', '') || node}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Terminates Indicator */}
        <div className="grounding-status">
          <span className="grounding-status__icon">{isGrounded ? '⚓' : '∞'}</span>
          <span className="grounding-status__label">
            {isGrounded ? 'Terminates at Axiom' : 'Floating (ungrounded)'}
          </span>
        </div>

        {/* Summary */}
        <div className="analysis-summary">{report.summary}</div>
      </div>
    </div>
  );
});

export default EpistemicPanel;
