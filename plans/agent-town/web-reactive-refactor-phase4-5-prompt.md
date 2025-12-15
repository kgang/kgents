# Phases 4 & 5: Migration and Cleanup - Continuation Prompt

## Context

**Previous Phases Complete:**
- Phase 1: Foundation (76 tests) - `types.ts`, `useWidgetState.ts`, `WidgetRenderer.tsx`, `context.tsx`
- Phase 2: Widget Components (109 tests) - `/widgets/` directory with primitives/, layout/, cards/, dashboards/
- Phase 3: SSE Integration (19 + 25 tests) - `live.state` event emission, `useTownStreamWidget` hook

**Goal:** Migrate `Town.tsx` to consume widget JSON from `useTownStreamWidget` instead of building state incrementally via Zustand. Then remove Zustand dependency.

---

## Current State Analysis

### What Exists

**Zustand Stores (`src/stores/`):**
- `townStore.ts` - Manages town state (citizens, positions, events, phase, day, etc.)
- `uiStore.ts` - UI state (event feed open/closed)

**Town Page (`src/pages/Town.tsx`):**
- Uses `useTownStore` for all state
- Uses `useTownStream` hook (old, incremental)
- Renders `Mesa` (PixiJS canvas) + `CitizenPanel` + event feed
- Complex loading/error state handling

**Mesa Component (`src/components/town/Mesa.tsx`):**
- Reads directly from `useTownStore`:
  - `citizens`, `selectedCitizenId`, `hoveredCitizenId`, `activeInteractions`
- Computes citizen positions from regions
- Renders PixiJS canvas with citizen circles and interaction lines

**CitizenPanel (`src/components/town/CitizenPanel.tsx`):**
- Reads from `useTownStore`: `selectedCitizenId`, `townId`, `citizens`, `currentLOD`
- Fetches citizen manifest via API
- Displays LOD-gated content

**New Widget Infrastructure (from Phases 1-3):**
- `useTownStreamWidget` hook returns `{ dashboard, events, isConnected, isPlaying, connect, disconnect }`
- `ColonyDashboard` widget component consumes `ColonyDashboardJSON`
- `CitizenCard` widget component consumes `CitizenCardJSON`
- `WidgetRenderer` dispatches to components by type

### The Gap

| Aspect | Current | Target |
|--------|---------|--------|
| State source | Zustand store | `useTownStreamWidget.dashboard` |
| Citizen data | `CitizenSummary[]` from store | `CitizenCardJSON[]` from dashboard |
| Events | `TownEvent[]` from store | `TownEvent[]` from hook |
| Playback control | `useTownStore.setPlaying()` | Local state + hook control |
| Mesa data | Reads from store | Receives props from parent |

---

## Implementation Tasks

### Phase 4: Migration (Effort: 1)

#### Task 4.1: Create TownV2 Page

Create a new version of the Town page that uses widget infrastructure. Keep the original for backwards compatibility during migration.

**File:** `impl/claude/web/src/pages/TownV2.tsx` (NEW)

```typescript
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
import type { ColonyDashboardJSON, CitizenCardJSON } from '@/reactive/types';

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
        speed={speed}
        onTogglePlay={() => isPlaying ? disconnect() : connect()}
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
// Sub-components (extract to separate files if large)
// =============================================================================

interface TownHeaderProps {
  townId: string | null;
  phase: string;
  day: number;
  citizenCount: number;
  isPlaying: boolean;
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
          <span>•</span>
          <span className={`font-medium ${getPhaseColor(phase)}`}>{phase}</span>
          <span>•</span>
          <span>{citizenCount} citizens</span>
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
  events: Array<{ tick: number; operation: string; message?: string }>;
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
    case 'MORNING': return 'text-phase-morning';
    case 'AFTERNOON': return 'text-phase-afternoon';
    case 'EVENING': return 'text-phase-evening';
    case 'NIGHT': return 'text-phase-night';
    default: return 'text-gray-400';
  }
}

function getEventColor(operation: string): string {
  if (['greet', 'gossip', 'trade'].includes(operation)) return 'text-green-400';
  if (['work', 'craft', 'build'].includes(operation)) return 'text-blue-400';
  if (['reflect', 'journal', 'meditate'].includes(operation)) return 'text-purple-400';
  if (['evolve', 'transform'].includes(operation)) return 'text-yellow-400';
  return 'text-gray-300';
}
```

