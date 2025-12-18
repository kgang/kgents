/**
 * useDesignPolynomial: React hook mirroring the Python DESIGN_POLYNOMIAL state machine.
 *
 * This hook implements the client-side polynomial from agents/design/polynomial.py,
 * providing:
 * - DesignState: density × content_level × motion × should_animate × animation_phase
 * - Transitions: ViewportResize, ContainerResize, AnimationToggle, MotionRequest
 * - Outputs: StateChanged, NoChange
 *
 * The Python polynomial has 144 states (3 × 4 × 6 × 2).
 * This hook mirrors that state machine in TypeScript.
 *
 * TEMPORAL COHERENCE:
 * - AnimationPhase tracks where each component is in its animation lifecycle
 * - AnimationConstraint coordinates sibling animations to prevent visual artifacts
 * - SyncStrategy determines how overlapping animations synchronize
 *
 * RELATIONSHIP TO AGENTESE:
 * - concept.design.operad.verify can verify law adherence
 * - This hook is a PROJECTION of the polynomial to React
 * - The polynomial IS the ground truth; this hook is a mirror
 *
 * @see impl/claude/agents/design/polynomial.py
 * @see impl/claude/agents/design/sheaf.py (temporal coherence)
 * @see plans/design-language-consolidation.md
 */

import { useState, useCallback, useEffect, useMemo } from 'react';

// =============================================================================
// Types (mirroring Python types.py and polynomial.py)
// =============================================================================

/**
 * Density dimension - determined by viewport width.
 * Breakpoints (aligned with spec): compact (<768), comfortable (768-1023), spacious (>=1024)
 */
export type Density = 'compact' | 'comfortable' | 'spacious';

/**
 * Content level dimension - determined by container width.
 * Breakpoints: icon (<60), title (60-149), summary (150-279), full (>=280)
 */
export type ContentLevel = 'icon' | 'title' | 'summary' | 'full';

/**
 * Motion type dimension - user preference + requested animation.
 */
export type MotionType = 'identity' | 'breathe' | 'pop' | 'shake' | 'shimmer';

// =============================================================================
// Temporal Coherence Types (mirroring Python types.py)
// =============================================================================

/**
 * Animation lifecycle phase names.
 */
export type AnimationPhaseName = 'idle' | 'entering' | 'active' | 'exiting';

/**
 * Where in an animation lifecycle a component is.
 * Enables the sheaf to detect temporal overlap between siblings.
 */
export interface AnimationPhase {
  readonly phase: AnimationPhaseName;
  readonly progress: number; // 0.0 to 1.0
  readonly startedAt: number; // timestamp
  readonly duration: number; // seconds
}

/**
 * How to synchronize overlapping animations.
 */
export type SyncStrategy =
  | 'lock_step' // Both use same progress curve
  | 'stagger' // One waits for other to reach threshold
  | 'interpolate_boundary' // Run independently, interpolate boundary
  | 'leader_follower'; // One is primary, other follows

/**
 * Constraint telling components how to coordinate animations.
 * Generated when sibling components animate simultaneously.
 */
export interface AnimationConstraint {
  readonly source: string; // Context ID of first component
  readonly target: string; // Context ID of second component
  readonly strategy: SyncStrategy;
  readonly window: [number, number]; // [start_time, end_time] of overlap
}

/**
 * Complete design state (product type: 3 × 4 × 5 × 2 = 120 states)
 * Note: Python has 6 motion types (includes a 6th), we have 5.
 * Extended with optional animation_phase for temporal coherence.
 */
export interface DesignState {
  readonly density: Density;
  readonly contentLevel: ContentLevel;
  readonly motion: MotionType;
  readonly shouldAnimate: boolean;
  readonly animationPhase?: AnimationPhase | null;
}

/**
 * Design inputs - the four transition types.
 */
export type DesignInput =
  | { type: 'viewportResize'; width: number; height: number }
  | { type: 'containerResize'; width: number }
  | { type: 'animationToggle'; enabled: boolean }
  | { type: 'motionRequest'; motion: MotionType };

/**
 * Design outputs - what happened after a transition.
 */
export type DesignOutput =
  | { type: 'stateChanged'; oldState: DesignState; newState: DesignState }
  | { type: 'noChange'; state: DesignState };

// =============================================================================
// State Machine Logic (mirroring polynomial.py)
// =============================================================================

