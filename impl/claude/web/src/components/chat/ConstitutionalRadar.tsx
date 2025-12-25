/**
 * ConstitutionalRadar — 7-point radar chart for constitutional principles
 *
 * Visualizes adherence to the 7 kgents constitutional principles:
 * - Tasteful
 * - Curated
 * - Ethical
 * - Joy-Inducing
 * - Composable
 * - Heterarchical
 * - Generative
 *
 * Pure SVG implementation (no dependencies).
 * Brutalist design: no decoration, pure function.
 */

import type { PrincipleScore } from '../../types/chat';
import './ConstitutionalRadar.css';

// =============================================================================
// Types
// =============================================================================

export interface ConstitutionalRadarProps {
  /** Principle scores (0-1 range) */
  scores: PrincipleScore;
  /** Size variant */
  size?: 'sm' | 'md' | 'lg';
  /** Show principle labels */
  showLabels?: boolean;
}

// =============================================================================
// Constants
// =============================================================================

/** Principle labels in clockwise order from top */
const PRINCIPLES = [
  'Tasteful',
  'Curated',
  'Ethical',
  'Joy-Inducing',
  'Composable',
  'Heterarchical',
  'Generative',
] as const;

/** Size dimensions (width/height in px) */
const SIZES = {
  sm: 120,
  md: 180,
  lg: 240,
} as const;

// =============================================================================
// Component
// =============================================================================

/**
 * ConstitutionalRadar — Heptagonal radar chart
 *
 * Color coding (subtle, text-based):
 * - Green (>0.8): High adherence
 * - Yellow (0.5-0.8): Medium adherence
 * - Red (<0.5): Low adherence
 */
export function ConstitutionalRadar({
  scores,
  size = 'md',
  showLabels = true,
}: ConstitutionalRadarProps) {
  const dimension = SIZES[size];
  const center = dimension / 2;
  const radius = (dimension / 2) * 0.7; // Leave room for labels

  // Extract scores in principle order
  const scoreValues = [
    scores.tasteful,
    scores.curated,
    scores.ethical,
    scores.joy_inducing,
    scores.composable,
    scores.heterarchical,
    scores.generative,
  ];

  // Calculate points for radar polygon
  const points = scoreValues.map((score, i) => {
    const angle = (Math.PI * 2 * i) / 7 - Math.PI / 2; // Start from top
    const distance = radius * score;
    return {
      x: center + distance * Math.cos(angle),
      y: center + distance * Math.sin(angle),
    };
  });

  // Calculate grid points (concentric heptagons at 0.2, 0.4, 0.6, 0.8, 1.0)
  const gridLevels = [0.2, 0.4, 0.6, 0.8, 1.0];
  const gridPolygons = gridLevels.map((level) => {
    const levelPoints = Array.from({ length: 7 }, (_, i) => {
      const angle = (Math.PI * 2 * i) / 7 - Math.PI / 2;
      const distance = radius * level;
      return {
        x: center + distance * Math.cos(angle),
        y: center + distance * Math.sin(angle),
      };
    });
    return pointsToPath(levelPoints);
  });

  // Calculate axis lines (from center to each vertex)
  const axisLines = Array.from({ length: 7 }, (_, i) => {
    const angle = (Math.PI * 2 * i) / 7 - Math.PI / 2;
    return {
      x1: center,
      y1: center,
      x2: center + radius * Math.cos(angle),
      y2: center + radius * Math.sin(angle),
    };
  });

  // Calculate label positions (outside radar)
  const labelPositions = PRINCIPLES.map((_, i) => {
    const angle = (Math.PI * 2 * i) / 7 - Math.PI / 2;
    const distance = radius * 1.15;
    return {
      x: center + distance * Math.cos(angle),
      y: center + distance * Math.sin(angle),
    };
  });

  // Calculate score colors
  const scoreColors = scoreValues.map((score) =>
    score > 0.8 ? '#fff' : score >= 0.5 ? '#ccc' : '#999'
  );

  return (
    <div
      className={`constitutional-radar constitutional-radar--${size}`}
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
          {gridPolygons.map((path, i) => (
            <path
              key={`grid-${i}`}
              d={path}
              fill="none"
              stroke="var(--brutalist-border, #333)"
              strokeWidth="1"
              opacity={0.3}
            />
          ))}
        </g>

        {/* Axis lines */}
        <g className="constitutional-radar__axes">
          {axisLines.map((line, i) => (
            <line
              key={`axis-${i}`}
              x1={line.x1}
              y1={line.y1}
              x2={line.x2}
              y2={line.y2}
              stroke="var(--brutalist-border, #333)"
              strokeWidth="1"
              opacity={0.5}
            />
          ))}
        </g>

        {/* Score polygon */}
        <g className="constitutional-radar__score">
          <polygon
            points={points.map((p) => `${p.x},${p.y}`).join(' ')}
            fill="var(--brutalist-accent, #fff)"
            fillOpacity="0.15"
            stroke="var(--brutalist-accent, #fff)"
            strokeWidth="2"
          />
        </g>

        {/* Score vertices (color-coded dots) */}
        <g className="constitutional-radar__vertices">
          {points.map((point, i) => (
            <circle
              key={`vertex-${i}`}
              cx={point.x}
              cy={point.y}
              r={size === 'sm' ? 3 : size === 'md' ? 4 : 5}
              fill={scoreColors[i]}
              stroke="var(--brutalist-bg, #0a0a0a)"
              strokeWidth="1"
            />
          ))}
        </g>

        {/* Labels */}
        {showLabels && (
          <g className="constitutional-radar__labels">
            {PRINCIPLES.map((label, i) => (
              <text
                key={`label-${i}`}
                x={labelPositions[i].x}
                y={labelPositions[i].y}
                textAnchor="middle"
                dominantBaseline="middle"
                className="constitutional-radar__label"
                fontSize={size === 'sm' ? 9 : size === 'md' ? 10 : 11}
              >
                {label}
              </text>
            ))}
          </g>
        )}
      </svg>

      {/* Score legend (optional) */}
      <div className="constitutional-radar__legend">
        {PRINCIPLES.map((label, i) => (
          <div
            key={`score-${i}`}
            className="constitutional-radar__score-item"
          >
            <span className="constitutional-radar__score-label">{label}</span>
            <span
              className="constitutional-radar__score-value"
              style={{ color: scoreColors[i] }}
            >
              {(scoreValues[i] * 100).toFixed(0)}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}

// =============================================================================
// Helpers
// =============================================================================

/**
 * Convert array of points to SVG path string.
 */
function pointsToPath(points: { x: number; y: number }[]): string {
  if (points.length === 0) return '';

  const [first, ...rest] = points;
  const pathParts = [`M ${first.x} ${first.y}`];

  for (const point of rest) {
    pathParts.push(`L ${point.x} ${point.y}`);
  }

  pathParts.push('Z'); // Close path

  return pathParts.join(' ');
}

export default ConstitutionalRadar;
