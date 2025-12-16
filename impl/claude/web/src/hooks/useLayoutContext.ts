/**
 * useLayoutContext: Hook for tracking layout context in elastic containers.
 *
 * Provides responsive layout information to child components:
 * - Available width/height from ResizeObserver
 * - Density based on viewport size
 * - Constraint detection
 *
 * @see plans/web-refactor/elastic-primitives.md
 */

import { useState, useEffect, useRef, createContext, useContext, type RefObject } from 'react';
import type { LayoutContext } from '@/reactive/types';

// Breakpoints aligned with Layout Projection Functor spec
// See: spec/protocols/projection.md (Layout Projection section)
// - compact: < 768px (mobile)
// - comfortable: 768-1024px (tablet)
// - spacious: > 1024px (desktop)
const BREAKPOINTS = {
  sm: 768,   // spec: compact threshold (was 640, now matches spec)
  md: 768,   // kept for compatibility
  lg: 1024,  // spec: comfortable → spacious transition
  xl: 1280,  // not used by spec, kept for Tailwind compatibility
};

/**
 * Get density based on available width
 */
function getDensity(width: number): LayoutContext['density'] {
  if (width < BREAKPOINTS.sm) return 'compact';
  if (width < BREAKPOINTS.lg) return 'comfortable';
  return 'spacious';
}

/**
 * Default layout context for components outside a provider
 */
const DEFAULT_CONTEXT: LayoutContext = {
  availableWidth: typeof window !== 'undefined' ? window.innerWidth : 1024,
  availableHeight: typeof window !== 'undefined' ? window.innerHeight : 768,
  depth: 0,
  parentLayout: 'stack',
  isConstrained: false,
  density: 'comfortable',
};

/**
 * React Context for layout information
 */
const LayoutContextReact = createContext<LayoutContext>(DEFAULT_CONTEXT);

/**
 * Hook to access layout context from a provider
 */
export function useLayoutContext(): LayoutContext {
  return useContext(LayoutContextReact);
}

/**
 * Hook to measure a container and provide layout context
 *
 * @param options Configuration options
 * @returns [ref to attach to container, current layout context]
 */
export function useLayoutMeasure(options: {
  parentLayout?: LayoutContext['parentLayout'];
  parentContext?: LayoutContext;
} = {}): [RefObject<HTMLDivElement | null>, LayoutContext] {
  const { parentLayout = 'stack', parentContext } = options;
  const containerRef = useRef<HTMLDivElement>(null);

  const [context, setContext] = useState<LayoutContext>(() => {
    const parentDepth = parentContext?.depth ?? 0;
    return {
      ...DEFAULT_CONTEXT,
      depth: parentDepth + 1,
      parentLayout,
    };
  });

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    const updateContext = () => {
      const rect = container.getBoundingClientRect();
      const width = rect.width;
      const height = rect.height;
      const parentDepth = parentContext?.depth ?? 0;

      setContext({
        availableWidth: width,
        availableHeight: height,
        depth: parentDepth + 1,
        parentLayout,
        isConstrained: width < BREAKPOINTS.sm,
        density: getDensity(width),
      });
    };

    // Initial measurement
    updateContext();

    // Watch for size changes
    const observer = new ResizeObserver(() => {
      updateContext();
    });

    observer.observe(container);

    return () => observer.disconnect();
  }, [parentLayout, parentContext?.depth]);

  return [containerRef, context];
}

/**
 * Hook for window-level layout information
 */
export function useWindowLayout(): {
  width: number;
  height: number;
  density: LayoutContext['density'];
  isMobile: boolean;
  isTablet: boolean;
  isDesktop: boolean;
} {
  const [layout, setLayout] = useState(() => ({
    width: typeof window !== 'undefined' ? window.innerWidth : 1024,
    height: typeof window !== 'undefined' ? window.innerHeight : 768,
  }));

  useEffect(() => {
    const handleResize = () => {
      setLayout({
        width: window.innerWidth,
        height: window.innerHeight,
      });
    };

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  return {
    width: layout.width,
    height: layout.height,
    density: getDensity(layout.width),
    isMobile: layout.width < BREAKPOINTS.sm,
    isTablet: layout.width >= BREAKPOINTS.sm && layout.width < BREAKPOINTS.lg,
    isDesktop: layout.width >= BREAKPOINTS.lg,
  };
}

/**
 * Provider component for layout context
 */
export { LayoutContextReact as LayoutContextProvider };
export { DEFAULT_CONTEXT as DEFAULT_LAYOUT_CONTEXT };

export default useLayoutContext;
