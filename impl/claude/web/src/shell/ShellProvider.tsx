/**
 * ShellProvider - OS Shell Context Provider
 *
 * Provides unified context for the entire shell:
 * - Density detection (compact/comfortable/spacious)
 * - Observer context (archetype, capabilities, session)
 * - Trace collection for devex visibility
 * - Shell state (drawer/panel expansion)
 *
 * @see spec/protocols/os-shell.md
 * @see spec/protocols/projection.md
 * @see spec/protocols/agentese.md
 *
 * @example
 * ```tsx
 * // In App.tsx
 * <ShellProvider>
 *   <Shell>
 *     <Routes />
 *   </Shell>
 * </ShellProvider>
 *
 * // In any component
 * const { density, observer, addTrace } = useShell();
 * ```
 */

import {
  createContext,
  useContext,
  useState,
  useCallback,
  useEffect,
  useMemo,
  useRef,
  type ReactNode,
} from 'react';
import { nanoid } from 'nanoid';

// =============================================================================
// Utilities
// =============================================================================

/**
 * Debounce function to limit how often a function can fire.
 * @param fn - Function to debounce
 * @param delay - Delay in milliseconds
 */
function debounce<T extends (...args: Parameters<T>) => void>(
  fn: T,
  delay: number
): (...args: Parameters<T>) => void {
  let timeoutId: ReturnType<typeof setTimeout> | null = null;

  return (...args: Parameters<T>) => {
    if (timeoutId) {
      clearTimeout(timeoutId);
    }
    timeoutId = setTimeout(() => {
      fn(...args);
      timeoutId = null;
    }, delay);
  };
}
import { useMotionPreferences } from '../components/joy/useMotionPreferences';
import { useShellAnimation } from './useShellAnimation';
import type {
  Density,
  Observer,
  ObserverArchetype,
  Capability,
  Trace,
  ShellContext,
} from './types';

// =============================================================================
// Constants
// =============================================================================

/** Breakpoints aligned with projection.md spec */
const BREAKPOINTS = {
  compact: 768,    // <768px = compact (mobile)
  comfortable: 1024, // 768-1024 = comfortable (tablet)
  // spacious: >1024px (desktop)
} as const;

/** Debounce delay for resize handler in milliseconds */
const RESIZE_DEBOUNCE_MS = 100;

/** Default observer for anonymous sessions */
const DEFAULT_OBSERVER: Observer = {
  sessionId: typeof window !== 'undefined' ? `session-${nanoid(8)}` : 'ssr',
  archetype: 'developer',
  capabilities: new Set(['read']),
};

/** Storage keys for persistence */
const STORAGE_KEYS = {
  observer: 'kgents.shell.observer',
  drawerExpanded: 'kgents.shell.drawer',
  navExpanded: 'kgents.shell.nav',
  terminalExpanded: 'kgents.shell.terminal',
} as const;

/** Maximum traces to retain */
const MAX_TRACES = 50;

// =============================================================================
// Context
// =============================================================================

const ShellContextReact = createContext<ShellContext | null>(null);

// =============================================================================
// Hook
// =============================================================================

/**
 * Access shell context. Must be used within ShellProvider.
 *
 * @throws Error if used outside ShellProvider
 */
export function useShell(): ShellContext {
  const ctx = useContext(ShellContextReact);
  if (!ctx) {
    throw new Error('useShell must be used within a ShellProvider');
  }
  return ctx;
}

/**
 * Access shell context, or null if outside provider.
 * Useful for optional shell integration.
 */
export function useShellMaybe(): ShellContext | null {
  return useContext(ShellContextReact);
}

// =============================================================================
// Provider Props
// =============================================================================

export interface ShellProviderProps {
  children: ReactNode;
  /** Initial observer override (for testing) */
  initialObserver?: Partial<Observer>;
  /** Initial capabilities override */
  initialCapabilities?: Capability[];
}

// =============================================================================
// Provider Component
// =============================================================================

