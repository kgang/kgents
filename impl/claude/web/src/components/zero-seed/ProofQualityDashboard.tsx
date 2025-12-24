/**
 * ProofQualityDashboard — View L3-L4 proof quality (Goals and Specs)
 *
 * "Every node justifies its existence - or admits it cannot."
 *
 * User Journey:
 * - View coherence scores for proofs
 * - See Toulmin breakdown visualization
 * - Explore ghost alternatives
 * - Identify weak proofs needing improvement
 */

import { memo, useCallback, useMemo, useState } from 'react';
import type { ProofQuality, ToulminProof, GhostAlternative } from '../../api/zeroSeed';
import './ZeroSeed.css';

// =============================================================================
// Types
// =============================================================================

interface ProofQualityDashboardProps {
  /** Proof quality data */
  proofs: ProofQuality[];
  /** Average coherence across all proofs */
  averageCoherence: number;
  /** Counts by quality tier */
  byQualityTier: Record<string, number>;
  /** Node IDs needing improvement */
  needsImprovement: string[];
  /** Selected node callback */
  onSelectNode?: (nodeId: string) => void;
  /** Currently selected node */
  selectedNode?: string | null;
  /** Loading state */
  loading?: boolean;
}

type ViewMode = 'grid' | 'list' | 'toulmin';
type SortField = 'coherence' | 'warrant' | 'backing' | 'rebuttals';

// =============================================================================
// Helpers
// =============================================================================

function getQualityColor(tier: 'strong' | 'moderate' | 'weak'): string {
  switch (tier) {
    case 'strong':
      return 'var(--status-insert)';
    case 'moderate':
      return 'var(--status-edge)';
    case 'weak':
      return 'var(--status-error)';
  }
}

function getTierLabel(tier: 'categorical' | 'empirical' | 'aesthetic' | 'somatic'): string {
  switch (tier) {
    case 'categorical':
      return 'Categorical (logical necessity)';
    case 'empirical':
      return 'Empirical (observed evidence)';
    case 'aesthetic':
      return 'Aesthetic (taste/beauty)';
    case 'somatic':
      return 'Somatic (felt sense)';
  }
}

function truncate(text: string, maxLen: number): string {
  if (text.length <= maxLen) return text;
  return text.slice(0, maxLen - 3) + '...';
}

// =============================================================================
// Sub-components
// =============================================================================

interface ToulminVisualizerProps {
  proof: ToulminProof;
  coherenceScore: number;
}

