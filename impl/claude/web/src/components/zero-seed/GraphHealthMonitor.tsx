/**
 * GraphHealthMonitor — View L5-L6 graph health (Actions and Reflections)
 *
 * "The loss IS the landscape. Navigate toward stability."
 *
 * User Journey:
 * - View instability indicators
 * - Detect contradictions (super-additive loss)
 * - Early warning system for graph degradation
 * - Monitor edge coherence
 */

import { memo, useMemo, useState } from 'react';
import type {
  GraphHealth,
  Contradiction,
  InstabilityIndicator,
} from '../../api/zeroSeed';
import { LAYER_NAMES } from '../../api/zeroSeed';
import './ZeroSeed.css';

// =============================================================================
// Types
// =============================================================================

interface GraphHealthMonitorProps {
  /** Graph health data */
  health: GraphHealth;
  /** Timestamp of health check */
  timestamp: string;
  /** Health trend */
  trend: 'improving' | 'stable' | 'degrading';
  /** Selected node callback */
  onSelectNode?: (nodeId: string) => void;
  /** Navigate to contradiction */
  onNavigateContradiction?: (contradiction: Contradiction) => void;
  /** Loading state */
  loading?: boolean;
}

type ViewTab = 'overview' | 'contradictions' | 'instability';

// =============================================================================
// Helpers
// =============================================================================

function getSeverityColor(severity: 'low' | 'medium' | 'high' | number): string {
  if (typeof severity === 'number') {
    if (severity < 0.3) return 'var(--status-insert)';
    if (severity < 0.7) return 'var(--status-edge)';
    return 'var(--status-error)';
  }
  switch (severity) {
    case 'low':
      return 'var(--status-insert)';
    case 'medium':
      return 'var(--status-edge)';
    case 'high':
      return 'var(--status-error)';
  }
}

function getTrendIcon(trend: 'improving' | 'stable' | 'degrading'): string {
  switch (trend) {
    case 'improving':
      return '\u2197'; // Up-right arrow
    case 'stable':
      return '\u2192'; // Right arrow
    case 'degrading':
      return '\u2198'; // Down-right arrow
  }
}

function getTrendColor(trend: 'improving' | 'stable' | 'degrading'): string {
  switch (trend) {
    case 'improving':
      return 'var(--status-insert)';
    case 'stable':
      return 'var(--steel-400)';
    case 'degrading':
      return 'var(--status-error)';
  }
}

function getInstabilityIcon(type: InstabilityIndicator['type']): string {
  switch (type) {
    case 'orphan':
      return '\u26A0'; // Warning
    case 'weak_proof':
      return '\u2753'; // Question
    case 'edge_drift':
      return '\u21C4'; // Left-right arrows
    case 'layer_skip':
      return '\u21A5'; // Up arrow with bar
    case 'contradiction':
      return '\u2717'; // X mark
  }
}

function formatTimestamp(ts: string): string {
  const d = new Date(ts);
  return d.toLocaleTimeString();
}

// =============================================================================
// Sub-components
// =============================================================================

interface LayerDistributionProps {
  byLayer: Record<number, number>;
  totalNodes: number;
}

const LayerDistribution = memo(function LayerDistribution({
  byLayer,
  totalNodes,
}: LayerDistributionProps) {
  const maxCount = Math.max(...Object.values(byLayer), 1);

  return (
    <div className="layer-distribution">
      <h4>Node Distribution by Layer</h4>
      <div className="layer-bars">
        {[1, 2, 3, 4, 5, 6, 7].map((layer) => {
          const count = byLayer[layer] ?? 0;
          const pct = totalNodes > 0 ? (count / totalNodes) * 100 : 0;
          const barHeight = maxCount > 0 ? (count / maxCount) * 100 : 0;

          return (
            <div key={layer} className="layer-bar-container">
              <div className="layer-bar-value">{count}</div>
              <div
                className="layer-bar"
                data-layer={layer}
                style={{ height: `${barHeight}%` }}
              />
              <div className="layer-bar-label">
                L{layer}
                <span className="layer-name">{LAYER_NAMES[layer as 1 | 2 | 3 | 4 | 5 | 6 | 7]}</span>
              </div>
              <div className="layer-bar-pct">{pct.toFixed(1)}%</div>
            </div>
          );
        })}
      </div>
    </div>
  );
});

interface HealthGaugeProps {
  healthy: number;
  warning: number;
  critical: number;
  total: number;
}