/**
 * Map viewport width to density.
 * Breakpoints aligned with spec/protocols/projection.md:
 * - compact: <768px (mobile)
 * - comfortable: 768-1023px (tablet)
 * - spacious: >=1024px (desktop)
 */
function densityFromWidth(width: number): Density {
  if (width < 768) return 'compact';
  if (width < 1024) return 'comfortable';
  return 'spacious';
}

/**
 * Map container width to content level.
 * Breakpoints from Python: icon (<60), title (60-149), summary (150-279), full (>=280)
 */
function contentLevelFromWidth(width: number): ContentLevel {
  if (width < 60) return 'icon';
  if (width < 150) return 'title';
  if (width < 280) return 'summary';
  return 'full';
}

/**
 * Process a design input and return new state + output.
 * This is the core state machine logic from Python.
 */
function designTransition(
  state: DesignState,
  input: DesignInput
): [DesignState, DesignOutput] {
  switch (input.type) {
    case 'viewportResize': {
      const newDensity = densityFromWidth(input.width);
      if (newDensity !== state.density) {
        const newState = { ...state, density: newDensity };
        return [newState, { type: 'stateChanged', oldState: state, newState }];
      }
      return [state, { type: 'noChange', state }];
    }

    case 'containerResize': {
      const newLevel = contentLevelFromWidth(input.width);
      if (newLevel !== state.contentLevel) {
        const newState = { ...state, contentLevel: newLevel };
        return [newState, { type: 'stateChanged', oldState: state, newState }];
      }
      return [state, { type: 'noChange', state }];
    }

    case 'animationToggle': {
      if (input.enabled !== state.shouldAnimate) {
        const newState: DesignState = {
          ...state,
          shouldAnimate: input.enabled,
          // Reset motion to identity when disabling animations (law enforcement)
          motion: input.enabled ? state.motion : 'identity',
        };
        return [newState, { type: 'stateChanged', oldState: state, newState }];
      }
      return [state, { type: 'noChange', state }];
    }

    case 'motionRequest': {
      // If animations disabled, ignore motion requests (law: !shouldAnimate => identity)
      if (!state.shouldAnimate) {
        return [state, { type: 'noChange', state }];
      }
      if (input.motion !== state.motion) {
        const newState = { ...state, motion: input.motion };
        return [newState, { type: 'stateChanged', oldState: state, newState }];
      }
      return [state, { type: 'noChange', state }];
    }
  }
}

// =============================================================================
// Default State
// =============================================================================

const DEFAULT_STATE: DesignState = {
  density: 'spacious',
  contentLevel: 'full',
  motion: 'identity',
  shouldAnimate: true,
};

// =============================================================================
// Hook
// =============================================================================

export interface UseDesignPolynomialOptions {
  /** Initial state (defaults to spacious/full/identity/animate) */
  initialState?: Partial<DesignState>;
  /** Auto-track viewport resize (default: true) */
  trackViewport?: boolean;
  /** Callback when state changes */
  onStateChange?: (output: DesignOutput) => void;
}

export interface UseDesignPolynomialResult {
  /** Current design state */
  state: DesignState;
  /** Send an input to the state machine */
  send: (input: DesignInput) => DesignOutput;
  /** Convenience: resize viewport (triggers density change) */
  resizeViewport: (width: number, height: number) => DesignOutput;
  /** Convenience: resize container (triggers content level change) */
  resizeContainer: (width: number) => DesignOutput;
  /** Convenience: toggle animations */
  toggleAnimation: (enabled: boolean) => DesignOutput;
  /** Convenience: request motion */
  requestMotion: (motion: MotionType) => DesignOutput;
  /** Reset to initial state */
  reset: () => void;
}

// =============================================================================
// Animation Coordination Types
// =============================================================================

/**
 * Registered animation for a context.
 */
interface RegisteredAnimation {
  contextId: string;
  phase: AnimationPhase;
  registeredAt: number;
}

/**
 * Options for useAnimationCoordination hook.
 */
export interface UseAnimationCoordinationOptions {
  /** How often to check for constraint updates (ms) */
  updateInterval?: number;
}

/**
 * Result from useAnimationCoordination hook.
 */
