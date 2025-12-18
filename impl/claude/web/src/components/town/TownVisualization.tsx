/**
 * TownVisualization - Agent Town Visualization Core
 *
 * Extracted visualization component for projection-first architecture.
 * Receives streaming data from useTownStreamWidget and handles all rendering.
 *
 * Features:
 * - Mesa (2D isometric canvas) with citizen positions
 * - Citizen selection and detail panel
 * - Event feed with streaming events
 * - Density-adaptive layouts (mobile/tablet/desktop)
 * - Playback controls (play/pause, speed)
 *
 * @see spec/protocols/os-shell.md - Part IV: Gallery Primitive Reliance
 * @see docs/skills/crown-jewel-patterns.md
 */

import { useState, useRef, useEffect, useCallback } from 'react';
import type { ColonyDashboardJSON } from '../../reactive/types';
import type { TownEvent } from '../../api/types';
import type { Density } from '../../shell/types';
import { Mesa } from './Mesa';
import { CitizenPanel } from './CitizenPanel';
import { TownTracePanel } from './TownTracePanel';
import { ObserverSelector, type ObserverUmwelt } from './ObserverSelector';
import { ColonyDashboard } from '../../widgets/dashboards';
import { ElasticSplit, ElasticContainer } from '../elastic';
import { BottomDrawer } from '../elastic/BottomDrawer';
import { FloatingActions, type FloatingAction } from '../elastic/FloatingActions';
import { FirstVisitOverlay } from '../categorical/FirstVisitOverlay';
import { useTeachingModeSafe } from '../../hooks';
import { getEmptyState } from '../../constants';
import {
  Users,
  Play,
  Pause,
  Settings,
  User,
  ChevronUp,
  ChevronDown,
  Clock,
  Lightbulb,
} from 'lucide-react';

// =============================================================================
// Constants
// =============================================================================

const MAX_EVENTS = {
  compact: 10,
  comfortable: 15,
  spacious: 20,
} as const;

const SPEED_OPTIONS = [
  { value: 0.5, label: '0.5x' },
  { value: 1, label: '1x' },
  { value: 2, label: '2x' },
  { value: 4, label: '4x' },
];

// =============================================================================
// Types
// =============================================================================

export interface TownVisualizationProps {
  /** Town ID */
  townId: string;
  /** Dashboard state from SSE stream */
  dashboard: ColonyDashboardJSON | null;
  /** Events from SSE stream */
  events: TownEvent[];
  /** Whether SSE is connected */
  isConnected: boolean;
  /** Whether simulation is playing */
  isPlaying: boolean;
  /** Current speed */
  speed: number;
  /** Layout density */
  density: Density;
  /** Whether mobile layout */
  isMobile: boolean;
  /** Whether tablet layout */
  isTablet: boolean;
  /** Whether desktop layout */
  isDesktop: boolean;
  /** Connect to stream */
  onConnect: () => void;
  /** Disconnect from stream */
  onDisconnect: () => void;
  /** Change playback speed */
  onSpeedChange: (speed: number) => void;
}

// =============================================================================
// Helper Functions
// =============================================================================

