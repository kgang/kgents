/**
 * OS Shell - Unified Layout System
 *
 * The shell transforms the web interface into an "operating system for autopoiesis"
 * with three persistent layers:
 * 1. Observer Drawer (top) - Who is looking / trace visibility
 * 2. Navigation Tree (sidebar) - AGENTESE-discovered paths
 * 3. Terminal (bottom) - AGENTESE CLI
 *
 * @see spec/protocols/os-shell.md
 *
 * @example
 * ```tsx
 * import { ShellProvider, useShell, useDensity, ObserverDrawer } from '@/shell';
 *
 * // In App.tsx
 * <ShellProvider>
 *   <RouterProvider router={router} />
 * </ShellProvider>
 *
 * // In Shell layout
 * <ShellProvider>
 *   <ObserverDrawer />
 *   <main>...</main>
 * </ShellProvider>
 *
 * // In components
 * const { density, observer, addTrace } = useShell();
 * ```
 */

// Provider & hooks
export {
  ShellProvider,
  useShell,
  useShellMaybe,
  useDensity,
  useObserver,
  useTraces,
  useTracedInvoke,
} from './ShellProvider';
export type { ShellProviderProps } from './ShellProvider';

// Components
export { ObserverDrawer } from './ObserverDrawer';
export type { ObserverDrawerProps } from './ObserverDrawer';

export { NavigationTree, __clearDiscoveryCache } from './NavigationTree';
export type { NavigationTreeProps } from './NavigationTree';

// PathProjection - Generic AGENTESE path to projection wrapper
export {
  PathProjection,
  LivePathProjection,
  LazyPathProjection,
} from './PathProjection';
export type { PathProjectionProps, ProjectionContext } from './PathProjection';

// StreamPathProjection - SSE-based projection wrapper
export { StreamPathProjection } from './StreamPathProjection';
export type {
  StreamPathProjectionProps,
  StreamProjectionContext,
  LoaderResult,
  StreamResult,
} from './StreamPathProjection';

// Terminal - AGENTESE CLI in browser
export { Terminal } from './Terminal';
export type { TerminalProps } from './Terminal';

// Shell - The unified layout wrapper
export { Shell } from './Shell';
export type { default as ShellComponent } from './Shell';

// Error Boundaries - Graceful degradation for shell components
export {
  ShellErrorBoundary,
  ObserverErrorBoundary,
  NavigationErrorBoundary,
  TerminalErrorBoundary,
  ProjectionErrorBoundary,
} from './ShellErrorBoundary';
export type { ShellErrorBoundaryProps, ShellLayer } from './ShellErrorBoundary';

// Terminal Service
export {
  TerminalService,
  createTerminalService,
  getTerminalService,
} from './TerminalService';

// Types
export type {
  Density,
  Observer,
  ObserverArchetype,
  Capability,
  Trace,
  TraceStatus,
  ShellContext,
  CrownJewel,
  PathInfo,
  DiscoveryResponse,
  ProjectionContext as ProjectionContextType,
  // Terminal types
  HistoryEntry,
  HistoryStatus,
  TerminalCollection,
  CompletionSuggestion,
  TerminalLine,
  TerminalServiceInterface,
} from './types';
