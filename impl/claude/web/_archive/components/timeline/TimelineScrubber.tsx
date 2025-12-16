/**
 * TimelineScrubber: Horizontal timeline for historical navigation.
 *
 * Provides a visual timeline with play controls, seek functionality,
 * and event markers. Used for replaying past simulations.
 *
 * @see plans/web-refactor/interaction-patterns.md
 */

import { useRef, useCallback, type MouseEvent, type KeyboardEvent } from 'react';
import { cn } from '@/lib/utils';
import type { HistoryMode } from '@/hooks/useHistoricalMode';

// =============================================================================
// Types
// =============================================================================

/**
 * A significant event on the timeline.
 */
export interface TimelineEvent {
  /** Tick when event occurred */
  tick: number;

  /** Event type for styling */
  type: 'citizen_action' | 'coalition_formed' | 'phase_change' | 'milestone';

  /** Short label */
  label: string;

  /** Optional detailed description */
  description?: string;
}

export interface TimelineScrubberProps {
  /** Total number of ticks */
  totalTicks: number;

  /** Current tick position */
  currentTick: number;

  /** Significant events to mark on timeline */
  events?: TimelineEvent[];

  /** Called when user seeks to a tick */
  onSeek: (tick: number) => void;

  /** Called when play is pressed */
  onPlay: () => void;

  /** Called when pause is pressed */
  onPause: () => void;

  /** Whether currently playing */
  isPlaying: boolean;

  /** Current playback speed */
  playbackSpeed?: number;

  /** Called when speed changes */
  onSpeedChange?: (speed: number) => void;

  /** Called to step forward */
  onStepForward?: () => void;

  /** Called to step backward */
  onStepBackward?: () => void;

  /** Called to return to live mode */
  onReturnToLive?: () => void;

  /** Current mode */
  mode?: HistoryMode;

  /** Additional class names */
  className?: string;
}

// =============================================================================
// Component
// =============================================================================

export function TimelineScrubber({
  totalTicks,
  currentTick,
  events = [],
  onSeek,
  onPlay,
  onPause,
  isPlaying,
  playbackSpeed = 1,
  onSpeedChange,
  onStepForward,
  onStepBackward,
  onReturnToLive,
  mode = 'historical',
  className,
}: TimelineScrubberProps) {
  const trackRef = useRef<HTMLDivElement>(null);

  // Calculate progress percentage
  const progress = totalTicks > 0 ? (currentTick / totalTicks) * 100 : 0;

  // ==========================================================================
  // Event Handlers
  // ==========================================================================

  const handleTrackClick = useCallback((e: MouseEvent<HTMLDivElement>) => {
    if (!trackRef.current) return;

    const rect = trackRef.current.getBoundingClientRect();
    const clickX = e.clientX - rect.left;
    const percentage = clickX / rect.width;
    const tick = Math.round(percentage * totalTicks);

    onSeek(Math.max(0, Math.min(tick, totalTicks)));
  }, [totalTicks, onSeek]);

  const handleKeyDown = useCallback((e: KeyboardEvent<HTMLDivElement>) => {
    switch (e.key) {
      case ' ':
      case 'k':
        e.preventDefault();
        isPlaying ? onPause() : onPlay();
        break;
      case 'ArrowLeft':
      case 'j':
        e.preventDefault();
        onStepBackward?.();
        break;
      case 'ArrowRight':
      case 'l':
        e.preventDefault();
        onStepForward?.();
        break;
      case 'Home':
        e.preventDefault();
        onSeek(0);
        break;
      case 'End':
        e.preventDefault();
        onSeek(totalTicks);
        break;
    }
  }, [isPlaying, onPlay, onPause, onStepForward, onStepBackward, onSeek, totalTicks]);

  // ==========================================================================
  // Render
  // ==========================================================================

  return (
    <div
      className={cn(
        'timeline-scrubber',
        'bg-town-surface/95 border-t border-town-accent/30',
        'px-4 py-3',
        className
      )}
      onKeyDown={handleKeyDown}
      tabIndex={0}
      role="slider"
      aria-label="Timeline scrubber"
      aria-valuemin={0}
      aria-valuemax={totalTicks}
      aria-valuenow={currentTick}
    >
      {/* Controls row */}
      <div className="flex items-center gap-4 mb-2">
        {/* Play/Pause */}
        <button
          onClick={isPlaying ? onPause : onPlay}
          className="w-10 h-10 flex items-center justify-center rounded-full bg-town-highlight hover:bg-town-highlight/80 transition-colors"
          title={isPlaying ? 'Pause (Space)' : 'Play (Space)'}
        >
          {isPlaying ? (
            <PauseIcon className="w-5 h-5" />
          ) : (
            <PlayIcon className="w-5 h-5" />
          )}
        </button>

        {/* Step controls */}
        <div className="flex items-center gap-1">
          <button
            onClick={onStepBackward}
            className="p-2 rounded hover:bg-town-accent/20 transition-colors"
            title="Step backward (←)"
          >
            <StepBackIcon className="w-4 h-4" />
          </button>
          <button
            onClick={onStepForward}
            className="p-2 rounded hover:bg-town-accent/20 transition-colors"
            title="Step forward (→)"
          >
            <StepForwardIcon className="w-4 h-4" />
          </button>
        </div>

        {/* Speed selector */}
        {onSpeedChange && (
          <div className="flex items-center gap-1 text-sm">
            <span className="text-gray-500">Speed:</span>
            {[0.5, 1, 2, 4].map((speed) => (
              <button
                key={speed}
                onClick={() => onSpeedChange(speed)}
                className={cn(
                  'px-2 py-1 rounded text-xs transition-colors',
                  speed === playbackSpeed
                    ? 'bg-town-highlight text-white'
                    : 'hover:bg-town-accent/20 text-gray-400'
                )}
              >
                {speed}x
              </button>
            ))}
          </div>
        )}

        {/* Time display */}
        <div className="flex-1 text-center">
          <span className="font-mono text-sm">
            Tick {currentTick} / {totalTicks}
          </span>
        </div>

        {/* Return to live */}
        {mode === 'historical' && onReturnToLive && (
          <button
            onClick={onReturnToLive}
            className="px-4 py-2 bg-red-500/20 hover:bg-red-500/30 text-red-300 rounded-lg text-sm transition-colors flex items-center gap-2"
          >
            <LiveIcon className="w-4 h-4" />
            Return to Live
          </button>
        )}
      </div>

      {/* Timeline track */}
      <div className="relative">
        {/* Track background */}
        <div
          ref={trackRef}
          onClick={handleTrackClick}
          className="h-8 bg-town-bg rounded-full cursor-pointer relative overflow-hidden"
        >
          {/* Progress bar */}
          <div
            className="absolute inset-y-0 left-0 bg-town-highlight/30 transition-all duration-100"
            style={{ width: `${progress}%` }}
          />

          {/* Event markers */}
          {events.map((event, i) => (
            <EventMarker
              key={`${event.tick}-${i}`}
              event={event}
              position={(event.tick / totalTicks) * 100}
              onClick={() => onSeek(event.tick)}
            />
          ))}

          {/* Current position indicator */}
          <div
            className="absolute top-1/2 -translate-y-1/2 w-4 h-4 bg-town-highlight rounded-full shadow-lg cursor-grab transition-all duration-100"
            style={{ left: `calc(${progress}% - 8px)` }}
          />
        </div>

        {/* Tick marks */}
        <div className="flex justify-between px-2 mt-1 text-xs text-gray-500">
          <span>0</span>
          <span>{Math.round(totalTicks / 4)}</span>
          <span>{Math.round(totalTicks / 2)}</span>
          <span>{Math.round((totalTicks * 3) / 4)}</span>
          <span>{totalTicks}</span>
        </div>
      </div>
    </div>
  );
}

