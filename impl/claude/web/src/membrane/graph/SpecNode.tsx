/**
 * SpecNode — Custom Reactflow node for specs
 *
 * Displays spec with tier coloring and status indicators.
 * STARK BIOME themed.
 */

import { memo } from 'react';
import { Handle, Position, type NodeProps } from 'reactflow';
import type { SpecNodeData } from './useSpecGraph';

import './SpecGraph.css';

// =============================================================================
// Component
// =============================================================================

export const SpecNode = memo(function SpecNode({ data, selected }: NodeProps<SpecNodeData>) {
  const { label, status, tier, claimCount, implCount, testCount } = data;

  // Status class for styling
  const statusClass = status.toLowerCase();

  return (
    <div
      className={`spec-node spec-node--tier-${tier} spec-node--${statusClass} ${selected ? 'spec-node--selected' : ''}`}
    >
      {/* Incoming handle (top) */}
      <Handle type="target" position={Position.Top} className="spec-node__handle" />

      {/* Content */}
      <div className="spec-node__content">
        <div className="spec-node__label" title={data.path}>
          {label}
        </div>
        <div className="spec-node__stats">
          {claimCount > 0 && (
            <span className="spec-node__stat" title="Claims">
              {claimCount}c
            </span>
          )}
          {implCount > 0 && (
            <span className="spec-node__stat spec-node__stat--impl" title="Implementations">
              {implCount}i
            </span>
          )}
          {testCount > 0 && (
            <span className="spec-node__stat spec-node__stat--test" title="Tests">
              {testCount}t
            </span>
          )}
        </div>
      </div>

      {/* Status indicator */}
      <div className="spec-node__status" data-status={status} title={status} />

      {/* Outgoing handle (bottom) */}
      <Handle type="source" position={Position.Bottom} className="spec-node__handle" />
    </div>
  );
});

export default SpecNode;
