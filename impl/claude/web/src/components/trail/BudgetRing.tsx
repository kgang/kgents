/**
 * BudgetRing - Circular budget indicator for exploration trails.
 *
 * Shows consumed vs remaining budget as a circular progress ring.
 * Color transitions: green -> yellow -> red as budget depletes.
 *
 * @see spec/protocols/trail-protocol.md Section 8
 */

import { useMemo } from 'react';

// =============================================================================
// Types
// =============================================================================

interface BudgetRingProps {
  /** Budget consumed */
  consumed: number;
  /** Total budget */
  total: number;
  /** Ring size in pixels */
  size?: number;
  /** Stroke width */
  strokeWidth?: number;
  /** Optional label */
  label?: string;
  /** Optional className */
  className?: string;
}

// =============================================================================
// Component
// =============================================================================

/**
 * BudgetRing component.
 *
 * Displays budget as a circular progress indicator with color gradient.
 */
export function BudgetRing({
  consumed,
  total,
  size = 80,
  strokeWidth = 8,
  label = 'Budget',
  className = '',
}: BudgetRingProps) {
  // Calculate progress
  const progress = useMemo(() => {
    if (total === 0) return 0;
    return Math.min(100, Math.max(0, (consumed / total) * 100));
  }, [consumed, total]);

  // Calculate SVG values
  const { radius, circumference, offset, color } = useMemo(() => {
    const r = (size - strokeWidth) / 2;
    const c = 2 * Math.PI * r;
    const o = c - (progress / 100) * c;

    // Color based on progress (inverted: high progress = bad)
    let col = '#22c55e'; // green
    if (progress > 60) col = '#f59e0b'; // yellow
    if (progress > 85) col = '#ef4444'; // red

    return { radius: r, circumference: c, offset: o, color: col };
  }, [size, strokeWidth, progress]);

  const remaining = total - consumed;
  const percentRemaining = Math.round(100 - progress);

  return (
    <div
      className={`bg-gray-800 rounded-lg border border-gray-700 p-4 ${className}`}
    >
      <h3 className="text-sm font-medium text-gray-300 mb-3">{label}</h3>

      <div className="flex items-center gap-4">
        {/* Ring */}
        <div className="relative" style={{ width: size, height: size }}>
          <svg
            width={size}
            height={size}
            className="transform -rotate-90"
          >
            {/* Background circle */}
            <circle
              cx={size / 2}
              cy={size / 2}
              r={radius}
              fill="none"
              stroke="#374151"
              strokeWidth={strokeWidth}
            />

            {/* Progress circle */}
            <circle
              cx={size / 2}
              cy={size / 2}
              r={radius}
              fill="none"
              stroke={color}
              strokeWidth={strokeWidth}
              strokeLinecap="round"
              strokeDasharray={circumference}
              strokeDashoffset={offset}
              className="transition-all duration-500 ease-out"
            />
          </svg>

          {/* Center text */}
          <div className="absolute inset-0 flex items-center justify-center">
            <span
              className="text-lg font-bold"
              style={{ color }}
            >
              {percentRemaining}%
            </span>
          </div>
        </div>

        {/* Stats */}
        <div className="flex-1">
          <div className="flex items-center justify-between text-sm">
            <span className="text-gray-400">Used</span>
            <span className="text-gray-200 font-medium">{consumed}</span>
          </div>
          <div className="flex items-center justify-between text-sm mt-1">
            <span className="text-gray-400">Remaining</span>
            <span className="font-medium" style={{ color }}>
              {remaining}
            </span>
          </div>
          <div className="flex items-center justify-between text-sm mt-1">
            <span className="text-gray-400">Total</span>
            <span className="text-gray-500">{total}</span>
          </div>
        </div>
      </div>

      {/* Progress bar (alternative view) */}
      <div className="mt-4 h-1.5 bg-gray-700 rounded-full overflow-hidden">
        <div
          className="h-full rounded-full transition-all duration-500 ease-out"
          style={{
            width: `${progress}%`,
            backgroundColor: color,
          }}
        />
      </div>
    </div>
  );
}

export default BudgetRing;
