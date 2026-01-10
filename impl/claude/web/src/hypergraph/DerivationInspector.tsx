/**
 * DerivationInspector — Side panel showing complete derivation lineage for a K-Block
 *
 * "The proof IS the decision. The derivation IS the lineage."
 *
 * Displays:
 * - Full derivation path from Constitution to current K-Block
 * - Path loss indicators showing coherence degradation
 * - Witnesses (principles, specs, tests) that ground this K-Block
 * - Downstream impact (K-Blocks that derive from this one)
 *
 * Philosophy:
 *   Every K-Block exists in a web of derivations.
 *   Understanding the path from axiom to implementation
 *   reveals the "why" behind every "what."
 */

import React, { memo, useState, useCallback, useEffect } from 'react';

import './DerivationInspector.css';

// =============================================================================
// Types
// =============================================================================

/**
 * A node in the derivation path from Constitution to target.
 */
export interface DerivationNode {
  /** Unique identifier for this node */
  id: string;
  /** Display label (filename, principle name, etc.) */
  label: string;
  /** Zero Seed layer (1-7), or undefined for non-layer nodes */
  layer?: 1 | 2 | 3 | 4 | 5 | 6 | 7;
  /** Node kind (axiom, principle, spec, impl, test, etc.) */
  kind: 'constitution' | 'principle' | 'spec' | 'implementation' | 'test' | 'other';
  /** Reasoning/justification connecting to next node */
  reasoning?: string;
  /** Cumulative path loss at this node (0 = perfect coherence) */
  pathLoss: number;
}

/**
 * A witness that grounds the K-Block.
 */
export interface Witness {
  /** Witness type */
  type: 'principle' | 'spec' | 'test' | 'mark' | 'proof';
  /** Display label */
  label: string;
  /** Reference path/ID */
  reference: string;
  /** Section within the reference (if applicable) */
  section?: string;
  /** Confidence score (0-1) */
  confidence?: number;
  /** Additional details */
  details?: string;
}

/**
 * A K-Block that derives from the current K-Block.
 */
export interface DownstreamKBlock {
  /** K-Block ID */
  id: string;
  /** Display label (usually filename) */
  label: string;
  /** Path loss from current K-Block to this one */
  pathLoss: number;
  /** Number of nested downstream K-Blocks */
  childCount?: number;
}

/**
 * Props for DerivationInspector.
 */
export interface DerivationInspectorProps {
  /** ID of the K-Block being inspected */
  kblockId: string;
  /** Derivation path from Constitution to this K-Block */
  derivationPath: DerivationNode[];
  /** Witnesses that ground this K-Block */
  witnesses: Witness[];
  /** K-Blocks that derive from this one */
  downstream: DownstreamKBlock[];
  /** Close handler */
  onClose: () => void;
  /** Trigger re-derivation */
  onRederive: () => void;
  /** Open proof explorer */
  onViewProof: () => void;
  /** Navigate to a different K-Block */
  onNavigate: (kblockId: string) => void;
  /** Panel open state (for animation) */
  isOpen?: boolean;
  /** Loading state */
  loading?: boolean;
}

// =============================================================================
// Constants
// =============================================================================

const KIND_ICONS: Record<DerivationNode['kind'], string> = {
  constitution: '📜',
  principle: '💎',
  spec: '📋',
  implementation: '⚙️',
  test: '🧪',
  other: '◈',
};

// Reserved for future use (e.g., tooltips, accessibility labels)
const _KIND_LABELS: Record<DerivationNode['kind'], string> = {
  constitution: 'Constitution',
  principle: 'Principle',
  spec: 'Specification',
  implementation: 'Implementation',
  test: 'Test',
  other: 'Node',
};

const WITNESS_ICONS: Record<Witness['type'], string> = {
  principle: '💎',
  spec: '📋',
  test: '🧪',
  mark: '⊛',
  proof: '✓',
};

// =============================================================================
// Sub-components
// =============================================================================

interface PathNodeProps {
  node: DerivationNode;
  isLast: boolean;
  isCurrent: boolean;
  onNavigate: (id: string) => void;
}

const PathNode = memo(function PathNode({ node, isLast, isCurrent, onNavigate }: PathNodeProps) {
  const lossPercent = Math.round(node.pathLoss * 100);
  const coherencePercent = 100 - lossPercent;

  return (
    <div className={`derivation-path__node ${isCurrent ? 'derivation-path__node--current' : ''}`}>
      {/* Node content */}
      <button
        className="derivation-path__node-button"
        onClick={() => onNavigate(node.id)}
        title={`Navigate to ${node.label}`}
        disabled={isCurrent}
      >
        <span className="derivation-path__node-icon">{KIND_ICONS[node.kind]}</span>
        <span className="derivation-path__node-label">{node.label}</span>
        {isCurrent && (
          <span className="derivation-path__current-marker" title="You are here">
            ◀
          </span>
        )}
      </button>

      {/* Connection to next node */}
      {!isLast && (
        <div className="derivation-path__connection">
          {node.reasoning && (
            <span className="derivation-path__reasoning" title={node.reasoning}>
              "{truncateReasoning(node.reasoning)}"
            </span>
          )}
          <span
            className="derivation-path__loss"
            title={`Path loss: ${lossPercent}% (${coherencePercent}% coherent)`}
          >
            L={node.pathLoss.toFixed(2)}
          </span>
          <span className="derivation-path__arrow">▼</span>
        </div>
      )}
    </div>
  );
});

