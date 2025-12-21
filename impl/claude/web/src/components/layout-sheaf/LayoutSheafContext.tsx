/**
 * Layout Sheaf Context
 *
 * The gluing context that manages global layout coherence from local component claims.
 *
 * Gluing Algorithm:
 * - Multiple claims for same slot → maximum wins (all content must fit)
 * - Constraints bound the result (minHeight, maxHeight)
 * - Height doesn't change on re-render (stability law)
 *
 * @see spec/ui/layout-sheaf.md
 */

import {
  createContext,
  useContext,
  useCallback,
  useMemo,
  useState,
  type ReactNode,
  type CSSProperties,
} from 'react';
import type {
  LayoutSlot,
  LayoutClaim,
  ClaimHandle,
  ResolvedSlot,
  LayoutSheafState,
} from './types';

// =============================================================================
// Context Types
// =============================================================================

interface LayoutSheafContextValue {
  // Registration
  registerSlot: (slot: LayoutSlot) => void;
  unregisterSlot: (slotId: string) => void;

  // Claims
  claim: (
    slotId: string,
    height: number,
    transient?: boolean,
    priority?: number
  ) => ClaimHandle;

  // Resolution
  getSlotHeight: (slotId: string) => number;
  getSlotStyle: (slotId: string) => CSSProperties;

  // Debug
  getLayoutMap: () => Map<string, ResolvedSlot>;
}

// =============================================================================
// Context
// =============================================================================

const LayoutSheafContext = createContext<LayoutSheafContextValue | null>(null);

// Claim ID counter (module-scoped for uniqueness across renders)
let claimIdCounter = 0;
const generateClaimId = () => `claim-${++claimIdCounter}`;

// =============================================================================
// Resolution Algorithm
// =============================================================================

/**
 * Resolve claims into slot heights.
 *
 * Sheaf gluing: take the maximum claim (all must fit).
 * Apply constraints to bound the result.
 */
function resolveSlots(
  slots: Map<string, LayoutSlot>,
  claims: Map<string, LayoutClaim>
): Map<string, ResolvedSlot> {
  const resolved = new Map<string, ResolvedSlot>();

  // Group claims by slot
  const claimsBySlot = new Map<string, LayoutClaim[]>();
  for (const claim of claims.values()) {
    const existing = claimsBySlot.get(claim.slotId) ?? [];
    existing.push(claim);
    claimsBySlot.set(claim.slotId, existing);
  }

  // Resolve each slot with claims
  for (const [slotId, slotClaims] of claimsBySlot) {
    const slot = slots.get(slotId);
    const constraints = slot?.constraints ?? {};

    // Maximum claim wins (sheaf gluing condition)
    let height =
      slotClaims.length > 0
        ? Math.max(...slotClaims.map((c) => c.requestedHeight))
        : (constraints.minHeight ?? 0);

    // Apply constraints
    if (constraints.maxHeight !== undefined) {
      height = Math.min(height, constraints.maxHeight);
    }
    if (constraints.minHeight !== undefined) {
      height = Math.max(height, constraints.minHeight);
    }

    resolved.set(slotId, {
      id: slotId,
      height,
      claims: slotClaims,
    });
  }

  // Add registered slots with no claims
  for (const [slotId, slot] of slots) {
    if (!resolved.has(slotId)) {
      resolved.set(slotId, {
        id: slotId,
        height: slot.constraints.minHeight ?? 0,
        claims: [],
      });
    }
  }

  return resolved;
}

// =============================================================================
// Provider
// =============================================================================

export function LayoutSheafProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<LayoutSheafState>({
    slots: new Map(),
    claims: new Map(),
    resolved: new Map(),
  });

  const registerSlot = useCallback((slot: LayoutSlot) => {
    setState((prev) => {
      const slots = new Map(prev.slots);
      slots.set(slot.id, slot);
      const resolved = resolveSlots(slots, prev.claims);
      return { ...prev, slots, resolved };
    });
  }, []);

  const unregisterSlot = useCallback((slotId: string) => {
    setState((prev) => {
      const slots = new Map(prev.slots);
      slots.delete(slotId);
      const resolved = resolveSlots(slots, prev.claims);
      return { ...prev, slots, resolved };
    });
  }, []);

  const claim = useCallback(
    (
      slotId: string,
      height: number,
      transient: boolean = false,
      priority: number = 0
    ): ClaimHandle => {
      const claimId = generateClaimId();
      const newClaim: LayoutClaim = {
        id: claimId,
        slotId,
        requestedHeight: height,
        isTransient: transient,
        priority,
      };

      setState((prev) => {
        const claims = new Map(prev.claims);
        claims.set(claimId, newClaim);
        const resolved = resolveSlots(prev.slots, claims);
        return { ...prev, claims, resolved };
      });

      return {
        id: claimId,
        slotId,
        release: () => {
          setState((prev) => {
            const claims = new Map(prev.claims);
            claims.delete(claimId);
            const resolved = resolveSlots(prev.slots, claims);
            return { ...prev, claims, resolved };
          });
        },
        update: (newHeight: number) => {
          setState((prev) => {
            const claims = new Map(prev.claims);
            const existing = claims.get(claimId);
            if (existing) {
              claims.set(claimId, { ...existing, requestedHeight: newHeight });
            }
            const resolved = resolveSlots(prev.slots, claims);
            return { ...prev, claims, resolved };
          });
        },
      };
    },
    []
  );

  const getSlotHeight = useCallback(
    (slotId: string): number => {
      return state.resolved.get(slotId)?.height ?? 0;
    },
    [state.resolved]
  );

  const getSlotStyle = useCallback(
    (slotId: string): CSSProperties => {
      const resolved = state.resolved.get(slotId);
      if (!resolved) return {};
      return {
        height: resolved.height,
        minHeight: resolved.height,
      };
    },
    [state.resolved]
  );

  const getLayoutMap = useCallback(() => state.resolved, [state.resolved]);

  const value = useMemo(
    () => ({
      registerSlot,
      unregisterSlot,
      claim,
      getSlotHeight,
      getSlotStyle,
      getLayoutMap,
    }),
    [registerSlot, unregisterSlot, claim, getSlotHeight, getSlotStyle, getLayoutMap]
  );

  return (
    <LayoutSheafContext.Provider value={value}>
      {children}
    </LayoutSheafContext.Provider>
  );
}

// =============================================================================
// Hooks
// =============================================================================

/**
 * Access the Layout Sheaf context.
 * Throws if used outside LayoutSheafProvider.
 */
export function useLayoutSheaf(): LayoutSheafContextValue {
  const context = useContext(LayoutSheafContext);
  if (!context) {
    throw new Error('useLayoutSheaf must be used within LayoutSheafProvider');
  }
  return context;
}

/**
 * Access the Layout Sheaf context, or null if not available.
 * Use this for components that should work with or without the provider.
 */
export function useLayoutSheafOptional(): LayoutSheafContextValue | null {
  return useContext(LayoutSheafContext);
}
