/**
 * CursorOverlay: Renders agent cursors on the canvas.
 *
 * CLI v7 Phase 4: Collaborative Canvas.
 *
 * Features:
 * - Animated cursors with state-based styling
 * - Smooth interpolation for cursor movement
 * - Personality-driven animations (breathing, pulsing)
 * - Focus path visualization
 *
 * Voice Anchor:
 * "Agents pretending to be there with their cursors moving,
 *  kinda following my cursor, kinda doing its own thing."
 *
 * Each cursor state has distinct visual treatment:
 * - FOLLOWING: Subtle, tracks user with lag
 * - EXPLORING: Active, moves independently
 * - WORKING: Pulsing at a specific node
 * - SUGGESTING: Gentle glow, attention-drawing
 * - WAITING: Soft breathing animation
 *
 * @see protocols/agentese/presence.py - CursorState enum
 */

import { useMemo } from 'react';
import type { AgentCursor, CursorState } from '@/hooks/usePresenceChannel';
import type { CanvasNode } from './AgentCanvas';

// =============================================================================
// Types
// =============================================================================

export interface CursorOverlayProps {
  /** Agent cursors to render */
  cursors: AgentCursor[];
  /** Canvas nodes (for position lookup) */
  nodes: CanvasNode[];
  /** Whether to show cursor labels */
  showLabels?: boolean;
  /** Whether to show activity text */
  showActivity?: boolean;
}

// =============================================================================
// Constants
// =============================================================================

/** State-based cursor colors */
const CURSOR_COLORS: Record<CursorState, string> = {
  following: '#22d3ee', // cyan-400
  exploring: '#3b82f6', // blue-500
  working: '#eab308', // yellow-500
  suggesting: '#22c55e', // green-500
  waiting: '#9ca3af', // gray-400
};

/** State-based cursor icons */
const CURSOR_ICONS: Record<CursorState, string> = {
  following: '○',
  exploring: '◎',
  working: '●',
  suggesting: '◐',
  waiting: '○',
};

/**
 * Animation timing constants.
 * Tuned for joy-inducing feel - not too fast, not too slow.
 *
 * Voice Anchor: "Daring, bold, creative, opinionated but not gaudy"
 */
const ANIMATION_TIMINGS = {
  /** Breathing animation for waiting state - calm, meditative */
  breathing: {
    duration: 4000, // 4s for a relaxed breath cycle
    minScale: 0.95,
    maxScale: 1.05,
    minOpacity: 0.6,
    maxOpacity: 1.0,
  },
  /** Following animation - subtle attention */
  following: {
    duration: 2000, // 2s pulse
    minScale: 0.98,
    maxScale: 1.02,
  },
  /** Exploring animation - energetic but not frantic */
  exploring: {
    duration: 1500, // 1.5s bounce cycle
    bounceHeight: 3, // pixels
  },
  /** Working animation - focused intensity */
  working: {
    duration: 800, // 0.8s - faster = more intensity
    pulseScale: 1.3,
  },
  /** Suggesting animation - gentle attention-drawing */
  suggesting: {
    duration: 2500, // 2.5s - slower = more inviting
    glowIntensity: 1.5,
  },
} as const;

// =============================================================================
// Individual Cursor Component
// =============================================================================

interface CursorMarkerProps {
  cursor: AgentCursor;
  position: { x: number; y: number };
  showLabel: boolean;
  showActivity: boolean;
}

