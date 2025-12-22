/**
 * Barrel exports for React hooks.
 *
 * Foundation hooks kept after surgical refactor.
 * AGENTESE-specific hooks removed 2025-12-22.
 */

// Async state management
export {
  useAsyncState,
  type AsyncState,
  type AsyncStatus,
  type UseAsyncStateOptions,
  type UseAsyncStateReturn,
} from './useAsyncState';

// SSE streaming (generic infrastructure)
export {
  useProjectedStream,
  type StreamConfig,
  type UseProjectedStreamResult,
} from './useProjectedStream';

// Performance optimization
export { useBatchedEvents } from './useBatchedEvents';

// Layout and responsiveness
export {
  useLayoutContext,
  useLayoutMeasure,
  useWindowLayout,
  LayoutContextProvider,
  DEFAULT_LAYOUT_CONTEXT,
} from './useLayoutContext';

// Connectivity
export { useOnlineStatus } from './useOnlineStatus';

// Input handling
export {
  useKeyboardShortcuts,
  createDefaultShortcuts,
  type ShortcutContext,
  type ShortcutDefinition,
  type Modifiers,
  type UseKeyboardShortcutsOptions,
  type UseKeyboardShortcutsReturn,
} from './useKeyboardShortcuts';

export {
  useTouchGestures,
  usePinchZoom,
  useLongPress,
  useSwipe,
  type PinchState,
  type LongPressState,
  type SwipeState,
  type UsePinchZoomOptions,
  type UseLongPressOptions,
  type UseSwipeOptions,
  type UseTouchGesturesOptions,
  type TouchGesturesState,
} from './useTouchGestures';

// Animation primitives (Everything Breathes)
export {
  useBreathing,
  getStaggeredPhaseOffset,
  getBreathingKeyframes,
  type BreathingOptions,
  type BreathingState,
} from './useBreathing';

export {
  useGrowing,
  getStaggeredGrowthDelay,
  triggerWithDelay,
  getGrowingKeyframes,
  getGrowingAnimation,
  type GrowthStage,
  type GrowingOptions,
  type GrowingState,
} from './useGrowing';

export {
  useUnfurling,
  getUnfurlingKeyframes,
  getUnfurlingAnimation,
  type UnfurlDirection,
  type UnfurlingOptions,
  type UnfurlingState,
} from './useUnfurling';

export {
  useFlowing,
  createCurvedPath,
  createSCurvePath,
  type Point,
  type FlowParticle,
  type FlowingOptions,
  type FlowingState,
} from './useFlowing';

// Simple toast notifications
export {
  useSimpleToast,
  simpleToast,
  type SimpleToastOptions,
  type UseSimpleToastReturn,
} from './useSimpleToast';

// Design polynomial state machine
export {
  useDesignPolynomial,
  useAnimationCoordination,
  densityFromWidth,
  contentLevelFromWidth,
  designTransition,
  inferSyncStrategy,
  computeTemporalOverlap,
  DEFAULT_STATE as DEFAULT_DESIGN_STATE,
  type Density,
  type ContentLevel,
  type MotionType,
  type AnimationPhaseName,
  type AnimationPhase,
  type SyncStrategy,
  type AnimationConstraint,
  type DesignState,
  type DesignInput,
  type DesignOutput,
  type UseDesignPolynomialOptions,
  type UseDesignPolynomialResult,
  type UseAnimationCoordinationOptions,
  type UseAnimationCoordinationResult,
} from './useDesignPolynomial';
