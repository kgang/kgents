/**
 * BidQueuePanel - Shows pending bids with animations
 *
 * The bid queue where spectators can influence creation.
 * Artisans see accept/reject buttons; spectators see bid status.
 *
 * Features:
 * - Vertical queue with newest at top
 * - Bid cards with type icon, content preview, token cost
 * - Accepted bids glow green, rejected fade out
 * - Animated entrance using useUnfurling
 *
 * @see plans/crown-jewels-genesis-phase2-continuation.md - Chunk 2: BidQueue Core
 * @see docs/skills/crown-jewel-patterns.md - Pattern 5: Dual-Channel Output
 */

import React, { useCallback, useMemo } from 'react';
import {
  Sparkles,
  ArrowRight,
  Zap,
  Check,
  X,
  Clock,
  ChevronDown,
} from 'lucide-react';
import { useUnfurling } from '@/hooks/useUnfurling';
import { LIVING_EARTH } from '@/constants/colors';
import { cn } from '@/lib/utils';

// =============================================================================
// Types
// =============================================================================

export type BidType = 'inject_constraint' | 'request_direction' | 'boost_builder';
export type BidStatus = 'pending' | 'accepted' | 'rejected' | 'acknowledged';

export interface Bid {
  id: string;
  spectatorId: string;
  spectatorName?: string;
  bidType: BidType;
  content: string;
  tokenCost: number;
  submittedAt: string;
  status: BidStatus;
}

export interface BidQueuePanelProps {
  /** List of bids to display */
  bids: Bid[];
  /** Whether the viewer is the creator (can accept/reject) */
  isCreator: boolean;
  /** Callback when creator accepts a bid */
  onAccept?: (bidId: string) => void;
  /** Callback when creator rejects a bid */
  onReject?: (bidId: string) => void;
  /** Current viewer's token balance */
  tokenBalance: number;
  /** Optional class name */
  className?: string;
  /** Maximum bids to show initially */
  initialLimit?: number;
}

// =============================================================================
// Constants
// =============================================================================

const BID_TYPE_CONFIG: Record<
  BidType,
  { icon: typeof Sparkles; label: string; color: string }
> = {
  inject_constraint: {
    icon: Sparkles,
    label: 'Constraint',
    color: LIVING_EARTH.amber,
  },
  request_direction: {
    icon: ArrowRight,
    label: 'Direction',
    color: LIVING_EARTH.honey,
  },
  boost_builder: {
    icon: Zap,
    label: 'Boost',
    color: LIVING_EARTH.lantern,
  },
};

const BID_STATUS_STYLES: Record<BidStatus, string> = {
  pending: 'border-stone-200 bg-white',
  accepted: 'border-green-300 bg-green-50 animate-pulse-once',
  rejected: 'border-red-200 bg-red-50/50 opacity-60',
  acknowledged: 'border-amber-200 bg-amber-50/50',
};

// =============================================================================
// Component: BidCard
// =============================================================================

interface BidCardProps {
  bid: Bid;
  isCreator: boolean;
  onAccept?: () => void;
  onReject?: () => void;
  index: number;
}

