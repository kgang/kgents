/**
 * ProofPanel — Collapsible side panel showing K-Block proof structure
 *
 * Displays:
 * - Zero Seed layer (L1-L7) with semantic meaning
 * - Confidence score with visual indicator
 * - Toulmin proof structure (data, warrant, claim, backing, qualifier, rebuttals)
 * - Lineage navigation (parent/child blocks)
 *
 * Philosophy: "The proof IS the decision. The derivation IS the lineage."
 */

import { memo, useState } from 'react';
import type { ToulminProof } from './useKBlock';
import './ProofPanel.css';

// =============================================================================
// Types
// =============================================================================

export interface ProofPanelProps {
  /** Zero Seed layer (1-7) */
  layer?: 1 | 2 | 3 | 4 | 5 | 6 | 7;
  /** Zero Seed node kind */
  kind?: string;
  /** Confidence score (0-1) */
  confidence: number;
  /** Whether this K-Block has a proof */
  hasProof: boolean;
  /** Toulmin proof structure */
  proof?: ToulminProof | null;
  /** Lineage (ancestor IDs) */
  lineage: string[];
  /** Parent block IDs */
  parentBlocks: string[];
  /** Child block IDs */
  childBlocks: string[];
  /** Navigate to a block */
  onNavigate?: (blockId: string) => void;
  /** Panel open state */
  isOpen: boolean;
  /** Toggle panel */
  onToggle: () => void;
}

// =============================================================================
// Constants
// =============================================================================

const LAYER_INFO: Record<number, { name: string; color: string; description: string }> = {
  1: { name: 'Axiom', color: 'var(--color-axiom)', description: 'Self-evident truths, foundational assumptions' },
  2: { name: 'Value', color: 'var(--color-value)', description: 'Core principles, ethical commitments' },
  3: { name: 'Goal', color: 'var(--color-goal)', description: 'Desired outcomes, objectives' },
  4: { name: 'Spec', color: 'var(--color-spec)', description: 'Specifications, requirements, contracts' },
  5: { name: 'Action', color: 'var(--color-action)', description: 'Concrete implementations, executable steps' },
  6: { name: 'Reflection', color: 'var(--color-reflection)', description: 'Meta-level observations, learnings' },
  7: { name: 'Representation', color: 'var(--color-representation)', description: 'Views, projections, artifacts' },
};

// =============================================================================
// Sub-components
// =============================================================================

interface LayerBadgeProps {
  layer: number;
  kind?: string;
}

const LayerBadge = memo(function LayerBadge({ layer, kind }: LayerBadgeProps) {
  const info = LAYER_INFO[layer];
  if (!info) return null;

  return (
    <div
      className="proof-panel__layer-badge"
      style={{ '--layer-color': info.color } as React.CSSProperties}
    >
      <span className="proof-panel__layer-number">L{layer}</span>
      <span className="proof-panel__layer-name">{kind || info.name}</span>
    </div>
  );
});

interface ConfidenceBarProps {
  confidence: number;
}

const ConfidenceBar = memo(function ConfidenceBar({ confidence }: ConfidenceBarProps) {
  const percentage = Math.round(confidence * 100);
  const getColor = () => {
    if (confidence >= 0.8) return 'var(--color-confidence-high)';
    if (confidence >= 0.5) return 'var(--color-confidence-medium)';
    return 'var(--color-confidence-low)';
  };

  return (
    <div className="proof-panel__confidence">
      <div className="proof-panel__confidence-label">
        Confidence: <strong>{percentage}%</strong>
      </div>
      <div className="proof-panel__confidence-bar">
        <div
          className="proof-panel__confidence-fill"
          style={{
            width: `${percentage}%`,
            backgroundColor: getColor(),
          }}
        />
      </div>
    </div>
  );
});

interface ToulminSectionProps {
  proof: ToulminProof;
}

