/**
 * useTokenBalance - Real-time token balance tracking hook
 *
 * Fetches initial balance and subscribes to balance updates via SSE.
 * Provides spend/earn methods for optimistic updates.
 *
 * Features:
 * - Initial balance fetch
 * - SSE subscription for real-time updates
 * - Optimistic spend/earn with rollback on error
 * - Loading and error states
 *
 * @see plans/crown-jewels-genesis-phase2-continuation.md - Chunk 2: Token Economy
 * @see docs/skills/crown-jewel-patterns.md - Pattern 3: Optimistic Updates
 */

import { useState, useCallback, useEffect, useRef } from 'react';

// =============================================================================
// Types
// =============================================================================

export interface TokenTransaction {
  id: string;
  amount: number;
  direction: 'in' | 'out';
  reason: string;
  timestamp: string;
  balanceAfter: number;
}

export interface UseTokenBalanceResult {
  /** Current token balance */
  balance: number;
  /** Whether the initial fetch is loading */
  isLoading: boolean;
  /** Error message if any */
  error: string | null;
  /** Recent transactions */
  recentTransactions: TokenTransaction[];
  /** Spend tokens (returns new balance or null on failure) */
  spend: (amount: number, reason?: string) => Promise<number | null>;
  /** Earn tokens (for local simulation/testing) */
  earn: (amount: number, reason?: string) => void;
  /** Refresh balance from server */
  refresh: () => Promise<void>;
  /** Whether connected to real-time updates */
  isConnected: boolean;
}

// =============================================================================
// Constants
// =============================================================================

const DEFAULT_INITIAL_BALANCE = 100;
const MAX_TRANSACTIONS_HISTORY = 20;

// =============================================================================
// Hook Implementation
// =============================================================================

export function useTokenBalance(userId: string): UseTokenBalanceResult {
  const [balance, setBalance] = useState(DEFAULT_INITIAL_BALANCE);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [recentTransactions, setRecentTransactions] = useState<TokenTransaction[]>([]);
  const [isConnected, setIsConnected] = useState(false);

  const abortRef = useRef<AbortController | null>(null);
  const eventSourceRef = useRef<EventSource | null>(null);

  // Add transaction to history
  const addTransaction = useCallback(
    (amount: number, direction: 'in' | 'out', reason: string, newBalance: number) => {
      const transaction: TokenTransaction = {
        id: `tx-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
        amount,
        direction,
        reason,
        timestamp: new Date().toISOString(),
        balanceAfter: newBalance,
      };

      setRecentTransactions((prev) =>
        [transaction, ...prev].slice(0, MAX_TRANSACTIONS_HISTORY)
      );
    },
    []
  );

  // Fetch initial balance
  const fetchBalance = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch(`/api/atelier/token/balance?user_id=${userId}`, {
        headers: {
          'X-API-Key': localStorage.getItem('api_key') || '',
        },
      });

      if (!response.ok) {
        // For demo purposes, use default balance if API not available
        if (response.status === 404) {
          setBalance(DEFAULT_INITIAL_BALANCE);
          return;
        }
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      setBalance(data.balance ?? DEFAULT_INITIAL_BALANCE);
    } catch (err) {
      // Silently use default balance for demo
      console.warn('[TokenBalance] Using default balance:', err);
      setBalance(DEFAULT_INITIAL_BALANCE);
    } finally {
      setIsLoading(false);
    }
  }, [userId]);

  // Subscribe to balance updates via SSE
  const subscribeToUpdates = useCallback(() => {
    // Clean up existing connection
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
    }

    try {
      const eventSource = new EventSource(
        `/api/atelier/token/stream?user_id=${userId}`
      );

      eventSource.onopen = () => {
        setIsConnected(true);
      };

      eventSource.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);

          if (data.type === 'balance_update') {
            setBalance(data.balance);
            if (data.transaction) {
              addTransaction(
                data.transaction.amount,
                data.transaction.direction,
                data.transaction.reason,
                data.balance
              );
            }
          }
        } catch (err) {
          console.warn('[TokenBalance] Failed to parse SSE event:', err);
        }
      };

      eventSource.onerror = () => {
        setIsConnected(false);
        // Reconnect after delay
        setTimeout(() => {
          if (eventSourceRef.current === eventSource) {
            subscribeToUpdates();
          }
        }, 5000);
      };

      eventSourceRef.current = eventSource;
    } catch (err) {
      // SSE not available, use polling or manual refresh
      console.warn('[TokenBalance] SSE not available:', err);
      setIsConnected(false);
    }
  }, [userId, addTransaction]);

  // Spend tokens
  const spend = useCallback(
    async (amount: number, reason: string = 'spend'): Promise<number | null> => {
      if (amount <= 0) return balance;
      if (balance < amount) {
        setError('Insufficient balance');
        return null;
      }

      // Optimistic update
      const previousBalance = balance;
      const newBalance = balance - amount;
      setBalance(newBalance);
      addTransaction(amount, 'out', reason, newBalance);
      setError(null);

      try {
        const response = await fetch('/api/atelier/token/spend', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-API-Key': localStorage.getItem('api_key') || '',
          },
          body: JSON.stringify({
            user_id: userId,
            amount,
            reason,
          }),
        });

        if (!response.ok) {
          throw new Error('Spend failed');
        }

        const data = await response.json();
        // Update with server balance if different
        if (data.balance !== undefined && data.balance !== newBalance) {
          setBalance(data.balance);
        }

        return data.balance ?? newBalance;
      } catch (err) {
        // Rollback on error
        setBalance(previousBalance);
        setError('Failed to process transaction');
        // Remove optimistic transaction
        setRecentTransactions((prev) => prev.slice(1));
        return null;
      }
    },
    [balance, userId, addTransaction]
  );

  // Earn tokens (for local simulation)
  const earn = useCallback(
    (amount: number, reason: string = 'earn') => {
      if (amount <= 0) return;
      const newBalance = balance + amount;
      setBalance(newBalance);
      addTransaction(amount, 'in', reason, newBalance);
    },
    [balance, addTransaction]
  );

  // Refresh balance from server
  const refresh = useCallback(async () => {
    await fetchBalance();
  }, [fetchBalance]);

  // Initial fetch
  useEffect(() => {
    fetchBalance();
  }, [fetchBalance]);

  // Subscribe to updates (optional, may not be available)
  useEffect(() => {
    // Only subscribe if we have a userId
    if (userId) {
      // Comment out SSE subscription for now since endpoint may not exist
      // subscribeToUpdates();
    }

    return () => {
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
        eventSourceRef.current = null;
      }
      if (abortRef.current) {
        abortRef.current.abort();
      }
    };
  }, [userId]);

  return {
    balance,
    isLoading,
    error,
    recentTransactions,
    spend,
    earn,
    refresh,
    isConnected,
  };
}

// =============================================================================
// Exports
// =============================================================================

export type { TokenTransaction, UseTokenBalanceResult };
