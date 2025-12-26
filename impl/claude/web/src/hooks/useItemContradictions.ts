/**
 * useItemContradictions Hook
 *
 * Fetches contradictions for a specific K-Block from the backend.
 * Uses the contradiction API to query by item ID filter.
 *
 * Philosophy:
 *   "Surfacing, interrogating, and systematically interacting with
 *    personal beliefs, values, and contradictions is ONE OF THE MOST
 *    IMPORTANT PARTS of the system."
 *   - Zero Seed Grand Strategy, LAW 4
 */

import { useEffect, useCallback } from 'react';
import { useAsyncState } from './useAsyncState';
import { apiClient } from '../api/client';

// =============================================================================
// Types
// =============================================================================

/**
 * K-Block summary within a contradiction pair.
 */
export interface ContradictionKBlockSummary {
  id: string;
  content: string;
  layer: number | null;
  title: string | null;
}

/**
 * A single contradiction pair detected between two K-Blocks.
 */
export interface ContradictionPair {
  /** Contradiction ID (sorted K-Block IDs) */
  id: string;
  /** Type: APPARENT, PRODUCTIVE, TENSION, FUNDAMENTAL */
  type: string;
  /** Severity/strength of contradiction (0.0 - 1.0) */
  severity: number;
  /** First K-Block in the pair */
  k_block_a: ContradictionKBlockSummary;
  /** Second K-Block in the pair */
  k_block_b: ContradictionKBlockSummary;
  /** Super-additive loss (combined - sum) */
  super_additive_loss: number;
  /** Individual loss of K-Block A */
  loss_a: number;
  /** Individual loss of K-Block B */
  loss_b: number;
  /** Combined loss */
  loss_combined: number;
  /** Detection timestamp (ISO) */
  detected_at: string;
  /** Suggested resolution strategy */
  suggested_strategy: string;
  /** Full classification data */
  classification: Record<string, unknown>;
}

/**
 * Response from listing contradictions.
 */
interface ListContradictionsResponse {
  contradictions: ContradictionPair[];
  total: number;
  has_more: boolean;
}

/**
 * Return type for useItemContradictions hook.
 */
export interface UseItemContradictionsResult {
  /** List of contradiction pairs involving this K-Block */
  contradictions: ContradictionPair[];
  /** Total count of contradictions */
  count: number;
  /** Loading state */
  loading: boolean;
  /** Error if fetch failed */
  error: Error | null;
  /** Refetch contradictions */
  refetch: () => void;
}

// =============================================================================
// Hook
// =============================================================================

/**
 * Hook to fetch contradictions for a specific K-Block.
 *
 * Queries /api/contradictions to find all contradiction pairs
 * where the given K-Block is either k_block_a or k_block_b.
 *
 * @param kblockId - K-Block ID to query contradictions for (or null to skip)
 * @returns Contradiction pairs, count, loading state, and error
 *
 * @example
 * ```typescript
 * const { contradictions, count, loading } = useItemContradictions(kblock.id);
 *
 * if (count > 0) {
 *   return <ContradictionBadge hasContradiction count={count} />;
 * }
 * ```
 */
export function useItemContradictions(
  kblockId: string | null
): UseItemContradictionsResult {
  const { state, execute } = useAsyncState<ListContradictionsResponse>();

  const fetchContradictions = useCallback(async () => {
    if (!kblockId) {
      return;
    }

    // Fetch all contradictions from the API
    // Note: The current API doesn't support filtering by K-Block ID directly,
    // so we fetch all and filter client-side. A future optimization could add
    // a server-side filter parameter.
    const response = await apiClient.get<ListContradictionsResponse>(
      '/api/contradictions',
      {
        params: {
          limit: 100, // Reasonable limit for client-side filtering
        },
      }
    );

    // Filter to only contradictions involving this K-Block
    const filtered = response.data.contradictions.filter(
      (c) => c.k_block_a.id === kblockId || c.k_block_b.id === kblockId
    );

    return {
      contradictions: filtered,
      total: filtered.length,
      has_more: false,
    };
  }, [kblockId]);

  // Fetch on mount and when kblockId changes
  useEffect(() => {
    if (kblockId) {
      execute(fetchContradictions() as Promise<ListContradictionsResponse>);
    }
  }, [kblockId, execute, fetchContradictions]);

  // Convert async state to hook result
  const contradictions = state.data?.contradictions ?? [];
  const count = state.data?.total ?? 0;

  return {
    contradictions,
    count,
    loading: state.isLoading,
    error: state.error ? new Error(state.error) : null,
    refetch: () => {
      if (kblockId) {
        execute(fetchContradictions() as Promise<ListContradictionsResponse>);
      }
    },
  };
}

/**
 * Determine severity level from numeric severity value.
 * Maps the 0.0-1.0 severity to low/medium/high categories.
 */
export function getSeverityLevel(severity: number): 'low' | 'medium' | 'high' {
  if (severity < 0.3) return 'low';
  if (severity < 0.6) return 'medium';
  return 'high';
}

/**
 * Get the "other" K-Block in a contradiction pair.
 * Given a K-Block ID and a contradiction pair, returns the other K-Block.
 */
export function getOtherKBlock(
  kblockId: string,
  pair: ContradictionPair
): ContradictionKBlockSummary {
  return pair.k_block_a.id === kblockId ? pair.k_block_b : pair.k_block_a;
}

export default useItemContradictions;
