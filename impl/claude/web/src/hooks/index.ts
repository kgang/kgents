/**
 * Barrel exports for React hooks.
 *
 * Import hooks from this module for cleaner imports:
 * ```ts
 * import { useAsyncState, useTownStreamWidget, useOnlineStatus } from '@/hooks';
 * ```
 */

// Async state management
export {
  useAsyncState,
  type AsyncState,
  type AsyncStatus,
  type UseAsyncStateOptions,
  type UseAsyncStateReturn,
} from './useAsyncState';

// SSE streaming hooks
export {
  useTownStreamWidget,
  type UseTownStreamWidgetOptions,
  type UseTownStreamWidgetResult,
} from './useTownStreamWidget';

// Town loading hook (projection-first extraction)
export { useTownLoader } from './useTownLoader';

// Atelier streaming
export { useAtelierStream, type UseAtelierStreamResult } from './useAtelierStream';

// Brain WebSocket streaming (Phase 1 Crown Jewels completion)
export {
  useBrainStream,
  type UseBrainStreamOptions,
  type UseBrainStreamResult,
  type BrainEvent,
} from './useBrainStream';

// Gestalt streaming (Sprint 1: Live Architecture)
export {
  useGestaltStream,
  type UseGestaltStreamOptions,
  type UseGestaltStreamReturn,
} from './useGestaltStream';

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

// Design polynomial state machine (mirrors Python DESIGN_POLYNOMIAL)
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

// Design gateway (bridges local state with AGENTESE backend)
export {
  useDesignGateway,
  type OperadInfo,
  type OperadOperationsInfo,
  type UseDesignGatewayOptions,
  type UseDesignGatewayResult,
} from './useDesignGateway';

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

// Emergence visualization hooks
export { useCymatics, type UseCymaticsOptions, type UseCymaticsReturn } from './useCymatics';

export {
  useGrowthAnimation,
  type GrowthAnimationOptions,
  type UseGrowthAnimationReturn,
} from './useGrowthAnimation';

// Teaching mode (Phase 4: Teaching Layer)
export {
  useTeachingMode,
  useTeachingModeContext,
  useTeachingModeSafe,
  TeachingModeProvider,
  TeachingToggle,
  WhenTeaching,
  WhenNotTeaching,
  type TeachingModeState,
  type TeachingModeProviderProps,
  type TeachingToggleProps,
} from './useTeachingMode';