interface WitnessItemProps {
  witness: Witness;
  expanded: boolean;
  onToggle: () => void;
}

const WitnessItem = memo(function WitnessItem({ witness, expanded, onToggle }: WitnessItemProps) {
  return (
    <div className={`witness-item witness-item--${witness.type}`}>
      <button className="witness-item__header" onClick={onToggle} aria-expanded={expanded}>
        <span className="witness-item__icon">{WITNESS_ICONS[witness.type]}</span>
        <span className="witness-item__type">{witness.type}</span>
        <span className="witness-item__label">{witness.label}</span>
        {witness.confidence !== undefined && (
          <span
            className="witness-item__confidence"
            title={`Confidence: ${Math.round(witness.confidence * 100)}%`}
          >
            {Math.round(witness.confidence * 100)}%
          </span>
        )}
        <span className="witness-item__toggle">{expanded ? '−' : '+'}</span>
      </button>
      {expanded && (
        <div className="witness-item__details">
          <div className="witness-item__reference">
            <span className="witness-item__detail-label">Reference:</span>
            <span className="witness-item__detail-value">{witness.reference}</span>
          </div>
          {witness.section && (
            <div className="witness-item__section">
              <span className="witness-item__detail-label">Section:</span>
              <span className="witness-item__detail-value">{witness.section}</span>
            </div>
          )}
          {witness.details && <div className="witness-item__extra">{witness.details}</div>}
        </div>
      )}
    </div>
  );
});

interface DownstreamTreeProps {
  items: DownstreamKBlock[];
  onNavigate: (id: string) => void;
  expanded: boolean;
  onToggle: () => void;
}

const DownstreamTree = memo(function DownstreamTree({
  items,
  onNavigate,
  expanded,
  onToggle,
}: DownstreamTreeProps) {
  const visibleItems = expanded ? items : items.slice(0, 3);
  const hasMore = items.length > 3;

  return (
    <div className="downstream-tree">
      <div className="downstream-tree__list">
        {visibleItems.map((item, index) => (
          <div key={item.id} className="downstream-tree__item">
            <span className="downstream-tree__branch">
              {index === visibleItems.length - 1 && !hasMore ? '└── ' : '├── '}
            </span>
            <button
              className="downstream-tree__link"
              onClick={() => onNavigate(item.id)}
              title={`Navigate to ${item.label}`}
            >
              {item.label}
            </button>
            <span
              className="downstream-tree__loss"
              title={`Path loss: ${Math.round(item.pathLoss * 100)}%`}
            >
              (L={item.pathLoss.toFixed(2)})
            </span>
            {item.childCount !== undefined && item.childCount > 0 && (
              <span
                className="downstream-tree__children"
                title={`${item.childCount} nested dependencies`}
              >
                +{item.childCount}
              </span>
            )}
          </div>
        ))}
      </div>
      {hasMore && (
        <button className="downstream-tree__more" onClick={onToggle}>
          {expanded ? '↑ Show less' : `↓ ${items.length - 3} more...`}
        </button>
      )}
    </div>
  );
});

interface CoherenceSummaryProps {
  totalLoss: number;
}

const CoherenceSummary = memo(function CoherenceSummary({ totalLoss }: CoherenceSummaryProps) {
  const coherencePercent = Math.round((1 - totalLoss) * 100);
  const lossPercent = Math.round(totalLoss * 100);

  const getCoherenceClass = () => {
    if (coherencePercent >= 80) return 'coherence-summary--high';
    if (coherencePercent >= 60) return 'coherence-summary--medium';
    return 'coherence-summary--low';
  };

  return (
    <div className={`coherence-summary ${getCoherenceClass()}`}>
      <div className="coherence-summary__bar">
        <div className="coherence-summary__fill" style={{ width: `${coherencePercent}%` }} />
      </div>
      <div className="coherence-summary__text">
        <span className="coherence-summary__label">TOTAL PATH LOSS:</span>
        <span className="coherence-summary__value">{lossPercent.toFixed(0)}%</span>
        <span className="coherence-summary__coherent">({coherencePercent}% coherent)</span>
      </div>
    </div>
  );
});

// =============================================================================
// Main Component
// =============================================================================

