/**
 * BottomDrawer: Mobile-friendly panel that slides up from the bottom.
 *
 * Part of the Layout Projection Functor's Panel primitive.
 * In compact mode, panels project to bottom drawers.
 *
 * Physical constraints enforced:
 * - Handle touch target: 48px x 48px (visual can be smaller)
 * - Drawer handle visual: 40px x 4px centered in 48px touch area
 *
 * TEMPORAL COHERENCE:
 * - Supports animation coordination via useAnimationCoordination hook
 * - When sibling drawers animate simultaneously, constraints ensure smooth transitions
 * - Uses AnimationConstraint to determine sync strategy with neighbors
 *
 * @see spec/protocols/projection.md (Layout Projection section)
 * @see plans/web-refactor/layout-projection-functor.md
 * @see impl/claude/agents/design/sheaf.py (temporal coherence)
 */

import { type ReactNode, type CSSProperties, useCallback, useEffect, useRef } from 'react';
import { PHYSICAL_CONSTRAINTS } from './types';
import {
  type AnimationConstraint,
  type AnimationPhase,
} from '../../hooks/useDesignPolynomial';

export interface BottomDrawerProps {
  /** Whether the drawer is open */
  isOpen: boolean;

  /** Callback when drawer should close */
  onClose: () => void;

  /** Title shown in the drawer header */
  title: string;

  /** Drawer content */
  children: ReactNode;

  /** Maximum height as percentage of viewport (default: 70) */
  maxHeightPercent?: number;

  /** Whether to show backdrop overlay (default: true) */
  showBackdrop?: boolean;

  /** Custom class name for the drawer */
  className?: string;

  /** Custom class name for the content area */
  contentClassName?: string;

  /** Whether to allow drag-to-close (future enhancement) */
  dragToClose?: boolean;

  /** Z-index for the drawer (default: 50) */
  zIndex?: number;

  /** Accessible label for the drawer */
  ariaLabel?: string;

  // ===== TEMPORAL COHERENCE PROPS =====

  /** Context ID for animation coordination (required for coordination) */
  contextId?: string;

  /** Animation constraints from useAnimationCoordination hook */
  animationConstraints?: AnimationConstraint[];

  /** Neighbor's animation progress for lock_step sync (0-1) */
  neighborProgress?: number | null;

  /** Callback when animation phase changes */
  onAnimationPhaseChange?: (phase: AnimationPhase) => void;

  /** Animation duration in seconds (default: 0.3) */
  animationDuration?: number;
}

/**
 * Compute effective animation duration based on constraints.
 * When lock_step is required, we may need to slow down to sync with neighbor.
 */
function computeEffectiveDuration(
  baseDuration: number,
  constraints: AnimationConstraint[],
  contextId?: string
): number {
  if (!contextId || constraints.length === 0) {
    return baseDuration;
  }

  // Find constraints involving this context
  const myConstraints = constraints.filter(
    (c) => c.source === contextId || c.target === contextId
  );

  // If any constraint is lock_step, use slightly slower animation for smoother sync
  const hasLockStep = myConstraints.some((c) => c.strategy === 'lock_step');
  if (hasLockStep) {
    return baseDuration * 1.2; // 20% slower for smoother coordination
  }

  // If stagger, use base duration but consider delay
  const hasStagger = myConstraints.some((c) => c.strategy === 'stagger');
  if (hasStagger) {
    // Stagger strategy: slightly faster to leave room for sequencing
    return baseDuration * 0.9;
  }

  return baseDuration;
}

/**
 * BottomDrawer component for mobile panel projection.
 *
 * Usage:
 * ```tsx
 * // Basic usage
 * <BottomDrawer
 *   isOpen={panelState.details}
 *   onClose={() => setPanelState(s => ({ ...s, details: false }))}
 *   title="Details"
 * >
 *   <DetailPanel />
 * </BottomDrawer>
 *
 * // With animation coordination
 * const { constraints, registerAnimation, getConstraintsFor, getNeighborProgress } = useAnimationCoordination();
 *
 * <BottomDrawer
 *   isOpen={isOpen}
 *   onClose={onClose}
 *   title="Sidebar"
 *   contextId="sidebar"
 *   animationConstraints={getConstraintsFor('sidebar')}
 *   neighborProgress={getNeighborProgress('sidebar')}
 *   onAnimationPhaseChange={(phase) => registerAnimation('sidebar', phase)}
 * >
 *   {content}
 * </BottomDrawer>
 * ```
 */
