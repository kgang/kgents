/**
 * TracePanel: Timeline visualization for state machine traces.
 *
 * Implements the N-gent witness pattern - showing history of state changes
 * with optional timeline scrubber and categorical interpretation.
 *
 * @see plans/park-town-design-overhaul.md
 * @see spec/n-gents/witness.md
 */

import { useState, useMemo } from 'react';
import { Clock, ChevronRight, Play, Pause, SkipBack, SkipForward } from 'lucide-react';
import { cn } from '@/lib/utils';

// =============================================================================
// Types
// =============================================================================

export interface TraceEvent {
  /** Unique event ID (monotonic) */
  id: number;
  /** Timestamp */
  timestamp: Date | string;
  /** Event type for categorization */
  type: 'phase_transition' | 'operation' | 'timer' | 'force' | 'mask' | 'custom';
  /** Human-readable title */
  title: string;
  /** Detailed description */
  description?: string;
  /** From state (for transitions) */
  from?: string;
  /** To state (for transitions) */
  to?: string;
  /** Associated data */
  data?: Record<string, unknown>;
  /** Color for the event dot */
  color?: string;
}

export interface TracePanelProps {
  /** Events to display */
  events: TraceEvent[];
  /** Max events to show (default: 10) */
  maxEvents?: number;
  /** Whether to show the timeline scrubber */
  showScrubber?: boolean;
  /** Current playback position (0-1) */
  playbackPosition?: number;
  /** Callback when playback position changes */
  onPlaybackChange?: (position: number) => void;
  /** Whether playback is active */
  isPlaying?: boolean;
  /** Callback to toggle playback */
  onPlaybackToggle?: () => void;
  /** Compact mode for sidebars */
  compact?: boolean;
  /** Additional className */
  className?: string;
  /** Title override */
  title?: string;
}

// =============================================================================
// Helpers
// =============================================================================

function formatTimestamp(ts: Date | string): string {
  const date = typeof ts === 'string' ? new Date(ts) : ts;
  return date.toLocaleTimeString(undefined, {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  });
}

function getEventColor(type: TraceEvent['type'], customColor?: string): string {
  if (customColor) return customColor;
  switch (type) {
    case 'phase_transition':
      return '#8b5cf6'; // purple
    case 'operation':
      return '#3b82f6'; // blue
    case 'timer':
      return '#f59e0b'; // amber
    case 'force':
      return '#ef4444'; // red
    case 'mask':
      return '#ec4899'; // pink
    default:
      return '#64748b'; // slate
  }
}

// =============================================================================
// Sub-components
// =============================================================================

interface TimelineScrubberProps {
  position: number;
  onChange: (position: number) => void;
  isPlaying: boolean;
  onPlayToggle: () => void;
  eventCount: number;
}

function TimelineScrubber({
  position,
  onChange,
  isPlaying,
  onPlayToggle,
  eventCount,
}: TimelineScrubberProps) {
  return (
    <div className="flex items-center gap-2 p-2 bg-slate-800/50 rounded-lg">
      {/* Playback controls */}
      <button
        onClick={() => onChange(0)}
        className="p-1 hover:bg-slate-700 rounded transition-colors"
        aria-label="Go to start"
      >
        <SkipBack className="w-4 h-4 text-gray-400" />
      </button>
      <button
        onClick={onPlayToggle}
        className="p-1 hover:bg-slate-700 rounded transition-colors"
        aria-label={isPlaying ? 'Pause' : 'Play'}
      >
        {isPlaying ? (
          <Pause className="w-4 h-4 text-gray-400" />
        ) : (
          <Play className="w-4 h-4 text-gray-400" />
        )}
      </button>
      <button
        onClick={() => onChange(1)}
        className="p-1 hover:bg-slate-700 rounded transition-colors"
        aria-label="Go to end"
      >
        <SkipForward className="w-4 h-4 text-gray-400" />
      </button>

      {/* Scrubber track */}
      <div className="flex-1 relative h-6 flex items-center">
        <div className="absolute inset-x-0 h-1 bg-slate-700 rounded-full">
          <div
            className="h-full bg-purple-500 rounded-full transition-all duration-100"
            style={{ width: `${position * 100}%` }}
          />
        </div>
        {/* Event markers */}
        {eventCount > 0 &&
          Array.from({ length: eventCount }).map((_, i) => (
            <div
              key={i}
              className="absolute w-1.5 h-1.5 bg-gray-500 rounded-full -translate-x-1/2"
              style={{ left: `${((i + 1) / eventCount) * 100}%` }}
            />
          ))}
        {/* Scrubber handle */}
        <input
          type="range"
          min={0}
          max={1}
          step={0.01}
          value={position}
          onChange={(e) => onChange(parseFloat(e.target.value))}
          className="absolute inset-0 w-full opacity-0 cursor-pointer"
        />
        <div
          className="absolute w-3 h-3 bg-white rounded-full shadow-md -translate-x-1/2 pointer-events-none"
          style={{ left: `${position * 100}%` }}
        />
      </div>

      {/* Position indicator */}
      <span className="text-xs text-gray-500 min-w-[40px] text-right">
        {Math.round(position * eventCount)}/{eventCount}
      </span>
    </div>
  );
}

interface TraceEventRowProps {
  event: TraceEvent;
  compact?: boolean;
  isHighlighted?: boolean;
}

