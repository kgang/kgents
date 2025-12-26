/**
 * CardProjection — Compact Summary Card
 *
 * Renders K-Block as a compact card (title, preview, metadata).
 * Ideal for dashboards, sidebars, or grids.
 */

import { memo } from 'react';
import type { ProjectionComponentProps } from '../types';
import { LAYER_COLORS } from '../types';
import './CardProjection.css';

export const CardProjection = memo(function CardProjection({
  kblock,
  className = '',
}: ProjectionComponentProps) {
  const layerColor = kblock.zeroSeedLayer
    ? LAYER_COLORS[kblock.zeroSeedLayer]
    : '#666';

  const title = kblock.path.split('/').pop() || kblock.id;
  const preview = kblock.content.substring(0, 100);

  return (
    <div className={`card-projection ${className}`}>
      {/* Layer indicator (left border) */}
      <div
        className="card-projection__layer-indicator"
        style={{ backgroundColor: layerColor }}
      />

      {/* Content */}
      <div className="card-projection__content">
        <div className="card-projection__title">{title}</div>
        <div className="card-projection__preview">
          {preview}
          {kblock.content.length > 100 && '...'}
        </div>
      </div>

      {/* Footer */}
      <div className="card-projection__footer">
        <span className="card-projection__author">{kblock.createdBy}</span>
        <span className="card-projection__confidence">
          {(kblock.confidence * 100).toFixed(0)}%
        </span>
      </div>
    </div>
  );
});
