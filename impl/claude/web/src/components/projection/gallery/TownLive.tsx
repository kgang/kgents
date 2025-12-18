/**
 * TownLive: Live Agent Town streaming visualization.
 *
 * Flagship pilot showing polynomial agents in motion - real-time
 * citizen updates via SSE, phase indicators, and event feeds.
 *
 * @see plans/gallery-pilots-top3.md
 * @see impl/claude/web/src/hooks/useTownStreamWidget.ts
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import { Play, Pause, Lightbulb, Wifi, WifiOff, Users } from 'lucide-react';

// =============================================================================
// Types
// =============================================================================

interface Citizen {
  id: string;
  name: string;
  char: string;
  phase: string;
  x: number;
  y: number;
  archetype: string;
}

interface TownEvent {
  tick: number;
  operation: string;
  message: string;
}

type TownPhase = 'MORNING' | 'AFTERNOON' | 'EVENING' | 'NIGHT';

export interface TownLiveProps {
  /** Town ID to stream */
  townId?: string;
  /** Initial citizens (for demo mode) */
  citizens?: Citizen[];
  /** Initial events (for demo mode) */
  events?: TownEvent[];
  /** Initial day */
  day?: number;
  /** Initial phase */
  phase?: TownPhase;
  /** Compact mode for gallery cards */
  compact?: boolean;
  /** Enable real SSE streaming */
  enableStreaming?: boolean;
}

// =============================================================================
// Constants
// =============================================================================

const PHASE_COLORS: Record<TownPhase, string> = {
  MORNING: '#f59e0b',
  AFTERNOON: '#f97316',
  EVENING: '#8b5cf6',
  NIGHT: '#3b82f6',
};

const CITIZEN_COLORS: Record<string, string> = {
  idle: '#64748b',
  active: '#22c55e',
  socializing: '#ec4899',
  working: '#f59e0b',
  reflecting: '#8b5cf6',
  resting: '#3b82f6',
};

// Demo citizens
const DEMO_CITIZENS: Citizen[] = [
  { id: 'socrates', name: 'Socrates', char: 'K', phase: 'active', x: 2, y: 2, archetype: 'Scholar' },
  { id: 'hypatia', name: 'Hypatia', char: 'H', phase: 'working', x: 5, y: 3, archetype: 'Builder' },
  { id: 'marcus', name: 'Marcus', char: 'M', phase: 'idle', x: 3, y: 5, archetype: 'Watcher' },
  { id: 'ada', name: 'Ada', char: 'A', phase: 'reflecting', x: 6, y: 4, archetype: 'Builder' },
  { id: 'leonardo', name: 'Leonardo', char: 'L', phase: 'resting', x: 4, y: 6, archetype: 'Healer' },
];

const DEMO_EVENTS: TownEvent[] = [
  { tick: 42, operation: 'greet', message: 'Socrates greeted Marcus' },
  { tick: 41, operation: 'work', message: 'Hypatia started building' },
  { tick: 40, operation: 'rest', message: 'Leonardo began rest (Right to Rest)' },
  { tick: 39, operation: 'reflect', message: 'Ada finished task, reflecting' },
];

// =============================================================================
// Component
// =============================================================================

