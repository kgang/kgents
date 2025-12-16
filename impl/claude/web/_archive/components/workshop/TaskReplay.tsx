/**
 * TaskReplay: Replay task execution with scrubber (Chunk 9).
 *
 * Shows a mini mesa with replay state, event log synced to timeline,
 * and playback controls.
 */

import { useEffect, useRef, useCallback, useState } from 'react';
import { useWorkshopStore } from '@/stores/workshopStore';
import { workshopApi } from '@/api/client';
import { BUILDER_COLORS, BUILDER_ICONS, type BuilderArchetype, type WorkshopEvent } from '@/api/types';

interface TaskReplayProps {
  taskId: string;
  onClose: () => void;
}

export function TaskReplay({ taskId, onClose }: TaskReplayProps) {
  const {
    replay,
    startReplay,
    stepReplay,
    seekReplay,
    setReplaySpeed,
    toggleReplayPlaying,
    stopReplay,
  } = useWorkshopStore();

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [taskDescription, setTaskDescription] = useState('');
  const intervalRef = useRef<number | null>(null);
  const eventListRef = useRef<HTMLDivElement>(null);

  // Load task events
  useEffect(() => {
    const loadEvents = async () => {
      setLoading(true);
      setError(null);
      try {
        const [eventsResponse, detailResponse] = await Promise.all([
          workshopApi.getTaskEvents(taskId),
          workshopApi.getTaskDetail(taskId),
        ]);
        setTaskDescription(detailResponse.data.task.description);
        startReplay(taskId, eventsResponse.data.events, eventsResponse.data.duration_seconds);
      } catch (err: unknown) {
        const axiosErr = err as { response?: { data?: { detail?: string } } };
        setError(axiosErr.response?.data?.detail || 'Failed to load task');
      } finally {
        setLoading(false);
      }
    };

    loadEvents();

    return () => {
      stopReplay();
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [taskId, startReplay, stopReplay]);

  // Handle playback
  useEffect(() => {
    if (replay?.isPlaying) {
      intervalRef.current = window.setInterval(() => {
        stepReplay(1);
      }, 1000 / (replay.playbackSpeed || 1));
    } else if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [replay?.isPlaying, replay?.playbackSpeed, stepReplay]);

  // Auto-pause at end
  useEffect(() => {
    if (replay && replay.currentIndex >= replay.events.length - 1 && replay.isPlaying) {
      toggleReplayPlaying();
    }
  }, [replay?.currentIndex, replay?.events.length, replay?.isPlaying, toggleReplayPlaying]);

  // Scroll event list to current event
  useEffect(() => {
    if (replay && eventListRef.current) {
      const currentEvent = eventListRef.current.querySelector(`[data-index="${replay.currentIndex}"]`);
      if (currentEvent) {
        currentEvent.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
      }
    }
  }, [replay?.currentIndex]);

  const handleSliderChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const index = parseInt(e.target.value, 10);
      seekReplay(index);
    },
    [seekReplay]
  );

  const formatTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  if (loading) {
    return (
      <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50">
        <div className="text-center">
          <div className="animate-pulse text-4xl mb-2">🔄</div>
          <p className="text-gray-400">Loading replay...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50">
        <div className="bg-town-surface rounded-lg p-6 max-w-md">
          <div className="text-center">
            <div className="text-4xl mb-2">⚠️</div>
            <p className="text-red-400 mb-4">{error}</p>
            <button
              onClick={onClose}
              className="px-4 py-2 bg-town-highlight rounded"
            >
              Close
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (!replay) return null;

  const progress = replay.events.length > 1
    ? (replay.currentIndex / (replay.events.length - 1)) * 100
    : 0;

  return (
    <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-8">
      <div className="bg-town-bg rounded-lg w-full max-w-4xl max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-town-accent/30">
          <div>
            <h2 className="font-semibold">Replay: {taskDescription}</h2>
            <div className="text-sm text-gray-400">
              Event {replay.currentIndex + 1} of {replay.events.length}
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 text-gray-400 hover:text-white transition-colors"
          >
            ✕
          </button>
        </div>

        {/* Main Content */}
        <div className="flex-1 flex overflow-hidden">
          {/* Mini Mesa */}
          <div className="flex-1 p-4">
            <div className="bg-town-surface/30 rounded-lg p-4 h-full">
              <BuilderStateViz
                events={replay.events}
                currentIndex={replay.currentIndex}
              />
            </div>
          </div>

          {/* Event Log */}
          <div className="w-80 border-l border-town-accent/30 flex flex-col">
            <div className="p-3 border-b border-town-accent/20 font-semibold">
              Event Log
            </div>
            <div ref={eventListRef} className="flex-1 overflow-y-auto p-2 space-y-1">
              {replay.events.map((event, idx) => (
                <EventLogItem
                  key={idx}
                  event={event}
                  index={idx}
                  isCurrent={idx === replay.currentIndex}
                  onClick={() => seekReplay(idx)}
                />
              ))}
            </div>
          </div>
        </div>

        {/* Timeline Controls */}
        <div className="p-4 border-t border-town-accent/30 space-y-3">
          {/* Progress Bar */}
          <div className="flex items-center gap-2">
            <span className="text-sm text-gray-400 w-12">
              {formatTime(replay.elapsed)}
            </span>
            <div className="flex-1 relative">
              <div className="h-2 bg-town-surface rounded-full overflow-hidden">
                <div
                  className="h-full bg-town-highlight transition-all"
                  style={{ width: `${progress}%` }}
                />
              </div>
              <input
                type="range"
                min={0}
                max={replay.events.length - 1}
                value={replay.currentIndex}
                onChange={handleSliderChange}
                className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
              />
            </div>
            <span className="text-sm text-gray-400 w-12">
              {formatTime(replay.duration)}
            </span>
          </div>

          {/* Playback Controls */}
          <div className="flex items-center justify-center gap-4">
            {/* Skip to Start */}
            <button
              onClick={() => seekReplay(0)}
              className="p-2 text-gray-400 hover:text-white transition-colors"
              title="Start"
            >
              |◀
            </button>

            {/* Step Back */}
            <button
              onClick={() => stepReplay(-1)}
              disabled={replay.currentIndex === 0}
              className="p-2 text-gray-400 hover:text-white disabled:opacity-50 transition-colors"
              title="Previous"
            >
              ◀
            </button>

            {/* Play/Pause */}
            <button
              onClick={toggleReplayPlaying}
              className="p-3 bg-town-highlight rounded-full text-white hover:bg-town-highlight/80 transition-colors"
              title={replay.isPlaying ? 'Pause' : 'Play'}
            >
              {replay.isPlaying ? '⏸' : '▶'}
            </button>

            {/* Step Forward */}
            <button
              onClick={() => stepReplay(1)}
              disabled={replay.currentIndex >= replay.events.length - 1}
              className="p-2 text-gray-400 hover:text-white disabled:opacity-50 transition-colors"
              title="Next"
            >
              ▶
            </button>

            {/* Skip to End */}
            <button
              onClick={() => seekReplay(replay.events.length - 1)}
              className="p-2 text-gray-400 hover:text-white transition-colors"
              title="End"
            >
              ▶|
            </button>

            {/* Speed Control */}
            <select
              value={replay.playbackSpeed}
              onChange={(e) => setReplaySpeed(parseFloat(e.target.value))}
              className="ml-4 bg-town-surface border border-town-accent/30 rounded px-2 py-1 text-sm"
            >
              <option value="0.5">0.5x</option>
              <option value="1">1x</option>
              <option value="2">2x</option>
              <option value="4">4x</option>
            </select>
          </div>
        </div>
      </div>
    </div>
  );
}

// =============================================================================
// Sub-Components
// =============================================================================

interface BuilderStateVizProps {
  events: WorkshopEvent[];
  currentIndex: number;
}

function BuilderStateViz({ events, currentIndex }: BuilderStateVizProps) {
  const archetypes: BuilderArchetype[] = ['Scout', 'Sage', 'Spark', 'Steady', 'Sync'];

  // Determine which builders have been active up to current index
  const activeBuilders = new Set<string>();
  const completedBuilders = new Set<string>();
  let currentBuilder: string | null = null;

  for (let i = 0; i <= currentIndex && i < events.length; i++) {
    const event = events[i];
    if (event.builder) {
      activeBuilders.add(event.builder);
      if (event.type === 'PHASE_COMPLETED' || event.type === 'HANDOFF') {
        completedBuilders.add(event.builder);
      }
    }
  }

  // Current builder is the last one that started
  const currentEvent = events[currentIndex];
  if (currentEvent?.builder) {
    currentBuilder = currentEvent.builder;
  }

  return (
    <div className="h-full flex flex-col items-center justify-center">
      {/* Builder Icons */}
      <div className="flex items-center gap-4 mb-8">
        {archetypes.map((archetype, idx) => {
          const icon = BUILDER_ICONS[archetype];
          const color = BUILDER_COLORS[archetype];
          const isActive = activeBuilders.has(archetype);
          const isCompleted = completedBuilders.has(archetype);
          const isCurrent = currentBuilder === archetype;

          return (
            <div key={archetype} className="flex items-center">
              <div
                className={`w-12 h-12 rounded-full flex items-center justify-center text-xl transition-all ${
                  isCurrent ? 'ring-2 ring-white scale-110' : ''
                }`}
                style={{
                  backgroundColor: isActive ? color + '50' : color + '20',
                  border: `2px solid ${isActive ? color : color + '40'}`,
                  opacity: isActive ? 1 : 0.5,
                }}
              >
                {icon}
              </div>
              {idx < archetypes.length - 1 && (
                <div
                  className="w-8 h-1 mx-2"
                  style={{
                    backgroundColor: isCompleted ? color : color + '30',
                  }}
                />
              )}
            </div>
          );
        })}
      </div>

      {/* Current Event Info */}
      {currentEvent && (
        <div className="text-center">
          <div className="text-lg font-semibold mb-2">
            {currentEvent.type.replace(/_/g, ' ')}
          </div>
          <div className="text-gray-400 max-w-md">{currentEvent.message}</div>
          {currentEvent.builder && (
            <div className="mt-2 text-sm text-gray-500">
              {BUILDER_ICONS[currentEvent.builder as BuilderArchetype] || ''} {currentEvent.builder} • {currentEvent.phase}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

interface EventLogItemProps {
  event: WorkshopEvent;
  index: number;
  isCurrent: boolean;
  onClick: () => void;
}

function EventLogItem({ event, index, isCurrent, onClick }: EventLogItemProps) {
  const timestamp = new Date(event.timestamp);
  const timeStr = timestamp.toLocaleTimeString([], {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  });

  const typeColors: Record<string, string> = {
    TASK_ASSIGNED: 'text-blue-400',
    PLAN_CREATED: 'text-purple-400',
    PHASE_STARTED: 'text-green-400',
    PHASE_COMPLETED: 'text-emerald-400',
    HANDOFF: 'text-amber-400',
    ARTIFACT_PRODUCED: 'text-pink-400',
    TASK_COMPLETED: 'text-teal-400',
    ERROR: 'text-red-400',
  };

  return (
    <button
      data-index={index}
      onClick={onClick}
      className={`w-full text-left p-2 rounded text-sm transition-colors ${
        isCurrent
          ? 'bg-town-highlight/30 border border-town-highlight'
          : 'hover:bg-town-surface/50'
      }`}
    >
      <div className="flex items-center gap-2">
        <span className="text-gray-500 text-xs">{timeStr}</span>
        {event.builder && (
          <span>{BUILDER_ICONS[event.builder as BuilderArchetype] || ''}</span>
        )}
      </div>
      <div className={`${typeColors[event.type] || 'text-gray-300'} truncate`}>
        {event.type.replace(/_/g, ' ')}
      </div>
      <div className="text-gray-500 text-xs truncate">{event.message}</div>
    </button>
  );
}

export default TaskReplay;
