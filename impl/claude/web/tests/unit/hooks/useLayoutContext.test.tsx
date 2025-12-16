/**
 * Tests for useLayoutContext hook.
 *
 * Responsive layout management:
 * - Context for layout information (width, height, density)
 * - ResizeObserver-based measurements
 * - Window dimension tracking
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import {
  useLayoutContext,
  useLayoutMeasure,
  useWindowLayout,
  LayoutContextProvider,
  DEFAULT_LAYOUT_CONTEXT,
} from '@/hooks/useLayoutContext';

// =============================================================================
// useLayoutContext Tests
// =============================================================================

describe('useLayoutContext', () => {
  describe('default context', () => {
    it('returns default values without provider', () => {
      const { result } = renderHook(() => useLayoutContext());

      expect(result.current).toEqual(DEFAULT_LAYOUT_CONTEXT);
    });

    it('DEFAULT_LAYOUT_CONTEXT has expected shape', () => {
      expect(DEFAULT_LAYOUT_CONTEXT).toHaveProperty('availableWidth');
      expect(DEFAULT_LAYOUT_CONTEXT).toHaveProperty('availableHeight');
      expect(DEFAULT_LAYOUT_CONTEXT).toHaveProperty('depth');
      expect(DEFAULT_LAYOUT_CONTEXT).toHaveProperty('parentLayout');
      expect(DEFAULT_LAYOUT_CONTEXT).toHaveProperty('isConstrained');
      expect(DEFAULT_LAYOUT_CONTEXT).toHaveProperty('density');
    });
  });

  describe('with provider', () => {
    it('provides context values from provider', () => {
      const customContext = {
        ...DEFAULT_LAYOUT_CONTEXT,
        availableWidth: 800,
        density: 'comfortable' as const,
      };

      const { result } = renderHook(() => useLayoutContext(), {
        wrapper: ({ children }) => (
          <LayoutContextProvider.Provider value={customContext}>
            {children}
          </LayoutContextProvider.Provider>
        ),
      });

      expect(result.current.availableWidth).toBe(800);
      expect(result.current.density).toBe('comfortable');
    });
  });
});

// =============================================================================
// useLayoutMeasure Tests
// =============================================================================

describe('useLayoutMeasure', () => {
  let resizeObserverMock: {
    observe: ReturnType<typeof vi.fn>;
    unobserve: ReturnType<typeof vi.fn>;
    disconnect: ReturnType<typeof vi.fn>;
  };

  beforeEach(() => {
    resizeObserverMock = {
      observe: vi.fn(),
      unobserve: vi.fn(),
      disconnect: vi.fn(),
    };

    vi.stubGlobal(
      'ResizeObserver',
      vi.fn().mockImplementation(() => resizeObserverMock)
    );
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it('returns a tuple of [ref, context]', () => {
    const { result } = renderHook(() => useLayoutMeasure());

    expect(Array.isArray(result.current)).toBe(true);
    expect(result.current).toHaveLength(2);
  });

  it('returns a ref as first element', () => {
    const { result } = renderHook(() => useLayoutMeasure());

    const [ref] = result.current;
    expect(ref).toHaveProperty('current');
  });

  it('returns layout context as second element', () => {
    const { result } = renderHook(() => useLayoutMeasure());

    const [, context] = result.current;
    expect(context).toHaveProperty('availableWidth');
    expect(context).toHaveProperty('availableHeight');
    expect(context).toHaveProperty('depth');
    expect(context).toHaveProperty('density');
  });

  it('accepts parentLayout option', () => {
    const { result } = renderHook(() =>
      useLayoutMeasure({ parentLayout: 'grid' })
    );

    const [, context] = result.current;
    expect(context.parentLayout).toBe('grid');
  });

  it('increments depth from parent context', () => {
    const parentContext = { ...DEFAULT_LAYOUT_CONTEXT, depth: 2 };
    const { result } = renderHook(() =>
      useLayoutMeasure({ parentContext })
    );

    const [, context] = result.current;
    expect(context.depth).toBe(3);
  });

  it('cleans up on unmount', () => {
    // Note: ResizeObserver disconnect is called in the useEffect cleanup
    // but since the ref is null in tests, the observer may not be created
    const { unmount } = renderHook(() => useLayoutMeasure());

    // Should not throw on unmount
    expect(() => unmount()).not.toThrow();
  });
});

// =============================================================================
// useWindowLayout Tests
// =============================================================================

describe('useWindowLayout', () => {
  const originalInnerWidth = window.innerWidth;
  const originalInnerHeight = window.innerHeight;

  function setWindowSize(width: number, height: number) {
    Object.defineProperty(window, 'innerWidth', {
      value: width,
      writable: true,
      configurable: true,
    });
    Object.defineProperty(window, 'innerHeight', {
      value: height,
      writable: true,
      configurable: true,
    });
  }

  afterEach(() => {
    setWindowSize(originalInnerWidth, originalInnerHeight);
  });

  describe('window dimensions', () => {
    it('returns current window dimensions', () => {
      setWindowSize(1920, 1080);

      const { result } = renderHook(() => useWindowLayout());

      expect(result.current.width).toBe(1920);
      expect(result.current.height).toBe(1080);
    });

    it('updates on window resize', () => {
      setWindowSize(1920, 1080);

      const { result } = renderHook(() => useWindowLayout());

      expect(result.current.width).toBe(1920);

      act(() => {
        setWindowSize(1024, 768);
        window.dispatchEvent(new Event('resize'));
      });

      expect(result.current.width).toBe(1024);
      expect(result.current.height).toBe(768);
    });
  });

  describe('breakpoint detection', () => {
    it('detects mobile breakpoint (< 640px)', () => {
      setWindowSize(375, 667);

      const { result } = renderHook(() => useWindowLayout());

      expect(result.current.isMobile).toBe(true);
      expect(result.current.isTablet).toBe(false);
      expect(result.current.isDesktop).toBe(false);
    });

    it('detects tablet breakpoint (640-1024px)', () => {
      setWindowSize(768, 1024);

      const { result } = renderHook(() => useWindowLayout());

      expect(result.current.isMobile).toBe(false);
      expect(result.current.isTablet).toBe(true);
      expect(result.current.isDesktop).toBe(false);
    });

    it('detects desktop breakpoint (> 1024px)', () => {
      setWindowSize(1920, 1080);

      const { result } = renderHook(() => useWindowLayout());

      expect(result.current.isMobile).toBe(false);
      expect(result.current.isTablet).toBe(false);
      expect(result.current.isDesktop).toBe(true);
    });

    it('updates breakpoint on resize', () => {
      setWindowSize(1920, 1080);

      const { result } = renderHook(() => useWindowLayout());

      expect(result.current.isDesktop).toBe(true);

      act(() => {
        setWindowSize(375, 667);
        window.dispatchEvent(new Event('resize'));
      });

      expect(result.current.isMobile).toBe(true);
      expect(result.current.isDesktop).toBe(false);
    });
  });

  describe('density', () => {
    it('returns compact density for small screens', () => {
      setWindowSize(375, 667);

      const { result } = renderHook(() => useWindowLayout());

      expect(result.current.density).toBe('compact');
    });

    it('returns comfortable density for medium screens', () => {
      setWindowSize(768, 1024);

      const { result } = renderHook(() => useWindowLayout());

      expect(result.current.density).toBe('comfortable');
    });

    it('returns spacious density for large screens', () => {
      setWindowSize(1920, 1080);

      const { result } = renderHook(() => useWindowLayout());

      expect(result.current.density).toBe('spacious');
    });
  });

  describe('cleanup', () => {
    it('removes resize listener on unmount', () => {
      const removeEventListenerSpy = vi.spyOn(window, 'removeEventListener');

      const { unmount } = renderHook(() => useWindowLayout());

      unmount();

      expect(removeEventListenerSpy).toHaveBeenCalledWith(
        'resize',
        expect.any(Function)
      );
    });
  });
});

// =============================================================================
// LayoutContextProvider Tests
// =============================================================================

describe('LayoutContextProvider', () => {
  it('is a React Context that can be used as Provider', () => {
    expect(LayoutContextProvider).toBeDefined();
    expect(LayoutContextProvider.Provider).toBeDefined();
  });

  it('provides custom layout context to children', () => {
    const customContext = {
      ...DEFAULT_LAYOUT_CONTEXT,
      availableWidth: 500,
      density: 'compact' as const,
    };

    const { result } = renderHook(() => useLayoutContext(), {
      wrapper: ({ children }) => (
        <LayoutContextProvider.Provider value={customContext}>
          {children}
        </LayoutContextProvider.Provider>
      ),
    });

    expect(result.current.availableWidth).toBe(500);
    expect(result.current.density).toBe('compact');
  });

  it('allows nested providers with different values', () => {
    const outerContext = {
      ...DEFAULT_LAYOUT_CONTEXT,
      depth: 1,
    };

    const innerContext = {
      ...DEFAULT_LAYOUT_CONTEXT,
      depth: 2,
    };

    const { result } = renderHook(() => useLayoutContext(), {
      wrapper: ({ children }) => (
        <LayoutContextProvider.Provider value={outerContext}>
          <LayoutContextProvider.Provider value={innerContext}>
            {children}
          </LayoutContextProvider.Provider>
        </LayoutContextProvider.Provider>
      ),
    });

    expect(result.current.depth).toBe(2);
  });
});
