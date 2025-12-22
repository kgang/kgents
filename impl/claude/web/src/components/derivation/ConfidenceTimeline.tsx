/**
 * ConfidenceTimeline: Line chart of confidence over time.
 *
 * Phase 5: Derivation Framework Visualization
 *
 * Shows how confidence components have changed over time:
 * - Stacked area for inherited/empirical/stigmergic
 * - Total line overlay
 * - Tier ceiling as horizontal limit
 *
 * Note: Historical data requires D-gent persistence (future).
 * Currently shows single snapshot with projected structure.
 *
 * @example
 * ```tsx
 * <ConfidenceTimeline
 *   data={{
 *     agent_name: "Flux",
 *     tier_ceiling: 0.98,
 *     points: [
 *       { timestamp: "2025-01-01T00:00:00Z", inherited: 0.95, empirical: 0.5, stigmergic: 0.3, total: 0.97 }
 *     ]
 *   }}
 * />
 * ```
 */

import { useMemo } from 'react';
import { motion } from 'framer-motion';
import type { DerivationTimelineResponse, ConfidenceTimePoint } from '../../api/types';

// =============================================================================
// Types
// =============================================================================

export interface ConfidenceTimelineProps {
  data: DerivationTimelineResponse;
  width?: number;
  height?: number;
  className?: string;
}

// =============================================================================
// Constants
// =============================================================================

const COLORS = {
  inherited: '#3b82f6',
  empirical: '#22c55e',
  stigmergic: '#f59e0b',
  total: '#ffffff',
  ceiling: '#ef4444',
};

const PADDING = { top: 20, right: 20, bottom: 40, left: 50 };

// =============================================================================
// Helper Functions
// =============================================================================

