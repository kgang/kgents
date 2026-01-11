/**
 * LayerEvolution - Layer Stability Visualization
 *
 * Shows how each layer has evolved:
 * - L0: Irreducibles (should rarely change)
 * - L1: Primitives (occasional refinement)
 * - L2: Derived (more frequent)
 * - L3: Architecture (active development)
 * - L4: Implementation (most active)
 *
 * Visual representation:
 * - Stacked layers with activity heat
 * - Highlight when layers change together
 * - Show stability score per layer
 *
 * STARK BIOME: 90% steel, 10% earned amber glow.
 */

import { memo } from 'react';
import { Layers, AlertTriangle, CheckCircle2 } from 'lucide-react';

import type { LayerStability } from './types';
import { HISTORY_LAYER_COLORS } from './types';

// =============================================================================
// Types
// =============================================================================

interface LayerEvolutionProps {
  layers: LayerStability[];
  onLayerClick: (layer: number) => void;
}

// =============================================================================
// Helpers
// =============================================================================

function getStabilityStatus(
  stability: number,
  expected: number
): 'healthy' | 'warning' | 'critical' {
  const diff = expected - stability;
  if (diff <= 0.05) return 'healthy';
  if (diff <= 0.15) return 'warning';
  return 'critical';
}

function formatPercentage(value: number): string {
  return `${Math.round(value * 100)}%`;
}

// =============================================================================
// Layer Bar Component
// =============================================================================

interface LayerBarProps {
  layer: LayerStability;
  onClick: () => void;
}

const LayerBar = memo(function LayerBar({ layer, onClick }: LayerBarProps) {
  const layerColor = HISTORY_LAYER_COLORS[layer.layer as keyof typeof HISTORY_LAYER_COLORS];
  const status = getStabilityStatus(layer.stability, layer.expectedStability);
  const stabilityWidth = Math.round(layer.stability * 100);
  const expectedWidth = Math.round(layer.expectedStability * 100);

  return (
    <button
      className={`layer-bar layer-bar--${status}`}
      onClick={onClick}
      style={{ '--layer-color': layerColor } as React.CSSProperties}
    >
      <div className="layer-bar__header">
        <div className="layer-bar__layer-info">
          <span className="layer-bar__layer-num">L{layer.layer}</span>
          <span className="layer-bar__layer-name">{layer.name}</span>
        </div>
        <div className="layer-bar__stats">
          <span className="layer-bar__kblock-count">{layer.kblockCount} K-Blocks</span>
          <span className="layer-bar__change-count">{layer.changeCount} changes</span>
        </div>
      </div>

      <div className="layer-bar__track">
        {/* Expected stability marker */}
        <div
          className="layer-bar__expected"
          style={{ left: `${expectedWidth}%` }}
          title={`Expected: ${formatPercentage(layer.expectedStability)}`}
        />
        {/* Actual stability bar */}
        <div className="layer-bar__fill" style={{ width: `${stabilityWidth}%` }} />
      </div>

      <div className="layer-bar__footer">
        <span className="layer-bar__stability">
          {status === 'healthy' && <CheckCircle2 size={12} />}
          {status === 'warning' && <AlertTriangle size={12} />}
          {status === 'critical' && <AlertTriangle size={12} />}
          {formatPercentage(layer.stability)} stable
        </span>
        {layer.lastChanged && (
          <span className="layer-bar__last-changed">Last: {layer.lastChanged}</span>
        )}
      </div>
    </button>
  );
});

// =============================================================================
// Main Component
// =============================================================================

export const LayerEvolution = memo(function LayerEvolution({
  layers,
  onLayerClick,
}: LayerEvolutionProps) {
  // Sort layers by number (L0 at top)
  const sortedLayers = [...layers].sort((a, b) => a.layer - b.layer);

  // Calculate overall health
  const overallStability =
    sortedLayers.reduce((acc, l) => acc + l.stability, 0) / sortedLayers.length;
  const overallExpected =
    sortedLayers.reduce((acc, l) => acc + l.expectedStability, 0) / sortedLayers.length;
  const overallStatus = getStabilityStatus(overallStability, overallExpected);

  return (
    <div className="layer-evolution">
      {/* Header */}
      <div className="layer-evolution__header">
        <Layers size={14} />
        <span className="layer-evolution__title">Layer Evolution</span>
      </div>

      {/* Overall Health */}
      <div className={`layer-evolution__overall layer-evolution__overall--${overallStatus}`}>
        <span className="layer-evolution__overall-label">Constitution Health</span>
        <span className="layer-evolution__overall-value">{formatPercentage(overallStability)}</span>
        {overallStatus !== 'healthy' && (
          <span className="layer-evolution__overall-warning">
            Expected: {formatPercentage(overallExpected)}
          </span>
        )}
      </div>

      {/* Layer Bars */}
      <div className="layer-evolution__layers">
        {sortedLayers.map((layer) => (
          <LayerBar key={layer.layer} layer={layer} onClick={() => onLayerClick(layer.layer)} />
        ))}
      </div>

      {/* Legend */}
      <div className="layer-evolution__legend">
        <div className="layer-evolution__legend-item">
          <div className="layer-evolution__legend-bar layer-evolution__legend-bar--fill" />
          <span>Actual Stability</span>
        </div>
        <div className="layer-evolution__legend-item">
          <div className="layer-evolution__legend-marker" />
          <span>Expected</span>
        </div>
      </div>

      {/* Help Text */}
      <div className="layer-evolution__help">
        <p>L0-L1 should be highly stable.</p>
        <p>L3-L4 change more frequently.</p>
        <p>Click a layer to filter timeline.</p>
      </div>
    </div>
  );
});