export function ShellProvider({
  children,
  initialObserver,
  initialCapabilities,
}: ShellProviderProps) {
  // ---------------------------------------------------------------------------
  // Layout Detection
  // ---------------------------------------------------------------------------

  const [layout, setLayout] = useState(() => ({
    width: typeof window !== 'undefined' ? window.innerWidth : 1024,
    height: typeof window !== 'undefined' ? window.innerHeight : 768,
  }));

  // Debounced resize handler ref to avoid recreating on each render
  const debouncedResizeRef = useRef<ReturnType<typeof debounce> | null>(null);

  useEffect(() => {
    const handleResize = () => {
      setLayout({
        width: window.innerWidth,
        height: window.innerHeight,
      });
    };

    // Create debounced handler once
    debouncedResizeRef.current = debounce(handleResize, RESIZE_DEBOUNCE_MS);

    // Use the debounced handler
    const onResize = () => debouncedResizeRef.current?.();

    window.addEventListener('resize', onResize);
    return () => window.removeEventListener('resize', onResize);
  }, []);

  const density: Density = useMemo(() => {
    if (layout.width < BREAKPOINTS.compact) return 'compact';
    if (layout.width < BREAKPOINTS.comfortable) return 'comfortable';
    return 'spacious';
  }, [layout.width]);

  const isMobile = layout.width < BREAKPOINTS.compact;
  const isTablet = layout.width >= BREAKPOINTS.compact && layout.width < BREAKPOINTS.comfortable;
  const isDesktop = layout.width >= BREAKPOINTS.comfortable;

  // ---------------------------------------------------------------------------
  // Observer State
  // ---------------------------------------------------------------------------

  const [observer, setObserver] = useState<Observer>(() => {
    // Try to restore from localStorage
    if (typeof window !== 'undefined') {
      try {
        const stored = localStorage.getItem(STORAGE_KEYS.observer);
        if (stored) {
          const parsed = JSON.parse(stored);
          return {
            ...DEFAULT_OBSERVER,
            ...parsed,
            // Ensure capabilities is a Set
            capabilities: new Set(parsed.capabilities || ['read']),
            // Override with initial props if provided
            ...initialObserver,
          };
        }
      } catch {
        // Ignore parse errors
      }
    }

    return {
      ...DEFAULT_OBSERVER,
      ...initialObserver,
      capabilities: initialCapabilities
        ? new Set(initialCapabilities)
        : DEFAULT_OBSERVER.capabilities,
    };
  });

  // Persist observer changes
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const toStore = {
        ...observer,
        capabilities: Array.from(observer.capabilities),
      };
      localStorage.setItem(STORAGE_KEYS.observer, JSON.stringify(toStore));
    }
  }, [observer]);

  const setArchetype = useCallback((archetype: ObserverArchetype) => {
    setObserver((prev) => ({ ...prev, archetype }));
  }, []);

  const setIntent = useCallback((intent: string) => {
    setObserver((prev) => ({ ...prev, intent }));
  }, []);

  const hasCapability = useCallback(
    (cap: Capability) => observer.capabilities.has(cap),
    [observer.capabilities]
  );

  // ---------------------------------------------------------------------------
  // Trace Collection
  // ---------------------------------------------------------------------------

  const [traces, setTraces] = useState<Trace[]>([]);

  const addTrace = useCallback((trace: Omit<Trace, 'id'>) => {
    const newTrace: Trace = {
      ...trace,
      id: nanoid(12),
    };

    setTraces((prev) => {
      const updated = [newTrace, ...prev];
      // Trim to max size
      return updated.slice(0, MAX_TRACES);
    });
  }, []);

  const clearTraces = useCallback(() => {
    setTraces([]);
  }, []);

  // ---------------------------------------------------------------------------
  // Shell Panel State
  // ---------------------------------------------------------------------------

  const [observerDrawerExpanded, setObserverDrawerExpanded] = useState(() => {
    if (typeof window !== 'undefined') {
      const stored = localStorage.getItem(STORAGE_KEYS.drawerExpanded);
      return stored === 'true';
    }
    return false;
  });

  const [navigationTreeExpanded, setNavigationTreeExpanded] = useState(() => {
    if (typeof window !== 'undefined') {
      const stored = localStorage.getItem(STORAGE_KEYS.navExpanded);
      // Default to expanded on desktop
      return stored ? stored === 'true' : !isMobile;
    }
    return true;
  });

  const [terminalExpanded, setTerminalExpanded] = useState(() => {
    if (typeof window !== 'undefined') {
      const stored = localStorage.getItem(STORAGE_KEYS.terminalExpanded);
      return stored === 'true';
    }
    return false;
  });

  // Persist panel states
  useEffect(() => {
    if (typeof window !== 'undefined') {
      localStorage.setItem(STORAGE_KEYS.drawerExpanded, String(observerDrawerExpanded));
    }
  }, [observerDrawerExpanded]);

  useEffect(() => {
    if (typeof window !== 'undefined') {
      localStorage.setItem(STORAGE_KEYS.navExpanded, String(navigationTreeExpanded));
    }
  }, [navigationTreeExpanded]);

  useEffect(() => {
    if (typeof window !== 'undefined') {
      localStorage.setItem(STORAGE_KEYS.terminalExpanded, String(terminalExpanded));
    }
  }, [terminalExpanded]);

  // Auto-collapse navigation when TRANSITIONING to mobile (not when already on mobile)
  const wasMobileRef = useRef(isMobile);
  useEffect(() => {
    // Only collapse if we just transitioned FROM desktop TO mobile
    if (isMobile && !wasMobileRef.current && navigationTreeExpanded) {
      setNavigationTreeExpanded(false);
    }
    wasMobileRef.current = isMobile;
  }, [isMobile, navigationTreeExpanded]);

  // ---------------------------------------------------------------------------
  // Animation Coordination (Temporal Coherence)
  // ---------------------------------------------------------------------------

  const { shouldAnimate } = useMotionPreferences();

  const {
    offsets,
    isAnyAnimating,
    observerHeight,
    terminalHeight,
    navigationWidth,
  } = useShellAnimation({
    observerExpanded: observerDrawerExpanded,
    navigationExpanded: navigationTreeExpanded,
    terminalExpanded,
    shouldAnimate,
  });

  // ---------------------------------------------------------------------------
  // Context Value
  // ---------------------------------------------------------------------------

  const contextValue: ShellContext = useMemo(
    () => ({
      // Layout
      density,
      width: layout.width,
      height: layout.height,
      isMobile,
      isTablet,
      isDesktop,

      // Observer
      observer,
      setArchetype,
      setIntent,

      // Capabilities
      capabilities: observer.capabilities,
      hasCapability,

      // Traces
      traces,
      addTrace,
      clearTraces,

      // Shell state
      observerDrawerExpanded,
      setObserverDrawerExpanded,
      navigationTreeExpanded,
      setNavigationTreeExpanded,
      terminalExpanded,
      setTerminalExpanded,

      // Animation coordination (temporal coherence)
      offsets,
      observerHeight,
      terminalHeight,
      navigationWidth,
      isAnimating: isAnyAnimating,
    }),
    [
      density,
      layout.width,
      layout.height,
      isMobile,
      isTablet,
      isDesktop,
      observer,
      setArchetype,
      setIntent,
      hasCapability,
      traces,
      addTrace,
      clearTraces,
      observerDrawerExpanded,
      navigationTreeExpanded,
      terminalExpanded,
      offsets,
      observerHeight,
      terminalHeight,
      navigationWidth,
      isAnyAnimating,
    ]
  );

  return (
    <ShellContextReact.Provider value={contextValue}>
      {children}
    </ShellContextReact.Provider>
  );
}

