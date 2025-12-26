/**
 * ValueCompassRadar - 7-principle radar chart for Daily Lab
 *
 * Design Goals:
 * - Visualize constitutional alignment across 7 principles
 * - Domain-calibrated weights (productivity = FLOW primary)
 * - Pure SVG implementation (no external dependencies)
 *
 * The 7 kgents Constitutional Principles:
 * 1. Tasteful - Each agent serves a clear, justified purpose
 * 2. Curated - Intentional selection over exhaustive cataloging
 * 3. Ethical - Agents augment human capability, never replace judgment
 * 4. Joy-Inducing - Delight in interaction
 * 5. Composable - Agents are morphisms in a category
 * 6. Heterarchical - Agents exist in flux, not fixed hierarchy
 * 7. Generative - Spec is compression
 *
 * @see pilots/trail-to-crystal-daily-lab/PROTO_SPEC.md
 * @see impl/claude/services/witness/daily_lab.py
 */

import { useMemo } from 'react';
import { useWindowLayout } from '../hooks/useLayoutContext';
import { LIVING_EARTH } from '../constants';

// =============================================================================
// Types
// =============================================================================

/** Principle scores (0-1 range for each) */
export interface PrincipleWeights {
  tasteful: number;
  curated: number;
  ethical: number;
  joy_inducing: number;
  composable: number;
  heterarchical: number;
  generative: number;
}

/** Domain calibration presets */
export type DomainCalibration =
  | 'balanced'
  | 'productivity'
  | 'creativity'
  | 'wellbeing'
  | 'learning';

export interface ValueCompassRadarProps {
  /** Principle weights (0-1 range) */
  weights: PrincipleWeights;

  /** Domain calibration affects which principles are emphasized */
  domain?: DomainCalibration;

  /** Size variant */
  size?: 'sm' | 'md' | 'lg';

  /** Show principle labels */
  showLabels?: boolean;

  /** Show score values in legend */
  showLegend?: boolean;

  /** Custom className */
  className?: string;

  /** Interactive: highlight on hover */
  interactive?: boolean;

  /** Callback when a principle is clicked */
  onPrincipleClick?: (principle: keyof PrincipleWeights) => void;
}

// =============================================================================
// Constants
// =============================================================================

/** Principle labels in clockwise order from top */
const PRINCIPLES: (keyof PrincipleWeights)[] = [
  'tasteful',
  'curated',
  'ethical',
  'joy_inducing',
  'composable',
  'heterarchical',
  'generative',
];

/** Display labels */
const PRINCIPLE_LABELS: Record<keyof PrincipleWeights, string> = {
  tasteful: 'Tasteful',
  curated: 'Curated',
  ethical: 'Ethical',
  joy_inducing: 'Joy',
  composable: 'Composable',
  heterarchical: 'Heterarchical',
  generative: 'Generative',
};

/** Domain calibration weights - multipliers for each principle */
const DOMAIN_CALIBRATIONS: Record<
  DomainCalibration,
  Record<keyof PrincipleWeights, number>
> = {
  balanced: {
    tasteful: 1.0,
    curated: 1.0,
    ethical: 1.0,
    joy_inducing: 1.0,
    composable: 1.0,
    heterarchical: 1.0,
    generative: 1.0,
  },
  productivity: {
    // FLOW primary - composable and generative boosted
    tasteful: 0.9,
    curated: 1.0,
    ethical: 0.8,
    joy_inducing: 1.2, // FLOW = joy in flow
    composable: 1.3,
    heterarchical: 0.9,
    generative: 1.2,
  },
  creativity: {
    // Generative and joy boosted
    tasteful: 1.2,
    curated: 0.8,
    ethical: 0.9,
    joy_inducing: 1.3,
    composable: 1.0,
    heterarchical: 1.2,
    generative: 1.4,
  },
  wellbeing: {
    // Ethical and joy boosted, heterarchical reduced
    tasteful: 1.0,
    curated: 0.9,
    ethical: 1.4,
    joy_inducing: 1.4,
    composable: 0.8,
    heterarchical: 0.7,
    generative: 0.9,
  },
  learning: {
    // Generative and curated boosted
    tasteful: 1.0,
    curated: 1.3,
    ethical: 1.0,
    joy_inducing: 1.1,
    composable: 1.2,
    heterarchical: 1.0,
    generative: 1.3,
  },
};

