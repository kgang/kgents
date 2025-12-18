/**
 * TownTracePanel: N-gent witness for town events.
 *
 * Wraps the generic TracePanel to provide town-specific event formatting.
 * Converts TownEvent[] to TraceEvent[] with appropriate categorization.
 *
 * @see plans/park-town-design-overhaul.md (Journey 9)
 * @see spec/n-gents/witness.md
 */

import { useMemo } from 'react';
import { TracePanel, type TraceEvent } from '@/components/categorical/TracePanel';
import { TeachingCallout, TEACHING_MESSAGES } from '@/components/categorical/TeachingCallout';
import type { TownEvent } from '@/api/types';

// =============================================================================
// Types
// =============================================================================

export interface TownTracePanelProps {
  /** Town events from SSE stream */
  events: TownEvent[];
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
// Event Mapping
// =============================================================================

/**
 * Map operation names to event types for categorization.
 */
function getEventType(operation: string): TraceEvent['type'] {
  // Phase transitions
  if (['evolve', 'transform', 'transition'].includes(operation)) {
    return 'phase_transition';
  }

  // Social operations
  if (['greet', 'gossip', 'farewell', 'trade'].includes(operation)) {
    return 'operation';
  }

  // Work operations
  if (['work', 'craft', 'build', 'task', 'focus'].includes(operation)) {
    return 'operation';
  }

  // Reflection operations
  if (['reflect', 'journal', 'meditate', 'ponder'].includes(operation)) {
    return 'operation';
  }

  // Rest operations (special handling)
  if (['rest', 'wake', 'tired', 'exhaust'].includes(operation)) {
    return 'operation';
  }

  return 'custom';
}

/**
 * Get a color for the operation type.
 */
function getOperationColor(operation: string): string {
  // Social - pink
  if (['greet', 'gossip', 'farewell', 'trade'].includes(operation)) {
    return '#ec4899';
  }

  // Work - amber
  if (['work', 'craft', 'build', 'task', 'focus', 'complete'].includes(operation)) {
    return '#f59e0b';
  }

  // Reflection - purple
  if (['reflect', 'journal', 'meditate', 'ponder'].includes(operation)) {
    return '#8b5cf6';
  }

  // Rest - green
  if (['rest', 'wake', 'tired', 'exhaust', 'energized'].includes(operation)) {
    return '#22c55e';
  }

  // Evolution - gold
  if (['evolve', 'transform', 'transition'].includes(operation)) {
    return '#eab308';
  }

  return '#64748b';
}

/**
 * Convert a TownEvent to a TraceEvent.
 */
function townEventToTraceEvent(event: TownEvent, index: number): TraceEvent {
  const type = getEventType(event.operation);
  const color = getOperationColor(event.operation);

  // Extract citizen info from message if available
  let title = event.message || `${event.operation}(${event.participants.join(', ')})`;
  let description: string | undefined;

  // For phase transitions, extract from/to
  let from: string | undefined;
  let to: string | undefined;

  if (event.operation === 'evolve' || event.operation === 'transform') {
    // For evolution events, parse from message or use dialogue
    if (event.participants.length > 0) {
      title = `${event.participants[0]} evolved`;
    }
  }

  // For operations, provide arity info
  if (type === 'operation') {
    const arity = event.participants.length;
    description = `Arity: ${arity}`;
  }

  return {
    id: event.tick || index,
    timestamp: event.timestamp ? new Date(event.timestamp) : new Date(),
    type,
    title,
    description,
    from,
    to,
    color,
    data: {
      operation: event.operation,
      participants: event.participants,
      success: event.success,
    },
  };
}

// =============================================================================
// Component
// =============================================================================

export function TownTracePanel({
  events,
  maxEvents = 10,
  showScrubber = false,
  showTeaching = true,
  compact = false,
  className,
}: TownTracePanelProps) {
  // Convert town events to trace events
  const traceEvents = useMemo(() => {
    return events.map((e, i) => townEventToTraceEvent(e, i));
  }, [events]);

  return (
    <div className={className}>
      <TracePanel
        events={traceEvents}
        maxEvents={maxEvents}
        showScrubber={showScrubber}
        compact={compact}
        title="Town Witness"
      />

      {/* Teaching callout */}
      {showTeaching && events.length > 0 && !compact && (
        <div className="mt-3">
          <TeachingCallout category="conceptual" compact>
            {TEACHING_MESSAGES.witness_trace}
          </TeachingCallout>
        </div>
      )}
    </div>
  );
}

export default TownTracePanel;
