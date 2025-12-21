/**
 * useLayoutClaim - Hook to claim space in a layout slot.
 *
 * Claims are registered on mount and released on unmount.
 * The slot will have at least the claimed height.
 *
 * Key Property: Transient claims (transient=true) reserve space even when
 * the component's content is not visible. This prevents layout shift when
 * content appears/disappears (e.g., on hover).
 *
 * @example
 * // Reserve 16px for hover description
 * useLayoutClaim('description-slot', 16, true);
 *
 * @see spec/ui/layout-sheaf.md
 */

import { useEffect, useRef } from 'react';
import { useLayoutSheafOptional } from './LayoutSheafContext';
import type { ClaimHandle } from './types';

/**
 * Claim space in a layout slot.
 *
 * @param slotId - The slot to claim space in
 * @param height - The height to claim (in pixels)
 * @param transient - If true, space is reserved even when content is hidden
 * @param priority - Higher priority claims take precedence in ties
 * @returns The claim handle, or null if no LayoutSheafProvider exists
 */
export function useLayoutClaim(
  slotId: string,
  height: number,
  transient: boolean = false,
  priority: number = 0
): ClaimHandle | null {
  const sheaf = useLayoutSheafOptional();
  const handleRef = useRef<ClaimHandle | null>(null);

  // Track previous height to detect changes
  const prevHeightRef = useRef<number>(height);

  // Register claim on mount, release on unmount
  useEffect(() => {
    if (!sheaf) return;

    // Create new claim
    handleRef.current = sheaf.claim(slotId, height, transient, priority);

    // Cleanup: release claim on unmount
    return () => {
      handleRef.current?.release();
      handleRef.current = null;
    };
    // Only re-run if slotId, transient, or priority changes
    // Height changes are handled separately via update()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [sheaf, slotId, transient, priority]);

  // Update height when it changes (without recreating the claim)
  useEffect(() => {
    if (height !== prevHeightRef.current && handleRef.current) {
      handleRef.current.update(height);
      prevHeightRef.current = height;
    }
  }, [height]);

  return handleRef.current;
}
