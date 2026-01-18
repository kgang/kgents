/**
 * useLayoutContext: Hook for tracking layout context in elastic containers.
 *
 * SEVERE STARK: Minimal responsive layout hook.
 */

import { useState, useEffect, useRef, createContext, useContext, type RefObject } from 'react';

/**
 * Density levels for SEVERE STARK.
 * Default is 'spacious' (dense by Western standards).
 */
export type Density = 'compact' | 'comfortable' | 'spacious';

/**
 * Layout context for elastic containers.
 */
export interface LayoutContext {
  availableWidth: number;
  availableHeight: number;
  depth: number;
  parentLayout: 'stack' | 'split' | 'grid';
  isConstrained: boolean;
  density: Density;
}

// Breakpoints for density calculation
const BREAKPOINTS = {
  sm: 768, // compact threshold
  lg: 1024, // spacious threshold
};

/**
 * Get density based on available width.
 */
function getDensity(width: number): Density {
  if (width < BREAKPOINTS.sm) return 'compact';
  if (width < BREAKPOINTS.lg) return 'comfortable';
  return 'spacious';
}

/**
 * Default layout context for components outside a provider.
 */
const DEFAULT_CONTEXT: LayoutContext = {
  availableWidth: typeof window !== 'undefined' ? window.innerWidth : 1024,
  availableHeight: typeof window !== 'undefined' ? window.innerHeight : 768,
  depth: 0,
  parentLayout: 'stack',
  isConstrained: false,
  density: 'spacious', // SEVERE STARK: default to dense
};

/**
 * React Context for layout information.
 */
const LayoutContextReact = createContext<LayoutContext>(DEFAULT_CONTEXT);

/**
 * Hook to access layout context from a provider.
 */
export function useLayoutContext(): LayoutContext {
  return useContext(LayoutContextReact);
}

/**
 * Hook to measure a container and provide layout context.
 */
export function useLayoutMeasure(
  options: {
    parentLayout?: LayoutContext['parentLayout'];
    parentContext?: LayoutContext;
  } = {}
): [RefObject<HTMLDivElement | null>, LayoutContext] {
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

    updateContext();

    const observer = new ResizeObserver(() => {
      updateContext();
    });

    observer.observe(container);

    return () => observer.disconnect();
  }, [parentLayout, parentContext?.depth]);

  return [containerRef, context];
}

/**
 * Hook for window-level layout information.
 */
export function useWindowLayout(): {
  width: number;
  height: number;
  density: Density;
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

export { LayoutContextReact as LayoutContextProvider };
export { DEFAULT_CONTEXT as DEFAULT_LAYOUT_CONTEXT };

export default useLayoutContext;