#### Task 4.2: Create MesaV2 Component

Mesa needs to receive citizens as props instead of reading from Zustand.

**File:** `impl/claude/web/src/components/town/MesaV2.tsx` (NEW)

```typescript
/**
 * MesaV2: Props-based Mesa canvas.
 *
 * Receives citizens as props instead of reading from Zustand store.
 * This enables the component to work with widget JSON data.
 */

import { Stage, Container, Graphics, Text } from '@pixi/react';
import { useCallback, useMemo } from 'react';
import * as PIXI from 'pixi.js';
import { gridToScreen, REGION_GRID_POSITIONS } from '@/lib/regionGrid';
import type { CitizenCardJSON } from '@/reactive/types';

// =============================================================================
// Constants
// =============================================================================

const CELL_SIZE = 24;

const ARCHETYPE_COLORS: Record<string, number> = {
  builder: 0x3b82f6,
  trader: 0xf59e0b,
  healer: 0x22c55e,
  scholar: 0x8b5cf6,
  watcher: 0x6b7280,
  // Add lowercase versions
  Builder: 0x3b82f6,
  Trader: 0xf59e0b,
  Healer: 0x22c55e,
  Scholar: 0x8b5cf6,
  Watcher: 0x6b7280,
};

const PHASE_ALPHA: Record<string, number> = {
  IDLE: 1.0,
  WORKING: 0.9,
  SOCIALIZING: 1.0,
  REFLECTING: 0.8,
  RESTING: 0.5,
};

// =============================================================================
// Types
// =============================================================================

interface MesaV2Props {
  width?: number;
  height?: number;
  citizens: CitizenCardJSON[];
  selectedCitizenId: string | null;
  onSelectCitizen?: (id: string) => void;
  onHoverCitizen?: (id: string | null) => void;
}

interface CitizenPosition {
  citizen: CitizenCardJSON;
  screenX: number;
  screenY: number;
}

// =============================================================================
// Component
// =============================================================================

export function MesaV2({
  width = 800,
  height = 600,
  citizens,
  selectedCitizenId,
  onSelectCitizen,
  onHoverCitizen,
}: MesaV2Props) {
  const offsetX = width / 2;
  const offsetY = height / 4;

  // Calculate citizen screen positions
  const citizenPositions = useMemo<CitizenPosition[]>(() => {
    const byRegion = new Map<string, CitizenCardJSON[]>();
    citizens.forEach((c) => {
      const list = byRegion.get(c.region) || [];
      list.push(c);
      byRegion.set(c.region, list);
    });

    const positions: CitizenPosition[] = [];
    byRegion.forEach((regionCitizens, region) => {
      const basePos = REGION_GRID_POSITIONS[region] || { x: 10, y: 10 };

      regionCitizens.forEach((citizen, index) => {
        let gridX = basePos.x;
        let gridY = basePos.y;

        if (regionCitizens.length > 1) {
          const angleStep = (2 * Math.PI) / regionCitizens.length;
          const angle = angleStep * index;
          const radius = 1.5;
          gridX += Math.cos(angle) * radius;
          gridY += Math.sin(angle) * radius;
        }

        const screen = gridToScreen(gridX, gridY, CELL_SIZE, offsetX, offsetY);
        positions.push({
          citizen,
          screenX: screen.x,
          screenY: screen.y,
        });
      });
    });

    return positions;
  }, [citizens, offsetX, offsetY]);

  // Draw citizen circle
  const drawCitizen = useCallback(
    (g: PIXI.Graphics, pos: CitizenPosition) => {
      const { citizen, screenX, screenY } = pos;
      const color = ARCHETYPE_COLORS[citizen.archetype] || 0x888888;
      const alpha = PHASE_ALPHA[citizen.phase] || 1.0;
      const isSelected = citizen.citizen_id === selectedCitizenId;
      const radius = isSelected ? 14 : 10;

      g.clear();

      // Selection ring
      if (isSelected) {
        g.lineStyle(3, 0xffffff, 0.8);
        g.drawCircle(screenX, screenY, radius + 4);
      }

      // Main circle
      g.beginFill(color, alpha);
      g.drawCircle(screenX, screenY, radius);
      g.endFill();
    },
    [selectedCitizenId]
  );

  return (
    <Stage
      width={width}
      height={height}
      options={{ backgroundColor: 0x1a1a2e, antialias: true }}
    >
      <Container>
        {/* Region labels */}
        {Object.entries(REGION_GRID_POSITIONS).map(([region, pos]) => {
          const screen = gridToScreen(pos.x, pos.y - 1.5, CELL_SIZE, offsetX, offsetY);
          return (
            <Text
              key={region}
              text={region}
              x={screen.x}
              y={screen.y}
              anchor={0.5}
              style={
                new PIXI.TextStyle({
                  fontSize: 10,
                  fill: 0x666666,
                  fontFamily: 'monospace',
                })
              }
            />
          );
        })}

        {/* Citizens */}
        {citizenPositions.map((pos) => (
          <Graphics
            key={pos.citizen.citizen_id}
            draw={(g) => drawCitizen(g, pos)}
            eventMode="static"
            cursor="pointer"
            pointerdown={() => onSelectCitizen?.(pos.citizen.citizen_id)}
            pointerover={() => onHoverCitizen?.(pos.citizen.citizen_id)}
            pointerout={() => onHoverCitizen?.(null)}
          />
        ))}

        {/* Citizen labels */}
        {citizenPositions.map((pos) => (
          <Text
            key={`label-${pos.citizen.citizen_id}`}
            text={pos.citizen.name}
            x={pos.screenX}
            y={pos.screenY + 18}
            anchor={0.5}
            style={
              new PIXI.TextStyle({
                fontSize: 9,
                fill: 0xaaaaaa,
                fontFamily: 'sans-serif',
              })
            }
          />
        ))}
      </Container>
    </Stage>
  );
}
```

