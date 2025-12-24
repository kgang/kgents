/**
 * FocalDistanceRuler — Vertical ruler showing focal distance layers
 *
 * "The telescope shows all layers at once."
 *
 * A vertical navigation control that displays the 7-layer epistemic hierarchy
 * and allows jumping to specific focal distances. Uses viridis gradient to
 * show layer stability (L1 purple → L7 yellow).
 */

import { memo, useCallback } from 'react';
import { getLayerName, getLayerIcon } from '../../hooks/useTelescopeState';
import './FocalDistanceRuler.css';

// =============================================================================
// Types
// =============================================================================

interface FocalDistanceRulerProps {
  /** Visible layers at current distance */
  visibleLayers: number[];

  /** Callback when layer is clicked */
  onLayerClick: (layer: number) => void;

  /** Compact mode (icons only) */
  compact?: boolean;
}

// =============================================================================
// Constants
// =============================================================================

const LAYERS = [1, 2, 3, 4, 5, 6, 7] as const;

// Viridis colors for each layer
const LAYER_COLORS: Record<number, string> = {
  1: 'var(--viridis-0)', // Deep purple - axiomatic
  2: 'var(--viridis-20)', // Purple-teal - values
  3: 'var(--viridis-30)', // Teal - goals
  4: 'var(--viridis-50)', // Green - specs (default view)
  5: 'var(--viridis-70)', // Lime - actions
  6: 'var(--viridis-80)', // Yellow-green - reflections
  7: 'var(--viridis-100)', // Yellow - documents
};

// =============================================================================
// Component
// =============================================================================

export const FocalDistanceRuler = memo(function FocalDistanceRuler({
  visibleLayers,
  onLayerClick,
  compact = false,
}: FocalDistanceRulerProps) {
  const handleLayerClick = useCallback(
    (layer: number) => {
      onLayerClick(layer);
    },
    [onLayerClick]
  );

  return (
    <div
      className={`focal-distance-ruler ${compact ? 'focal-distance-ruler--compact' : ''}`}
      aria-label="Focal distance layer navigation"
    >
      {/* Layer markers */}
      <div className="focal-distance-ruler__layers">
        {LAYERS.map((layer) => {
          const isVisible = visibleLayers.includes(layer);
          const isCurrent =
            visibleLayers.length === 1 && visibleLayers[0] === layer;

          return (
            <button
              key={layer}
              className={`focal-distance-ruler__layer ${
                isVisible ? 'focal-distance-ruler__layer--visible' : ''
              } ${isCurrent ? 'focal-distance-ruler__layer--current' : ''}`}
              style={{ '--layer-color': LAYER_COLORS[layer] } as React.CSSProperties}
              onClick={() => handleLayerClick(layer)}
              title={`${getLayerName(layer)} (L${layer})`}
              aria-label={`Jump to ${getLayerName(layer)}`}
              aria-current={isCurrent ? 'location' : undefined}
            >
              <span className="focal-distance-ruler__icon">{getLayerIcon(layer)}</span>
              {!compact && (
                <span className="focal-distance-ruler__label">L{layer}</span>
              )}
            </button>
          );
        })}
      </div>

      {/* Current position indicator */}
      {visibleLayers.length === 1 && (
        <div
          className="focal-distance-ruler__indicator"
          style={
            {
              '--indicator-position': `${((visibleLayers[0] - 1) / 6) * 100}%`,
              '--indicator-color': LAYER_COLORS[visibleLayers[0]],
            } as React.CSSProperties
          }
          aria-hidden="true"
        />
      )}

      {/* Zoom shortcuts hint */}
      {!compact && (
        <div className="focal-distance-ruler__hint">
          <kbd>gL</kbd> out
          <br />
          <kbd>gH</kbd> in
        </div>
      )}
    </div>
  );
});
