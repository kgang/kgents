/**
 * PresenceBadge - Agent presence indicator for Portal view.
 *
 * Phase 4C: Agent Collaboration Layer.
 *
 * Shows agent cursors inline with portal nodes:
 * - Who's exploring this path
 * - What they're doing (state emoji)
 * - Brief activity description
 *
 * Uses usePresenceChannel hook for real-time updates.
 *
 * @see spec/protocols/context-perception.md §6
 */

import { memo, useMemo } from 'react';
import {
  usePresenceChannel,
  getCursorEmoji,
  getCursorColor,
  formatCursorStatus,
  type AgentCursor,
  type CursorState,
} from '@/hooks/usePresenceChannel';
import { Breathe } from '@/components/joy';

// =============================================================================
// Types
// =============================================================================

export interface PresenceBadgeProps {
  /** Optional path to filter cursors focusing on this path */
  focusPath?: string;
  /** Show all cursors regardless of focus path */
  showAll?: boolean;
  /** Compact mode (just emoji) */
  compact?: boolean;
  /** Custom class name */
  className?: string;
}

export interface SingleCursorBadgeProps {
  cursor: AgentCursor;
  compact?: boolean;
  className?: string;
}

// =============================================================================
// Animation Speed by State
// =============================================================================

function getAnimationSpeed(state: CursorState): 'slow' | 'normal' | 'fast' {
  switch (state) {
    case 'following':
      return 'fast';
    case 'exploring':
      return 'normal'; // Breathe uses 'normal' not 'medium'
    case 'working':
      return 'fast';
    case 'suggesting':
      return 'slow';
    case 'waiting':
      return 'slow';
    default:
      return 'normal';
  }
}

function getIntensity(state: CursorState): number {
  switch (state) {
    case 'following':
      return 0.3;
    case 'exploring':
      return 0.4;
    case 'working':
      return 0.5;
    case 'suggesting':
      return 0.2;
    case 'waiting':
      return 0.1;
    default:
      return 0.2;
  }
}

// =============================================================================
// Single Cursor Badge
// =============================================================================

export const SingleCursorBadge = memo(function SingleCursorBadge({
  cursor,
  compact = false,
  className = '',
}: SingleCursorBadgeProps) {
  const emoji = getCursorEmoji(cursor.state);
  const color = getCursorColor(cursor.state);
  const intensity = getIntensity(cursor.state);
  const speed = getAnimationSpeed(cursor.state);

  // Tailwind color class from string
  const colorClass = `text-${color}-400`;

  if (compact) {
    return (
      <Breathe intensity={intensity} speed={speed}>
        <span
          className={`inline-flex items-center ${className}`}
          title={formatCursorStatus(cursor)}
        >
          <span className="text-sm">{emoji}</span>
        </span>
      </Breathe>
    );
  }

  return (
    <Breathe intensity={intensity} speed={speed}>
      <span
        className={`
          inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full
          bg-gray-800/60 border border-gray-700/50
          ${className}
        `}
        title={formatCursorStatus(cursor)}
      >
        <span className="text-sm">{emoji}</span>
        <span className={`text-xs font-medium ${colorClass}`}>
          {cursor.display_name}
        </span>
        {cursor.activity && (
          <span className="text-xs text-gray-400 truncate max-w-[100px]">
            {cursor.activity}
          </span>
        )}
      </span>
    </Breathe>
  );
});

// =============================================================================
// Main Component
// =============================================================================

export const PresenceBadge = memo(function PresenceBadge({
  focusPath,
  showAll = false,
  compact = false,
  className = '',
}: PresenceBadgeProps) {
  const { cursorList, isConnected } = usePresenceChannel({
    autoConnect: true,
  });

  // Filter cursors by focus path if provided
  const relevantCursors = useMemo(() => {
    if (showAll || !focusPath) {
      return cursorList;
    }
    return cursorList.filter(
      (cursor) =>
        cursor.focus_path === focusPath ||
        cursor.focus_path?.startsWith(focusPath + '.') ||
        focusPath.startsWith(cursor.focus_path + '.')
    );
  }, [cursorList, focusPath, showAll]);

  // Don't render if not connected or no relevant cursors
  if (!isConnected || relevantCursors.length === 0) {
    return null;
  }

  return (
    <div className={`flex items-center gap-2 ${className}`}>
      {relevantCursors.map((cursor) => (
        <SingleCursorBadge
          key={cursor.agent_id}
          cursor={cursor}
          compact={compact}
        />
      ))}
    </div>
  );
});

// =============================================================================
// Presence Footer
// =============================================================================

export interface PresenceFooterProps {
  className?: string;
}

/**
 * Footer showing all active agent presences.
 *
 * Displayed at the bottom of the Portal view.
 */
export const PresenceFooter = memo(function PresenceFooter({
  className = '',
}: PresenceFooterProps) {
  const { cursorList, isConnected, status } = usePresenceChannel({
    autoConnect: true,
  });

  if (!isConnected && status === 'connecting') {
    return (
      <div className={`text-xs text-gray-500 ${className}`}>
        Connecting to presence channel...
      </div>
    );
  }

  if (cursorList.length === 0) {
    return null;
  }

  return (
    <div className={`flex flex-col gap-2 ${className}`}>
      <div className="text-xs text-gray-500 border-t border-gray-800 pt-2">
        Active Agents
      </div>
      <div className="flex flex-wrap gap-2">
        {cursorList.map((cursor) => (
          <SingleCursorBadge key={cursor.agent_id} cursor={cursor} />
        ))}
      </div>
    </div>
  );
});

// =============================================================================
// Inline Presence Indicator
// =============================================================================

export interface InlinePresenceProps {
  /** Path this indicator is attached to */
  path: string;
  /** Custom class name */
  className?: string;
}

/**
 * Small inline indicator showing cursors at a specific path.
 *
 * Used next to portal tree nodes.
 */
export const InlinePresence = memo(function InlinePresence({
  path,
  className = '',
}: InlinePresenceProps) {
  const { cursorList } = usePresenceChannel({
    autoConnect: true,
  });

  // Find cursors at this exact path
  const atPath = useMemo(
    () => cursorList.filter((c) => c.focus_path === path),
    [cursorList, path]
  );

  if (atPath.length === 0) {
    return null;
  }

  return (
    <span className={`inline-flex gap-0.5 ${className}`}>
      {atPath.map((cursor) => (
        <span
          key={cursor.agent_id}
          className="text-xs"
          title={formatCursorStatus(cursor)}
        >
          {getCursorEmoji(cursor.state)}
        </span>
      ))}
    </span>
  );
});

// =============================================================================
// Exports
// =============================================================================

export default PresenceBadge;
