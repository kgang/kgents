/**
 * useViewport — Pan/Zoom state management
 *
 * Handles viewport transformations for the Astronomical Chart:
 * - Mouse wheel zoom (centered on cursor)
 * - Click-drag pan
 * - Keyboard shortcuts (+ / - for zoom, arrows for pan)
 * - Smooth animations via requestAnimationFrame
 *
 * "The file is a lie. There is only the graph."
 */

import { useState, useCallback, useRef, useEffect } from 'react';

// =============================================================================
// Types
// =============================================================================

export interface ViewportState {
  /** Pan offset X (world coordinates) */
  x: number;
  /** Pan offset Y (world coordinates) */
  y: number;
  /** Zoom scale (1.0 = 100%) */
  scale: number;
}

export interface ViewportBounds {
  minX: number;
  maxX: number;
  minY: number;
  maxY: number;
}

export interface ViewportOptions {
  /** Minimum zoom level */
  minScale?: number;
  /** Maximum zoom level */
  maxScale?: number;
  /** Zoom sensitivity (multiplier per wheel tick) */
  zoomSensitivity?: number;
  /** Initial viewport state */
  initial?: Partial<ViewportState>;
}

export interface ViewportActions {
  /** Set absolute position */
  setPosition: (x: number, y: number) => void;
  /** Pan by delta */
  pan: (dx: number, dy: number) => void;
  /** Set absolute scale */
  setScale: (scale: number) => void;
  /** Zoom by delta (centered) */
  zoom: (delta: number, centerX?: number, centerY?: number) => void;
  /** Reset to initial state */
  reset: () => void;
  /** Fit bounds into view */
  fitBounds: (bounds: ViewportBounds, padding?: number) => void;
}

export interface ViewportReturn {
  state: ViewportState;
  actions: ViewportActions;
  /** Bind to canvas element for event handling */
  bind: {
    onWheel: (e: WheelEvent) => void;
    onMouseDown: (e: MouseEvent) => void;
    onMouseMove: (e: MouseEvent) => void;
    onMouseUp: (e: MouseEvent) => void;
    onMouseLeave: (e: MouseEvent) => void;
  };
}

// =============================================================================
// Constants
// =============================================================================

const DEFAULT_MIN_SCALE = 0.05;
const DEFAULT_MAX_SCALE = 5.0;
const DEFAULT_ZOOM_SENSITIVITY = 0.001;

const DEFAULT_STATE: ViewportState = {
  x: 0,
  y: 0,
  scale: 1.0,
};

// =============================================================================
// Hook
// =============================================================================

