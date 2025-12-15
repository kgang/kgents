import { useEffect, useState, useRef, useCallback } from 'react';
import { Link } from 'react-router-dom';
import { townApi } from '@/api/client';
import { REGION_GRID_POSITIONS, gridToScreen } from '@/lib/regionGrid';
import type { CitizenSummary, TownEvent } from '@/api/types';

// =============================================================================
// Constants
// =============================================================================

const GRID_SIZE = 20;
const CELL_SIZE = 16; // Smaller for preview
const CANVAS_WIDTH = 480;
const CANVAS_HEIGHT = 320;

// Archetype colors
const ARCHETYPE_COLORS: Record<string, string> = {
  Builder: '#3b82f6',
  Trader: '#f59e0b',
  Healer: '#22c55e',
  Scholar: '#8b5cf6',
  Watcher: '#6b7280',
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
  const animationFrameRef = useRef<number>(0);

  const [state, setState] = useState<DemoState>({
    townId: null,
    citizens: [],
    events: [],
    isConnected: false,
    error: null,
  });

  // Calculate citizen screen positions
  const getCitizenPositions = useCallback(() => {
    const offsetX = CANVAS_WIDTH / 2;
    const offsetY = CANVAS_HEIGHT / 4;

    // Group citizens by region
    const byRegion = new Map<string, CitizenSummary[]>();
    state.citizens.forEach((c) => {
      const list = byRegion.get(c.region) || [];
      list.push(c);
      byRegion.set(c.region, list);
    });

    const positions: Array<{ citizen: CitizenSummary; x: number; y: number }> = [];

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
        positions.push({ citizen, x: screen.x, y: screen.y });
      });
    });

    return positions;
  }, [state.citizens]);

  // Draw the canvas
  const draw = useCallback(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Clear
    ctx.fillStyle = '#1a1a2e';
    ctx.fillRect(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT);

    const offsetX = CANVAS_WIDTH / 2;
    const offsetY = CANVAS_HEIGHT / 4;

    // Draw subtle grid
    ctx.strokeStyle = 'rgba(22, 33, 62, 0.3)';
    ctx.lineWidth = 1;

    for (let i = 0; i <= GRID_SIZE; i += 2) {
      // Horizontal lines
      const startH = gridToScreen(i, 0, CELL_SIZE, offsetX, offsetY);
      const endH = gridToScreen(i, GRID_SIZE, CELL_SIZE, offsetX, offsetY);
      ctx.beginPath();
      ctx.moveTo(startH.x, startH.y);
      ctx.lineTo(endH.x, endH.y);
      ctx.stroke();

      // Vertical lines
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

    // Draw citizens
    const positions = getCitizenPositions();
    positions.forEach(({ citizen, x, y }) => {
      const color = ARCHETYPE_COLORS[citizen.archetype] || '#6b7280';

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

    animationFrameRef.current = requestAnimationFrame(draw);
  }, [getCitizenPositions]);

  // Initialize demo town
  useEffect(() => {
    let mounted = true;

    const initDemo = async () => {
      try {
        // Create a demo town (or use existing)
        const response = await townApi.create({
          name: 'demo-preview',
          phase: 3, // Smaller town (10 citizens)
          enable_dialogue: false,
        });

        if (!mounted) return;

        const townId = response.data.id;
        setState((s) => ({ ...s, townId }));

        // Load citizens
        const citizensRes = await townApi.getCitizens(townId);
        if (!mounted) return;

        setState((s) => ({
          ...s,
          citizens: citizensRes.data.citizens,
        }));

        // Connect to SSE
        connectSSE(townId);
      } catch (err) {
        console.error('Failed to init demo:', err);
        if (mounted) {
          setState((s) => ({ ...s, error: 'Demo unavailable' }));
        }
      }
    };

    const connectSSE = (townId: string) => {
      const url = `/v1/town/${townId}/live?speed=2&phases=100`;
      const eventSource = new EventSource(url);
      eventSourceRef.current = eventSource;

      eventSource.onopen = () => {
        setState((s) => ({ ...s, isConnected: true }));
      };

      eventSource.addEventListener('live.event', (e) => {
        const event: TownEvent = JSON.parse(e.data);
        setState((s) => ({
          ...s,
          events: [event, ...s.events.slice(0, 4)], // Keep last 5 events
        }));

        // Update citizen positions based on event
        if (event.participants && event.participants.length > 0) {
          setState((s) => {
            const updatedCitizens = s.citizens.map((c) => {
              if (event.participants.includes(c.name)) {
                return { ...c, phase: getPhaseFromOperation(event.operation) };
              }
              return c;
            });
            return { ...s, citizens: updatedCitizens };
          });
        }
      });

      eventSource.onerror = () => {
        setState((s) => ({ ...s, isConnected: false }));
        // Reconnect after 3 seconds
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
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
    };
  }, []);

  // Start drawing when citizens load
  useEffect(() => {
    if (state.citizens.length > 0) {
      draw();
    }
    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
    };
  }, [state.citizens.length, draw]);

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

  return (
    <div className="bg-town-surface/50 rounded-2xl border border-town-accent/30 overflow-hidden">
      {/* Canvas */}
      <div className="relative">
        <canvas
          ref={canvasRef}
          width={CANVAS_WIDTH}
          height={CANVAS_HEIGHT}
          className="w-full"
          style={{ aspectRatio: `${CANVAS_WIDTH}/${CANVAS_HEIGHT}` }}
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

        {/* Legend */}
        <div className="absolute bottom-3 left-3 flex gap-3 text-xs">
          {Object.entries(ARCHETYPE_COLORS).slice(0, 4).map(([name, color]) => (
            <div key={name} className="flex items-center gap-1">
              <div
                className="w-3 h-3 rounded-full"
                style={{ backgroundColor: color }}
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
