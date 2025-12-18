/**
 * useShellAnimation - Coordinated Animation for OS Shell Elements
 *
 * This hook implements temporal coherence for the OS shell, ensuring that
 * when one element animates (expands/collapses), neighboring elements
 * smoothly adjust their positions.
 *
 * The three shell layers:
 * - ObserverDrawer (top) - affects NavigationTree.top and main content
 * - NavigationTree (left) - affects main content left margin
 * - Terminal (bottom) - affects NavigationTree.bottom and main content
 *
 * Sheaf conditions (boundary constraints):
 * - nav.top = observer.bottom
 * - nav.bottom = terminal.top
 * - main.top = observer.bottom
 * - main.bottom = terminal.top
 * - main.left = nav.right (when nav expanded)
 *
 * The categorical insight: element positions are morphisms from animation
 * progress to pixel coordinates. The sheaf ensures these morphisms compose
 * coherently at boundaries.
 *
 * @see impl/claude/agents/design/sheaf.py (temporal coherence)
 * @see impl/claude/web/src/components/elastic/CoordinatedDrawers.tsx
 */

import { useState, useCallback, useEffect, useRef, useMemo } from 'react';
import { TOP_PANEL_HEIGHTS, BOTTOM_PANEL_HEIGHTS, SIDEBAR_WIDTHS } from '@/components/elastic';

// =============================================================================
// Types
// =============================================================================

/** Shell element identifiers */
export type ShellElementId = 'observer' | 'navigation' | 'terminal';

/** Animation phase for a shell element */
export interface ShellAnimationPhase {
  element: ShellElementId;
  action: 'expanding' | 'collapsing';
  progress: number; // 0 to 1
  startedAt: number;
  duration: number;
}

/** Computed offsets for shell layout */
export interface ShellOffsets {
  /** Top offset for elements below observer (NavigationTree, main content) */
  topOffset: number;
  /** Bottom offset for elements above terminal (NavigationTree, main content) */
  bottomOffset: number;
  /** Left offset for main content when nav is expanded */
  leftOffset: number;
  /** Whether observer is animating */
  observerAnimating: boolean;
  /** Whether terminal is animating */
  terminalAnimating: boolean;
  /** Whether navigation is animating */
  navigationAnimating: boolean;
}

/** Shell animation coordination result */
export interface UseShellAnimationResult {
  /** Current computed offsets */
  offsets: ShellOffsets;
  /** Register an animation for an element */
  registerAnimation: (element: ShellElementId, action: 'expanding' | 'collapsing', duration?: number) => void;
  /** Get current progress for an element (0-1, null if not animating) */
  getProgress: (element: ShellElementId) => number | null;
  /** Check if any element is currently animating */
  isAnyAnimating: boolean;
  /** Current observer height (animated) */
  observerHeight: number;
  /** Current terminal height (animated) */
  terminalHeight: number;
  /** Current navigation width (animated) */
  navigationWidth: number;
}

// =============================================================================
// Constants
// =============================================================================

const DEFAULT_ANIMATION_DURATION = 0.25; // seconds

// =============================================================================
// Hook
// =============================================================================

/**
 * Hook for coordinating animations between OS shell elements.
 *
 * @param observerExpanded - Current observer drawer expanded state
 * @param navigationExpanded - Current navigation tree expanded state
 * @param terminalExpanded - Current terminal expanded state
 * @param shouldAnimate - Whether animations are enabled (from motion preferences)
 *
 * @example
 * ```tsx
 * const { offsets, registerAnimation, observerHeight } = useShellAnimation({
 *   observerExpanded,
 *   navigationExpanded,
 *   terminalExpanded,
 *   shouldAnimate: true,
 * });
 *
 * // When observer toggles:
 * const handleToggle = () => {
 *   setObserverExpanded(!observerExpanded);
 *   registerAnimation('observer', observerExpanded ? 'collapsing' : 'expanding');
 * };
 *
 * // Use computed offsets
 * <NavigationTree style={{ top: offsets.topOffset }} />
 * ```
 */
