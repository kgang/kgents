/**
 * LossLegend - Renders the loss colormap legend
 *
 * Shows the viridis colormap with threshold indicator and toggles.
 */

import { memo } from 'react';
import type { ColormapName } from './types';

interface LossLegendProps {
  showLoss?: boolean;
  showGradient?: boolean;
  threshold?: number;
  colormap?: ColormapName;
}

// Colormap gradients
const COLORMAP_GRADIENTS: Record<ColormapName, string> = {
  viridis: 'linear-gradient(to right, #440154, #21918c, #fde725)',
  coolwarm: 'linear-gradient(to right, #3b4cc0, #dddddd, #b40426)',
  terrain: 'linear-gradient(to right, #333399, #00cc00, #ffcc00, #cc6600)',
};

export const LossLegend = memo(function LossLegend({
  showLoss = true,
  showGradient = true,
  threshold = 0.5,
  colormap = 'viridis',
}: LossLegendProps) {
  if (!showLoss) return null;

  return (
    <div className="loss-legend">
      <div className="loss-legend__header">
        <span className="loss-legend__title">Loss ({colormap})</span>
        <div className="loss-legend__toggles">
          <span
            className={`loss-legend__toggle ${showLoss ? 'loss-legend__toggle--active' : ''}`}
            title="Loss coloring"
          >
            L
          </span>
          <span
            className={`loss-legend__toggle ${showGradient ? 'loss-legend__toggle--active' : ''}`}
            title="Gradient arrows"
          >
            G
          </span>
        </div>
      </div>
      <div
        className="loss-legend__gradient"
        style={{
          background: COLORMAP_GRADIENTS[colormap],
          height: '8px',
          borderRadius: '4px',
          marginBottom: '4px',
          position: 'relative',
        }}
      >
        {/* Threshold marker */}
        <div
          className="loss-legend__threshold-marker"
          style={{
            position: 'absolute',
            left: `${threshold * 100}%`,
            top: '-2px',
            bottom: '-2px',
            width: '2px',
            backgroundColor: '#fff',
            boxShadow: '0 0 2px rgba(0,0,0,0.5)',
          }}
        />
      </div>
      <div
        className="loss-legend__labels"
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          fontSize: '9px',
          color: '#888',
        }}
      >
        <span>0.0 (stable)</span>
        <span>threshold: {threshold.toFixed(2)}</span>
        <span>1.0 (drift)</span>
      </div>
    </div>
  );
});

export default LossLegend;