function TraceEventRow({ event, compact, isHighlighted }: TraceEventRowProps) {
  const color = getEventColor(event.type, event.color);

  return (
    <div
      className={cn(
        'flex items-start gap-3 rounded-lg transition-colors',
        compact ? 'py-1.5 px-2' : 'py-2 px-3',
        isHighlighted ? 'bg-slate-700/50' : 'hover:bg-slate-800/30'
      )}
    >
      {/* Event ID badge */}
      <span className="flex-shrink-0 w-8 text-xs text-gray-500 font-mono text-right">
        [{event.id}]
      </span>

      {/* Color dot */}
      <div
        className="flex-shrink-0 w-2 h-2 rounded-full mt-1.5"
        style={{ backgroundColor: color }}
      />

      {/* Content */}
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2">
          <span className="font-medium text-gray-200 truncate">{event.title}</span>
          {event.from && event.to && (
            <span className="flex items-center gap-1 text-xs text-gray-500">
              <span style={{ color }}>{event.from}</span>
              <ChevronRight className="w-3 h-3" />
              <span style={{ color }}>{event.to}</span>
            </span>
          )}
        </div>
        {event.description && !compact && (
          <p className="text-xs text-gray-400 mt-0.5 truncate">{event.description}</p>
        )}
      </div>

      {/* Timestamp */}
      <span className="flex-shrink-0 text-xs text-gray-600">
        {formatTimestamp(event.timestamp)}
      </span>
    </div>
  );
}

// =============================================================================
// Main Component
// =============================================================================

export function TracePanel({
  events,
  maxEvents = 10,
  showScrubber = false,
  playbackPosition = 1,
  onPlaybackChange,
  isPlaying = false,
  onPlaybackToggle,
  compact = false,
  className,
  title = 'Trace History',
}: TracePanelProps) {
  const [localPosition, setLocalPosition] = useState(1);

  const effectivePosition = onPlaybackChange ? playbackPosition : localPosition;
  const handlePositionChange = onPlaybackChange ?? setLocalPosition;

  // Calculate which events to show based on position
  const visibleEvents = useMemo(() => {
    const cutoff = Math.ceil(effectivePosition * events.length);
    return events.slice(Math.max(0, cutoff - maxEvents), cutoff).reverse();
  }, [events, effectivePosition, maxEvents]);

  // Highlighted event (most recent at current position)
  const highlightedId = visibleEvents[0]?.id;

  if (events.length === 0) {
    return (
      <div className={cn('bg-slate-900 rounded-xl p-4', className)}>
        <div className="flex items-center gap-2 text-gray-500 mb-4">
          <Clock className="w-4 h-4" />
          <span className="text-sm font-medium">{title}</span>
        </div>
        <p className="text-center text-gray-600 text-sm py-8">No events recorded yet</p>
      </div>
    );
  }

  return (
    <div className={cn('bg-slate-900 rounded-xl', compact ? 'p-3' : 'p-4', className)}>
      {/* Header */}
      <div className="flex items-center gap-2 text-gray-400 mb-3">
        <Clock className="w-4 h-4" />
        <span className="text-sm font-medium">{title}</span>
        <span className="text-xs text-gray-600 ml-auto">
          {events.length} event{events.length !== 1 ? 's' : ''}
        </span>
      </div>

      {/* Timeline scrubber */}
      {showScrubber && onPlaybackToggle && (
        <div className="mb-3">
          <TimelineScrubber
            position={effectivePosition}
            onChange={handlePositionChange}
            isPlaying={isPlaying}
            onPlayToggle={onPlaybackToggle}
            eventCount={events.length}
          />
        </div>
      )}

      {/* Event list */}
      <div className={cn('space-y-1', compact ? 'max-h-48' : 'max-h-64', 'overflow-y-auto')}>
        {visibleEvents.map((event) => (
          <TraceEventRow
            key={event.id}
            event={event}
            compact={compact}
            isHighlighted={event.id === highlightedId}
          />
        ))}
      </div>

      {/* "Show more" indicator */}
      {events.length > maxEvents && (
        <p className="text-center text-xs text-gray-600 mt-2">
          Showing latest {Math.min(maxEvents, visibleEvents.length)} of {events.length}
        </p>
      )}
    </div>
  );
}

// =============================================================================
// Factory Helpers
// =============================================================================

let eventIdCounter = 0;

/** Create a phase transition event */
export function createPhaseTransitionEvent(
  from: string,
  to: string,
  data?: Record<string, unknown>
): TraceEvent {
  return {
    id: ++eventIdCounter,
    timestamp: new Date(),
    type: 'phase_transition',
    title: `Phase: ${from} -> ${to}`,
    from,
    to,
    data,
  };
}

/** Create a timer event */
export function createTimerEvent(timerName: string, state: string, remaining?: string): TraceEvent {
  return {
    id: ++eventIdCounter,
    timestamp: new Date(),
    type: 'timer',
    title: `Timer: ${timerName} ${state}`,
    description: remaining ? `Remaining: ${remaining}` : undefined,
    data: { timerName, state, remaining },
  };
}

/** Create a force event */
export function createForceEvent(forcesUsed: number, forcesTotal: number, reason?: string): TraceEvent {
  return {
    id: ++eventIdCounter,
    timestamp: new Date(),
    type: 'force',
    title: `Force used (${forcesUsed}/${forcesTotal})`,
    description: reason,
    data: { forcesUsed, forcesTotal, reason },
  };
}

/** Create a mask event */
export function createMaskEvent(maskName: string, action: 'don' | 'doff', affordances?: string[]): TraceEvent {
  return {
    id: ++eventIdCounter,
    timestamp: new Date(),
    type: 'mask',
    title: `Mask ${action === 'don' ? 'donned' : 'doffed'}: ${maskName}`,
    description: affordances ? `Affordances: ${affordances.join(', ')}` : undefined,
    data: { maskName, action, affordances },
  };
}

/** Reset the event counter (for testing) */
export function resetEventCounter(): void {
  eventIdCounter = 0;
}

export default TracePanel;
