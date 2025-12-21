/**
 * NavigationTree - Sidebar AGENTESE Ontology Navigation
 *
 * The Navigation Tree provides tree-based semantic navigation that mirrors
 * the five AGENTESE contexts. Paths are auto-discovered from the gateway.
 *
 * Features:
 * - Auto-populate from /agentese/discover
 * - Tree structure for five contexts (world, self, concept, void, time)
 * - Crown Jewel shortcuts
 * - Current path highlighting
 * - Density-adaptive (sidebar vs drawer vs hamburger)
 * - Keyboard navigation (arrows, enter, escape)
 * - Persistent state with reset
 *
 * @see spec/protocols/os-shell.md
 * @see spec/protocols/agentese.md
 * @see plans/navtree-refinement.md
 */

import {
  useEffect,
  useState,
  useCallback,
  useMemo,
  useRef,
  useDeferredValue,
  startTransition,
} from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronRight, X, RotateCcw, Globe, User, BookOpen, Sparkles, Clock } from 'lucide-react';
import { useShell } from './ShellProvider';
import { useMotionPreferences } from '@/components/joy/useMotionPreferences';
import { apiClient } from '@/api/client';
import { parseAgentesePath } from '@/utils/parseAgentesePath';
import type { PathInfo, Density } from './types';

// Extracted modules
import { useNavigationState } from './hooks';
import {
  TreeNodeItem,
  CrownJewelsSection,
  GallerySection,
  type TreeNode,
  type ContextInfo,
} from './components';

// =============================================================================
// Types
// =============================================================================

export interface NavigationTreeProps {
  className?: string;
}

// =============================================================================
// Constants
// =============================================================================

/** AGENTESE contexts with icons and colors */
const CONTEXT_INFO: Record<string, ContextInfo> = {
  world: {
    icon: Globe,
    label: 'World',
    color: 'text-green-400',
    description: 'External entities and environments',
  },
  self: {
    icon: User,
    label: 'Self',
    color: 'text-cyan-400',
    description: 'Internal memory and capability',
  },
  concept: {
    icon: BookOpen,
    label: 'Concept',
    color: 'text-violet-400',
    description: 'Abstract definitions and logic',
  },
  void: {
    icon: Sparkles,
    label: 'Void',
    color: 'text-pink-400',
    description: 'Entropy and serendipity',
  },
  time: {
    icon: Clock,
    label: 'Time',
    color: 'text-amber-400',
    description: 'Traces and schedules',
  },
};

const VALID_CONTEXTS = Object.keys(CONTEXT_INFO);

/** Sidebar width by density */
const SIDEBAR_WIDTH: Record<Density, number | null> = {
  spacious: 280,
  comfortable: 240,
  compact: null,
};

// =============================================================================
// Discovery Hook
// =============================================================================

const MAX_DISCOVERY_RETRIES = 3;
const DISCOVERY_CACHE_TTL = 5 * 60 * 1000;

interface DiscoveryCache {
  paths: PathInfo[];
  timestamp: number;
}

let discoveryCache: DiscoveryCache | null = null;

export function __clearDiscoveryCache(): void {
  discoveryCache = null;
}

function getBackoffDelay(attempt: number, baseDelay = 1000, maxDelay = 30000): number {
  const delay = Math.min(baseDelay * Math.pow(2, attempt), maxDelay);
  const jitter = delay * Math.random() * 0.25;
  return delay + jitter;
}

