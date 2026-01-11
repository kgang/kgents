/**
 * useNavigationState — Isolated navigation state management
 *
 * "Only the editor should re-render when the path changes."
 *
 * Problem: When currentPath state lives in HypergraphEditorPage and is passed
 * down as props, changing it causes the entire tree to re-render (sidebars included).
 *
 * Solution: Store path in a ref and use a subscription pattern. Components that
 * need to react to path changes subscribe explicitly. The KBlockExplorer only
 * needs the selectedId for highlighting, which can be updated without re-rendering
 * the entire sidebar.
 *
 * Architecture:
 * - NavigationProvider wraps the app (or just the workspace area)
 * - useNavigationPath() returns the current path (subscribes to changes)
 * - useNavigationDispatch() returns navigate() function (no subscription)
 * - useSelectedId() returns selectedId for highlighting (subscribes)
 *
 * This separates:
 * - State changes (path updates) from
 * - State consumption (reading the path)
 *
 * Only components that call useNavigationPath() will re-render on path changes.
 */

import {
  createContext,
  useCallback,
  useContext,
  useRef,
  useSyncExternalStore,
  type ReactNode,
} from 'react';

// =============================================================================
// Types
// =============================================================================

interface NavigationState {
  currentPath: string | null;
  recentFiles: string[];
}

interface NavigationContextValue {
  /** Get current state (for reading in callbacks, doesn't cause re-render) */
  getState: () => NavigationState;

  /** Subscribe to state changes */
  subscribe: (listener: () => void) => () => void;

  /** Navigate to a new path */
  navigate: (path: string) => void;

  /** Navigate internally (URL update without full re-render) */
  navigateInternal: (path: string) => void;

  /** Add to recent files */
  addRecent: (path: string) => void;

  /** Clear recent files */
  clearRecent: () => void;
}

// =============================================================================
// Context
// =============================================================================

const NavigationContext = createContext<NavigationContextValue | null>(null);

// =============================================================================
// Provider
// =============================================================================

interface NavigationProviderProps {
  children: ReactNode;
  initialPath?: string | null;
  /** Called when navigation occurs (for URL updates) */
  onNavigate?: (path: string) => void;
  /** Called for internal navigation (silent URL update) */
  onInternalNavigate?: (path: string) => void;
}

export function NavigationProvider({
  children,
  initialPath = null,
  onNavigate,
  onInternalNavigate,
}: NavigationProviderProps) {
  // Store state in a ref to avoid re-renders
  const stateRef = useRef<NavigationState>({
    currentPath: initialPath,
    recentFiles: [],
  });

  // Listeners for useSyncExternalStore
  const listenersRef = useRef(new Set<() => void>());

  // Notify all listeners
  const emitChange = useCallback(() => {
    listenersRef.current.forEach((listener) => listener());
  }, []);

  // Get current state (stable reference)
  const getState = useCallback(() => stateRef.current, []);

  // Subscribe to changes
  const subscribe = useCallback((listener: () => void) => {
    listenersRef.current.add(listener);
    return () => {
      listenersRef.current.delete(listener);
    };
  }, []);

  // Navigate to a new path (full navigation)
  const navigate = useCallback(
    (path: string) => {
      if (stateRef.current.currentPath === path) return;

      stateRef.current = {
        ...stateRef.current,
        currentPath: path,
        recentFiles: addToRecent(stateRef.current.recentFiles, path),
      };
      emitChange();
      onNavigate?.(path);
    },
    [emitChange, onNavigate]
  );

  // Navigate internally (no URL update trigger)
  const navigateInternal = useCallback(
    (path: string) => {
      if (stateRef.current.currentPath === path) return;

      stateRef.current = {
        ...stateRef.current,
        currentPath: path,
        recentFiles: addToRecent(stateRef.current.recentFiles, path),
      };
      emitChange();
      onInternalNavigate?.(path);
    },
    [emitChange, onInternalNavigate]
  );

  // Add to recent files
  const addRecent = useCallback(
    (path: string) => {
      stateRef.current = {
        ...stateRef.current,
        recentFiles: addToRecent(stateRef.current.recentFiles, path),
      };
      emitChange();
    },
    [emitChange]
  );

  // Clear recent files
  const clearRecent = useCallback(() => {
    stateRef.current = {
      ...stateRef.current,
      recentFiles: [],
    };
    emitChange();
  }, [emitChange]);

  const value: NavigationContextValue = {
    getState,
    subscribe,
    navigate,
    navigateInternal,
    addRecent,
    clearRecent,
  };

  return <NavigationContext.Provider value={value}>{children}</NavigationContext.Provider>;
}

