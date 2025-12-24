/**
 * ValueFunctionChart — Radar chart visualization of principle scores
 *
 * Shows the 7 core kgents principles as a radar/spider chart.
 * Each axis represents one principle, value 0.0 (center) to 1.0 (edge).
 *
 * Visual encoding:
 * - Area fill: overall satisfaction (larger = better)
 * - Color: health gradient (green = good, yellow = degraded, red = critical)
 * - Dots on vertices: individual principle scores
 *
 * Stark, minimal. The structure reveals itself.
 */

import { useMemo } from 'react';
import type { ValueScore, Principle, PrincipleScore } from './types';
import { PRINCIPLE_LABELS } from './types';
import './ValueFunctionChart.css';

// =============================================================================
// Types
// =============================================================================

export interface ValueFunctionChartProps {
  /** Value score to visualize */
  valueScore: ValueScore | null;
  /** Width of chart (default 400) */
  width?: number;
  /** Height of chart (default 400) */
  height?: number;
  /** Show labels on axes */
  showLabels?: boolean;
  /** Show grid lines */
  showGrid?: boolean;
  /** Compact mode (smaller) */
  compact?: boolean;
}

interface Point {
  x: number;
  y: number;
}

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

function getHealthColor(score: number): string {
  if (score >= 0.8) return 'var(--health-healthy)';
  if (score >= 0.6) return 'var(--health-degraded)';
  if (score >= 0.4) return 'var(--health-warning)';
  return 'var(--health-critical)';
}

// =============================================================================
// Component
// =============================================================================

export function ValueFunctionChart({
  valueScore,
  width = 400,
  height = 400,
  showLabels = true,
  showGrid = true,
  compact = false,
}: ValueFunctionChartProps) {
  const size = compact ? Math.min(width, height) * 0.8 : Math.min(width, height);
  const centerX = width / 2;
  const centerY = height / 2;
  const maxRadius = (size / 2) * 0.7; // Leave space for labels

  // Sort principles in canonical order
  const principleOrder: Principle[] = useMemo(
    () => [
      'TASTEFUL',
      'CURATED',
      'ETHICAL',
      'JOY_INDUCING',
      'COMPOSABLE',
      'HETERARCHICAL',
      'GENERATIVE',
    ] as Principle[],
    []
  );

  const numPrinciples = principleOrder.length;

  // Calculate points for the radar chart
  const radarPoints = useMemo(() => {
    if (!valueScore) return [];

    const scoreMap = new Map<Principle, PrincipleScore>();
    valueScore.principle_scores.forEach((ps) => {
      scoreMap.set(ps.principle, ps);
    });

    return principleOrder.map((principle, i) => {
      const angle = (i / numPrinciples) * 2 * Math.PI - Math.PI / 2; // Start at top
      const score = scoreMap.get(principle)?.score || 0;
      const radius = score * maxRadius;
      return {
        principle,
        score,
        point: polarToCartesian(centerX, centerY, radius, angle),
        axisEnd: polarToCartesian(centerX, centerY, maxRadius, angle),
        angle,
      };
    });
  }, [valueScore, centerX, centerY, maxRadius, principleOrder, numPrinciples]);

  // Grid circles (0.25, 0.5, 0.75, 1.0)
  const gridCircles = [0.25, 0.5, 0.75, 1.0];

  // Axes (one per principle)
  const axes = useMemo(() => {
    return principleOrder.map((principle, i) => {
      const angle = (i / numPrinciples) * 2 * Math.PI - Math.PI / 2;
      const end = polarToCartesian(centerX, centerY, maxRadius, angle);
      const labelPoint = polarToCartesian(centerX, centerY, maxRadius + 30, angle);
      return {
        principle,
        end,
        labelPoint,
      };
    });
  }, [centerX, centerY, maxRadius, principleOrder, numPrinciples]);

  // Path string for filled area
  const pathString = useMemo(() => {
    if (radarPoints.length === 0) return '';
    const points = radarPoints.map((rp) => `${rp.point.x},${rp.point.y}`).join(' L ');
    return `M ${points} Z`;
  }, [radarPoints]);

  // Empty state
  if (!valueScore) {
    return (
      <div className="value-function-chart value-function-chart--empty">
        <span className="value-function-chart__placeholder">No value score</span>
      </div>
    );
  }

  const fillColor = getHealthColor(valueScore.total_score);

  return (
    <div className="value-function-chart" data-compact={compact}>
      <svg
        className="value-function-chart__svg"
        width={width}
        height={height}
        viewBox={`0 0 ${width} ${height}`}
      >
        {/* Grid circles */}
        {showGrid &&
          gridCircles.map((level) => (
            <circle
              key={level}
              cx={centerX}
              cy={centerY}
              r={level * maxRadius}
              className="value-function-chart__grid-circle"
              stroke="var(--steel-700)"
              strokeWidth="1"
              fill="none"
              opacity={level === 1.0 ? 0.5 : 0.2}
            />
          ))}

        {/* Axes */}
        {axes.map((axis) => (
          <line
            key={axis.principle}
            x1={centerX}
            y1={centerY}
            x2={axis.end.x}
            y2={axis.end.y}
            className="value-function-chart__axis"
            stroke="var(--steel-700)"
            strokeWidth="1"
            opacity={0.3}
          />
        ))}

        {/* Filled area */}
        <path
          d={pathString}
          className="value-function-chart__area"
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
              className="value-function-chart__dot"
              fill={fillColor}
            />
            {/* Tooltip on hover */}
            <title>
              {PRINCIPLE_LABELS[rp.principle]}: {(rp.score * 100).toFixed(0)}%
            </title>
          </g>
        ))}

        {/* Labels */}
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
                className="value-function-chart__label"
                textAnchor="middle"
                dominantBaseline="middle"
                fill="var(--steel-300)"
                fontSize={compact ? '10px' : '12px'}
              >
                {label}
              </text>
            );
          })}

        {/* Center dot */}
        <circle cx={centerX} cy={centerY} r={2} fill="var(--steel-600)" />
      </svg>

      {/* Score summary */}
      <div className="value-function-chart__summary">
        <div className="value-function-chart__score" style={{ color: fillColor }}>
          {(valueScore.total_score * 100).toFixed(0)}%
        </div>
        {!compact && (
          <div className="value-function-chart__score-label">
            Overall (min: {(valueScore.min_score * 100).toFixed(0)}%)
          </div>
        )}
      </div>
    </div>
  );
}
