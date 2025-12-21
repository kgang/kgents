/**
 * Layout Sheaf - Global Coherence from Local Components
 *
 * A Layout Sheaf provides stable global layout from locally varying components.
 * When a component's internal state changes (hover, expand, animate), the
 * global layout constraints remain satisfied.
 *
 * Core Insight: UI layout is a sheaf gluing problem. Local component states
 * are sections over a topology of layout regions. The global layout is the
 * glued section that satisfies all constraints.
 *
 * Four Laws:
 * 1. Stability - Height doesn't change on re-render
 * 2. Containment - All claims fit (max wins)
 * 3. Monotonicity - Adding claims only increases height
 * 4. Idempotence - Duplicate claims have no effect
 *
 * @example
 * // Reserve 16px for hover description
 * useLayoutClaim('description-slot', 16, true);
 *
 * // Render with stable height
 * <ReservedSlot id="description-slot">
 *   <FadeTransition show={isHovered}>
 *     {description}
 *   </FadeTransition>
 * </ReservedSlot>
 *
 * @see spec/ui/layout-sheaf.md
 */

// Types
export type {
  LayoutSlot,
  LayoutClaim,
  ClaimHandle,
  ResolvedSlot,
  LayoutSheafState,
} from './types';

// Context & Provider
export {
  LayoutSheafProvider,
  useLayoutSheaf,
  useLayoutSheafOptional,
} from './LayoutSheafContext';

// Hook
export { useLayoutClaim } from './useLayoutClaim';

// Components
export { ReservedSlot, type ReservedSlotProps } from './ReservedSlot';
export { FadeTransition, type FadeTransitionProps } from './FadeTransition';
