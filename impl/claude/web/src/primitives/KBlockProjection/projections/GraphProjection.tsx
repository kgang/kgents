/**
 * GraphProjection — Hypergraph Node View
 *
 * Renders K-Block as a node in the hypergraph editor.
 * Shows: title, layer badge, edge count, isolation state.
 */

import { memo } from 'react';
import type { ProjectionComponentProps } from '../types';
import { LAYER_NAMES, LAYER_COLORS } from '../types';
import './GraphProjection.css';

export const GraphProjection = memo(function GraphProjection({
  kblock,
  className = '',
}: ProjectionComponentProps) {
  const layerName = kblock.zeroSeedLayer
    ? LAYER_NAMES[kblock.zeroSeedLayer]
    : 'File';
  const layerColor = kblock.zeroSeedLayer
    ? LAYER_COLORS[kblock.zeroSeedLayer]
    : '#666';

  const edgeCount =
    kblock.incomingEdges.length + kblock.outgoingEdges.length;

  // Extract title from path (last segment)
  const title = kblock.path.split('/').pop() || kblock.id;

  return (
    <div className={`graph-projection ${className}`}>
      {/* Layer badge */}
      <div
        className="graph-projection__layer-badge"
        style={{ backgroundColor: layerColor }}
        title={layerName}
      >
        {kblock.zeroSeedLayer ? `L${kblock.zeroSeedLayer}` : 'F'}
      </div>

      {/* Title */}
      <div className="graph-projection__title" title={kblock.path}>
        {title}
      </div>

      {/* Edge count */}
      <div className="graph-projection__edges" title="Edge connections">
        {edgeCount} edges
      </div>

      {/* Isolation indicator */}
      {kblock.isolation !== 'PRISTINE' && (
        <div
          className={`graph-projection__isolation graph-projection__isolation--${kblock.isolation.toLowerCase()}`}
          title={`Isolation: ${kblock.isolation}`}
        >
          {kblock.isolation}
        </div>
      )}
    </div>
  );
});
