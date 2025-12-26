/**
 * ConstitutionalDashboard — Main composite component
 *
 * Combines:
 * - ConstitutionalRadar (7-principle radar chart)
 * - ConstitutionalScorecard (detailed table)
 * - TrustLevelBadge (trust level indicator)
 *
 * Fetches data via useConstitutional hook.
 * Responsive layout with vertical/horizontal modes.
 */

import { ConstitutionalRadar } from './ConstitutionalRadar';
import { ConstitutionalScorecard } from './ConstitutionalScorecard';
import { TrustLevelBadge } from './TrustLevelBadge';
import { useConstitutional } from './useConstitutional';
import './ConstitutionalDashboard.css';

// =============================================================================
// Types
// =============================================================================

export interface ConstitutionalDashboardProps {
  /** Agent ID to fetch data for */
  agentId: string;
  /** Layout mode */
  layout?: 'horizontal' | 'vertical';
  /** Show radar chart */
  showRadar?: boolean;
  /** Show scorecard */
  showScorecard?: boolean;
  /** Show trust badge */
  showTrust?: boolean;
  /** Subscribe to real-time updates */
  subscribe?: boolean;
}

// =============================================================================
// Component
// =============================================================================

export function ConstitutionalDashboard({
  agentId,
  layout = 'vertical',
  showRadar = true,
  showScorecard = true,
  showTrust = true,
  subscribe = false,
}: ConstitutionalDashboardProps) {
  const { data, alignment, trust, loading, error } = useConstitutional({
    agentId,
    subscribe,
  });

  // Loading state
  if (loading && !data) {
    return (
      <div className="constitutional-dashboard constitutional-dashboard--loading">
        <div className="constitutional-dashboard__placeholder">
          <div className="constitutional-dashboard__spinner" />
          <p>Loading constitutional data...</p>
        </div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="constitutional-dashboard constitutional-dashboard--error">
        <div className="constitutional-dashboard__placeholder">
          <h3>Error loading constitutional data</h3>
          <p>{error.message}</p>
        </div>
      </div>
    );
  }

  // Empty state
  if (!alignment && !trust) {
    return (
      <div className="constitutional-dashboard constitutional-dashboard--empty">
        <div className="constitutional-dashboard__placeholder">
          <h3>No constitutional data available</h3>
          <p>Constitutional scores and trust data will appear here.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="constitutional-dashboard" data-layout={layout}>
      {/* Header with trust badge */}
      {showTrust && trust && (
        <div className="constitutional-dashboard__header">
          <h2 className="constitutional-dashboard__title">Constitutional Dashboard</h2>
          <TrustLevelBadge level={trust.trust_level} reasoning={trust.reasoning} />
        </div>
      )}

      {/* Top row: Radar + Scorecard */}
      {(showRadar || showScorecard) && (
        <div className="constitutional-dashboard__top">
          {showRadar && (
            <div className="constitutional-dashboard__radar">
              <ConstitutionalRadar alignment={alignment} width={400} height={400} />
            </div>
          )}
          {showScorecard && (
            <div className="constitutional-dashboard__scorecard">
              <ConstitutionalScorecard alignment={alignment} trust={trust} />
            </div>
          )}
        </div>
      )}

      {/* Trust metrics (if available) */}
      {trust && (
        <div className="constitutional-dashboard__metrics">
          <div className="constitutional-dashboard__metric">
            <div className="constitutional-dashboard__metric-label">Average Alignment</div>
            <div className="constitutional-dashboard__metric-value">
              {(trust.average_alignment * 100).toFixed(1)}%
            </div>
          </div>
          <div className="constitutional-dashboard__metric">
            <div className="constitutional-dashboard__metric-label">Violation Rate</div>
            <div className="constitutional-dashboard__metric-value">
              {(trust.violation_rate * 100).toFixed(1)}%
            </div>
          </div>
          <div className="constitutional-dashboard__metric">
            <div className="constitutional-dashboard__metric-label">Trust Capital</div>
            <div className="constitutional-dashboard__metric-value">
              {trust.trust_capital.toFixed(2)}
            </div>
          </div>
          <div className="constitutional-dashboard__metric">
            <div className="constitutional-dashboard__metric-label">Marks Analyzed</div>
            <div className="constitutional-dashboard__metric-value">
              {trust.total_marks_analyzed}
            </div>
          </div>
        </div>
      )}

      {/* Dominant principles (if available) */}
      {trust && trust.dominant_principles.length > 0 && (
        <div className="constitutional-dashboard__dominant">
          <h4 className="constitutional-dashboard__dominant-title">Dominant Principles</h4>
          <div className="constitutional-dashboard__dominant-list">
            {trust.dominant_principles.map((principle) => (
              <div key={principle} className="constitutional-dashboard__dominant-item">
                {principle}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Reasoning */}
      {trust && (
        <div className="constitutional-dashboard__reasoning">
          <h4 className="constitutional-dashboard__reasoning-title">Trust Assessment</h4>
          <p className="constitutional-dashboard__reasoning-text">{trust.reasoning}</p>
        </div>
      )}
    </div>
  );
}
