/**
 * SpecEdge — Custom Reactflow edge for spec relationships
 *
 * Styled by relationship type and strength.
 * STARK BIOME themed.
 */

import { memo } from 'react';
import { BaseEdge, EdgeLabelRenderer, getBezierPath, type EdgeProps } from 'reactflow';
import type { SpecEdgeData } from './useSpecGraph';

import './SpecGraph.css';

// =============================================================================
// Relationship colors
// =============================================================================

const RELATIONSHIP_COLORS: Record<string, string> = {
  defines: '#88C0D0',
  extends: '#81A1C1',
  implements: '#A3BE8C',
  references: '#5a5a64',
  contradicts: '#a65d4a',
  harmonizes: '#4a6b4a',
  tests: '#8ba98b',
  uses: '#8a8a94',
  fulfills: '#c4a77d',
};

// =============================================================================
// Component
// =============================================================================

export const SpecEdge = memo(function SpecEdge({
  id,
  sourceX,
  sourceY,
  targetX,
  targetY,
  sourcePosition,
  targetPosition,
  data,
  selected,
}: EdgeProps<SpecEdgeData>) {
  const { relationship = 'references', strength = 0.5 } = data || {};

  // Get path
  const [edgePath, labelX, labelY] = getBezierPath({
    sourceX,
    sourceY,
    sourcePosition,
    targetX,
    targetY,
    targetPosition,
  });

  // Style based on relationship
  const color = RELATIONSHIP_COLORS[relationship.toLowerCase()] || RELATIONSHIP_COLORS.references;
  const strokeWidth = 1 + strength * 2; // 1-3 based on strength
  const opacity = 0.5 + strength * 0.5; // 0.5-1 based on strength

  return (
    <>
      <BaseEdge
        id={id}
        path={edgePath}
        style={{
          stroke: color,
          strokeWidth: selected ? strokeWidth + 1 : strokeWidth,
          opacity: selected ? 1 : opacity,
          strokeDasharray: relationship === 'contradicts' ? '5,5' : undefined,
        }}
      />
      {/* Label on hover/select */}
      {selected && (
        <EdgeLabelRenderer>
          <div
            className="spec-edge__label"
            style={{
              transform: `translate(-50%, -50%) translate(${labelX}px,${labelY}px)`,
            }}
          >
            {relationship}
          </div>
        </EdgeLabelRenderer>
      )}
    </>
  );
});

export default SpecEdge;
