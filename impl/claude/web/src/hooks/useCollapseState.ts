/**
 * useCollapseState — Hook for collapse verification state
 *
 * Grounded in: spec/ui/axioms.md — A2 (Sloppification), A8 (Understandability)
 *
 * Fetches collapse state for a K-Block from the backend API.
 * Four collapsing functions make AI capabilities graspable:
 * - TypeScript → Binary (compiles?)
 * - Tests → Binary (passes?)
 * - Constitution → Score (0-7)
 * - Galois → Loss (0-1)
 */

import { useState, useEffect, useCallback } from 'react';
import type {
  CollapseState,
  CollapseResult,
  ConstitutionalCollapse,
  GaloisCollapse,
  SlopLevel,
  GaloisTier,
} from '../types';

const API_BASE = '/api/collapse';

interface UseCollapseStateResult {
  /** Current collapse state */
  state: CollapseState | null;

  /** Loading status */
  loading: boolean;

  /** Error (if any) */
  error: string | null;

  /** Refresh collapse state */
  refresh: () => Promise<void>;
}

/**
 * Default pending collapse state.
 */
const PENDING_STATE: CollapseState = {
  typescript: { status: 'pending' },
  tests: { status: 'pending' },
  constitution: { score: 0, principles: {} },
  galois: { loss: 0.5, tier: 'AESTHETIC' as GaloisTier },
  overallSlop: 'medium' as SlopLevel,
  evidence: [],
};

/**
 * Hook for fetching collapse state for a K-Block.
 */
export function useCollapseState(kblockId: string | null): UseCollapseStateResult {
  const [state, setState] = useState<CollapseState | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  /**
   * Fetch collapse state from backend.
   */
  const refresh = useCallback(async () => {
    if (!kblockId) {
      setState(null);
      return;
    }

    try {
      setLoading(true);
      setError(null);

      const response = await fetch(`${API_BASE}/${encodeURIComponent(kblockId)}`);
      if (!response.ok) {
        if (response.status === 404) {
          // K-Block not found, use pending state
          setState(PENDING_STATE);
          return;
        }
        throw new Error(`Failed to fetch collapse state: ${response.status}`);
      }

      const data = await response.json();

      // Map backend response to frontend types
      const collapseState: CollapseState = {
        typescript: mapCollapseResult(data.typescript),
        tests: mapCollapseResult(data.tests),
        constitution: mapConstitutionalCollapse(data.constitution),
        galois: mapGaloisCollapse(data.galois),
        overallSlop: mapSlopLevel(data.overall_slop),
        evidence: data.evidence || [],
      };

      setState(collapseState);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      // Use pending state on error
      setState(PENDING_STATE);
    } finally {
      setLoading(false);
    }
  }, [kblockId]);

  // Fetch when kblockId changes
  useEffect(() => {
    refresh();
  }, [refresh]);

  return {
    state,
    loading,
    error,
    refresh,
  };
}

/**
 * Map backend collapse result to frontend type.
 */
function mapCollapseResult(result: Record<string, unknown> | undefined): CollapseResult {
  if (!result) {
    return { status: 'pending' };
  }

  return {
    status: mapCollapseStatus(String(result.status || 'pending')),
    score: result.score as number | undefined,
    total: result.total as number | undefined,
    message: result.message as string | undefined,
  };
}

/**
 * Map status string to CollapseStatus.
 */
function mapCollapseStatus(status: string): 'pass' | 'partial' | 'fail' | 'pending' {
  const statusMap: Record<string, 'pass' | 'partial' | 'fail' | 'pending'> = {
    pass: 'pass',
    partial: 'partial',
    fail: 'fail',
    pending: 'pending',
  };
  return statusMap[status.toLowerCase()] || 'pending';
}

/**
 * Map backend constitutional collapse to frontend type.
 */
function mapConstitutionalCollapse(
  data: Record<string, unknown> | undefined
): ConstitutionalCollapse {
  if (!data) {
    return { score: 0, principles: {} };
  }

  return {
    score: Number(data.score || 0),
    principles: (data.principles as Record<string, number>) || {},
    weakest: findWeakestPrinciple(data.principles as Record<string, number> | undefined),
  };
}

/**
 * Find the weakest principle (lowest score).
 */
function findWeakestPrinciple(principles: Record<string, number> | undefined): string | undefined {
  if (!principles) return undefined;

  let weakest: string | undefined;
  let lowestScore = Infinity;

  for (const [principle, score] of Object.entries(principles)) {
    if (score < lowestScore) {
      lowestScore = score;
      weakest = principle;
    }
  }

  return weakest;
}

/**
 * Map backend Galois collapse to frontend type.
 */
function mapGaloisCollapse(data: Record<string, unknown> | undefined): GaloisCollapse {
  if (!data) {
    return { loss: 0.5, tier: 'AESTHETIC' as GaloisTier };
  }

  return {
    loss: Number(data.loss || 0.5),
    tier: mapGaloisTier(String(data.tier || 'AESTHETIC')),
  };
}

/**
 * Map tier string to GaloisTier.
 */
function mapGaloisTier(tier: string): GaloisTier {
  const tierMap: Record<string, GaloisTier> = {
    CATEGORICAL: 'CATEGORICAL',
    EMPIRICAL: 'EMPIRICAL',
    AESTHETIC: 'AESTHETIC',
    SOMATIC: 'SOMATIC',
    CHAOTIC: 'CHAOTIC',
  };
  return tierMap[tier.toUpperCase()] || 'AESTHETIC';
}

/**
 * Map slop level string to SlopLevel.
 */
function mapSlopLevel(level: string | undefined): SlopLevel {
  if (!level) return 'medium';

  const levelMap: Record<string, SlopLevel> = {
    low: 'low',
    medium: 'medium',
    high: 'high',
  };
  return levelMap[level.toLowerCase()] || 'medium';
}

export default useCollapseState;
