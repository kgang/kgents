/**
 * ConstitutionalRadar - 7-spoke radar chart for constitutional principles
 *
 * Visualizes adherence to the 7 kgents constitutional principles:
 * 1. Tasteful - clear, justified purpose
 * 2. Curated - intentional selection
 * 3. Ethical - augments human capability
 * 4. Joy-Inducing - delight in interaction
 * 5. Composable - morphisms in a category
 * 6. Heterarchical - flux, not hierarchy
 * 7. Generative - spec is compression
 *
 * Pure SVG heptagon radar chart with color-coded vertices.
 * Design: STARK biome with subtle glow on hover.
 */

import { memo, useMemo } from 'react';
import type { ConstitutionalScores, PrincipleKey } from './types';
import { PRINCIPLE_ORDER, PRINCIPLES, getScoreColor } from './types';
import './ConstitutionalRadar.css';

// =============================================================================
// Types
// =============================================================================

export interface ConstitutionalRadarProps {
  /** Principle scores (0-1 range) */
  scores: ConstitutionalScores;

  /** Size variant */
  size?: 'sm' | 'md' | 'lg';

  /** Show principle labels around perimeter */
  showLabels?: boolean;

  /** Enable hover effects and interactivity */
  interactive?: boolean;

  /** Click handler for individual principles */
  onPrincipleClick?: (principle: PrincipleKey) => void;
}

// =============================================================================
// Constants
// =============================================================================

const SIZES = {
  sm: 160,
  md: 240,
  lg: 320,
} as const;

const NUM_PRINCIPLES = 7;
const GRID_LEVELS = [0.2, 0.4, 0.6, 0.8, 1.0];

// =============================================================================
// Geometry Helpers
// =============================================================================

interface Point {
  x: number;
  y: number;
}

/**
 * Calculate point on heptagon at given angle and distance from center
 */
function polarToCartesian(
  centerX: number,
  centerY: number,
  radius: number,
  angleInRadians: number
): Point {
  return {
    x: centerX + radius * Math.cos(angleInRadians),
    y: centerY + radius * Math.sin(angleInRadians),
  };
}

/**
 * Get angle for principle at index (clockwise from top)
 */
function getPrincipleAngle(index: number): number {
  return (Math.PI * 2 * index) / NUM_PRINCIPLES - Math.PI / 2;
}

/**
 * Convert points array to SVG polygon points string
 */
function pointsToString(points: Point[]): string {
  return points.map((p) => `${p.x},${p.y}`).join(' ');
}

/**
 * Convert points array to SVG path (for closed polygons)
 */
function pointsToPath(points: Point[]): string {
  if (points.length === 0) return '';

  const [first, ...rest] = points;
  const pathParts = [`M ${first.x} ${first.y}`];

  for (const point of rest) {
    pathParts.push(`L ${point.x} ${point.y}`);
  }

  pathParts.push('Z'); // Close path

  return pathParts.join(' ');
}

// =============================================================================
// Component
// =============================================================================

/**
 * ConstitutionalRadar - Heptagonal radar chart
 *
 * Shows 7 constitutional principles as a radar polygon with:
 * - Background grid (concentric heptagons)
 * - Axis lines (from center to vertices)
 * - Score polygon (filled, color-coded vertices)
 * - Optional labels around perimeter
 */