function CursorMarker({ cursor, position, showLabel, showActivity }: CursorMarkerProps) {
  const color = CURSOR_COLORS[cursor.state];
  const icon = CURSOR_ICONS[cursor.state];

  // Get animation style based on cursor state
  const getAnimationStyle = (): React.CSSProperties => {
    const t = ANIMATION_TIMINGS;

    switch (cursor.state) {
      case 'waiting':
        return {
          animation: `cursor-breathing ${t.breathing.duration}ms ease-in-out infinite`,
        };
      case 'following':
        return {
          animation: `cursor-following ${t.following.duration}ms ease-in-out infinite`,
        };
      case 'exploring':
        return {
          animation: `cursor-exploring ${t.exploring.duration}ms ease-in-out infinite`,
        };
      case 'working':
        return {
          animation: `cursor-working ${t.working.duration}ms ease-in-out infinite`,
        };
      case 'suggesting':
        return {
          animation: `cursor-suggesting ${t.suggesting.duration}ms ease-in-out infinite`,
        };
      default:
        return {};
    }
  };

  return (
    <div
      className="absolute pointer-events-none select-none"
      style={{
        left: position.x,
        top: position.y,
        transform: 'translate(-50%, -50%)',
        transition: 'left 300ms ease-out, top 300ms ease-out',
        ...getAnimationStyle(),
      }}
    >
      {/* Cursor ring */}
      <div className="relative flex items-center justify-center" style={{ color }}>
        {/* Outer glow - intensity varies by state */}
        <div
          className="absolute rounded-full blur-sm transition-all duration-300"
          style={{
            backgroundColor: color,
            width: cursor.state === 'suggesting' ? 40 : cursor.state === 'working' ? 36 : 32,
            height: cursor.state === 'suggesting' ? 40 : cursor.state === 'working' ? 36 : 32,
            opacity: cursor.state === 'suggesting' ? 0.4 : cursor.state === 'working' ? 0.35 : 0.25,
          }}
        />

        {/* Inner ring */}
        <div
          className="relative w-6 h-6 rounded-full border-2 flex items-center justify-center text-xs font-bold transition-all duration-300"
          style={{
            borderColor: color,
            backgroundColor: `${color}20`,
            boxShadow:
              cursor.state === 'suggesting'
                ? `0 0 12px ${color}60`
                : cursor.state === 'working'
                  ? `0 0 8px ${color}40`
                  : 'none',
          }}
        >
          {icon}
        </div>

        {/* Focus line to node (if exploring/working/suggesting) */}
        {cursor.focus_path && cursor.state !== 'waiting' && cursor.state !== 'following' && (
          <div
            className="absolute w-0.5 h-4 -bottom-4 transition-opacity duration-300"
            style={{
              backgroundColor: color,
              opacity: cursor.state === 'working' ? 0.8 : 0.5,
            }}
          />
        )}
      </div>

      {/* Label and activity */}
      {(showLabel || showActivity) && (
        <div
          className="absolute top-full left-1/2 -translate-x-1/2 mt-2 whitespace-nowrap transition-opacity duration-300"
          style={{
            color,
            opacity: cursor.state === 'waiting' ? 0.7 : 1,
          }}
        >
          {showLabel && (
            <div className="text-[10px] font-medium text-center">{cursor.display_name}</div>
          )}
          {showActivity && cursor.activity && (
            <div className="text-[9px] opacity-70 text-center max-w-[100px] truncate">
              {cursor.activity}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

// =============================================================================
// Main Overlay Component
// =============================================================================

export function CursorOverlay({
  cursors,
  nodes,
  showLabels = true,
  showActivity = true,
}: CursorOverlayProps) {
  // Create node lookup map
  const nodeMap = useMemo(() => {
    const map = new Map<string, CanvasNode>();
    nodes.forEach((n) => map.set(n.path, n));
    return map;
  }, [nodes]);

  // Calculate cursor positions
  const cursorPositions = useMemo(() => {
    return cursors.map((cursor) => {
      let position = { x: 0, y: 0 };

      // If cursor has a focus path, position at that node
      if (cursor.focus_path) {
        const node = nodeMap.get(cursor.focus_path);
        if (node) {
          // Offset slightly based on cursor index to avoid overlap
          const offset = cursors.indexOf(cursor) * 15;
          position = {
            x: node.position.x + offset,
            y: node.position.y - 30 + offset,
          };
        }
      }

      return { cursor, position };
    });
  }, [cursors, nodeMap]);

  // Filter out cursors with no valid position
  const visibleCursors = cursorPositions.filter(
    ({ position }) => position.x !== 0 || position.y !== 0
  );

  if (visibleCursors.length === 0) {
    return null;
  }

  return (
    <>
      {/* Inject cursor animation keyframes - tuned for joy */}
      <style>{`
        /* Breathing: calm, meditative (for waiting state) */
        @keyframes cursor-breathing {
          0%, 100% {
            transform: translate(-50%, -50%) scale(0.95);
            opacity: 0.6;
          }
          50% {
            transform: translate(-50%, -50%) scale(1.05);
            opacity: 1;
          }
        }

        /* Following: subtle pulse (tracking user) */
        @keyframes cursor-following {
          0%, 100% {
            transform: translate(-50%, -50%) scale(0.98);
          }
          50% {
            transform: translate(-50%, -50%) scale(1.02);
          }
        }

        /* Exploring: energetic but not frantic */
        @keyframes cursor-exploring {
          0%, 100% {
            transform: translate(-50%, -50%) translateY(0);
          }
          25% {
            transform: translate(-50%, -50%) translateY(-3px);
          }
          75% {
            transform: translate(-50%, -50%) translateY(2px);
          }
        }

        /* Working: focused intensity */
        @keyframes cursor-working {
          0%, 100% {
            transform: translate(-50%, -50%) scale(1);
          }
          50% {
            transform: translate(-50%, -50%) scale(1.15);
          }
        }

        /* Suggesting: gentle attention-drawing glow */
        @keyframes cursor-suggesting {
          0%, 100% {
            transform: translate(-50%, -50%) scale(1);
            filter: brightness(1);
          }
          50% {
            transform: translate(-50%, -50%) scale(1.05);
            filter: brightness(1.3);
          }
        }
      `}</style>

      {/* Render cursors */}
      {visibleCursors.map(({ cursor, position }) => (
        <CursorMarker
          key={cursor.cursor_id}
          cursor={cursor}
          position={position}
          showLabel={showLabels}
          showActivity={showActivity}
        />
      ))}
    </>
  );
}

// =============================================================================
// Presence Status Badge
// =============================================================================

export interface PresenceStatusBadgeProps {
  /** Number of active cursors */
  cursorCount: number;
  /** Connection status */
  isConnected: boolean;
  /** Extra CSS classes */
  className?: string;
}

export function PresenceStatusBadge({
  cursorCount,
  isConnected,
  className = '',
}: PresenceStatusBadgeProps) {
  if (cursorCount === 0) {
    return (
      <div className={`flex items-center gap-1.5 text-xs text-gray-500 ${className}`}>
        <div className="w-2 h-2 rounded-full bg-gray-500" />
        <span>No agents active</span>
      </div>
    );
  }

  return (
    <div className={`flex items-center gap-1.5 text-xs ${className}`}>
      <div
        className={`w-2 h-2 rounded-full ${
          isConnected ? 'bg-green-500 animate-pulse' : 'bg-yellow-500'
        }`}
      />
      <span className="text-gray-300">
        {cursorCount} agent{cursorCount !== 1 ? 's' : ''} active
      </span>
    </div>
  );
}

// =============================================================================
// Cursor List (for sidebar display)
// =============================================================================

export interface CursorListProps {
  cursors: AgentCursor[];
  onCursorClick?: (cursor: AgentCursor) => void;
  className?: string;
}

export function CursorList({ cursors, onCursorClick, className = '' }: CursorListProps) {
  if (cursors.length === 0) {
    return <div className={`text-xs text-gray-500 ${className}`}>No agents currently active</div>;
  }

  return (
    <div className={`space-y-1 ${className}`}>
      {cursors.map((cursor) => (
        <div
          key={cursor.cursor_id}
          className="flex items-center gap-2 px-2 py-1 rounded hover:bg-gray-800/50 cursor-pointer transition-colors"
          onClick={() => onCursorClick?.(cursor)}
        >
          {/* State indicator */}
          <div
            className="w-2 h-2 rounded-full"
            style={{ backgroundColor: CURSOR_COLORS[cursor.state] }}
          />

          {/* Name and state */}
          <div className="flex-1 min-w-0">
            <div className="text-sm font-medium text-gray-200 truncate">{cursor.display_name}</div>
            <div className="text-[10px] text-gray-500 truncate">{formatCursorActivity(cursor)}</div>
          </div>

          {/* Focus path */}
          {cursor.focus_path && (
            <code className="text-[9px] text-gray-600 bg-gray-800 px-1 rounded max-w-[80px] truncate">
              {cursor.focus_path}
            </code>
          )}
        </div>
      ))}
    </div>
  );
}

// =============================================================================
// Helper Functions
// =============================================================================

function formatCursorActivity(cursor: AgentCursor): string {
  switch (cursor.state) {
    case 'following':
      return 'Following...';
    case 'exploring':
      return cursor.activity || 'Exploring...';
    case 'working':
      return cursor.activity || 'Working...';
    case 'suggesting':
      return cursor.activity || 'Has a suggestion';
    case 'waiting':
      return 'Ready';
    default:
      return cursor.activity || '';
  }
}

// =============================================================================
// Exports
// =============================================================================

export default CursorOverlay;
