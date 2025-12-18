/**
 * SpendHistoryPanel - Collapsible transaction history
 *
 * Shows recent token activity with timestamps and balances.
 * Each row: timestamp, action, amount, balance after.
 *
 * Features:
 * - Collapsible panel using useUnfurling
 * - Direction-aware row styling (green earn, red spend)
 * - Relative timestamps (e.g., "2m ago")
 * - Empty state for new users
 *
 * @see plans/crown-jewels-genesis-phase2-chunks3-5.md - Chunk 3: Token Economy Visualization
 * @see hooks/useTokenBalance.ts - recentTransactions source
 */

import { useState, useMemo } from 'react';
import { ChevronDown, ChevronUp, Zap, TrendingUp, TrendingDown, History, Clock } from 'lucide-react';
import { useUnfurling } from '@/hooks/useUnfurling';
import { LIVING_EARTH } from '@/constants/colors';
import { cn } from '@/lib/utils';
import type { TokenTransaction } from '@/hooks/useTokenBalance';

// =============================================================================
// Types
// =============================================================================

export interface SpendHistoryPanelProps {
  /** Transaction history from useTokenBalance */
  transactions: TokenTransaction[];
  /** Current balance for reference */
  currentBalance: number;
  /** Initial collapsed state */
  initialCollapsed?: boolean;
  /** Maximum rows to show */
  maxRows?: number;
  /** Optional class name */
  className?: string;
}

// =============================================================================
// Helper: Format relative time
// =============================================================================

function formatRelativeTime(isoString: string): string {
  const date = new Date(isoString);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffSecs = Math.floor(diffMs / 1000);
  const diffMins = Math.floor(diffSecs / 60);
  const diffHours = Math.floor(diffMins / 60);
  const diffDays = Math.floor(diffHours / 24);

  if (diffSecs < 60) return 'just now';
  if (diffMins < 60) return `${diffMins}m ago`;
  if (diffHours < 24) return `${diffHours}h ago`;
  if (diffDays === 1) return 'yesterday';
  if (diffDays < 7) return `${diffDays}d ago`;

  return date.toLocaleDateString();
}

// =============================================================================
// Component: TransactionRow
// =============================================================================

interface TransactionRowProps {
  transaction: TokenTransaction;
  index: number;
}

function TransactionRow({ transaction, index }: TransactionRowProps) {
  const isEarn = transaction.direction === 'in';

  return (
    <div
      className={cn(
        'flex items-center justify-between py-2.5 px-3',
        'border-b border-stone-100 last:border-b-0',
        'transition-colors',
        index % 2 === 0 ? 'bg-white' : 'bg-stone-50/50'
      )}
    >
      {/* Left: Direction icon + reason */}
      <div className="flex items-center gap-2.5 min-w-0 flex-1">
        <div
          className={cn(
            'p-1.5 rounded-full flex-shrink-0',
            isEarn ? 'bg-green-100' : 'bg-red-50'
          )}
        >
          {isEarn ? (
            <TrendingUp className="w-3.5 h-3.5 text-green-600" />
          ) : (
            <TrendingDown className="w-3.5 h-3.5 text-red-500" />
          )}
        </div>

        <div className="min-w-0 flex-1">
          <p className="text-sm text-stone-700 truncate capitalize">
            {transaction.reason}
          </p>
          <p className="text-xs text-stone-400 flex items-center gap-1">
            <Clock className="w-3 h-3" />
            {formatRelativeTime(transaction.timestamp)}
          </p>
        </div>
      </div>

      {/* Right: Amount + balance after */}
      <div className="text-right flex-shrink-0 ml-3">
        <p
          className={cn(
            'text-sm font-semibold tabular-nums',
            isEarn ? 'text-green-600' : 'text-red-500'
          )}
        >
          {isEarn ? '+' : '-'}{transaction.amount}
        </p>
        <p className="text-xs text-stone-400 tabular-nums">
          → {transaction.balanceAfter}
        </p>
      </div>
    </div>
  );
}

// =============================================================================
// Component: SpendHistoryPanel
// =============================================================================