const ToulminVisualizer = memo(function ToulminVisualizer({
  proof,
  coherenceScore,
}: ToulminVisualizerProps) {
  return (
    <div className="toulmin-visualizer">
      <div className="toulmin-visualizer__header">
        <span className="toulmin-visualizer__tier">{getTierLabel(proof.tier)}</span>
        <span className="toulmin-visualizer__coherence">
          Coherence: {(coherenceScore * 100).toFixed(1)}%
        </span>
      </div>

      <div className="toulmin-visualizer__structure">
        {/* Data -> Claim flow */}
        <div className="toulmin-section toulmin-section--data">
          <h5>Data (Evidence)</h5>
          <p>{proof.data}</p>
        </div>

        <div className="toulmin-arrow toulmin-arrow--horizontal" />

        <div className="toulmin-section toulmin-section--claim">
          <h5>Claim</h5>
          <p>
            <span className="qualifier">{proof.qualifier}</span>
            {proof.claim}
          </p>
        </div>

        {/* Warrant (below arrow) */}
        <div className="toulmin-section toulmin-section--warrant">
          <h5>Warrant (Reasoning)</h5>
          <p>{proof.warrant}</p>
        </div>

        {/* Backing (supports warrant) */}
        <div className="toulmin-section toulmin-section--backing">
          <h5>Backing</h5>
          <p>{proof.backing}</p>
        </div>

        {/* Rebuttals */}
        {proof.rebuttals.length > 0 && (
          <div className="toulmin-section toulmin-section--rebuttals">
            <h5>Rebuttals ({proof.rebuttals.length})</h5>
            <ul>
              {proof.rebuttals.map((r, i) => (
                <li key={i}>{r}</li>
              ))}
            </ul>
          </div>
        )}

        {/* Principles */}
        {proof.principles.length > 0 && (
          <div className="toulmin-section toulmin-section--principles">
            <h5>Principles Referenced</h5>
            <div className="principle-tags">
              {proof.principles.map((p) => (
                <span key={p} className="principle-tag">
                  {p}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
});

interface GhostAlternativesProps {
  alternatives: GhostAlternative[];
  onSelect?: (alt: GhostAlternative) => void;
}

const GhostAlternatives = memo(function GhostAlternatives({
  alternatives,
  onSelect,
}: GhostAlternativesProps) {
  if (alternatives.length === 0) {
    return (
      <div className="ghost-alternatives ghost-alternatives--empty">
        <span>No ghost alternatives discovered</span>
      </div>
    );
  }

  return (
    <div className="ghost-alternatives">
      <h4>Ghost Alternatives</h4>
      <p className="ghost-alternatives__desc">
        Alternative warrants that could justify this claim
      </p>
      <div className="ghost-alternatives__list">
        {alternatives.map((alt) => (
          <div
            key={alt.id}
            className="ghost-card"
            onClick={() => onSelect?.(alt)}
          >
            <div className="ghost-card__header">
              <span className="ghost-card__confidence">
                {(alt.confidence * 100).toFixed(0)}% confidence
              </span>
            </div>
            <div className="ghost-card__warrant">
              <strong>Warrant:</strong> {alt.warrant}
            </div>
            <div className="ghost-card__reasoning">
              <strong>Reasoning:</strong> {alt.reasoning}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
});

// =============================================================================
// Main Component
// =============================================================================

export const ProofQualityDashboard = memo(function ProofQualityDashboard({
  proofs,
  averageCoherence,
  byQualityTier,
  needsImprovement,
  onSelectNode,
  selectedNode,
  loading = false,
}: ProofQualityDashboardProps) {
  // UI state
  const [viewMode, setViewMode] = useState<ViewMode>('grid');
  const [sortField, setSortField] = useState<SortField>('coherence');
  const [sortDir, setSortDir] = useState<'asc' | 'desc'>('desc');
  const [qualityFilter, setQualityFilter] = useState<string | null>(null);
  const [expandedProof, setExpandedProof] = useState<string | null>(null);

  // Filter and sort proofs
  const sortedProofs = useMemo(() => {
    let result = [...proofs];

    // Filter by quality tier
    if (qualityFilter) {
      result = result.filter((p) => p.quality_tier === qualityFilter);
    }

    // Sort
    result.sort((a, b) => {
      let cmp = 0;
      switch (sortField) {
        case 'coherence':
          cmp = a.coherence_score - b.coherence_score;
          break;
        case 'warrant':
          cmp = a.warrant_strength - b.warrant_strength;
          break;
        case 'backing':
          cmp = a.backing_coverage - b.backing_coverage;
          break;
        case 'rebuttals':
          cmp = a.rebuttal_count - b.rebuttal_count;
          break;
      }
      return sortDir === 'asc' ? cmp : -cmp;
    });

    return result;
  }, [proofs, qualityFilter, sortField, sortDir]);

  // Selected proof details (used for future enhancement)
  const _selectedProof = useMemo(() => {
    if (!expandedProof) return null;
    return proofs.find((p) => p.node_id === expandedProof);
  }, [proofs, expandedProof]);
  void _selectedProof; // Mark as intentionally unused for now

  // Handle proof click
  const handleProofClick = useCallback(
    (nodeId: string) => {
      setExpandedProof(nodeId === expandedProof ? null : nodeId);
      onSelectNode?.(nodeId);
    },
    [expandedProof, onSelectNode]
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
        <span>Loading proof quality...</span>
      </div>
    );
  }

  return (
    <div className="zero-seed-panel proof-dashboard">
      {/* Header */}
      <header className="zero-seed-panel__header">
        <h2 className="zero-seed-panel__title">
          Proof Quality Dashboard
          <span className="zero-seed-panel__subtitle">L3-L4 Justification Layer</span>
        </h2>
        <div className="zero-seed-panel__stats">
          <span className="stat stat--coherence">
            {(averageCoherence * 100).toFixed(1)}% avg coherence
          </span>
          <span className="stat stat--count">{proofs.length} proofs</span>
        </div>
      </header>

      {/* Quality tier summary */}
      <div className="proof-dashboard__tier-summary">
        <button
          className={`tier-btn ${qualityFilter === null ? 'tier-btn--active' : ''}`}
          onClick={() => setQualityFilter(null)}
        >
          All ({proofs.length})
        </button>
        <button
          className={`tier-btn tier-btn--strong ${qualityFilter === 'strong' ? 'tier-btn--active' : ''}`}
          onClick={() => setQualityFilter('strong')}
        >
          Strong ({byQualityTier.strong ?? 0})
        </button>
        <button
          className={`tier-btn tier-btn--moderate ${qualityFilter === 'moderate' ? 'tier-btn--active' : ''}`}
          onClick={() => setQualityFilter('moderate')}
        >
          Moderate ({byQualityTier.moderate ?? 0})
        </button>
        <button
          className={`tier-btn tier-btn--weak ${qualityFilter === 'weak' ? 'tier-btn--active' : ''}`}
          onClick={() => setQualityFilter('weak')}
        >
          Weak ({byQualityTier.weak ?? 0})
        </button>
      </div>

      {/* View mode toggle */}
      <div className="proof-dashboard__controls">
        <div className="view-toggle">
          <button
            className={viewMode === 'grid' ? 'active' : ''}
            onClick={() => setViewMode('grid')}
            title="Grid view"
          >
            Grid
          </button>
          <button
            className={viewMode === 'list' ? 'active' : ''}
            onClick={() => setViewMode('list')}
            title="List view"
          >
            List
          </button>
          <button
            className={viewMode === 'toulmin' ? 'active' : ''}
            onClick={() => setViewMode('toulmin')}
            title="Toulmin view"
          >
            Toulmin
          </button>
        </div>

        <div className="sort-controls">
          <span>Sort:</span>
          <button
            className={sortField === 'coherence' ? 'active' : ''}
            onClick={() => handleSort('coherence')}
          >
            Coherence {sortField === 'coherence' && (sortDir === 'asc' ? '\u25B2' : '\u25BC')}
          </button>
          <button
            className={sortField === 'warrant' ? 'active' : ''}
            onClick={() => handleSort('warrant')}
          >
            Warrant {sortField === 'warrant' && (sortDir === 'asc' ? '\u25B2' : '\u25BC')}
          </button>
          <button
            className={sortField === 'rebuttals' ? 'active' : ''}
            onClick={() => handleSort('rebuttals')}
          >
            Rebuttals {sortField === 'rebuttals' && (sortDir === 'asc' ? '\u25B2' : '\u25BC')}
          </button>
        </div>
      </div>

      {/* Needs improvement banner */}
      {needsImprovement.length > 0 && (
        <div className="proof-dashboard__warning">
          <strong>{needsImprovement.length} proofs need improvement</strong>
          <span>Click to view weak proofs with suggested actions</span>
        </div>
      )}

      {/* Proof grid/list */}
      <div className={`proof-dashboard__content proof-dashboard__content--${viewMode}`}>
        {sortedProofs.length === 0 ? (
          <div className="proof-dashboard__empty">
            No proofs match the current filter
          </div>
        ) : (
          sortedProofs.map((pq) => {
            const isExpanded = expandedProof === pq.node_id;
            const isSelected = selectedNode === pq.node_id;
            const needsWork = needsImprovement.includes(pq.node_id);

            return (
              <div
                key={pq.node_id}
                className={`proof-card ${isExpanded ? 'proof-card--expanded' : ''} ${isSelected ? 'proof-card--selected' : ''} ${needsWork ? 'proof-card--needs-work' : ''}`}
                onClick={() => handleProofClick(pq.node_id)}
              >
                {/* Summary row */}
                <div className="proof-card__summary">
                  <div className="proof-card__info">
                    <span
                      className="proof-card__quality-badge"
                      style={{
                        '--badge-color': getQualityColor(pq.quality_tier),
                      } as React.CSSProperties}
                    >
                      {pq.quality_tier}
                    </span>
                    <span className="proof-card__id">{pq.node_id}</span>
                    {needsWork && <span className="proof-card__needs-work-badge">!</span>}
                  </div>

                  <div className="proof-card__metrics">
                    <div className="metric">
                      <span className="metric__label">Coherence</span>
                      <span className="metric__value">
                        {(pq.coherence_score * 100).toFixed(0)}%
                      </span>
                    </div>
                    <div className="metric">
                      <span className="metric__label">Warrant</span>
                      <span className="metric__value">
                        {(pq.warrant_strength * 100).toFixed(0)}%
                      </span>
                    </div>
                    <div className="metric">
                      <span className="metric__label">Backing</span>
                      <span className="metric__value">
                        {(pq.backing_coverage * 100).toFixed(0)}%
                      </span>
                    </div>
                    <div className="metric">
                      <span className="metric__label">Rebuttals</span>
                      <span className="metric__value">{pq.rebuttal_count}</span>
                    </div>
                  </div>

                  {/* Preview of claim */}
                  <div className="proof-card__preview">
                    <strong>Claim:</strong> {truncate(pq.proof.claim, 100)}
                  </div>
                </div>

                {/* Expanded: Full Toulmin view */}
                {isExpanded && (
                  <div className="proof-card__details">
                    <ToulminVisualizer
                      proof={pq.proof}
                      coherenceScore={pq.coherence_score}
                    />

                    <GhostAlternatives
                      alternatives={pq.ghost_alternatives}
                      onSelect={(alt) => {
                        console.log('Selected ghost alternative:', alt);
                      }}
                    />
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

export default ProofQualityDashboard;
