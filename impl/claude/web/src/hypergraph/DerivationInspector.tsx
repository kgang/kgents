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

import React, { memo, useState, useCallback, useEffect, useMemo } from 'react';

import { useLoss, useLossBatch, lossToColor, LossSignature } from '../hooks/useLoss';
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
  /** Witnesses attached to this derivation step */
  witnesses?: Array<{ type: WitnessType; confidence: number }>;
}

/**
 * Witness type enumeration with categorical semantics.
 */
export type WitnessType =
  | 'COMPOSITION'
  | 'GALOIS'
  | 'PRINCIPLE'
  | 'EMPIRICAL'
  | 'AESTHETIC'
  | 'SOMATIC';

/**
 * A witness that grounds the K-Block.
 */
export interface Witness {
  /** Witness type (categorical witness taxonomy) */
  type: WitnessType;
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
  /** Handler for clicking on a witness */
  onWitnessClick?: (witness: Witness) => void;
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

/**
 * Witness type icons and colors for categorical witness taxonomy.
 */
const WITNESS_CONFIG: Record<
  WitnessType,
  { icon: string; color: string; bgColor: string; label: string }
> = {
  COMPOSITION: {
    icon: '🔗',
    color: '#06b6d4', // cyan-500
    bgColor: 'rgba(6, 182, 212, 0.15)',
    label: 'Composition',
  },
  GALOIS: {
    icon: '📐',
    color: '#a855f7', // purple-500
    bgColor: 'rgba(168, 85, 247, 0.15)',
    label: 'Galois Connection',
  },
  PRINCIPLE: {
    icon: '💎',
    color: '#3b82f6', // blue-500
    bgColor: 'rgba(59, 130, 246, 0.15)',
    label: 'Principle',
  },
  EMPIRICAL: {
    icon: '🧪',
    color: '#f59e0b', // amber-500
    bgColor: 'rgba(245, 158, 11, 0.15)',
    label: 'Empirical',
  },
  AESTHETIC: {
    icon: '🎨',
    color: '#ec4899', // pink-500
    bgColor: 'rgba(236, 72, 153, 0.15)',
    label: 'Aesthetic',
  },
  SOMATIC: {
    icon: '💜',
    color: '#a855f7', // purple-500 (magenta-ish)
    bgColor: 'rgba(168, 85, 247, 0.15)',
    label: 'Somatic',
  },
};

// =============================================================================
// Sub-components
// =============================================================================

interface PathNodeProps {
  node: DerivationNode;
  isLast: boolean;
  isCurrent: boolean;
  onNavigate: (id: string) => void;
  onWitnessClick?: (nodeId: string) => void;
  /** Real-time loss signature from useLoss hook */
  lossSignature?: LossSignature | null;
  /** Whether loss data is loading */
  lossLoading?: boolean;
}

/**
 * InlineWitnessBadges - Shows small witness indicators on path nodes
 */
const InlineWitnessBadges = memo(function InlineWitnessBadges({
  witnesses,
  onClick,
}: {
  witnesses: Array<{ type: WitnessType; confidence: number }>;
  onClick?: () => void;
}) {
  if (!witnesses || witnesses.length === 0) return null;

  // Group by type and show max 3 icons
  const uniqueTypes = [...new Set(witnesses.map((w) => w.type))].slice(0, 3);
  const avgConfidence = witnesses.reduce((sum, w) => sum + w.confidence, 0) / witnesses.length;

  return (
    <button
      className="derivation-path__witnesses"
      onClick={(e) => {
        e.stopPropagation();
        onClick?.();
      }}
      title={`${witnesses.length} witness${witnesses.length !== 1 ? 'es' : ''} (avg ${Math.round(avgConfidence * 100)}% confidence)`}
    >
      <span className="derivation-path__witness-icons">
        {uniqueTypes.map((type) => (
          <span
            key={type}
            className="derivation-path__witness-icon"
            style={{ '--witness-color': WITNESS_CONFIG[type].color } as React.CSSProperties}
          >
            {WITNESS_CONFIG[type].icon}
          </span>
        ))}
      </span>
      <span className="derivation-path__witness-count">{witnesses.length}w</span>
    </button>
  );
});

const PathNode = memo(function PathNode({
  node,
  isLast,
  isCurrent,
  onNavigate,
  onWitnessClick,
  lossSignature,
  lossLoading,
}: PathNodeProps) {
  // Use real-time loss if available, otherwise fall back to static value
  const effectiveLoss = lossSignature?.total ?? node.pathLoss;
  const lossPercent = Math.round(effectiveLoss * 100);
  const coherencePercent = 100 - lossPercent;
  const isAxiomatic = lossSignature?.isAxiomatic ?? effectiveLoss < 0.01;

  // Get color based on loss for visual gradient
  const lossColor = lossToColor(effectiveLoss);

  // Status indicator based on loss thresholds
  const getStatusIndicator = () => {
    if (isAxiomatic) return { icon: '\u2605', color: '#9b59b6', label: 'Axiomatic' }; // Purple star
    if (effectiveLoss < 0.3) return { icon: '\u25CF', color: '#22c55e', label: 'Stable' }; // Green dot
    if (effectiveLoss <= 0.7) return { icon: '\u25CF', color: '#f1c40f', label: 'Transitional' }; // Yellow dot
    return { icon: '\u25CF', color: '#ef4444', label: 'Unstable' }; // Red dot
  };
  const status = getStatusIndicator();

  return (
    <div
      className={`derivation-path__node ${isCurrent ? 'derivation-path__node--current' : ''} ${isAxiomatic ? 'derivation-path__node--axiomatic' : ''}`}
      style={{ '--loss-color': lossColor } as React.CSSProperties}
    >
      {/* Node content */}
      <button
        className="derivation-path__node-button"
        onClick={() => onNavigate(node.id)}
        title={`Navigate to ${node.label}${lossSignature ? `\nLoss: ${lossPercent}%\nStatus: ${status.label}` : ''}`}
        disabled={isCurrent}
      >
        <span className="derivation-path__node-icon">{KIND_ICONS[node.kind]}</span>
        <span className="derivation-path__node-label">{node.label}</span>
        {/* Axiomatic indicator */}
        {isAxiomatic && (
          <span
            className="derivation-path__axiomatic-badge"
            style={{ color: '#9b59b6' }}
            title="Axiomatic fixed-point (loss < 0.01)"
          >
            &#9733;
          </span>
        )}
        {/* Inline witness badges */}
        {node.witnesses && node.witnesses.length > 0 && (
          <InlineWitnessBadges
            witnesses={node.witnesses}
            onClick={() => onWitnessClick?.(node.id)}
          />
        )}
        {isCurrent && (
          <span className="derivation-path__current-marker" title="You are here">
            &#9664;
          </span>
        )}
      </button>

      {/* Connection to next node with loss visualization */}
      {!isLast && (
        <div className="derivation-path__connection">
          {node.reasoning && (
            <span className="derivation-path__reasoning" title={node.reasoning}>
              "{truncateReasoning(node.reasoning)}"
            </span>
          )}
          {/* Loss badge with color gradient */}
          <span
            className={`derivation-path__loss ${lossLoading ? 'derivation-path__loss--loading' : ''}`}
            style={{ color: lossColor, borderColor: lossColor }}
            title={`Path loss: ${lossPercent}% (${coherencePercent}% coherent)${lossSignature ? `\n\nComponents:\n  Content: ${(lossSignature.components.content * 100).toFixed(1)}%\n  Proof: ${(lossSignature.components.proof * 100).toFixed(1)}%\n  Edge: ${(lossSignature.components.edge * 100).toFixed(1)}%\n  Metadata: ${(lossSignature.components.metadata * 100).toFixed(1)}%` : ''}`}
          >
            {lossLoading ? (
              <span className="derivation-path__loss-spinner" />
            ) : (
              <>
                <span className="derivation-path__status-indicator" style={{ color: status.color }}>
                  {status.icon}
                </span>
                L={effectiveLoss.toFixed(2)}
              </>
            )}
          </span>
          <span className="derivation-path__arrow" style={{ color: lossColor }}>
            &#9660;
          </span>
        </div>
      )}

      {/* Loss signature breakdown (shown on current node) */}
      {isCurrent && lossSignature && (
        <div className="derivation-path__loss-breakdown">
          <div className="derivation-path__loss-breakdown-title">Loss Components:</div>
          <div className="derivation-path__loss-breakdown-grid">
            <div className="derivation-path__loss-component">
              <span style={{ color: lossToColor(lossSignature.components.content) }}>Content</span>
              <span className="derivation-path__loss-bar">
                <span
                  className="derivation-path__loss-bar-fill"
                  style={{
                    width: `${lossSignature.components.content * 100}%`,
                    backgroundColor: lossToColor(lossSignature.components.content),
                  }}
                />
              </span>
              <span>{(lossSignature.components.content * 100).toFixed(1)}%</span>
            </div>
            <div className="derivation-path__loss-component">
              <span style={{ color: lossToColor(lossSignature.components.proof) }}>Proof</span>
              <span className="derivation-path__loss-bar">
                <span
                  className="derivation-path__loss-bar-fill"
                  style={{
                    width: `${lossSignature.components.proof * 100}%`,
                    backgroundColor: lossToColor(lossSignature.components.proof),
                  }}
                />
              </span>
              <span>{(lossSignature.components.proof * 100).toFixed(1)}%</span>
            </div>
            <div className="derivation-path__loss-component">
              <span style={{ color: lossToColor(lossSignature.components.edge) }}>Edge</span>
              <span className="derivation-path__loss-bar">
                <span
                  className="derivation-path__loss-bar-fill"
                  style={{
                    width: `${lossSignature.components.edge * 100}%`,
                    backgroundColor: lossToColor(lossSignature.components.edge),
                  }}
                />
              </span>
              <span>{(lossSignature.components.edge * 100).toFixed(1)}%</span>
            </div>
            <div className="derivation-path__loss-component">
              <span style={{ color: lossToColor(lossSignature.components.metadata) }}>
                Metadata
              </span>
              <span className="derivation-path__loss-bar">
                <span
                  className="derivation-path__loss-bar-fill"
                  style={{
                    width: `${lossSignature.components.metadata * 100}%`,
                    backgroundColor: lossToColor(lossSignature.components.metadata),
                  }}
                />
              </span>
              <span>{(lossSignature.components.metadata * 100).toFixed(1)}%</span>
            </div>
          </div>
          <div className="derivation-path__loss-status">
            Status: <span style={{ color: status.color }}>{lossSignature.status}</span>
            {lossSignature.layer && (
              <span className="derivation-path__loss-layer"> | Layer {lossSignature.layer}</span>
            )}
          </div>
        </div>
      )}
    </div>
  );
});

interface WitnessItemProps {
  witness: Witness;
  expanded: boolean;
  onToggle: () => void;
  onClick?: () => void;
}

/**
 * Get confidence level class for styling
 */
function getConfidenceClass(confidence: number): string {
  if (confidence >= 0.8) return 'witness-item__confidence--high';
  if (confidence >= 0.6) return 'witness-item__confidence--medium';
  return 'witness-item__confidence--low';
}

const WitnessItem = memo(function WitnessItem({
  witness,
  expanded,
  onToggle,
  onClick,
}: WitnessItemProps) {
  const config = WITNESS_CONFIG[witness.type];
  const confidenceValue = witness.confidence ?? 0;

  return (
    <div
      className={`witness-item witness-item--${witness.type.toLowerCase()}`}
      style={
        {
          '--witness-color': config.color,
          '--witness-bg': config.bgColor,
        } as React.CSSProperties
      }
    >
      <button
        className="witness-item__header"
        onClick={() => {
          onToggle();
          onClick?.();
        }}
        aria-expanded={expanded}
      >
        <span className="witness-item__icon">{config.icon}</span>
        <span className="witness-item__type" style={{ color: config.color }}>
          {config.label}
        </span>
        <span className="witness-item__label">{witness.label}</span>
        {witness.confidence !== undefined && (
          <span
            className={`witness-item__confidence ${getConfidenceClass(confidenceValue)}`}
            title={`Confidence: ${Math.round(confidenceValue * 100)}%`}
          >
            {Math.round(confidenceValue * 100)}%
          </span>
        )}
        <span className="witness-item__toggle">{expanded ? '−' : '+'}</span>
      </button>
      {expanded && (
        <div className="witness-item__details">
          {/* Confidence bar */}
          <div className="witness-item__confidence-bar">
            <div
              className="witness-item__confidence-fill"
              style={{
                width: `${confidenceValue * 100}%`,
                backgroundColor: config.color,
              }}
            />
          </div>
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
  /** Optional full loss signature for breakdown display */
  lossSignature?: LossSignature | null;
  /** Whether loss is loading */
  loading?: boolean;
}

const CoherenceSummary = memo(function CoherenceSummary({
  totalLoss,
  lossSignature,
  loading,
}: CoherenceSummaryProps) {
  const coherencePercent = Math.round((1 - totalLoss) * 100);
  const lossPercent = Math.round(totalLoss * 100);

  // Use lossToColor for dynamic gradient coloring
  const lossColor = lossToColor(totalLoss);
  const coherenceColor = lossToColor(1 - totalLoss); // Invert for coherence

  const getCoherenceClass = () => {
    if (coherencePercent >= 80) return 'coherence-summary--high';
    if (coherencePercent >= 60) return 'coherence-summary--medium';
    return 'coherence-summary--low';
  };

  // Status based on loss thresholds
  const status =
    totalLoss < 0.01
      ? 'axiomatic'
      : totalLoss < 0.3
        ? 'stable'
        : totalLoss <= 0.7
          ? 'transitional'
          : 'unstable';
  const statusIcon = status === 'axiomatic' ? '\u2605' : '\u25CF';
  const statusColor =
    status === 'axiomatic'
      ? '#9b59b6'
      : status === 'stable'
        ? '#22c55e'
        : status === 'transitional'
          ? '#f1c40f'
          : '#ef4444';

  return (
    <div className={`coherence-summary ${getCoherenceClass()}`}>
      {/* Progress bar with gradient coloring */}
      <div className="coherence-summary__bar">
        <div
          className="coherence-summary__fill"
          style={{
            width: `${coherencePercent}%`,
            background: `linear-gradient(90deg, ${lossToColor(0)} 0%, ${lossToColor(totalLoss / 2)} 50%, ${lossColor} 100%)`,
          }}
        />
      </div>
      <div className="coherence-summary__text">
        <span className="coherence-summary__label">TOTAL PATH LOSS:</span>
        {loading ? (
          <span className="coherence-summary__loading">Loading...</span>
        ) : (
          <>
            <span className="coherence-summary__status" style={{ color: statusColor }}>
              {statusIcon}
            </span>
            <span className="coherence-summary__value" style={{ color: lossColor }}>
              {lossPercent.toFixed(0)}%
            </span>
            <span className="coherence-summary__coherent">({coherencePercent}% coherent)</span>
          </>
        )}
      </div>

      {/* Show status label */}
      <div className="coherence-summary__status-label" style={{ color: statusColor }}>
        {status.charAt(0).toUpperCase() + status.slice(1)}
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
  onWitnessClick,
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

  // ==========================================================================
  // Real-time Loss Integration
  // ==========================================================================

  // Extract node IDs for batch loss fetching
  const nodeIds = useMemo(() => {
    return derivationPath.map((n) => n.id);
  }, [derivationPath]);

  // Fetch real-time loss for all nodes in the derivation path
  const { signatures: lossSignatures, loading: lossLoading } = useLossBatch(nodeIds);

  // Also fetch the current K-Block's loss signature for detailed breakdown
  const { signature: currentLossSignature } = useLoss(kblockId);

  // Calculate total path loss - use real-time data if available
  const totalPathLoss = useMemo(() => {
    if (derivationPath.length === 0) return 0;
    const lastNodeId = derivationPath[derivationPath.length - 1].id;
    const realTimeLoss = lossSignatures.get(lastNodeId);
    return realTimeLoss?.total ?? derivationPath[derivationPath.length - 1].pathLoss;
  }, [derivationPath, lossSignatures]);

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
                onWitnessClick={() => {
                  // When clicking witnesses on a path node, scroll to witnesses section
                  const witnessSection = document.querySelector('.derivation-inspector__witnesses');
                  witnessSection?.scrollIntoView({ behavior: 'smooth', block: 'start' });
                }}
                lossSignature={
                  lossSignatures.get(node.id) ??
                  (index === currentIndex ? currentLossSignature : null)
                }
                lossLoading={lossLoading}
              />
            ))}
          </div>
        </section>

        {/* Coherence Summary */}
        <section className="derivation-inspector__section derivation-inspector__section--summary">
          <CoherenceSummary
            totalLoss={totalPathLoss}
            lossSignature={currentLossSignature}
            loading={lossLoading}
          />
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
                  onClick={() => onWitnessClick?.(witness)}
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