#### Task 4.3: Create CitizenPanelV2 Component

CitizenPanel needs to accept citizen data as props.

**File:** `impl/claude/web/src/components/town/CitizenPanelV2.tsx` (NEW)

```typescript
/**
 * CitizenPanelV2: Props-based citizen detail panel.
 *
 * Receives citizen from props instead of reading from Zustand.
 */

import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useUserStore, selectCanInhabit } from '@/stores/userStore';
import { townApi } from '@/api/client';
import { LODGate } from '@/components/paywall/LODGate';
import type { CitizenCardJSON } from '@/reactive/types';
import type { CitizenManifest } from '@/api/types';

interface CitizenPanelV2Props {
  citizen: CitizenCardJSON;
  townId: string;
  onClose: () => void;
}

export function CitizenPanelV2({ citizen, townId, onClose }: CitizenPanelV2Props) {
  const { userId, tier } = useUserStore();
  const canInhabit = useUserStore(selectCanInhabit());
  const [manifest, setManifest] = useState<CitizenManifest | null>(null);
  const [currentLOD, setCurrentLOD] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Fetch citizen manifest when LOD changes
  useEffect(() => {
    const fetchManifest = async () => {
      setLoading(true);
      setError(null);
      try {
        const res = await townApi.getCitizen(
          townId,
          citizen.name,
          currentLOD,
          userId || 'anonymous'
        );
        setManifest(res.data.citizen);
      } catch (err) {
        console.error('Failed to fetch citizen:', err);
        setError('Failed to load citizen details');
      } finally {
        setLoading(false);
      }
    };

    fetchManifest();
  }, [citizen.name, townId, currentLOD, userId]);

  if (loading) {
    return (
      <div className="p-6 text-center text-gray-400">
        <div className="animate-pulse">Loading...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6 text-center text-red-400">
        <p>{error}</p>
        <button onClick={() => setCurrentLOD(0)} className="mt-2 text-sm text-gray-400 hover:text-white">
          Reset to LOD 0
        </button>
      </div>
    );
  }

  return (
    <div className="p-4 space-y-4 overflow-y-auto h-full">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold">{citizen.name}</h2>
        <button onClick={onClose} className="text-gray-400 hover:text-white">
          ✕
        </button>
      </div>

      {/* Basic info from CitizenCardJSON */}
      <div className="space-y-2">
        <div className="flex items-center gap-2">
          <span className="text-2xl">{getPhaseGlyph(citizen.phase)}</span>
          <span className="text-cyan-400">{citizen.archetype}</span>
        </div>
        <div className="text-sm text-gray-400">
          <span>{citizen.phase}</span> • <span>{citizen.region}</span>
        </div>
        <div className="text-sm text-gray-500">{citizen.mood}</div>
      </div>

      {/* Eigenvectors */}
      <div className="space-y-1">
        <h3 className="text-sm font-semibold text-gray-400">Eigenvectors</h3>
        <EigenvectorBar label="Warmth" value={citizen.eigenvectors.warmth} />
        <EigenvectorBar label="Curiosity" value={citizen.eigenvectors.curiosity} />
        <EigenvectorBar label="Trust" value={citizen.eigenvectors.trust} />
      </div>

      {/* Capability */}
      <div className="space-y-1">
        <h3 className="text-sm font-semibold text-gray-400">Capability</h3>
        <div className="h-2 bg-gray-700 rounded">
          <div
            className="h-full bg-yellow-500 rounded"
            style={{ width: `${citizen.capability * 100}%` }}
          />
        </div>
      </div>

      {/* LOD selector (for higher tiers) */}
      <div className="pt-4 border-t border-gray-700">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm text-gray-400">Detail Level</span>
          <select
            value={currentLOD}
            onChange={(e) => setCurrentLOD(parseInt(e.target.value))}
            className="bg-gray-800 border border-gray-600 rounded px-2 py-1 text-sm"
          >
            <option value="0">LOD 0 - Silhouette</option>
            <option value="1">LOD 1 - Sketch</option>
            <option value="2">LOD 2 - Portrait</option>
            <option value="3">LOD 3 - Biography</option>
            <option value="4">LOD 4 - Psyche</option>
            <option value="5">LOD 5 - Full Manifest</option>
          </select>
        </div>
      </div>

      {/* INHABIT button */}
      {canInhabit && (
        <Link
          to={`/town/${townId}/inhabit/${citizen.name}`}
          className="block w-full text-center px-4 py-2 bg-purple-600 hover:bg-purple-500 rounded font-medium transition-colors"
        >
          🎭 INHABIT
        </Link>
      )}
    </div>
  );
}

function EigenvectorBar({ label, value }: { label: string; value: number }) {
  return (
    <div className="flex items-center gap-2">
      <span className="text-xs text-gray-500 w-16">{label}</span>
      <div className="flex-1 h-1.5 bg-gray-700 rounded">
        <div
          className="h-full bg-blue-500 rounded"
          style={{ width: `${value * 100}%` }}
        />
      </div>
      <span className="text-xs text-gray-500 w-8">{(value * 100).toFixed(0)}%</span>
    </div>
  );
}

function getPhaseGlyph(phase: string): string {
  switch (phase) {
    case 'IDLE': return '○';
    case 'SOCIALIZING': return '◉';
    case 'WORKING': return '●';
    case 'REFLECTING': return '◐';
    case 'RESTING': return '◯';
    default: return '?';
  }
}
```

