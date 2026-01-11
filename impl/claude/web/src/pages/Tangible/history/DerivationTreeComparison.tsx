/**
 * DerivationTreeComparison - Compare Derivation Trees at Two Points
 *
 * Shows how the derivation tree changed between two points in time:
 * - Side-by-side or overlay mode
 * - Highlight added/removed/modified edges
 * - Animate the transition
 * - Show Galois loss changes
 *
 * STARK BIOME: 90% steel, 10% earned amber glow.
 */

import { memo, useState, useMemo } from 'react';
import {
  X,
  GitBranch,
  Plus,
  Minus,
  Edit,
  ArrowRight,
  TrendingUp,
  TrendingDown,
  Layers,
} from 'lucide-react';

import type { DerivationComparison } from './types';
import { HISTORY_LAYER_COLORS } from './types';

// =============================================================================
// Types
// =============================================================================

interface DerivationTreeComparisonProps {
  fromTimestamp: string;
  toTimestamp: string;
  onClose: () => void;
}

// =============================================================================
// Mock Data
// =============================================================================

const MOCK_COMPARISON: DerivationComparison = {
  beforeTimestamp: '2025-11-01T00:00:00Z',
  afterTimestamp: '2025-12-21T00:00:00Z',
  nodes: [
    { id: 'composable', title: 'COMPOSABLE', layer: 0, status: 'modified' },
    { id: 'ethical', title: 'ETHICAL', layer: 0, status: 'unchanged' },
    { id: 'tasteful', title: 'TASTEFUL', layer: 0, status: 'unchanged' },
    { id: 'joy-inducing', title: 'JOY_INDUCING', layer: 1, status: 'added' },
    { id: 'heterarchical', title: 'HETERARCHICAL', layer: 1, status: 'unchanged' },
    { id: 'agentese', title: 'AGENTESE', layer: 2, status: 'modified' },
    { id: 'witness', title: 'Witness Protocol', layer: 2, status: 'unchanged' },
    { id: 'polyagent', title: 'PolyAgent', layer: 2, status: 'unchanged' },
    { id: 'di-container', title: 'DI Container', layer: 3, status: 'modified' },
    { id: 'self-reflective', title: 'Self-Reflective OS', layer: 3, status: 'added' },
    { id: 'gestalt', title: 'Gestalt', layer: 3, status: 'removed' },
  ],
  edges: [
    { from: 'composable', to: 'heterarchical', status: 'unchanged' },
    { from: 'tasteful', to: 'joy-inducing', status: 'added' },
    { from: 'ethical', to: 'witness', status: 'unchanged' },
    { from: 'composable', to: 'agentese', status: 'unchanged' },
    { from: 'composable', to: 'polyagent', status: 'unchanged' },
    { from: 'heterarchical', to: 'di-container', status: 'unchanged' },
    { from: 'joy-inducing', to: 'self-reflective', status: 'added' },
    { from: 'composable', to: 'gestalt', status: 'removed' },
  ],
  lossChange: {
    before: 0.12,
    after: 0.09,
    delta: -0.03,
  },
};

// =============================================================================
// Helpers
// =============================================================================

function formatTimestamp(timestamp: string): string {
  return new Date(timestamp).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  });
}

function getStatusIcon(status: string) {
  switch (status) {
    case 'added':
      return Plus;
    case 'removed':
      return Minus;
    case 'modified':
      return Edit;
    default:
      return null;
  }
}

// =============================================================================
// Node Component
// =============================================================================

interface ComparisonNodeProps {
  node: DerivationComparison['nodes'][0];
}

const ComparisonNode = memo(function ComparisonNode({ node }: ComparisonNodeProps) {
  const layerColor =
    HISTORY_LAYER_COLORS[node.layer as keyof typeof HISTORY_LAYER_COLORS] ||
    HISTORY_LAYER_COLORS[4];
  const StatusIcon = getStatusIcon(node.status);

  return (
    <div
      className={`comparison-node comparison-node--${node.status}`}
      style={{ '--layer-color': layerColor } as React.CSSProperties}
    >
      <span className="comparison-node__layer">L{node.layer}</span>
      <span className="comparison-node__title">{node.title}</span>
      {StatusIcon && <StatusIcon size={12} className="comparison-node__status-icon" />}
    </div>
  );
});

