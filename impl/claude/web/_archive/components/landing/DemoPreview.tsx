import { useEffect, useState, useRef } from 'react';
import { Link } from 'react-router-dom';
import { townApi } from '@/api/client';
import { REGION_GRID_POSITIONS, gridToScreen } from '@/lib/regionGrid';
import type { CitizenSummary, TownEvent } from '@/api/types';

// =============================================================================
// Constants
// =============================================================================

const GRID_SIZE = 20;
const CELL_SIZE = 16;

// Use device pixel ratio for sharp rendering
const getCanvasDimensions = () => {
  const dpr = window.devicePixelRatio || 1;
  const width = 480;
  const height = 320;
  return { width, height, dpr, scaledWidth: width * dpr, scaledHeight: height * dpr };
};

// Archetype colors - match actual archetypes from API
const ARCHETYPE_COLORS: Record<string, string> = {
  // Base archetypes
  Builder: '#3b82f6',
  Innkeeper: '#f59e0b',
  Explorer: '#10b981',
  Healer: '#22c55e',
  Elder: '#8b5cf6',
  Merchant: '#f59e0b',
  Gardener: '#22c55e',
  Scholar: '#8b5cf6',
  Watcher: '#6b7280',
  Trader: '#f59e0b',
  // Evolved archetypes
  'Gardener-Sage': '#a855f7',
  'Scout-Adapter': '#06b6d4',
  'Scholar-Synthesizer': '#ec4899',
  // Fallback
  default: '#6b7280',
};

// =============================================================================
// Types
// =============================================================================

interface DemoState {
  townId: string | null;
  citizens: CitizenSummary[];
  events: TownEvent[];
  isConnected: boolean;
  error: string | null;
}

// =============================================================================
// Component
// =============================================================================