export function TownLive({
  townId = 'demo',
  citizens: initialCitizens,
  events: initialEvents,
  day: initialDay = 1,
  phase: initialPhase = 'MORNING',
  compact = false,
  enableStreaming = false,
}: TownLiveProps) {
  // State
  const [citizens, setCitizens] = useState<Citizen[]>(initialCitizens ?? DEMO_CITIZENS);
  const [events, setEvents] = useState<TownEvent[]>(initialEvents ?? DEMO_EVENTS);
  const [day, setDay] = useState(initialDay);
  const [phase, setPhase] = useState<TownPhase>(initialPhase);
  const [isPlaying, setIsPlaying] = useState(false);
  const [isConnected, setIsConnected] = useState(false);
  const [speed, setSpeed] = useState(1);

  // Demo tick ref
  const tickRef = useRef<NodeJS.Timeout | null>(null);
  const tickCountRef = useRef(42);

  // Demo simulation (when not streaming)
  const runDemoTick = useCallback(() => {
    tickCountRef.current += 1;
    const tick = tickCountRef.current;

    // Randomly update a citizen phase
    setCitizens((prev) => {
      const idx = Math.floor(Math.random() * prev.length);
      const phases = ['idle', 'active', 'socializing', 'working', 'reflecting', 'resting'];
      const newPhase = phases[Math.floor(Math.random() * phases.length)];
      return prev.map((c, i) => (i === idx ? { ...c, phase: newPhase } : c));
    });

    // Add a random event
    const operations = ['greet', 'work', 'reflect', 'rest', 'trade'];
    const op = operations[Math.floor(Math.random() * operations.length)];
    const citizenNames = citizens.map((c) => c.name);
    const actor = citizenNames[Math.floor(Math.random() * citizenNames.length)];

    const messages: Record<string, string> = {
      greet: `${actor} greeted a neighbor`,
      work: `${actor} started working on a task`,
      reflect: `${actor} began reflecting`,
      rest: `${actor} is resting (Right to Rest)`,
      trade: `${actor} made a trade`,
    };

    setEvents((prev) => [{ tick, operation: op, message: messages[op] }, ...prev.slice(0, 9)]);

    // Advance phase every 10 ticks
    if (tick % 10 === 0) {
      const phaseOrder: TownPhase[] = ['MORNING', 'AFTERNOON', 'EVENING', 'NIGHT'];
      setPhase((prev) => {
        const idx = phaseOrder.indexOf(prev);
        if (idx === phaseOrder.length - 1) {
          setDay((d) => d + 1);
          return 'MORNING';
        }
        return phaseOrder[idx + 1];
      });
    }
  }, [citizens]);

  // Toggle play/pause
  const handleTogglePlay = useCallback(() => {
    setIsPlaying((prev) => !prev);
  }, []);

  // Effect: Demo simulation
  useEffect(() => {
    if (isPlaying && !enableStreaming) {
      tickRef.current = setInterval(runDemoTick, 1000 / speed);
      setIsConnected(true);
    } else {
      if (tickRef.current) {
        clearInterval(tickRef.current);
        tickRef.current = null;
      }
      if (!isPlaying) {
        setIsConnected(false);
      }
    }

    return () => {
      if (tickRef.current) {
        clearInterval(tickRef.current);
      }
    };
  }, [isPlaying, enableStreaming, speed, runDemoTick]);

  const phaseColor = PHASE_COLORS[phase];

  // ==========================================================================
  // Compact Mode
  // ==========================================================================

  if (compact) {
    return (
      <div className="space-y-3">
        {/* Citizen mini-grid */}
        <div className="flex gap-1.5 flex-wrap justify-center">
          {citizens.slice(0, 5).map((c) => {
            const color = CITIZEN_COLORS[c.phase] || '#64748b';
            return (
              <div
                key={c.id}
                className="w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold"
                style={{
                  background: `${color}20`,
                  border: `1px solid ${color}60`,
                  color,
                  textShadow: `0 0 8px ${color}60`,
                }}
                title={`${c.name} (${c.phase})`}
              >
                {c.char}
              </div>
            );
          })}
        </div>

        {/* Phase indicator */}
        <div className="flex justify-center items-center gap-2 text-xs">
          <span className="text-gray-500">Day {day}</span>
          <span
            className="px-2 py-0.5 rounded-full font-medium"
            style={{ background: `${phaseColor}20`, color: phaseColor }}
          >
            {phase}
          </span>
          {isConnected && (
            <span className="flex items-center gap-1 text-green-500">
              <span className="w-1.5 h-1.5 rounded-full bg-green-500 animate-pulse" />
              Live
            </span>
          )}
        </div>
      </div>
    );
  }

  // ==========================================================================
  // Full Mode
  // ==========================================================================

  return (
    <div className="bg-slate-900 rounded-xl p-5 space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-slate-800 pb-4">
        <div className="flex items-center gap-3">
          <Users className="w-5 h-5 text-violet-400" />
          <h3 className="text-lg font-semibold text-white">Town: {townId}</h3>
          <span className="text-sm text-gray-500">Day {day}</span>
          <span
            className="px-2.5 py-1 rounded-full text-xs font-semibold"
            style={{ background: `${phaseColor}20`, color: phaseColor }}
          >
            {phase}
          </span>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={handleTogglePlay}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium text-sm transition-colors ${
              isPlaying
                ? 'bg-amber-500 hover:bg-amber-400 text-black'
                : 'bg-green-600 hover:bg-green-500 text-white'
            }`}
          >
            {isPlaying ? (
              <>
                <Pause className="w-4 h-4" />
                Pause
              </>
            ) : (
              <>
                <Play className="w-4 h-4" />
                Play
              </>
            )}
          </button>
          <select
            value={speed}
            onChange={(e) => setSpeed(Number(e.target.value))}
            className="bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-gray-200"
          >
            <option value={0.5}>0.5x</option>
            <option value={1}>1x</option>
            <option value={2}>2x</option>
            <option value={4}>4x</option>
          </select>
        </div>
      </div>

      {/* Citizens Grid */}
      <div className="flex gap-2 flex-wrap">
        {citizens.map((c) => {
          const color = CITIZEN_COLORS[c.phase] || '#64748b';
          return (
            <div
              key={c.id}
              className="flex items-center gap-2 px-3 py-2 rounded-lg min-w-[120px] transition-all duration-300"
              style={{
                background: `linear-gradient(135deg, ${color}15, ${color}05)`,
                border: `1px solid ${color}40`,
              }}
            >
              <span
                className="text-xl"
                style={{ color, textShadow: `0 0 8px ${color}60` }}
              >
                {c.char}
              </span>
              <div>
                <div className="font-semibold text-sm text-gray-100">{c.name}</div>
                <div
                  className="text-[10px] uppercase font-medium"
                  style={{ color }}
                >
                  {c.phase}
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Event Feed */}
      <div className="bg-slate-800 rounded-lg p-4">
        <div className="text-xs text-gray-500 uppercase tracking-wider mb-3">
          Event Feed
        </div>
        <div className="space-y-1 max-h-32 overflow-y-auto">
          {events.map((e, idx) => (
            <div key={idx} className="text-sm">
              <span className="text-gray-600 font-mono text-xs">[{e.tick}]</span>{' '}
              <span className="text-gray-300">{e.message}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Teaching Callout */}
      <div className="bg-gradient-to-r from-green-500/20 to-blue-500/20 border-l-4 border-green-500 rounded-r-lg p-4">
        <div className="flex items-center gap-2 text-green-400 text-xs uppercase tracking-wider mb-1">
          <Lightbulb className="w-3 h-3" />
          Teaching
        </div>
        <p className="text-sm text-gray-200">
          Polynomial agents in motion - watch state machines interact in real-time
        </p>
      </div>

      {/* SSE Indicator */}
      <div className="flex items-center gap-2 pt-2 border-t border-slate-800">
        {isConnected ? (
          <>
            <Wifi className="w-4 h-4 text-green-500" />
            <span className="text-xs text-gray-500">
              {enableStreaming ? `Streaming from /api/town/${townId}/stream` : 'Demo simulation active'}
            </span>
            <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
          </>
        ) : (
          <>
            <WifiOff className="w-4 h-4 text-gray-600" />
            <span className="text-xs text-gray-600">Not connected - press Play to start</span>
          </>
        )}
      </div>
    </div>
  );
}

export default TownLive;
