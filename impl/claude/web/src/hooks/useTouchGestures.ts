/**
 * useTouchGestures: Touch gesture support for mobile interactions.
 *
 * Provides hooks for:
 * - Pinch-to-zoom on canvas
 * - Long-press for context menus
 * - Swipe for quick actions
 *
 * @see plans/web-refactor/interaction-patterns.md
 */

import { useRef, useCallback, useEffect, type RefObject } from 'react';

// =============================================================================
// Types
// =============================================================================

export interface PinchState {
  /** Whether pinch is active */
  isPinching: boolean;

  /** Current scale factor (1 = normal) */
  scale: number;

  /** Center point of pinch */
  center: { x: number; y: number };

  /** Initial distance between touches */
  initialDistance: number;
}

export interface LongPressState {
  /** Whether long press is in progress */
  isPressing: boolean;

  /** Progress percentage (0-100) */
  progress: number;

  /** Position of long press */
  position: { x: number; y: number } | null;
}

export interface SwipeState {
  /** Whether swipe is active */
  isSwiping: boolean;

  /** Swipe direction */
  direction: 'left' | 'right' | 'up' | 'down' | null;

  /** Swipe distance in pixels */
  distance: number;

  /** Swipe velocity (px/ms) */
  velocity: number;
}

export interface UsePinchZoomOptions {
  /** Minimum scale */
  minScale?: number;

  /** Maximum scale */
  maxScale?: number;

  /** Called when scale changes */
  onScaleChange?: (scale: number, center: { x: number; y: number }) => void;

  /** Called when pinch starts */
  onPinchStart?: () => void;

  /** Called when pinch ends */
  onPinchEnd?: (finalScale: number) => void;
}

export interface UseLongPressOptions {
  /** Duration in ms before long press triggers (default: 500) */
  duration?: number;

  /** Called when long press completes */
  onLongPress?: (position: { x: number; y: number }) => void;

  /** Called when long press starts */
  onStart?: () => void;

  /** Called when long press is cancelled */
  onCancel?: () => void;
}

export interface UseSwipeOptions {
  /** Minimum distance to trigger swipe (default: 50) */
  threshold?: number;

  /** Direction(s) to detect (default: all) */
  directions?: ('left' | 'right' | 'up' | 'down')[];

  /** Called when swipe is detected */
  onSwipe?: (direction: SwipeState['direction'], distance: number) => void;

  /** Called during swipe (for visual feedback) */
  onSwiping?: (state: SwipeState) => void;
}

// =============================================================================
// Pinch-to-Zoom Hook
// =============================================================================

export function usePinchZoom(
  ref: RefObject<HTMLElement | null>,
  options: UsePinchZoomOptions = {}
): PinchState {
  const {
    minScale = 0.5,
    maxScale = 3,
    onScaleChange,
    onPinchStart,
    onPinchEnd,
  } = options;

  const stateRef = useRef<PinchState>({
    isPinching: false,
    scale: 1,
    center: { x: 0, y: 0 },
    initialDistance: 0,
  });

  const initialScaleRef = useRef(1);

  // Calculate distance between two touch points
  const getDistance = useCallback((t1: Touch, t2: Touch): number => {
    const dx = t1.clientX - t2.clientX;
    const dy = t1.clientY - t2.clientY;
    return Math.sqrt(dx * dx + dy * dy);
  }, []);

  // Get center point between two touches
  const getCenter = useCallback((t1: Touch, t2: Touch): { x: number; y: number } => {
    return {
      x: (t1.clientX + t2.clientX) / 2,
      y: (t1.clientY + t2.clientY) / 2,
    };
  }, []);

  useEffect(() => {
    const element = ref.current;
    if (!element) return;

    const handleTouchStart = (e: TouchEvent) => {
      if (e.touches.length === 2) {
        e.preventDefault();
        const [t1, t2] = [e.touches[0], e.touches[1]];

        stateRef.current = {
          isPinching: true,
          scale: stateRef.current.scale,
          center: getCenter(t1, t2),
          initialDistance: getDistance(t1, t2),
        };

        initialScaleRef.current = stateRef.current.scale;
        element.classList.add('pinch-zooming');
        onPinchStart?.();
      }
    };

    const handleTouchMove = (e: TouchEvent) => {
      if (e.touches.length === 2 && stateRef.current.isPinching) {
        e.preventDefault();
        const [t1, t2] = [e.touches[0], e.touches[1]];

        const currentDistance = getDistance(t1, t2);
        const scaleChange = currentDistance / stateRef.current.initialDistance;
        const newScale = Math.min(maxScale, Math.max(minScale, initialScaleRef.current * scaleChange));
        const center = getCenter(t1, t2);

        stateRef.current = {
          ...stateRef.current,
          scale: newScale,
          center,
        };

        onScaleChange?.(newScale, center);
      }
    };

    const handleTouchEnd = () => {
      if (stateRef.current.isPinching) {
        stateRef.current = {
          ...stateRef.current,
          isPinching: false,
        };
        element.classList.remove('pinch-zooming');
        onPinchEnd?.(stateRef.current.scale);
      }
    };

    element.addEventListener('touchstart', handleTouchStart, { passive: false });
    element.addEventListener('touchmove', handleTouchMove, { passive: false });
    element.addEventListener('touchend', handleTouchEnd);
    element.addEventListener('touchcancel', handleTouchEnd);

    return () => {
      element.removeEventListener('touchstart', handleTouchStart);
      element.removeEventListener('touchmove', handleTouchMove);
      element.removeEventListener('touchend', handleTouchEnd);
      element.removeEventListener('touchcancel', handleTouchEnd);
    };
  }, [ref, minScale, maxScale, onScaleChange, onPinchStart, onPinchEnd, getDistance, getCenter]);

  return stateRef.current;
}

