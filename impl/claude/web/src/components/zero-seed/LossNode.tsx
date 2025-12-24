/**
 * LossNode - Renders a node with loss visualization
 *
 * Displays nodes with loss-based coloring using viridis colormap.
 * Nodes glow when they have high loss (semantic drift warning).
 */

import { memo } from 'react';
import type { NodeProjection, Position2D } from './types';
import { LAYER_SHAPES } from './types';

interface LossNodeProps {
  projection: NodeProjection;
  position: Position2D;
  isHovered?: boolean;
  isFocal?: boolean;
  showLoss?: boolean;
  onClick?: () => void;
  onMouseEnter?: () => void;
  onMouseLeave?: () => void;
}

export const LossNode = memo(function LossNode({
  projection,
  position,
  isHovered = false,
  isFocal = false,
  showLoss = true,
  onClick,
  onMouseEnter,
  onMouseLeave,
}: LossNodeProps) {
  const { layer, scale, opacity, color, glow, glow_intensity } = projection;
  const radius = 20 * scale;
  const shape = LAYER_SHAPES[layer] || 'circle';

  // Use projection color if showing loss, otherwise use layer color
  const fillColor = showLoss ? color : `hsl(${layer * 50}, 60%, 50%)`;

  // Render shape based on layer
  const renderShape = () => {
    switch (shape) {
      case 'diamond':
        return (
          <polygon
            points={`0,${-radius} ${radius},0 0,${radius} ${-radius},0`}
            fill={fillColor}
            opacity={opacity}
          />
        );
      case 'star': {
        // 5-pointed star
        const outerR = radius;
        const innerR = radius * 0.5;
        const points = [];
        for (let i = 0; i < 10; i++) {
          const r = i % 2 === 0 ? outerR : innerR;
          const angle = (i * Math.PI) / 5 - Math.PI / 2;
          points.push(`${r * Math.cos(angle)},${r * Math.sin(angle)}`);
        }
        return (
          <polygon points={points.join(' ')} fill={fillColor} opacity={opacity} />
        );
      }
      case 'rectangle':
        return (
          <rect
            x={-radius}
            y={-radius * 0.7}
            width={radius * 2}
            height={radius * 1.4}
            fill={fillColor}
            opacity={opacity}
          />
        );
      case 'hexagon': {
        const hexPoints = [];
        for (let i = 0; i < 6; i++) {
          const angle = (i * Math.PI) / 3;
          hexPoints.push(`${radius * Math.cos(angle)},${radius * Math.sin(angle)}`);
        }
        return (
          <polygon points={hexPoints.join(' ')} fill={fillColor} opacity={opacity} />
        );
      }
      case 'octagon': {
        const octPoints = [];
        for (let i = 0; i < 8; i++) {
          const angle = (i * Math.PI) / 4;
          octPoints.push(`${radius * Math.cos(angle)},${radius * Math.sin(angle)}`);
        }
        return (
          <polygon points={octPoints.join(' ')} fill={fillColor} opacity={opacity} />
        );
      }
      case 'cloud':
        // Simplified cloud shape using circles
        return (
          <g opacity={opacity}>
            <circle cx={-radius * 0.3} cy={0} r={radius * 0.6} fill={fillColor} />
            <circle cx={radius * 0.3} cy={0} r={radius * 0.6} fill={fillColor} />
            <circle cx={0} cy={-radius * 0.3} r={radius * 0.7} fill={fillColor} />
          </g>
        );
      case 'circle':
      default:
        return <circle r={radius} fill={fillColor} opacity={opacity} />;
    }
  };

  return (
    <g
      transform={`translate(${position.x}, ${position.y})`}
      onClick={onClick}
      onMouseEnter={onMouseEnter}
      onMouseLeave={onMouseLeave}
      style={{ cursor: 'pointer' }}
      className="loss-node"
    >
      {/* Glow effect for high loss nodes */}
      {glow && (
        <circle
          r={radius * 1.5}
          fill="none"
          stroke="#ff6b6b"
          strokeWidth={2}
          opacity={glow_intensity * 0.5}
          className="loss-node__glow"
        />
      )}

      {/* Focal point indicator */}
      {isFocal && (
        <circle
          r={radius * 1.3}
          fill="none"
          stroke="#ffd700"
          strokeWidth={3}
          className="loss-node__focal"
        />
      )}

      {/* Hover indicator */}
      {isHovered && (
        <circle
          r={radius * 1.2}
          fill="none"
          stroke="#ffffff"
          strokeWidth={2}
          opacity={0.7}
          className="loss-node__hover"
        />
      )}

      {/* Main shape */}
      {renderShape()}

      {/* Layer label */}
      <text
        y={radius + 14}
        textAnchor="middle"
        fontSize={9}
        fill="#888"
        className="loss-node__label"
      >
        L{layer}
      </text>
    </g>
  );
});

export default LossNode;
