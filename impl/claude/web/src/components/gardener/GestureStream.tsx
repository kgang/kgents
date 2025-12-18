/**
 * GestureStream - Living Gesture Feed with Tone Visualization
 *
 * A living stream of recent tending operations with tone indicators.
 * Replaces GestureHistory with a more organic, streaming design.
 *
 * @see spec/protocols/2d-renaissance.md - Section 3.4D
 * @see docs/creative/visual-system.md - NO EMOJIS policy
 */

import { Sprout } from 'lucide-react';
import { getVerbIcon } from '@/constants';
import type { GestureJSON, TendingVerb } from '@/reactive/types';

// =============================================================================
// Types
// =============================================================================

export interface GestureStreamProps {
  /** List of gestures to display */
  gestures: GestureJSON[];
  /** Maximum gestures to show */
  maxDisplay?: number;
  /** Compact mode */
  compact?: boolean;
  /** Custom class name */
  className?: string;
}

// =============================================================================
// Living Earth Verb Colors
// =============================================================================

const VERB_COLORS: Record<
  TendingVerb,
  {
    text: string;
    bg: string;
    border: string;
  }
> = {
  OBSERVE: {
    text: '#06B6D4', // Cyan (existing)
    bg: '#06B6D410',
    border: '#06B6D430',
  },
  PRUNE: {
    text: '#C08552', // Copper
    bg: '#C0855210',
    border: '#C0855230',
  },
  GRAFT: {
    text: '#4A6B4A', // Sage
    bg: '#4A6B4A10',
    border: '#4A6B4A30',
  },
  WATER: {
    text: '#8BAB8B', // Sprout
    bg: '#8BAB8B10',
    border: '#8BAB8B30',
  },
  ROTATE: {
    text: '#D4A574', // Amber
    bg: '#D4A57410',
    border: '#D4A57430',
  },
  WAIT: {
    text: '#6B4E3D', // Wood
    bg: '#6B4E3D10',
    border: '#6B4E3D30',
  },
};

// =============================================================================
// Main Component
// =============================================================================

export function GestureStream({
  gestures,
  maxDisplay = 10,
  compact = false,
  className = '',
}: GestureStreamProps) {
  const displayGestures = gestures.slice(-maxDisplay).reverse();

  if (displayGestures.length === 0) {
    return (
      <div className={`text-center py-6 ${className}`}>
        <Sprout className="w-10 h-10 mx-auto mb-3 text-[#4A6B4A]" />
        <p className="text-sm text-[#AB9080]">No gestures yet</p>
        <p className="text-xs text-[#6B4E3D]">Start tending your garden</p>
      </div>
    );
  }

  return (
    <div className={`space-y-2 ${className}`}>
      {displayGestures.map((gesture, index) => (
        <GestureCard
          key={`${gesture.timestamp}-${index}`}
          gesture={gesture}
          compact={compact}
          isNewest={index === 0}
        />
      ))}
    </div>
  );
}

// =============================================================================
// Gesture Card Component
// =============================================================================

interface GestureCardProps {
  gesture: GestureJSON;
  compact?: boolean;
  isNewest?: boolean;
}

function GestureCard({ gesture, compact = false, isNewest = false }: GestureCardProps) {
  const colors = VERB_COLORS[gesture.verb];
  const VerbIcon = getVerbIcon(gesture.verb);
  const timeStr = formatGestureTime(gesture.timestamp);

  return (
    <div
      className={`
        rounded-lg border transition-all duration-300
        ${compact ? 'p-2' : 'p-3'}
        ${isNewest ? 'ring-1 ring-[#8BAB8B]/30' : ''}
      `}
      style={{
        backgroundColor: colors.bg,
        borderColor: colors.border,
      }}
    >
      {/* Header Row */}
      <div className="flex items-center justify-between mb-1">
        <div className="flex items-center gap-2">
          <VerbIcon
            className={compact ? 'w-3.5 h-3.5' : 'w-4 h-4'}
            style={{ color: colors.text }}
          />
          <span
            className={`font-medium ${compact ? 'text-xs' : 'text-sm'}`}
            style={{ color: colors.text }}
          >
            {gesture.verb}
          </span>
        </div>
        <span className={`text-[#6B4E3D] ${compact ? 'text-[10px]' : 'text-xs'}`}>{timeStr}</span>
      </div>

      {/* Target */}
      <p className={`font-mono truncate text-[#AB9080] ${compact ? 'text-[10px]' : 'text-xs'}`}>
        {shortenTarget(gesture.target)}
      </p>

      {/* Reasoning (if present and not compact) */}
      {gesture.reasoning && !compact && (
        <p className="text-xs text-[#6B4E3D] mt-1 line-clamp-2 italic">"{gesture.reasoning}"</p>
      )}

      {/* Footer: Tone + Entropy */}
      <div className={`flex items-center justify-between mt-2 ${compact ? 'mt-1' : 'mt-2'}`}>
        {/* Tone Bar */}
        <ToneIndicator tone={gesture.tone} compact={compact} />

        {/* Entropy cost + result */}
        <div className={`flex items-center gap-2 ${compact ? 'text-[10px]' : 'text-xs'}`}>
          <span className="text-[#6B4E3D]">-{gesture.entropy_cost.toFixed(2)}</span>
          {gesture.result_summary && (
            <span
              className={gesture.result_summary === 'success' ? 'text-[#8BAB8B]' : 'text-[#D4A574]'}
            >
              {gesture.result_summary}
            </span>
          )}
        </div>
      </div>
    </div>
  );
}

