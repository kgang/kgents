/**
 * useTouch - Touch device detection and gesture handling for 3D primitives
 *
 * Provides:
 * 1. Touch device detection
 * 2. Tap vs drag disambiguation
 * 3. Touch target size calculations
 *
 * Philosophy:
 *   "Accessibility is not an afterthought—it's a constitutional right."
 *
 * @see plans/3d-projection-consolidation.md
 */

import { useRef, useCallback, useState, useEffect } from 'react';

// =============================================================================
// Types
// =============================================================================

/**
 * Touch configuration.
 */
export interface TouchConfig {
  /** Minimum touch target size in pixels (default 48 per WCAG) */
  minTouchTargetPx: number;
  /** Maximum distance (in pixels) for tap vs drag disambiguation */
  tapThresholdPx: number;
  /** Maximum duration (in ms) for tap vs long press */
  tapDurationMs: number;
}

/**
 * Gesture result from useGesture.
 */
export interface GestureResult {
  /** Whether this was a tap (not a drag) */
  isTap: boolean;
  /** Whether this was a long press */
  isLongPress: boolean;
  /** Total distance moved during gesture */
  distance: number;
  /** Duration of gesture in ms */
  duration: number;
}

// =============================================================================
// Default Config
// =============================================================================

const DEFAULT_TOUCH_CONFIG: TouchConfig = {
  minTouchTargetPx: 48, // WCAG 2.1 Level AAA recommends 44px, we use 48
  tapThresholdPx: 10,   // Movement under 10px = tap
  tapDurationMs: 300,   // Under 300ms = tap, over = long press
};

// =============================================================================
// Touch Detection Hook
// =============================================================================

/**
 * Detect if the current device has touch capability.
 *
 * Usage:
 * ```tsx
 * const { isTouchDevice, isHybrid } = useTouchDevice();
 * <TopologyNode3D isTouchDevice={isTouchDevice} ... />
 * ```
 */
export function useTouchDevice() {
  const [isTouchDevice, setIsTouchDevice] = useState(false);
  const [isHybrid, setIsHybrid] = useState(false);

  useEffect(() => {
    if (typeof window === 'undefined') return;

    // Check for touch capability
    const hasTouch =
      'ontouchstart' in window ||
      navigator.maxTouchPoints > 0 ||
      // @ts-expect-error - msMaxTouchPoints is IE-specific
      navigator.msMaxTouchPoints > 0;

    // Check for pointer (mouse) capability
    const hasMouse = window.matchMedia('(pointer: fine)').matches;

    setIsTouchDevice(hasTouch);
    setIsHybrid(hasTouch && hasMouse); // Has both touch and precise pointer

    // Listen for first touch to enable touch mode
    const enableTouch = () => {
      setIsTouchDevice(true);
      window.removeEventListener('touchstart', enableTouch);
    };
    window.addEventListener('touchstart', enableTouch, { once: true });

    return () => {
      window.removeEventListener('touchstart', enableTouch);
    };
  }, []);

  return { isTouchDevice, isHybrid };
}

// =============================================================================
// Touch Target Size Hook
// =============================================================================

/**
 * Calculate touch target multiplier based on current node size and viewport.
 *
 * Ensures touch targets are at least minTouchTargetPx equivalent.
 *
 * @param nodeSize - Current node size in 3D units
 * @param cameraFov - Camera field of view in degrees
 * @param cameraDistance - Distance from camera to nodes
 * @param config - Touch configuration
 */
export function useTouchTargetMultiplier(
  nodeSize: number,
  cameraFov: number = 75,
  cameraDistance: number = 10,
  config: Partial<TouchConfig> = {}
) {
  const { minTouchTargetPx = DEFAULT_TOUCH_CONFIG.minTouchTargetPx } = config;

  // Calculate approximate pixels per 3D unit at this camera distance
  // This is a rough approximation assuming standard viewport height
  const viewportHeight = typeof window !== 'undefined' ? window.innerHeight : 800;
  const fovRadians = (cameraFov * Math.PI) / 180;
  const visibleHeightAtDistance = 2 * cameraDistance * Math.tan(fovRadians / 2);
  const pixelsPerUnit = viewportHeight / visibleHeightAtDistance;

  // Calculate how many pixels the node currently occupies
  const currentNodePx = nodeSize * pixelsPerUnit;

  // Calculate multiplier needed to reach minimum touch target
  if (currentNodePx >= minTouchTargetPx) {
    return 1.0; // Already big enough
  }

  return minTouchTargetPx / currentNodePx;
}

