/**
 * GradientField - Renders gradient arrows for loss navigation
 *
 * Visualizes the loss gradient field as arrows pointing toward
 * lower loss regions (stability).
 */

import { memo } from 'react';
import type { GradientArrow, Position2D } from './types';

interface GradientFieldProps {
  arrows: GradientArrow[];
  scalePosition?: (pos: Position2D) => Position2D;
  opacity?: number;
}

export const GradientField = memo(function GradientField({
  arrows,
  scalePosition,
  opacity = 0.6,
}: GradientFieldProps) {
  // Apply position scaling if provided
  const scale = scalePosition || ((pos: Position2D) => pos);

  return (
    <g className="gradient-field" opacity={opacity}>
      <defs>
        <marker
          id="gradient-arrow-head"
          markerWidth="10"
          markerHeight="7"
          refX="9"
          refY="3.5"
          orient="auto"
        >
          <polygon points="0 0, 10 3.5, 0 7" fill="#22c55e" />
        </marker>
        <marker
          id="gradient-arrow-head-warning"
          markerWidth="10"
          markerHeight="7"
          refX="9"
          refY="3.5"
          orient="auto"
        >
          <polygon points="0 0, 10 3.5, 0 7" fill="#f59e0b" />
        </marker>
        <marker
          id="gradient-arrow-head-danger"
          markerWidth="10"
          markerHeight="7"
          refX="9"
          refY="3.5"
          orient="auto"
        >
          <polygon points="0 0, 10 3.5, 0 7" fill="#ef4444" />
        </marker>
      </defs>
      {arrows.map((arrow, i) => {
        const start = scale(arrow.start);
        const end = scale(arrow.end);

        // Choose marker based on magnitude (high = warning, very high = danger)
        let markerId = 'gradient-arrow-head';
        if (arrow.magnitude > 0.7) {
          markerId = 'gradient-arrow-head-danger';
        } else if (arrow.magnitude > 0.4) {
          markerId = 'gradient-arrow-head-warning';
        }

        return (
          <line
            key={i}
            x1={start.x}
            y1={start.y}
            x2={end.x}
            y2={end.y}
            stroke={arrow.color || '#22c55e'}
            strokeWidth={arrow.width || 2}
            markerEnd={`url(#${markerId})`}
            className="gradient-field__arrow"
          />
        );
      })}
    </g>
  );
});

export default GradientField;
