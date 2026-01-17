/**
 * ConstitutionalNode - Individual K-Block node in the derivation graph.
 *
 * "Simplistic, brutalistic, dense, intelligent design."
 *
 * Displays:
 * - Block name (truncated if needed)
 * - Galois loss indicator
 * - Evidence tier color
 * - Selection/highlight state
 * - Orphan warning state
 *
 * @see services/zero_seed/ashc_self_awareness.py
 */

import { memo, useCallback } from 'react';
import type { ConstitutionalKBlock, DensityMode } from './graphTypes';
import {
  LAYER_COLORS,
  PRINCIPLE_COLORS,
  EVIDENCE_TIER_COLORS,
  DENSITY_SIZES,
  L2_PRINCIPLES,
} from './graphTypes';
import './ConstitutionalNode.css';

// =============================================================================
// Types
// =============================================================================

export interface ConstitutionalNodeProps {
  /** The K-Block to render */
  block: ConstitutionalKBlock;
  /** Whether this node is currently selected */
  isSelected: boolean;
  /** Whether this node is highlighted (part of derivation path) */
  isHighlighted: boolean;
  /** Whether this node is an orphan (not grounded) */
  isOrphan: boolean;
  /** X position in the graph */
  x: number;
  /** Y position in the graph */
  y: number;
  /** Current density mode */
  density: DensityMode;
  /** Callback when node is clicked */
  onClick: (blockId: string) => void;
  /** Callback when node is hovered */
  onHover?: (blockId: string | null) => void;
}

// =============================================================================
// Helper Functions
// =============================================================================

/**
 * Get the display color for a block.
 * Principles use special colors, others use layer colors.
 */
function getBlockColor(block: ConstitutionalKBlock): string {
  // Check if it's a principle with a custom color
  if (L2_PRINCIPLES.includes(block.id as (typeof L2_PRINCIPLES)[number])) {
    return PRINCIPLE_COLORS[block.id] || LAYER_COLORS[block.layer];
  }
  return LAYER_COLORS[block.layer];
}

/**
 * Format Galois loss for display.
 */
function formatLoss(loss: number): string {
  if (loss === 0) return '0';
  if (loss < 0.01) return '<.01';
  return loss.toFixed(2);
}

/**
 * Get truncated name for display.
 */
function getTruncatedName(name: string, maxLength: number): string {
  // Remove common prefixes for cleaner display
  const cleanName = name
    .replace('A1_', 'A1:')
    .replace('A2_', 'A2:')
    .replace('A3_', 'A3:')
    .replace('G_', 'G:')
    .replace('_', '-');

  if (cleanName.length <= maxLength) return cleanName;
  return cleanName.slice(0, maxLength - 2) + '..';
}

// =============================================================================
// Component
// =============================================================================

export const ConstitutionalNode = memo(function ConstitutionalNode({
  block,
  isSelected,
  isHighlighted,
  isOrphan,
  x,
  y,
  density,
  onClick,
  onHover,
}: ConstitutionalNodeProps) {
  const sizes = DENSITY_SIZES[density];
  const blockColor = getBlockColor(block);
  const tierColor = EVIDENCE_TIER_COLORS[block.evidenceTier];

  // Calculate max name length based on width
  const maxNameLength = Math.floor((sizes.nodeWidth - 40) / (sizes.fontSize * 0.6));

  const handleClick = useCallback(() => {
    onClick(block.id);
  }, [block.id, onClick]);

  const handleMouseEnter = useCallback(() => {
    onHover?.(block.id);
  }, [block.id, onHover]);

  const handleMouseLeave = useCallback(() => {
    onHover?.(null);
  }, [onHover]);

  // Build class names
  const classNames = [
    'cgn',
    `cgn--layer-${block.layer}`,
    `cgn--tier-${block.evidenceTier}`,
    isSelected && 'cgn--selected',
    isHighlighted && 'cgn--highlighted',
    isOrphan && 'cgn--orphan',
  ]
    .filter(Boolean)
    .join(' ');

  return (
    <g
      className={classNames}
      transform={`translate(${x - sizes.nodeWidth / 2}, ${y - sizes.nodeHeight / 2})`}
      onClick={handleClick}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
      role="button"
      tabIndex={0}
      aria-label={`K-Block: ${block.title}`}
      aria-selected={isSelected}
    >
      {/* Background rect */}
      <rect
        className="cgn__bg"
        width={sizes.nodeWidth}
        height={sizes.nodeHeight}
        rx={3}
        style={{
          fill: isSelected ? blockColor : 'var(--cgn-bg, #1a1a1a)',
          stroke: isOrphan ? '#ef4444' : isHighlighted ? blockColor : 'var(--cgn-border, #333)',
          strokeWidth: isSelected || isHighlighted ? 2 : 1,
        }}
      />

      {/* Layer indicator (left edge) */}
      <rect
        className="cgn__layer-indicator"
        x={0}
        y={0}
        width={3}
        height={sizes.nodeHeight}
        rx={1}
        style={{ fill: blockColor }}
      />

      {/* Block name */}
      <text
        className="cgn__name"
        x={sizes.padding + 6}
        y={sizes.nodeHeight / 2}
        dominantBaseline="central"
        style={{
          fontSize: sizes.fontSize,
          fill: isSelected ? 'white' : 'var(--cgn-text, #e0e0e0)',
        }}
      >
        {getTruncatedName(block.id, maxNameLength)}
      </text>

      {/* Loss badge (right side) */}
      <g transform={`translate(${sizes.nodeWidth - 28}, ${(sizes.nodeHeight - 14) / 2})`}>
        <rect
          className="cgn__loss-bg"
          width={24}
          height={14}
          rx={2}
          style={{ fill: 'var(--cgn-loss-bg, #252525)' }}
        />
        <text
          className="cgn__loss-text"
          x={12}
          y={7}
          textAnchor="middle"
          dominantBaseline="central"
          style={{
            fontSize: 8,
            fill: tierColor,
            fontFamily: 'monospace',
          }}
        >
          {formatLoss(block.galoisLoss)}
        </text>
      </g>

      {/* Evidence tier dot */}
      <circle
        className="cgn__tier-dot"
        cx={sizes.nodeWidth - 6}
        cy={6}
        r={3}
        style={{ fill: tierColor }}
      />

      {/* Orphan warning indicator */}
      {isOrphan && (
        <g transform={`translate(${sizes.nodeWidth - 16}, ${sizes.nodeHeight - 10})`}>
          <text
            className="cgn__orphan-warning"
            textAnchor="end"
            style={{
              fontSize: 10,
              fill: '#ef4444',
            }}
          >
            !
          </text>
        </g>
      )}
    </g>
  );
});

export default ConstitutionalNode;
