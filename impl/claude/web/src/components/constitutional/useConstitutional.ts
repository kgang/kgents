/**
 * useConstitutional — Data fetching hook for Constitutional Dashboard
 *
 * Fetches constitutional alignment and trust data for an agent.
 * Supports SSE subscriptions for real-time updates.
 */

import { useCallback, useEffect, useState } from 'react';
import type { ConstitutionalData, ConstitutionalAlignment, ConstitutionalTrustResult } from './types';

// =============================================================================
// Types
// =============================================================================

export interface UseConstitutionalOptions {
  /** Agent ID to fetch data for */
  agentId: string;
  /** Auto-fetch on mount (default: true) */
  autoFetch?: boolean;
  /** Subscribe to SSE updates (default: false) */
  subscribe?: boolean;
}

export interface UseConstitutionalResult {
  /** Combined constitutional data */
  data: ConstitutionalData | null;
  /** Latest alignment */
  alignment: ConstitutionalAlignment | null;
  /** Trust result */
  trust: ConstitutionalTrustResult | null;
  /** Loading state */
  loading: boolean;
  /** Error state */
  error: Error | null;
  /** Refresh data */
  refresh: () => Promise<void>;
}

// =============================================================================
// Hook
// =============================================================================

export function useConstitutional(options: UseConstitutionalOptions): UseConstitutionalResult {
  const { agentId, autoFetch = true, subscribe = false } = options;

  const [data, setData] = useState<ConstitutionalData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  /**
   * Fetch constitutional data from API.
   */
  const fetchData = useCallback(async () => {
    if (!agentId) return;

    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`/api/witness/constitutional/${agentId}`);

      if (!response.ok) {
        throw new Error(`Failed to fetch constitutional data: ${response.statusText}`);
      }

      const result: ConstitutionalData = await response.json();
      setData(result);
    } catch (err) {
      const error = err instanceof Error ? err : new Error(String(err));
      setError(error);
      console.error('Failed to fetch constitutional data:', error);
    } finally {
      setLoading(false);
    }
  }, [agentId]);

  /**
   * Subscribe to SSE updates.
   */
  useEffect(() => {
    if (!subscribe || !agentId) return;

    const eventSource = new EventSource(`/api/witness/stream?agent_id=${agentId}&type=constitutional`);

    eventSource.onmessage = (event) => {
      try {
        const update: ConstitutionalData = JSON.parse(event.data);
        setData(update);
      } catch (err) {
        console.error('Failed to parse SSE update:', err);
      }
    };

    eventSource.onerror = (err) => {
      console.error('SSE connection error:', err);
      eventSource.close();
    };

    return () => {
      eventSource.close();
    };
  }, [subscribe, agentId]);

  /**
   * Auto-fetch on mount or when agentId changes.
   */
  useEffect(() => {
    if (autoFetch) {
      fetchData();
    }
  }, [autoFetch, fetchData]);

  return {
    data,
    alignment: data?.alignment ?? null,
    trust: data?.trust ?? null,
    loading,
    error,
    refresh: fetchData,
  };
}
