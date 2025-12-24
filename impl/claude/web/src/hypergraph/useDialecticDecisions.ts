/**
 * useDialecticDecisions — Data fetching hook for dialectical decisions
 *
 * Fetches and manages dialectic decision history.
 * Real-time updates via polling (SSE can be added later).
 */

import { useCallback, useEffect, useState } from 'react';
import type { DialecticDecision } from './types/dialectic';

export interface UseDialecticDecisionsParams {
  /** Filter by date range (ISO timestamp) */
  since?: string;

  /** Filter by tags */
  tags?: string[];

  /** Polling interval in ms (0 to disable) */
  pollInterval?: number;

  /** Auto-fetch on mount */
  autoFetch?: boolean;
}

export interface UseDialecticDecisionsResult {
  /** All fetched decisions */
  decisions: DialecticDecision[];

  /** Loading state */
  loading: boolean;

  /** Error state */
  error: string | null;

  /** Manually trigger fetch */
  fetch: () => Promise<void>;

  /** Refresh (alias for fetch) */
  refresh: () => Promise<void>;

  /** Filter decisions locally */
  filter: (predicate: (d: DialecticDecision) => boolean) => DialecticDecision[];
}

/**
 * Fetch decisions from the backend.
 */
async function fetchDecisions(params?: {
  since?: string;
  tags?: string[];
}): Promise<DialecticDecision[]> {
  const url = new URL('/api/witness/decisions', window.location.origin);

  if (params?.since) {
    url.searchParams.set('since', params.since);
  }

  if (params?.tags && params.tags.length > 0) {
    url.searchParams.set('tags', params.tags.join(','));
  }

  const response = await fetch(url.toString());

  // Handle 404 gracefully - endpoint may not exist yet
  if (response.status === 404) {
    return [];
  }

  if (!response.ok) {
    throw new Error(`Failed to fetch decisions: ${response.statusText}`);
  }

  const data = await response.json();

  // Handle both array response and {decisions: [...]} wrapper
  let decisions: DialecticDecision[] = [];

  if (Array.isArray(data)) {
    decisions = data;
  } else if (data.decisions && Array.isArray(data.decisions)) {
    decisions = data.decisions;
  } else {
    console.warn('[useDialecticDecisions] Unexpected response format:', data);
    return [];
  }

  // Normalize snake_case to camelCase for vetoReason
  return decisions.map((d: any) => ({
    ...d,
    vetoReason: d.vetoReason ?? d.veto_reason ?? null,
  }));
}

/**
 * Hook for managing dialectic decisions.
 */
export function useDialecticDecisions({
  since,
  tags,
  pollInterval = 0,
  autoFetch = true,
}: UseDialecticDecisionsParams = {}): UseDialecticDecisionsResult {
  const [decisions, setDecisions] = useState<DialecticDecision[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetch = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const data = await fetchDecisions({ since, tags });
      setDecisions(data);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Unknown error';
      setError(message);
      console.error('[useDialecticDecisions] Fetch failed:', err);
    } finally {
      setLoading(false);
    }
  }, [since, tags]);

  // Auto-fetch on mount
  useEffect(() => {
    if (autoFetch) {
      fetch();
    }
  }, [autoFetch, fetch]);

  // Polling (if enabled)
  useEffect(() => {
    if (pollInterval > 0) {
      const intervalId = setInterval(() => {
        fetch();
      }, pollInterval);

      return () => clearInterval(intervalId);
    }
  }, [pollInterval, fetch]);

  // Filter helper
  const filter = useCallback(
    (predicate: (d: DialecticDecision) => boolean) => {
      return decisions.filter(predicate);
    },
    [decisions]
  );

  return {
    decisions,
    loading,
    error,
    fetch,
    refresh: fetch,
    filter,
  };
}