const ToulminSection = memo(function ToulminSection({ proof }: ToulminSectionProps) {
  const [expanded, setExpanded] = useState<Record<string, boolean>>({
    claim: true,
    data: false,
    warrant: false,
    backing: false,
    qualifier: false,
    rebuttals: false,
  });

  const toggle = (key: string) => {
    setExpanded((prev) => ({ ...prev, [key]: !prev[key] }));
  };

  return (
    <div className="proof-panel__toulmin">
      <h4 className="proof-panel__section-title">Toulmin Structure</h4>

      {/* Claim - always visible */}
      <div className="proof-panel__toulmin-item proof-panel__toulmin-item--claim">
        <button
          className="proof-panel__toulmin-header"
          onClick={() => toggle('claim')}
          aria-expanded={expanded.claim}
        >
          <span className="proof-panel__toulmin-icon">◆</span>
          <span className="proof-panel__toulmin-label">Claim</span>
          <span className="proof-panel__toulmin-toggle">{expanded.claim ? '−' : '+'}</span>
        </button>
        {expanded.claim && (
          <div className="proof-panel__toulmin-content">{proof.claim}</div>
        )}
      </div>

      {/* Data */}
      {proof.data && (
        <div className="proof-panel__toulmin-item">
          <button
            className="proof-panel__toulmin-header"
            onClick={() => toggle('data')}
            aria-expanded={expanded.data}
          >
            <span className="proof-panel__toulmin-icon">◇</span>
            <span className="proof-panel__toulmin-label">Data</span>
            <span className="proof-panel__toulmin-toggle">{expanded.data ? '−' : '+'}</span>
          </button>
          {expanded.data && (
            <div className="proof-panel__toulmin-content">{proof.data}</div>
          )}
        </div>
      )}

      {/* Warrant */}
      {proof.warrant && (
        <div className="proof-panel__toulmin-item">
          <button
            className="proof-panel__toulmin-header"
            onClick={() => toggle('warrant')}
            aria-expanded={expanded.warrant}
          >
            <span className="proof-panel__toulmin-icon">→</span>
            <span className="proof-panel__toulmin-label">Warrant</span>
            <span className="proof-panel__toulmin-toggle">{expanded.warrant ? '−' : '+'}</span>
          </button>
          {expanded.warrant && (
            <div className="proof-panel__toulmin-content">{proof.warrant}</div>
          )}
        </div>
      )}

      {/* Backing */}
      {proof.backing && (
        <div className="proof-panel__toulmin-item">
          <button
            className="proof-panel__toulmin-header"
            onClick={() => toggle('backing')}
            aria-expanded={expanded.backing}
          >
            <span className="proof-panel__toulmin-icon">⬒</span>
            <span className="proof-panel__toulmin-label">Backing</span>
            <span className="proof-panel__toulmin-toggle">{expanded.backing ? '−' : '+'}</span>
          </button>
          {expanded.backing && (
            <div className="proof-panel__toulmin-content">{proof.backing}</div>
          )}
        </div>
      )}

      {/* Qualifier */}
      {proof.qualifier && (
        <div className="proof-panel__toulmin-item">
          <button
            className="proof-panel__toulmin-header"
            onClick={() => toggle('qualifier')}
            aria-expanded={expanded.qualifier}
          >
            <span className="proof-panel__toulmin-icon">≈</span>
            <span className="proof-panel__toulmin-label">Qualifier</span>
            <span className="proof-panel__toulmin-toggle">{expanded.qualifier ? '−' : '+'}</span>
          </button>
          {expanded.qualifier && (
            <div className="proof-panel__toulmin-content">{proof.qualifier}</div>
          )}
        </div>
      )}

      {/* Rebuttals */}
      {proof.rebuttals && proof.rebuttals.length > 0 && (
        <div className="proof-panel__toulmin-item proof-panel__toulmin-item--rebuttals">
          <button
            className="proof-panel__toulmin-header"
            onClick={() => toggle('rebuttals')}
            aria-expanded={expanded.rebuttals}
          >
            <span className="proof-panel__toulmin-icon">△</span>
            <span className="proof-panel__toulmin-label">
              Rebuttals ({proof.rebuttals.length})
            </span>
            <span className="proof-panel__toulmin-toggle">{expanded.rebuttals ? '−' : '+'}</span>
          </button>
          {expanded.rebuttals && (
            <ul className="proof-panel__toulmin-rebuttals">
              {proof.rebuttals.map((rebuttal: string, i: number) => (
                <li key={i} className="proof-panel__toulmin-rebuttal">{rebuttal}</li>
              ))}
            </ul>
          )}
        </div>
      )}
    </div>
  );
});

interface LineageNavigationProps {
  parentBlocks: string[];
  childBlocks: string[];
  lineage: string[];
  onNavigate?: (blockId: string) => void;
}