export function useViewport(options: ViewportOptions = {}): ViewportReturn {
  const {
    minScale = DEFAULT_MIN_SCALE,
    maxScale = DEFAULT_MAX_SCALE,
    zoomSensitivity = DEFAULT_ZOOM_SENSITIVITY,
    initial = {},
  } = options;

  const initialState: ViewportState = { ...DEFAULT_STATE, ...initial };

  // State
  const [state, setState] = useState<ViewportState>(initialState);

  // Drag state (not in React state for performance)
  const isDragging = useRef(false);
  const dragStart = useRef({ x: 0, y: 0 });
  const dragStartViewport = useRef({ x: 0, y: 0 });

  // Clamp scale to bounds
  const clampScale = useCallback(
    (scale: number) => Math.min(maxScale, Math.max(minScale, scale)),
    [minScale, maxScale]
  );

  // Actions
  const setPosition = useCallback((x: number, y: number) => {
    setState((prev) => ({ ...prev, x, y }));
  }, []);

  const pan = useCallback((dx: number, dy: number) => {
    setState((prev) => ({
      ...prev,
      x: prev.x + dx,
      y: prev.y + dy,
    }));
  }, []);

  const setScale = useCallback(
    (scale: number) => {
      setState((prev) => ({ ...prev, scale: clampScale(scale) }));
    },
    [clampScale]
  );

  const zoom = useCallback(
    (delta: number, centerX?: number, centerY?: number) => {
      setState((prev) => {
        const newScale = clampScale(prev.scale * (1 + delta));

        // If center point provided, adjust position to zoom toward it
        if (centerX !== undefined && centerY !== undefined) {
          const scaleFactor = newScale / prev.scale;
          const newX = centerX - (centerX - prev.x) * scaleFactor;
          const newY = centerY - (centerY - prev.y) * scaleFactor;
          return { x: newX, y: newY, scale: newScale };
        }

        return { ...prev, scale: newScale };
      });
    },
    [clampScale]
  );

  const reset = useCallback(() => {
    setState(initialState);
  }, [initialState]);

  const fitBounds = useCallback(
    (bounds: ViewportBounds, _padding: number = 50) => {
      // Calculate scale to fit (assuming we have viewport dimensions)
      // For now, just center on the bounds
      const centerX = (bounds.minX + bounds.maxX) / 2;
      const centerY = (bounds.minY + bounds.maxY) / 2;

      setState({
        x: -centerX,
        y: -centerY,
        scale: clampScale(1.0), // Could calculate based on viewport size
      });
    },
    [clampScale]
  );

  // Event handlers
  const onWheel = useCallback(
    (e: WheelEvent) => {
      e.preventDefault();

      // Calculate zoom delta from wheel
      const delta = -e.deltaY * zoomSensitivity;

      // Get cursor position relative to canvas
      const rect = (e.currentTarget as HTMLElement).getBoundingClientRect();
      const centerX = e.clientX - rect.left - rect.width / 2;
      const centerY = e.clientY - rect.top - rect.height / 2;

      zoom(delta, centerX, centerY);
    },
    [zoom, zoomSensitivity]
  );

  const onMouseDown = useCallback(
    (e: MouseEvent) => {
      // Only pan with left mouse button or middle button
      if (e.button !== 0 && e.button !== 1) return;

      isDragging.current = true;
      dragStart.current = { x: e.clientX, y: e.clientY };
      dragStartViewport.current = { x: state.x, y: state.y };

      // Change cursor
      (e.currentTarget as HTMLElement).style.cursor = 'grabbing';
    },
    [state.x, state.y]
  );

  const onMouseMove = useCallback(
    (e: MouseEvent) => {
      if (!isDragging.current) return;

      const dx = (e.clientX - dragStart.current.x) / state.scale;
      const dy = (e.clientY - dragStart.current.y) / state.scale;

      setState({
        ...state,
        x: dragStartViewport.current.x + dx,
        y: dragStartViewport.current.y + dy,
      });
    },
    [state]
  );

  const onMouseUp = useCallback((e: MouseEvent) => {
    isDragging.current = false;
    (e.currentTarget as HTMLElement).style.cursor = 'grab';
  }, []);

  const onMouseLeave = useCallback((e: MouseEvent) => {
    isDragging.current = false;
    (e.currentTarget as HTMLElement).style.cursor = 'grab';
  }, []);

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Don't handle if focus is on input
      if (e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement) {
        return;
      }

      switch (e.key) {
        case '+':
        case '=':
          e.preventDefault();
          zoom(0.1);
          break;
        case '-':
          e.preventDefault();
          zoom(-0.1);
          break;
        case '0':
          e.preventDefault();
          reset();
          break;
        case 'ArrowUp':
          e.preventDefault();
          pan(0, 50 / state.scale);
          break;
        case 'ArrowDown':
          e.preventDefault();
          pan(0, -50 / state.scale);
          break;
        case 'ArrowLeft':
          e.preventDefault();
          pan(50 / state.scale, 0);
          break;
        case 'ArrowRight':
          e.preventDefault();
          pan(-50 / state.scale, 0);
          break;
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [zoom, pan, reset, state.scale]);

  return {
    state,
    actions: {
      setPosition,
      pan,
      setScale,
      zoom,
      reset,
      fitBounds,
    },
    bind: {
      onWheel,
      onMouseDown,
      onMouseMove,
      onMouseUp,
      onMouseLeave,
    },
  };
}

export default useViewport;
