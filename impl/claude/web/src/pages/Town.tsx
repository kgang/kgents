/**
 * Town: Widget-based Agent Town visualization.
 *
 * Consumes ColonyDashboardJSON from useTownStreamWidget for rendering.
 * Uses ElasticSplit for responsive layout with collapsible sidebar.
 *
 * Layout:
 * - Desktop (>1024px): Mesa (main canvas) | Details Sidebar (resizable)
 * - Tablet (768-1024px): Mesa | Sidebar (collapsible)
 * - Mobile (<768px): Full canvas + floating actions + drawer panels
 *
 * Session 8: Elastic UI Refactor
 * @see plans/web-refactor/elastic-audit-report.md
 */

import { useParams } from 'react-router-dom';
import { useState, useEffect, useRef } from 'react';
import { useTownStreamWidget } from '@/hooks/useTownStreamWidget';
import { townApi } from '@/api/client';
import { Mesa } from '@/components/town/Mesa';
import { CitizenPanel } from '@/components/town/CitizenPanel';
import { ColonyDashboard } from '@/widgets/dashboards';
import { ElasticSplit, ElasticContainer, useWindowLayout } from '@/components/elastic';
import { getEmptyState } from '@/constants';
import { EmpathyError } from '@/components/joy';
import type { TownEvent } from '@/api/types';

type LoadingState = 'loading' | 'loaded' | 'error' | 'creating';
type Density = 'compact' | 'comfortable' | 'spacious';

// =============================================================================
// Constants - Density-aware
// =============================================================================

/** Maximum events shown by density */
const MAX_EVENTS = {
  compact: 10,
  comfortable: 15,
  spacious: 20,
} as const;

/** Speed options */
const SPEED_OPTIONS = [
  { value: 0.5, label: '0.5x' },
  { value: 1, label: '1x' },
  { value: 2, label: '2x' },
  { value: 4, label: '4x' },
];

// =============================================================================
// Floating Actions (Mobile)
// =============================================================================

interface FloatingActionsProps {
  isPlaying: boolean;
  onTogglePlay: () => void;
  onOpenControls: () => void;
  selectedCitizen: boolean;
  onOpenCitizen: () => void;
}

function FloatingActions({
  isPlaying,
  onTogglePlay,
  onOpenControls,
  selectedCitizen,
  onOpenCitizen,
}: FloatingActionsProps) {
  return (
    <div className="absolute bottom-4 right-4 flex flex-col gap-2 z-10">
      <button
        onClick={onTogglePlay}
        className={`w-12 h-12 rounded-full shadow-lg flex items-center justify-center text-xl transition-colors ${
          isPlaying ? 'bg-town-accent' : 'bg-town-highlight'
        }`}
        title={isPlaying ? 'Pause' : 'Play'}
      >
        {isPlaying ? '⏸️' : '▶️'}
      </button>
      <button
        onClick={onOpenControls}
        className="w-12 h-12 bg-gray-700 hover:bg-gray-600 rounded-full shadow-lg flex items-center justify-center text-xl transition-colors"
        title="Controls"
      >
        ⚙️
      </button>
      {selectedCitizen && (
        <button
          onClick={onOpenCitizen}
          className="w-12 h-12 bg-purple-600 hover:bg-purple-700 rounded-full shadow-lg flex items-center justify-center text-xl transition-colors"
          title="View Citizen"
        >
          👤
        </button>
      )}
    </div>
  );
}

// =============================================================================
// Bottom Drawer (Mobile)
// =============================================================================

interface BottomDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  children: React.ReactNode;
}

function BottomDrawer({ isOpen, onClose, title, children }: BottomDrawerProps) {
  if (!isOpen) return null;

  return (
    <>
      <div className="fixed inset-0 bg-black/50 z-40" onClick={onClose} />
      <div
        className="fixed bottom-0 left-0 right-0 z-50 max-h-[75vh] bg-town-surface rounded-t-xl shadow-2xl"
        style={{ transform: isOpen ? 'translateY(0)' : 'translateY(100%)' }}
      >
        <div className="flex justify-center py-2">
          <div className="w-10 h-1 bg-gray-600 rounded-full" />
        </div>
        <div className="flex justify-between items-center px-4 pb-2 border-b border-town-accent/30">
          <h3 className="text-sm font-semibold text-white">{title}</h3>
          <button onClick={onClose} className="text-gray-400 hover:text-white text-lg p-1">
            ×
          </button>
        </div>
        <div className="overflow-y-auto max-h-[calc(75vh-60px)]">{children}</div>
      </div>
    </>
  );
}

