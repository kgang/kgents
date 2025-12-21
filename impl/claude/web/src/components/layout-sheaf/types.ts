/**
 * Layout Sheaf Types
 *
 * A Layout Sheaf provides stable global layout from locally varying components.
 * When a component's internal state changes (hover, expand), the global layout
 * constraints remain satisfied.
 *
 * "Local components, global stability. The sheaf glues them all."
 *
 * @see spec/ui/layout-sheaf.md
 */

/**
 * A named region in the layout with height constraints.
 */
export interface LayoutSlot {
  id: string;
  constraints: {
    minHeight?: number;
    maxHeight?: number;
  };
  priority: number;
}

/**
 * A component's request for space in a slot.
 *
 * Key Property: Transient claims reserve space even when inactive.
 * The space is claimed at mount, not at activation.
 */
export interface LayoutClaim {
  id: string;
  slotId: string;
  requestedHeight: number;
  isTransient: boolean;
  priority: number;
}

/**
 * Handle returned from claim() to manage the claim lifecycle.
 */
export interface ClaimHandle {
  id: string;
  slotId: string;
  /** Release the claim (call on unmount) */
  release: () => void;
  /** Update the claimed height */
  update: (newHeight: number) => void;
}

/**
 * A slot with resolved height from all claims.
 */
export interface ResolvedSlot {
  id: string;
  height: number;
  claims: LayoutClaim[];
}

/**
 * Internal state of the Layout Sheaf.
 */
export interface LayoutSheafState {
  slots: Map<string, LayoutSlot>;
  claims: Map<string, LayoutClaim>;
  resolved: Map<string, ResolvedSlot>;
}