// =============================================================================
// Long-Press Hook
// =============================================================================

export function useLongPress(
  ref: RefObject<HTMLElement | null>,
  options: UseLongPressOptions = {}
): LongPressState {
  const {
    duration = 500,
    onLongPress,
    onStart,
    onCancel,
  } = options;

  const stateRef = useRef<LongPressState>({
    isPressing: false,
    progress: 0,
    position: null,
  });

  const timerRef = useRef<NodeJS.Timeout | null>(null);
  const progressRef = useRef<NodeJS.Timeout | null>(null);
  const startTimeRef = useRef<number>(0);

  useEffect(() => {
    const element = ref.current;
    if (!element) return;

    const clearTimers = () => {
      if (timerRef.current) {
        clearTimeout(timerRef.current);
        timerRef.current = null;
      }
      if (progressRef.current) {
        clearInterval(progressRef.current);
        progressRef.current = null;
      }
    };

    const handleStart = (e: TouchEvent | MouseEvent) => {
      // Get position
      const clientX = 'touches' in e ? e.touches[0].clientX : e.clientX;
      const clientY = 'touches' in e ? e.touches[0].clientY : e.clientY;

      stateRef.current = {
        isPressing: true,
        progress: 0,
        position: { x: clientX, y: clientY },
      };

      startTimeRef.current = Date.now();
      element.classList.add('pressing');
      onStart?.();

      // Update progress every 16ms (~60fps)
      progressRef.current = setInterval(() => {
        const elapsed = Date.now() - startTimeRef.current;
        const progress = Math.min(100, (elapsed / duration) * 100);
        stateRef.current.progress = progress;
        element.style.setProperty('--long-press-progress', `${progress}%`);
      }, 16);

      // Trigger long press after duration
      timerRef.current = setTimeout(() => {
        clearTimers();
        element.classList.remove('pressing');
        onLongPress?.(stateRef.current.position!);
        stateRef.current = {
          isPressing: false,
          progress: 0,
          position: null,
        };
      }, duration);
    };

    const handleEnd = () => {
      if (stateRef.current.isPressing) {
        clearTimers();
        element.classList.remove('pressing');
        element.style.setProperty('--long-press-progress', '0%');
        onCancel?.();
        stateRef.current = {
          isPressing: false,
          progress: 0,
          position: null,
        };
      }
    };

    const handleMove = (e: TouchEvent | MouseEvent) => {
      if (stateRef.current.isPressing && stateRef.current.position) {
        const clientX = 'touches' in e ? e.touches[0].clientX : e.clientX;
        const clientY = 'touches' in e ? e.touches[0].clientY : e.clientY;

        // Cancel if moved too far (10px threshold)
        const dx = clientX - stateRef.current.position.x;
        const dy = clientY - stateRef.current.position.y;
        if (Math.sqrt(dx * dx + dy * dy) > 10) {
          handleEnd();
        }
      }
    };

    // Touch events
    element.addEventListener('touchstart', handleStart, { passive: true });
    element.addEventListener('touchend', handleEnd);
    element.addEventListener('touchcancel', handleEnd);
    element.addEventListener('touchmove', handleMove, { passive: true });

    // Mouse events (for testing on desktop)
    element.addEventListener('mousedown', handleStart);
    element.addEventListener('mouseup', handleEnd);
    element.addEventListener('mouseleave', handleEnd);
    element.addEventListener('mousemove', handleMove);

    return () => {
      clearTimers();
      element.removeEventListener('touchstart', handleStart);
      element.removeEventListener('touchend', handleEnd);
      element.removeEventListener('touchcancel', handleEnd);
      element.removeEventListener('touchmove', handleMove);
      element.removeEventListener('mousedown', handleStart);
      element.removeEventListener('mouseup', handleEnd);
      element.removeEventListener('mouseleave', handleEnd);
      element.removeEventListener('mousemove', handleMove);
    };
  }, [ref, duration, onLongPress, onStart, onCancel]);

  return stateRef.current;
}

