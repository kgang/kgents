/**
 * TimerDisplay: Real-time countdown for crisis timers.
 *
 * Wave 3: Punchdrunk Park crisis practice.
 *
 * Features:
 * - Color-coded progress bar (green -> yellow -> red)
 * - Status emoji indicators
 * - Accelerated mode indicator
 * - Animated critical state
 */

import { useMemo } from 'react';
import type { ParkTimerInfo, ParkTimerStatus } from '../../api/types';
import { PARK_TIMER_CONFIG } from '../../api/types';
// Design tokens available for future use (using Tailwind classes for now)
// import { STATE_COLORS, HEALTH_COLORS } from '../../constants';

interface TimerDisplayProps {
  timer: ParkTimerInfo;
  accelerated?: boolean;
  compact?: boolean;
  className?: string;
}

/**
 * Get progress bar color class based on progress.
 * Maps timer progress to health gradient (inverted: 0% = healthy, 100% = critical)
 */
function getProgressColor(progress: number): string {
  // Timer progress: 0 = start (healthy), 1 = expired (critical)
  if (progress <= 0.3) return 'bg-green-500';  // Healthy
  if (progress <= 0.6) return 'bg-yellow-500'; // Degraded
  if (progress <= 0.85) return 'bg-orange-500'; // Warning
  return 'bg-red-500'; // Critical
}

/**
 * Get background color based on timer status.
 */
function getStatusBg(status: ParkTimerStatus): string {
  switch (status) {
    case 'ACTIVE':
      return 'bg-gray-700/50';
    case 'WARNING':
      return 'bg-yellow-900/30';
    case 'CRITICAL':
      return 'bg-red-900/40';
    case 'EXPIRED':
      return 'bg-red-900/60';
    case 'COMPLETED':
      return 'bg-green-900/30';
    default:
      return 'bg-gray-800/50';
  }
}

export function TimerDisplay({
  timer,
  accelerated = false,
  compact = false,
  className = '',
}: TimerDisplayProps) {
  const config = PARK_TIMER_CONFIG[timer.status];
  const progressColor = useMemo(() => getProgressColor(timer.progress), [timer.progress]);
  const statusBg = useMemo(() => getStatusBg(timer.status), [timer.status]);
  const isCritical = timer.status === 'CRITICAL' || timer.status === 'EXPIRED';

  if (compact) {
    return (
      <div className={`flex items-center gap-2 ${className}`}>
        <span className="font-mono text-xs" style={{ color: config.color }}>
          {config.emoji}
        </span>
        <span className="text-xs text-gray-300 font-mono">{timer.countdown}</span>
        <div className="flex-1 h-1 bg-gray-700 rounded-full overflow-hidden">
          <div
            className={`h-full rounded-full transition-all duration-300 ${progressColor}`}
            style={{ width: `${timer.progress * 100}%` }}
          />
        </div>
      </div>
    );
  }

  return (
    <div
      className={`
        rounded-lg p-4 transition-all duration-300
        ${statusBg}
        ${isCritical ? 'animate-pulse' : ''}
        ${className}
      `}
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          <span
            className="font-mono text-lg"
            style={{ color: config.color }}
          >
            {config.emoji}
          </span>
          <span className="text-sm font-medium text-gray-200">{timer.name}</span>
        </div>
        {accelerated && (
          <span className="text-xs text-gray-400 bg-gray-700 px-2 py-0.5 rounded">
            60x
          </span>
        )}
      </div>

      {/* Countdown */}
      <div className="text-center mb-3">
        <span
          className="text-3xl font-mono font-bold tracking-wider"
          style={{ color: config.color }}
        >
          {timer.countdown}
        </span>
      </div>

      {/* Progress bar */}
      <div className="h-2 bg-gray-700 rounded-full overflow-hidden mb-2">
        <div
          className={`h-full rounded-full transition-all duration-300 ${progressColor}`}
          style={{ width: `${timer.progress * 100}%` }}
        />
      </div>

      {/* Status */}
      <div className="flex items-center justify-between text-xs">
        <span className="text-gray-400">{timer.status}</span>
        <span className="text-gray-500">{Math.round(timer.progress * 100)}% elapsed</span>
      </div>
    </div>
  );
}

/**
 * Multiple timers in a row/grid.
 */
interface TimerGridProps {
  timers: ParkTimerInfo[];
  accelerated?: boolean;
  compact?: boolean;
  className?: string;
}

export function TimerGrid({
  timers,
  accelerated = false,
  compact = false,
  className = '',
}: TimerGridProps) {
  if (timers.length === 0) {
    return (
      <div className={`text-center py-4 text-gray-500 ${className}`}>
        No active timers
      </div>
    );
  }

  if (compact) {
    return (
      <div className={`space-y-2 ${className}`}>
        {timers.map((timer) => (
          <TimerDisplay
            key={timer.name}
            timer={timer}
            accelerated={accelerated}
            compact
          />
        ))}
      </div>
    );
  }

  return (
    <div className={`grid gap-4 ${timers.length === 1 ? '' : 'grid-cols-2'} ${className}`}>
      {timers.map((timer) => (
        <TimerDisplay
          key={timer.name}
          timer={timer}
          accelerated={accelerated}
        />
      ))}
    </div>
  );
}

export default TimerDisplay;
