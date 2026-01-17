/**
 * DerivationEdge - SVG edge between K-Blocks in the derivation graph.
 *
 * "Simplistic, brutalistic, dense, intelligent design."
 *
 * Renders a curved path from parent to child block with:
 * - Subtle gradient indicating derivation direction
 * - Opacity based on Galois loss (lower loss = more opaque)
 * - Highlight state when part of selected derivation path
 *
 * @see services/zero_seed/ashc_self_awareness.py
 */

import { memo, useMemo } from 'react';
import type { NodePosition, EpistemicLayer } from './graphTypes';
import { LAYER_COLORS } from './graphTypes';
import './DerivationEdge.css';

// =============================================================================
// Types
// =============================================================================

export interface DerivationEdgeProps {
  /** Source block ID (parent) */
  sourceId: string;
  /** Target block ID (child) */
  targetId: string;
  /** Source position */
  sourcePos: NodePosition;
  /** Target position */
  targetPos: NodePosition;
  /** Source layer (for coloring) */
  sourceLayer: EpistemicLayer;
  /** Target layer (for coloring) */
  targetLayer: EpistemicLayer;
  /** Galois loss for this derivation step */
  loss: number;
  /** Whether this edge is highlighted (part of selected path) */
  isHighlighted: boolean;
  /** Node height (for calculating connection points) */
  nodeHeight: number;
}

// =============================================================================
// Helper Functions
// =============================================================================

/**
 * Calculate a bezier curve path between two points.
 * Curves upward from parent to child with control points.
 */
function calculatePath(source: NodePosition, target: NodePosition, nodeHeight: number): string {
  // Edges connect from top of parent to bottom of child
  const startY = source.y - nodeHeight / 2; // Top of parent
  const endY = target.y + nodeHeight / 2; // Bottom of child

  // Calculate control points for smooth curve
  const midY = (startY + endY) / 2;
  const curvature = Math.abs(target.x - source.x) * 0.3;

  // Use quadratic bezier for simpler, cleaner curves
  if (Math.abs(target.x - source.x) < 10) {
    // Nearly vertical - use straight line with slight curve
    return `M ${source.x} ${startY}
            C ${source.x} ${midY},
              ${target.x} ${midY},
              ${target.x} ${endY}`;
  }

  // Standard curved path
  const controlOffset = Math.min(curvature, 50);
  return `M ${source.x} ${startY}
          C ${source.x} ${startY - controlOffset},
            ${target.x} ${endY + controlOffset},
            ${target.x} ${endY}`;
}

/**
 * Calculate opacity based on loss.
 * Lower loss = higher opacity (stronger derivation)
 */
function getOpacity(loss: number, isHighlighted: boolean): number {
  if (isHighlighted) return 0.9;
  // Map loss [0, 1] to opacity [0.6, 0.2]
  return Math.max(0.2, 0.6 - loss * 0.4);
}

/**
 * Calculate stroke width based on highlight state.
 */
function getStrokeWidth(isHighlighted: boolean): number {
  return isHighlighted ? 2 : 1;
}

// =============================================================================
// Component
// =============================================================================

export const DerivationEdge = memo(function DerivationEdge({
  sourceId,
  targetId,
  sourcePos,
  targetPos,
  sourceLayer,
  targetLayer,
  loss,
  isHighlighted,
  nodeHeight,
}: DerivationEdgeProps) {
  // Calculate path
  const path = useMemo(
    () => calculatePath(sourcePos, targetPos, nodeHeight),
    [sourcePos, targetPos, nodeHeight]
  );

  // Calculate visual properties
  const opacity = getOpacity(loss, isHighlighted);
  const strokeWidth = getStrokeWidth(isHighlighted);

  // Use target layer color (the child's layer)
  const strokeColor = LAYER_COLORS[targetLayer];

  // Unique ID for gradient
  const gradientId = `edge-gradient-${sourceId}-${targetId}`;

  const classNames = ['cge', isHighlighted && 'cge--highlighted'].filter(Boolean).join(' ');

  return (
    <g className={classNames}>
      {/* Gradient definition */}
      <defs>
        <linearGradient id={gradientId} x1="0%" y1="100%" x2="0%" y2="0%">
          <stop offset="0%" stopColor={LAYER_COLORS[sourceLayer]} stopOpacity={opacity * 0.5} />
          <stop offset="100%" stopColor={strokeColor} stopOpacity={opacity} />
        </linearGradient>
      </defs>

      {/* Edge path */}
      <path
        className="cge__path"
        d={path}
        fill="none"
        stroke={isHighlighted ? strokeColor : `url(#${gradientId})`}
        strokeWidth={strokeWidth}
        strokeLinecap="round"
        style={{ opacity: isHighlighted ? 1 : opacity }}
      />

      {/* Arrow head (subtle) */}
      {isHighlighted && (
        <circle
          className="cge__arrow"
          cx={targetPos.x}
          cy={targetPos.y + nodeHeight / 2 + 2}
          r={3}
          fill={strokeColor}
        />
      )}
    </g>
  );
});

export default DerivationEdge;
