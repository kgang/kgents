/**
 * ConstitutionalRadar — 7-principle radar chart (pure SVG)
 *
 * Visualizes the 7 constitutional principles as a heptagonal radar chart.
 * Color-coded by score: green (>0.8), yellow (0.5-0.8), red (<0.5).
 *
 * Pure SVG implementation, no dependencies.
 * Brutalist design: stark, minimal, function over form.
 */

import { useMemo } from 'react';
import type { ConstitutionalAlignment } from './types';
import { PRINCIPLE_LABELS, Principle } from './types';
import './ConstitutionalRadar.css';

// =============================================================================
// Types
// =============================================================================

export interface ConstitutionalRadarProps {
  /** Alignment scores to visualize */
  alignment: ConstitutionalAlignment | null;
  /** Width of chart (default 400) */
  width?: number;
  /** Height of chart (default 400) */
  height?: number;
  /** Show principle labels */
  showLabels?: boolean;
  /** Show grid lines */
  showGrid?: boolean;
  /** Compact mode */
  compact?: boolean;
}

interface Point {
  x: number;
  y: number;
}

// =============================================================================
// Constants
// =============================================================================

/** Canonical principle order (clockwise from top) */
const PRINCIPLE_ORDER: Principle[] = [
  Principle.TASTEFUL,
  Principle.CURATED,
  Principle.ETHICAL,
  Principle.JOY_INDUCING,
  Principle.COMPOSABLE,
  Principle.HETERARCHICAL,
  Principle.GENERATIVE,
];

// =============================================================================
// Helpers
// =============================================================================

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
 * STARK BIOME: Health color mapping
 * Good (>0.8): life-sage (#4A6B4A) - healthy green
 * Medium (0.5-0.8): glow-spore (#C4A77D) - earned gold
 * Low (<0.5): accent-error (#A65D4A) - muted rust, not alarming
 */
function getHealthColor(score: number): string {
  if (score >= 0.8) return 'var(--color-life-sage)';
  if (score >= 0.5) return 'var(--color-glow-spore)';
  return 'var(--accent-error)';
}

// =============================================================================
// Component
// =============================================================================

export function ConstitutionalRadar({
  alignment,
  width = 400,
  height = 400,
  showLabels = true,
  showGrid = true,
  compact = false,
}: ConstitutionalRadarProps) {
  const size = compact ? Math.min(width, height) * 0.8 : Math.min(width, height);
  const centerX = width / 2;
  const centerY = height / 2;
  const maxRadius = (size / 2) * 0.7; // Leave space for labels

  const numPrinciples = PRINCIPLE_ORDER.length;

  // Calculate radar points
  const radarPoints = useMemo(() => {
    if (!alignment) return [];

    return PRINCIPLE_ORDER.map((principle, i) => {
      const angle = (i / numPrinciples) * 2 * Math.PI - Math.PI / 2; // Start at top
      const score = alignment.principle_scores[principle] || 0;
      const radius = score * maxRadius;
      return {
        principle,
        score,
        point: polarToCartesian(centerX, centerY, radius, angle),
        axisEnd: polarToCartesian(centerX, centerY, maxRadius, angle),
        angle,
      };
    });
  }, [alignment, centerX, centerY, maxRadius, numPrinciples]);

  // Grid circles (0.2, 0.4, 0.6, 0.8, 1.0)
  const gridCircles = [0.2, 0.4, 0.6, 0.8, 1.0];

  // Axes (one per principle)
  const axes = useMemo(() => {
    return PRINCIPLE_ORDER.map((principle, i) => {
      const angle = (i / numPrinciples) * 2 * Math.PI - Math.PI / 2;
      const end = polarToCartesian(centerX, centerY, maxRadius, angle);
      const labelPoint = polarToCartesian(centerX, centerY, maxRadius + 30, angle);
      return {
        principle,
        end,
        labelPoint,
      };
    });
  }, [centerX, centerY, maxRadius, numPrinciples]);

  // Path string for filled area
  const pathString = useMemo(() => {
    if (radarPoints.length === 0) return '';
    const points = radarPoints.map((rp) => `${rp.point.x},${rp.point.y}`).join(' L ');
    return `M ${points} Z`;
  }, [radarPoints]);

  // Empty state
  if (!alignment) {
    return (
      <div className="constitutional-radar constitutional-radar--empty">
        <span className="constitutional-radar__placeholder">No alignment data</span>
      </div>
    );
  }

  const fillColor = getHealthColor(alignment.weighted_total);

  return (
    <div className="constitutional-radar" data-compact={compact}>
      <svg
        className="constitutional-radar__svg"
        width={width}
        height={height}
        viewBox={`0 0 ${width} ${height}`}
      >
        {/* Grid circles — STARK BIOME: steel-gunmetal */}
        {showGrid &&
          gridCircles.map((level) => (
            <circle
              key={level}
              cx={centerX}
              cy={centerY}
              r={level * maxRadius}
              className="constitutional-radar__grid-circle"
              stroke="var(--color-steel-gunmetal)"
              strokeWidth="1"
              fill="none"
              opacity={level === 1.0 ? 0.5 : 0.2}
            />
          ))}

        {/* Axes — STARK BIOME: steel-gunmetal */}
        {axes.map((axis) => (
          <line
            key={axis.principle}
            x1={centerX}
            y1={centerY}
            x2={axis.end.x}
            y2={axis.end.y}
            className="constitutional-radar__axis"
            stroke="var(--color-steel-gunmetal)"
            strokeWidth="1"
            opacity={0.3}
          />
        ))}

        {/* Filled area */}
        <path
          d={pathString}
          className="constitutional-radar__area"
          fill={fillColor}
          fillOpacity={0.15}
          stroke={fillColor}
          strokeWidth="2"
        />

        {/* Score dots */}
        {radarPoints.map((rp) => (
          <g key={rp.principle}>
            <circle
              cx={rp.point.x}
              cy={rp.point.y}
              r={4}
              className="constitutional-radar__dot"
              fill={getHealthColor(rp.score)}
            />
            {/* Tooltip */}
            <title>
              {PRINCIPLE_LABELS[rp.principle]}: {(rp.score * 100).toFixed(0)}%
            </title>
          </g>
        ))}

        {/* Labels — STARK BIOME: text-secondary */}
        {showLabels &&
          axes.map((axis) => {
            const label = compact
              ? PRINCIPLE_LABELS[axis.principle].substring(0, 3)
              : PRINCIPLE_LABELS[axis.principle];
            return (
              <text
                key={axis.principle}
                x={axis.labelPoint.x}
                y={axis.labelPoint.y}
                className="constitutional-radar__label"
                textAnchor="middle"
                dominantBaseline="middle"
                fill="var(--text-secondary)"
                fontSize={compact ? '10px' : '12px'}
              >
                {label}
              </text>
            );
          })}

        {/* Center dot — STARK BIOME: steel-zinc */}
        <circle cx={centerX} cy={centerY} r={2} fill="var(--color-steel-zinc)" />
      </svg>

      {/* Score summary */}
      <div className="constitutional-radar__summary">
        <div className="constitutional-radar__score" style={{ color: fillColor }}>
          {(alignment.weighted_total * 100).toFixed(0)}%
        </div>
        {!compact && (
          <div className="constitutional-radar__score-label">
            Overall Score ({alignment.violation_count} violations)
          </div>
        )}
      </div>
    </div>
  );
}