#### Task 4.4: Add Route for TownV2

**File:** `impl/claude/web/src/main.tsx` (MODIFY)

Add a route for TownV2 (feature-flagged or alongside Town):

```typescript
// Add import
import TownV2 from './pages/TownV2';

// Add route (can be feature-flagged)
<Route path="/town-v2/:townId" element={<TownV2 />} />
```

#### Task 4.5: Deprecate Zustand Stores

**File:** `impl/claude/web/src/stores/townStore.ts` (MODIFY)

Add deprecation notice:

```typescript
/**
 * @deprecated Use useTownStreamWidget hook instead.
 *
 * Migration guide:
 * - Replace `useTownStore().citizens` with `useTownStreamWidget().dashboard.citizens`
 * - Replace `useTownStore().events` with `useTownStreamWidget().events`
 * - Replace `useTownStore().currentPhase` with `useTownStreamWidget().dashboard.phase`
 *
 * This store will be removed in the next major version.
 */
export const useTownStore = create<TownState>()(
  // ... existing implementation
);
```

#### Task 4.6: Tests for Phase 4

**File:** `impl/claude/web/tests/unit/pages/TownV2.test.tsx` (NEW)

```typescript
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import TownV2 from '@/pages/TownV2';

// Mock useTownStreamWidget
vi.mock('@/hooks/useTownStreamWidget', () => ({
  useTownStreamWidget: vi.fn(() => ({
    dashboard: {
      type: 'colony_dashboard',
      colony_id: 'test-town',
      phase: 'MORNING',
      day: 1,
      metrics: { total_events: 10, total_tokens: 100, entropy_budget: 1.0 },
      citizens: [
        {
          type: 'citizen_card',
          citizen_id: 'alice-123',
          name: 'Alice',
          archetype: 'builder',
          phase: 'WORKING',
          nphase: 'ACT',
          activity: [],
          capability: 0.8,
          entropy: 0.1,
          region: 'plaza',
          mood: 'happy',
          eigenvectors: { warmth: 0.7, curiosity: 0.8, trust: 0.6 },
        },
      ],
      grid_cols: 5,
      selected_citizen_id: null,
    },
    events: [],
    isConnected: true,
    isPlaying: true,
    connect: vi.fn(),
    disconnect: vi.fn(),
  })),
}));

// Mock townApi
vi.mock('@/api/client', () => ({
  townApi: {
    get: vi.fn().mockResolvedValue({ data: { id: 'test-town', name: 'Test Town' } }),
    create: vi.fn().mockResolvedValue({ data: { id: 'new-town', name: 'Demo Town' } }),
  },
}));

describe('TownV2', () => {
  it('renders town header with phase and day', async () => {
    render(
      <MemoryRouter initialEntries={['/town/test-town']}>
        <Routes>
          <Route path="/town/:townId" element={<TownV2 />} />
        </Routes>
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByText(/Day 1/)).toBeInTheDocument();
      expect(screen.getByText(/MORNING/)).toBeInTheDocument();
    });
  });

  it('displays citizen count from dashboard', async () => {
    render(
      <MemoryRouter initialEntries={['/town/test-town']}>
        <Routes>
          <Route path="/town/:townId" element={<TownV2 />} />
        </Routes>
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByText(/1 citizens/)).toBeInTheDocument();
    });
  });
});
```

