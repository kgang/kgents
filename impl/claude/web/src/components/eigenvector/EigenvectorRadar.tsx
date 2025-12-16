/**
 * EigenvectorRadar: Visualize 7D personality eigenvectors.
 *
 * Wave 2: Atelier eigenvector personality in bidding UI.
 *
 * The 7 dimensions capture builder personality:
 * - Warmth: Friendliness and approachability
 * - Curiosity: Exploratory drive
 * - Trust: Reliability and consistency
 * - Creativity: Novel solution generation
 * - Patience: Tolerance for iteration
 * - Resilience: Recovery from setbacks
 * - Ambition: Drive for excellence
 *
 * This component renders a radar/spider chart showing these
 * dimensions, with optional comparison mode for compatibility.
 */

import { useMemo } from 'react';

export interface EigenvectorDimensions {
  warmth: number;
  curiosity: number;
  trust: number;
  creativity: number;
  patience: number;
  resilience: number;
  ambition: number;
}

interface EigenvectorRadarProps {
  dimensions: EigenvectorDimensions;
  size?: number;
  showLabels?: boolean;
  color?: string;
  comparison?: EigenvectorDimensions;
  comparisonColor?: string;
  animated?: boolean;
  className?: string;
}

const DIMENSION_LABELS: (keyof EigenvectorDimensions)[] = [
  'warmth',
  'curiosity',
  'trust',
  'creativity',
  'patience',
  'resilience',
  'ambition',
];

const DIMENSION_ICONS: Record<keyof EigenvectorDimensions, string> = {
  warmth: '🌡️',
  curiosity: '🔍',
  trust: '🤝',
  creativity: '✨',
  patience: '⏳',
  resilience: '💪',
  ambition: '🚀',
};

/**
 * Calculate point coordinates for a radar chart.
 */
function getRadarPoint(
  index: number,
  total: number,
  value: number,
  radius: number,
  center: number
): { x: number; y: number } {
  const angle = (Math.PI * 2 * index) / total - Math.PI / 2;
  const x = center + radius * value * Math.cos(angle);
  const y = center + radius * value * Math.sin(angle);
  return { x, y };
}

/**
 * Generate SVG path for radar polygon.
 */
function getRadarPath(
  dimensions: EigenvectorDimensions,
  radius: number,
  center: number
): string {
  const points = DIMENSION_LABELS.map((key, index) => {
    const value = dimensions[key];
    return getRadarPoint(index, DIMENSION_LABELS.length, value, radius, center);
  });

  return (
    points.map((p, i) => (i === 0 ? `M ${p.x} ${p.y}` : `L ${p.x} ${p.y}`)).join(' ') + ' Z'
  );
}