// =============================================================================
// Edge Component
// =============================================================================

interface ComparisonEdgeProps {
  edge: DerivationComparison['edges'][0];
  nodes: DerivationComparison['nodes'];
}

const ComparisonEdge = memo(function ComparisonEdge({ edge, nodes }: ComparisonEdgeProps) {
  const fromNode = nodes.find((n) => n.id === edge.from);
  const toNode = nodes.find((n) => n.id === edge.to);

  if (!fromNode || !toNode) return null;

  return (
    <div className={`comparison-edge comparison-edge--${edge.status}`}>
      <span className="comparison-edge__from">{fromNode.title}</span>
      <ArrowRight size={12} className="comparison-edge__arrow" />
      <span className="comparison-edge__to">{toNode.title}</span>
    </div>
  );
});

// =============================================================================
// Main Component
// =============================================================================

export const DerivationTreeComparison = memo(function DerivationTreeComparison({
  fromTimestamp,
  toTimestamp,
  onClose,
}: DerivationTreeComparisonProps) {
  const [viewMode, setViewMode] = useState<'nodes' | 'edges'>('nodes');

  // Use mock data for now
  const comparison = MOCK_COMPARISON;

  // Group nodes by status
  const nodesByStatus = useMemo(() => {
    const groups = {
      added: comparison.nodes.filter((n) => n.status === 'added'),
      removed: comparison.nodes.filter((n) => n.status === 'removed'),
      modified: comparison.nodes.filter((n) => n.status === 'modified'),
      unchanged: comparison.nodes.filter((n) => n.status === 'unchanged'),
    };
    return groups;
  }, [comparison.nodes]);

  // Group edges by status
  const edgesByStatus = useMemo(() => {
    const groups = {
      added: comparison.edges.filter((e) => e.status === 'added'),
      removed: comparison.edges.filter((e) => e.status === 'removed'),
      unchanged: comparison.edges.filter((e) => e.status === 'unchanged'),
    };
    return groups;
  }, [comparison.edges]);

  const lossImproved = comparison.lossChange.delta < 0;

  return (
    <div className="derivation-comparison-backdrop">
      <div className="derivation-comparison">
        {/* Header */}
        <div className="derivation-comparison__header">
          <div className="derivation-comparison__title">
            <GitBranch size={16} />
            <span>Derivation Tree Comparison</span>
          </div>
          <button
            className="derivation-comparison__close"
            onClick={onClose}
            aria-label="Close comparison"
          >
            <X size={16} />
          </button>
        </div>

        {/* Time Range */}
        <div className="derivation-comparison__range">
          <span className="derivation-comparison__from">{formatTimestamp(fromTimestamp)}</span>
          <ArrowRight size={14} />
          <span className="derivation-comparison__to">{formatTimestamp(toTimestamp)}</span>
        </div>

        {/* Galois Loss Change */}
        <div
          className={`derivation-comparison__loss ${lossImproved ? 'derivation-comparison__loss--improved' : 'derivation-comparison__loss--degraded'}`}
        >
          <Layers size={14} />
          <span>Galois Loss:</span>
          <span className="derivation-comparison__loss-value">
            {(comparison.lossChange.before * 100).toFixed(1)}%
          </span>
          <ArrowRight size={12} />
          <span className="derivation-comparison__loss-value">
            {(comparison.lossChange.after * 100).toFixed(1)}%
          </span>
          <span className="derivation-comparison__loss-delta">
            {lossImproved ? <TrendingDown size={12} /> : <TrendingUp size={12} />}
            {Math.abs(comparison.lossChange.delta * 100).toFixed(1)}%
          </span>
        </div>

        {/* View Mode Toggle */}
        <div className="derivation-comparison__tabs">
          <button
            className={`derivation-comparison__tab ${viewMode === 'nodes' ? 'derivation-comparison__tab--active' : ''}`}
            onClick={() => setViewMode('nodes')}
          >
            Nodes
          </button>
          <button
            className={`derivation-comparison__tab ${viewMode === 'edges' ? 'derivation-comparison__tab--active' : ''}`}
            onClick={() => setViewMode('edges')}
          >
            Edges
          </button>
        </div>

        {/* Content */}
        <div className="derivation-comparison__content">
          {viewMode === 'nodes' ? (
            <div className="derivation-comparison__nodes">
              {/* Added */}
              {nodesByStatus.added.length > 0 && (
                <div className="derivation-comparison__group derivation-comparison__group--added">
                  <div className="derivation-comparison__group-header">
                    <Plus size={12} />
                    <span>Added ({nodesByStatus.added.length})</span>
                  </div>
                  <div className="derivation-comparison__group-items">
                    {nodesByStatus.added.map((node) => (
                      <ComparisonNode key={node.id} node={node} />
                    ))}
                  </div>
                </div>
              )}

              {/* Removed */}
              {nodesByStatus.removed.length > 0 && (
                <div className="derivation-comparison__group derivation-comparison__group--removed">
                  <div className="derivation-comparison__group-header">
                    <Minus size={12} />
                    <span>Removed ({nodesByStatus.removed.length})</span>
                  </div>
                  <div className="derivation-comparison__group-items">
                    {nodesByStatus.removed.map((node) => (
                      <ComparisonNode key={node.id} node={node} />
                    ))}
                  </div>
                </div>
              )}

              {/* Modified */}
              {nodesByStatus.modified.length > 0 && (
                <div className="derivation-comparison__group derivation-comparison__group--modified">
                  <div className="derivation-comparison__group-header">
                    <Edit size={12} />
                    <span>Modified ({nodesByStatus.modified.length})</span>
                  </div>
                  <div className="derivation-comparison__group-items">
                    {nodesByStatus.modified.map((node) => (
                      <ComparisonNode key={node.id} node={node} />
                    ))}
                  </div>
                </div>
              )}

              {/* Unchanged */}
              <div className="derivation-comparison__group derivation-comparison__group--unchanged">
                <div className="derivation-comparison__group-header">
                  <span>Unchanged ({nodesByStatus.unchanged.length})</span>
                </div>
                <div className="derivation-comparison__group-items derivation-comparison__group-items--compact">
                  {nodesByStatus.unchanged.map((node) => (
                    <ComparisonNode key={node.id} node={node} />
                  ))}
                </div>
              </div>
            </div>
          ) : (
            <div className="derivation-comparison__edges">
              {/* Added Edges */}
              {edgesByStatus.added.length > 0 && (
                <div className="derivation-comparison__group derivation-comparison__group--added">
                  <div className="derivation-comparison__group-header">
                    <Plus size={12} />
                    <span>Added Edges ({edgesByStatus.added.length})</span>
                  </div>
                  <div className="derivation-comparison__group-items">
                    {edgesByStatus.added.map((edge, i) => (
                      <ComparisonEdge key={i} edge={edge} nodes={comparison.nodes} />
                    ))}
                  </div>
                </div>
              )}

              {/* Removed Edges */}
              {edgesByStatus.removed.length > 0 && (
                <div className="derivation-comparison__group derivation-comparison__group--removed">
                  <div className="derivation-comparison__group-header">
                    <Minus size={12} />
                    <span>Removed Edges ({edgesByStatus.removed.length})</span>
                  </div>
                  <div className="derivation-comparison__group-items">
                    {edgesByStatus.removed.map((edge, i) => (
                      <ComparisonEdge key={i} edge={edge} nodes={comparison.nodes} />
                    ))}
                  </div>
                </div>
              )}

              {/* Unchanged Edges */}
              <div className="derivation-comparison__group derivation-comparison__group--unchanged">
                <div className="derivation-comparison__group-header">
                  <span>Unchanged Edges ({edgesByStatus.unchanged.length})</span>
                </div>
                <div className="derivation-comparison__group-items derivation-comparison__group-items--compact">
                  {edgesByStatus.unchanged.map((edge, i) => (
                    <ComparisonEdge key={i} edge={edge} nodes={comparison.nodes} />
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
});
