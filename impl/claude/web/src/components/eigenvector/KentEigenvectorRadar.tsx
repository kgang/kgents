/**
 * KentEigenvectorRadar: Visualize Kent's 6D personality eigenvectors.
 *
 * Kent's 6 dimensions (from agents/k/eigenvectors.py):
 * - Aesthetic: Minimalist (0) ↔ Baroque (1) — Kent is 0.15 (minimalist)
 * - Categorical: Concrete (0) ↔ Abstract (1) — Kent is 0.92 (strongly abstract)
 * - Gratitude: Utilitarian (0) ↔ Sacred (1) — Kent is 0.78 (leaning sacred)
 * - Heterarchy: Hierarchical (0) ↔ Peer-to-Peer (1) — Kent is 0.88 (strongly peer)
 * - Generativity: Documentation (0) ↔ Generation (1) — Kent is 0.90 (strongly generative)
 * - Joy: Austere (0) ↔ Playful (1) — Kent is 0.75 (leaning playful)
 *
 * This is NOT the same as the 7D artisan eigenvector radar (warmth, curiosity, etc.)
 * This is Kent's soul coordinates for K-gent governance.
 *
 * @see agents/k/eigenvectors.py
 * @see spec/protocols/metaphysical-forge.md
 */

import { useMemo } from 'react';

// Kent's 6D eigenvector dimensions
export interface KentEigenvectorDimensions {
  aesthetic: number; // 0 = minimalist, 1 = baroque
  categorical: number; // 0 = concrete, 1 = abstract
  gratitude: number; // 0 = utilitarian, 1 = sacred
  heterarchy: number; // 0 = hierarchical, 1 = peer-to-peer
  generativity: number; // 0 = documentation, 1 = generation
  joy: number; // 0 = austere, 1 = playful
}

// Default Kent values from eigenvectors.py
export const KENT_EIGENVECTORS: KentEigenvectorDimensions = {
  aesthetic: 0.15,
  categorical: 0.92,
  gratitude: 0.78,
  heterarchy: 0.88,
  generativity: 0.9,
  joy: 0.75,
};

// Dimension order for radar chart
const DIMENSION_LABELS: (keyof KentEigenvectorDimensions)[] = [
  'aesthetic',
  'categorical',
  'gratitude',
  'heterarchy',
  'generativity',
  'joy',
];

// Labels showing the axis extremes (low → high)
const DIMENSION_AXIS_LABELS: Record<keyof KentEigenvectorDimensions, [string, string]> = {
  aesthetic: ['Minimal', 'Baroque'],
  categorical: ['Concrete', 'Abstract'],
  gratitude: ['Utilitarian', 'Sacred'],
  heterarchy: ['Hierarchy', 'Peer'],
  generativity: ['Document', 'Generate'],
  joy: ['Austere', 'Playful'],
};

// Short labels for compact display
const DIMENSION_SHORT_LABELS: Record<keyof KentEigenvectorDimensions, string> = {
  aesthetic: 'Aes',
  categorical: 'Cat',
  gratitude: 'Gra',
  heterarchy: 'Het',
  generativity: 'Gen',
  joy: 'Joy',
};

interface KentEigenvectorRadarProps {
  dimensions: KentEigenvectorDimensions;
  size?: number;
  showLabels?: boolean;
  color?: string;
  animated?: boolean;
  className?: string;
}

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
  dimensions: KentEigenvectorDimensions,
  radius: number,
  center: number
): string {
  const points = DIMENSION_LABELS.map((key, index) => {
    const value = dimensions[key];
    return getRadarPoint(index, DIMENSION_LABELS.length, value, radius, center);
  });

  return points.map((p, i) => (i === 0 ? `M ${p.x} ${p.y}` : `L ${p.x} ${p.y}`)).join(' ') + ' Z';
}

export function KentEigenvectorRadar({
  dimensions,
  size = 160,
  showLabels = true,
  color = 'rgb(251 191 36)', // amber-400
  animated = true,
  className = '',
}: KentEigenvectorRadarProps) {
  const center = size / 2;
  const radius = (size / 2) * 0.7; // Leave room for labels

  // Generate path
  const mainPath = useMemo(
    () => getRadarPath(dimensions, radius, center),
    [dimensions, radius, center]
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
    const point = getRadarPoint(index, DIMENSION_LABELS.length, 1.2, radius, center);
    return { key, ...point, label: DIMENSION_SHORT_LABELS[key] };
  });

  return (
    <div className={`relative ${className}`}>
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`} className="overflow-visible">
        {/* Grid rings */}
        {gridRings.map((ringValue) => {
          const ringDimensions: KentEigenvectorDimensions = {
            aesthetic: ringValue,
            categorical: ringValue,
            gratitude: ringValue,
            heterarchy: ringValue,
            generativity: ringValue,
            joy: ringValue,
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
              r={3}
              fill={color}
              stroke="white"
              strokeWidth={1.5}
              className={animated ? 'transition-all duration-500' : ''}
            />
          );
        })}
      </svg>

      {/* Labels (positioned absolutely) */}
      {showLabels && (
        <div className="absolute inset-0 pointer-events-none">
          {labelPositions.map(({ key, x, y, label }) => (
            <div
              key={key}
              className="absolute -translate-x-1/2 -translate-y-1/2 text-center"
              style={{ left: x, top: y }}
            >
              <span className="block text-[10px] text-stone-500 font-medium">{label}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

/**
 * Compact Kent eigenvector display as horizontal bars.
 */
interface KentEigenvectorBarsProps {
  dimensions: KentEigenvectorDimensions;
  showLabels?: boolean;
  compact?: boolean;
  className?: string;
}

export function KentEigenvectorBars({
  dimensions,
  showLabels = true,
  compact = false,
  className = '',
}: KentEigenvectorBarsProps) {
  return (
    <div className={`space-y-1 ${className}`}>
      {DIMENSION_LABELS.map((key) => {
        const value = dimensions[key];
        const percentage = Math.round(value * 100);
        const [lowLabel, highLabel] = DIMENSION_AXIS_LABELS[key];

        // Color based on value
        const getColor = (v: number) => {
          if (v >= 0.7) return 'bg-amber-400';
          if (v >= 0.4) return 'bg-amber-300';
          return 'bg-stone-300';
        };

        return (
          <div key={key} className="flex items-center gap-2">
            {showLabels && (
              <span
                className="text-xs text-stone-500 w-16 truncate"
                title={`${lowLabel} ↔ ${highLabel}`}
              >
                {compact ? DIMENSION_SHORT_LABELS[key] : key}
              </span>
            )}
            <div className="flex-1 h-1.5 bg-stone-100 rounded-full overflow-hidden">
              <div
                className={`h-full rounded-full transition-all duration-500 ${getColor(value)}`}
                style={{ width: `${percentage}%` }}
              />
            </div>
            {!compact && (
              <span className="text-xs text-stone-400 w-8 text-right">{percentage}%</span>
            )}
          </div>
        );
      })}
    </div>
  );
}

export default KentEigenvectorRadar;