function getPhaseColor(phase: string): string {
  switch (phase) {
    case 'MORNING':
      return 'text-amber-400';
    case 'AFTERNOON':
      return 'text-orange-400';
    case 'EVENING':
      return 'text-purple-400';
    case 'NIGHT':
      return 'text-indigo-400';
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

// =============================================================================
// Sub-components
// =============================================================================

interface TownHeaderProps {
  townId: string;
  phase: string;
  day: number;
  citizenCount: number;
  isPlaying: boolean;
  isConnected: boolean;
  speed: number;
  onTogglePlay: () => void;
  onSpeedChange: (speed: number) => void;
  density: Density;
  observer: ObserverUmwelt;
  onObserverChange: (observer: ObserverUmwelt) => void;
  /** Whether teaching mode is enabled */
  teachingEnabled: boolean;
  /** Toggle teaching mode */
  onToggleTeaching: () => void;
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
  observer,
  onObserverChange,
  teachingEnabled,
  onToggleTeaching,
}: TownHeaderProps) {
  const isCompact = density === 'compact';

  return (
    <div
      className={`bg-violet-950/50 border-b border-violet-500/30 ${isCompact ? 'px-3 py-1.5' : 'px-4 py-2'}`}
    >
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2">
            <Users className="w-5 h-5 text-violet-400" />
            <h1 className={`font-semibold ${isCompact ? 'text-sm' : ''}`}>Town: {townId}</h1>
          </div>
          <div
            className={`flex items-center gap-2 text-gray-400 ${isCompact ? 'text-xs' : 'text-sm'}`}
          >
            <span>Day {day}</span>
            <span className="text-gray-600">|</span>
            <span className={`font-medium ${getPhaseColor(phase)}`}>{phase}</span>
            <span className="text-gray-600">|</span>
            <span>{citizenCount} citizens</span>
            {!isConnected && (
              <>
                <span className="text-gray-600">|</span>
                <span className="text-yellow-500">Disconnected</span>
              </>
            )}
          </div>
        </div>

        <div className="flex items-center gap-2">
          {/* Teaching Mode Toggle (Phase 4) */}
          <button
            onClick={onToggleTeaching}
            className={`p-1.5 rounded transition-colors ${
              teachingEnabled
                ? 'bg-blue-500/30 text-blue-400'
                : 'bg-violet-950/50 text-gray-500 hover:text-gray-300'
            }`}
            title={`Teaching Mode: ${teachingEnabled ? 'ON' : 'OFF'}`}
          >
            <Lightbulb className={isCompact ? 'w-3.5 h-3.5' : 'w-4 h-4'} />
          </button>
          {/* Observer selector (Phase 2) */}
          <ObserverSelector value={observer} onChange={onObserverChange} compact />
          <button
            onClick={onTogglePlay}
            className={`flex items-center gap-1.5 bg-violet-500/30 rounded hover:bg-violet-500/50 transition-colors ${
              isCompact ? 'px-2 py-1 text-xs' : 'px-3 py-1 text-sm'
            }`}
          >
            {isPlaying ? <Pause className="w-3.5 h-3.5" /> : <Play className="w-3.5 h-3.5" />}
            {isPlaying ? 'Pause' : 'Play'}
          </button>
          <select
            value={speed}
            onChange={(e) => onSpeedChange(parseFloat(e.target.value))}
            className={`bg-violet-950 border border-violet-500/30 rounded ${
              isCompact ? 'px-1.5 py-1 text-xs' : 'px-2 py-1 text-sm'
            }`}
          >
            {SPEED_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
        </div>
      </div>
    </div>
  );
}

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
      <div>
        <h4 className="text-xs font-semibold text-gray-400 uppercase mb-2">Playback</h4>
        <div className="flex items-center gap-3">
          <button
            onClick={onTogglePlay}
            className={`flex-1 py-2 rounded-lg font-medium transition-colors flex items-center justify-center gap-2 ${
              isPlaying ? 'bg-violet-500 text-white' : 'bg-violet-400 text-white'
            }`}
          >
            {isPlaying ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
            {isPlaying ? 'Pause' : 'Play'}
          </button>
        </div>
      </div>

      <div>
        <h4 className="text-xs font-semibold text-gray-400 uppercase mb-2">Speed</h4>
        <div className="flex gap-2">
          {SPEED_OPTIONS.map((opt) => (
            <button
              key={opt.value}
              onClick={() => onSpeedChange(opt.value)}
              className={`flex-1 py-2 rounded-lg text-sm transition-colors ${
                speed === opt.value
                  ? 'bg-violet-400 text-white'
                  : 'bg-violet-950/50 text-gray-400 hover:text-white'
              }`}
            >
              {opt.label}
            </button>
          ))}
        </div>
      </div>

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

// =============================================================================
// Main Component
// =============================================================================

export function TownVisualization({
  townId,
  dashboard,
  events,
  isConnected,
  isPlaying,
  speed,
  density,
  isMobile,
  isTablet: _isTablet,
  isDesktop,
  onConnect,
  onDisconnect,
  onSpeedChange,
}: TownVisualizationProps) {
  // Note: isTablet reserved for future responsive refinements
  void _isTablet;
  // Selection state
  const [selectedCitizenId, setSelectedCitizenId] = useState<string | null>(null);
  const [isEventFeedOpen, setIsEventFeedOpen] = useState(false);

  // Observer umwelt state (Phase 2)
  const [observer, setObserver] = useState<ObserverUmwelt>('default');

  // Trace panel state (Phase 2)
  const [showTracePanel, setShowTracePanel] = useState(false);

  // Teaching mode (Phase 4)
  const { enabled: teachingEnabled, toggle: toggleTeaching } = useTeachingModeSafe();

  // Mobile drawer state
  const [controlsDrawerOpen, setControlsDrawerOpen] = useState(false);
  const [citizenDrawerOpen, setCitizenDrawerOpen] = useState(false);
  const [tracePanelDrawerOpen, setTracePanelDrawerOpen] = useState(false);

  // Mesa sizing
  const mesaContainerRef = useRef<HTMLDivElement>(null);
  const [mesaSize, setMesaSize] = useState({ width: 800, height: 600 });

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

  const handleTogglePlay = useCallback(() => {
    if (isPlaying) {
      onDisconnect();
    } else {
      onConnect();
    }
  }, [isPlaying, onConnect, onDisconnect]);

  // ==========================================================================
  // Mobile Layout
  // ==========================================================================

  if (isMobile) {
    return (
      <FirstVisitOverlay jewel="town">
        <div className="h-full flex flex-col bg-violet-950">
          <header className="flex-shrink-0 bg-violet-950/50 border-b border-violet-500/30 px-3 py-2">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Users className="w-4 h-4 text-violet-400" />
                <span className="font-semibold text-sm">{townId}</span>
                <span
                  className={`text-xs font-medium ${getPhaseColor(dashboard?.phase || 'MORNING')}`}
                >
                  {dashboard?.phase || 'MORNING'}
                </span>
              </div>
              <div className="flex items-center gap-2">
                {/* Teaching toggle (Phase 4) */}
                <button
                  onClick={toggleTeaching}
                  className={`p-1 rounded transition-colors ${
                    teachingEnabled
                      ? 'bg-blue-500/30 text-blue-400'
                      : 'bg-violet-950/50 text-gray-500'
                  }`}
                  title={`Teaching: ${teachingEnabled ? 'ON' : 'OFF'}`}
                >
                  <Lightbulb className="w-3.5 h-3.5" />
                </button>
                {/* Observer selector (compact) */}
                <ObserverSelector value={observer} onChange={setObserver} compact />
                {!isConnected && <span className="text-xs text-yellow-500">Disconnected</span>}
              </div>
            </div>
          </header>

          <div className="flex-1 relative" ref={mesaContainerRef}>
            <div className="absolute inset-0">
              <Mesa
                width={mesaSize.width}
                height={mesaSize.height}
                citizens={dashboard?.citizens || []}
                events={events}
                selectedCitizenId={selectedCitizenId}
                onSelectCitizen={(id) => {
                  setSelectedCitizenId(id);
                  if (id) setCitizenDrawerOpen(true);
                }}
              />
            </div>

            <div className="absolute top-2 left-2 bg-violet-950/90 backdrop-blur-sm rounded-lg px-2 py-1 text-[10px] text-gray-300">
              <span>Day {dashboard?.day || 1}</span>
              {' | '}
              <span className="text-violet-400">{dashboard?.citizens.length || 0}</span> citizens
            </div>

            <FloatingActions
              actions={[
                {
                  id: 'play',
                  icon: isPlaying ? <Pause className="w-5 h-5" /> : <Play className="w-5 h-5" />,
                  label: isPlaying ? 'Pause' : 'Play',
                  onClick: handleTogglePlay,
                  variant: 'primary',
                },
                {
                  id: 'trace',
                  icon: <Clock className="w-5 h-5" />,
                  label: 'Trace',
                  onClick: () => setTracePanelDrawerOpen(true),
                },
                {
                  id: 'controls',
                  icon: <Settings className="w-5 h-5" />,
                  label: 'Controls',
                  onClick: () => setControlsDrawerOpen(true),
                },
                ...(selectedCitizenId
                  ? [
                      {
                        id: 'citizen',
                        icon: <User className="w-5 h-5" />,
                        label: 'View Citizen',
                        onClick: () => setCitizenDrawerOpen(true),
                      } as FloatingAction,
                    ]
                  : []),
              ]}
              position="bottom-right"
            />
          </div>

          <BottomDrawer
            isOpen={controlsDrawerOpen}
            onClose={() => setControlsDrawerOpen(false)}
            title="Controls"
          >
            <ControlsPanel
              speed={speed}
              onSpeedChange={onSpeedChange}
              isPlaying={isPlaying}
              onTogglePlay={handleTogglePlay}
              events={events}
              density={density}
            />
          </BottomDrawer>

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
                townId={townId}
                onClose={() => {
                  setCitizenDrawerOpen(false);
                  setSelectedCitizenId(null);
                }}
              />
            )}
          </BottomDrawer>

          {/* Trace Panel Drawer (Phase 2) */}
          <BottomDrawer
            isOpen={tracePanelDrawerOpen}
            onClose={() => setTracePanelDrawerOpen(false)}
            title="Town Witness"
          >
            <div className="p-4">
              <TownTracePanel
                events={events}
                maxEvents={20}
                showTeaching={teachingEnabled}
                compact={false}
              />
            </div>
          </BottomDrawer>
        </div>
      </FirstVisitOverlay>
    );
  }

  // ==========================================================================
  // Tablet/Desktop Layout
  // ==========================================================================

  return (
    <FirstVisitOverlay jewel="town">
      <div className="h-full flex flex-col">
        <TownHeader
          townId={townId}
          phase={dashboard?.phase || 'MORNING'}
          day={dashboard?.day || 1}
          citizenCount={dashboard?.citizens.length || 0}
          isPlaying={isPlaying}
          isConnected={isConnected}
          speed={speed}
          onTogglePlay={handleTogglePlay}
          onSpeedChange={onSpeedChange}
          density={density}
          observer={observer}
          onObserverChange={setObserver}
          teachingEnabled={teachingEnabled}
          onToggleTeaching={toggleTeaching}
        />

        <div className="flex-1 overflow-hidden">
          <ElasticSplit
            direction="horizontal"
            defaultRatio={0.75}
            collapseAt={768}
            collapsePriority="secondary"
            minPaneSize={280}
            resizable={isDesktop}
            primary={
              <ElasticContainer layout="stack" overflow="scroll" className="h-full bg-violet-950">
                <div className="flex-1 relative" ref={mesaContainerRef}>
                  <div className="absolute inset-0">
                    <Mesa
                      width={mesaSize.width}
                      height={mesaSize.height}
                      citizens={dashboard?.citizens || []}
                      events={events}
                      selectedCitizenId={selectedCitizenId}
                      onSelectCitizen={setSelectedCitizenId}
                    />
                  </div>
                </div>
              </ElasticContainer>
            }
            secondary={
              <div className="h-full flex flex-col bg-violet-950/30 border-l border-violet-500/30">
                <div className="flex-1 overflow-y-auto">
                  {selectedCitizen ? (
                    <CitizenPanel
                      citizen={selectedCitizen}
                      townId={townId}
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

                {/* Feed/Trace Toggle (Phase 2) */}
                <div className="border-t border-violet-500/30">
                  <div className="flex">
                    <button
                      onClick={() => setShowTracePanel(false)}
                      className={`flex-1 flex items-center justify-center gap-1.5 px-3 py-2 text-xs font-medium transition-colors ${
                        !showTracePanel
                          ? 'bg-violet-500/30 text-violet-300'
                          : 'text-gray-400 hover:text-white hover:bg-violet-950/50'
                      }`}
                    >
                      <ChevronUp className="w-3.5 h-3.5" />
                      Events ({events.length})
                    </button>
                    <button
                      onClick={() => setShowTracePanel(true)}
                      className={`flex-1 flex items-center justify-center gap-1.5 px-3 py-2 text-xs font-medium transition-colors ${
                        showTracePanel
                          ? 'bg-violet-500/30 text-violet-300'
                          : 'text-gray-400 hover:text-white hover:bg-violet-950/50'
                      }`}
                    >
                      <Clock className="w-3.5 h-3.5" />
                      Trace
                    </button>
                  </div>

                  {/* Event Feed or Trace Panel */}
                  <div
                    className={`overflow-hidden transition-all ${isEventFeedOpen ? 'h-64' : 'h-0'}`}
                  >
                    {showTracePanel ? (
                      <div className="p-3 max-h-64 overflow-y-auto">
                        <TownTracePanel
                          events={events}
                          maxEvents={15}
                          compact
                          showTeaching={teachingEnabled}
                        />
                      </div>
                    ) : (
                      <div className="px-4 pb-4 max-h-60 overflow-y-auto">
                        {events.length > 0 ? (
                          <ul className="space-y-1 text-sm">
                            {events.slice(0, MAX_EVENTS[density]).map((event, i) => (
                              <li key={i} className="text-gray-400">
                                <span className="text-gray-500 font-mono text-xs">
                                  {event.tick}:
                                </span>{' '}
                                <span className={getEventColor(event.operation)}>
                                  {event.message || event.operation}
                                </span>
                              </li>
                            ))}
                          </ul>
                        ) : (
                          <p className="text-gray-600 text-sm">
                            {getEmptyState('noData').description} Press Play to start.
                          </p>
                        )}
                      </div>
                    )}
                  </div>

                  {/* Toggle button */}
                  <button
                    onClick={() => setIsEventFeedOpen(!isEventFeedOpen)}
                    className="w-full py-1 text-gray-500 hover:text-white hover:bg-violet-950/50 transition-colors"
                  >
                    {isEventFeedOpen ? (
                      <ChevronDown className="w-4 h-4 mx-auto" />
                    ) : (
                      <ChevronUp className="w-4 h-4 mx-auto" />
                    )}
                  </button>
                </div>
              </div>
            }
          />
        </div>
      </div>
    </FirstVisitOverlay>
  );
}

export default TownVisualization;
