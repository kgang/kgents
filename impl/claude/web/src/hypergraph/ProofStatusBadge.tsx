/**
 * ProofStatusBadge — Compact proof status indicator for editor header
 *
 * Shows:
 * - Layer (L1-L7) with color
 * - Confidence as visual indicator
 * - Click to toggle proof panel
 *
 * Philosophy: "Minimal surface, maximum signal."
 */

import { memo } from 'react';
import './ProofStatusBadge.css';

// =============================================================================
// Types
// =============================================================================

export interface ProofStatusBadgeProps {
  /** Zero Seed layer (1-7) */
  layer?: 1 | 2 | 3 | 4 | 5 | 6 | 7;
  /** Zero Seed node kind */
  kind?: string;
  /** Confidence score (0-1) */
  confidence: number;
  /** Whether this K-Block has a proof */
  hasProof: boolean;
  /** Whether proof panel is open */
  isPanelOpen: boolean;
  /** Toggle proof panel */
  onTogglePanel: () => void;
}

// =============================================================================
// Constants
// =============================================================================

const LAYER_COLORS: Record<number, string> = {
  1: '#8b5cf6', // Purple - Axiom
  2: '#6366f1', // Indigo - Value
  3: '#3b82f6', // Blue - Goal
  4: '#0891b2', // Cyan - Spec
  5: '#10b981', // Emerald - Action
  6: '#f59e0b', // Amber - Reflection
  7: '#ec4899', // Pink - Representation
};

const LAYER_NAMES: Record<number, string> = {
  1: 'Axiom',
  2: 'Value',
  3: 'Goal',
  4: 'Spec',
  5: 'Action',
  6: 'Reflection',
  7: 'Repr',
};

// =============================================================================
// Component
// =============================================================================

export const ProofStatusBadge = memo(function ProofStatusBadge({
  layer,
  kind,
  confidence,
  hasProof,
  isPanelOpen,
  onTogglePanel,
}: ProofStatusBadgeProps) {
  const layerColor = layer ? LAYER_COLORS[layer] : undefined;
  const layerName = layer ? (kind || LAYER_NAMES[layer]) : undefined;

  // Confidence color
  const getConfidenceColor = () => {
    if (confidence >= 0.8) return '#10b981'; // Green
    if (confidence >= 0.5) return '#f59e0b'; // Amber
    return '#ef4444'; // Red
  };

  // No layer means not a Zero Seed node
  if (!layer) {
    return (
      <button
        className="proof-status-badge proof-status-badge--inactive"
        onClick={onTogglePanel}
        title="No proof data (click to open panel)"
      >
        <span className="proof-status-badge__icon">○</span>
        <span className="proof-status-badge__label">No proof</span>
      </button>
    );
  }

  return (
    <button
      className={`proof-status-badge ${isPanelOpen ? 'proof-status-badge--active' : ''}`}
      onClick={onTogglePanel}
      style={{ '--layer-color': layerColor } as React.CSSProperties}
      title={`Layer ${layer}: ${layerName} • Confidence: ${Math.round(confidence * 100)}% • Click to ${isPanelOpen ? 'close' : 'open'} proof panel`}
    >
      {/* Layer indicator */}
      <span className="proof-status-badge__layer">L{layer}</span>

      {/* Proof status icon */}
      <span className="proof-status-badge__proof-icon">
        {hasProof ? '✓' : '○'}
      </span>

      {/* Confidence dot */}
      <span
        className="proof-status-badge__confidence"
        style={{ backgroundColor: getConfidenceColor() }}
        title={`Confidence: ${Math.round(confidence * 100)}%`}
      />

      {/* Layer name (on hover/active) */}
      <span className="proof-status-badge__name">{layerName}</span>
    </button>
  );
});

export default ProofStatusBadge;
