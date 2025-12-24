/**
 * CategoricalPanel — Visualize categorical analysis (laws & fixed points)
 *
 * "Does X satisfy its own composition laws?"
 */

import { memo } from 'react';
import type { CategoricalReport, LawStatus } from './useAnalysis';
import './AnalysisQuadrant.css';

interface CategoricalPanelProps {
  report: CategoricalReport | null;
  loading: boolean;
}

function getLawStatusIcon(status: LawStatus): string {
  switch (status) {
    case 'PASSED':
      return '✓';
    case 'STRUCTURAL':
      return '⊞';
    case 'FAILED':
      return '✗';
    case 'UNDECIDABLE':
      return '?';
    default:
      return '?';
  }
}

function getLawStatusClass(status: LawStatus): string {
  switch (status) {
    case 'PASSED':
      return 'law-status--passed';
    case 'STRUCTURAL':
      return 'law-status--structural';
    case 'FAILED':
      return 'law-status--failed';
    case 'UNDECIDABLE':
      return 'law-status--undecidable';
    default:
      return '';
  }
}

export const CategoricalPanel = memo(function CategoricalPanel({
  report,
  loading,
}: CategoricalPanelProps) {
  if (loading) {
    return (
      <div className="analysis-panel analysis-panel--categorical">
        <div className="analysis-panel__header">
          <span className="analysis-panel__icon">⊚</span>
          <h3 className="analysis-panel__title">CATEGORICAL</h3>
        </div>
        <div className="analysis-panel__body">
          <div className="analysis-panel__loading">Loading laws...</div>
        </div>
      </div>
    );
  }

  if (!report) {
    return (
      <div className="analysis-panel analysis-panel--categorical">
        <div className="analysis-panel__header">
          <span className="analysis-panel__icon">⊚</span>
          <h3 className="analysis-panel__title">CATEGORICAL</h3>
        </div>
        <div className="analysis-panel__body">
          <div className="analysis-panel__empty">No analysis available</div>
        </div>
      </div>
    );
  }

  const lawsPassed = report.law_verifications.filter((v) => v.passed).length;
  const lawsTotal = report.law_verifications.length;
  const hasViolations = report.law_verifications.some((v) => v.status === 'FAILED');

  return (
    <div className="analysis-panel analysis-panel--categorical">
      <div className="analysis-panel__header">
        <span className="analysis-panel__icon">⊚</span>
        <h3 className="analysis-panel__title">CATEGORICAL</h3>
        <span
          className={`analysis-panel__status ${hasViolations ? 'analysis-panel__status--fail' : 'analysis-panel__status--pass'}`}
        >
          {hasViolations ? '✗' : '✓'}
        </span>
      </div>

      <div className="analysis-panel__body">
        {/* Summary */}
        <div className="analysis-metric">
          <span className="analysis-metric__label">Laws Verified</span>
          <span className="analysis-metric__value">
            {lawsPassed}/{lawsTotal}
          </span>
        </div>

        {/* Law Verifications */}
        <div className="law-list">
          {report.law_verifications.map((verification, idx) => (
            <div key={idx} className="law-item">
              <span
                className={`law-status ${getLawStatusClass(verification.status)}`}
                title={verification.evidence}
              >
                {getLawStatusIcon(verification.status)}
              </span>
              <span className="law-name">{verification.law_name}</span>
            </div>
          ))}
        </div>

        {/* Fixed Point Indicator */}
        {report.fixed_point && report.fixed_point.is_self_referential && (
          <div className="fixed-point-indicator">
            <span className="fixed-point-icon">⊛</span>
            <span className="fixed-point-label">
              {report.fixed_point.is_valid ? 'Valid Fixed Point' : 'Paradox'}
            </span>
          </div>
        )}

        {/* Summary */}
        <div className="analysis-summary">{report.summary}</div>
      </div>
    </div>
  );
});

export default CategoricalPanel;