// =============================================================================
// Gesture Recognition Hook
// =============================================================================

interface GestureState {
  startX: number;
  startY: number;
  startTime: number;
}

/**
 * Recognize tap vs drag gestures.
 *
 * Usage:
 * ```tsx
 * const { onPointerDown, onPointerUp, onPointerMove } = useGesture({
 *   onTap: () => console.log('Tapped!'),
 *   onLongPress: () => console.log('Long pressed!'),
 * });
 * ```
 */
export function useGesture(
  callbacks: {
    onTap?: () => void;
    onLongPress?: () => void;
    onDrag?: (dx: number, dy: number) => void;
  },
  config: Partial<TouchConfig> = {}
) {
  const mergedConfig = { ...DEFAULT_TOUCH_CONFIG, ...config };
  const gestureRef = useRef<GestureState | null>(null);
  const longPressTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const [isDragging, setIsDragging] = useState(false);

  const cancelLongPress = useCallback(() => {
    if (longPressTimeoutRef.current) {
      clearTimeout(longPressTimeoutRef.current);
      longPressTimeoutRef.current = null;
    }
  }, []);

  const onPointerDown = useCallback(
    (e: { clientX: number; clientY: number }) => {
      gestureRef.current = {
        startX: e.clientX,
        startY: e.clientY,
        startTime: Date.now(),
      };
      setIsDragging(false);

      // Set up long press detection
      if (callbacks.onLongPress) {
        longPressTimeoutRef.current = setTimeout(() => {
          if (gestureRef.current) {
            callbacks.onLongPress?.();
            gestureRef.current = null; // Consume the gesture
          }
        }, mergedConfig.tapDurationMs * 2); // Long press = 2x tap duration
      }
    },
    [callbacks, mergedConfig.tapDurationMs]
  );

  const onPointerMove = useCallback(
    (e: { clientX: number; clientY: number }) => {
      if (!gestureRef.current) return;

      const dx = e.clientX - gestureRef.current.startX;
      const dy = e.clientY - gestureRef.current.startY;
      const distance = Math.sqrt(dx * dx + dy * dy);

      // If moved beyond tap threshold, it's a drag
      if (distance > mergedConfig.tapThresholdPx) {
        setIsDragging(true);
        cancelLongPress();
        callbacks.onDrag?.(dx, dy);
      }
    },
    [callbacks, mergedConfig.tapThresholdPx, cancelLongPress]
  );

  const onPointerUp = useCallback(
    (e: { clientX: number; clientY: number }) => {
      cancelLongPress();

      if (!gestureRef.current) return;

      const dx = e.clientX - gestureRef.current.startX;
      const dy = e.clientY - gestureRef.current.startY;
      const distance = Math.sqrt(dx * dx + dy * dy);
      const duration = Date.now() - gestureRef.current.startTime;

      // Determine gesture type
      const isTap = distance < mergedConfig.tapThresholdPx && duration < mergedConfig.tapDurationMs;

      if (isTap) {
        callbacks.onTap?.();
      }

      gestureRef.current = null;
      setIsDragging(false);
    },
    [callbacks, mergedConfig.tapThresholdPx, mergedConfig.tapDurationMs, cancelLongPress]
  );

  // Cleanup on unmount
  useEffect(() => {
    return () => cancelLongPress();
  }, [cancelLongPress]);

  return {
    onPointerDown,
    onPointerMove,
    onPointerUp,
    isDragging,
  };
}

// =============================================================================
// Combined Export
// =============================================================================

export const TOUCH_DEFAULTS = DEFAULT_TOUCH_CONFIG;

export default useTouchDevice;
