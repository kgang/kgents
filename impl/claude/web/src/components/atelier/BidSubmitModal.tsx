/**
 * BidSubmitModal - Modal for spectators to submit bids
 *
 * Allows spectators to choose bid type, write content, and submit.
 * Validates token balance before submission.
 *
 * Features:
 * - Bid type selector with cost display
 * - Content textarea with character limit
 * - Token balance validation
 * - Loading state during submission
 *
 * @see plans/crown-jewels-genesis-phase2-continuation.md - Chunk 2: BidQueue Core
 * @see docs/skills/crown-jewel-patterns.md - Pattern 2: Input Validation
 */

import React, { useState, useCallback, useMemo } from 'react';
import {
  Sparkles,
  ArrowRight,
  Zap,
  X,
  AlertCircle,
  Loader2,
} from 'lucide-react';
import { LIVING_EARTH } from '@/constants/colors';
import { cn } from '@/lib/utils';
import type { BidType } from './BidQueuePanel';

// =============================================================================
// Types
// =============================================================================

export interface NewBid {
  bidType: BidType;
  content: string;
}

export interface BidSubmitModalProps {
  /** Whether the modal is open */
  isOpen: boolean;
  /** Close callback */
  onClose: () => void;
  /** Submit callback */
  onSubmit: (bid: NewBid) => Promise<void>;
  /** Current token balance */
  tokenBalance: number;
  /** Bid costs by type */
  bidCosts?: Record<BidType, number>;
  /** Optional session ID for context */
  sessionId?: string;
}

// =============================================================================
// Constants
// =============================================================================

const DEFAULT_BID_COSTS: Record<BidType, number> = {
  inject_constraint: 10,
  request_direction: 5,
  boost_builder: 3,
};

const BID_TYPE_CONFIG: Record<
  BidType,
  { icon: typeof Sparkles; label: string; description: string; color: string }
> = {
  inject_constraint: {
    icon: Sparkles,
    label: 'Inject Constraint',
    description: 'Add a creative constraint the artisan must follow',
    color: LIVING_EARTH.amber,
  },
  request_direction: {
    icon: ArrowRight,
    label: 'Request Direction',
    description: 'Suggest a direction for the creation',
    color: LIVING_EARTH.honey,
  },
  boost_builder: {
    icon: Zap,
    label: 'Boost Builder',
    description: 'Show appreciation and encourage the artisan',
    color: LIVING_EARTH.lantern,
  },
};

const MIN_CONTENT_LENGTH = 3;
const MAX_CONTENT_LENGTH = 500;

// =============================================================================
// Component: BidTypeSelector
// =============================================================================

interface BidTypeSelectorProps {
  selectedType: BidType;
  onSelect: (type: BidType) => void;
  costs: Record<BidType, number>;
  balance: number;
}

