/**
 * DialecticalPanel — Visualize dialectical analysis (tensions & synthesis)
 *
 * "What tensions exist? How are they resolved?"
 */

import { memo } from 'react';
import type { DialecticalReport, ContradictionType } from './useAnalysis';
import './AnalysisQuadrant.css';

interface DialecticalPanelProps {
  report: DialecticalReport | null;
  loading: boolean;
}

function getTensionIcon(type: ContradictionType): string {
  switch (type) {
    case 'APPARENT':
      return '≈';
    case 'PRODUCTIVE':
      return '⇌';
    case 'PROBLEMATIC':
      return '△';
    case 'PARACONSISTENT':
      return '∥';
    default:
      return '?';
  }
}

function getTensionClass(type: ContradictionType): string {
  switch (type) {
    case 'APPARENT':
      return 'tension--apparent';
    case 'PRODUCTIVE':
      return 'tension--productive';
    case 'PROBLEMATIC':
      return 'tension--problematic';
    case 'PARACONSISTENT':
      return 'tension--paraconsistent';
    default:
      return '';
  }
}

function getTensionLabel(type: ContradictionType): string {
  switch (type) {
    case 'APPARENT':
      return 'Apparent';
    case 'PRODUCTIVE':
      return 'Productive';
    case 'PROBLEMATIC':
      return 'Problematic';
    case 'PARACONSISTENT':
      return 'Paraconsistent';
    default:
      return type;
  }
}

export const DialecticalPanel = memo(function DialecticalPanel({
  report,
  loading,
}: DialecticalPanelProps) {
  if (loading) {
    return (
      <div className="analysis-panel analysis-panel--dialectical">
        <div className="analysis-panel__header">
          <span className="analysis-panel__icon">⇌</span>
          <h3 className="analysis-panel__title">DIALECTICAL</h3>
        </div>
        <div className="analysis-panel__body">
          <div className="analysis-panel__loading">Detecting tensions...</div>
        </div>
      </div>
    );
  }

  if (!report) {
    return (
      <div className="analysis-panel analysis-panel--dialectical">
        <div className="analysis-panel__header">
          <span className="analysis-panel__icon">⇌</span>
          <h3 className="analysis-panel__title">DIALECTICAL</h3>
        </div>
        <div className="analysis-panel__body">
          <div className="analysis-panel__empty">No analysis available</div>
        </div>
      </div>
    );
  }

  const problematicCount = report.tensions.filter(
    (t) => t.classification === 'PROBLEMATIC'
  ).length;
  const productiveCount = report.tensions.filter(
    (t) => t.classification === 'PRODUCTIVE'
  ).length;
  const hasProblems = problematicCount > 0;

  return (
    <div className="analysis-panel analysis-panel--dialectical">
      <div className="analysis-panel__header">
        <span className="analysis-panel__icon">⇌</span>
        <h3 className="analysis-panel__title">DIALECTICAL</h3>
        <span
          className={`analysis-panel__status ${hasProblems ? 'analysis-panel__status--fail' : 'analysis-panel__status--pass'}`}
        >
          {hasProblems ? '✗' : '✓'}
        </span>
      </div>

      <div className="analysis-panel__body">
        {/* Summary Metrics */}
        <div className="analysis-metric">
          <span className="analysis-metric__label">Tensions</span>
          <span className="analysis-metric__value">{report.tensions.length}</span>
        </div>

        {/* Tension Breakdown */}
        <div className="tension-breakdown">
          {productiveCount > 0 && (
            <div className="tension-stat tension-stat--productive">
              <span className="tension-stat__icon">⇌</span>
              <span className="tension-stat__count">{productiveCount}</span>
              <span className="tension-stat__label">Productive</span>
            </div>
          )}
          {problematicCount > 0 && (
            <div className="tension-stat tension-stat--problematic">
              <span className="tension-stat__icon">△</span>
              <span className="tension-stat__count">{problematicCount}</span>
              <span className="tension-stat__label">Problematic</span>
            </div>
          )}
        </div>

        {/* Tension List */}
        <div className="tension-list">
          {report.tensions.slice(0, 3).map((tension, idx) => (
            <div key={idx} className={`tension-item ${getTensionClass(tension.classification)}`}>
              <div className="tension-item__header">
                <span className="tension-item__icon">
                  {getTensionIcon(tension.classification)}
                </span>
                <span className="tension-item__type">
                  {getTensionLabel(tension.classification)}
                </span>
                {tension.is_resolved && (
                  <span className="tension-item__resolved" title="Resolved">
                    ✓
                  </span>
                )}
              </div>
              <div className="tension-item__content">
                <div className="tension-item__thesis" title={tension.thesis}>
                  {tension.thesis.slice(0, 40)}
                  {tension.thesis.length > 40 ? '...' : ''}
                </div>
                <div className="tension-item__vs">vs</div>
                <div className="tension-item__antithesis" title={tension.antithesis}>
                  {tension.antithesis.slice(0, 40)}
                  {tension.antithesis.length > 40 ? '...' : ''}
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Summary */}
        <div className="analysis-summary">{report.summary}</div>
      </div>
    </div>
  );
});

export default DialecticalPanel;
