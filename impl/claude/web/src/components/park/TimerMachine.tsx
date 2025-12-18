/**
 * TimerMachine: Timer with polynomial state machine visualization.
 *
 * Phase 3 of park-town-design-overhaul: Enhances TimerDisplay to show
 * timers as polynomial agents with their own state machines.
 *
 * Features:
 * - State machine visualization per timer
 * - Phase colors and glow effects
 * - Valid inputs based on current timer state
 * - Teaching callout for timer polynomial
 *
 * @see plans/park-town-design-overhaul.md (Journey 5: Timer State Machine)
 * @see spec/park/index.md (timer specification)
 */

import { useMemo } from 'react';
import { cn } from '@/lib/utils';
import type { ParkTimerInfo, ParkTimerStatus } from '@/api/types';
import { PARK_TIMER_CONFIG } from '@/api/types';
import { TimerStateIndicator } from '@/components/categorical/StateIndicator';
import { TeachingCallout, TEACHING_MESSAGES } from '@/components/categorical/TeachingCallout';
import { TIMER_STATE as TIMER_PRESET } from '@/components/categorical/presets';
import { TIMER_STATUS_ICONS } from '@/constants';

// =============================================================================
// Types
// =============================================================================

export interface TimerMachineProps {
  timer: ParkTimerInfo;
  accelerated?: boolean;
  showStateMachine?: boolean;
  showTeaching?: boolean;
  compact?: boolean;
  className?: string;
}

export interface TimerMachineGridProps {
  timers: ParkTimerInfo[];
  accelerated?: boolean;
  showStateMachine?: boolean;
  showTeaching?: boolean;
  compact?: boolean;
  className?: string;
}

// =============================================================================
// Helpers
// =============================================================================

/**
 * Get progress bar color based on timer progress.
 * Maps timer progress to health gradient (0 = healthy, 1 = critical)
 */
function getProgressColor(progress: number): string {
  if (progress <= 0.3) return '#22c55e'; // green
  if (progress <= 0.6) return '#f59e0b'; // amber
  if (progress <= 0.85) return '#f97316'; // orange
  return '#ef4444'; // red
}

/**
 * Map timer status to preset position ID
 */
function statusToPositionId(status: ParkTimerStatus): string {
  return status.toUpperCase();
}

/**
 * Calculate valid inputs from current timer state
 */
function getValidInputs(status: ParkTimerStatus): string[] {
  const positionId = statusToPositionId(status);
  const inputs: string[] = [];

  for (const edge of TIMER_PRESET.edges) {
    if (edge.source === positionId) {
      inputs.push(edge.label);
    }
  }

  return [...new Set(inputs)];
}

// =============================================================================
// State Machine Visualization
// =============================================================================

interface TimerStateMachineProps {
  currentStatus: ParkTimerStatus;
  compact?: boolean;
}

function TimerStateMachine({ currentStatus, compact = false }: TimerStateMachineProps) {
  const normalizedStatus = currentStatus.toUpperCase();

  return (
    <div className={cn('flex gap-1 justify-center flex-wrap', compact ? 'py-1' : 'py-2')}>
      {TIMER_PRESET.positions.map((position) => {
        const isCurrent = position.id === normalizedStatus;
        return (
          <div
            key={position.id}
            className={cn(
              'relative flex items-center justify-center rounded-lg transition-all duration-300',
              compact ? 'w-8 h-8' : 'w-12 h-12'
            )}
            style={{
              backgroundColor: `${position.color}15`,
              border: `2px solid ${isCurrent ? position.color : position.color + '30'}`,
              boxShadow: isCurrent ? `0 0 12px ${position.color}40, 0 0 0 2px ${position.color}` : 'none',
            }}
            title={`${position.label}: ${position.description}`}
          >
            <span
              className={cn('font-bold', compact ? 'text-[8px]' : 'text-xs')}
              style={{ color: isCurrent ? position.color : position.color + '80' }}
            >
              {position.label[0]}
            </span>
          </div>
        );
      })}
    </div>
  );
}

// =============================================================================
// Main Component
// =============================================================================