// =============================================================================
// Convenience Hooks
// =============================================================================

/**
 * Get current density.
 * Shorthand for useShell().density
 */
export function useDensity(): Density {
  return useShell().density;
}

/**
 * Get current observer.
 * Shorthand for useShell().observer
 */
export function useObserver(): Observer {
  return useShell().observer;
}

/**
 * Get trace management functions.
 */
export function useTraces(): Pick<ShellContext, 'traces' | 'addTrace' | 'clearTraces'> {
  const { traces, addTrace, clearTraces } = useShell();
  return { traces, addTrace, clearTraces };
}

/**
 * Hook to automatically add trace when invoking AGENTESE path.
 *
 * @example
 * ```tsx
 * const traced = useTracedInvoke();
 *
 * const result = await traced(
 *   'self.memory.capture',
 *   'manifest',
 *   () => brainApi.capture(data)
 * );
 * ```
 */
export function useTracedInvoke() {
  const { addTrace } = useTraces();

  return useCallback(
    async <T,>(
      path: string,
      aspect: string,
      invoke: () => Promise<T>
    ): Promise<T> => {
      const start = Date.now();
      try {
        const result = await invoke();
        addTrace({
          timestamp: new Date(),
          path,
          aspect,
          duration: Date.now() - start,
          status: 'success',
          result,
        });
        return result;
      } catch (error) {
        addTrace({
          timestamp: new Date(),
          path,
          aspect,
          duration: Date.now() - start,
          status: 'error',
          error: error instanceof Error ? error.message : String(error),
        });
        throw error;
      }
    },
    [addTrace]
  );
}

export default ShellProvider;
