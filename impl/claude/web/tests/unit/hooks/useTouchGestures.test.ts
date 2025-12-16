/**
 * Tests for useTouchGestures hook interfaces.
 *
 * Touch gesture support for mobile interactions:
 * - Pinch-to-zoom
 * - Long-press for context menus
 * - Swipe for quick actions
 *
 * Note: JSDOM has limited TouchEvent support. These tests verify the hook
 * interfaces and return types rather than full gesture simulation.
 * Integration testing with real touch events should be done in E2E tests.
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import type { RefObject } from 'react';

// =============================================================================
// Test Setup - We test the hook interfaces without actual touch events
// =============================================================================

// Since JSDOM doesn't support TouchEvent, we'll test the hook's interface
// by importing the real hooks and verifying their return shapes

describe('useTouchGestures hooks', () => {
  let element: HTMLDivElement;
  let ref: RefObject<HTMLDivElement>;

  beforeEach(() => {
    element = document.createElement('div');
    document.body.appendChild(element);
    ref = { current: element };
  });

  afterEach(() => {
    document.body.removeChild(element);
    vi.restoreAllMocks();
  });

  // ===========================================================================
  // usePinchZoom Interface Tests
  // ===========================================================================

  describe('usePinchZoom', () => {
    // Import dynamically to test actual implementation
    it('returns expected interface shape', async () => {
      const { usePinchZoom } = await import('@/hooks/useTouchGestures');
      const { result } = renderHook(() => usePinchZoom(ref));

      // Verify return type has expected properties
      expect(result.current).toHaveProperty('scale');
      expect(result.current).toHaveProperty('isPinching');
      expect(typeof result.current.scale).toBe('number');
      expect(typeof result.current.isPinching).toBe('boolean');
    });

    it('initializes with scale=1 and isPinching=false', async () => {
      const { usePinchZoom } = await import('@/hooks/useTouchGestures');
      const { result } = renderHook(() => usePinchZoom(ref));

      expect(result.current.scale).toBe(1);
      expect(result.current.isPinching).toBe(false);
    });

    it('accepts options with callbacks', async () => {
      const { usePinchZoom } = await import('@/hooks/useTouchGestures');
      const onPinchStart = vi.fn();
      const onPinchEnd = vi.fn();
      const onScaleChange = vi.fn();

      // Should not throw when callbacks are provided
      expect(() => {
        renderHook(() =>
          usePinchZoom(ref, {
            onPinchStart,
            onPinchEnd,
            onScaleChange,
            minScale: 0.5,
            maxScale: 3,
          })
        );
      }).not.toThrow();
    });

    it('handles null ref gracefully', async () => {
      const { usePinchZoom } = await import('@/hooks/useTouchGestures');
      const nullRef = { current: null };

      expect(() => {
        renderHook(() => usePinchZoom(nullRef));
      }).not.toThrow();
    });
  });

  // ===========================================================================
  // useLongPress Interface Tests
  // ===========================================================================

  describe('useLongPress', () => {
    beforeEach(() => {
      vi.useFakeTimers();
    });

    afterEach(() => {
      vi.useRealTimers();
    });

    it('returns expected interface shape', async () => {
      const { useLongPress } = await import('@/hooks/useTouchGestures');
      const { result } = renderHook(() => useLongPress(ref));

      expect(result.current).toHaveProperty('isPressing');
      expect(result.current).toHaveProperty('progress');
      expect(result.current).toHaveProperty('position');
      expect(typeof result.current.isPressing).toBe('boolean');
      expect(typeof result.current.progress).toBe('number');
    });

    it('initializes with expected default state', async () => {
      const { useLongPress } = await import('@/hooks/useTouchGestures');
      const { result } = renderHook(() => useLongPress(ref));

      expect(result.current.isPressing).toBe(false);
      expect(result.current.progress).toBe(0);
      expect(result.current.position).toBeNull();
    });

    it('accepts duration and callback options', async () => {
      const { useLongPress } = await import('@/hooks/useTouchGestures');
      const onLongPress = vi.fn();
      const onStart = vi.fn();
      const onCancel = vi.fn();

      expect(() => {
        renderHook(() =>
          useLongPress(ref, {
            duration: 800,
            onLongPress,
            onStart,
            onCancel,
          })
        );
      }).not.toThrow();
    });

    it('can detect mouse down as alternative to touch', async () => {
      const { useLongPress } = await import('@/hooks/useTouchGestures');
      const onLongPress = vi.fn();

      renderHook(() =>
        useLongPress(ref, {
          duration: 500,
          onLongPress,
        })
      );

      // Simulate mouse down (works in JSDOM unlike touch events)
      act(() => {
        element.dispatchEvent(
          new MouseEvent('mousedown', {
            clientX: 100,
            clientY: 100,
            bubbles: true,
          })
        );
      });

      // Advance timer to trigger long press
      act(() => {
        vi.advanceTimersByTime(500);
      });

      expect(onLongPress).toHaveBeenCalledWith({ x: 100, y: 100 });
    });

    it('cancels on mouse up before duration', async () => {
      const { useLongPress } = await import('@/hooks/useTouchGestures');
      const onLongPress = vi.fn();
      const onCancel = vi.fn();

      renderHook(() =>
        useLongPress(ref, {
          duration: 500,
          onLongPress,
          onCancel,
        })
      );

      act(() => {
        element.dispatchEvent(
          new MouseEvent('mousedown', {
            clientX: 100,
            clientY: 100,
            bubbles: true,
          })
        );
      });

      act(() => {
        vi.advanceTimersByTime(200);
      });

      act(() => {
        element.dispatchEvent(new MouseEvent('mouseup', { bubbles: true }));
      });

      expect(onLongPress).not.toHaveBeenCalled();
      expect(onCancel).toHaveBeenCalled();
    });
  });

  // ===========================================================================
  // useSwipe Interface Tests
  // ===========================================================================

  describe('useSwipe', () => {
    it('returns expected interface shape', async () => {
      const { useSwipe } = await import('@/hooks/useTouchGestures');
      const { result } = renderHook(() => useSwipe(ref));

      expect(result.current).toHaveProperty('isSwiping');
      expect(result.current).toHaveProperty('direction');
      expect(result.current).toHaveProperty('distance');
      expect(typeof result.current.isSwiping).toBe('boolean');
      expect(typeof result.current.distance).toBe('number');
    });

    it('initializes with expected default state', async () => {
      const { useSwipe } = await import('@/hooks/useTouchGestures');
      const { result } = renderHook(() => useSwipe(ref));

      expect(result.current.isSwiping).toBe(false);
      expect(result.current.direction).toBeNull();
      expect(result.current.distance).toBe(0);
    });

    it('accepts threshold and direction options', async () => {
      const { useSwipe } = await import('@/hooks/useTouchGestures');
      const onSwipe = vi.fn();
      const onSwiping = vi.fn();

      expect(() => {
        renderHook(() =>
          useSwipe(ref, {
            threshold: 50,
            directions: ['left', 'right'],
            onSwipe,
            onSwiping,
          })
        );
      }).not.toThrow();
    });
  });

  // ===========================================================================
  // useTouchGestures (Combined) Interface Tests
  // ===========================================================================

  describe('useTouchGestures', () => {
    it('combines all gesture hooks', async () => {
      const { useTouchGestures } = await import('@/hooks/useTouchGestures');
      const { result } = renderHook(() => useTouchGestures(ref));

      expect(result.current).toHaveProperty('pinch');
      expect(result.current).toHaveProperty('longPress');
      expect(result.current).toHaveProperty('swipe');
    });

    it('pinch has expected interface', async () => {
      const { useTouchGestures } = await import('@/hooks/useTouchGestures');
      const { result } = renderHook(() => useTouchGestures(ref));

      expect(result.current.pinch).toHaveProperty('scale');
      expect(result.current.pinch).toHaveProperty('isPinching');
    });

    it('longPress has expected interface', async () => {
      const { useTouchGestures } = await import('@/hooks/useTouchGestures');
      const { result } = renderHook(() => useTouchGestures(ref));

      expect(result.current.longPress).toHaveProperty('isPressing');
      expect(result.current.longPress).toHaveProperty('progress');
      expect(result.current.longPress).toHaveProperty('position');
    });

    it('swipe has expected interface', async () => {
      const { useTouchGestures } = await import('@/hooks/useTouchGestures');
      const { result } = renderHook(() => useTouchGestures(ref));

      expect(result.current.swipe).toHaveProperty('isSwiping');
      expect(result.current.swipe).toHaveProperty('direction');
      expect(result.current.swipe).toHaveProperty('distance');
    });

    it('accepts individual hook options', async () => {
      const { useTouchGestures } = await import('@/hooks/useTouchGestures');

      expect(() => {
        renderHook(() =>
          useTouchGestures(ref, {
            pinch: { minScale: 0.5, maxScale: 3 },
            longPress: { duration: 800 },
            swipe: { threshold: 50, directions: ['left', 'right'] },
          })
        );
      }).not.toThrow();
    });
  });
});