/** Size dimensions */
const SIZES = {
  sm: { dimension: 160, labelOffset: 1.2, fontSize: 9 },
  md: { dimension: 240, labelOffset: 1.15, fontSize: 10 },
  lg: { dimension: 320, labelOffset: 1.12, fontSize: 12 },
} as const;

// =============================================================================
// Helpers
// =============================================================================

/** Apply domain calibration to weights */
function applyCalibration(
  weights: PrincipleWeights,
  domain: DomainCalibration
): PrincipleWeights {
  const calibration = DOMAIN_CALIBRATIONS[domain];
  const result: PrincipleWeights = { ...weights };

  for (const key of PRINCIPLES) {
    result[key] = Math.min(1, weights[key] * calibration[key]);
  }

  return result;
}

/** Convert points array to SVG path */
function pointsToPath(points: { x: number; y: number }[]): string {
  if (points.length === 0) return '';
  const [first, ...rest] = points;
  const parts = [`M ${first.x} ${first.y}`];
  for (const point of rest) {
    parts.push(`L ${point.x} ${point.y}`);
  }
  parts.push('Z');
  return parts.join(' ');
}

/** Calculate polygon points for a value */
function calculatePoints(
  values: number[],
  center: number,
  radius: number
): { x: number; y: number }[] {
  return values.map((value, i) => {
    const angle = (Math.PI * 2 * i) / 7 - Math.PI / 2;
    const distance = radius * value;
    return {
      x: center + distance * Math.cos(angle),
      y: center + distance * Math.sin(angle),
    };
  });
}

/** Get color for a score value */
function getScoreColor(score: number): string {
  if (score > 0.8) return LIVING_EARTH.sage;
  if (score >= 0.5) return LIVING_EARTH.amber;
  return LIVING_EARTH.clay;
}

// =============================================================================
// Component
// =============================================================================

/**
 * ValueCompassRadar
 *
 * Heptagonal radar chart for constitutional principle visualization.
 * Supports domain calibration to emphasize relevant principles.
 *
 * @example Basic usage:
 * ```tsx
 * <ValueCompassRadar
 *   weights={{
 *     tasteful: 0.8,
 *     curated: 0.7,
 *     ethical: 0.9,
 *     joy_inducing: 0.85,
 *     composable: 0.6,
 *     heterarchical: 0.5,
 *     generative: 0.75,
 *   }}
 * />
 * ```
 *
 * @example With domain calibration:
 * ```tsx
 * <ValueCompassRadar
 *   weights={principleWeights}
 *   domain="productivity"
 *   showLegend
 * />
 * ```
 */
