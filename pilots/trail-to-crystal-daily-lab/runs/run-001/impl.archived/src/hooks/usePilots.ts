/**
 * usePilots Hook
 *
 * React hook for fetching and caching pilot data.
 * Automatically refreshes every 5 minutes.
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import {
  listPilots,
  listActivePilots,
  FALLBACK_PILOTS,
  type PilotManifest,
} from '../api/pilots';

const REFRESH_INTERVAL_MS = 5 * 60 * 1000; // 5 minutes

export interface UsePilotsResult {
  /** All pilots (active, coming_soon, experimental) */
  pilots: PilotManifest[];
  /** Only active pilots */
  activePilots: PilotManifest[];
  /** Loading state */
  loading: boolean;
  /** Error message if fetch failed */
  error: string | null;
  /** Manually refresh pilots */
  refresh: () => Promise<void>;
  /** Whether using fallback data due to API failure */
  usingFallback: boolean;
}

/**
 * Hook to fetch and manage pilot data with caching and auto-refresh.
 */
export function usePilots(): UsePilotsResult {
  const [pilots, setPilots] = useState<PilotManifest[]>([]);
  const [activePilots, setActivePilots] = useState<PilotManifest[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [usingFallback, setUsingFallback] = useState(false);

  // Use ref to avoid stale closure in interval
  const mountedRef = useRef(true);

  const fetchPilots = useCallback(async () => {
    try {
      // Fetch both in parallel for efficiency
      const [allPilots, active] = await Promise.all([
        listPilots(),
        listActivePilots(),
      ]);

      if (mountedRef.current) {
        setPilots(allPilots);
        setActivePilots(active);
        setError(null);
        setUsingFallback(false);
      }
    } catch (err) {
      console.error('Failed to fetch pilots, using fallback:', err);

      if (mountedRef.current) {
        // Use fallback pilots on error
        setPilots(FALLBACK_PILOTS);
        setActivePilots(FALLBACK_PILOTS.filter((p) => p.status === 'active'));
        setError(err instanceof Error ? err.message : 'Failed to fetch pilots');
        setUsingFallback(true);
      }
    } finally {
      if (mountedRef.current) {
        setLoading(false);
      }
    }
  }, []);

  const refresh = useCallback(async () => {
    setLoading(true);
    await fetchPilots();
  }, [fetchPilots]);

  // Initial fetch on mount
  useEffect(() => {
    mountedRef.current = true;
    fetchPilots();

    return () => {
      mountedRef.current = false;
    };
  }, [fetchPilots]);

  // Auto-refresh every 5 minutes
  useEffect(() => {
    const intervalId = setInterval(() => {
      fetchPilots();
    }, REFRESH_INTERVAL_MS);

    return () => clearInterval(intervalId);
  }, [fetchPilots]);

  return {
    pilots,
    activePilots,
    loading,
    error,
    refresh,
    usingFallback,
  };
}