function BidCard({ bid, isCreator, onAccept, onReject, index }: BidCardProps) {
  const { style: unfurlStyle, ref } = useUnfurling({
    enabled: true,
    delay: index * 50, // Stagger animation
    duration: 300,
  });

  const typeConfig = BID_TYPE_CONFIG[bid.bidType];
  const Icon = typeConfig.icon;

  const isPending = bid.status === 'pending';
  const isAccepted = bid.status === 'accepted';

  return (
    <div
      ref={ref}
      style={unfurlStyle}
      className={cn(
        'rounded-lg border p-3 transition-all duration-300',
        BID_STATUS_STYLES[bid.status]
      )}
    >
      {/* Header: Type + Spectator + Cost */}
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          <div
            className="p-1.5 rounded"
            style={{ backgroundColor: `${typeConfig.color}20` }}
          >
            <Icon
              className="w-3.5 h-3.5"
              style={{ color: typeConfig.color }}
            />
          </div>
          <div>
            <span className="text-xs font-medium text-stone-600">
              {typeConfig.label}
            </span>
            {bid.spectatorName && (
              <span className="text-xs text-stone-400 ml-1">
                by {bid.spectatorName}
              </span>
            )}
          </div>
        </div>

        <div className="flex items-center gap-1 text-xs font-medium text-amber-600">
          <Zap className="w-3 h-3" />
          {bid.tokenCost}
        </div>
      </div>

      {/* Content Preview */}
      <p className="text-sm text-stone-700 line-clamp-2 mb-2">
        {bid.content}
      </p>

      {/* Footer: Status or Actions */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-1 text-xs text-stone-400">
          <Clock className="w-3 h-3" />
          <span>{formatTime(bid.submittedAt)}</span>
        </div>

        {/* Creator actions */}
        {isCreator && isPending && (
          <div className="flex items-center gap-2">
            <button
              onClick={onReject}
              className="p-1.5 rounded hover:bg-red-100 text-red-500 transition-colors"
              title="Reject bid"
            >
              <X className="w-4 h-4" />
            </button>
            <button
              onClick={onAccept}
              className="p-1.5 rounded hover:bg-green-100 text-green-600 transition-colors"
              title="Accept bid"
            >
              <Check className="w-4 h-4" />
            </button>
          </div>
        )}

        {/* Status badge */}
        {!isPending && (
          <span
            className={cn(
              'px-2 py-0.5 rounded-full text-xs font-medium',
              isAccepted
                ? 'bg-green-100 text-green-700'
                : bid.status === 'acknowledged'
                  ? 'bg-amber-100 text-amber-700'
                  : 'bg-red-100 text-red-600'
            )}
          >
            {bid.status}
          </span>
        )}
      </div>
    </div>
  );
}

// =============================================================================
// Component: BidQueuePanel
// =============================================================================

export function BidQueuePanel({
  bids,
  isCreator,
  onAccept,
  onReject,
  tokenBalance,
  className,
  initialLimit = 5,
}: BidQueuePanelProps) {
  const [showAll, setShowAll] = React.useState(false);

  // Sort bids: pending first, then by submission time (newest first)
  const sortedBids = useMemo(() => {
    return [...bids].sort((a, b) => {
      // Pending bids first
      if (a.status === 'pending' && b.status !== 'pending') return -1;
      if (b.status === 'pending' && a.status !== 'pending') return 1;
      // Then by time (newest first)
      return new Date(b.submittedAt).getTime() - new Date(a.submittedAt).getTime();
    });
  }, [bids]);

  const visibleBids = showAll ? sortedBids : sortedBids.slice(0, initialLimit);
  const hiddenCount = sortedBids.length - visibleBids.length;

  const pendingCount = bids.filter((b) => b.status === 'pending').length;

  const handleAccept = useCallback(
    (bidId: string) => {
      onAccept?.(bidId);
    },
    [onAccept]
  );

  const handleReject = useCallback(
    (bidId: string) => {
      onReject?.(bidId);
    },
    [onReject]
  );

  if (bids.length === 0) {
    return (
      <div className={cn('rounded-lg border border-stone-200 p-6', className)}>
        <div className="text-center text-stone-400">
          <Sparkles className="w-8 h-8 mx-auto mb-2 opacity-50" />
          <p className="text-sm">No bids yet</p>
          <p className="text-xs mt-1">
            Spectators can submit bids to influence creation
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className={cn('rounded-lg border border-stone-200 bg-stone-50', className)}>
      {/* Header */}
      <div className="px-4 py-3 border-b border-stone-200 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <h3 className="font-medium text-stone-700">Bid Queue</h3>
          {pendingCount > 0 && (
            <span className="px-2 py-0.5 rounded-full bg-amber-100 text-amber-700 text-xs font-medium">
              {pendingCount} pending
            </span>
          )}
        </div>

        {/* Token balance indicator */}
        <div className="flex items-center gap-1 text-sm">
          <Zap className="w-4 h-4 text-amber-500" />
          <span className="font-medium text-stone-700">{tokenBalance}</span>
          <span className="text-stone-400">tokens</span>
        </div>
      </div>

      {/* Bid List */}
      <div className="p-3 space-y-2 max-h-[400px] overflow-y-auto">
        {visibleBids.map((bid, index) => (
          <BidCard
            key={bid.id}
            bid={bid}
            isCreator={isCreator}
            onAccept={() => handleAccept(bid.id)}
            onReject={() => handleReject(bid.id)}
            index={index}
          />
        ))}
      </div>

      {/* Show more button */}
      {hiddenCount > 0 && (
        <div className="px-4 py-2 border-t border-stone-200">
          <button
            onClick={() => setShowAll(true)}
            className="w-full flex items-center justify-center gap-1 text-sm text-stone-500 hover:text-stone-700 transition-colors"
          >
            <ChevronDown className="w-4 h-4" />
            Show {hiddenCount} more
          </button>
        </div>
      )}
    </div>
  );
}

// =============================================================================
// Helpers
// =============================================================================

function formatTime(isoString: string): string {
  const date = new Date(isoString);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);

  if (diffMins < 1) return 'just now';
  if (diffMins < 60) return `${diffMins}m ago`;

  const diffHours = Math.floor(diffMins / 60);
  if (diffHours < 24) return `${diffHours}h ago`;

  return date.toLocaleDateString();
}

// =============================================================================
// Exports
// =============================================================================

export default BidQueuePanel;
