/**
 * TokenFlowIndicator - Visual token flow on FishbowlCanvas edge
 *
 * Shows token particles flowing when bids are accepted.
 * Positioned on the edge of FishbowlCanvas, subtle but visible.
 *
 * Features:
 * - Particle stream using useFlowing hook
 * - Triggered by bid acceptance events
 * - LIVING_EARTH.honey colored particles
 * - Fade in/out for non-intrusive presence
 *
 * @see plans/crown-jewels-genesis-phase2-chunks3-5.md - Chunk 3: Token Economy Visualization
 * @see hooks/useFlowing.ts - Particle animation system
 */

import { useEffect, useCallback, useState, useRef } from 'react';
import { useFlowing, createCurvedPath, type Point } from '@/hooks/useFlowing';
import { LIVING_EARTH } from '@/constants/colors';
import { cn } from '@/lib/utils';

// =============================================================================
// Types
// =============================================================================

export interface TokenFlowEvent {
  /** Unique event ID */
  id: string;
  /** Amount of tokens */
  amount: number;
  /** Flow direction: 'in' to artisan, 'out' from spectator */
  direction: 'in' | 'out';
  /** Timestamp */
  timestamp: string;
}

export interface TokenFlowIndicatorProps {
  /** Token flow events to visualize */
  events: TokenFlowEvent[];
  /** Position on the canvas edge */
  position?: 'top' | 'right' | 'bottom' | 'left';
  /** Canvas dimensions for positioning */
  canvasWidth?: number;
  canvasHeight?: number;
  /** Whether flow animation is enabled */
  enabled?: boolean;
  /** Optional class name */
  className?: string;
}

// =============================================================================
// Constants
// =============================================================================

const FLOW_DURATION = 1500; // ms per flow
const PARTICLE_COUNT = 6;
const PARTICLE_SIZE = 3;

// Edge positions as percentages
const EDGE_POSITIONS: Record<string, { start: Point; end: Point }> = {
  top: {
    start: { x: 20, y: 5 },
    end: { x: 80, y: 5 },
  },
  right: {
    start: { x: 95, y: 20 },
    end: { x: 95, y: 80 },
  },
  bottom: {
    start: { x: 80, y: 95 },
    end: { x: 20, y: 95 },
  },
  left: {
    start: { x: 5, y: 80 },
    end: { x: 5, y: 20 },
  },
};

// =============================================================================
// Component
// =============================================================================

export function TokenFlowIndicator({
  events,
  position = 'bottom',
  canvasWidth = 400,
  canvasHeight = 300,
  enabled = true,
  className,
}: TokenFlowIndicatorProps) {
  // Track which events we've shown
  const shownEventsRef = useRef<Set<string>>(new Set());
  const [activeFlow, setActiveFlow] = useState<TokenFlowEvent | null>(null);

  // Convert percentage positions to pixels
  const edgePos = EDGE_POSITIONS[position];
  const startPoint: Point = {
    x: (edgePos.start.x / 100) * canvasWidth,
    y: (edgePos.start.y / 100) * canvasHeight,
  };
  const endPoint: Point = {
    x: (edgePos.end.x / 100) * canvasWidth,
    y: (edgePos.end.y / 100) * canvasHeight,
  };

  // Create curved path along edge
  const pathPoints = createCurvedPath(startPoint, endPoint, 0.15);

  // useFlowing hook for particle animation
  const { particles, isFlowing, start, stop, pathD } = useFlowing(pathPoints, {
    enabled: enabled && !!activeFlow,
    duration: FLOW_DURATION,
    particleCount: PARTICLE_COUNT,
    particleSize: PARTICLE_SIZE,
    direction: activeFlow?.direction === 'in' ? 'forward' : 'reverse',
    loop: false,
    onParticleComplete: useCallback(() => {
      // Clear active flow when all particles complete
      setActiveFlow(null);
    }, []),
  });

  // Watch for new events
  useEffect(() => {
    if (events.length === 0 || !enabled) return;

    // Find first unshown event
    const newEvent = events.find((e) => !shownEventsRef.current.has(e.id));

    if (newEvent && !activeFlow) {
      shownEventsRef.current.add(newEvent.id);
      setActiveFlow(newEvent);
    }
  }, [events, enabled, activeFlow]);

  // Start flow when active event changes
  useEffect(() => {
    if (activeFlow && enabled) {
      start();
    }
  }, [activeFlow, enabled, start]);

  // Clear old events from memory (prevent memory leak)
  useEffect(() => {
    const maxSize = 100;
    if (shownEventsRef.current.size > maxSize) {
      const eventsArray = Array.from(shownEventsRef.current);
      shownEventsRef.current = new Set(eventsArray.slice(-50));
    }
  }, [events.length]);

  // Get particle color based on flow direction
  const particleColor = activeFlow?.direction === 'in'
    ? LIVING_EARTH.honey
    : LIVING_EARTH.amber;

  // Don't render if disabled or no active flow
  if (!enabled) return null;

  return (
    <svg
      className={cn(
        'absolute inset-0 pointer-events-none',
        'transition-opacity duration-300',
        isFlowing ? 'opacity-100' : 'opacity-0',
        className
      )}
      viewBox={`0 0 ${canvasWidth} ${canvasHeight}`}
      preserveAspectRatio="none"
    >
      {/* Path (subtle, mostly invisible) */}
      <path
        d={pathD}
        fill="none"
        stroke={`${particleColor}20`}
        strokeWidth={1}
        strokeLinecap="round"
      />

      {/* Particles */}
      {particles.map((particle) => (
        <g key={particle.id}>
          {/* Glow */}
          <circle
            cx={particle.x}
            cy={particle.y}
            r={particle.size * 2}
            fill={`${particleColor}40`}
            opacity={particle.opacity * 0.5}
          />
          {/* Core */}
          <circle
            cx={particle.x}
            cy={particle.y}
            r={particle.size}
            fill={particleColor}
            opacity={particle.opacity}
          />
        </g>
      ))}

      {/* Amount label (appears mid-flow) */}
      {activeFlow && isFlowing && (
        <g transform={`translate(${(startPoint.x + endPoint.x) / 2}, ${(startPoint.y + endPoint.y) / 2 - 15})`}>
          <rect
            x={-20}
            y={-10}
            width={40}
            height={20}
            rx={4}
            fill="white"
            fillOpacity={0.9}
            stroke={particleColor}
            strokeWidth={1}
          />
          <text
            textAnchor="middle"
            dominantBaseline="middle"
            fontSize={11}
            fontWeight={600}
            fill={LIVING_EARTH.bark}
          >
            {activeFlow.direction === 'in' ? '+' : '-'}{activeFlow.amount}
          </text>
        </g>
      )}
    </svg>
  );
}

// =============================================================================
// Exports
// =============================================================================

export default TokenFlowIndicator;
