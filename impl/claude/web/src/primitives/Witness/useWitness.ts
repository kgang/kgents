/**
 * useWitness Hook
 *
 * Unified hook for witnessing actions across all surfaces.
 *
 * "Every action leaves a mark. The mark IS the witness."
 */

import { useCallback, useState } from 'react';
import { createMark, type CreateMarkRequest } from '../../api/witness';
import type { WitnessMark } from './types';

// =============================================================================
// Hook Options
// =============================================================================

export interface UseWitnessOptions {
  /** Whether to enable witnessing (default: true) */
  enabled?: boolean;

  /** Default author for marks */
  author?: 'kent' | 'claude' | 'system';

  /** Parent mark ID for causal lineage */
  parentMarkId?: string;
}

// =============================================================================
// Hook Implementation
// =============================================================================

/**
 * Hook for witnessing actions.
 *
 * @example
 * const { witness, marks, isWitnessing } = useWitness();
 *
 * // Witness an action
 * const markId = await witness('Expanded portal', {
 *   reasoning: 'User requested to see docs',
 *   principles: ['joy_inducing', 'composable'],
 * });
 *
 * // Fire-and-forget witnessing
 * witness('Quick action', { fireAndForget: true });
 */
export function useWitness(options?: UseWitnessOptions) {
  const { enabled = true, parentMarkId } = options ?? {};

  // State
  const [marks, setMarks] = useState<WitnessMark[]>([]);
  const [isWitnessing, setIsWitnessing] = useState(false);
  const [pendingCount, setPendingCount] = useState(0);

  /**
   * Witness an action and create a mark.
   *
   * @param action - What was done
   * @param options - Witnessing options
   * @returns The mark ID (or null if fire-and-forget)
   */
  const witness = useCallback(
    async (
      action: string,
      witnessOptions?: {
        reasoning?: string;
        principles?: string[];
        metadata?: Record<string, unknown>;
        automatic?: boolean;
        fireAndForget?: boolean;
      }
    ): Promise<string | null> => {
      if (!enabled) {
        return null;
      }

      const {
        reasoning,
        principles = [],
        metadata,
        automatic = false,
        fireAndForget = false,
      } = witnessOptions ?? {};

      // Build the mark request
      const request: CreateMarkRequest = {
        action,
        reasoning,
        principles,
        parent_mark_id: parentMarkId,
      };

      if (fireAndForget) {
        // Fire and forget - don't wait for response
        setPendingCount((c) => c + 1);

        createMark(request)
          .then((mark) => {
            // Add to local marks
            setMarks((prev) => [
              {
                ...mark,
                automatic,
                metadata,
              },
              ...prev,
            ]);
          })
          .catch((error) => {
            console.error('[useWitness] Fire-and-forget mark failed:', error);
          })
          .finally(() => {
            setPendingCount((c) => Math.max(0, c - 1));
          });

        return null;
      }

      // Wait for response
      setIsWitnessing(true);
      try {
        const mark = await createMark(request);

        // Add to local marks
        setMarks((prev) => [
          {
            ...mark,
            automatic,
            metadata,
          },
          ...prev,
        ]);

        return mark.id;
      } catch (error) {
        console.error('[useWitness] Mark creation failed:', error);
        return null;
      } finally {
        setIsWitnessing(false);
      }
    },
    [enabled, parentMarkId]
  );

  /**
   * Clear local marks cache.
   */
  const clearMarks = useCallback(() => {
    setMarks([]);
  }, []);

  return {
    /** Witness an action */
    witness,

    /** Local marks cache */
    marks,

    /** Whether currently witnessing (for awaited calls) */
    isWitnessing,

    /** Number of pending fire-and-forget marks */
    pendingCount,

    /** Whether there are pending marks */
    hasPending: pendingCount > 0,

    /** Clear local marks cache */
    clearMarks,
  };
}

export default useWitness;
