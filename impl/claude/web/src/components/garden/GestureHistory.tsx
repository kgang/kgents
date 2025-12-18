/**
 * GestureHistory: Display of recent tending gestures.
 *
 * The six primitive gestures:
 * - OBSERVE: Perceive without changing
 * - PRUNE: Remove what no longer serves
 * - GRAFT: Add something new
 * - WATER: Nurture via TextGRAD
 * - ROTATE: Change perspective
 * - WAIT: Allow time to pass
 *
 * @see docs/creative/visual-system.md - NO EMOJIS policy
 */

import type { GestureJSON, TendingVerb } from '@/reactive/types';
import { getVerbIcon } from '@/constants';
import { Sprout } from 'lucide-react';

interface GestureHistoryProps {
  gestures: GestureJSON[];
  maxDisplay?: number;
  className?: string;
}

/** Verb visual configuration (using Lucide icons per visual-system.md) */
const VERB_CONFIG: Record<TendingVerb, { color: string; bgColor: string }> = {
  OBSERVE: { color: 'text-blue-400', bgColor: 'bg-blue-900/30' },
  PRUNE: { color: 'text-red-400', bgColor: 'bg-red-900/30' },
  GRAFT: { color: 'text-green-400', bgColor: 'bg-green-900/30' },
  WATER: { color: 'text-cyan-400', bgColor: 'bg-cyan-900/30' },
  ROTATE: { color: 'text-purple-400', bgColor: 'bg-purple-900/30' },
  WAIT: { color: 'text-gray-400', bgColor: 'bg-gray-800' },
};

export function GestureHistory({ gestures, maxDisplay = 10, className = '' }: GestureHistoryProps) {
  const displayGestures = gestures.slice(-maxDisplay).reverse();

  if (displayGestures.length === 0) {
    return (
      <div className={`text-center py-4 text-gray-500 ${className}`}>
        <Sprout className="w-8 h-8 mx-auto mb-2 text-green-500" />
        <p className="text-sm">No gestures yet</p>
        <p className="text-xs">Start tending your garden</p>
      </div>
    );
  }

  return (
    <div className={className}>
      <ul className="space-y-2">
        {displayGestures.map((gesture, index) => (
          <GestureItem key={`${gesture.timestamp}-${index}`} gesture={gesture} />
        ))}
      </ul>
    </div>
  );
}

/** Individual gesture display */
function GestureItem({ gesture }: { gesture: GestureJSON }) {
  const config = VERB_CONFIG[gesture.verb];
  const VerbIcon = getVerbIcon(gesture.verb);
  const timeStr = formatGestureTime(gesture.timestamp);

  return (
    <div className={`rounded-lg p-3 ${config.bgColor}`}>
      {/* Header */}
      <div className="flex items-center justify-between mb-1">
        <div className="flex items-center gap-2">
          <VerbIcon className={`w-4 h-4 ${config.color}`} />
          <span className={`text-sm font-medium ${config.color}`}>{gesture.verb}</span>
        </div>
        <span className="text-xs text-gray-500">{timeStr}</span>
      </div>

      {/* Target */}
      <p className="text-xs text-gray-300 font-mono truncate">{gesture.target}</p>

      {/* Reasoning (if present) */}
      {gesture.reasoning && (
        <p className="text-xs text-gray-400 mt-1 line-clamp-2">{gesture.reasoning}</p>
      )}

      {/* Footer metrics */}
      <div className="flex items-center gap-3 mt-2 text-[10px] text-gray-500">
        <span>Tone: {(gesture.tone * 100).toFixed(0)}%</span>
        <span>Entropy: {gesture.entropy_cost.toFixed(3)}</span>
        {gesture.result_summary && (
          <span
            className={
              gesture.result_summary === 'success' ? 'text-green-500' : 'text-yellow-500'
            }
          >
            {gesture.result_summary}
          </span>
        )}
      </div>
    </div>
  );
}

/** Compact gesture list for sidebars */
export function GestureList({
  gestures,
  maxDisplay = 5,
  className = '',
}: GestureHistoryProps) {
  const displayGestures = gestures.slice(-maxDisplay).reverse();

  if (displayGestures.length === 0) {
    return <p className={`text-xs text-gray-500 ${className}`}>No recent gestures</p>;
  }

  return (
    <ul className={`space-y-1 ${className}`}>
      {displayGestures.map((gesture, index) => {
        const config = VERB_CONFIG[gesture.verb];
        const VerbIcon = getVerbIcon(gesture.verb);
        const timeStr = formatGestureTime(gesture.timestamp);

        return (
          <li
            key={`${gesture.timestamp}-${index}`}
            className="flex items-center gap-2 text-xs text-gray-400"
          >
            <VerbIcon className={`w-3.5 h-3.5 ${config.color}`} />
            <span className={config.color}>{gesture.verb.toLowerCase()}</span>
            <span className="text-gray-600 truncate flex-1 font-mono text-[10px]">
              {shortenTarget(gesture.target)}
            </span>
            <span className="text-gray-600">{timeStr}</span>
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
  if (hours > 0) return `${hours}h ago`;
  if (minutes > 0) return `${minutes}m ago`;
  return 'now';
}

function shortenTarget(target: string): string {
  // Show last 2 parts of AGENTESE path
  const parts = target.split('.');
  if (parts.length <= 2) return target;
  return '...' + parts.slice(-2).join('.');
}

export default GestureHistory;
