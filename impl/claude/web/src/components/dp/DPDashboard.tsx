/**
 * DPDashboard — Example composite view
 *
 * Shows how to combine the three DP visualization components:
 * - ValueFunctionChart (radar)
 * - ConstitutionScorecard (detailed table)
 * - PolicyTraceView (solution timeline)
 *
 * This is a demo/example component. Adapt for your use case.
 */

import { ValueFunctionChart } from './ValueFunctionChart';
import { ConstitutionScorecard } from './ConstitutionScorecard';
import { PolicyTraceView } from './PolicyTraceView';
import type { ValueScore, PolicyTrace } from './types';
import './DPDashboard.css';

// =============================================================================
// Types
// =============================================================================

export interface DPDashboardProps {
  /** Value score (principle evaluations) */
  valueScore: ValueScore | null;
  /** Policy trace (solution path) */
  policyTrace: PolicyTrace | null;
  /** Layout mode */
  layout?: 'horizontal' | 'vertical';
  /** Show radar chart */
  showRadar?: boolean;
  /** Show scorecard */
  showScorecard?: boolean;
  /** Show trace */
  showTrace?: boolean;
}

// =============================================================================
// Component
// =============================================================================

export function DPDashboard({
  valueScore,
  policyTrace,
  layout = 'vertical',
  showRadar = true,
  showScorecard = true,
  showTrace = true,
}: DPDashboardProps) {
  const isEmpty = !valueScore && !policyTrace;

  if (isEmpty) {
    return (
      <div className="dp-dashboard dp-dashboard--empty">
        <div className="dp-dashboard__placeholder">
          <h3>No DP data available</h3>
          <p>Value scores and policy traces will appear here.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="dp-dashboard" data-layout={layout}>
      {/* Top row: Radar + Scorecard */}
      {(showRadar || showScorecard) && (
        <div className="dp-dashboard__top">
          {showRadar && (
            <div className="dp-dashboard__chart">
              <ValueFunctionChart valueScore={valueScore} width={400} height={400} />
            </div>
          )}
          {showScorecard && (
            <div className="dp-dashboard__scorecard">
              <ConstitutionScorecard valueScore={valueScore} />
            </div>
          )}
        </div>
      )}

      {/* Bottom row: Policy Trace */}
      {showTrace && (
        <div className="dp-dashboard__trace">
          <PolicyTraceView trace={policyTrace} showCumulative />
        </div>
      )}
    </div>
  );
}
