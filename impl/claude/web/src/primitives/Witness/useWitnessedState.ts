/**
 * useWitnessedState Hook
 *
 * A state hook that automatically witnesses state transitions.
 *
 * "Every state change is a morphism that returns (newState, witnessMark)"
 */

import { useState, useCallback } from 'react';
import type { StateMorphism, WitnessedStateSetter, WitnessConfig } from './types';
import { useWitness } from './useWitness';

// =============================================================================
// Hook Implementation
// =============================================================================

/**
 * A React state hook with automatic witnessing.
 *
 * Instead of `setState(newState)`, you provide a morphism that returns
 * both the new state and the witness mark metadata.
 *
 * @example
 * const [expanded, setExpanded] = useWitnessedState(false, {
 *   action: 'portal-expand',
 *   principles: ['joy_inducing'],
 *   automatic: true,
 * });
 *
 * // Witness the state change
 * setExpanded((prev) => [
 *   !prev,
 *   {
 *     action: `Portal ${!prev ? 'expanded' : 'collapsed'}`,
 *     reasoning: 'User toggled expansion',
 *     principles: ['joy_inducing', 'composable'],
 *   }
 * ]);
 */
export function useWitnessedState<S>(
  initialState: S,
  config: WitnessConfig
): [S, WitnessedStateSetter<S>] {
  const { action, principles = [], automatic = true, enabled = true, metadata } = config;

  // Regular state
  const [state, setState] = useState<S>(initialState);

  // Witness hook
  const { witness } = useWitness({ enabled });

  /**
   * Set state with witnessing.
   *
   * The morphism takes the current state and returns:
   * [newState, witnessMarkData]
   */
  const setWitnessedState: WitnessedStateSetter<S> = useCallback(
    async (morphism: StateMorphism<S>) => {
      if (!enabled) {
        // If witnessing is disabled, just apply the morphism to state
        setState((prev) => {
          const [newState] = morphism(prev);
          return newState;
        });
        return;
      }

      // Apply the morphism
      setState((prev) => {
        const [newState, markData] = morphism(prev);

        // Witness the state change (fire-and-forget)
        witness(markData.action || action, {
          reasoning: markData.reasoning,
          principles: markData.principles || principles,
          metadata: {
            ...metadata,
            ...markData.metadata,
            previousState: prev,
            newState,
          },
          automatic,
          fireAndForget: true,
        });

        return newState;
      });
    },
    [enabled, action, principles, automatic, metadata, witness]
  );

  return [state, setWitnessedState];
}

export default useWitnessedState;