export interface UseAnimationCoordinationResult {
  /** Current animation constraints between components */
  constraints: AnimationConstraint[];
  /** Register an animation for coordination */
  registerAnimation: (contextId: string, phase: AnimationPhase) => void;
  /** Unregister an animation */
  unregisterAnimation: (contextId: string) => void;
  /** Get neighbor's animation progress (for lock_step coordination) */
  getNeighborProgress: (contextId: string) => number | null;
  /** Check if a context has any active constraints */
  hasConstraints: (contextId: string) => boolean;
  /** Get constraints involving a specific context */
  getConstraintsFor: (contextId: string) => AnimationConstraint[];
}

/**
 * React hook that implements the DESIGN_POLYNOMIAL state machine.
 *
 * Usage:
 * ```tsx
 * const { state, resizeViewport } = useDesignPolynomial();
 *
 * // State updates on window resize (if trackViewport: true)
 * console.log(state.density); // 'compact' | 'comfortable' | 'spacious'
 *
 * // Manual transition
 * resizeViewport(375, 667); // Mobile dimensions
 * ```
 */
export function useDesignPolynomial(
  options: UseDesignPolynomialOptions = {}
): UseDesignPolynomialResult {
  const {
    initialState,
    trackViewport = true,
    onStateChange,
  } = options;

  // Initialize state with defaults + overrides
  const [state, setState] = useState<DesignState>(() => ({
    ...DEFAULT_STATE,
    ...initialState,
  }));

  // Send an input through the state machine
  // Note: setState is synchronous in React, so capturedOutput will be set before we use it
  const send = useCallback(
    (input: DesignInput): DesignOutput => {
      // Compute transition synchronously first to get the output
      const [newState, output] = designTransition(state, input);

      // Only update state if it changed
      if (output.type === 'stateChanged') {
        setState(newState);
        if (onStateChange) {
          onStateChange(output);
        }
      }

      return output;
    },
    [onStateChange, state]
  );

  // Convenience methods
  const resizeViewport = useCallback(
    (width: number, height: number) =>
      send({ type: 'viewportResize', width, height }),
    [send]
  );

  const resizeContainer = useCallback(
    (width: number) => send({ type: 'containerResize', width }),
    [send]
  );

  const toggleAnimation = useCallback(
    (enabled: boolean) => send({ type: 'animationToggle', enabled }),
    [send]
  );

  const requestMotion = useCallback(
    (motion: MotionType) => send({ type: 'motionRequest', motion }),
    [send]
  );

  const reset = useCallback(() => {
    setState({ ...DEFAULT_STATE, ...initialState });
  }, [initialState]);

  // Auto-track viewport resize
  useEffect(() => {
    if (!trackViewport) return;

    const handleResize = () => {
      resizeViewport(window.innerWidth, window.innerHeight);
    };

    // Initial measurement
    handleResize();

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, [trackViewport, resizeViewport]);

  return useMemo(
    () => ({
      state,
      send,
      resizeViewport,
      resizeContainer,
      toggleAnimation,
      requestMotion,
      reset,
    }),
    [state, send, resizeViewport, resizeContainer, toggleAnimation, requestMotion, reset]
  );
}

// =============================================================================
// Animation Coordination Hook
// =============================================================================

/**
 * Infer sync strategy from two animation phases.
 * Mirrors Python sheaf._infer_sync_strategy().
 */
function inferSyncStrategy(
  phase1: AnimationPhase,
  phase2: AnimationPhase
): SyncStrategy {
  const p1 = phase1.phase;
  const p2 = phase2.phase;

  // Entering + exiting: stagger them
  if (
    (p1 === 'entering' && p2 === 'exiting') ||
    (p1 === 'exiting' && p2 === 'entering')
  ) {
    return 'stagger';
  }

  // Same phase: lock step
  if (p1 === p2) {
    return 'lock_step';
  }

  // One is active: interpolate boundary
  if (p1 === 'active' || p2 === 'active') {
    return 'interpolate_boundary';
  }

  // Default: lock step
  return 'lock_step';
}

/**
 * Compute temporal overlap between two animation phases.
 */
function computeTemporalOverlap(
  phase1: AnimationPhase,
  phase2: AnimationPhase
): [number, number] | null {
  const end1 = phase1.startedAt + phase1.duration;
  const end2 = phase2.startedAt + phase2.duration;

  const overlapStart = Math.max(phase1.startedAt, phase2.startedAt);
  const overlapEnd = Math.min(end1, end2);

  if (overlapStart >= overlapEnd) {
    return null; // No temporal overlap
  }

  return [overlapStart, overlapEnd];
}

/**
 * Hook for coordinating animations between sibling components.
 *
 * This hook implements the client-side equivalent of DesignSheaf's
 * temporal coherence features. It tracks registered animations and
 * generates constraints when siblings animate simultaneously.
 *
 * Usage:
 * ```tsx
 * const { registerAnimation, constraints, getConstraintsFor } = useAnimationCoordination();
 *
 * // When component starts animating
 * registerAnimation('sidebar', {
 *   phase: 'exiting',
 *   progress: 0,
 *   startedAt: Date.now() / 1000,
 *   duration: 0.3,
 * });
 *
 * // Check for coordination constraints
 * const myConstraints = getConstraintsFor('sidebar');
 * if (myConstraints.some(c => c.strategy === 'lock_step')) {
 *   // Sync with neighbor's progress
 * }
 * ```
 */
export function useAnimationCoordination(
  _options: UseAnimationCoordinationOptions = {}
): UseAnimationCoordinationResult {
  // Note: updateInterval is reserved for future use with real-time progress tracking
  // const { updateInterval = 16 } = options; // ~60fps default

  // Track registered animations
  const [animations, setAnimations] = useState<Map<string, RegisteredAnimation>>(
    () => new Map()
  );

  // Computed constraints
  const [constraints, setConstraints] = useState<AnimationConstraint[]>([]);

  // Register an animation
  const registerAnimation = useCallback(
    (contextId: string, phase: AnimationPhase) => {
      setAnimations((prev) => {
        const next = new Map(prev);
        next.set(contextId, {
          contextId,
          phase,
          registeredAt: Date.now(),
        });
        return next;
      });
    },
    []
  );

  // Unregister an animation
  const unregisterAnimation = useCallback((contextId: string) => {
    setAnimations((prev) => {
      const next = new Map(prev);
      next.delete(contextId);
      return next;
    });
  }, []);

  // Compute constraints when animations change
  useEffect(() => {
    const animList = Array.from(animations.values());
    const newConstraints: AnimationConstraint[] = [];

    // Pairwise comparison (simplified - in real impl, check sibling relationship)
    for (let i = 0; i < animList.length; i++) {
      for (let j = i + 1; j < animList.length; j++) {
        const anim1 = animList[i];
        const anim2 = animList[j];

        const window = computeTemporalOverlap(anim1.phase, anim2.phase);
        if (window !== null) {
          newConstraints.push({
            source: anim1.contextId,
            target: anim2.contextId,
            strategy: inferSyncStrategy(anim1.phase, anim2.phase),
            window,
          });
        }
      }
    }

    setConstraints(newConstraints);
  }, [animations]);

  // Get neighbor's progress for lock_step coordination
  const getNeighborProgress = useCallback(
    (contextId: string): number | null => {
      // Find constraint involving this context
      const relevantConstraint = constraints.find(
        (c) => c.source === contextId || c.target === contextId
      );

      if (!relevantConstraint || relevantConstraint.strategy !== 'lock_step') {
        return null;
      }

      // Get neighbor's animation
      const neighborId =
        relevantConstraint.source === contextId
          ? relevantConstraint.target
          : relevantConstraint.source;

      const neighborAnim = animations.get(neighborId);
      return neighborAnim?.phase.progress ?? null;
    },
    [constraints, animations]
  );

  // Check if context has any constraints
  const hasConstraints = useCallback(
    (contextId: string): boolean => {
      return constraints.some(
        (c) => c.source === contextId || c.target === contextId
      );
    },
    [constraints]
  );

  // Get constraints for a specific context
  const getConstraintsFor = useCallback(
    (contextId: string): AnimationConstraint[] => {
      return constraints.filter(
        (c) => c.source === contextId || c.target === contextId
      );
    },
    [constraints]
  );

  return useMemo(
    () => ({
      constraints,
      registerAnimation,
      unregisterAnimation,
      getNeighborProgress,
      hasConstraints,
      getConstraintsFor,
    }),
    [
      constraints,
      registerAnimation,
      unregisterAnimation,
      getNeighborProgress,
      hasConstraints,
      getConstraintsFor,
    ]
  );
}

// =============================================================================
// Exports
// =============================================================================

export {
  densityFromWidth,
  contentLevelFromWidth,
  designTransition,
  inferSyncStrategy,
  computeTemporalOverlap,
  DEFAULT_STATE,
};

export default useDesignPolynomial;