function useDiscovery() {
  const [paths, setPaths] = useState<PathInfo[]>([]);
  const [loading, setLoading] = useState(true);
  const [loadingAspects, setLoadingAspects] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  const retryTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const mountedRef = useRef(true);

  // Check cache validity without causing re-renders
  const isCacheValid = useCallback(() => {
    if (!discoveryCache) return false;
    return Date.now() - discoveryCache.timestamp < DISCOVERY_CACHE_TTL;
  }, []);

  const fetchPaths = useCallback(
    async (attempt = 0): Promise<void> => {
      // Use cached data immediately if valid (non-blocking)
      if (attempt === 0 && isCacheValid() && discoveryCache) {
        setPaths(discoveryCache.paths);
        setLoading(false);
        return;
      }

      setLoading(true);
      try {
        const response = await apiClient.get<{
          paths: string[];
          stats: { registered_nodes: number; contexts: string[] };
        }>('/agentese/discover');

        if (!mountedRef.current) return;

        const pathInfos: PathInfo[] = response.data.paths.map((p) => ({
          path: p,
          context: p.split('.')[0] as PathInfo['context'],
          aspects: ['manifest'],
        }));

        // Set paths immediately so tree is interactive
        setPaths(pathInfos);
        setLoading(false);
        setError(null);

        // Fetch affordances in background without blocking
        // Use startTransition to mark this as non-urgent
        setLoadingAspects(true);

        // Fire off affordance fetches but don't await them all at once
        // Instead, update as each one completes (streaming pattern)
        const fetchAndUpdateAffordance = async (info: PathInfo) => {
          try {
            const pathSegments = info.path.replace(/\./g, '/');
            const resp = await apiClient.get<{ path: string; affordances: string[] }>(
              `/agentese/${pathSegments}/affordances`
            );
            return { ...info, aspects: resp.data.affordances || ['manifest'] };
          } catch {
            return { ...info, aspects: ['manifest'] };
          }
        };

        // Process affordances and update cache when done
        // This happens in background - UI is already interactive
        Promise.all(pathInfos.map(fetchAndUpdateAffordance)).then((pathsWithAspects) => {
          if (!mountedRef.current) return;
          // Use startTransition to avoid blocking urgent updates
          startTransition(() => {
            discoveryCache = { paths: pathsWithAspects, timestamp: Date.now() };
            setPaths(pathsWithAspects);
            setLoadingAspects(false);
          });
        });
      } catch (e) {
        if (!mountedRef.current) return;
        const err = e as Error;
        setError(err);
        setLoading(false);

        if (attempt < MAX_DISCOVERY_RETRIES) {
          const delay = getBackoffDelay(attempt);
          retryTimeoutRef.current = setTimeout(() => {
            fetchPaths(attempt + 1);
          }, delay);
        }
      }
    },
    [isCacheValid]
  );

  useEffect(() => {
    mountedRef.current = true;
    fetchPaths();

    return () => {
      mountedRef.current = false;
      if (retryTimeoutRef.current) {
        clearTimeout(retryTimeoutRef.current);
      }
    };
  }, [fetchPaths]);

  return { paths, loading, loadingAspects, error };
}

// =============================================================================
// Tree Building
// =============================================================================

function buildTree(paths: PathInfo[]): Map<string, TreeNode> {
  const root = new Map<string, TreeNode>();

  for (const pathInfo of paths) {
    const segments = pathInfo.path.split('.');
    let currentLevel = root;
    let currentPath = '';

    for (let i = 0; i < segments.length; i++) {
      const segment = segments[i];
      currentPath = currentPath ? `${currentPath}.${segment}` : segment;

      if (!currentLevel.has(segment)) {
        currentLevel.set(segment, {
          segment,
          path: currentPath,
          children: new Map(),
          isRegistered: false,
        });
      }

      const node = currentLevel.get(segment);
      if (!node) continue;

      if (i === segments.length - 1) {
        node.isRegistered = true;
        node.description = pathInfo.description;
        node.aspects = pathInfo.aspects;
      }

      currentLevel = node.children;
    }
  }

  return root;
}

/** Collect all visible paths for keyboard navigation */
function collectVisiblePaths(tree: Map<string, TreeNode>, expandedPaths: Set<string>): string[] {
  const result: string[] = [];

  function traverse(nodes: Map<string, TreeNode>) {
    for (const node of nodes.values()) {
      result.push(node.path);
      if (node.children.size > 0 && expandedPaths.has(node.path)) {
        traverse(node.children);
      }
    }
  }

  traverse(tree);
  return result;
}

// =============================================================================
// Main Component
// =============================================================================

