/**
 * Witness Primitive - Evidence display with confidence tiers and causal graphs
 *
 * Consolidates:
 * - ASHCEvidence.tsx (ASHC compilation evidence)
 * - ConfidenceIndicator.tsx (per-response confidence)
 * - Parts of ContextIndicator.tsx (evidence display)
 *
 * Design: STARK biome with brutalist foundations
 * - Steel background surfaces
 * - Tier-specific border colors (green/yellow/red)
 * - Subtle glow on hover
 * - Breathing animation for high-influence edges
 */

import { memo, useState } from 'react';
import type { EvidenceCorpus, Evidence, CausalEdge } from '../../types/theory';
import './Witness.css';

// =============================================================================
// Types
// =============================================================================

export interface WitnessProps {
  /** Evidence corpus with items and confidence */
  evidence: EvidenceCorpus;

  /** Show causal influence graph */
  showCausal?: boolean;

  /** Compact mode for inline display */
  compact?: boolean;

  /** Click handler for evidence items */
  onEvidenceClick?: (evidenceId: string) => void;

  /** Size variant */
  size?: 'sm' | 'md' | 'lg';
}

// =============================================================================
// Helper Functions
// =============================================================================

function getTierConfig(tier: EvidenceCorpus['tier']) {
  switch (tier) {
    case 'confident':
      return {
        label: 'High Confidence',
        icon: '●',
        borderClass: 'witness--confident',
        threshold: '> 0.80',
      };
    case 'uncertain':
      return {
        label: 'Medium Confidence',
        icon: '◐',
        borderClass: 'witness--uncertain',
        threshold: '0.50-0.80',
      };
    case 'speculative':
      return {
        label: 'Low Confidence',
        icon: '◯',
        borderClass: 'witness--speculative',
        threshold: '< 0.50',
      };
  }
}

function formatConfidence(confidence: number): string {
  return `P=${confidence.toFixed(2)}`;
}

// =============================================================================
// Subcomponents
// =============================================================================

interface EvidenceItemProps {
  evidence: Evidence;
  onClick?: (id: string) => void;
  compact?: boolean;
}

const EvidenceItem = memo(function EvidenceItem({
  evidence,
  onClick,
  compact,
}: EvidenceItemProps) {
  return (
    <div
      className={`witness__item ${onClick ? 'witness__item--clickable' : ''} ${compact ? 'witness__item--compact' : ''}`}
      onClick={() => onClick?.(evidence.id)}
      role={onClick ? 'button' : undefined}
      tabIndex={onClick ? 0 : undefined}
    >
      <div className="witness__item-header">
        <span className="witness__item-confidence">
          {formatConfidence(evidence.confidence)}
        </span>
        {!compact && (
          <span className="witness__item-source">{evidence.source}</span>
        )}
      </div>
      <div className="witness__item-content">{evidence.content}</div>
    </div>
  );
});

interface CausalGraphProps {
  edges: CausalEdge[];
  items: Evidence[];
}

const CausalGraph = memo(function CausalGraph({
  edges,
  items,
}: CausalGraphProps) {
  // Create a map for quick item lookup
  const itemMap = new Map(items.map((item) => [item.id, item]));

  return (
    <div className="witness__causal-graph">
      <div className="witness__causal-header">Causal Influence Graph</div>
      <div className="witness__causal-edges">
        {edges.map((edge, idx) => {
          const fromItem = itemMap.get(edge.from);
          const toItem = itemMap.get(edge.to);
          const isHighInfluence = edge.influence > 0.7;

          return (
            <div
              key={idx}
              className={`witness__causal-edge ${isHighInfluence ? 'witness__causal-edge--high' : ''}`}
            >
              <div className="witness__causal-from">
                {fromItem?.content.slice(0, 30) || edge.from}...
              </div>
              <div className="witness__causal-arrow">
                →
                <span className="witness__causal-influence">
                  ({(edge.influence * 100).toFixed(0)}%)
                </span>
              </div>
              <div className="witness__causal-to">
                {toItem?.content.slice(0, 30) || edge.to}...
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
});

// =============================================================================
// Main Component
// =============================================================================

export const Witness = memo(function Witness({
  evidence,
  showCausal = false,
  compact = false,
  onEvidenceClick,
  size = 'md',
}: WitnessProps) {
  const [expanded, setExpanded] = useState(!compact);

  const config = getTierConfig(evidence.tier);
  const itemCount = evidence.items.length;
  const hasCausalGraph = evidence.causalGraph.length > 0;

  // Compact mode: just badge + count
  if (compact) {
    return (
      <div
        className={`witness witness--compact witness--${size} ${config.borderClass}`}
        onClick={() => setExpanded(!expanded)}
        role="button"
        tabIndex={0}
      >
        <div className="witness__badge">
          <span className="witness__icon">{config.icon}</span>
          <span className="witness__label">{config.label}</span>
          <span className="witness__count">({itemCount})</span>
        </div>
      </div>
    );
  }

  // Full mode
  return (
    <div className={`witness witness--${size} ${config.borderClass}`}>
      {/* Header */}
      <div className="witness__header">
        <div className="witness__title">
          <span className="witness__icon">{config.icon}</span>
          <span className="witness__label">{config.label}</span>
        </div>
        <div className="witness__meta">
          <span className="witness__threshold">{config.threshold}</span>
          <span className="witness__count">{itemCount} items</span>
        </div>
      </div>

      {/* Evidence items */}
      {expanded && (
        <div className="witness__items">
          {evidence.items.map((item) => (
            <EvidenceItem
              key={item.id}
              evidence={item}
              onClick={onEvidenceClick}
              compact={compact}
            />
          ))}
        </div>
      )}

      {/* Causal graph */}
      {expanded && showCausal && hasCausalGraph && (
        <CausalGraph edges={evidence.causalGraph} items={evidence.items} />
      )}

      {/* Toggle hint */}
      {!compact && itemCount > 3 && (
        <div
          className="witness__toggle"
          onClick={() => setExpanded(!expanded)}
          role="button"
          tabIndex={0}
        >
          {expanded ? 'Collapse' : 'Expand'}
        </div>
      )}
    </div>
  );
});

export default Witness;
