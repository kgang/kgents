/**
 * SpectatorOverlay - Opt-in cursor visibility for spectators
 *
 * Shows other spectators' cursors on the canvas when enabled.
 * Colors can be derived from citizen eigenvectors for Town integration.
 *
 * Features:
 * - Real-time cursor position rendering
 * - Optional eigenvector-based coloring (links to Town citizens)
 * - Stale cursor cleanup
 * - Performance-optimized rendering
 *
 * @see plans/crown-jewels-genesis-phase2.md - Week 3: SpectatorOverlay
 * @see agents/town/citizen.py - Eigenvector personality model
 */

import { useMemo, useCallback } from 'react';
import { LIVING_EARTH } from '@/constants/colors';
import { cn } from '@/lib/utils';

// =============================================================================
// Types
// =============================================================================

export interface SpectatorCursor {
  /** Unique spectator ID */
  id: string;
  /** Normalized position (0-1 for both x and y) */
  position: { x: number; y: number };
  /** Optional Town citizen ID for eigenvector coloring */
  citizenId?: string;
  /** Optional eigenvector for personality-based coloring */
  eigenvector?: number[];
  /** Timestamp of last update (ms) */
  lastUpdate: number;
  /** Optional display name */
  name?: string;
}

export interface SpectatorOverlayProps {
  /** List of spectator cursors to display */
  spectators: SpectatorCursor[];
  /** Whether to show cursors */
  showCursors: boolean;
  /** Color cursors based on citizen eigenvector */
  eigenvectorColors?: boolean;
  /** Max age for cursors before fading (ms, default 5000) */
  maxAge?: number;
  /** Show spectator names on hover */
  showNames?: boolean;
  /** Additional class name */
  className?: string;
}

// =============================================================================
// Constants
// =============================================================================

const DEFAULT_MAX_AGE = 5000; // 5 seconds
const CURSOR_SIZE = 12;
const NAME_OFFSET = 16;

// Default cursor colors (warm amber palette)
const DEFAULT_CURSOR_COLORS = [
  LIVING_EARTH.amber,
  LIVING_EARTH.honey,
  LIVING_EARTH.copper,
  LIVING_EARTH.lantern,
  LIVING_EARTH.sage,
] as const;

// =============================================================================
// Helper: Eigenvector to Color
// =============================================================================

/**
 * Convert a citizen eigenvector to an HSL color.
 * Maps the first 3 eigenvector components to hue, saturation, lightness.
 *
 * @param eigenvector Array of normalized values [-1, 1]
 * @returns HSL color string
 */
function eigenvectorToColor(eigenvector: number[] | undefined): string {
  if (!eigenvector || eigenvector.length < 3) {
    // Fallback to amber
    return LIVING_EARTH.amber;
  }

  // Map eigenvector[0] to hue (warm range: 20-60 degrees)
  const hue = Math.round(20 + (eigenvector[0] + 1) * 20);
  // Map eigenvector[1] to saturation (50-90%)
  const saturation = Math.round(50 + (eigenvector[1] + 1) * 20);
  // Map eigenvector[2] to lightness (40-70%)
  const lightness = Math.round(40 + (eigenvector[2] + 1) * 15);

  return `hsl(${hue}, ${saturation}%, ${lightness}%)`;
}

/**
 * Get a consistent color for a spectator ID (hash-based).
 */
function getColorForId(id: string): string {
  let hash = 0;
  for (let i = 0; i < id.length; i++) {
    hash = ((hash << 5) - hash + id.charCodeAt(i)) | 0;
  }
  const index = Math.abs(hash) % DEFAULT_CURSOR_COLORS.length;
  return DEFAULT_CURSOR_COLORS[index];
}

// =============================================================================
// Component: SpectatorCursorDot
// =============================================================================

interface SpectatorCursorDotProps {
  cursor: SpectatorCursor;
  color: string;
  opacity: number;
  showName: boolean;
}

function SpectatorCursorDot({ cursor, color, opacity, showName }: SpectatorCursorDotProps) {
  return (
    <div
      className="absolute pointer-events-none"
      style={{
        left: `${cursor.position.x * 100}%`,
        top: `${cursor.position.y * 100}%`,
        transform: 'translate(-50%, -50%)',
        opacity,
        transition: 'left 80ms ease-out, top 80ms ease-out, opacity 300ms ease-out',
      }}
      aria-hidden="true"
    >
      {/* Cursor dot */}
      <div
        className="rounded-full"
        style={{
          width: CURSOR_SIZE,
          height: CURSOR_SIZE,
          backgroundColor: `${color}80`, // 50% opacity
          border: `2px solid ${color}`,
          boxShadow: `0 0 8px ${color}40`,
        }}
      />

      {/* Optional name label */}
      {showName && cursor.name && (
        <div
          className="absolute left-1/2 -translate-x-1/2 whitespace-nowrap text-xs font-medium px-1.5 py-0.5 rounded bg-stone-800/80 text-stone-200"
          style={{ top: NAME_OFFSET }}
        >
          {cursor.name}
        </div>
      )}
    </div>
  );
}

// =============================================================================
// Component: SpectatorOverlay
// =============================================================================

export function SpectatorOverlay({
  spectators,
  showCursors,
  eigenvectorColors = false,
  maxAge = DEFAULT_MAX_AGE,
  showNames = false,
  className,
}: SpectatorOverlayProps) {
  // Calculate cursor opacity based on age
  const getCursorOpacity = useCallback(
    (lastUpdate: number): number => {
      const age = Date.now() - lastUpdate;
      if (age > maxAge) return 0;
      if (age < maxAge * 0.5) return 1;
      // Fade out in second half of max age
      return 1 - (age - maxAge * 0.5) / (maxAge * 0.5);
    },
    [maxAge]
  );

  // Filter visible cursors and calculate their properties
  const visibleCursors = useMemo(() => {
    if (!showCursors) return [];

    const now = Date.now();
    return spectators
      .filter((cursor) => now - cursor.lastUpdate <= maxAge)
      .map((cursor) => ({
        cursor,
        color: eigenvectorColors
          ? eigenvectorToColor(cursor.eigenvector)
          : getColorForId(cursor.id),
        opacity: getCursorOpacity(cursor.lastUpdate),
      }))
      .filter(({ opacity }) => opacity > 0);
  }, [spectators, showCursors, eigenvectorColors, maxAge, getCursorOpacity]);

  if (!showCursors || visibleCursors.length === 0) {
    return null;
  }

  return (
    <div
      className={cn(
        'absolute inset-0 pointer-events-none overflow-hidden',
        className
      )}
      role="presentation"
      aria-label={`${visibleCursors.length} spectators visible`}
    >
      {visibleCursors.map(({ cursor, color, opacity }) => (
        <SpectatorCursorDot
          key={cursor.id}
          cursor={cursor}
          color={color}
          opacity={opacity}
          showName={showNames}
        />
      ))}
    </div>
  );
}

// =============================================================================
// Exports
// =============================================================================

export default SpectatorOverlay;
export { eigenvectorToColor, getColorForId };