export function NavigationTree({ className = '' }: NavigationTreeProps) {
  const {
    density,
    navigationTreeExpanded,
    setNavigationTreeExpanded,
    observerHeight,
    terminalHeight,
  } = useShell();

  const navigate = useNavigate();
  const location = useLocation();
  const { shouldAnimate } = useMotionPreferences();
  const { paths, loading, loadingAspects } = useDiscovery();
  const containerRef = useRef<HTMLDivElement>(null);

  // Navigation state with persistence
  const [navState, navActions] = useNavigationState({
    persist: true,
    validContexts: VALID_CONTEXTS,
  });

  // Defer paths so tree building doesn't block urgent updates
  const deferredPaths = useDeferredValue(paths);

  // Build tree from deferred paths (non-blocking)
  const tree = useMemo(() => buildTree(deferredPaths), [deferredPaths]);

  // Current AGENTESE path from URL
  const currentPath = useMemo(() => {
    const parsed = parseAgentesePath(location.pathname);
    return parsed.isValid ? parsed.path : '';
  }, [location.pathname]);

  // Ancestor paths for highlighting
  const ancestorPaths = useMemo(() => {
    if (!currentPath) return new Set<string>();
    const segments = currentPath.split('.');
    const ancestors = new Set<string>();
    for (let i = 1; i < segments.length; i++) {
      ancestors.add(segments.slice(0, i).join('.'));
    }
    return ancestors;
  }, [currentPath]);

  // Visible paths for keyboard navigation
  const visiblePaths = useMemo(
    () => collectVisiblePaths(tree, navState.expandedPaths),
    [tree, navState.expandedPaths]
  );

  // Auto-expand tree to reveal current path
  // Use a ref to track previous path and avoid infinite loops
  const prevPathRef = useRef<string>('');

  useEffect(() => {
    // Only run when currentPath actually changes
    if (!currentPath || currentPath === prevPathRef.current) return;
    prevPathRef.current = currentPath;

    const segments = currentPath.split('.');
    const context = segments[0];

    if (context && CONTEXT_INFO[context]) {
      // Mark as non-urgent so main panel renders first
      startTransition(() => {
        navActions.setActiveSection(context);

        const pathsToExpand: string[] = [];
        for (let i = 1; i <= segments.length; i++) {
          pathsToExpand.push(segments.slice(0, i).join('.'));
        }
        navActions.expandPathsInSection(context, pathsToExpand);
      });
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps -- intentionally only react to currentPath changes
  }, [currentPath]);

  // Keyboard navigation handler
  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      const { focusedPath, expandedPaths } = navState;

      switch (e.key) {
        case 'ArrowDown':
          e.preventDefault();
          navActions.moveFocus('down', visiblePaths);
          break;

        case 'ArrowUp':
          e.preventDefault();
          navActions.moveFocus('up', visiblePaths);
          break;

        case 'ArrowRight':
          e.preventDefault();
          if (focusedPath && !expandedPaths.has(focusedPath)) {
            navActions.toggle(focusedPath);
          }
          break;

        case 'ArrowLeft':
          e.preventDefault();
          if (focusedPath) {
            if (expandedPaths.has(focusedPath)) {
              navActions.toggle(focusedPath);
            } else {
              // Go to parent
              const segments = focusedPath.split('.');
              if (segments.length > 1) {
                const parentPath = segments.slice(0, -1).join('.');
                navActions.setFocusedPath(parentPath);
              }
            }
          }
          break;

        case 'Enter':
          e.preventDefault();
          if (focusedPath) {
            handleNavigateToPath(focusedPath);
          }
          break;

        case 'Escape':
          e.preventDefault();
          if (navState.activeSection) {
            navActions.setActiveSection(null);
          }
          break;
      }
    },
    [navState, navActions, visiblePaths]
  );

  // Navigation handlers
  const handleNavigateToPath = useCallback(
    (path: string) => {
      navigate(`/${path}`);
      if (density === 'compact') {
        setNavigationTreeExpanded(false);
      }
    },
    [navigate, density, setNavigationTreeExpanded]
  );

  const handleNavigateToRoute = useCallback(
    (route: string) => {
      navigate(route);
      if (density === 'compact') {
        setNavigationTreeExpanded(false);
      }
    },
    [navigate, density, setNavigationTreeExpanded]
  );

  // Layout calculations
  const width = SIDEBAR_WIDTH[density];
  const getTopOffset = () => (density === 'compact' ? '0' : `${observerHeight}px`);
  const getBottomOffset = () => (density === 'compact' ? '0' : `${terminalHeight}px`);

  // ==========================================================================
  // Tree Content (shared across density modes)
  // ==========================================================================

  const TreeContent = (
    <div
      ref={containerRef}
      className="space-y-1 outline-none"
      tabIndex={0}
      onKeyDown={handleKeyDown}
      role="tree"
      aria-label="AGENTESE navigation tree"
    >
      {Array.from(tree.values()).map((node) => (
        <TreeNodeItem
          key={node.path}
          node={node}
          level={0}
          expandedPaths={navState.expandedPaths}
          currentPath={currentPath}
          ancestorPaths={ancestorPaths}
          focusedPath={navState.focusedPath}
          onToggle={navActions.toggle}
          onNavigate={handleNavigateToPath}
          onFocus={navActions.setFocusedPath}
          contextInfo={CONTEXT_INFO}
        />
      ))}
    </div>
  );

  const HeaderWithReset = (
    <div className="flex items-center gap-2">
      <h2 className="text-xs font-medium text-gray-500 uppercase tracking-wider">AGENTESE Paths</h2>
      {loadingAspects && (
        <span
          className="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-pulse"
          title="Loading aspects..."
        />
      )}
      <button
        onClick={navActions.reset}
        className="ml-auto p-1 hover:bg-gray-700 rounded transition-colors opacity-50 hover:opacity-100"
        title="Reset tree"
        aria-label="Reset navigation tree"
      >
        <RotateCcw className="w-3 h-3 text-gray-400" />
      </button>
    </div>
  );

  // ==========================================================================
  // Compact: Bottom drawer
  // ==========================================================================

  if (density === 'compact') {
    return (
      <AnimatePresence>
        {navigationTreeExpanded && (
          <>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: shouldAnimate ? 0.2 : 0 }}
              className="fixed inset-0 z-40 bg-black/50"
              onClick={() => setNavigationTreeExpanded(false)}
            />

            <motion.div
              initial={{ y: '100%' }}
              animate={{ y: 0 }}
              exit={{ y: '100%' }}
              transition={{
                type: 'spring',
                damping: 25,
                stiffness: 300,
                duration: shouldAnimate ? undefined : 0,
              }}
              className={`
                fixed bottom-0 left-0 right-0 z-50
                bg-gray-800 rounded-t-2xl shadow-xl
                max-h-[80vh] overflow-auto
                ${className}
              `}
            >
              <div className="sticky top-0 flex justify-center pt-2 pb-1 bg-gray-800">
                <div className="w-10 h-1 rounded-full bg-gray-600" />
              </div>

              <button
                onClick={() => setNavigationTreeExpanded(false)}
                className="absolute top-2 right-2 p-2 hover:bg-gray-700 rounded-full"
                aria-label="Close navigation"
              >
                <X className="w-5 h-5 text-gray-400" />
              </button>

              <div className="p-4 space-y-4">
                {HeaderWithReset}
                {loading ? (
                  <div className="py-4 text-center text-gray-500 text-sm">Loading paths...</div>
                ) : (
                  TreeContent
                )}
                <CrownJewelsSection currentPath={currentPath} onNavigate={handleNavigateToPath} />
                <GallerySection
                  currentRoute={location.pathname}
                  onNavigate={handleNavigateToRoute}
                />
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    );
  }

  // ==========================================================================
  // Comfortable: Collapsible sidebar
  // ==========================================================================

  if (density === 'comfortable') {
    return (
      <>
        {!navigationTreeExpanded && (
          <button
            onClick={() => setNavigationTreeExpanded(true)}
            className="fixed left-0 top-1/2 -translate-y-1/2 z-30 p-2 bg-gray-800/80 backdrop-blur-sm rounded-r-lg border border-l-0 border-gray-700/50 hover:bg-gray-700 transition-colors"
            aria-label="Open navigation sidebar"
          >
            <ChevronRight className="w-4 h-4 text-gray-400" />
          </button>
        )}

        <AnimatePresence>
          {navigationTreeExpanded && (
            <motion.aside
              initial={{ x: -(width || 240), opacity: 0 }}
              animate={{ x: 0, opacity: 1 }}
              exit={{ x: -(width || 240), opacity: 0 }}
              transition={{ duration: shouldAnimate ? 0.2 : 0, ease: 'easeOut' }}
              style={{ width: width || 240, top: getTopOffset(), bottom: getBottomOffset() }}
              className={`
                fixed left-0 z-30
                bg-gray-800/[0.825] backdrop-blur-md
                border-r border-gray-700/50
                overflow-y-auto
                ${className}
              `}
            >
              <button
                onClick={() => setNavigationTreeExpanded(false)}
                className="absolute top-2 right-2 p-1 hover:bg-gray-700 rounded"
                aria-label="Close navigation sidebar"
              >
                <X className="w-4 h-4 text-gray-400" />
              </button>

              <div className="p-3 pt-8 space-y-4">
                <div className="px-3">{HeaderWithReset}</div>
                {loading ? (
                  <div className="py-4 text-center text-gray-500 text-sm">Loading...</div>
                ) : (
                  TreeContent
                )}
                <CrownJewelsSection currentPath={currentPath} onNavigate={handleNavigateToPath} />
                <GallerySection
                  currentRoute={location.pathname}
                  onNavigate={handleNavigateToRoute}
                />
              </div>
            </motion.aside>
          )}
        </AnimatePresence>
      </>
    );
  }

  // ==========================================================================
  // Spacious: Floating collapsible sidebar
  // ==========================================================================

  return (
    <>
      <button
        onClick={() => setNavigationTreeExpanded(!navigationTreeExpanded)}
        className={`
          fixed left-0 top-1/2 -translate-y-1/2 z-40
          p-2 bg-gray-800/90 backdrop-blur-sm rounded-r-lg
          border border-l-0 border-gray-700/50
          hover:bg-gray-700 transition-all duration-200
          ${navigationTreeExpanded ? 'translate-x-[280px]' : 'translate-x-0'}
        `}
        aria-label={navigationTreeExpanded ? 'Close navigation sidebar' : 'Open navigation sidebar'}
      >
        <motion.span
          animate={{ rotate: navigationTreeExpanded ? 180 : 0 }}
          transition={{ duration: shouldAnimate ? 0.2 : 0 }}
          className="block"
        >
          <ChevronRight className="w-4 h-4 text-gray-400" />
        </motion.span>
      </button>

      <AnimatePresence>
        {navigationTreeExpanded && (
          <motion.aside
            initial={{ x: -(width || 280), opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            exit={{ x: -(width || 280), opacity: 0 }}
            transition={{ duration: shouldAnimate ? 0.25 : 0, ease: [0.4, 0, 0.2, 1] }}
            style={{ width: width || 280, top: getTopOffset(), bottom: getBottomOffset() }}
            className={`
              fixed left-0 z-30
              bg-gray-800/[0.825] backdrop-blur-md
              border-r border-gray-700/50
              overflow-y-auto
              shadow-xl
              ${className}
            `}
          >
            <div className="sticky top-0 bg-gray-800/[0.825] backdrop-blur-md border-b border-gray-700/50 px-3 py-2 flex items-center justify-between">
              {HeaderWithReset}
              <button
                onClick={() => setNavigationTreeExpanded(false)}
                className="p-1 hover:bg-gray-700 rounded transition-colors"
                aria-label="Close navigation sidebar"
              >
                <X className="w-4 h-4 text-gray-400" />
              </button>
            </div>

            <div className="p-3 space-y-4">
              {loading ? (
                <div className="py-4 text-center text-gray-500 text-sm">Loading paths...</div>
              ) : (
                TreeContent
              )}
              <CrownJewelsSection currentPath={currentPath} onNavigate={handleNavigateToPath} />
              <GallerySection currentRoute={location.pathname} onNavigate={handleNavigateToRoute} />
            </div>
          </motion.aside>
        )}
      </AnimatePresence>
    </>
  );
}

export default NavigationTree;