function formatTime(timestamp: string): string {
  const date = new Date(timestamp);
  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

// =============================================================================
// Component
// =============================================================================

export function ConfidenceTimeline({
  data,
  width = 500,
  height = 200,
  className = '',
}: ConfidenceTimelineProps) {
  const chartWidth = width - PADDING.left - PADDING.right;
  const chartHeight = height - PADDING.top - PADDING.bottom;

  // Generate synthetic points if only one exists (for visual structure)
  const points = useMemo((): ConfidenceTimePoint[] => {
    if (data.points.length >= 2) return data.points;

    // If single point, create a "history" for visual effect
    if (data.points.length === 1) {
      const p = data.points[0];
      const now = new Date(p.timestamp);

      // Generate 5 synthetic historical points
      return Array.from({ length: 6 }, (_, i) => {
        const time = new Date(now.getTime() - (5 - i) * 60000); // 1 minute intervals
        const factor = 0.8 + (i / 5) * 0.2; // Ramp up to current

        return {
          timestamp: time.toISOString(),
          inherited: p.inherited * factor,
          empirical: p.empirical * (0.5 + (i / 5) * 0.5),
          stigmergic: p.stigmergic * (i / 5),
          total: p.total * factor,
        };
      });
    }

    return [];
  }, [data.points]);

  // Scale functions
  const xScale = (index: number) =>
    PADDING.left + (index / Math.max(points.length - 1, 1)) * chartWidth;

  const yScale = (value: number) =>
    PADDING.top + chartHeight - (value / data.tier_ceiling) * chartHeight;

  // Generate paths
  const generatePath = (
    key: keyof Pick<ConfidenceTimePoint, 'inherited' | 'empirical' | 'stigmergic' | 'total'>
  ): string => {
    if (points.length === 0) return '';

    return points
      .map((p, i) => `${i === 0 ? 'M' : 'L'} ${xScale(i)} ${yScale(p[key])}`)
      .join(' ');
  };

  // Generate area path (for stacked area)
  const generateAreaPath = (
    key: keyof Pick<ConfidenceTimePoint, 'inherited' | 'empirical' | 'stigmergic'>
  ): string => {
    if (points.length === 0) return '';

    const topLine = points
      .map((p, i) => `${i === 0 ? 'M' : 'L'} ${xScale(i)} ${yScale(p[key])}`)
      .join(' ');

    const bottomLine = points
      .reverse()
      .map((_, i) => `L ${xScale(points.length - 1 - i)} ${yScale(0)}`)
      .join(' ');

    return `${topLine} ${bottomLine} Z`;
  };

  return (
    <div className={`bg-gray-900 rounded-lg p-4 ${className}`}>
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-sm font-semibold text-white">
          {data.agent_name} Confidence History
        </h3>
        <span className="text-xs text-gray-400">
          Ceiling: {Math.round(data.tier_ceiling * 100)}%
        </span>
      </div>

      <svg width={width} height={height} className="overflow-visible">
        {/* Y-axis grid lines */}
        {[0, 0.25, 0.5, 0.75, 1].map((tick) => {
          const y = yScale(tick * data.tier_ceiling);
          return (
            <g key={tick}>
              <line
                x1={PADDING.left}
                y1={y}
                x2={width - PADDING.right}
                y2={y}
                stroke="#374151"
                strokeWidth={tick === 1 ? 1 : 0.5}
                strokeDasharray={tick === 1 ? undefined : '4 2'}
              />
              <text
                x={PADDING.left - 8}
                y={y + 4}
                textAnchor="end"
                className="text-[10px] fill-gray-500"
              >
                {Math.round(tick * data.tier_ceiling * 100)}%
              </text>
            </g>
          );
        })}

        {/* Tier ceiling line */}
        <line
          x1={PADDING.left}
          y1={yScale(data.tier_ceiling)}
          x2={width - PADDING.right}
          y2={yScale(data.tier_ceiling)}
          stroke={COLORS.ceiling}
          strokeWidth={1.5}
          strokeDasharray="4 2"
        />

        {/* Stacked areas */}
        {points.length > 0 && (
          <>
            {/* Inherited area */}
            <motion.path
              d={generateAreaPath('inherited')}
              fill={COLORS.inherited}
              opacity={0.2}
              initial={{ opacity: 0 }}
              animate={{ opacity: 0.2 }}
              transition={{ duration: 0.5 }}
            />

            {/* Lines */}
            <motion.path
              d={generatePath('inherited')}
              fill="none"
              stroke={COLORS.inherited}
              strokeWidth={2}
              initial={{ pathLength: 0 }}
              animate={{ pathLength: 1 }}
              transition={{ duration: 1 }}
            />

            <motion.path
              d={generatePath('empirical')}
              fill="none"
              stroke={COLORS.empirical}
              strokeWidth={1.5}
              strokeDasharray="4 2"
              initial={{ pathLength: 0 }}
              animate={{ pathLength: 1 }}
              transition={{ duration: 1, delay: 0.2 }}
            />

            <motion.path
              d={generatePath('stigmergic')}
              fill="none"
              stroke={COLORS.stigmergic}
              strokeWidth={1.5}
              strokeDasharray="2 2"
              initial={{ pathLength: 0 }}
              animate={{ pathLength: 1 }}
              transition={{ duration: 1, delay: 0.4 }}
            />

            {/* Total line (bold) */}
            <motion.path
              d={generatePath('total')}
              fill="none"
              stroke={COLORS.total}
              strokeWidth={2.5}
              initial={{ pathLength: 0 }}
              animate={{ pathLength: 1 }}
              transition={{ duration: 1, delay: 0.6 }}
            />

            {/* Data points on total */}
            {points.map((p, i) => (
              <motion.circle
                key={i}
                cx={xScale(i)}
                cy={yScale(p.total)}
                r={3}
                fill={COLORS.total}
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ duration: 0.2, delay: 0.6 + i * 0.05 }}
              />
            ))}
          </>
        )}

        {/* X-axis labels */}
        {points.length > 1 && (
          <>
            <text
              x={xScale(0)}
              y={height - 10}
              textAnchor="start"
              className="text-[10px] fill-gray-500"
            >
              {formatTime(points[0].timestamp)}
            </text>
            <text
              x={xScale(points.length - 1)}
              y={height - 10}
              textAnchor="end"
              className="text-[10px] fill-gray-500"
            >
              {formatTime(points[points.length - 1].timestamp)}
            </text>
          </>
        )}
      </svg>

      {/* Legend */}
      <div className="flex gap-4 mt-4 text-xs justify-center">
        <span className="flex items-center gap-1">
          <span className="w-3 h-0.5 rounded" style={{ backgroundColor: COLORS.inherited }} />
          Inherited
        </span>
        <span className="flex items-center gap-1">
          <span
            className="w-3 h-0.5 rounded"
            style={{ backgroundColor: COLORS.empirical, opacity: 0.7 }}
          />
          Empirical
        </span>
        <span className="flex items-center gap-1">
          <span
            className="w-3 h-0.5 rounded"
            style={{ backgroundColor: COLORS.stigmergic, opacity: 0.7 }}
          />
          Stigmergic
        </span>
        <span className="flex items-center gap-1">
          <span className="w-3 h-0.5 rounded bg-white" />
          Total
        </span>
        <span className="flex items-center gap-1">
          <span
            className="w-3 h-0.5 rounded"
            style={{ backgroundColor: COLORS.ceiling }}
          />
          Ceiling
        </span>
      </div>

      {/* Note about historical data */}
      {data.points.length <= 1 && (
        <div className="mt-4 text-center text-xs text-gray-500">
          Historical data requires D-gent persistence (showing synthetic preview)
        </div>
      )}
    </div>
  );
}

export default ConfidenceTimeline;
