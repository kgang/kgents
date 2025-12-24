/**
 * GenerativePanel — Visualize generative analysis (regeneration & compression)
 *
 * "Can X be regenerated from its axioms?"
 */

import { memo } from 'react';
import type { GenerativeReport } from './useAnalysis';
import { lossToHue } from '../../hooks/useLoss';
import './AnalysisQuadrant.css';

interface GenerativePanelProps {
  report: GenerativeReport | null;
  loading: boolean;
}

export const GenerativePanel = memo(function GenerativePanel({
  report,
  loading,
}: GenerativePanelProps) {
  if (loading) {
    return (
      <div className="analysis-panel analysis-panel--generative">
        <div className="analysis-panel__header">
          <span className="analysis-panel__icon">⚛</span>
          <h3 className="analysis-panel__title">GENERATIVE</h3>
        </div>
        <div className="analysis-panel__body">
          <div className="analysis-panel__loading">Testing regeneration...</div>
        </div>
      </div>
    );
  }

  if (!report) {
    return (
      <div className="analysis-panel analysis-panel--generative">
        <div className="analysis-panel__header">
          <span className="analysis-panel__icon">⚛</span>
          <h3 className="analysis-panel__title">GENERATIVE</h3>
        </div>
        <div className="analysis-panel__body">
          <div className="analysis-panel__empty">No analysis available</div>
        </div>
      </div>
    );
  }

  const isRegenerable = report.regeneration.passed;
  const compressionRatio = report.compression_ratio;
  const compressionHue = lossToHue(compressionRatio);

  // Quality assessment
  const compressionQuality =
    compressionRatio < 0.3 ? 'excellent' : compressionRatio < 0.7 ? 'good' : 'poor';

  return (
    <div className="analysis-panel analysis-panel--generative">
      <div className="analysis-panel__header">
        <span className="analysis-panel__icon">⚛</span>
        <h3 className="analysis-panel__title">GENERATIVE</h3>
        <span
          className={`analysis-panel__status ${isRegenerable ? 'analysis-panel__status--pass' : 'analysis-panel__status--fail'}`}
        >
          {isRegenerable ? '✓' : '✗'}
        </span>
      </div>

      <div className="analysis-panel__body">
        {/* Regeneration Status */}
        <div className="analysis-metric">
          <span className="analysis-metric__label">Regenerable</span>
          <span className="analysis-metric__value">{isRegenerable ? 'Yes' : 'No'}</span>
        </div>

        {/* Compression Ratio */}
        <div className="compression-metric">
          <div className="compression-metric__label">Compression Ratio</div>
          <div className="compression-metric__value">
            <span
              className="compression-ratio"
              style={{ color: `hsl(${compressionHue}, 60%, 60%)` }}
            >
              {compressionRatio.toFixed(2)}
            </span>
            <span className={`compression-quality compression-quality--${compressionQuality}`}>
              {compressionQuality}
            </span>
          </div>
          <div className="compression-bar">
            <div
              className="compression-bar__fill"
              style={{
                width: `${Math.min(100, compressionRatio * 100)}%`,
                backgroundColor: `hsl(${compressionHue}, 60%, 50%)`,
              }}
            />
          </div>
        </div>

        {/* Minimal Kernel */}
        <div className="kernel-metric">
          <div className="kernel-metric__label">
            Minimal Kernel ({report.minimal_kernel.length} axioms)
          </div>
          <div className="kernel-list">
            {report.minimal_kernel.slice(0, 3).map((axiom, idx) => (
              <div key={idx} className="kernel-item" title={axiom}>
                <span className="kernel-item__bullet">•</span>
                <span className="kernel-item__text">
                  {axiom.length > 30 ? axiom.slice(0, 30) + '...' : axiom}
                </span>
              </div>
            ))}
            {report.minimal_kernel.length > 3 && (
              <div className="kernel-item kernel-item--more">
                +{report.minimal_kernel.length - 3} more
              </div>
            )}
          </div>
        </div>

        {/* Summary */}
        <div className="analysis-summary">{report.summary}</div>
      </div>
    </div>
  );
});

export default GenerativePanel;
