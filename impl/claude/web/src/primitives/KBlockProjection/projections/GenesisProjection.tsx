/**
 * GenesisProjection — Zero Seed Cascade View
 *
 * Renders K-Block as part of a lineage cascade (indented by depth).
 * Shows: layer, title, lineage indicator.
 */

import { memo } from 'react';
import type { ProjectionComponentProps } from '../types';
import { LAYER_NAMES, LAYER_COLORS } from '../types';
import './GenesisProjection.css';

export const GenesisProjection = memo(function GenesisProjection({
  kblock,
  depth = 0,
  className = '',
}: ProjectionComponentProps) {
  const layerName = kblock.zeroSeedLayer
    ? LAYER_NAMES[kblock.zeroSeedLayer]
    : 'File';
  const layerColor = kblock.zeroSeedLayer
    ? LAYER_COLORS[kblock.zeroSeedLayer]
    : '#666';

  const title = kblock.path.split('/').pop() || kblock.id;

  return (
    <div
      className={`genesis-projection ${className}`}
      style={{
        paddingLeft: `calc(${depth} * var(--space-xl))`,
      }}
    >
      {/* Depth indicator */}
      {depth > 0 && (
        <div className="genesis-projection__depth-indicator">
          {'→ '.repeat(depth)}
        </div>
      )}

      {/* Layer badge */}
      <div
        className="genesis-projection__layer-badge"
        style={{ backgroundColor: layerColor }}
        title={layerName}
      >
        L{kblock.zeroSeedLayer ?? 'F'}
      </div>

      {/* Title */}
      <div className="genesis-projection__title">{title}</div>

      {/* Lineage count */}
      {kblock.lineage.length > 0 && (
        <div className="genesis-projection__lineage-count">
          {kblock.lineage.length} parent{kblock.lineage.length > 1 ? 's' : ''}
        </div>
      )}
    </div>
  );
});