// =============================================================================
// Sub-components
// =============================================================================

interface EventMarkerProps {
  event: TimelineEvent;
  position: number;
  onClick: () => void;
}

function EventMarker({ event, position, onClick }: EventMarkerProps) {
  const colorMap: Record<TimelineEvent['type'], string> = {
    citizen_action: 'bg-blue-400',
    coalition_formed: 'bg-green-400',
    phase_change: 'bg-yellow-400',
    milestone: 'bg-purple-400',
  };

  return (
    <button
      onClick={(e) => {
        e.stopPropagation();
        onClick();
      }}
      className={cn(
        'absolute top-1/2 -translate-y-1/2 w-2 h-2 rounded-full',
        'hover:scale-150 transition-transform cursor-pointer',
        colorMap[event.type] || 'bg-gray-400'
      )}
      style={{ left: `${position}%` }}
      title={`${event.label} (tick ${event.tick})`}
    />
  );
}

// =============================================================================
// Icons
// =============================================================================

function PlayIcon({ className }: { className?: string }) {
  return (
    <svg className={className} fill="currentColor" viewBox="0 0 20 20">
      <path
        fillRule="evenodd"
        d="M5 4a1 1 0 011.54-.84l10 6.5a1 1 0 010 1.68l-10 6.5A1 1 0 015 17V4z"
        clipRule="evenodd"
      />
    </svg>
  );
}

function PauseIcon({ className }: { className?: string }) {
  return (
    <svg className={className} fill="currentColor" viewBox="0 0 20 20">
      <path
        fillRule="evenodd"
        d="M5 4a1 1 0 011 1v10a1 1 0 11-2 0V5a1 1 0 011-1zm9 0a1 1 0 011 1v10a1 1 0 11-2 0V5a1 1 0 011-1z"
        clipRule="evenodd"
      />
    </svg>
  );
}

function StepBackIcon({ className }: { className?: string }) {
  return (
    <svg className={className} fill="currentColor" viewBox="0 0 20 20">
      <path
        fillRule="evenodd"
        d="M15.79 14.77a.75.75 0 01-1.06.02l-4.5-4.25a.75.75 0 010-1.08l4.5-4.25a.75.75 0 111.04 1.08L11.44 10l4.35 4.23a.75.75 0 01-.02 1.06zM4.25 10a.75.75 0 01.75-.75h4.5a.75.75 0 010 1.5H5a.75.75 0 01-.75-.75z"
        clipRule="evenodd"
      />
    </svg>
  );
}

function StepForwardIcon({ className }: { className?: string }) {
  return (
    <svg className={className} fill="currentColor" viewBox="0 0 20 20">
      <path
        fillRule="evenodd"
        d="M4.21 14.77a.75.75 0 001.06.02l4.5-4.25a.75.75 0 000-1.08l-4.5-4.25a.75.75 0 10-1.04 1.08L8.56 10l-4.35 4.23a.75.75 0 00.02 1.06zM15.75 10a.75.75 0 00-.75-.75h-4.5a.75.75 0 000 1.5H15a.75.75 0 00.75-.75z"
        clipRule="evenodd"
      />
    </svg>
  );
}

function LiveIcon({ className }: { className?: string }) {
  return (
    <svg className={className} fill="currentColor" viewBox="0 0 20 20">
      <circle cx="10" cy="10" r="4" className="animate-pulse" />
    </svg>
  );
}

export default TimelineScrubber;
