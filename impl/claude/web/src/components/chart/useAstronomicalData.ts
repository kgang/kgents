/**
 * useAstronomicalData — Data hook for Astronomical Chart
 *
 * Fetches spec data and transforms it to star/connection format.
 * Replaces the old useSpecGraph hook.
 *
 * "The file is a lie. There is only the graph."
 */

import { useState, useCallback, useMemo } from 'react';

// NOTE: The old spec ledger API has been removed.
// This hook now returns empty data to avoid breaking components that still reference it.
// The Document Director (/director) is the canonical documents view.

// =============================================================================
// Types
// =============================================================================

export interface StarData {
  id: string;
  label: string;
  path: string;
  tier: number;
  status: 'active' | 'deprecated' | 'archived';
  claimCount: number;
  implCount: number;
  testCount: number;
  wordCount: number;
  // Position (set by layout, initially 0)
  x: number;
  y: number;
  // Visual properties (calculated)
  radius: number;
}

export interface ConnectionData {
  id: string;
  source: string;
  target: string;
  relationship: string;
  strength: number;
}

export interface AstronomicalDataOptions {
  statusFilter?: string;
  limit?: number;
}

export interface AstronomicalDataReturn {
  stars: StarData[];
  connections: ConnectionData[];
  isLoading: boolean;
  error: Error | null;
  needsScan: boolean;
  scan: () => Promise<void>;
  refetch: () => void;
}

// =============================================================================
// Stub Hook (Spec Ledger API removed)
// =============================================================================

/**
 * useAstronomicalData - STUB IMPLEMENTATION
 *
 * The old spec ledger backend has been removed. This hook now returns
 * empty data to prevent breaking components that still reference it.
 *
 * Use the Document Director (/director) for document management.
 */
export function useAstronomicalData(_options: AstronomicalDataOptions = {}): AstronomicalDataReturn {
  const [isLoading] = useState(false);
  const [error] = useState<Error | null>(null);
  const [needsScan] = useState(true);

  const scan = useCallback(async () => {
    // No-op: spec ledger removed
    console.warn('useAstronomicalData: Spec ledger backend removed. Use Document Director instead.');
  }, []);

  const refetch = useCallback(() => {
    // No-op: spec ledger removed
  }, []);

  const stars = useMemo(() => [] as StarData[], []);
  const connections = useMemo(() => [] as ConnectionData[], []);

  return {
    stars,
    connections,
    isLoading,
    error,
    needsScan,
    scan,
    refetch,
  };
}

export default useAstronomicalData;