export function SpendHistoryPanel({
  transactions,
  currentBalance,
  initialCollapsed = true,
  maxRows = 10,
  className,
}: SpendHistoryPanelProps) {
  const [isCollapsed, setIsCollapsed] = useState(initialCollapsed);

  // Unfurling animation for content
  const { style: unfurlStyle, contentStyle, toggle } = useUnfurling({
    initialOpen: !initialCollapsed,
    direction: 'down',
    duration: 250,
    onUnfurled: () => setIsCollapsed(false),
    onFolded: () => setIsCollapsed(true),
  });

  // Limit visible transactions
  const visibleTransactions = useMemo(
    () => transactions.slice(0, maxRows),
    [transactions, maxRows]
  );

  // Summary stats
  const { totalEarned, totalSpent } = useMemo(() => {
    let earned = 0;
    let spent = 0;

    for (const tx of transactions) {
      if (tx.direction === 'in') {
        earned += tx.amount;
      } else {
        spent += tx.amount;
      }
    }

    return { totalEarned: earned, totalSpent: spent };
  }, [transactions]);

  const handleToggle = () => {
    toggle();
  };

  return (
    <div
      className={cn(
        'rounded-lg border border-stone-200 bg-white overflow-hidden',
        className
      )}
    >
      {/* Header (always visible, clickable) */}
      <button
        onClick={handleToggle}
        className={cn(
          'w-full flex items-center justify-between p-3',
          'hover:bg-stone-50 transition-colors',
          'border-b border-stone-100'
        )}
      >
        <div className="flex items-center gap-2">
          <History className="w-4 h-4 text-stone-400" />
          <span className="text-sm font-medium text-stone-700">
            Recent Activity
          </span>
          {transactions.length > 0 && (
            <span className="px-1.5 py-0.5 rounded-full bg-stone-100 text-xs text-stone-500">
              {transactions.length}
            </span>
          )}
        </div>

        <div className="flex items-center gap-3">
          {/* Quick summary */}
          {!isCollapsed && transactions.length > 0 && (
            <div className="flex items-center gap-2 text-xs">
              <span className="text-green-600">+{totalEarned}</span>
              <span className="text-stone-300">/</span>
              <span className="text-red-500">-{totalSpent}</span>
            </div>
          )}

          {/* Expand/collapse icon */}
          {isCollapsed ? (
            <ChevronDown className="w-4 h-4 text-stone-400" />
          ) : (
            <ChevronUp className="w-4 h-4 text-stone-400" />
          )}
        </div>
      </button>

      {/* Content (unfurls) */}
      <div style={unfurlStyle}>
        <div style={contentStyle}>
          {transactions.length === 0 ? (
            // Empty state
            <div className="p-6 text-center">
              <Zap
                className="w-8 h-8 mx-auto mb-2"
                style={{ color: `${LIVING_EARTH.honey}80` }}
              />
              <p className="text-sm text-stone-500">No activity yet</p>
              <p className="text-xs text-stone-400 mt-1">
                Your token transactions will appear here
              </p>
            </div>
          ) : (
            // Transaction list
            <div className="max-h-[300px] overflow-y-auto">
              {visibleTransactions.map((tx, index) => (
                <TransactionRow
                  key={tx.id}
                  transaction={tx}
                  index={index}
                />
              ))}

              {/* More indicator */}
              {transactions.length > maxRows && (
                <div className="p-2 text-center text-xs text-stone-400">
                  {transactions.length - maxRows} more transactions
                </div>
              )}
            </div>
          )}

          {/* Footer with current balance */}
          {transactions.length > 0 && (
            <div className="px-3 py-2 border-t border-stone-100 bg-stone-50/50 flex items-center justify-between">
              <span className="text-xs text-stone-500">Current Balance</span>
              <div className="flex items-center gap-1">
                <Zap
                  className="w-3.5 h-3.5"
                  style={{ color: LIVING_EARTH.amber }}
                />
                <span className="text-sm font-semibold text-stone-700 tabular-nums">
                  {currentBalance}
                </span>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

// =============================================================================
// Exports
// =============================================================================

export default SpendHistoryPanel;