export function TimerMachine({
  timer,
  accelerated = false,
  showStateMachine = true,
  showTeaching = false,
  compact = false,
  className = '',
}: TimerMachineProps) {
  const config = PARK_TIMER_CONFIG[timer.status];
  const StatusIcon = TIMER_STATUS_ICONS[timer.status];
  const progressColor = useMemo(() => getProgressColor(timer.progress), [timer.progress]);
  const validInputs = useMemo(() => getValidInputs(timer.status), [timer.status]);
  const isCritical = timer.status === 'CRITICAL' || timer.status === 'EXPIRED';

  if (compact) {
    return (
      <div className={cn('bg-gray-800/50 rounded-lg p-3', className)}>
        {/* Header */}
        <div className="flex items-center gap-2 mb-2">
          <StatusIcon className="w-4 h-4" style={{ color: config.color }} />
          <span className="text-xs font-medium text-gray-300">{timer.name}</span>
          <TimerStateIndicator state={timer.status} size="sm" className="ml-auto" />
        </div>

        {/* Countdown */}
        <div
          className="text-xl font-mono font-bold text-center mb-2"
          style={{ color: config.color }}
        >
          {timer.countdown}
        </div>

        {/* Progress bar */}
        <div className="h-1.5 bg-gray-700 rounded-full overflow-hidden">
          <div
            className="h-full rounded-full transition-all duration-300"
            style={{
              width: `${timer.progress * 100}%`,
              backgroundColor: progressColor,
            }}
          />
        </div>

        {/* Mini state machine */}
        {showStateMachine && <TimerStateMachine currentStatus={timer.status} compact />}
      </div>
    );
  }

  return (
    <div
      className={cn(
        'bg-gray-800/50 rounded-xl p-4 border transition-all duration-300',
        isCritical ? 'border-red-500/50 animate-pulse' : 'border-gray-700',
        className
      )}
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <StatusIcon className="w-5 h-5" style={{ color: config.color }} />
          <span className="text-sm font-medium text-gray-200">{timer.name}</span>
        </div>
        <div className="flex items-center gap-2">
          {accelerated && (
            <span className="text-xs text-gray-400 bg-gray-700 px-2 py-0.5 rounded">
              60x
            </span>
          )}
          <TimerStateIndicator state={timer.status} size="sm" />
        </div>
      </div>

      {/* Countdown */}
      <div className="text-center mb-4">
        <span
          className="text-4xl font-mono font-bold tracking-wider"
          style={{ color: config.color }}
        >
          {timer.countdown}
        </span>
      </div>

      {/* Progress bar with markers */}
      <div className="relative mb-4">
        <div className="h-3 bg-gray-700 rounded-full overflow-hidden">
          <div
            className="h-full rounded-full transition-all duration-300"
            style={{
              width: `${timer.progress * 100}%`,
              backgroundColor: progressColor,
            }}
          />
        </div>
        {/* Threshold markers */}
        <div className="absolute inset-x-0 top-0 h-3 flex pointer-events-none">
          <div className="w-[75%]" />
          <div className="w-px h-full bg-gray-500/50" title="Warning threshold" />
          <div className="w-[15%]" />
          <div className="w-px h-full bg-red-500/50" title="Critical threshold" />
        </div>
        {/* Progress text */}
        <div className="flex justify-between text-xs text-gray-500 mt-1">
          <span>{timer.status}</span>
          <span>{Math.round(timer.progress * 100)}% elapsed</span>
        </div>
      </div>

      {/* State machine visualization */}
      {showStateMachine && (
        <div className="bg-gray-800/30 rounded-lg p-3 mb-3">
          <div className="text-xs text-gray-500 mb-2 text-center">State Machine</div>
          <TimerStateMachine currentStatus={timer.status} />
        </div>
      )}

      {/* Valid inputs */}
      <div className="flex flex-wrap gap-1.5 items-center">
        <span className="text-xs text-gray-500">Valid:</span>
        {validInputs.map((input) => (
          <span
            key={input}
            className="px-2 py-0.5 text-xs rounded-full bg-blue-500/20 text-blue-400 border border-blue-500/30"
          >
            {input}
          </span>
        ))}
      </div>

      {/* Teaching callout for critical state */}
      {showTeaching && isCritical && (
        <div className="mt-3">
          <TeachingCallout category="operational" compact>
            {TEACHING_MESSAGES.timer_polynomial}
          </TeachingCallout>
        </div>
      )}
    </div>
  );
}

// =============================================================================
// Grid Component
// =============================================================================

export function TimerMachineGrid({
  timers,
  accelerated = false,
  showStateMachine = true,
  showTeaching = false,
  compact = false,
  className = '',
}: TimerMachineGridProps) {
  if (timers.length === 0) {
    return (
      <div className={cn('text-center py-4 text-gray-500', className)}>
        No active timers
      </div>
    );
  }

  return (
    <div
      className={cn(
        'grid gap-4',
        compact
          ? 'grid-cols-2'
          : timers.length === 1
          ? 'grid-cols-1'
          : 'grid-cols-2',
        className
      )}
    >
      {timers.map((timer) => (
        <TimerMachine
          key={timer.name}
          timer={timer}
          accelerated={accelerated}
          showStateMachine={showStateMachine}
          showTeaching={showTeaching}
          compact={compact}
        />
      ))}
    </div>
  );
}

export default TimerMachine;