function BidTypeSelector({
  selectedType,
  onSelect,
  costs,
  balance,
}: BidTypeSelectorProps) {
  const bidTypes: BidType[] = ['inject_constraint', 'request_direction', 'boost_builder'];

  return (
    <div className="space-y-2">
      <label className="text-sm font-medium text-stone-700">Bid Type</label>
      <div className="grid gap-2">
        {bidTypes.map((type) => {
          const config = BID_TYPE_CONFIG[type];
          const cost = costs[type];
          const canAfford = balance >= cost;
          const isSelected = selectedType === type;
          const Icon = config.icon;

          return (
            <button
              key={type}
              type="button"
              onClick={() => canAfford && onSelect(type)}
              disabled={!canAfford}
              className={cn(
                'flex items-center gap-3 p-3 rounded-lg border transition-all text-left',
                isSelected
                  ? 'border-amber-300 bg-amber-50'
                  : canAfford
                    ? 'border-stone-200 hover:border-amber-200 hover:bg-stone-50'
                    : 'border-stone-100 bg-stone-50 opacity-50 cursor-not-allowed'
              )}
            >
              <div
                className="p-2 rounded-lg"
                style={{ backgroundColor: `${config.color}20` }}
              >
                <Icon
                  className="w-5 h-5"
                  style={{ color: isSelected ? config.color : '#78716c' }}
                />
              </div>
              <div className="flex-1">
                <div className="flex items-center justify-between">
                  <span
                    className={cn(
                      'font-medium',
                      isSelected ? 'text-stone-800' : 'text-stone-600'
                    )}
                  >
                    {config.label}
                  </span>
                  <span
                    className={cn(
                      'flex items-center gap-1 text-sm',
                      canAfford ? 'text-amber-600' : 'text-red-500'
                    )}
                  >
                    <Zap className="w-3.5 h-3.5" />
                    {cost}
                  </span>
                </div>
                <p className="text-xs text-stone-400 mt-0.5">{config.description}</p>
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
}

// =============================================================================
// Component: BidSubmitModal
// =============================================================================

export function BidSubmitModal({
  isOpen,
  onClose,
  onSubmit,
  tokenBalance,
  bidCosts = DEFAULT_BID_COSTS,
  sessionId: _sessionId,
}: BidSubmitModalProps) {
  const [bidType, setBidType] = useState<BidType>('request_direction');
  const [content, setContent] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const selectedCost = bidCosts[bidType];
  const canAfford = tokenBalance >= selectedCost;
  const contentLength = content.length;
  const isContentValid =
    contentLength >= MIN_CONTENT_LENGTH && contentLength <= MAX_CONTENT_LENGTH;
  const canSubmit = canAfford && isContentValid && !isSubmitting;

  const handleSubmit = useCallback(
    async (e: React.FormEvent) => {
      e.preventDefault();
      if (!canSubmit) return;

      setIsSubmitting(true);
      setError(null);

      try {
        await onSubmit({ bidType, content: content.trim() });
        // Reset form on success
        setContent('');
        setBidType('request_direction');
        onClose();
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to submit bid');
      } finally {
        setIsSubmitting(false);
      }
    },
    [bidType, content, canSubmit, onSubmit, onClose]
  );

  const handleClose = useCallback(() => {
    if (!isSubmitting) {
      setError(null);
      onClose();
    }
  }, [isSubmitting, onClose]);

  // Don't render if not open
  if (!isOpen) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/50"
      onClick={handleClose}
    >
      <div
        className="bg-white rounded-xl shadow-xl max-w-md w-full mx-4 overflow-hidden"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="px-6 py-4 border-b border-stone-100 flex items-center justify-between">
          <h2 className="text-lg font-medium text-stone-800">Submit Bid</h2>
          <button
            onClick={handleClose}
            disabled={isSubmitting}
            className="p-1 rounded hover:bg-stone-100 text-stone-400 hover:text-stone-600 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          {/* Token Balance Display */}
          <div className="flex items-center justify-between p-3 rounded-lg bg-stone-50">
            <span className="text-sm text-stone-600">Your Balance</span>
            <div className="flex items-center gap-1.5">
              <Zap className="w-4 h-4 text-amber-500" />
              <span className="font-medium text-stone-800">{tokenBalance}</span>
              <span className="text-stone-400">tokens</span>
            </div>
          </div>

          {/* Bid Type Selector */}
          <BidTypeSelector
            selectedType={bidType}
            onSelect={setBidType}
            costs={bidCosts}
            balance={tokenBalance}
          />

          {/* Content Input */}
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <label className="text-sm font-medium text-stone-700">
                Your Bid
              </label>
              <span
                className={cn(
                  'text-xs',
                  contentLength > MAX_CONTENT_LENGTH
                    ? 'text-red-500'
                    : contentLength >= MIN_CONTENT_LENGTH
                      ? 'text-stone-400'
                      : 'text-amber-500'
                )}
              >
                {contentLength}/{MAX_CONTENT_LENGTH}
              </span>
            </div>
            <textarea
              value={content}
              onChange={(e) => setContent(e.target.value)}
              placeholder={
                bidType === 'inject_constraint'
                  ? 'e.g., "Include a reference to the sea..."'
                  : bidType === 'request_direction'
                    ? 'e.g., "Could you explore a darker tone?"'
                    : 'e.g., "Love the direction this is going!"'
              }
              className={cn(
                'w-full px-4 py-3 rounded-lg border text-sm resize-none',
                'focus:outline-none focus:ring-2 focus:ring-amber-300 focus:border-amber-300',
                'placeholder:text-stone-300',
                contentLength > MAX_CONTENT_LENGTH
                  ? 'border-red-300'
                  : 'border-stone-200'
              )}
              rows={4}
              disabled={isSubmitting}
            />
          </div>

          {/* Error Display */}
          {error && (
            <div className="flex items-center gap-2 p-3 rounded-lg bg-red-50 text-red-700 text-sm">
              <AlertCircle className="w-4 h-4 flex-shrink-0" />
              <span>{error}</span>
            </div>
          )}

          {/* Insufficient Balance Warning */}
          {!canAfford && (
            <div className="flex items-center gap-2 p-3 rounded-lg bg-amber-50 text-amber-700 text-sm">
              <AlertCircle className="w-4 h-4 flex-shrink-0" />
              <span>
                Insufficient tokens. You need {selectedCost - tokenBalance} more.
              </span>
            </div>
          )}

          {/* Submit Button */}
          <div className="flex gap-3">
            <button
              type="button"
              onClick={handleClose}
              disabled={isSubmitting}
              className="flex-1 px-4 py-2.5 rounded-lg border border-stone-200 text-stone-600 hover:bg-stone-50 transition-colors disabled:opacity-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={!canSubmit}
              className={cn(
                'flex-1 px-4 py-2.5 rounded-lg font-medium transition-all',
                'flex items-center justify-center gap-2',
                canSubmit
                  ? 'bg-amber-500 text-white hover:bg-amber-600'
                  : 'bg-stone-200 text-stone-400 cursor-not-allowed'
              )}
            >
              {isSubmitting ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Submitting...
                </>
              ) : (
                <>
                  <Zap className="w-4 h-4" />
                  Submit ({selectedCost} tokens)
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

// =============================================================================
// Exports
// =============================================================================

export default BidSubmitModal;
