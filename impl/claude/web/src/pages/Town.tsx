import { useParams, Link } from 'react-router-dom';
import { useEffect, useRef, useState } from 'react';
import { useTownStore } from '@/stores/townStore';
import { useUIStore } from '@/stores/uiStore';
import { townApi } from '@/api/client';
import { Mesa } from '@/components/town/Mesa';
import { CitizenPanel } from '@/components/town/CitizenPanel';
import { useTownStream } from '@/hooks/useTownStream';

type LoadingState = 'loading' | 'loaded' | 'error' | 'creating';

export default function Town() {
  const { townId: paramTownId } = useParams<{ townId: string }>();
  const { setTownId, setTownName, setCitizens, currentPhase, currentDay, events, isPlaying, setPlaying, speed, setSpeed, townId, citizens } = useTownStore();
  const { isEventFeedOpen, toggleEventFeed } = useUIStore();
  const mesaContainerRef = useRef<HTMLDivElement>(null);
  const [mesaSize, setMesaSize] = useState({ width: 800, height: 600 });
  const [loadingState, setLoadingState] = useState<LoadingState>('loading');
  const [error, setError] = useState<string | null>(null);

  // Connect SSE stream when playing (use actual townId from store, not param)
  useTownStream({ townId: townId || '', speed, autoConnect: true });

  // Load town data on mount
  useEffect(() => {
    if (!paramTownId) return;

    const loadTown = async (id: string) => {
      setLoadingState('loading');
      setError(null);
      try {
        console.log('[Town] Loading town:', id);
        const [townRes, citizensRes] = await Promise.all([
          townApi.get(id),
          townApi.getCitizens(id),
        ]);
        console.log('[Town] Loaded:', townRes.data, citizensRes.data);
        setTownId(id);
        setTownName(townRes.data.name);
        setCitizens(citizensRes.data.citizens);
        setLoadingState('loaded');
        // Auto-start simulation after loading citizens
        setPlaying(true);
      } catch (err: unknown) {
        console.error('[Town] Failed to load town:', err);
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
        console.log('[Town] Creating demo town...');
        const response = await townApi.create({
          name: 'Demo Town',
          phase: 3, // 10 citizens
          enable_dialogue: false,
        });
        const newTownId = response.data.id;
        console.log('[Town] Created town:', newTownId);

        // Update URL without full navigation (prevents re-mount issues)
        window.history.replaceState(null, '', `/town/${newTownId}`);

        // Load citizens for the new town
        console.log('[Town] Loading citizens...');
        const citizensRes = await townApi.getCitizens(newTownId);
        console.log('[Town] Citizens loaded:', citizensRes.data);

        setTownId(newTownId);
        setTownName(response.data.name);
        setCitizens(citizensRes.data.citizens);
        setLoadingState('loaded');
        setPlaying(true);
      } catch (err: unknown) {
        console.error('[Town] Failed to create demo town:', err);
        const axiosErr = err as { response?: { data?: { detail?: string } } };
        setError(axiosErr.response?.data?.detail || 'Failed to create demo town');
        setLoadingState('error');
      }
    };

    // Handle "demo" as a special case - create a new town
    if (paramTownId === 'demo') {
      createAndLoadTown();
    } else {
      loadTown(paramTownId);
    }
  }, [paramTownId, setTownId, setTownName, setCitizens, setPlaying]);

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
      {/* Town Header */}
      <div className="bg-town-surface/50 border-b border-town-accent/30 px-4 py-2 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <h1 className="font-semibold">Town: {townId}</h1>
          <div className="flex items-center gap-2 text-sm text-gray-400">
            <span>Day {currentDay}</span>
            <span>•</span>
            <span className={`font-medium ${getPhaseColor(currentPhase)}`}>{currentPhase}</span>
            <span>•</span>
            <span>{citizens.length} citizens</span>
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
