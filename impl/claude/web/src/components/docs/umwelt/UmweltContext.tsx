/**
 * UmweltContext - Provider for observer reality shift state
 *
 * This context manages the transition state when observers change,
 * coordinating animations across the AspectPanel, ObserverPicker,
 * and toast notifications.
 *
 * @see plans/umwelt-visualization.md
 */

import {
  createContext,
  useContext,
  useState,
  useCallback,
  useRef,
  useMemo,
  type ReactNode,
} from 'react';
import type { Density } from '@/hooks/useDesignPolynomial';
import { useMotionPreferences } from '@/components/joy/useMotionPreferences';
import type { Observer } from '../ObserverPicker';
import type { PathMetadata } from '../useAgenteseDiscovery';
import { computeUmweltDiff } from './useUmweltDiff';
import {
  type UmweltDiff,
  UMWELT_MOTION,
  UMWELT_DENSITY_CONFIG,
  getObserverColor,
} from './umwelt.types';
import { simpleToast } from '@/hooks/useSimpleToast';

// =============================================================================
// Context Types
// =============================================================================

interface UmweltContextValue {
  /** Current diff being animated (null if idle) */
  currentDiff: UmweltDiff | null;

  /** Whether a transition animation is in progress */
  isTransitioning: boolean;

  /** The color of the current observer (for ripple) */
  observerColor: string;

  /** Whether the ripple effect should be shown */
  showRipple: boolean;

  /** Set of aspects currently being revealed (for stagger) */
  revealingAspects: Set<string>;

  /** Set of aspects currently being hidden */
  hidingAspects: Set<string>;

  /** Trigger a transition between observers */
  triggerTransition: (
    from: Observer,
    to: Observer,
    metadata: Record<string, PathMetadata>,
    density: Density
  ) => void;

  /** Clear the transition state immediately */
  clearTransition: () => void;
}

// =============================================================================
// Context
// =============================================================================

const UmweltContext = createContext<UmweltContextValue | null>(null);

// =============================================================================
// Toast Formatting
// =============================================================================

function formatDiffMessage(diff: UmweltDiff, format: 'minimal' | 'standard' | 'detailed'): string {
  if (format === 'minimal') {
    const parts: string[] = [];
    if (diff.revealed.length > 0) parts.push(`+${diff.revealed.length}`);
    if (diff.hidden.length > 0) parts.push(`-${diff.hidden.length}`);
    return parts.join(' ') || 'No change';
  }

  if (format === 'standard') {
    const parts: string[] = [];
    if (diff.revealed.length > 0) {
      parts.push(`${diff.revealed.length} aspect${diff.revealed.length > 1 ? 's' : ''} revealed`);
    }
    if (diff.hidden.length > 0) {
      parts.push(`${diff.hidden.length} faded from view`);
    }
    return parts.join(', ') || 'No perceptual change';
  }

  // Detailed format
  const parts: string[] = [];
  if (diff.revealed.length > 0) {
    const names = diff.revealed.slice(0, 5).map((a) => a.aspect);
    const more = diff.revealed.length > 5 ? ` +${diff.revealed.length - 5}` : '';
    parts.push(`Revealed: ${names.join(', ')}${more}`);
  }
  if (diff.hidden.length > 0) {
    const names = diff.hidden.slice(0, 3).map((a) => a.aspect);
    const more = diff.hidden.length > 3 ? ` +${diff.hidden.length - 3}` : '';
    parts.push(`Hidden: ${names.join(', ')}${more}`);
  }
  return parts.join('. ') || 'Reality unchanged';
}

// =============================================================================
// Provider
// =============================================================================

export interface UmweltProviderProps {
  children: ReactNode;
}

/**
 * Provider for umwelt transition state.
 *
 * Wrap your AGENTESE docs explorer with this to enable
 * observer reality shift animations.
 *
 * @example
 * ```tsx
 * <UmweltProvider>
 *   <AgenteseDocs />
 * </UmweltProvider>
 * ```
 */