export function useShellAnimation({
  observerExpanded,
  navigationExpanded,
  terminalExpanded,
  shouldAnimate = true,
}: {
  observerExpanded: boolean;
  navigationExpanded: boolean;
  terminalExpanded: boolean;
  shouldAnimate?: boolean;
}): UseShellAnimationResult {
  // Track animation phases for each element
  const [animations, setAnimations] = useState<Map<ShellElementId, ShellAnimationPhase>>(
    () => new Map()
  );

  // Track animated values (0-1 progress for each element's expansion)
  const [observerProgress, setObserverProgress] = useState(observerExpanded ? 1 : 0);
  const [navigationProgress, setNavigationProgress] = useState(navigationExpanded ? 1 : 0);
  const [terminalProgress, setTerminalProgress] = useState(terminalExpanded ? 1 : 0);

  // Animation frame refs
  const observerRafRef = useRef<number | null>(null);
  const navigationRafRef = useRef<number | null>(null);
  const terminalRafRef = useRef<number | null>(null);

  // Cleanup animation frames on unmount
  useEffect(() => {
    return () => {
      if (observerRafRef.current) cancelAnimationFrame(observerRafRef.current);
      if (navigationRafRef.current) cancelAnimationFrame(navigationRafRef.current);
      if (terminalRafRef.current) cancelAnimationFrame(terminalRafRef.current);
    };
  }, []);

  // Register an animation
  const registerAnimation = useCallback(
    (element: ShellElementId, action: 'expanding' | 'collapsing', duration = DEFAULT_ANIMATION_DURATION) => {
      if (!shouldAnimate) {
        // Skip animation, just set final value
        const finalProgress = action === 'expanding' ? 1 : 0;
        if (element === 'observer') setObserverProgress(finalProgress);
        if (element === 'navigation') setNavigationProgress(finalProgress);
        if (element === 'terminal') setTerminalProgress(finalProgress);
        return;
      }

      const phase: ShellAnimationPhase = {
        element,
        action,
        progress: 0,
        startedAt: performance.now(),
        duration: duration * 1000, // Convert to ms
      };

      setAnimations((prev) => {
        const next = new Map(prev);
        next.set(element, phase);
        return next;
      });

      // Start animation loop
      const setProgress = element === 'observer' ? setObserverProgress
        : element === 'navigation' ? setNavigationProgress
        : setTerminalProgress;

      const rafRef = element === 'observer' ? observerRafRef
        : element === 'navigation' ? navigationRafRef
        : terminalRafRef;

      const startProgress = element === 'observer' ? observerProgress
        : element === 'navigation' ? navigationProgress
        : terminalProgress;

      const targetProgress = action === 'expanding' ? 1 : 0;
      const startTime = performance.now();

      const animate = (currentTime: number) => {
        const elapsed = currentTime - startTime;
        const t = Math.min(elapsed / phase.duration, 1);
        // Ease out cubic for smooth deceleration
        const eased = 1 - Math.pow(1 - t, 3);
        const current = startProgress + (targetProgress - startProgress) * eased;

        setProgress(current);

        // Update phase progress
        setAnimations((prev) => {
          const existing = prev.get(element);
          if (existing) {
            const next = new Map(prev);
            next.set(element, { ...existing, progress: t });
            return next;
          }
          return prev;
        });

        if (t < 1) {
          rafRef.current = requestAnimationFrame(animate);
        } else {
          // Animation complete - remove from tracking
          setAnimations((prev) => {
            const next = new Map(prev);
            next.delete(element);
            return next;
          });
          rafRef.current = null;
        }
      };

      // Cancel any existing animation for this element
      if (rafRef.current) {
        cancelAnimationFrame(rafRef.current);
      }

      rafRef.current = requestAnimationFrame(animate);
    },
    [shouldAnimate, observerProgress, navigationProgress, terminalProgress]
  );

  // Sync progress with expanded state when props change (without animation registration)
  // This handles initial state and external state changes
  const prevObserverExpanded = useRef(observerExpanded);
  const prevNavigationExpanded = useRef(navigationExpanded);
  const prevTerminalExpanded = useRef(terminalExpanded);

  useEffect(() => {
    // Only auto-animate if state changed and no animation is currently running
    if (prevObserverExpanded.current !== observerExpanded && !animations.has('observer')) {
      registerAnimation('observer', observerExpanded ? 'expanding' : 'collapsing');
    }
    prevObserverExpanded.current = observerExpanded;
  }, [observerExpanded, animations, registerAnimation]);

  useEffect(() => {
    if (prevNavigationExpanded.current !== navigationExpanded && !animations.has('navigation')) {
      registerAnimation('navigation', navigationExpanded ? 'expanding' : 'collapsing');
    }
    prevNavigationExpanded.current = navigationExpanded;
  }, [navigationExpanded, animations, registerAnimation]);

  useEffect(() => {
    if (prevTerminalExpanded.current !== terminalExpanded && !animations.has('terminal')) {
      registerAnimation('terminal', terminalExpanded ? 'expanding' : 'collapsing');
    }
    prevTerminalExpanded.current = terminalExpanded;
  }, [terminalExpanded, animations, registerAnimation]);

  // Get progress for an element
  const getProgress = useCallback(
    (element: ShellElementId): number | null => {
      const phase = animations.get(element);
      return phase?.progress ?? null;
    },
    [animations]
  );

  // Compute current heights/widths from progress
  const observerHeight = useMemo(() => {
    const collapsed = TOP_PANEL_HEIGHTS.collapsed;
    const expanded = TOP_PANEL_HEIGHTS.expanded;
    return collapsed + (expanded - collapsed) * observerProgress;
  }, [observerProgress]);

  const terminalHeight = useMemo(() => {
    const collapsed = BOTTOM_PANEL_HEIGHTS.collapsed;
    const expanded = BOTTOM_PANEL_HEIGHTS.expanded;
    return collapsed + (expanded - collapsed) * terminalProgress;
  }, [terminalProgress]);

  const navigationWidth = useMemo(() => {
    const collapsed = 0;
    const expanded = SIDEBAR_WIDTHS.full;
    return collapsed + (expanded - collapsed) * navigationProgress;
  }, [navigationProgress]);

  // Compute offsets
  const offsets = useMemo((): ShellOffsets => ({
    topOffset: observerHeight,
    bottomOffset: terminalHeight,
    leftOffset: navigationWidth,
    observerAnimating: animations.has('observer'),
    terminalAnimating: animations.has('terminal'),
    navigationAnimating: animations.has('navigation'),
  }), [observerHeight, terminalHeight, navigationWidth, animations]);

  const isAnyAnimating = animations.size > 0;

  return {
    offsets,
    registerAnimation,
    getProgress,
    isAnyAnimating,
    observerHeight,
    terminalHeight,
    navigationWidth,
  };
}

export default useShellAnimation;