// =============================================================================
// Swipe Hook
// =============================================================================

export function useSwipe(
  ref: RefObject<HTMLElement | null>,
  options: UseSwipeOptions = {}
): SwipeState {
  const {
    threshold = 50,
    directions = ['left', 'right', 'up', 'down'],
    onSwipe,
    onSwiping,
  } = options;

  const stateRef = useRef<SwipeState>({
    isSwiping: false,
    direction: null,
    distance: 0,
    velocity: 0,
  });

  const startRef = useRef<{ x: number; y: number; time: number } | null>(null);

  useEffect(() => {
    const element = ref.current;
    if (!element) return;

    const handleTouchStart = (e: TouchEvent) => {
      const touch = e.touches[0];
      startRef.current = {
        x: touch.clientX,
        y: touch.clientY,
        time: Date.now(),
      };
      stateRef.current = {
        isSwiping: true,
        direction: null,
        distance: 0,
        velocity: 0,
      };
    };

    const handleTouchMove = (e: TouchEvent) => {
      if (!startRef.current) return;

      const touch = e.touches[0];
      const dx = touch.clientX - startRef.current.x;
      const dy = touch.clientY - startRef.current.y;
      const elapsed = Date.now() - startRef.current.time;

      const absDx = Math.abs(dx);
      const absDy = Math.abs(dy);
      const distance = Math.sqrt(dx * dx + dy * dy);
      const velocity = elapsed > 0 ? distance / elapsed : 0;

      // Determine direction
      let direction: SwipeState['direction'] = null;
      if (absDx > absDy) {
        direction = dx > 0 ? 'right' : 'left';
      } else {
        direction = dy > 0 ? 'down' : 'up';
      }

      stateRef.current = {
        isSwiping: true,
        direction,
        distance,
        velocity,
      };

      onSwiping?.(stateRef.current);
    };

    const handleTouchEnd = () => {
      if (!startRef.current) return;

      const { direction, distance, velocity } = stateRef.current;

      // Check if swipe meets threshold and is in allowed directions
      if (distance >= threshold && direction && directions.includes(direction)) {
        onSwipe?.(direction, distance);
      }

      // Reset
      startRef.current = null;
      stateRef.current = {
        isSwiping: false,
        direction: null,
        distance: 0,
        velocity,
      };
    };

    element.addEventListener('touchstart', handleTouchStart, { passive: true });
    element.addEventListener('touchmove', handleTouchMove, { passive: true });
    element.addEventListener('touchend', handleTouchEnd);
    element.addEventListener('touchcancel', handleTouchEnd);

    return () => {
      element.removeEventListener('touchstart', handleTouchStart);
      element.removeEventListener('touchmove', handleTouchMove);
      element.removeEventListener('touchend', handleTouchEnd);
      element.removeEventListener('touchcancel', handleTouchEnd);
    };
  }, [ref, threshold, directions, onSwipe, onSwiping]);

  return stateRef.current;
}

// =============================================================================
// Combined Hook (Convenience)
// =============================================================================

export interface UseTouchGesturesOptions {
  pinch?: UsePinchZoomOptions;
  longPress?: UseLongPressOptions;
  swipe?: UseSwipeOptions;
}

export interface TouchGesturesState {
  pinch: PinchState;
  longPress: LongPressState;
  swipe: SwipeState;
}

/**
 * Combined touch gesture hook for convenience.
 * Enable only what you need by passing options.
 */
export function useTouchGestures(
  ref: RefObject<HTMLElement | null>,
  options: UseTouchGesturesOptions = {}
): TouchGesturesState {
  const pinch = usePinchZoom(ref, options.pinch);
  const longPress = useLongPress(ref, options.longPress);
  const swipe = useSwipe(ref, options.swipe);

  return { pinch, longPress, swipe };
}

export default useTouchGestures;