const HealthGauge = memo(function HealthGauge({
  healthy,
  warning,
  critical,
  total,
}: HealthGaugeProps) {
  const healthyPct = total > 0 ? (healthy / total) * 100 : 100;
  const warningPct = total > 0 ? (warning / total) * 100 : 0;
  const criticalPct = total > 0 ? (critical / total) * 100 : 0;

  return (
    <div className="health-gauge">
      <div className="health-gauge__ring">
        <svg viewBox="0 0 100 100" className="health-gauge__svg">
          <circle
            cx="50"
            cy="50"
            r="45"
            fill="none"
            stroke="var(--steel-800)"
            strokeWidth="10"
          />
          {/* Healthy arc */}
          <circle
            cx="50"
            cy="50"
            r="45"
            fill="none"
            stroke="var(--status-insert)"
            strokeWidth="10"
            strokeDasharray={`${healthyPct * 2.83} 283`}
            strokeDashoffset="0"
            transform="rotate(-90 50 50)"
          />
          {/* Warning arc */}
          <circle
            cx="50"
            cy="50"
            r="45"
            fill="none"
            stroke="var(--status-edge)"
            strokeWidth="10"
            strokeDasharray={`${warningPct * 2.83} 283`}
            strokeDashoffset={`${-healthyPct * 2.83}`}
            transform="rotate(-90 50 50)"
          />
          {/* Critical arc */}
          <circle
            cx="50"
            cy="50"
            r="45"
            fill="none"
            stroke="var(--status-error)"
            strokeWidth="10"
            strokeDasharray={`${criticalPct * 2.83} 283`}
            strokeDashoffset={`${-(healthyPct + warningPct) * 2.83}`}
            transform="rotate(-90 50 50)"
          />
        </svg>
        <div className="health-gauge__center">
          <span className="health-gauge__value">{healthyPct.toFixed(0)}%</span>
          <span className="health-gauge__label">Healthy</span>
        </div>
      </div>
      <div className="health-gauge__legend">
        <div className="legend-item legend-item--healthy">
          <span className="legend-dot" />
          <span>{healthy} healthy</span>
        </div>
        <div className="legend-item legend-item--warning">
          <span className="legend-dot" />
          <span>{warning} warning</span>
        </div>
        <div className="legend-item legend-item--critical">
          <span className="legend-dot" />
          <span>{critical} critical</span>
        </div>
      </div>
    </div>
  );
});

interface ContradictionCardProps {
  contradiction: Contradiction;
  onClick?: () => void;
}

const ContradictionCard = memo(function ContradictionCard({
  contradiction,
  onClick,
}: ContradictionCardProps) {
  return (
    <div
      className={`contradiction-card ${contradiction.is_resolved ? 'contradiction-card--resolved' : ''}`}
      onClick={onClick}
    >
      <div className="contradiction-card__header">
        <span
          className="contradiction-card__severity"
          style={{ color: getSeverityColor(contradiction.severity) }}
        >
          {contradiction.severity.toUpperCase()}
        </span>
        {contradiction.is_resolved && (
          <span className="contradiction-card__resolved">Resolved</span>
        )}
      </div>
      <div className="contradiction-card__nodes">
        <span className="node-id">{contradiction.node_a}</span>
        <span className="contradiction-symbol">\u2194</span>
        <span className="node-id">{contradiction.node_b}</span>
      </div>
      <p className="contradiction-card__desc">{contradiction.description}</p>
      {contradiction.resolution_id && (
        <div className="contradiction-card__resolution">
          Resolved by: {contradiction.resolution_id}
        </div>
      )}
    </div>
  );
});

interface InstabilityListProps {
  indicators: InstabilityIndicator[];
  onSelectNode?: (nodeId: string) => void;
}