---

### Phase 5: Cleanup (Effort: 0.5)

#### Task 5.1: Remove Zustand Dependency

Once TownV2 is stable and replaces Town.tsx:

```bash
cd impl/claude/web
npm uninstall zustand immer
```

#### Task 5.2: Rename TownV2 to Town

```bash
# Remove old Town.tsx
rm src/pages/Town.tsx

# Rename TownV2
mv src/pages/TownV2.tsx src/pages/Town.tsx

# Update imports in Town.tsx
sed -i '' 's/TownV2/Town/g' src/pages/Town.tsx

# Same for components
rm src/components/town/Mesa.tsx
rm src/components/town/CitizenPanel.tsx
mv src/components/town/MesaV2.tsx src/components/town/Mesa.tsx
mv src/components/town/CitizenPanelV2.tsx src/components/town/CitizenPanel.tsx
```

#### Task 5.3: Remove Old Stores

```bash
rm src/stores/townStore.ts
# Keep uiStore.ts if used elsewhere, or migrate its state too
```

#### Task 5.4: Update Exports

**File:** `impl/claude/web/src/index.ts` (MODIFY)

```typescript
// Reactive infrastructure
export * from './reactive';
export * from './widgets';

// Hooks
export { useTownStreamWidget } from './hooks/useTownStreamWidget';

// Remove deprecated exports
// export { useTownStore } from './stores/townStore';  // REMOVED
```

#### Task 5.5: Update Documentation

**File:** `impl/claude/web/README.md` (MODIFY)

Add section on new architecture:

```markdown
## Architecture

### Widget-Based Rendering

The Agent Town frontend uses a widget-based architecture:

1. **Backend emits widget JSON** via SSE (`live.state` events)
2. **`useTownStreamWidget` hook** consumes the JSON stream
3. **Widget components** render from JSON (type-discriminated union)

```
Backend (Python)                    Frontend (React)
     │                                    │
     │  ColonyDashboard.to_json()         │
     ├───────── SSE ──────────────────────►│ useTownStreamWidget()
     │  live.state event                  │
     │                                    ▼
     │                              ColonyDashboardJSON
     │                                    │
     │                              WidgetRenderer
     │                                    │
     │                              React Components
```

### Key Files

| File | Purpose |
|------|---------|
| `src/hooks/useTownStreamWidget.ts` | SSE streaming hook |
| `src/reactive/types.ts` | Widget JSON type definitions |
| `src/reactive/WidgetRenderer.tsx` | Type-discriminated dispatcher |
| `src/widgets/` | Widget component implementations |
```

---

## Acceptance Criteria

### Phase 4

1. **TownV2 renders from dashboard JSON**: All UI state derived from `useTownStreamWidget().dashboard`
2. **MesaV2 accepts props**: No direct Zustand access
3. **CitizenPanelV2 accepts props**: Citizen data passed from parent
4. **Feature parity**: TownV2 has same functionality as Town.tsx
5. **Tests pass**: Unit tests for TownV2, MesaV2, CitizenPanelV2
6. **Deprecation notices**: Zustand stores marked deprecated

### Phase 5

1. **Zustand removed**: No zustand or immer in package.json
2. **Clean codebase**: No V2 suffixes, single implementation
3. **Documentation updated**: README reflects new architecture
4. **All tests pass**: 100+ reactive/widget tests, new page tests

---

## Files to Create/Modify

### Phase 4

| File | Action |
|------|--------|
| `src/pages/TownV2.tsx` | Create - new widget-based page |
| `src/components/town/MesaV2.tsx` | Create - props-based Mesa |
| `src/components/town/CitizenPanelV2.tsx` | Create - props-based panel |
| `src/main.tsx` | Modify - add TownV2 route |
| `src/stores/townStore.ts` | Modify - add deprecation notice |
| `tests/unit/pages/TownV2.test.tsx` | Create - page tests |

### Phase 5

| File | Action |
|------|--------|
| `package.json` | Modify - remove zustand, immer |
| `src/pages/Town.tsx` | Delete old, rename TownV2 |
| `src/components/town/Mesa.tsx` | Delete old, rename MesaV2 |
| `src/components/town/CitizenPanel.tsx` | Delete old, rename CitizenPanelV2 |
| `src/stores/townStore.ts` | Delete |
| `src/index.ts` | Modify - update exports |
| `README.md` | Modify - update architecture docs |

---

## Verification Commands

```bash
# Phase 4
cd impl/claude/web

# Run all tests
npm test

# Specific tests
npm test -- --run tests/unit/pages/TownV2.test.tsx
npm test -- --run tests/unit/reactive tests/unit/widgets

# Type check
npm run typecheck

# Dev server test (manual)
npm run dev
# Visit http://localhost:3000/town-v2/demo

# Phase 5
# After cleanup, verify no zustand imports
grep -r "zustand" src/ --include="*.ts" --include="*.tsx"
# Should return empty

# Verify package.json
cat package.json | grep zustand
# Should return empty
```

---

## Notes

- **Parallel operation**: TownV2 runs alongside Town.tsx until stable
- **Feature flag option**: Could use env var to control which version loads at `/town/:id`
- **Mesa compatibility**: MesaV2 uses same PixiJS rendering, just different data source
- **userStore preserved**: UI preferences (tier, userId) still use Zustand if not migrated
- **Gradual rollout**: Test TownV2 thoroughly before replacing Town.tsx

---

## Dependencies

- Phase 3 complete (useTownStreamWidget hook, live.state emission)
- Widget components exist (ColonyDashboard, CitizenCard, etc.)
- WidgetRenderer dispatches correctly
- Backend emits ColonyDashboardJSON in live.state events
