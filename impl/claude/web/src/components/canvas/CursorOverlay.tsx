/**
 * CursorOverlay: Renders agent cursors on the canvas with spring physics.
 *
 * CLI v7 Phase 5: Collaborative Canvas.
 *
 * Features:
 * - Spring-physics cursor interpolation (not CSS transition)
 * - Behavior-driven animation (FOLLOWER snappy, EXPLORER loose)
 * - Circadian tempo modulation (night = slower, contemplative)
 * - State-based styling (working pulses, suggesting glows)
 *
 * Voice Anchor:
 * "Agents pretending to be there with their cursors moving,
 *  kinda following my cursor, kinda doing its own thing."
 *
 * The magic: Each CursorBehavior has distinct spring feel.
 * This makes cursors feel alive, not mechanical.
 *
 * @see services/conductor/behaviors.py - CursorBehavior enum
 * @see services/conductor/presence.py - CursorState, CircadianPhase
 */

import { useMemo } from 'react';
import type { AgentCursor, CursorState } from '@/hooks/usePresenceChannel';
import type { CanvasNode } from './AgentCanvas';
import { AnimatedCursor } from './AnimatedCursor';

// =============================================================================
// Types
// =============================================================================

export interface CursorOverlayProps {
  /** Agent cursors to render */
  cursors: AgentCursor[];
  /** Canvas nodes (for position lookup) */
  nodes: CanvasNode[];
  /** Node positions (from useCanvasLayout) */
  positions?: Map<string, { x: number; y: number }>;
  /** Whether to show cursor labels */
  showLabels?: boolean;
  /** Whether to show activity text */
  showActivity?: boolean;
  /** Circadian tempo modifier (0.0-1.0 for animation speed) */
  circadianTempo?: number;
}

// =============================================================================
// Constants (used by sidebar components)
// =============================================================================

/** State-based cursor colors */
const CURSOR_COLORS: Record<CursorState, string> = {
  following: '#22d3ee', // cyan-400
  exploring: '#3b82f6', // blue-500
  working: '#eab308', // yellow-500
  suggesting: '#22c55e', // green-500
  waiting: '#9ca3af', // gray-400
};

// =============================================================================
// Main Overlay Component
// =============================================================================

export function CursorOverlay({
  cursors,
  nodes,
  positions,
  showLabels = true,
  showActivity = true,
  circadianTempo = 1.0,
}: CursorOverlayProps) {
  // Create node lookup map (by path)
  const nodeMap = useMemo(() => {
    const map = new Map<string, CanvasNode>();
    nodes.forEach((n) => map.set(n.path, n));
    return map;
  }, [nodes]);

  // Calculate cursor positions using layout positions if available
  const cursorPositions = useMemo(() => {
    return cursors.map((cursor, index) => {
      let position = { x: 0, y: 0 };

      // If cursor has a focus path, position at that node
      if (cursor.focus_path) {
        const node = nodeMap.get(cursor.focus_path);
        if (node) {
          // Try to get position from layout (dynamic) or fall back to node.position (static)
          const layoutPos = positions?.get(node.id);
          const basePos = layoutPos || node.position;

          // Offset slightly based on cursor index to avoid overlap
          const offset = index * 15;
          position = {
            x: basePos.x + offset,
            y: basePos.y - 30 + offset,
          };
        }
      }

      return { cursor, position };
    });
  }, [cursors, nodeMap, positions]);

  // Filter out cursors with no valid position
  const visibleCursors = cursorPositions.filter(
    ({ position }) => position.x !== 0 || position.y !== 0
  );

  if (visibleCursors.length === 0) {
    return null;
  }

  // Render using AnimatedCursor for spring physics
  return (
    <>
      {visibleCursors.map(({ cursor, position }) => (
        <AnimatedCursor
          key={cursor.cursor_id}
          cursor={cursor}
          targetPosition={position}
          circadianTempo={circadianTempo}
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