export default function Town() {
  const { townId: paramTownId } = useParams<{ townId: string }>();

  // Layout context
  const { density, isMobile, isDesktop } = useWindowLayout();

  // Local state
  const [townId, setTownId] = useState<string | null>(null);
  const [loadingState, setLoadingState] = useState<LoadingState>('loading');
  const [error, setError] = useState<string | null>(null);
  const [speed, setSpeed] = useState(1.0);
  const [selectedCitizenId, setSelectedCitizenId] = useState<string | null>(null);
  const [isEventFeedOpen, setIsEventFeedOpen] = useState(false);

  // Mobile drawer state
  const [controlsDrawerOpen, setControlsDrawerOpen] = useState(false);
  const [citizenDrawerOpen, setCitizenDrawerOpen] = useState(false);

  // Mesa sizing
  const mesaContainerRef = useRef<HTMLDivElement>(null);
  const [mesaSize, setMesaSize] = useState({ width: 800, height: 600 });

  // Widget-based streaming
  const { dashboard, events, isConnected, isPlaying, connect, disconnect } = useTownStreamWidget({
    townId: townId || '',
    speed,
    phases: 4,
    nphaseEnabled: false,
    autoConnect: false,
  });

  // Load or create town on mount
  useEffect(() => {
    if (!paramTownId) return;

    const loadTown = async (id: string) => {
      setLoadingState('loading');
      setError(null);
      try {
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
        const newTownId = response.id;
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
  const selectedCitizen = dashboard?.citizens.find((c) => c.citizen_id === selectedCitizenId);

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
        <EmpathyError
          type="notfound"
          title="Town Not Found"
          subtitle={error || 'The town you requested could not be located.'}
          action="Create New Town"
          onAction={() => window.location.href = '/town/demo'}
          size="lg"
        />
      </div>
    );
  }

  // ==========================================================================
  // Render: Mobile Layout
  // ==========================================================================

  if (isMobile) {
    return (
      <div className="h-[calc(100vh-64px)] flex flex-col bg-town-bg">
        {/* Compact header */}
        <header className="flex-shrink-0 bg-town-surface/50 border-b border-town-accent/30 px-3 py-2">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="text-lg">🏘️</span>
              <span className="font-semibold text-sm">{townId}</span>
              <span className={`text-xs font-medium ${getPhaseColor(dashboard?.phase || 'MORNING')}`}>
                {dashboard?.phase || 'MORNING'}
              </span>
            </div>
            {!isConnected && (
              <span className="text-xs text-yellow-500">Disconnected</span>
            )}
          </div>
        </header>

        {/* Main canvas */}
        <div className="flex-1 relative" ref={mesaContainerRef}>
          <div className="absolute inset-0">
            <Mesa
              width={mesaSize.width}
              height={mesaSize.height}
              citizens={dashboard?.citizens || []}
              selectedCitizenId={selectedCitizenId}
              onSelectCitizen={(id) => {
                setSelectedCitizenId(id);
                if (id) setCitizenDrawerOpen(true);
              }}
            />
          </div>

          {/* Stats overlay */}
          <div className="absolute top-2 left-2 bg-town-surface/90 backdrop-blur-sm rounded-lg px-2 py-1 text-[10px] text-gray-300">
            <span>Day {dashboard?.day || 1}</span>
            {' • '}
            <span className="text-town-highlight">{dashboard?.citizens.length || 0}</span> citizens
          </div>

          {/* Floating actions */}
          <FloatingActions
            isPlaying={isPlaying}
            onTogglePlay={() => (isPlaying ? disconnect() : connect())}
            onOpenControls={() => setControlsDrawerOpen(true)}
            selectedCitizen={!!selectedCitizenId}
            onOpenCitizen={() => setCitizenDrawerOpen(true)}
          />
        </div>

        {/* Controls drawer */}
        <BottomDrawer
          isOpen={controlsDrawerOpen}
          onClose={() => setControlsDrawerOpen(false)}
          title="Controls"
        >
          <ControlsPanel
            speed={speed}
            onSpeedChange={setSpeed}
            isPlaying={isPlaying}
            onTogglePlay={() => (isPlaying ? disconnect() : connect())}
            events={events}
            density={density}
          />
        </BottomDrawer>

        {/* Citizen drawer */}
        <BottomDrawer
          isOpen={citizenDrawerOpen && !!selectedCitizen}
          onClose={() => {
            setCitizenDrawerOpen(false);
            setSelectedCitizenId(null);
          }}
          title={selectedCitizen?.name || 'Citizen'}
        >
          {selectedCitizen && (
            <CitizenPanel
              citizen={selectedCitizen}
              townId={townId || ''}
              onClose={() => {
                setCitizenDrawerOpen(false);
                setSelectedCitizenId(null);
              }}
            />
          )}
        </BottomDrawer>
      </div>
    );
  }

  // ==========================================================================
  // Render: Tablet/Desktop Layout
  // ==========================================================================

  return (
    <div className="h-[calc(100vh-64px)] flex flex-col">
      {/* Town Header */}
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
        density={density}
      />

      {/* Main Content - ElasticSplit for mesa | sidebar */}
      <div className="flex-1 overflow-hidden">
        <ElasticSplit
          direction="horizontal"
          defaultRatio={0.75}
          collapseAt={768}
          collapsePriority="secondary"
          minPaneSize={280}
          resizable={isDesktop}
          primary={
            /* Mesa (Main Canvas) */
            <ElasticContainer
              layout="stack"
              overflow="scroll"
              className="h-full bg-town-bg"
            >
              <div className="flex-1 relative" ref={mesaContainerRef}>
                <div className="absolute inset-0">
                  <Mesa
                    width={mesaSize.width}
                    height={mesaSize.height}
                    citizens={dashboard?.citizens || []}
                    selectedCitizenId={selectedCitizenId}
                    onSelectCitizen={setSelectedCitizenId}
                  />
                </div>
              </div>
            </ElasticContainer>
          }
          secondary={
            /* Right Sidebar - Details Panel */
            <div className="h-full flex flex-col bg-town-surface/30 border-l border-town-accent/30">
              {/* Citizen Panel or Dashboard Mini */}
              <div className="flex-1 overflow-y-auto">
                {selectedCitizen ? (
                  <CitizenPanel
                    citizen={selectedCitizen}
                    townId={townId || ''}
                    onClose={() => setSelectedCitizenId(null)}
                  />
                ) : (
                  <div className="p-4">
                    <p className="text-gray-500 text-center mb-4">Click a citizen on the map</p>
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
                density={density}
              />
            </div>
          }
        />
      </div>
    </div>
  );
}

// =============================================================================
// Sub-components
// =============================================================================

// Controls Panel for mobile drawer
interface ControlsPanelProps {
  speed: number;
  onSpeedChange: (speed: number) => void;
  isPlaying: boolean;
  onTogglePlay: () => void;
  events: TownEvent[];
  density: Density;
}

function ControlsPanel({
  speed,
  onSpeedChange,
  isPlaying,
  onTogglePlay,
  events,
  density,
}: ControlsPanelProps) {
  const maxEvents = MAX_EVENTS[density];

  return (
    <div className="p-4 space-y-4">
      {/* Playback */}
      <div>
        <h4 className="text-xs font-semibold text-gray-400 uppercase mb-2">Playback</h4>
        <div className="flex items-center gap-3">
          <button
            onClick={onTogglePlay}
            className={`flex-1 py-2 rounded-lg font-medium transition-colors ${
              isPlaying
                ? 'bg-town-accent text-white'
                : 'bg-town-highlight text-white'
            }`}
          >
            {isPlaying ? '⏸️ Pause' : '▶️ Play'}
          </button>
        </div>
      </div>

      {/* Speed */}
      <div>
        <h4 className="text-xs font-semibold text-gray-400 uppercase mb-2">Speed</h4>
        <div className="flex gap-2">
          {SPEED_OPTIONS.map((opt) => (
            <button
              key={opt.value}
              onClick={() => onSpeedChange(opt.value)}
              className={`flex-1 py-2 rounded-lg text-sm transition-colors ${
                speed === opt.value
                  ? 'bg-town-highlight text-white'
                  : 'bg-town-surface/50 text-gray-400 hover:text-white'
              }`}
            >
              {opt.label}
            </button>
          ))}
        </div>
      </div>

      {/* Recent Events */}
      <div>
        <h4 className="text-xs font-semibold text-gray-400 uppercase mb-2">
          Recent Events ({events.length})
        </h4>
        <div className="max-h-40 overflow-y-auto space-y-1">
          {events.length > 0 ? (
            events.slice(0, maxEvents).map((event, i) => (
              <div key={i} className="text-xs text-gray-400">
                <span className="text-gray-500 font-mono">{event.tick}:</span>{' '}
                <span className={getEventColor(event.operation)}>
                  {event.message || event.operation}
                </span>
              </div>
            ))
          ) : (
            <p className="text-xs text-gray-600">{getEmptyState('noData').description}</p>
          )}
        </div>
      </div>
    </div>
  );
}

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
  density: Density;
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
  density,
}: TownHeaderProps) {
  const isCompact = density === 'compact';

  return (
    <div className={`bg-town-surface/50 border-b border-town-accent/30 ${isCompact ? 'px-3 py-1.5' : 'px-4 py-2'}`}>
      <div className="flex items-center justify-between">
        {/* Left: Town info */}
        <div className="flex items-center gap-3">
          <h1 className={`font-semibold ${isCompact ? 'text-sm' : ''}`}>Town: {townId}</h1>
          <div className={`flex items-center gap-2 text-gray-400 ${isCompact ? 'text-xs' : 'text-sm'}`}>
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

        {/* Right: Controls */}
        <div className="flex items-center gap-2">
          <button
            onClick={onTogglePlay}
            className={`bg-town-accent/30 rounded hover:bg-town-accent/50 transition-colors ${
              isCompact ? 'px-2 py-1 text-xs' : 'px-3 py-1 text-sm'
            }`}
          >
            {isPlaying ? '⏸️ Pause' : '▶️ Play'}
          </button>
          <select
            value={speed}
            onChange={(e) => onSpeedChange(parseFloat(e.target.value))}
            className={`bg-town-surface border border-town-accent/30 rounded ${
              isCompact ? 'px-1.5 py-1 text-xs' : 'px-2 py-1 text-sm'
            }`}
          >
            {SPEED_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>{opt.label}</option>
            ))}
          </select>
        </div>
      </div>
    </div>
  );
}

