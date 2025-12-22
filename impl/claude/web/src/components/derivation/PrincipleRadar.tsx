/**
 * PrincipleRadar: Radar chart visualization of 7 principle draws.
 *
 * Phase 5: Derivation Framework Visualization
 *
 * Shows how strongly an agent draws from each of the 7 principles:
 * 1. Tasteful - Each agent serves a clear, justified purpose
 * 2. Curated - Intentional selection over exhaustive cataloging
 * 3. Ethical - Agents augment human capability
 * 4. Joy-Inducing - Delight in interaction
 * 5. Composable - Agents are morphisms in a category
 * 6. Heterarchical - Agents exist in flux, not fixed hierarchy
 * 7. Generative - Spec is compression
 *
 * @example
 * ```tsx
 * <PrincipleRadar
 *   data={{
 *     agent_name: "Flux",
 *     tier: "functor",
 *     labels: ["Tasteful", "Curated", "Ethical", "Joy-Inducing", "Composable", "Heterarchical", "Generative"],
 *     data: [0.8, 0.6, 0.9, 0.7, 0.95, 0.85, 0.75],
 *     total_confidence: 0.98,
 *   }}
 * />
 * ```
 */

import { useMemo } from 'react';
import { motion } from 'framer-motion';
import type { DerivationPrinciplesResponse } from '../../api/types';
import { DERIVATION_PRINCIPLE_CONFIG } from '../../api/types';

// =============================================================================
// Types
// =============================================================================

export interface PrincipleRadarProps {
  data: DerivationPrinciplesResponse;
  size?: number;
  className?: string;
  showLegend?: boolean;
}

// =============================================================================
// Constants
// =============================================================================

const PRINCIPLES = [
  'Tasteful',
  'Curated',
  'Ethical',
  'Joy-Inducing',
  'Composable',
  'Heterarchical',
  'Generative',
];

// =============================================================================
// Helper Functions
// =============================================================================

function polarToCartesian(
  centerX: number,
  centerY: number,
  radius: number,
  angleInDegrees: number
): { x: number; y: number } {
  const angleInRadians = ((angleInDegrees - 90) * Math.PI) / 180;
  return {
    x: centerX + radius * Math.cos(angleInRadians),
    y: centerY + radius * Math.sin(angleInRadians),
  };
}

function getPolygonPoints(
  centerX: number,
  centerY: number,
  values: number[],
  maxRadius: number
): string {
  return values
    .map((value, i) => {
      const angle = (i / values.length) * 360;
      const radius = value * maxRadius;
      const { x, y } = polarToCartesian(centerX, centerY, radius, angle);
      return `${x},${y}`;
    })
    .join(' ');
}

// =============================================================================
// Component
// =============================================================================

export function PrincipleRadar({
  data,
  size = 280,
  className = '',
  showLegend = true,
}: PrincipleRadarProps) {
  const center = size / 2;
  const maxRadius = size / 2 - 40;

  // Ensure we have 7 values (pad with 0 if needed)
  const values = useMemo(() => {
    const result: number[] = [];
    for (let i = 0; i < 7; i++) {
      result.push(data.data[i] ?? 0);
    }
    return result;
  }, [data.data]);

  // Calculate polygon points
  const polygonPoints = useMemo(
    () => getPolygonPoints(center, center, values, maxRadius),
    [center, values, maxRadius]
  );

  // Grid rings at 25%, 50%, 75%, 100%
  const gridRings = [0.25, 0.5, 0.75, 1.0];

  return (
    <div className={`flex flex-col items-center ${className}`}>
      <svg width={size} height={size} className="overflow-visible">
        {/* Grid rings */}
        {gridRings.map((ring) => (
          <polygon
            key={ring}
            points={getPolygonPoints(center, center, Array(7).fill(ring), maxRadius)}
            fill="none"
            stroke="#374151"
            strokeWidth={ring === 1 ? 1.5 : 0.5}
            opacity={0.5}
          />
        ))}

        {/* Axis lines */}
        {PRINCIPLES.map((_, i) => {
          const angle = (i / 7) * 360;
          const { x: endX, y: endY } = polarToCartesian(
            center,
            center,
            maxRadius,
            angle
          );
          return (
            <line
              key={i}
              x1={center}
              y1={center}
              x2={endX}
              y2={endY}
              stroke="#374151"
              strokeWidth={0.5}
              opacity={0.5}
            />
          );
        })}

        {/* Data polygon */}
        <motion.polygon
          points={polygonPoints}
          fill="#3b82f6"
          fillOpacity={0.3}
          stroke="#3b82f6"
          strokeWidth={2}
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5 }}
        />

        {/* Data points */}
        {values.map((value, i) => {
          const angle = (i / 7) * 360;
          const radius = value * maxRadius;
          const { x, y } = polarToCartesian(center, center, radius, angle);
          const principle = PRINCIPLES[i];
          const config = DERIVATION_PRINCIPLE_CONFIG[principle] || {
            color: '#3b82f6',
          };

          return (
            <motion.circle
              key={i}
              cx={x}
              cy={y}
              r={4}
              fill={config.color}
              stroke="#fff"
              strokeWidth={1.5}
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ duration: 0.3, delay: i * 0.05 }}
            />
          );
        })}

        {/* Axis labels */}
        {PRINCIPLES.map((principle, i) => {
          const angle = (i / 7) * 360;
          const { x, y } = polarToCartesian(center, center, maxRadius + 16, angle);
          const config = DERIVATION_PRINCIPLE_CONFIG[principle] || {
            color: '#9ca3af',
          };

          // Adjust text anchor based on position
          let textAnchor: 'start' | 'middle' | 'end' = 'middle';
          if (x < center - 10) textAnchor = 'end';
          if (x > center + 10) textAnchor = 'start';

          return (
            <text
              key={i}
              x={x}
              y={y + 4}
              textAnchor={textAnchor}
              className="text-[10px] font-medium"
              fill={config.color}
            >
              {principle}
            </text>
          );
        })}

        {/* Center label */}
        <text
          x={center}
          y={center + 4}
          textAnchor="middle"
          className="text-xs font-bold fill-white"
        >
          {Math.round(data.total_confidence * 100)}%
        </text>
      </svg>

      {/* Agent info */}
      <div className="mt-4 text-center">
        <div className="text-sm font-semibold text-white">{data.agent_name}</div>
        <div className="text-xs text-gray-400">{data.tier} tier</div>
      </div>

      {/* Legend */}
      {showLegend && (
        <div className="mt-4 grid grid-cols-2 gap-x-4 gap-y-1 text-xs">
          {PRINCIPLES.map((principle, i) => {
            const config = DERIVATION_PRINCIPLE_CONFIG[principle] || {
              color: '#9ca3af',
            };
            const value = values[i];

            return (
              <div key={principle} className="flex items-center justify-between gap-2">
                <span className="flex items-center gap-1">
                  <span
                    className="w-2 h-2 rounded-full"
                    style={{ backgroundColor: config.color }}
                  />
                  <span className="text-gray-400">{principle}</span>
                </span>
                <span className="font-mono text-gray-300">
                  {Math.round(value * 100)}%
                </span>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

export default PrincipleRadar;