// =============================================================================
// Hooks
// =============================================================================

/**
 * useNavigationContext — Get the raw context (for advanced use cases)
 */
export function useNavigationContext(): NavigationContextValue {
  const context = useContext(NavigationContext);
  if (!context) {
    throw new Error('useNavigationContext must be used within NavigationProvider');
  }
  return context;
}

/**
 * useNavigationPath — Subscribe to path changes (causes re-render on change)
 *
 * Use this in components that need to react to path changes (e.g., HypergraphEditor)
 *
 * Note: The getSnapshot function must return a stable reference between calls
 * unless the store has actually updated. We cache the snapshot result.
 */
export function useNavigationPath(): string | null {
  const { getState, subscribe } = useNavigationContext();

  // Cache the snapshot to avoid React's "getSnapshot should be cached" warning
  const getSnapshot = useCallback(() => getState().currentPath, [getState]);
  const getServerSnapshot = useCallback(() => getState().currentPath, [getState]);

  return useSyncExternalStore(subscribe, getSnapshot, getServerSnapshot);
}

/**
 * useSelectedId — Get the current path as selectedId (for highlighting)
 *
 * Use this in KBlockExplorer for highlighting the selected item.
 * This subscribes to changes but can be optimized with useDeferredValue if needed.
 */
export function useSelectedId(): string | undefined {
  const path = useNavigationPath();
  return path ?? undefined;
}

/**
 * useRecentFiles — Subscribe to recent files changes
 *
 * Note: The getSnapshot function must return a stable reference between calls
 * unless the store has actually updated. We cache the snapshot result.
 */
export function useRecentFiles(): string[] {
  const { getState, subscribe } = useNavigationContext();

  // Cache the snapshot to avoid React's "getSnapshot should be cached" warning
  const getSnapshot = useCallback(() => getState().recentFiles, [getState]);
  const getServerSnapshot = useCallback(() => getState().recentFiles, [getState]);

  return useSyncExternalStore(subscribe, getSnapshot, getServerSnapshot);
}

/**
 * useNavigate — Get navigate function without subscribing to state
 *
 * Use this in components that trigger navigation but don't need to re-render
 * when the path changes (e.g., KBlockExplorer's click handler).
 */
export function useNavigate(): (path: string) => void {
  const { navigate } = useNavigationContext();
  return navigate;
}

/**
 * useNavigateInternal — Get internal navigate function
 *
 * Use this for edge clicks and in-editor navigation that shouldn't
 * trigger full sidebar re-renders.
 */
export function useNavigateInternal(): (path: string) => void {
  const { navigateInternal } = useNavigationContext();
  return navigateInternal;
}

/**
 * useRecentFilesActions — Get actions for recent files
 */
export function useRecentFilesActions() {
  const { addRecent, clearRecent } = useNavigationContext();
  return { addRecent, clearRecent };
}

// =============================================================================
// Utilities
// =============================================================================

const MAX_RECENT = 10;

function addToRecent(recent: string[], path: string): string[] {
  // Remove if already exists
  const filtered = recent.filter((p) => p !== path);
  // Add to front
  const updated = [path, ...filtered];
  // Limit size
  return updated.slice(0, MAX_RECENT);
}
