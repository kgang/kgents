import { useParams } from 'react-router-dom';
import { useEffect, useRef, useState } from 'react';
import { useTownStore } from '@/stores/townStore';
import { useUIStore } from '@/stores/uiStore';
import { townApi } from '@/api/client';
import { Mesa } from '@/components/town/Mesa';
import { CitizenPanel } from '@/components/town/CitizenPanel';
import { useTownStream } from '@/hooks/useTownStream';

export default function Town() {
  const { townId } = useParams<{ townId: string }>();
  const { setTownId, setTownName, setCitizens, currentPhase, currentDay, events, isPlaying, setPlaying, speed, setSpeed } = useTownStore();
  const { isEventFeedOpen, toggleEventFeed } = useUIStore();
  const mesaContainerRef = useRef<HTMLDivElement>(null);
  const [mesaSize, setMesaSize] = useState({ width: 800, height: 600 });

  // Connect SSE stream when playing
  useTownStream({ townId: townId || '', speed, autoConnect: true });

  // Load town data on mount
  useEffect(() => {
    if (!townId) return;

    setTownId(townId);

    const loadTown = async () => {
      try {
        const [townRes, citizensRes] = await Promise.all([
          townApi.get(townId),
          townApi.getCitizens(townId),
        ]);
        setTownName(townRes.data.name);
        setCitizens(citizensRes.data.citizens);
      } catch (err) {
        console.error('Failed to load town:', err);
      }
    };

    loadTown();
  }, [townId, setTownId, setTownName, setCitizens]);

  // Track mesa container size
  useEffect(() => {
    const container = mesaContainerRef.current;
    if (!container) return;

    const observer = new ResizeObserver((entries) => {
      const entry = entries[0];
      if (entry) {
        setMesaSize({
          width: entry.contentRect.width,
          height: entry.contentRect.height,
        });
      }
    });

    observer.observe(container);
    return () => observer.disconnect();
  }, []);

  return (
    <div className="h-[calc(100vh-64px)] flex flex-col">
      {/* Town Header */}
      <div className="bg-town-surface/50 border-b border-town-accent/30 px-4 py-2 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <h1 className="font-semibold">Town: {townId}</h1>
          <div className="flex items-center gap-2 text-sm text-gray-400">
            <span>Day {currentDay}</span>
            <span>•</span>
            <span className={`font-medium ${getPhaseColor(currentPhase)}`}>{currentPhase}</span>
          </div>
        </div>
        <div className="flex items-center gap-4">
          {/* Time Controls */}
          <button
            onClick={() => setPlaying(!isPlaying)}
            className="px-3 py-1 bg-town-accent/30 rounded text-sm hover:bg-town-accent/50 transition-colors"
          >
            {isPlaying ? '⏸️ Pause' : '▶️ Play'}
          </button>
          <select
            value={speed}
            onChange={(e) => setSpeed(parseFloat(e.target.value))}
            className="bg-town-surface border border-town-accent/30 rounded px-2 py-1 text-sm"
          >
            <option value="0.5">0.5x Speed</option>
            <option value="1">1x Speed</option>
            <option value="2">2x Speed</option>
            <option value="4">4x Speed</option>
          </select>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Mesa (Main Canvas) */}
        <div className="flex-1 relative" ref={mesaContainerRef}>
          <div className="absolute inset-0 bg-town-bg">
            <Mesa width={mesaSize.width} height={mesaSize.height} />
          </div>
        </div>

        {/* Right Sidebar */}
        <div className="w-80 border-l border-town-accent/30 flex flex-col bg-town-surface/30">
          {/* Citizen Panel */}
          <div className="flex-1 overflow-y-auto">
            <CitizenPanel />
          </div>

          {/* Event Feed */}
          <div className={`border-t border-town-accent/30 transition-all ${isEventFeedOpen ? 'h-64' : 'h-10'}`}>
            <button
              onClick={toggleEventFeed}
              className="w-full px-4 py-2 flex items-center justify-between text-sm font-semibold hover:bg-town-surface/50"
            >
              <span>Event Feed ({events.length})</span>
              <span>{isEventFeedOpen ? '▼' : '▲'}</span>
            </button>
            {isEventFeedOpen && (
              <div className="px-4 pb-4 overflow-y-auto h-[calc(100%-40px)]">
                {events.length > 0 ? (
                  <ul className="space-y-2 text-sm">
                    {events.slice(0, 20).map((event, i) => (
                      <li key={i} className="text-gray-400">
                        <span className="text-gray-500 font-mono text-xs">{event.tick}:</span>{' '}
                        <span className={getEventColor(event.operation)}>{event.message}</span>
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p className="text-gray-600 text-sm">No events yet. Press Play to start.</p>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

function getPhaseColor(phase: string): string {
  switch (phase) {
    case 'MORNING':
      return 'text-phase-morning';
    case 'AFTERNOON':
      return 'text-phase-afternoon';
    case 'EVENING':
      return 'text-phase-evening';
    case 'NIGHT':
      return 'text-phase-night';
    default:
      return 'text-gray-400';
  }
}

function getEventColor(operation: string): string {
  if (['greet', 'gossip', 'trade'].includes(operation)) {
    return 'text-green-400';
  }
  if (['work', 'craft', 'build'].includes(operation)) {
    return 'text-blue-400';
  }
  if (['reflect', 'journal', 'meditate'].includes(operation)) {
    return 'text-purple-400';
  }
  if (['evolve', 'transform'].includes(operation)) {
    return 'text-yellow-400';
  }
  return 'text-gray-300';
}