interface EventFeedProps {
  events: TownEvent[];
  isOpen: boolean;
  onToggle: () => void;
  density: Density;
}

function EventFeed({ events, isOpen, onToggle, density }: EventFeedProps) {
  const maxEvents = MAX_EVENTS[density];
  const isCompact = density === 'compact';

  return (
    <div className={`border-t border-town-accent/30 transition-all ${isOpen ? 'h-64' : isCompact ? 'h-8' : 'h-10'}`}>
      <button
        onClick={onToggle}
        className={`w-full flex items-center justify-between font-semibold hover:bg-town-surface/50 ${
          isCompact ? 'px-3 py-1.5 text-xs' : 'px-4 py-2 text-sm'
        }`}
      >
        <span>Event Feed ({events.length})</span>
        <span>{isOpen ? '▼' : '▲'}</span>
      </button>
      {isOpen && (
        <div className={`overflow-y-auto ${isCompact ? 'px-3 pb-3 h-[calc(100%-32px)]' : 'px-4 pb-4 h-[calc(100%-40px)]'}`}>
          {events.length > 0 ? (
            <ul className={`space-y-1 ${isCompact ? 'text-xs' : 'text-sm'}`}>
              {events.slice(0, maxEvents).map((event, i) => (
                <li key={i} className="text-gray-400">
                  <span className={`text-gray-500 font-mono ${isCompact ? 'text-[10px]' : 'text-xs'}`}>{event.tick}:</span>{' '}
                  <span className={getEventColor(event.operation)}>
                    {event.message || event.operation}
                  </span>
                </li>
              ))}
            </ul>
          ) : (
            <p className={`text-gray-600 ${isCompact ? 'text-xs' : 'text-sm'}`}>{getEmptyState('noData').description} Press Play to start.</p>
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
