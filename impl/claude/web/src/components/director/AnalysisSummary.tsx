/**
 * AnalysisSummary - Compact summary of document analysis results
 *
 * Displays key metrics from AnalysisCrystal:
 * - Claim count
 * - Reference count (discovered_refs)
 * - Placeholder count (pending implementations)
 * - Anticipated implementations count
 *
 * Supports compact mode for dense layouts.
 */

import type { AnalysisCrystal } from '../../api/director';

import './AnalysisSummary.css';

// =============================================================================
// Types
// =============================================================================

export interface AnalysisSummaryProps {
  analysis: AnalysisCrystal | null;
  compact?: boolean;
}

interface MetricConfig {
  icon: string;
  label: string;
  getValue: (analysis: AnalysisCrystal) => number;
  color?: string;
}

// =============================================================================
// Config
// =============================================================================

const METRICS: MetricConfig[] = [
  {
    icon: '◈',
    label: 'Claims',
    getValue: (a) => a.claims?.length || 0,
  },
  {
    icon: '∘',
    label: 'References',
    getValue: (a) => a.discovered_refs?.length || 0,
  },
  {
    icon: '⌛',
    label: 'Pending',
    getValue: (a) => a.placeholder_paths?.length || 0,
    color: 'pending',
  },
  {
    icon: '◉',
    label: 'Anticipated',
    getValue: (a) => a.anticipated?.length || 0,
    color: 'anticipated',
  },
];

// =============================================================================
// Component
// =============================================================================

export function AnalysisSummary({ analysis, compact = false }: AnalysisSummaryProps) {
  if (!analysis) {
    return (
      <div className="analysis-summary analysis-summary--empty">
        <span className="analysis-summary__placeholder">Not analyzed</span>
      </div>
    );
  }

  return (
    <div className="analysis-summary" data-compact={compact} role="region" aria-label="Analysis summary">
      {METRICS.map((metric) => {
        const value = metric.getValue(analysis);
        const className = `analysis-summary__metric${metric.color ? ` analysis-summary__metric--${metric.color}` : ''}`;

        return (
          <div key={metric.label} className={className} title={metric.label}>
            <span className="analysis-summary__icon" aria-hidden="true">
              {metric.icon}
            </span>
            <span className="analysis-summary__value">{value}</span>
            {!compact && <span className="analysis-summary__label">{metric.label}</span>}
          </div>
        );
      })}
    </div>
  );
}