export const DerivationInspector = memo(function DerivationInspector({
  kblockId,
  derivationPath,
  witnesses,
  downstream,
  onClose,
  onRederive,
  onViewProof,
  onNavigate,
  isOpen = true,
  loading = false,
}: DerivationInspectorProps) {
  // Track expanded witnesses
  const [expandedWitnesses, setExpandedWitnesses] = useState<Set<number>>(new Set());
  const [downstreamExpanded, setDownstreamExpanded] = useState(false);

  // Toggle witness expansion
  const toggleWitness = useCallback((index: number) => {
    setExpandedWitnesses((prev) => {
      const next = new Set(prev);
      if (next.has(index)) {
        next.delete(index);
      } else {
        next.add(index);
      }
      return next;
    });
  }, []);

  // Toggle downstream expansion
  const toggleDownstream = useCallback(() => {
    setDownstreamExpanded((prev) => !prev);
  }, []);

  // Calculate total path loss
  const totalPathLoss =
    derivationPath.length > 0 ? derivationPath[derivationPath.length - 1].pathLoss : 0;

  // Extract current node label for header
  const currentLabel =
    derivationPath.length > 0 ? derivationPath[derivationPath.length - 1].label : kblockId;

  // Find current node index
  const currentIndex = derivationPath.length - 1;

  // Handle keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (!isOpen) return;

      if (e.key === 'Escape') {
        e.preventDefault();
        onClose();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  return (
    <aside
      className={`derivation-inspector ${isOpen ? 'derivation-inspector--open' : 'derivation-inspector--closed'}`}
      aria-label="Derivation inspector panel"
    >
      {/* Header */}
      <header className="derivation-inspector__header">
        <div className="derivation-inspector__title">
          <span className="derivation-inspector__icon">📜</span>
          <span className="derivation-inspector__title-text">DERIVATION PATH</span>
        </div>
        <div className="derivation-inspector__target">{currentLabel}</div>
        <button
          className="derivation-inspector__close"
          onClick={onClose}
          aria-label="Close derivation inspector"
          title="Close (Esc)"
        >
          ✕
        </button>
      </header>

      {/* Loading overlay */}
      {loading && (
        <div className="derivation-inspector__loading">
          <span className="derivation-inspector__spinner" />
          <span>Tracing derivation...</span>
        </div>
      )}

      {/* Content */}
      <div className="derivation-inspector__content">
        {/* Derivation Path */}
        <section className="derivation-inspector__section">
          <div className="derivation-path">
            {derivationPath.map((node, index) => (
              <PathNode
                key={node.id}
                node={node}
                isLast={index === derivationPath.length - 1}
                isCurrent={index === currentIndex}
                onNavigate={onNavigate}
              />
            ))}
          </div>
        </section>

        {/* Coherence Summary */}
        <section className="derivation-inspector__section derivation-inspector__section--summary">
          <CoherenceSummary totalLoss={totalPathLoss} />
        </section>

        {/* Witnesses */}
        {witnesses.length > 0 && (
          <section className="derivation-inspector__section">
            <h3 className="derivation-inspector__section-title">WITNESSES</h3>
            <div className="derivation-inspector__witnesses">
              {witnesses.map((witness, index) => (
                <WitnessItem
                  key={`${witness.type}-${witness.reference}-${index}`}
                  witness={witness}
                  expanded={expandedWitnesses.has(index)}
                  onToggle={() => toggleWitness(index)}
                />
              ))}
            </div>
          </section>
        )}

        {/* Downstream Impact */}
        {downstream.length > 0 && (
          <section className="derivation-inspector__section">
            <h3 className="derivation-inspector__section-title">
              DOWNSTREAM IMPACT
              <span className="derivation-inspector__count">{downstream.length} K-Blocks</span>
            </h3>
            <DownstreamTree
              items={downstream}
              onNavigate={onNavigate}
              expanded={downstreamExpanded}
              onToggle={toggleDownstream}
            />
          </section>
        )}

        {/* Empty state */}
        {derivationPath.length === 0 &&
          witnesses.length === 0 &&
          downstream.length === 0 &&
          !loading && (
            <div className="derivation-inspector__empty">
              <span className="derivation-inspector__empty-icon">⊘</span>
              <span className="derivation-inspector__empty-text">No derivation data available</span>
            </div>
          )}
      </div>

      {/* Footer Actions */}
      <footer className="derivation-inspector__footer">
        <button
          className="derivation-inspector__action btn-base btn-secondary btn-sm"
          onClick={onRederive}
          disabled={loading}
          title="Re-trace derivation path"
        >
          Re-derive
        </button>
        <button
          className="derivation-inspector__action btn-base btn-secondary btn-sm"
          onClick={onViewProof}
          disabled={loading}
          title="Open proof explorer"
        >
          View Proof
        </button>
        <button
          className="derivation-inspector__action btn-base btn-ghost btn-sm"
          onClick={() => onNavigate(derivationPath[0]?.id)}
          disabled={loading || derivationPath.length === 0}
          title="Navigate to Constitution root"
        >
          View Full Graph
        </button>
      </footer>
    </aside>
  );
});

// =============================================================================
// Helpers
// =============================================================================

/**
 * Truncate reasoning text for inline display.
 */
function truncateReasoning(text: string, maxLength: number = 40): string {
  if (text.length <= maxLength) return text;
  return text.slice(0, maxLength - 3) + '...';
}

export default DerivationInspector;
