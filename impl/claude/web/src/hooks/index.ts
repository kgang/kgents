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

// Witness streaming (SSE connection for witness events)
export {
  useWitnessStream,
  type WitnessEvent,
  type WitnessEventType,
  type SemanticDelta,
  type UseWitnessStream,
} from './useWitnessStream';

// Document Director hook
export { useDirector, type UseDirectorOptions, type UseDirectorResult } from './useDirector';

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

// Galois loss signatures (loss-native frontend)
export {
  useLoss,
  useLossBatch,
  lossToHue,
  lossToColor,
  type LossSignature,
  type LossComponents,
  type UseLossResult,
} from './useLoss';

// Telescope navigation (unified focal distance navigation)
export {
  useTelescope,
  useTelescopeState,
  TelescopeProvider,
  focalDistanceToLayers,
  layerToFocalDistance,
  getLayerName,
  getLayerIcon,
  type TelescopeState,
  type TelescopeAction,
  type TelescopeContextValue,
} from './useTelescopeState';

// Workspace sidebar state (three-panel layout)
export { useSidebarState, type SidebarState, type UseSidebarStateReturn } from './useSidebarState';

// Unified witness hook (Witness Architecture)
export {
  useWitness,
  extractActionType,
  formatMark,
  type WitnessDomain,
  type NavigationAction,
  type PortalAction,
  type ChatAction,
  type DomainMark,
  type WitnessOptions,
} from './useWitness';

// Mode system (six-mode editing for hypergraph)
export { useMode, type UseModeReturn } from './useMode';

// Route-aware mode reset (reset to NORMAL on navigation)
export { useRouteAwareModeReset } from './useRouteAwareModeReset';

// Contradiction detection for K-Blocks
export {
  useItemContradictions,
  getSeverityLevel,
  getOtherKBlock,
  type ContradictionPair,
  type ContradictionKBlockSummary,
  type UseItemContradictionsResult,
} from './useItemContradictions';

// Command Palette (Ctrl+K universal gateway)
export {
  useCommandPalette,
  type Command,
  type CommandCategory,
  type CommandPaletteState,
  type UseCommandPaletteOptions,
  type UseCommandPaletteReturn,
} from './useCommandPalette';

// Derivation Navigation (Constitutional graph traversal)
export {
  useDerivationNavigation,
  type DerivationNode,
  type DerivationLink,
  type DerivationSibling,
  type DerivationNavigationResult,
} from './useDerivationNavigation';
