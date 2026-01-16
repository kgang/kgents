/**
 * AxiomCard - Single axiom display with evidence and actions.
 *
 * Design Goals:
 * - Axioms should feel discovered, not imposed
 * - Evidence-based UI (show why, not just what)
 * - Warmth: "I noticed some patterns worth keeping"
 *
 * Philosophy:
 *   "The persona is a garden, not a museum."
 *   "Daring, bold, creative, opinionated but not gaudy."
 *
 * @see components/constitution/PersonalConstitutionBuilder.tsx
 * @see stores/personalConstitutionStore.ts
 */

import { useState, useCallback, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import type { AxiomCandidate, ConstitutionalAxiom, AxiomLayer } from './types';
import { getLayerLabel, getLayerDescription, getAxiomLayer } from './types';
import { TIMING, GLOW, GREEN, EARTH } from '@/constants';
import './AxiomCard.css';

// =============================================================================
// Types
// =============================================================================

export interface AxiomCardProps {
  /** The axiom to display (either candidate or constitutional) */
  axiom: AxiomCandidate | ConstitutionalAxiom;

  /** Display variant */
  variant?: 'candidate' | 'constitutional' | 'compact';

  /** Whether this card is selected */
  isSelected?: boolean;

  /** Whether this card is expanded to show details */
  isExpanded?: boolean;

  /** Callback when card is clicked */
  onClick?: () => void;

  /** Callback when expanded state changes */
  onExpandedChange?: (expanded: boolean) => void;

  /** Callback when Accept is clicked (for candidates) */
  onAccept?: (axiom: AxiomCandidate) => void;

  /** Callback when Reject is clicked (for candidates) */
  onReject?: (axiom: AxiomCandidate) => void;

  /** Callback when Edit is clicked */
  onEdit?: (axiom: AxiomCandidate | ConstitutionalAxiom) => void;

  /** Callback when Remove is clicked (for constitutional) */
  onRemove?: (axiom: ConstitutionalAxiom) => void;

  /** Custom className */
  className?: string;

  /** Index for staggered animations */
  index?: number;
}

// =============================================================================
// Sub-components
// =============================================================================

interface LossMeterProps {
  loss: number;
  size?: 'sm' | 'md';
}

function LossMeter({ loss, size = 'md' }: LossMeterProps) {
  const percent = Math.max(0, Math.min(100, (1 - loss) * 100));
  const height = size === 'sm' ? 4 : 6;

  // Color based on loss threshold
  const getColor = () => {
    if (loss < 0.05) return GREEN.mint; // Axiom
    if (loss < 0.2) return GREEN.sage; // Value
    if (loss < 0.4) return GLOW.amber; // Goal
    return GLOW.copper; // Weak
  };

  return (
    <div className="loss-meter" style={{ height }}>
      <motion.div
        className="loss-meter-fill"
        style={{ backgroundColor: getColor() }}
        initial={{ width: 0 }}
        animate={{ width: `${percent}%` }}
        transition={{ duration: 0.5, ease: 'easeOut' }}
      />
    </div>
  );
}

interface LayerBadgeProps {
  layer: AxiomLayer;
}

function LayerBadge({ layer }: LayerBadgeProps) {
  const getColor = () => {
    switch (layer) {
      case 'L0':
        return GREEN.mint;
      case 'L1':
        return GREEN.sage;
      case 'L2':
        return GLOW.amber;
    }
  };

  return (
    <span
      className="layer-badge"
      style={{ backgroundColor: `${getColor()}20`, color: getColor() }}
      title={getLayerDescription(layer)}
    >
      {getLayerLabel(layer)}
    </span>
  );
}

interface ConfidencePipProps {
  confidence: number;
}

function ConfidencePip({ confidence }: ConfidencePipProps) {
  const pips = 5;
  const filled = Math.round(confidence * pips);

  return (
    <div className="confidence-pips" title={`${Math.round(confidence * 100)}% confident`}>
      {Array.from({ length: pips }).map((_, i) => (
        <span
          key={i}
          className={`confidence-pip ${i < filled ? 'filled' : ''}`}
          style={{
            backgroundColor: i < filled ? GLOW.amber : `${EARTH.clay}40`,
          }}
        />
      ))}
    </div>
  );
}

interface EvidencePreviewProps {
  evidence: string[];
  expanded: boolean;
}

function EvidencePreview({ evidence, expanded }: EvidencePreviewProps) {
  const displayCount = expanded ? evidence.length : Math.min(3, evidence.length);
  const remaining = evidence.length - displayCount;

  return (
    <div className="evidence-preview">
      <span className="evidence-label">
        Based on {evidence.length} decision{evidence.length !== 1 ? 's' : ''}
      </span>
      {expanded && evidence.length > 0 && (
        <div className="evidence-ids">
          {evidence.slice(0, displayCount).map((id) => (
            <span key={id} className="evidence-id">
              {id.slice(0, 8)}...
            </span>
          ))}
          {remaining > 0 && <span className="evidence-more">+{remaining} more</span>}
        </div>
      )}
    </div>
  );
}

// =============================================================================
// Main Component
// =============================================================================

export function AxiomCard({
  axiom,
  variant = 'candidate',
  isSelected = false,
  isExpanded: controlledExpanded,
  onClick,
  onExpandedChange,
  onAccept,
  onReject,
  onEdit,
  onRemove,
  className = '',
  index = 0,
}: AxiomCardProps) {
  const [internalExpanded, setInternalExpanded] = useState(false);
  const isExpanded = controlledExpanded ?? internalExpanded;

  const handleToggleExpanded = useCallback(() => {
    const newExpanded = !isExpanded;
    setInternalExpanded(newExpanded);
    onExpandedChange?.(newExpanded);
  }, [isExpanded, onExpandedChange]);

  // Determine display content
  const content = useMemo(() => {
    if ('editedContent' in axiom && axiom.editedContent) {
      return axiom.editedContent;
    }
    return axiom.content;
  }, [axiom]);

  const layer = useMemo(() => {
    if ('layer' in axiom) {
      return axiom.layer;
    }
    return getAxiomLayer(axiom.loss);
  }, [axiom]);

  const isConstitutional = 'status' in axiom;

  // Animation variants
  const cardVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: {
      opacity: 1,
      y: 0,
      transition: {
        delay: index * 0.05,
        duration: TIMING.standard / 1000,
      },
    },
  };

  return (
    <motion.article
      className={`axiom-card ${variant} ${isSelected ? 'selected' : ''} ${isExpanded ? 'expanded' : ''} ${className}`}
      variants={cardVariants}
      initial="hidden"
      animate="visible"
      layout
      onClick={onClick}
    >
      {/* Header */}
      <header className="axiom-card-header">
        <div className="axiom-card-badges">
          <LayerBadge layer={layer} />
          {isConstitutional && (axiom as ConstitutionalAxiom).status === 'edited' && (
            <span className="edited-badge">Edited</span>
          )}
        </div>
        <ConfidencePip confidence={axiom.confidence} />
      </header>

      {/* Content */}
      <div className="axiom-card-content">
        <p className="axiom-text">{content}</p>
        {!isConstitutional && content !== axiom.content && (
          <p className="axiom-original">(Originally: {axiom.content})</p>
        )}
      </div>

      {/* Metrics */}
      <div className="axiom-card-metrics">
        <div className="metric">
          <span className="metric-label">Stability</span>
          <LossMeter loss={axiom.loss} size="sm" />
          <span className="metric-value">L={axiom.loss.toFixed(3)}</span>
        </div>
        <div className="metric">
          <span className="metric-label">Frequency</span>
          <span className="metric-value">{axiom.frequency}x</span>
        </div>
      </div>

      {/* Evidence */}
      <EvidencePreview evidence={axiom.evidence} expanded={isExpanded} />

      {/* Expanded Details */}
      <AnimatePresence>
        {isExpanded && (
          <motion.div
            className="axiom-card-details"
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: TIMING.quick / 1000 }}
          >
            <div className="detail-row">
              <span className="detail-label">Source Pattern</span>
              <span className="detail-value">{axiom.sourcePattern}</span>
            </div>
            <div className="detail-row">
              <span className="detail-label">First Seen</span>
              <span className="detail-value">{new Date(axiom.firstSeen).toLocaleDateString()}</span>
            </div>
            <div className="detail-row">
              <span className="detail-label">Last Seen</span>
              <span className="detail-value">{new Date(axiom.lastSeen).toLocaleDateString()}</span>
            </div>
            {isConstitutional && (axiom as ConstitutionalAxiom).notes && (
              <div className="detail-row">
                <span className="detail-label">Notes</span>
                <span className="detail-value">{(axiom as ConstitutionalAxiom).notes}</span>
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Actions */}
      <footer className="axiom-card-actions">
        <button
          className="action-btn secondary"
          onClick={(e) => {
            e.stopPropagation();
            handleToggleExpanded();
          }}
        >
          {isExpanded ? 'Less' : 'More'}
        </button>

        {variant === 'candidate' && (
          <>
            <button
              className="action-btn secondary"
              onClick={(e) => {
                e.stopPropagation();
                onEdit?.(axiom);
              }}
            >
              Edit
            </button>
            <button
              className="action-btn reject"
              onClick={(e) => {
                e.stopPropagation();
                onReject?.(axiom as AxiomCandidate);
              }}
            >
              Reject
            </button>
            <button
              className="action-btn accept"
              onClick={(e) => {
                e.stopPropagation();
                onAccept?.(axiom as AxiomCandidate);
              }}
            >
              Accept
            </button>
          </>
        )}

        {variant === 'constitutional' && (
          <>
            <button
              className="action-btn secondary"
              onClick={(e) => {
                e.stopPropagation();
                onEdit?.(axiom);
              }}
            >
              Edit
            </button>
            <button
              className="action-btn reject"
              onClick={(e) => {
                e.stopPropagation();
                onRemove?.(axiom as ConstitutionalAxiom);
              }}
            >
              Remove
            </button>
          </>
        )}
      </footer>
    </motion.article>
  );
}

export default AxiomCard;
