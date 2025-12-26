/**
 * LayoutProvider
 *
 * Provides responsive layout context for the pilots webapp.
 * Tracks viewport size and provides density-aware layout information.
 *
 * Density Modes (aligned with elastic-ui-patterns):
 * - compact: < 768px (mobile)
 * - comfortable: 768-1024px (tablet)
 * - spacious: > 1024px (desktop)
 */

import {
  createContext,
  useContext,
  useState,
  useEffect,
  type ReactNode,
} from 'react';

// =============================================================================
// Types
// =============================================================================

export type Density = 'compact' | 'comfortable' | 'spacious';

export interface LayoutContext {
  /** Current density mode based on viewport */
  density: Density;
  /** Viewport width in pixels */
  width: number;
  /** Viewport height in pixels */
  height: number;
  /** Is viewport mobile-sized (< 768px) */
  isMobile: boolean;
  /** Is viewport tablet-sized (768-1024px) */
  isTablet: boolean;
  /** Is viewport desktop-sized (> 1024px) */
  isDesktop: boolean;
  /** Should sidebar be collapsed */
  sidebarCollapsed: boolean;
  /** Toggle sidebar collapsed state */
  toggleSidebar: () => void;
  /** Set sidebar collapsed state */
  setSidebarCollapsed: (collapsed: boolean) => void;
}

// =============================================================================
// Constants
// =============================================================================

/** Breakpoints aligned with Layout Projection Functor spec */
const BREAKPOINTS = {
  sm: 768,   // compact threshold
  lg: 1024,  // comfortable -> spacious transition
};

const SIDEBAR_STORAGE_KEY = 'kgents-sidebar-collapsed';

// =============================================================================
// Context
// =============================================================================

const LayoutContextReact = createContext<LayoutContext | null>(null);

// =============================================================================
// Hook
// =============================================================================

/**
 * Hook to access layout context.
 * Must be used within a LayoutProvider.
 */
export function useLayout(): LayoutContext {
  const context = useContext(LayoutContextReact);
  if (!context) {
    throw new Error('useLayout must be used within a LayoutProvider');
  }
  return context;
}

// =============================================================================
// Helper
// =============================================================================

function getDensity(width: number): Density {
  if (width < BREAKPOINTS.sm) return 'compact';
  if (width < BREAKPOINTS.lg) return 'comfortable';
  return 'spacious';
}

// =============================================================================
// Provider Component
// =============================================================================

export interface LayoutProviderProps {
  children: ReactNode;
}

/**
 * LayoutProvider
 *
 * Provides responsive layout context to child components.
 * Automatically tracks viewport size and updates density.
 *
 * @example
 * ```tsx
 * <LayoutProvider>
 *   <App />
 * </LayoutProvider>
 * ```
 *
 * Usage in components:
 * ```tsx
 * function MyComponent() {
 *   const { density, isMobile, toggleSidebar } = useLayout();
 *   return (
 *     <div className={density === 'compact' ? 'p-2' : 'p-4'}>
 *       {!isMobile && <Sidebar />}
 *     </div>
 *   );
 * }
 * ```
 */
export function LayoutProvider({ children }: LayoutProviderProps) {
  const [dimensions, setDimensions] = useState(() => ({
    width: typeof window !== 'undefined' ? window.innerWidth : 1024,
    height: typeof window !== 'undefined' ? window.innerHeight : 768,
  }));

  const [sidebarCollapsed, setSidebarCollapsedState] = useState(() => {
    if (typeof window === 'undefined') return false;
    const stored = localStorage.getItem(SIDEBAR_STORAGE_KEY);
    return stored === 'true';
  });

  // Track viewport size
  useEffect(() => {
    let rafId: number;

    const handleResize = () => {
      // Throttle with requestAnimationFrame
      cancelAnimationFrame(rafId);
      rafId = requestAnimationFrame(() => {
        setDimensions({
          width: window.innerWidth,
          height: window.innerHeight,
        });
      });
    };

    window.addEventListener('resize', handleResize);
    return () => {
      window.removeEventListener('resize', handleResize);
      cancelAnimationFrame(rafId);
    };
  }, []);

  // Auto-collapse sidebar on mobile
  useEffect(() => {
    if (dimensions.width < BREAKPOINTS.sm) {
      setSidebarCollapsedState(true);
    }
  }, [dimensions.width]);

  const density = getDensity(dimensions.width);
  const isMobile = dimensions.width < BREAKPOINTS.sm;
  const isTablet = dimensions.width >= BREAKPOINTS.sm && dimensions.width < BREAKPOINTS.lg;
  const isDesktop = dimensions.width >= BREAKPOINTS.lg;

  const setSidebarCollapsed = (collapsed: boolean) => {
    setSidebarCollapsedState(collapsed);
    localStorage.setItem(SIDEBAR_STORAGE_KEY, String(collapsed));
  };

  const toggleSidebar = () => {
    setSidebarCollapsed(!sidebarCollapsed);
  };

  const value: LayoutContext = {
    density,
    width: dimensions.width,
    height: dimensions.height,
    isMobile,
    isTablet,
    isDesktop,
    sidebarCollapsed,
    toggleSidebar,
    setSidebarCollapsed,
  };

  return (
    <LayoutContextReact.Provider value={value}>
      {children}
    </LayoutContextReact.Provider>
  );
}

LayoutProvider.displayName = 'LayoutProvider';

export default LayoutProvider;
