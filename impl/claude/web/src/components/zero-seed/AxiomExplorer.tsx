/**
 * AxiomExplorer — View L1-L2 nodes (Axioms and Values)
 *
 * "The ground layer. Irreducible truth taken on faith."
 *
 * User Journey:
 * - View discovered axioms as fixed points
 * - See loss values and health status
 * - Drill into axiom proofs (none, by definition)
 * - Navigate grounding relationships
 */

import { memo, useCallback, useMemo, useState } from 'react';
import type { ZeroNode, NodeLoss } from '../../api/zeroSeed';
import './ZeroSeed.css';

// =============================================================================
// Types
// =============================================================================

interface AxiomExplorerProps {
  /** Axiom nodes (L1) */
  axioms: ZeroNode[];
  /** Value nodes (L2) */
  values: ZeroNode[];
  /** Loss data for nodes */
  losses: Map<string, NodeLoss>;
  /** Fixed point node IDs */
  fixedPoints: Set<string>;
  /** Selected node callback */
  onSelectNode?: (nodeId: string) => void;
  /** Open node in hypergraph editor */
  onOpenInEditor?: (node: ZeroNode) => void;
  /** Currently selected node */
  selectedNode?: string | null;
  /** Loading state */
  loading?: boolean;
}

type SortField = 'title' | 'loss' | 'confidence' | 'created_at';
type SortDir = 'asc' | 'desc';
type LayerFilter = 'all' | 1 | 2;

// =============================================================================
// Helpers
// =============================================================================

function getLossColor(loss: number): string {
  if (loss < 0.3) return 'var(--status-insert)'; // Green - healthy
  if (loss < 0.7) return 'var(--status-edge)'; // Yellow - warning
  return 'var(--status-error)'; // Red - critical
}

function getHealthBadge(status: 'healthy' | 'warning' | 'critical'): {
  color: string;
  label: string;
} {
  switch (status) {
    case 'healthy':
      return { color: 'var(--status-insert)', label: 'Healthy' };
    case 'warning':
      return { color: 'var(--status-edge)', label: 'Warning' };
    case 'critical':
      return { color: 'var(--status-error)', label: 'Critical' };
  }
}

function formatDate(dateStr: string): string {
  const d = new Date(dateStr);
  const now = new Date();
  const diff = now.getTime() - d.getTime();
  const days = Math.floor(diff / 86400000);

  if (days < 1) return 'today';
  if (days === 1) return 'yesterday';
  if (days < 7) return `${days}d ago`;
  return d.toLocaleDateString();
}

// =============================================================================
// Component
// =============================================================================