export function EigenvectorRadar({
  dimensions,
  size = 200,
  showLabels = true,
  color = 'rgb(251 191 36)', // amber-400
  comparison,
  comparisonColor = 'rgb(168 162 158)', // stone-400
  animated = true,
  className = '',
}: EigenvectorRadarProps) {
  const center = size / 2;
  const radius = (size / 2) * 0.75; // Leave room for labels

  // Generate paths
  const mainPath = useMemo(
    () => getRadarPath(dimensions, radius, center),
    [dimensions, radius, center]
  );

  const comparisonPath = useMemo(
    () => (comparison ? getRadarPath(comparison, radius, center) : null),
    [comparison, radius, center]
  );

  // Generate grid rings
  const gridRings = [0.25, 0.5, 0.75, 1.0];

  // Generate axis lines
  const axisLines = DIMENSION_LABELS.map((_, index) => {
    const endPoint = getRadarPoint(index, DIMENSION_LABELS.length, 1, radius, center);
    return { x1: center, y1: center, x2: endPoint.x, y2: endPoint.y };
  });

  // Generate label positions
  const labelPositions = DIMENSION_LABELS.map((key, index) => {
    const point = getRadarPoint(index, DIMENSION_LABELS.length, 1.15, radius, center);
    return { key, ...point, icon: DIMENSION_ICONS[key] };
  });

  return (
    <div className={`relative ${className}`}>
      <svg
        width={size}
        height={size}
        viewBox={`0 0 ${size} ${size}`}
        className="overflow-visible"
      >
        {/* Grid rings */}
        {gridRings.map((ringValue) => {
          const ringDimensions: EigenvectorDimensions = {
            warmth: ringValue,
            curiosity: ringValue,
            trust: ringValue,
            creativity: ringValue,
            patience: ringValue,
            resilience: ringValue,
            ambition: ringValue,
          };
          const ringPath = getRadarPath(ringDimensions, radius, center);
          return (
            <path
              key={ringValue}
              d={ringPath}
              fill="none"
              stroke="rgb(214 211 209)" // stone-300
              strokeWidth={1}
              opacity={0.5}
            />
          );
        })}

        {/* Axis lines */}
        {axisLines.map((line, index) => (
          <line
            key={index}
            {...line}
            stroke="rgb(214 211 209)" // stone-300
            strokeWidth={1}
            opacity={0.3}
          />
        ))}

        {/* Comparison polygon (background) */}
        {comparisonPath && (
          <path
            d={comparisonPath}
            fill={comparisonColor}
            fillOpacity={0.2}
            stroke={comparisonColor}
            strokeWidth={1}
            strokeOpacity={0.5}
            className={animated ? 'transition-all duration-500' : ''}
          />
        )}

        {/* Main polygon */}
        <path
          d={mainPath}
          fill={color}
          fillOpacity={0.3}
          stroke={color}
          strokeWidth={2}
          className={animated ? 'transition-all duration-500' : ''}
        />

        {/* Data points */}
        {DIMENSION_LABELS.map((key, index) => {
          const point = getRadarPoint(
            index,
            DIMENSION_LABELS.length,
            dimensions[key],
            radius,
            center
          );
          return (
            <circle
              key={key}
              cx={point.x}
              cy={point.y}
              r={4}
              fill={color}
              stroke="white"
              strokeWidth={2}
              className={animated ? 'transition-all duration-500' : ''}
            />
          );
        })}
      </svg>

      {/* Labels (positioned absolutely) */}
      {showLabels && (
        <div className="absolute inset-0 pointer-events-none">
          {labelPositions.map(({ key, x, y, icon }) => (
            <div
              key={key}
              className="absolute -translate-x-1/2 -translate-y-1/2 text-center"
              style={{ left: x, top: y }}
            >
              <span className="text-xs">{icon}</span>
              <span className="block text-[10px] text-stone-500 capitalize">
                {key}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

/**
 * Compact eigenvector display as horizontal bars.
 */
interface EigenvectorBarsProps {
  dimensions: EigenvectorDimensions;
  showLabels?: boolean;
  compact?: boolean;
  className?: string;
}

export function EigenvectorBars({
  dimensions,
  showLabels = true,
  compact = false,
  className = '',
}: EigenvectorBarsProps) {
  return (
    <div className={`space-y-1 ${className}`}>
      {DIMENSION_LABELS.map((key) => {
        const value = dimensions[key];
        const percentage = Math.round(value * 100);

        // Color based on value
        const getColor = (v: number) => {
          if (v >= 0.7) return 'bg-emerald-400';
          if (v >= 0.4) return 'bg-amber-400';
          return 'bg-stone-300';
        };

        return (
          <div key={key} className="flex items-center gap-2">
            {showLabels && (
              <span className="text-xs text-stone-500 w-16 capitalize truncate">
                {compact ? DIMENSION_ICONS[key] : key}
              </span>
            )}
            <div className="flex-1 h-1.5 bg-stone-100 rounded-full overflow-hidden">
              <div
                className={`h-full rounded-full transition-all duration-500 ${getColor(value)}`}
                style={{ width: `${percentage}%` }}
              />
            </div>
            {!compact && (
              <span className="text-xs text-stone-400 w-8 text-right">
                {percentage}%
              </span>
            )}
          </div>
        );
      })}
    </div>
  );
}

/**
 * Compatibility score display between two eigenvectors.
 */
interface CompatibilityScoreProps {
  builderA: string;
  builderB: string;
  dimensionsA: EigenvectorDimensions;
  dimensionsB: EigenvectorDimensions;
  showDetails?: boolean;
  className?: string;
}

export function CompatibilityScore({
  builderA,
  builderB,
  dimensionsA,
  dimensionsB,
  showDetails = false,
  className = '',
}: CompatibilityScoreProps) {
  // Calculate compatibility per dimension (using cosine similarity concept)
  const perDimension = useMemo(() => {
    return DIMENSION_LABELS.map((key) => ({
      key,
      a: dimensionsA[key],
      b: dimensionsB[key],
      // Simple compatibility: 1 - absolute difference
      compatibility: 1 - Math.abs(dimensionsA[key] - dimensionsB[key]),
    }));
  }, [dimensionsA, dimensionsB]);

  // Overall compatibility (average)
  const overall = useMemo(() => {
    const sum = perDimension.reduce((acc, d) => acc + d.compatibility, 0);
    return sum / perDimension.length;
  }, [perDimension]);

  const overallPercent = Math.round(overall * 100);

  // Color based on compatibility
  const getCompatColor = (v: number) => {
    if (v >= 0.8) return 'text-emerald-500';
    if (v >= 0.6) return 'text-amber-500';
    return 'text-stone-400';
  };

  const getBgColor = (v: number) => {
    if (v >= 0.8) return 'bg-emerald-50';
    if (v >= 0.6) return 'bg-amber-50';
    return 'bg-stone-50';
  };

  return (
    <div className={`${getBgColor(overall)} rounded-lg p-3 ${className}`}>
      <div className="flex items-center justify-between mb-2">
        <div className="text-sm text-stone-600">
          <span className="font-medium">{builderA}</span>
          <span className="text-stone-400 mx-1">&</span>
          <span className="font-medium">{builderB}</span>
        </div>
        <div className={`text-lg font-bold ${getCompatColor(overall)}`}>
          {overallPercent}%
        </div>
      </div>

      {/* Compatibility bar */}
      <div className="h-2 bg-stone-200 rounded-full overflow-hidden mb-2">
        <div
          className={`h-full rounded-full transition-all duration-500 ${
            overall >= 0.8
              ? 'bg-emerald-400'
              : overall >= 0.6
                ? 'bg-amber-400'
                : 'bg-stone-300'
          }`}
          style={{ width: `${overallPercent}%` }}
        />
      </div>

      {showDetails && (
        <div className="grid grid-cols-7 gap-1 mt-2">
          {perDimension.map(({ key, compatibility }) => (
            <div key={key} className="text-center">
              <span className="text-xs">{DIMENSION_ICONS[key]}</span>
              <div
                className={`text-[10px] ${
                  compatibility >= 0.8
                    ? 'text-emerald-500'
                    : compatibility >= 0.6
                      ? 'text-amber-500'
                      : 'text-stone-400'
                }`}
              >
                {Math.round(compatibility * 100)}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default EigenvectorRadar;