export function ValueCompassRadar({
  weights,
  domain = 'balanced',
  size = 'md',
  showLabels = true,
  showLegend = false,
  className = '',
  interactive = false,
  onPrincipleClick,
}: ValueCompassRadarProps) {
  useWindowLayout(); // For responsive density (reserved for future use)
  const sizeConfig = SIZES[size];

  // Apply domain calibration
  const calibratedWeights = useMemo(
    () => applyCalibration(weights, domain),
    [weights, domain]
  );

  // Calculate dimensions
  const dimension = sizeConfig.dimension;
  const center = dimension / 2;
  const radius = (dimension / 2) * 0.65; // Leave room for labels

  // Extract values in principle order
  const values = PRINCIPLES.map((p) => calibratedWeights[p]);

  // Calculate radar polygon points
  const radarPoints = useMemo(
    () => calculatePoints(values, center, radius),
    [values, center, radius]
  );

  // Calculate grid polygons (concentric at 0.2, 0.4, 0.6, 0.8, 1.0)
  const gridLevels = [0.2, 0.4, 0.6, 0.8, 1.0];
  const gridPolygons = useMemo(
    () =>
      gridLevels.map((level) => {
        const points = calculatePoints(
          Array(7).fill(level),
          center,
          radius
        );
        return pointsToPath(points);
      }),
    [center, radius]
  );

  // Calculate axis lines
  const axisLines = useMemo(
    () =>
      Array.from({ length: 7 }, (_, i) => {
        const angle = (Math.PI * 2 * i) / 7 - Math.PI / 2;
        return {
          x1: center,
          y1: center,
          x2: center + radius * Math.cos(angle),
          y2: center + radius * Math.sin(angle),
        };
      }),
    [center, radius]
  );

  // Calculate label positions
  const labelPositions = useMemo(
    () =>
      PRINCIPLES.map((_, i) => {
        const angle = (Math.PI * 2 * i) / 7 - Math.PI / 2;
        const distance = radius * sizeConfig.labelOffset;
        return {
          x: center + distance * Math.cos(angle),
          y: center + distance * Math.sin(angle),
        };
      }),
    [center, radius, sizeConfig.labelOffset]
  );

  // Handle principle click
  const handlePrincipleClick = (principle: keyof PrincipleWeights) => {
    if (interactive && onPrincipleClick) {
      onPrincipleClick(principle);
    }
  };

  return (
    <div className={`value-compass-radar ${className}`}>
      <svg
        width={dimension}
        height={dimension}
        viewBox={`0 0 ${dimension} ${dimension}`}
        role="img"
        aria-label="Constitutional principle scores radar chart"
      >
        {/* Background grid */}
        <g className="radar-grid">
          {gridPolygons.map((path, i) => (
            <path
              key={`grid-${i}`}
              d={path}
              fill="none"
              stroke={`${LIVING_EARTH.sage}33`}
              strokeWidth="1"
            />
          ))}
        </g>

        {/* Axis lines */}
        <g className="radar-axes">
          {axisLines.map((line, i) => (
            <line
              key={`axis-${i}`}
              x1={line.x1}
              y1={line.y1}
              x2={line.x2}
              y2={line.y2}
              stroke={`${LIVING_EARTH.sage}44`}
              strokeWidth="1"
            />
          ))}
        </g>

        {/* Score polygon */}
        <g className="radar-score">
          <polygon
            points={radarPoints.map((p) => `${p.x},${p.y}`).join(' ')}
            fill={`${LIVING_EARTH.amber}22`}
            stroke={LIVING_EARTH.amber}
            strokeWidth="2"
          />
        </g>

        {/* Score vertices */}
        <g className="radar-vertices">
          {radarPoints.map((point, i) => (
            <g
              key={`vertex-${i}`}
              className={interactive ? 'cursor-pointer' : ''}
              onClick={() => handlePrincipleClick(PRINCIPLES[i])}
            >
              <circle
                cx={point.x}
                cy={point.y}
                r={size === 'sm' ? 4 : size === 'md' ? 5 : 6}
                fill={getScoreColor(values[i])}
                stroke={LIVING_EARTH.bark}
                strokeWidth="2"
              />
              {interactive && (
                <circle
                  cx={point.x}
                  cy={point.y}
                  r={12}
                  fill="transparent"
                  className="hover:fill-white/10 transition-all"
                />
              )}
            </g>
          ))}
        </g>

        {/* Labels */}
        {showLabels && (
          <g className="radar-labels">
            {PRINCIPLES.map((principle, i) => (
              <text
                key={`label-${i}`}
                x={labelPositions[i].x}
                y={labelPositions[i].y}
                textAnchor="middle"
                dominantBaseline="middle"
                fontSize={sizeConfig.fontSize}
                fill={LIVING_EARTH.sand}
                className={interactive ? 'cursor-pointer hover:fill-white' : ''}
                onClick={() => handlePrincipleClick(principle)}
              >
                {PRINCIPLE_LABELS[principle]}
              </text>
            ))}
          </g>
        )}
      </svg>

      {/* Legend */}
      {showLegend && (
        <div
          className="mt-4 grid grid-cols-2 gap-x-4 gap-y-2"
          style={{ maxWidth: dimension }}
        >
          {PRINCIPLES.map((principle, i) => (
            <div
              key={principle}
              className={`flex items-center justify-between text-xs ${
                interactive ? 'cursor-pointer hover:opacity-100' : ''
              } opacity-80`}
              onClick={() => handlePrincipleClick(principle)}
            >
              <span style={{ color: LIVING_EARTH.sand }}>
                {PRINCIPLE_LABELS[principle]}
              </span>
              <span
                style={{ color: getScoreColor(values[i]) }}
                className="font-medium"
              >
                {Math.round(values[i] * 100)}
              </span>
            </div>
          ))}

          {/* Domain indicator */}
          {domain !== 'balanced' && (
            <div
              className="col-span-2 mt-2 pt-2 border-t text-xs text-center opacity-60"
              style={{
                borderColor: `${LIVING_EARTH.sage}33`,
                color: LIVING_EARTH.sand,
              }}
            >
              Calibrated for: {domain.charAt(0).toUpperCase() + domain.slice(1)}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

// =============================================================================
// Exports
// =============================================================================

export default ValueCompassRadar;