// =============================================================================
// Tone Indicator Component
// =============================================================================

interface ToneIndicatorProps {
  tone: number;
  compact?: boolean;
}

/**
 * Tone visualization: Higher tone = warmer color gradient
 * Per spec: "Gestures have tone (0-1). Higher tone = warmer color gradient."
 */
function ToneIndicator({ tone, compact = false }: ToneIndicatorProps) {
  const percentage = Math.round(tone * 100);
  const width = compact ? 'w-16' : 'w-20';

  return (
    <div className={`flex items-center gap-1.5 ${compact ? 'text-[10px]' : 'text-xs'}`}>
      <span className="text-[#6B4E3D]">tone</span>
      <div className={`${width} h-1.5 rounded-full bg-[#2D1B14] overflow-hidden`}>
        <div
          className="h-full rounded-full transition-all duration-300"
          style={{
            width: `${percentage}%`,
            background: getToneGradient(tone),
          }}
        />
      </div>
    </div>
  );
}

// =============================================================================
// Compact Gesture List (for sidebars)
// =============================================================================

export function GestureList({ gestures, maxDisplay = 5, className = '' }: GestureStreamProps) {
  const displayGestures = gestures.slice(-maxDisplay).reverse();

  if (displayGestures.length === 0) {
    return <p className={`text-xs text-[#6B4E3D] ${className}`}>No recent gestures</p>;
  }

  return (
    <ul className={`space-y-1 ${className}`}>
      {displayGestures.map((gesture, index) => {
        const colors = VERB_COLORS[gesture.verb];
        const VerbIcon = getVerbIcon(gesture.verb);
        const timeStr = formatGestureTime(gesture.timestamp);

        return (
          <li key={`${gesture.timestamp}-${index}`} className="flex items-center gap-2 text-xs">
            <VerbIcon className="w-3 h-3" style={{ color: colors.text }} />
            <span style={{ color: colors.text }} className="font-medium">
              {gesture.verb.toLowerCase()}
            </span>
            <span className="text-[#6B4E3D] truncate flex-1 font-mono text-[10px]">
              {shortenTarget(gesture.target)}
            </span>
            <span className="text-[#4A3728]">{timeStr}</span>
          </li>
        );
      })}
    </ul>
  );
}

// =============================================================================
// Helpers
// =============================================================================

function formatGestureTime(isoDate: string): string {
  const date = new Date(isoDate);
  const now = new Date();
  const diff = now.getTime() - date.getTime();

  const minutes = Math.floor(diff / (1000 * 60));
  const hours = Math.floor(minutes / 60);

  if (hours > 24) {
    return date.toLocaleDateString(undefined, { month: 'short', day: 'numeric' });
  }
  if (hours > 0) return `${hours}h`;
  if (minutes > 0) return `${minutes}m`;
  return 'now';
}

function shortenTarget(target: string): string {
  const parts = target.split('.');
  if (parts.length <= 2) return target;
  return '...' + parts.slice(-2).join('.');
}

function getToneGradient(tone: number): string {
  // Cold (0) to warm (1)
  // Fern → Sage → Amber → Copper
  if (tone >= 0.8) {
    return 'linear-gradient(90deg, #D4A574, #C08552)'; // Amber to Copper
  }
  if (tone >= 0.6) {
    return 'linear-gradient(90deg, #8BAB8B, #D4A574)'; // Sprout to Amber
  }
  if (tone >= 0.4) {
    return 'linear-gradient(90deg, #4A6B4A, #8BAB8B)'; // Sage to Sprout
  }
  if (tone >= 0.2) {
    return '#4A6B4A'; // Sage
  }
  return '#2E4A2E'; // Fern (cool)
}

export default GestureStream;