export function DemoPreview() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const eventSourceRef = useRef<EventSource | null>(null);

  const [state, setState] = useState<DemoState>({
    townId: null,
    citizens: [],
    events: [],
    isConnected: false,
    error: null,
  });

  // Draw the canvas (called when citizens change)
  const drawCanvas = (citizens: CitizenSummary[]) => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const { width, height, dpr } = getCanvasDimensions();
    const offsetX = width / 2;
    const offsetY = height / 4;

    // Scale for retina displays
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);

    // Clear
    ctx.fillStyle = '#1a1a2e';
    ctx.fillRect(0, 0, width, height);

    // Draw subtle grid
    ctx.strokeStyle = 'rgba(22, 33, 62, 0.3)';
    ctx.lineWidth = 1;

    for (let i = 0; i <= GRID_SIZE; i += 2) {
      const startH = gridToScreen(i, 0, CELL_SIZE, offsetX, offsetY);
      const endH = gridToScreen(i, GRID_SIZE, CELL_SIZE, offsetX, offsetY);
      ctx.beginPath();
      ctx.moveTo(startH.x, startH.y);
      ctx.lineTo(endH.x, endH.y);
      ctx.stroke();

      const startV = gridToScreen(0, i, CELL_SIZE, offsetX, offsetY);
      const endV = gridToScreen(GRID_SIZE, i, CELL_SIZE, offsetX, offsetY);
      ctx.beginPath();
      ctx.moveTo(startV.x, startV.y);
      ctx.lineTo(endV.x, endV.y);
      ctx.stroke();
    }

    // Draw region highlights
    ctx.fillStyle = 'rgba(15, 52, 96, 0.15)';
    Object.values(REGION_GRID_POSITIONS).forEach((pos) => {
      const screen = gridToScreen(pos.x, pos.y, CELL_SIZE, offsetX, offsetY);
      ctx.beginPath();
      ctx.arc(screen.x, screen.y, CELL_SIZE * 1.5, 0, Math.PI * 2);
      ctx.fill();
    });

    // Group citizens by region for positioning
    const byRegion = new Map<string, CitizenSummary[]>();
    citizens.forEach((c) => {
      const list = byRegion.get(c.region) || [];
      list.push(c);
      byRegion.set(c.region, list);
    });

    // Draw citizens
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

        const { x, y } = gridToScreen(gridX, gridY, CELL_SIZE, offsetX, offsetY);
        const color = ARCHETYPE_COLORS[citizen.archetype] || ARCHETYPE_COLORS.default;

        // Citizen circle
        ctx.fillStyle = color;
        ctx.beginPath();
        ctx.arc(x, y, 8, 0, Math.PI * 2);
        ctx.fill();

        // Initial letter
        ctx.fillStyle = '#ffffff';
        ctx.font = 'bold 10px sans-serif';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(citizen.name[0], x, y);

        // Evolving indicator
        if (citizen.is_evolving) {
          ctx.strokeStyle = '#e94560';
          ctx.lineWidth = 2;
          ctx.beginPath();
          ctx.arc(x, y, 10, 0, Math.PI * 2);
          ctx.stroke();
        }
      });
    });
  };

  // Initialize demo town
  useEffect(() => {
    let mounted = true;

    const initDemo = async () => {
      try {
        console.log('[DemoPreview] Creating demo town...');
        const response = await townApi.create({
          name: 'demo-preview',
          phase: 3,
          enable_dialogue: false,
        });

        if (!mounted) return;

        const townId = response.data.id;
        console.log('[DemoPreview] Town created:', townId);

        const citizensRes = await townApi.getCitizens(townId);
        if (!mounted) return;

        console.log('[DemoPreview] Citizens loaded:', citizensRes.data.citizens.length);
        setState((s) => ({
          ...s,
          townId,
          citizens: citizensRes.data.citizens,
        }));

        // Connect to SSE
        connectSSE(townId);
      } catch (err) {
        console.error('[DemoPreview] Failed to init:', err);
        if (mounted) {
          setState((s) => ({ ...s, error: 'Demo unavailable' }));
        }
      }
    };

    const connectSSE = (townId: string) => {
      const url = `/v1/town/${townId}/live?speed=2&phases=100`;
      console.log('[DemoPreview] Connecting SSE:', url);
      const eventSource = new EventSource(url);
      eventSourceRef.current = eventSource;

      eventSource.onopen = () => {
        console.log('[DemoPreview] SSE connected');
        if (mounted) {
          setState((s) => ({ ...s, isConnected: true }));
        }
      };

      eventSource.addEventListener('live.event', (e) => {
        if (!mounted) return;
        const event: TownEvent = JSON.parse(e.data);
        console.log('[DemoPreview] Event:', event.operation, event.participants);

        setState((s) => {
          // Update events
          const newEvents = [event, ...s.events.slice(0, 4)];

          // Update citizen phases if participants
          let newCitizens = s.citizens;
          if (event.participants && event.participants.length > 0) {
            newCitizens = s.citizens.map((c) => {
              if (event.participants.includes(c.name)) {
                return { ...c, phase: getPhaseFromOperation(event.operation) };
              }
              return c;
            });
          }

          return { ...s, events: newEvents, citizens: newCitizens };
        });
      });

      eventSource.onerror = () => {
        console.log('[DemoPreview] SSE error, will reconnect...');
        if (mounted) {
          setState((s) => ({ ...s, isConnected: false }));
        }
        setTimeout(() => {
          if (mounted && eventSourceRef.current?.readyState === EventSource.CLOSED) {
            connectSSE(townId);
          }
        }, 3000);
      };
    };

    initDemo();

    return () => {
      mounted = false;
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
      }
    };
  }, []);

  // Redraw when citizens change
  useEffect(() => {
    if (state.citizens.length > 0) {
      drawCanvas(state.citizens);
    }
  }, [state.citizens]);

  // Set up canvas dimensions on mount
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const { scaledWidth, scaledHeight } = getCanvasDimensions();
    canvas.width = scaledWidth;
    canvas.height = scaledHeight;
  }, []);

  // Error state
  if (state.error) {
    return (
      <div className="bg-town-surface/50 rounded-2xl border border-town-accent/30 overflow-hidden">
        <div className="aspect-video flex items-center justify-center text-gray-500">
          <div className="text-center">
            <div className="text-6xl mb-4">🏘️</div>
            <p className="text-lg">Live demo preview</p>
            <p className="text-sm text-gray-600 mt-2">{state.error}</p>
          </div>
        </div>
      </div>
    );
  }

  const { width, height } = getCanvasDimensions();

  return (
    <div className="bg-town-surface/50 rounded-2xl border border-town-accent/30 overflow-hidden">
      {/* Canvas */}
      <div className="relative">
        <canvas
          ref={canvasRef}
          style={{ width: `${width}px`, height: `${height}px`, maxWidth: '100%' }}
          className="mx-auto block"
        />

        {/* Loading overlay */}
        {state.citizens.length === 0 && (
          <div className="absolute inset-0 flex items-center justify-center bg-town-bg/80">
            <div className="text-center">
              <div className="animate-pulse text-4xl mb-2">🏘️</div>
              <p className="text-sm text-gray-400">Loading town...</p>
            </div>
          </div>
        )}

        {/* Connection indicator */}
        <div className="absolute top-3 right-3 flex items-center gap-2">
          <div
            className={`w-2 h-2 rounded-full ${
              state.isConnected ? 'bg-green-500 animate-pulse' : 'bg-gray-500'
            }`}
          />
          <span className="text-xs text-gray-400">
            {state.isConnected ? 'LIVE' : 'Connecting...'}
          </span>
        </div>

        {/* Legend - show actual archetypes */}
        <div className="absolute bottom-3 left-3 flex flex-wrap gap-2 text-xs">
          {['Builder', 'Merchant', 'Healer', 'Scholar'].map((name) => (
            <div key={name} className="flex items-center gap-1">
              <div
                className="w-2 h-2 rounded-full"
                style={{ backgroundColor: ARCHETYPE_COLORS[name] }}
              />
              <span className="text-gray-400">{name}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Event Feed */}
      <div className="border-t border-town-accent/30 p-4 bg-town-bg/50">
        <div className="flex items-center justify-between mb-2">
          <span className="text-xs text-gray-500 font-medium">LIVE ACTIVITY</span>
          {state.townId && (
            <Link
              to={`/town/${state.townId}`}
              className="text-xs text-town-highlight hover:underline"
            >
              Open Full View →
            </Link>
          )}
        </div>
        <div className="space-y-1.5 min-h-[80px]">
          {state.events.length > 0 ? (
            state.events.map((event, i) => (
              <div
                key={`${event.tick}-${i}`}
                className={`text-sm transition-opacity ${i === 0 ? 'opacity-100' : 'opacity-60'}`}
              >
                <span className="text-gray-500 font-mono text-xs mr-2">
                  {event.tick}
                </span>
                <span className={getEventColor(event.operation)}>
                  {event.message}
                </span>
              </div>
            ))
          ) : (
            <p className="text-sm text-gray-600 italic">
              Waiting for activity...
            </p>
          )}
        </div>
      </div>
    </div>
  );
}

// =============================================================================
// Helpers
// =============================================================================

function getPhaseFromOperation(operation: string): 'IDLE' | 'WORKING' | 'SOCIALIZING' | 'REFLECTING' | 'RESTING' {
  if (['greet', 'gossip', 'trade'].includes(operation)) return 'SOCIALIZING';
  if (['work', 'craft', 'build'].includes(operation)) return 'WORKING';
  if (['reflect', 'journal', 'meditate'].includes(operation)) return 'REFLECTING';
  if (['rest', 'sleep'].includes(operation)) return 'RESTING';
  return 'IDLE';
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

export default DemoPreview;
