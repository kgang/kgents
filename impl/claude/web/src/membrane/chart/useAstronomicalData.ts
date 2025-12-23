/**
 * useAstronomicalData — Data hook for Astronomical Chart
 *
 * Fetches spec data and transforms it to star/connection format.
 * Replaces the old useSpecGraph hook.
 *
 * "The file is a lie. There is only the graph."
 */

import { useState, useEffect, useCallback, useMemo } from 'react';
import {
  getLedger,
  getHarmonies,
  scanCorpus,
  type SpecEntry,
  type LedgerResponse,
  type HarmoniesResponse,
  type DataNotComputedResponse,
} from '../../api/specLedger';

// =============================================================================
// Types
// =============================================================================

export interface StarData {
  id: string;
  label: string;
  path: string;
  tier: number;
  status: SpecEntry['status'];
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
  /** AD-015: True if proxy handle data hasn't been computed yet */
  needsScan: boolean;
  /** AD-015: Trigger explicit scan to generate proxy handles */
  scan: () => Promise<void>;
  /** Re-fetch existing data */
  refetch: () => void;
}

// =============================================================================
// Constants
// =============================================================================

const BASE_RADIUS = 4;
const RADIUS_SCALE = 3;

/**
 * AD-015: Type guard to detect "needs scan" response.
 */
function isNeedsScanResponse(
  response: LedgerResponse | HarmoniesResponse | DataNotComputedResponse
): response is DataNotComputedResponse {
  return 'needs_scan' in response && response.needs_scan === true;
}

/**
 * Detect tier from spec path.
 * Tier determines color (spectral class).
 */
function detectTier(path: string): number {
  if (path.includes('principles') || path.includes('constitution')) return 0;
  if (path.includes('protocols')) return 1;
  if (path.includes('agents')) return 2;
  if (path.includes('services') || path.includes('crown')) return 3;
  if (path.includes('agentese')) return 4;
  return 2; // Default to protocols tier
}

/**
 * Calculate star radius from evidence counts.
 * Even 0-evidence specs are visible, but high-evidence specs glow larger.
 */
function calculateRadius(implCount: number, testCount: number): number {
  const evidence = implCount + testCount;
  return BASE_RADIUS + Math.log(evidence + 1) * RADIUS_SCALE;
}

// =============================================================================
// Hook
// =============================================================================

export function useAstronomicalData(options: AstronomicalDataOptions = {}): AstronomicalDataReturn {
  const { statusFilter, limit = 100 } = options;

  // State
  const [specsData, setSpecsData] = useState<LedgerResponse | null>(null);
  const [harmoniesData, setHarmoniesData] = useState<HarmoniesResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);
  const [needsScan, setNeedsScan] = useState(false);
  const [fetchTrigger, setFetchTrigger] = useState(0);

  // Fetch data
  useEffect(() => {
    let cancelled = false;

    async function fetchData() {
      setIsLoading(true);
      setError(null);
      setNeedsScan(false);

      try {
        const [specsResponse, harmoniesResponse] = await Promise.all([
          getLedger({ status: statusFilter, limit }),
          getHarmonies(limit),
        ]);

        if (cancelled) return;

        // AD-015: Check if data needs to be computed
        if (isNeedsScanResponse(specsResponse)) {
          setNeedsScan(true);
          setSpecsData(null);
          setHarmoniesData(null);
          return;
        }

        setSpecsData(specsResponse as LedgerResponse);
        setHarmoniesData(
          isNeedsScanResponse(harmoniesResponse) ? null : (harmoniesResponse as HarmoniesResponse)
        );
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err : new Error(String(err)));
        }
      } finally {
        if (!cancelled) {
          setIsLoading(false);
        }
      }
    }

    fetchData();

    return () => {
      cancelled = true;
    };
  }, [statusFilter, limit, fetchTrigger]);

  // AD-015: Explicit scan function
  const scan = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      await scanCorpus(true); // force=true for fresh analysis
      // Trigger refetch after scan completes
      setFetchTrigger((prev) => prev + 1);
    } catch (err) {
      setError(err instanceof Error ? err : new Error(String(err)));
      setIsLoading(false);
    }
  }, []);

  // Transform data to astronomical format
  const { stars, connections } = useMemo(() => {
    if (!specsData?.specs) {
      return { stars: [], connections: [] };
    }

    const specs = specsData.specs;
    const harmonies = harmoniesData?.harmonies || [];

    // Create stars from specs
    const starList: StarData[] = specs.map((spec: SpecEntry) => ({
      id: spec.path,
      label: spec.title || spec.path.split('/').pop() || spec.path,
      path: spec.path,
      tier: detectTier(spec.path),
      status: spec.status,
      claimCount: spec.claim_count,
      implCount: spec.impl_count,
      testCount: spec.test_count,
      wordCount: spec.word_count,
      // Initial position (will be set by layout)
      x: 0,
      y: 0,
      // Calculate visual radius
      radius: calculateRadius(spec.impl_count, spec.test_count),
    }));

    // Create lookup for edge validation
    const starIds = new Set(starList.map((s) => s.id));

    // Create connections from harmonies
    const connectionList: ConnectionData[] = harmonies
      .filter(
        (h: { spec_a: string; spec_b: string }) => starIds.has(h.spec_a) && starIds.has(h.spec_b)
      )
      .map(
        (
          h: { spec_a: string; spec_b: string; relationship: string; strength: number },
          i: number
        ) => ({
          id: `conn-${i}`,
          source: h.spec_a,
          target: h.spec_b,
          relationship: h.relationship,
          strength: h.strength,
        })
      );

    return { stars: starList, connections: connectionList };
  }, [specsData, harmoniesData]);

  // Refetch callback
  const refetch = useCallback(() => {
    setFetchTrigger((prev) => prev + 1);
  }, []);

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
