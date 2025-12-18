/**
 * ParkTracePanel: N-gent witness for park scenario events.
 *
 * Phase 3 of park-town-design-overhaul: Provides trace history for
 * Punchdrunk Park scenarios, showing:
 * - Phase transitions with consent debt changes
 * - Timer events (warning, critical, expired)
 * - Force usage
 * - Mask donning/doffing
 *
 * @see plans/park-town-design-overhaul.md (Journey 9: Trace History)
 * @see spec/n-gents/witness.md
 */

import { useMemo } from 'react';
import { cn } from '@/lib/utils';
import {
  TracePanel,
  type TraceEvent,
  createPhaseTransitionEvent,
  createTimerEvent,
  createForceEvent,
  createMaskEvent,
} from '@/components/categorical/TracePanel';
import { TeachingCallout, TEACHING_MESSAGES } from '@/components/categorical/TeachingCallout';
import type { ParkScenarioState, ParkCrisisPhase, ParkTimerInfo, ParkMaskInfo } from '@/api/types';
import { PARK_PHASE_CONFIG } from '@/api/types';

// =============================================================================
// Types
// =============================================================================

export interface ParkTracePanelProps {
  /** Phase transitions from scenario */
  phaseTransitions: ParkScenarioState['phase_transitions'];
  /** Current timers for event context */
  timers?: ParkTimerInfo[];
  /** Current mask for event context */
  currentMask?: ParkMaskInfo | null;
  /** Forces used count */
  forcesUsed?: number;
  /** Maximum events to show */
  maxEvents?: number;
  /** Whether to show the timeline scrubber */
  showScrubber?: boolean;
  /** Whether to show the teaching callout */
  showTeaching?: boolean;
  /** Compact mode for sidebars */
  compact?: boolean;
  /** Additional className */
  className?: string;
}

// =============================================================================
// Event Builders
// =============================================================================

/**
 * Convert phase transitions to trace events.
 */
function buildPhaseTransitionEvents(
  transitions: ParkScenarioState['phase_transitions']
): TraceEvent[] {
  return transitions.map((t) => {
    return createPhaseTransitionEvent(
      t.from,
      t.to,
      {
        consent_debt: `${Math.round(t.consent_debt * 100)}%`,
      }
    );
  });
}

/**
 * Build timer events from current timer states.
 * Only includes timers in WARNING, CRITICAL, or EXPIRED states.
 */
function buildTimerEvents(timers: ParkTimerInfo[]): TraceEvent[] {
  return timers
    .filter((t) => ['WARNING', 'CRITICAL', 'EXPIRED'].includes(t.status))
    .map((timer) => {
      let description = '';
      if (timer.status === 'WARNING') {
        description = `Remaining: ${timer.countdown}`;
      } else if (timer.status === 'CRITICAL') {
        description = `Critical! ${timer.countdown} remaining`;
      } else if (timer.status === 'EXPIRED') {
        description = 'Time exhausted';
      }

      return createTimerEvent(timer.name, timer.status, description);
    });
}

/**
 * Build force events from usage count.
 */
function buildForceEvents(forcesUsed: number): TraceEvent[] {
  return Array.from({ length: forcesUsed }).map((_, i) =>
    createForceEvent(i + 1, 3, `Force ${i + 1} used`)
  );
}

/**
 * Build mask event from current mask.
 */
function buildMaskEvent(mask: ParkMaskInfo | null | undefined): TraceEvent[] {
  if (!mask) return [];

  return [
    createMaskEvent(mask.name, 'don', mask.special_abilities),
  ];
}

// =============================================================================
// Component
// =============================================================================

export function ParkTracePanel({
  phaseTransitions,
  timers = [],
  currentMask,
  forcesUsed = 0,
  maxEvents = 10,
  showScrubber = false,
  showTeaching = true,
  compact = false,
  className,
}: ParkTracePanelProps) {
  // Build all trace events from different sources
  const traceEvents = useMemo(() => {
    const phaseEvents = buildPhaseTransitionEvents(phaseTransitions);
    const timerEvents = buildTimerEvents(timers);
    const forceEvents = buildForceEvents(forcesUsed);
    const maskEvents = buildMaskEvent(currentMask);

    // Combine and sort by ID (proxy for chronological order)
    const allEvents = [...phaseEvents, ...timerEvents, ...forceEvents, ...maskEvents];
    return allEvents.sort((a, b) => a.id - b.id);
  }, [phaseTransitions, timers, forcesUsed, currentMask]);

  // Calculate summary stats
  const stats = useMemo(() => {
    const phaseCount = phaseTransitions.length;
    const timerWarnings = timers.filter((t) => t.status === 'WARNING').length;
    const timerCritical = timers.filter((t) => t.status === 'CRITICAL').length;
    const timerExpired = timers.filter((t) => t.status === 'EXPIRED').length;

    return {
      phaseCount,
      timerWarnings,
      timerCritical,
      timerExpired,
      forcesUsed,
      hasMask: !!currentMask,
    };
  }, [phaseTransitions, timers, forcesUsed, currentMask]);

  if (compact) {
    return (
      <div className={cn('space-y-2', className)}>
        {/* Compact stats row */}
        <div className="flex items-center gap-2 text-xs text-gray-400">
          <span>Phases: {stats.phaseCount}</span>
          <span>•</span>
          <span>Forces: {stats.forcesUsed}/3</span>
          {stats.timerCritical > 0 && (
            <>
              <span>•</span>
              <span className="text-red-400">Critical: {stats.timerCritical}</span>
            </>
          )}
        </div>

        {/* Compact trace */}
        <TracePanel
          events={traceEvents}
          maxEvents={maxEvents}
          showScrubber={false}
          compact
          title="Park Witness"
        />
      </div>
    );
  }

  return (
    <div className={cn('space-y-4', className)}>
      {/* Stats header */}
      <div className="bg-gray-800/30 rounded-lg p-3">
        <div className="grid grid-cols-4 gap-2 text-center">
          <div>
            <p className="text-lg font-bold text-gray-200">{stats.phaseCount}</p>
            <p className="text-xs text-gray-500">Phases</p>
          </div>
          <div>
            <p
              className={cn(
                'text-lg font-bold',
                stats.forcesUsed > 0 ? 'text-red-400' : 'text-gray-200'
              )}
            >
              {stats.forcesUsed}/3
            </p>
            <p className="text-xs text-gray-500">Forces</p>
          </div>
          <div>
            <p
              className={cn(
                'text-lg font-bold',
                stats.timerCritical > 0
                  ? 'text-red-400'
                  : stats.timerWarnings > 0
                  ? 'text-amber-400'
                  : 'text-gray-200'
              )}
            >
              {stats.timerWarnings + stats.timerCritical}
            </p>
            <p className="text-xs text-gray-500">Alerts</p>
          </div>
          <div>
            <p className={cn('text-lg font-bold', stats.hasMask ? 'text-purple-400' : 'text-gray-500')}>
              {stats.hasMask ? '1' : '0'}
            </p>
            <p className="text-xs text-gray-500">Mask</p>
          </div>
        </div>
      </div>

      {/* Main trace panel */}
      <TracePanel
        events={traceEvents}
        maxEvents={maxEvents}
        showScrubber={showScrubber}
        compact={false}
        title="Scenario Witness"
      />

      {/* Teaching callout */}
      {showTeaching && traceEvents.length > 0 && (
        <TeachingCallout category="conceptual" compact>
          {TEACHING_MESSAGES.witness_trace}
        </TeachingCallout>
      )}
    </div>
  );
}

export default ParkTracePanel;
