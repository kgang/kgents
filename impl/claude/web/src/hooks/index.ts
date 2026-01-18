/**
 * Hooks — SEVERE STARK
 *
 * Essential hooks for the unified workspace.
 */

// Layout and responsiveness
export {
  useLayoutContext,
  useLayoutMeasure,
  useWindowLayout,
  DEFAULT_LAYOUT_CONTEXT,
} from './useLayoutContext';

// Garden lifecycle state (A4: No-Shipping)
export { useGardenState } from './useGardenState';

// Collapse verification state (A2: Sloppification)
export { useCollapseState } from './useCollapseState';

// Real-time SSE stream
export { useRealtimeStream } from './useRealtimeStream';

// Keyboard shortcuts (Kent's Decision #6)
export { useKeyboardShortcuts } from './useKeyboardShortcuts';