export const AxiomExplorer = memo(function AxiomExplorer({
  axioms,
  values,
  losses,
  fixedPoints,
  onSelectNode,
  onOpenInEditor,
  selectedNode,
  loading = false,
}: AxiomExplorerProps) {
  // UI state
  const [layerFilter, setLayerFilter] = useState<LayerFilter>('all');
  const [sortField, setSortField] = useState<SortField>('loss');
  const [sortDir, setSortDir] = useState<SortDir>('desc');
  const [searchQuery, setSearchQuery] = useState('');
  const [expandedNode, setExpandedNode] = useState<string | null>(null);

  // Combine and filter nodes
  const allNodes = useMemo(() => {
    let nodes: ZeroNode[] = [];

    if (layerFilter === 'all' || layerFilter === 1) {
      nodes = nodes.concat(axioms);
    }
    if (layerFilter === 'all' || layerFilter === 2) {
      nodes = nodes.concat(values);
    }

    // Search filter
    if (searchQuery) {
      const q = searchQuery.toLowerCase();
      nodes = nodes.filter(
        (n) =>
          n.title.toLowerCase().includes(q) ||
          n.content.toLowerCase().includes(q) ||
          n.path.toLowerCase().includes(q)
      );
    }

    // Sort
    nodes.sort((a, b) => {
      let cmp = 0;
      switch (sortField) {
        case 'title':
          cmp = a.title.localeCompare(b.title);
          break;
        case 'loss': {
          const lossA = losses.get(a.id)?.loss ?? 0;
          const lossB = losses.get(b.id)?.loss ?? 0;
          cmp = lossA - lossB;
          break;
        }
        case 'confidence':
          cmp = a.confidence - b.confidence;
          break;
        case 'created_at':
          cmp = new Date(a.created_at).getTime() - new Date(b.created_at).getTime();
          break;
      }
      return sortDir === 'asc' ? cmp : -cmp;
    });

    return nodes;
  }, [axioms, values, layerFilter, searchQuery, sortField, sortDir, losses]);

  // Stats
  const stats = useMemo(() => {
    let healthy = 0;
    let warning = 0;
    let critical = 0;

    for (const node of [...axioms, ...values]) {
      const loss = losses.get(node.id);
      if (!loss) continue;
      switch (loss.health_status) {
        case 'healthy':
          healthy++;
          break;
        case 'warning':
          warning++;
          break;
        case 'critical':
          critical++;
          break;
      }
    }

    return {
      total: axioms.length + values.length,
      axiomCount: axioms.length,
      valueCount: values.length,
      fixedPointCount: fixedPoints.size,
      healthy,
      warning,
      critical,
    };
  }, [axioms, values, losses, fixedPoints]);

  // Handle node click
  const handleNodeClick = useCallback(
    (nodeId: string) => {
      if (expandedNode === nodeId) {
        setExpandedNode(null);
      } else {
        setExpandedNode(nodeId);
      }
      onSelectNode?.(nodeId);
    },
    [expandedNode, onSelectNode]
  );

  // Handle sort
  const handleSort = useCallback(
    (field: SortField) => {
      if (sortField === field) {
        setSortDir((d) => (d === 'asc' ? 'desc' : 'asc'));
      } else {
        setSortField(field);
        setSortDir('desc');
      }
    },
    [sortField]
  );

  if (loading) {
    return (
      <div className="zero-seed-panel zero-seed-panel--loading">
        <div className="zero-seed-panel__spinner" />
        <span>Loading axioms...</span>
      </div>
    );
  }

  return (
    <div className="zero-seed-panel axiom-explorer">
      {/* Header */}
      <header className="zero-seed-panel__header">
        <h2 className="zero-seed-panel__title">
          Axiom Explorer
          <span className="zero-seed-panel__subtitle">L1-L2 Ground Layer</span>
        </h2>
        <div className="zero-seed-panel__stats">
          <span className="stat stat--total">
            {stats.total} nodes
          </span>
          <span className="stat stat--fixed" title="Fixed points (low loss)">
            {stats.fixedPointCount} fixed
          </span>
        </div>
      </header>

      {/* Health summary */}
      <div className="axiom-explorer__health-bar">
        <div
          className="health-segment health-segment--healthy"
          style={{ flex: stats.healthy }}
          title={`${stats.healthy} healthy`}
        />
        <div
          className="health-segment health-segment--warning"
          style={{ flex: stats.warning }}
          title={`${stats.warning} warning`}
        />
        <div
          className="health-segment health-segment--critical"
          style={{ flex: stats.critical }}
          title={`${stats.critical} critical`}
        />
      </div>

      {/* Filters */}
      <div className="axiom-explorer__filters">
        <div className="filter-group">
          <button
            className={`filter-btn ${layerFilter === 'all' ? 'filter-btn--active' : ''}`}
            onClick={() => setLayerFilter('all')}
          >
            All ({stats.total})
          </button>
          <button
            className={`filter-btn ${layerFilter === 1 ? 'filter-btn--active' : ''}`}
            onClick={() => setLayerFilter(1)}
          >
            L1 Axioms ({stats.axiomCount})
          </button>
          <button
            className={`filter-btn ${layerFilter === 2 ? 'filter-btn--active' : ''}`}
            onClick={() => setLayerFilter(2)}
          >
            L2 Values ({stats.valueCount})
          </button>
        </div>

        <input
          type="text"
          className="axiom-explorer__search"
          placeholder="Search axioms..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
        />
      </div>

      {/* Column headers */}
      <div className="axiom-explorer__header-row">
        <button
          className={`header-cell header-cell--sortable ${sortField === 'title' ? 'header-cell--active' : ''}`}
          onClick={() => handleSort('title')}
        >
          Node {sortField === 'title' && (sortDir === 'asc' ? '\u25B2' : '\u25BC')}
        </button>
        <button
          className={`header-cell header-cell--sortable ${sortField === 'loss' ? 'header-cell--active' : ''}`}
          onClick={() => handleSort('loss')}
        >
          Loss {sortField === 'loss' && (sortDir === 'asc' ? '\u25B2' : '\u25BC')}
        </button>
        <button
          className={`header-cell header-cell--sortable ${sortField === 'confidence' ? 'header-cell--active' : ''}`}
          onClick={() => handleSort('confidence')}
        >
          Conf {sortField === 'confidence' && (sortDir === 'asc' ? '\u25B2' : '\u25BC')}
        </button>
        <span className="header-cell">Status</span>
      </div>

      {/* Node list */}
      <div className="axiom-explorer__list">
        {allNodes.length === 0 ? (
          <div className="axiom-explorer__empty">
            {searchQuery ? 'No matching axioms found' : 'No axioms discovered yet'}
          </div>
        ) : (
          allNodes.map((node) => {
            const loss = losses.get(node.id);
            const isFixed = fixedPoints.has(node.id);
            const isExpanded = expandedNode === node.id;
            const isSelected = selectedNode === node.id;
            const health = loss ? getHealthBadge(loss.health_status) : null;

            return (
              <div
                key={node.id}
                className={`axiom-card ${isExpanded ? 'axiom-card--expanded' : ''} ${isSelected ? 'axiom-card--selected' : ''}`}
                onClick={() => handleNodeClick(node.id)}
              >
                {/* Main row */}
                <div className="axiom-card__row">
                  {/* Node info */}
                  <div className="axiom-card__info">
                    <div className="axiom-card__title">
                      <span
                        className="axiom-card__layer-badge"
                        data-layer={node.layer}
                      >
                        L{node.layer}
                      </span>
                      {node.title}
                      {isFixed && (
                        <span className="axiom-card__fixed-badge" title="Fixed point (stable)">
                          FP
                        </span>
                      )}
                    </div>
                    <div className="axiom-card__path">{node.path}</div>
                  </div>

                  {/* Loss */}
                  <div className="axiom-card__loss">
                    <div
                      className="loss-bar"
                      style={{
                        '--loss-value': loss?.loss ?? 0,
                        '--loss-color': getLossColor(loss?.loss ?? 0),
                      } as React.CSSProperties}
                    >
                      <div className="loss-bar__fill" />
                    </div>
                    <span className="loss-value">{(loss?.loss ?? 0).toFixed(3)}</span>
                  </div>

                  {/* Confidence */}
                  <div className="axiom-card__confidence">
                    {(node.confidence * 100).toFixed(0)}%
                  </div>

                  {/* Health status */}
                  <div className="axiom-card__status">
                    {health && (
                      <span
                        className="status-badge"
                        style={{ '--badge-color': health.color } as React.CSSProperties}
                      >
                        {health.label}
                      </span>
                    )}
                  </div>
                </div>

                {/* Expanded details */}
                {isExpanded && (
                  <div className="axiom-card__details">
                    <div className="axiom-card__content">
                      <h4>Content</h4>
                      <p>{node.content || 'No content'}</p>
                    </div>

                    {loss && (
                      <div className="axiom-card__loss-breakdown">
                        <h4>Loss Components</h4>
                        <div className="loss-components">
                          <div className="loss-component">
                            <span className="loss-component__label">Content</span>
                            <span className="loss-component__value">
                              {loss.components.content_loss.toFixed(3)}
                            </span>
                          </div>
                          <div className="loss-component">
                            <span className="loss-component__label">Proof</span>
                            <span className="loss-component__value">
                              {loss.components.proof_loss.toFixed(3)}
                            </span>
                          </div>
                          <div className="loss-component">
                            <span className="loss-component__label">Edge</span>
                            <span className="loss-component__value">
                              {loss.components.edge_loss.toFixed(3)}
                            </span>
                          </div>
                          <div className="loss-component">
                            <span className="loss-component__label">Meta</span>
                            <span className="loss-component__value">
                              {loss.components.metadata_loss.toFixed(3)}
                            </span>
                          </div>
                        </div>
                      </div>
                    )}

                    <div className="axiom-card__meta">
                      <span>Created: {formatDate(node.created_at)}</span>
                      <span>By: {node.created_by}</span>
                      {node.tags.length > 0 && (
                        <div className="axiom-card__tags">
                          {node.tags.map((tag) => (
                            <span key={tag} className="tag">
                              {tag}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>

                    <div className="axiom-card__note">
                      <strong>Note:</strong> L1-L2 nodes have no proof by definition.
                      They are taken on faith as irreducible ground.
                    </div>

                    {onOpenInEditor && (
                      <div className="axiom-card__actions">
                        <button
                          className="btn btn--primary btn--sm"
                          onClick={(e) => {
                            e.stopPropagation();
                            onOpenInEditor(node);
                          }}
                        >
                          Open in Editor
                        </button>
                      </div>
                    )}
                  </div>
                )}
              </div>
            );
          })
        )}
      </div>
    </div>
  );
});

export default AxiomExplorer;
