/**
 * Barrel exports for React hooks.
 *
 * Import hooks from this module for cleaner imports:
 * ```ts
 * import { useAsyncState, useTownStreamWidget, useOnlineStatus } from '@/hooks';
 * ```
 */

// Async state management
export { useAsyncState, type AsyncState, type AsyncStatus, type UseAsyncStateOptions, type UseAsyncStateReturn } from './useAsyncState';

// SSE streaming hooks
export { useTownStreamWidget, type UseTownStreamWidgetOptions, type UseTownStreamWidgetResult } from './useTownStreamWidget';
export { useWorkshopStream, useReconnectingWorkshopStream } from './useWorkshopStream';
export { useNPhaseStream, useNPhaseFromDashboard, INITIAL_NPHASE_STATE, type UseNPhaseStreamOptions, type UseNPhaseStreamResult } from './useNPhaseStream';

// Performance optimization
export { useBatchedEvents } from './useBatchedEvents';

// Session hooks
export { useInhabitSession, type InhabitStatus, type InhabitResponse } from './useInhabitSession';

// Historical replay
export { useHistoricalMode, type HistoryMode, type HistoricalState, type HistoricalActions, type UseHistoricalModeOptions } from './useHistoricalMode';

// Layout and responsiveness
export { useLayoutContext, useLayoutMeasure, useWindowLayout, LayoutContextProvider, DEFAULT_LAYOUT_CONTEXT } from './useLayoutContext';

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
