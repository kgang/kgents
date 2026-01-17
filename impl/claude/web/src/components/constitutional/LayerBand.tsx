/**
 * LayerBand - Horizontal band representing an epistemic layer.
 *
 * "Simplistic, brutalistic, dense, intelligent design."
 *
 * Renders a subtle horizontal band for each layer (L0-L3) with:
 * - Layer label on the left
 * - Count of blocks in that layer
 * - Subtle background color from layer palette
 *
 * @see services/zero_seed/ashc_self_awareness.py
 */

import { memo } from 'react';
import type { EpistemicLayer, DensityMode } from './graphTypes';
import { LAYER_NAMES, LAYER_COLORS, DENSITY_SIZES } from './graphTypes';
import './LayerBand.css';

// =============================================================================
// Types
// =============================================================================

export interface LayerBandProps {
  /** The epistemic layer (0-3) */
  layer: EpistemicLayer;
  /** Y position of the band */
  y: number;
  /** Width of the band (container width) */
  width: number;
  /** Height of the band */
  height: number;
  /** Number of blocks in this layer */
  blockCount: number;
  /** Current density mode */
  density: DensityMode;
}

// =============================================================================
// Component
// =============================================================================

export const LayerBand = memo(function LayerBand({
  layer,
  y,
  width,
  height,
  blockCount,
  density,
}: LayerBandProps) {
  const sizes = DENSITY_SIZES[density];
  const layerColor = LAYER_COLORS[layer];
  const layerName = LAYER_NAMES[layer];

  // Calculate label position
  const labelX = 12;
  const labelY = y + height / 2;

  return (
    <g className={`clb clb--layer-${layer}`}>
      {/* Background rect with subtle gradient */}
      <rect
        className="clb__bg"
        x={0}
        y={y}
        width={width}
        height={height}
        style={{
          fill: `${layerColor}08`, // Very subtle tint
        }}
      />

      {/* Left edge indicator */}
      <rect
        className="clb__edge"
        x={0}
        y={y}
        width={3}
        height={height}
        style={{ fill: layerColor }}
      />

      {/* Layer label */}
      <text
        className="clb__label"
        x={labelX}
        y={labelY}
        dominantBaseline="central"
        style={{ fontSize: sizes.fontSize - 1 }}
      >
        <tspan className="clb__layer-name" style={{ fill: layerColor }}>
          L{layer}
        </tspan>
        <tspan className="clb__layer-desc" dx={6} style={{ fill: 'var(--clb-text-muted, #666)' }}>
          {layerName}
        </tspan>
      </text>

      {/* Block count badge */}
      <g transform={`translate(${width - 40}, ${labelY - 8})`}>
        <rect className="clb__count-bg" width={32} height={16} rx={8} />
        <text
          className="clb__count"
          x={16}
          y={8}
          textAnchor="middle"
          dominantBaseline="central"
          style={{ fontSize: 9 }}
        >
          {blockCount}
        </text>
      </g>
    </g>
  );
});

export default LayerBand;