export function BottomDrawer({
  isOpen,
  onClose,
  title,
  children,
  maxHeightPercent = 70,
  showBackdrop = true,
  className = '',
  contentClassName = '',
  zIndex = 50,
  ariaLabel,
  // Temporal coherence props
  contextId,
  animationConstraints = [],
  neighborProgress,
  onAnimationPhaseChange,
  animationDuration = 0.3,
}: BottomDrawerProps) {
  // Track previous isOpen state to detect transitions
  const wasOpen = useRef(isOpen);

  // Compute effective duration based on constraints
  const effectiveDuration = computeEffectiveDuration(
    animationDuration,
    animationConstraints,
    contextId
  );

  // Notify about animation phase changes
  useEffect(() => {
    if (!onAnimationPhaseChange || !contextId) return;

    // Detect state change
    if (wasOpen.current !== isOpen) {
      const phase: AnimationPhase = {
        phase: isOpen ? 'entering' : 'exiting',
        progress: 0,
        startedAt: Date.now() / 1000,
        duration: effectiveDuration,
      };
      onAnimationPhaseChange(phase);

      // After animation completes, update to active/idle
      const timerId = setTimeout(() => {
        onAnimationPhaseChange({
          ...phase,
          phase: isOpen ? 'active' : 'idle',
          progress: 1,
        });
      }, effectiveDuration * 1000);

      wasOpen.current = isOpen;
      return () => clearTimeout(timerId);
    }
  }, [isOpen, contextId, effectiveDuration, onAnimationPhaseChange]);

  // Handle escape key to close
  useEffect(() => {
    if (!isOpen) return;

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose();
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  // Prevent body scroll when open
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = '';
    }

    return () => {
      document.body.style.overflow = '';
    };
  }, [isOpen]);

  const handleBackdropClick = useCallback(() => {
    onClose();
  }, [onClose]);

  if (!isOpen) return null;

  // Determine if we should adjust animation based on neighbor
  const hasLockStepConstraint = animationConstraints.some(
    (c) =>
      c.strategy === 'lock_step' &&
      (c.source === contextId || c.target === contextId)
  );

  // If lock_step and we have neighbor progress, sync our animation
  // This is a simplified implementation - in practice, you'd use a more
  // sophisticated animation library like Framer Motion or GSAP
  const syncedTransform =
    hasLockStepConstraint && neighborProgress != null
      ? `translateY(${(1 - neighborProgress) * 100}%)`
      : isOpen
      ? 'translateY(0)'
      : 'translateY(100%)';

  const drawerStyle: CSSProperties = {
    transform: syncedTransform,
    maxHeight: `${maxHeightPercent}vh`,
    zIndex,
    // Adjust transition duration based on constraints
    transitionDuration: `${effectiveDuration}s`,
  };

  return (
    <>
      {/* Backdrop */}
      {showBackdrop && (
        <div
          className="fixed inset-0 bg-black/50"
          style={{ zIndex: zIndex - 1 }}
          onClick={handleBackdropClick}
          aria-hidden="true"
        />
      )}

      {/* Drawer */}
      <div
        role="dialog"
        aria-modal="true"
        aria-label={ariaLabel || title}
        className={`fixed bottom-0 left-0 right-0 bg-gray-800 rounded-t-xl shadow-2xl transform transition-transform duration-300 ${className}`}
        style={drawerStyle}
      >
        {/* Handle - 48px touch target with 40x4 visual handle */}
        <div
          className="flex justify-center items-center cursor-pointer"
          onClick={onClose}
          role="button"
          aria-label="Close drawer"
          tabIndex={0}
          onKeyDown={(e) => {
            if (e.key === 'Enter' || e.key === ' ') {
              e.preventDefault();
              onClose();
            }
          }}
          style={{
            height: PHYSICAL_CONSTRAINTS.minTouchTarget,
            minHeight: PHYSICAL_CONSTRAINTS.minTouchTarget,
          }}
        >
          {/* Visual handle indicator */}
          <div
            className="bg-gray-600 rounded-full"
            style={{
              width: PHYSICAL_CONSTRAINTS.drawerHandleVisual.width,
              height: PHYSICAL_CONSTRAINTS.drawerHandleVisual.height,
            }}
          />
        </div>

        {/* Header */}
        <div className="flex justify-between items-center px-4 pb-2 border-b border-gray-700">
          <h3 className="text-sm font-semibold text-white">{title}</h3>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-white text-lg p-1 rounded hover:bg-gray-700 transition-colors"
            style={{
              minWidth: PHYSICAL_CONSTRAINTS.minTouchTarget,
              minHeight: PHYSICAL_CONSTRAINTS.minTouchTarget,
            }}
            aria-label="Close"
          >
            ×
          </button>
        </div>

        {/* Content */}
        <div
          className={`overflow-y-auto ${contentClassName}`}
          style={{ maxHeight: `calc(${maxHeightPercent}vh - 60px)` }}
        >
          {children}
        </div>
      </div>
    </>
  );
}

export default BottomDrawer;