export function UmweltProvider({ children }: UmweltProviderProps) {
  const { shouldAnimate } = useMotionPreferences();

  const [currentDiff, setCurrentDiff] = useState<UmweltDiff | null>(null);
  const [isTransitioning, setIsTransitioning] = useState(false);
  const [observerColor, setObserverColor] = useState<string>('#22C55E'); // developer default
  const [showRipple, setShowRipple] = useState(false);
  const [revealingAspects, setRevealingAspects] = useState<Set<string>>(new Set());
  const [hidingAspects, setHidingAspects] = useState<Set<string>>(new Set());

  // Track last switch time for rapid switching detection
  const lastSwitchRef = useRef<number>(0);
  const transitionTimeoutRef = useRef<number | null>(null);

  // Clear any pending timeout
  const clearPendingTimeout = useCallback(() => {
    if (transitionTimeoutRef.current !== null) {
      clearTimeout(transitionTimeoutRef.current);
      transitionTimeoutRef.current = null;
    }
  }, []);

  // Clear transition state
  const clearTransition = useCallback(() => {
    clearPendingTimeout();
    setCurrentDiff(null);
    setIsTransitioning(false);
    setShowRipple(false);
    setRevealingAspects(new Set());
    setHidingAspects(new Set());
  }, [clearPendingTimeout]);

  // Trigger a transition
  const triggerTransition = useCallback(
    (from: Observer, to: Observer, metadata: Record<string, PathMetadata>, density: Density) => {
      const now = Date.now();
      const isRapidSwitch = now - lastSwitchRef.current < UMWELT_MOTION.rapidSwitchThreshold;
      lastSwitchRef.current = now;

      // Compute the diff
      const diff = computeUmweltDiff(from, to, metadata);

      // If no perceptual change, skip animation
      if (diff.revealed.length === 0 && diff.hidden.length === 0) {
        setObserverColor(getObserverColor(to.archetype));
        return;
      }

      // Update observer color immediately
      setObserverColor(getObserverColor(to.archetype));

      // If rapid switching, skip to final state (no toast)
      if (isRapidSwitch) {
        clearTransition();
        return;
      }

      // Clear any existing transition
      clearPendingTimeout();

      // Get density config
      const config = UMWELT_DENSITY_CONFIG[density];

      // Start transition
      setCurrentDiff(diff);
      setIsTransitioning(true);

      // Show ripple
      if (config.ripple && shouldAnimate) {
        setShowRipple(true);
        setTimeout(() => setShowRipple(false), UMWELT_MOTION.standard);
      }

      // Set revealing/hiding aspect sets for stagger
      const revealKeys = new Set(diff.revealed.map((a) => `${a.path}:${a.aspect}`));
      const hideKeys = new Set(diff.hidden.map((a) => `${a.path}:${a.aspect}`));
      setRevealingAspects(revealKeys);
      setHidingAspects(hideKeys);

      // Show toast (with density-appropriate format) - subtle, brief
      const message = formatDiffMessage(diff, config.toast);
      if (diff.revealed.length > 0 || diff.hidden.length > 0) {
        simpleToast.info(`→ ${to.archetype}`, message, { duration: 1500 });
      }

      // Clear after animation completes
      const animationDuration = shouldAnimate ? UMWELT_MOTION.deliberate : 0;
      transitionTimeoutRef.current = window.setTimeout(() => {
        setIsTransitioning(false);
        setCurrentDiff(null);
        setRevealingAspects(new Set());
        setHidingAspects(new Set());
      }, animationDuration);
    },
    [shouldAnimate, clearPendingTimeout, clearTransition]
  );

  // Memoize context value
  const value = useMemo(
    (): UmweltContextValue => ({
      currentDiff,
      isTransitioning,
      observerColor,
      showRipple,
      revealingAspects,
      hidingAspects,
      triggerTransition,
      clearTransition,
    }),
    [
      currentDiff,
      isTransitioning,
      observerColor,
      showRipple,
      revealingAspects,
      hidingAspects,
      triggerTransition,
      clearTransition,
    ]
  );

  return <UmweltContext.Provider value={value}>{children}</UmweltContext.Provider>;
}

// =============================================================================
// Hook
// =============================================================================

/**
 * Access umwelt transition state.
 *
 * @throws If used outside UmweltProvider
 */
export function useUmwelt(): UmweltContextValue {
  const context = useContext(UmweltContext);

  if (!context) {
    throw new Error('useUmwelt must be used within an UmweltProvider');
  }

  return context;
}

/**
 * Safe version of useUmwelt that returns null if no provider.
 * Useful for components that work with or without umwelt animations.
 */
export function useUmweltSafe(): UmweltContextValue | null {
  return useContext(UmweltContext);
}

export default UmweltProvider;
