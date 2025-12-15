/**
 * TownV2: Widget-based Agent Town visualization.
 *
 * Consumes ColonyDashboardJSON from useTownStreamWidget instead of
 * building state incrementally via Zustand.
 *
 * Migration Path:
 * 1. TownV2 runs in parallel with Town.tsx
 * 2. Feature flag controls which version loads
 * 3. Once stable, TownV2 replaces Town.tsx
 */

import { useParams, Link } from 'react-router-dom';
import { useState, useEffect, useRef } from 'react';
import { useTownStreamWidget } from '@/hooks/useTownStreamWidget';
import { townApi } from '@/api/client';
import { MesaV2 } from '@/components/town/MesaV2';
import { CitizenPanelV2 } from '@/components/town/CitizenPanelV2';
import { ColonyDashboard } from '@/widgets/dashboards';
import type { TownEvent } from '@/api/types';

type LoadingState = 'loading' | 'loaded' | 'error' | 'creating';

export default function TownV2() {
  const { townId: paramTownId } = useParams<{ townId: string }>();

  // Local state (replaces Zustand)
  const [townId, setTownId] = useState<string | null>(null);
  const [loadingState, setLoadingState] = useState<LoadingState>('loading');
  const [error, setError] = useState<string | null>(null);
  const [speed, setSpeed] = useState(1.0);
  const [selectedCitizenId, setSelectedCitizenId] = useState<string | null>(null);
  const [isEventFeedOpen, setIsEventFeedOpen] = useState(false);

  // Mesa sizing
  const mesaContainerRef = useRef<HTMLDivElement>(null);
  const [mesaSize, setMesaSize] = useState({ width: 800, height: 600 });

  // Widget-based streaming (Phase 3 hook)
  const {
    dashboard,
    events,
    isConnected,
    isPlaying,
    connect,
    disconnect,
  } = useTownStreamWidget({
    townId: townId || '',
    speed,
    phases: 4,
    autoConnect: false, // We control connection after town loads
  });

  // Load or create town on mount
  useEffect(() => {
    if (!paramTownId) return;

    const loadTown = async (id: string) => {
      setLoadingState('loading');
      setError(null);
      try {
        // Verify town exists
        await townApi.get(id);
        setTownId(id);
        setLoadingState('loaded');
      } catch (err: unknown) {
        const axiosErr = err as { response?: { status?: number; data?: { detail?: string } } };
        if (axiosErr.response?.status === 404) {
          setError(`Town "${id}" not found`);
        } else {
          setError(axiosErr.response?.data?.detail || 'Failed to load town');
        }
        setLoadingState('error');
      }
    };

    const createAndLoadTown = async () => {
      setLoadingState('creating');
      setError(null);
      try {
        const response = await townApi.create({
          name: 'Demo Town',
          phase: 3,
          enable_dialogue: false,
        });
        const newTownId = response.data.id;
        window.history.replaceState(null, '', `/town/${newTownId}`);
        setTownId(newTownId);
        setLoadingState('loaded');
      } catch (err: unknown) {
        const axiosErr = err as { response?: { data?: { detail?: string } } };
        setError(axiosErr.response?.data?.detail || 'Failed to create demo town');
        setLoadingState('error');
      }
    };

    if (paramTownId === 'demo') {
      createAndLoadTown();
    } else {
      loadTown(paramTownId);
    }
  }, [paramTownId]);

  // Auto-connect stream when town loads
  useEffect(() => {
    if (loadingState === 'loaded' && townId) {
      connect();
    }
    return () => disconnect();
  }, [loadingState, townId, connect, disconnect]);

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

  // Derive selected citizen from dashboard
  const selectedCitizen = dashboard?.citizens.find(
    (c) => c.citizen_id === selectedCitizenId
  );

  // Loading state
  if (loadingState === 'loading' || loadingState === 'creating') {
    return (
      <div className="h-[calc(100vh-64px)] flex items-center justify-center bg-town-bg">
        <div className="text-center">
          <div className="animate-pulse text-6xl mb-4">🏘️</div>
          <p className="text-gray-400 text-lg">
            {loadingState === 'creating' ? 'Creating your town...' : 'Loading town...'}
          </p>
        </div>
      </div>
    );
  }

  // Error state
  if (loadingState === 'error') {
    return (
      <div className="h-[calc(100vh-64px)] flex items-center justify-center bg-town-bg">
        <div className="text-center max-w-md">
          <div className="text-6xl mb-4">🏚️</div>
          <h2 className="text-xl font-semibold mb-2 text-red-400">Town Not Found</h2>
          <p className="text-gray-400 mb-6">{error}</p>
          <div className="flex gap-4 justify-center">
            <Link
              to="/town/demo"
              className="px-6 py-2 bg-town-highlight hover:bg-town-highlight/80 rounded-lg font-medium transition-colors"
            >
              Create New Town
            </Link>
            <Link
              to="/"
              className="px-6 py-2 bg-town-accent hover:bg-town-accent/80 rounded-lg font-medium transition-colors"
            >
              Back to Home
            </Link>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="h-[calc(100vh-64px)] flex flex-col">
      {/* Town Header - derived from dashboard */}
      <TownHeader
        townId={townId}
        phase={dashboard?.phase || 'MORNING'}
        day={dashboard?.day || 1}
        citizenCount={dashboard?.citizens.length || 0}
        isPlaying={isPlaying}
        isConnected={isConnected}
        speed={speed}
        onTogglePlay={() => (isPlaying ? disconnect() : connect())}
        onSpeedChange={setSpeed}
      />

      {/* Main Content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Mesa (Main Canvas) */}
        <div className="flex-1 relative" ref={mesaContainerRef}>
          <div className="absolute inset-0 bg-town-bg">
            <MesaV2
              width={mesaSize.width}
              height={mesaSize.height}
              citizens={dashboard?.citizens || []}
              selectedCitizenId={selectedCitizenId}
              onSelectCitizen={setSelectedCitizenId}
            />
          </div>
        </div>

        {/* Right Sidebar */}
        <div className="w-80 border-l border-town-accent/30 flex flex-col bg-town-surface/30">
          {/* Citizen Panel or Dashboard Mini */}
          <div className="flex-1 overflow-y-auto">
            {selectedCitizen ? (
              <CitizenPanelV2
                citizen={selectedCitizen}
                townId={townId || ''}
                onClose={() => setSelectedCitizenId(null)}
              />
            ) : (
              <div className="p-4">
                <p className="text-gray-500 text-center mb-4">
                  Click a citizen on the map
                </p>
                {dashboard && (
                  <ColonyDashboard
                    {...dashboard}
                    onSelectCitizen={setSelectedCitizenId}
                    className="text-sm"
                  />
                )}
              </div>
            )}
          </div>

          {/* Event Feed */}
          <EventFeed
            events={events}
            isOpen={isEventFeedOpen}
            onToggle={() => setIsEventFeedOpen(!isEventFeedOpen)}
          />
        </div>
      </div>
    </div>
  );
}

// =============================================================================
// Sub-components
// =============================================================================

interface TownHeaderProps {
  townId: string | null;
  phase: string;
  day: number;
  citizenCount: number;
  isPlaying: boolean;
  isConnected: boolean;
  speed: number;
  onTogglePlay: () => void;
  onSpeedChange: (speed: number) => void;
}

function TownHeader({
  townId,
  phase,
  day,
  citizenCount,
  isPlaying,
  isConnected,
  speed,
  onTogglePlay,
  onSpeedChange,
}: TownHeaderProps) {
  return (
    <div className="bg-town-surface/50 border-b border-town-accent/30 px-4 py-2 flex items-center justify-between">
      <div className="flex items-center gap-4">
        <h1 className="font-semibold">Town: {townId}</h1>
        <div className="flex items-center gap-2 text-sm text-gray-400">
          <span>Day {day}</span>
          <span>·</span>
          <span className={`font-medium ${getPhaseColor(phase)}`}>{phase}</span>
          <span>·</span>
          <span>{citizenCount} citizens</span>
          {!isConnected && (
            <>
              <span>·</span>
              <span className="text-yellow-500">Disconnected</span>
            </>
          )}
        </div>
      </div>
      <div className="flex items-center gap-4">
        <button
          onClick={onTogglePlay}
          className="px-3 py-1 bg-town-accent/30 rounded text-sm hover:bg-town-accent/50 transition-colors"
        >
          {isPlaying ? '⏸️ Pause' : '▶️ Play'}
        </button>
        <select
          value={speed}
          onChange={(e) => onSpeedChange(parseFloat(e.target.value))}
          className="bg-town-surface border border-town-accent/30 rounded px-2 py-1 text-sm"
        >
          <option value="0.5">0.5x Speed</option>
          <option value="1">1x Speed</option>
          <option value="2">2x Speed</option>
          <option value="4">4x Speed</option>
        </select>
      </div>
    </div>
  );
}

interface EventFeedProps {
  events: TownEvent[];
  isOpen: boolean;
  onToggle: () => void;
}

function EventFeed({ events, isOpen, onToggle }: EventFeedProps) {
  return (
    <div className={`border-t border-town-accent/30 transition-all ${isOpen ? 'h-64' : 'h-10'}`}>
      <button
        onClick={onToggle}
        className="w-full px-4 py-2 flex items-center justify-between text-sm font-semibold hover:bg-town-surface/50"
      >
        <span>Event Feed ({events.length})</span>
        <span>{isOpen ? '▼' : '▲'}</span>
      </button>
      {isOpen && (
        <div className="px-4 pb-4 overflow-y-auto h-[calc(100%-40px)]">
          {events.length > 0 ? (
            <ul className="space-y-2 text-sm">
              {events.slice(0, 20).map((event, i) => (
                <li key={i} className="text-gray-400">
                  <span className="text-gray-500 font-mono text-xs">{event.tick}:</span>{' '}
                  <span className={getEventColor(event.operation)}>
                    {event.message || event.operation}
                  </span>
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-gray-600 text-sm">No events yet. Press Play to start.</p>
          )}
        </div>
      )}
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
  if (['greet', 'gossip', 'trade'].includes(operation)) return 'text-green-400';
  if (['work', 'craft', 'build'].includes(operation)) return 'text-blue-400';
  if (['reflect', 'journal', 'meditate'].includes(operation)) return 'text-purple-400';
  if (['evolve', 'transform'].includes(operation)) return 'text-yellow-400';
  return 'text-gray-300';
}