const LineageNavigation = memo(function LineageNavigation({
  parentBlocks,
  childBlocks,
  lineage,
  onNavigate,
}: LineageNavigationProps) {
  const truncateId = (id: string) => {
    if (id.length <= 12) return id;
    return id.slice(0, 6) + '…' + id.slice(-4);
  };

  return (
    <div className="proof-panel__lineage">
      <h4 className="proof-panel__section-title">Derivation Graph</h4>

      {/* Parents (direct) */}
      {parentBlocks.length > 0 && (
        <div className="proof-panel__lineage-section">
          <span className="proof-panel__lineage-label">↑ Parents</span>
          <div className="proof-panel__lineage-list">
            {parentBlocks.map((id) => (
              <button
                key={id}
                className="proof-panel__lineage-link"
                onClick={() => onNavigate?.(id)}
                title={id}
              >
                {truncateId(id)}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Children (direct) */}
      {childBlocks.length > 0 && (
        <div className="proof-panel__lineage-section">
          <span className="proof-panel__lineage-label">↓ Children</span>
          <div className="proof-panel__lineage-list">
            {childBlocks.map((id) => (
              <button
                key={id}
                className="proof-panel__lineage-link"
                onClick={() => onNavigate?.(id)}
                title={id}
              >
                {truncateId(id)}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Full lineage (ancestors) */}
      {lineage.length > 0 && (
        <div className="proof-panel__lineage-section proof-panel__lineage-section--ancestors">
          <span className="proof-panel__lineage-label">⤴ Ancestors ({lineage.length})</span>
          <div className="proof-panel__lineage-list proof-panel__lineage-list--compact">
            {lineage.slice(0, 5).map((id) => (
              <button
                key={id}
                className="proof-panel__lineage-link proof-panel__lineage-link--small"
                onClick={() => onNavigate?.(id)}
                title={id}
              >
                {truncateId(id)}
              </button>
            ))}
            {lineage.length > 5 && (
              <span className="proof-panel__lineage-more">+{lineage.length - 5} more</span>
            )}
          </div>
        </div>
      )}

      {parentBlocks.length === 0 && childBlocks.length === 0 && lineage.length === 0 && (
        <div className="proof-panel__lineage-empty">
          No derivation relationships
        </div>
      )}
    </div>
  );
});

// =============================================================================
// Main Component
// =============================================================================

export const ProofPanel = memo(function ProofPanel({
  layer,
  kind,
  confidence,
  hasProof,
  proof,
  lineage,
  parentBlocks,
  childBlocks,
  onNavigate,
  isOpen,
  onToggle,
}: ProofPanelProps) {
  return (
    <aside
      className={`proof-panel ${isOpen ? 'proof-panel--open' : 'proof-panel--closed'}`}
      aria-label="Proof structure panel"
    >
      {/* Toggle button */}
      <button
        className="proof-panel__toggle"
        onClick={onToggle}
        aria-expanded={isOpen}
        aria-label={isOpen ? 'Close proof panel' : 'Open proof panel'}
        title={isOpen ? 'Close proof panel (gp)' : 'Open proof panel (gp)'}
      >
        <span className="proof-panel__toggle-icon">{isOpen ? '◂' : '▸'}</span>
        <span className="proof-panel__toggle-label">Proof</span>
      </button>

      {/* Panel content */}
      {isOpen && (
        <div className="proof-panel__content">
          {/* Header with layer and status */}
          <div className="proof-panel__header">
            {layer && <LayerBadge layer={layer} kind={kind} />}
            <div className="proof-panel__status">
              {hasProof ? (
                <span className="proof-panel__status-badge proof-panel__status-badge--proven">
                  ✓ Proven
                </span>
              ) : (
                <span className="proof-panel__status-badge proof-panel__status-badge--unproven">
                  ○ Unproven
                </span>
              )}
            </div>
          </div>

          {/* Confidence */}
          <ConfidenceBar confidence={confidence} />

          {/* Layer description */}
          {layer && (
            <div className="proof-panel__layer-description">
              {LAYER_INFO[layer]?.description}
            </div>
          )}

          {/* Toulmin proof structure */}
          {hasProof && proof && <ToulminSection proof={proof} />}

          {/* Lineage navigation */}
          <LineageNavigation
            parentBlocks={parentBlocks}
            childBlocks={childBlocks}
            lineage={lineage}
            onNavigate={onNavigate}
          />
        </div>
      )}
    </aside>
  );
});

export default ProofPanel;