const InstabilityList = memo(function InstabilityList({
  indicators,
  onSelectNode,
}: InstabilityListProps) {
  // Group by type - must be before any early returns to follow Rules of Hooks
  const byType = useMemo(() => {
    const groups: Record<string, InstabilityIndicator[]> = {};
    for (const ind of indicators) {
      if (!groups[ind.type]) groups[ind.type] = [];
      groups[ind.type].push(ind);
    }
    return groups;
  }, [indicators]);

  if (indicators.length === 0) {
    return (
      <div className="instability-list instability-list--empty">
        <span className="instability-list__icon">\u2705</span>
        <span>No instability detected. Graph is healthy.</span>
      </div>
    );
  }

  return (
    <div className="instability-list">
      {Object.entries(byType).map(([type, items]) => (
        <div key={type} className="instability-group">
          <h4 className="instability-group__header">
            <span className="instability-icon">
              {getInstabilityIcon(type as InstabilityIndicator['type'])}
            </span>
            {type.replace('_', ' ')} ({items.length})
          </h4>
          <div className="instability-group__items">
            {items.map((ind, i) => (
              <div
                key={`${ind.node_id}-${i}`}
                className="instability-item"
                onClick={() => onSelectNode?.(ind.node_id)}
              >
                <div className="instability-item__header">
                  <span className="instability-item__node">{ind.node_id}</span>
                  <span
                    className="instability-item__severity"
                    style={{ color: getSeverityColor(ind.severity) }}
                  >
                    {(ind.severity * 100).toFixed(0)}%
                  </span>
                </div>
                <p className="instability-item__desc">{ind.description}</p>
                <p className="instability-item__action">
                  <strong>Suggested:</strong> {ind.suggested_action}
                </p>
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
});

// =============================================================================
// Main Component
// =============================================================================

export const GraphHealthMonitor = memo(function GraphHealthMonitor({
  health,
  timestamp,
  trend,
  onSelectNode,
  onNavigateContradiction,
  loading = false,
}: GraphHealthMonitorProps) {
  // UI state
  const [activeTab, setActiveTab] = useState<ViewTab>('overview');

  // Super-additive loss warning
  const hasSuper = health.super_additive_loss_detected;
  const unresolvedContradictions = useMemo(
    () => health.contradictions.filter((c) => !c.is_resolved),
    [health.contradictions]
  );

  if (loading) {
    return (
      <div className="zero-seed-panel zero-seed-panel--loading">
        <div className="zero-seed-panel__spinner" />
        <span>Checking graph health...</span>
      </div>
    );
  }

  return (
    <div className="zero-seed-panel health-monitor">
      {/* Header */}
      <header className="zero-seed-panel__header">
        <h2 className="zero-seed-panel__title">
          Graph Health Monitor
          <span className="zero-seed-panel__subtitle">L5-L6 Execution Layer</span>
        </h2>
        <div className="zero-seed-panel__stats">
          <span
            className="stat stat--trend"
            style={{ color: getTrendColor(trend) }}
          >
            {getTrendIcon(trend)} {trend}
          </span>
          <span className="stat stat--time">
            Last check: {formatTimestamp(timestamp)}
          </span>
        </div>
      </header>

      {/* Super-additive loss warning */}
      {hasSuper && (
        <div className="health-monitor__super-warning">
          <span className="warning-icon">\u26A0</span>
          <div className="warning-content">
            <strong>Super-additive loss detected!</strong>
            <p>
              The combined loss of conflicting nodes exceeds individual losses.
              This indicates deep incoherence requiring resolution.
            </p>
          </div>
        </div>
      )}

      {/* Tabs */}
      <div className="health-monitor__tabs">
        <button
          className={`tab-btn ${activeTab === 'overview' ? 'tab-btn--active' : ''}`}
          onClick={() => setActiveTab('overview')}
        >
          Overview
        </button>
        <button
          className={`tab-btn ${activeTab === 'contradictions' ? 'tab-btn--active' : ''}`}
          onClick={() => setActiveTab('contradictions')}
        >
          Contradictions
          {unresolvedContradictions.length > 0 && (
            <span className="tab-badge">{unresolvedContradictions.length}</span>
          )}
        </button>
        <button
          className={`tab-btn ${activeTab === 'instability' ? 'tab-btn--active' : ''}`}
          onClick={() => setActiveTab('instability')}
        >
          Instability
          {health.instability_indicators.length > 0 && (
            <span className="tab-badge">{health.instability_indicators.length}</span>
          )}
        </button>
      </div>

      {/* Tab content */}
      <div className="health-monitor__content">
        {activeTab === 'overview' && (
          <div className="health-monitor__overview">
            {/* Summary cards */}
            <div className="overview-cards">
              <div className="overview-card">
                <span className="overview-card__value">{health.total_nodes}</span>
                <span className="overview-card__label">Total Nodes</span>
              </div>
              <div className="overview-card">
                <span className="overview-card__value">{health.total_edges}</span>
                <span className="overview-card__label">Total Edges</span>
              </div>
              <div className="overview-card">
                <span className="overview-card__value">
                  {health.contradictions.length}
                </span>
                <span className="overview-card__label">Contradictions</span>
              </div>
              <div className="overview-card">
                <span className="overview-card__value">
                  {health.instability_indicators.length}
                </span>
                <span className="overview-card__label">Warnings</span>
              </div>
            </div>

            {/* Health gauge */}
            <HealthGauge
              healthy={health.healthy_count}
              warning={health.warning_count}
              critical={health.critical_count}
              total={health.total_nodes}
            />

            {/* Layer distribution */}
            <LayerDistribution
              byLayer={health.by_layer}
              totalNodes={health.total_nodes}
            />
          </div>
        )}

        {activeTab === 'contradictions' && (
          <div className="health-monitor__contradictions">
            {health.contradictions.length === 0 ? (
              <div className="empty-state">
                <span className="empty-icon">\u2705</span>
                <span>No contradictions detected. The graph is consistent.</span>
              </div>
            ) : (
              <div className="contradiction-list">
                {health.contradictions.map((c) => (
                  <ContradictionCard
                    key={c.id}
                    contradiction={c}
                    onClick={() => onNavigateContradiction?.(c)}
                  />
                ))}
              </div>
            )}
          </div>
        )}

        {activeTab === 'instability' && (
          <div className="health-monitor__instability">
            <InstabilityList
              indicators={health.instability_indicators}
              onSelectNode={onSelectNode}
            />
          </div>
        )}
      </div>
    </div>
  );
});

export default GraphHealthMonitor;