export const ConstitutionalRadar = memo(function ConstitutionalRadar({
  scores,
  size = 'md',
  showLabels = true,
  interactive = false,
  onPrincipleClick,
}: ConstitutionalRadarProps) {
  const dimension = SIZES[size];
  const center = dimension / 2;
  const radius = (dimension / 2) * 0.7; // Leave room for labels

  // Calculate geometry
  const geometry = useMemo(() => {
    // Score values in principle order
    const scoreValues = PRINCIPLE_ORDER.map((key) => scores[key]);

    // Score polygon points
    const scorePoints = scoreValues.map((score, i) => {
      const angle = getPrincipleAngle(i);
      const distance = radius * score;
      return polarToCartesian(center, center, distance, angle);
    });

    // Grid polygons (concentric heptagons)
    const gridPolygons = GRID_LEVELS.map((level) => {
      const levelPoints = Array.from({ length: NUM_PRINCIPLES }, (_, i) => {
        const angle = getPrincipleAngle(i);
        const distance = radius * level;
        return polarToCartesian(center, center, distance, angle);
      });
      return pointsToPath(levelPoints);
    });

    // Axis lines (from center to each vertex)
    const axisLines = Array.from({ length: NUM_PRINCIPLES }, (_, i) => {
      const angle = getPrincipleAngle(i);
      const endpoint = polarToCartesian(center, center, radius, angle);
      return {
        x1: center,
        y1: center,
        x2: endpoint.x,
        y2: endpoint.y,
      };
    });

    // Label positions (outside radar)
    const labelPositions = PRINCIPLE_ORDER.map((_, i) => {
      const angle = getPrincipleAngle(i);
      const distance = radius * 1.2;
      return polarToCartesian(center, center, distance, angle);
    });

    // Vertex colors (based on score tier)
    const vertexColors = scoreValues.map((score) => getScoreColor(score));

    return {
      scoreValues,
      scorePoints,
      gridPolygons,
      axisLines,
      labelPositions,
      vertexColors,
    };
  }, [scores, radius, center]);

  const vertexRadius = size === 'sm' ? 3 : size === 'md' ? 4 : 5;
  const fontSize = size === 'sm' ? 9 : size === 'md' ? 10 : 12;

  return (
    <div
      className={`constitutional-radar constitutional-radar--${size} ${interactive ? 'constitutional-radar--interactive' : ''}`}
      role="img"
      aria-label="Constitutional principle scores radar chart"
    >
      <svg
        width={dimension}
        height={dimension}
        viewBox={`0 0 ${dimension} ${dimension}`}
        className="constitutional-radar__svg"
      >
        {/* Background grid (concentric heptagons) */}
        <g className="constitutional-radar__grid">
          {geometry.gridPolygons.map((path, i) => (
            <path
              key={`grid-${i}`}
              d={path}
              fill="none"
              stroke="var(--surface-3)"
              strokeWidth="1"
              opacity={0.3}
            />
          ))}
        </g>

        {/* Axis lines */}
        <g className="constitutional-radar__axes">
          {geometry.axisLines.map((line, i) => (
            <line
              key={`axis-${i}`}
              x1={line.x1}
              y1={line.y1}
              x2={line.x2}
              y2={line.y2}
              stroke="var(--surface-3)"
              strokeWidth="1"
              opacity={0.5}
            />
          ))}
        </g>

        {/* Score polygon (filled area) */}
        <g className="constitutional-radar__score">
          <polygon
            points={pointsToString(geometry.scorePoints)}
            fill="var(--accent-primary)"
            fillOpacity="0.15"
            stroke="var(--accent-primary)"
            strokeWidth="2"
          />
        </g>

        {/* Score vertices (color-coded dots) */}
        <g className="constitutional-radar__vertices">
          {geometry.scorePoints.map((point, i) => {
            const principleKey = PRINCIPLE_ORDER[i];
            const handleClick = onPrincipleClick
              ? () => onPrincipleClick(principleKey)
              : undefined;

            return (
              <circle
                key={`vertex-${i}`}
                cx={point.x}
                cy={point.y}
                r={vertexRadius}
                fill={geometry.vertexColors[i]}
                stroke="var(--surface-0)"
                strokeWidth="1.5"
                className={handleClick ? 'constitutional-radar__vertex--clickable' : ''}
                onClick={handleClick}
                style={{ cursor: handleClick ? 'pointer' : 'default' }}
              />
            );
          })}
        </g>

        {/* Labels */}
        {showLabels && (
          <g className="constitutional-radar__labels">
            {PRINCIPLE_ORDER.map((key, i) => {
              const meta = PRINCIPLES[key];
              const pos = geometry.labelPositions[i];
              return (
                <text
                  key={`label-${i}`}
                  x={pos.x}
                  y={pos.y}
                  textAnchor="middle"
                  dominantBaseline="middle"
                  className="constitutional-radar__label"
                  fontSize={fontSize}
                >
                  {meta.shortLabel}
                </text>
              );
            })}
          </g>
        )}
      </svg>
    </div>
  );
});

export default ConstitutionalRadar;
