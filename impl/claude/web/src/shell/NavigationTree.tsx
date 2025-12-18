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
 *
 * @see spec/protocols/os-shell.md
 * @see spec/protocols/agentese.md
 */

import { useEffect, useState, useCallback, useMemo, memo, useRef } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import {
  ChevronRight,
  Menu,
  X,
  Globe,
  User,
  BookOpen,
  Sparkles,
  Clock,
  Brain,
  Network,
  Leaf,
  Palette,
  Users,
  Theater,
  Building,
  Layers,
  type LucideIcon,
} from 'lucide-react';
import { useShell } from './ShellProvider';
import { JEWEL_COLORS, type JewelName } from '@/constants/jewels';
import { useMotionPreferences } from '@/components/joy/useMotionPreferences';
import { apiClient } from '@/api/client';
import type { PathInfo, Density } from './types';

// =============================================================================
// Types
// =============================================================================

export interface NavigationTreeProps {
  /** Additional CSS classes */
  className?: string;
}

interface TreeNode {
  /** Node path segment */
  segment: string;
  /** Full AGENTESE path */
  path: string;
  /** Child nodes */
  children: Map<string, TreeNode>;
  /** Is this a leaf (registered path) */
  isLeaf: boolean;
  /** Description from discovery */
  description?: string;
  /** Available aspects */
  aspects?: string[];
}

interface ContextInfo {
  icon: LucideIcon;
  label: string;
  color: string;
  description: string;
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

/** Crown Jewel shortcuts */
const CROWN_JEWELS: Array<{
  name: JewelName;
  label: string;
  path: string;
  route: string;
  icon: LucideIcon;
}> = [
  { name: 'brain', label: 'Brain', path: 'self.memory', route: '/brain', icon: Brain },
  { name: 'gestalt', label: 'Gestalt', path: 'world.codebase', route: '/gestalt', icon: Network },
  { name: 'gardener', label: 'Gardener', path: 'concept.gardener', route: '/gardener', icon: Leaf },
  { name: 'atelier', label: 'Atelier', path: 'world.atelier', route: '/atelier', icon: Palette },
  { name: 'coalition', label: 'Coalition', path: 'world.town', route: '/town', icon: Users },
  { name: 'park', label: 'Park', path: 'world.park', route: '/park', icon: Theater },
  { name: 'domain', label: 'Domain', path: 'world.domain', route: '/workshop', icon: Building },
];

/** Sidebar width by density */
const SIDEBAR_WIDTH: Record<Density, number | null> = {
  spacious: 280,
  comfortable: 240,
  compact: null, // Full-screen drawer
};

// =============================================================================
// Hooks
// =============================================================================

/**
 * Exponential backoff delay calculator.
 * @param attempt - The current attempt number (0-indexed)
 * @param baseDelay - Base delay in milliseconds (default: 1000ms)
 * @param maxDelay - Maximum delay cap in milliseconds (default: 30000ms)
 */
function getBackoffDelay(attempt: number, baseDelay = 1000, maxDelay = 30000): number {
  const delay = Math.min(baseDelay * Math.pow(2, attempt), maxDelay);
  // Add jitter (0-25% of delay) to prevent thundering herd
  const jitter = delay * Math.random() * 0.25;
  return delay + jitter;
}

/** Maximum retry attempts for discovery */
const MAX_DISCOVERY_RETRIES = 3;

/** Cache expiry time in milliseconds (5 minutes) */
const DISCOVERY_CACHE_TTL = 5 * 60 * 1000;

/** Cached discovery result */
interface DiscoveryCache {
  paths: PathInfo[];
  timestamp: number;
}

let discoveryCache: DiscoveryCache | null = null;

/**
 * Clear the discovery cache (for testing).
 * @internal
 */
export function __clearDiscoveryCache(): void {
  discoveryCache = null;
}

/**
 * Hook to fetch AGENTESE paths from discovery endpoint.
 * Features:
 * - Retry with exponential backoff
 * - Local caching with TTL
 * - Graceful fallback to hardcoded paths
 */
function useDiscovery() {
  const [paths, setPaths] = useState<PathInfo[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);
  const [retryCount, setRetryCount] = useState(0);
  const retryTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  // Check if cache is valid
  const isCacheValid = useCallback(() => {
    if (!discoveryCache) return false;
    return Date.now() - discoveryCache.timestamp < DISCOVERY_CACHE_TTL;
  }, []);

  const fetchPaths = useCallback(async (attempt = 0): Promise<void> => {
    // Use cache if valid
    if (attempt === 0 && isCacheValid() && discoveryCache) {
      setPaths(discoveryCache.paths);
      setLoading(false);
      return;
    }

    setLoading(true);
    try {
      const response = await apiClient.get<{
        paths: string[];
        stats: {
          registered_nodes: number;
          contexts: string[];
        };
      }>('/agentese/discover');

      // Transform flat paths to PathInfo
      const pathInfos: PathInfo[] = response.data.paths.map((p) => ({
        path: p,
        context: p.split('.')[0] as PathInfo['context'],
        aspects: ['manifest'], // Default - actual aspects come from individual path queries
      }));

      // Update cache
      discoveryCache = {
        paths: pathInfos,
        timestamp: Date.now(),
      };

      setPaths(pathInfos);
      setError(null);
      setRetryCount(0);
    } catch (e) {
      const err = e as Error;
      setError(err);

      // Retry with exponential backoff if we haven't exceeded max retries
      if (attempt < MAX_DISCOVERY_RETRIES) {
        const delay = getBackoffDelay(attempt);
        console.warn(
          `[NavigationTree] Discovery failed, retrying in ${Math.round(delay)}ms (attempt ${attempt + 1}/${MAX_DISCOVERY_RETRIES})`
        );

        retryTimeoutRef.current = setTimeout(() => {
          setRetryCount(attempt + 1);
          fetchPaths(attempt + 1);
        }, delay);
      } else {
        // Use fallback paths after all retries exhausted
        console.warn('[NavigationTree] Discovery failed after max retries, using fallback paths');
        const fallbackPaths = CROWN_JEWELS.map((j) => ({
          path: j.path,
          context: j.path.split('.')[0] as PathInfo['context'],
          aspects: ['manifest'],
        }));
        setPaths(fallbackPaths);
      }
    } finally {
      setLoading(false);
    }
  }, [isCacheValid]);

  // Cleanup retry timeout on unmount
  useEffect(() => {
    return () => {
      if (retryTimeoutRef.current) {
        clearTimeout(retryTimeoutRef.current);
      }
    };
  }, []);

  useEffect(() => {
    fetchPaths();
  }, [fetchPaths]);

  return { paths, loading, error, retryCount, refetch: () => fetchPaths(0) };
}

/**
 * Build tree structure from flat paths.
 */
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
          isLeaf: false,
        });
      }

      const node = currentLevel.get(segment)!;

      // Mark as leaf and add metadata for final segment
      if (i === segments.length - 1) {
        node.isLeaf = true;
        node.description = pathInfo.description;
        node.aspects = pathInfo.aspects;
      }

      currentLevel = node.children;
    }
  }

  return root;
}

// =============================================================================
// Subcomponents
// =============================================================================

/** Tree node item */
const TreeNodeItem = memo(function TreeNodeItem({
  node,
  level,
  expandedPaths,
  currentPath,
  onToggle,
  onNavigate,
}: {
  node: TreeNode;
  level: number;
  expandedPaths: Set<string>;
  currentPath: string;
  onToggle: (path: string) => void;
  onNavigate: (path: string) => void;
}) {
  const hasChildren = node.children.size > 0;
  const isExpanded = expandedPaths.has(node.path);
  const isActive = currentPath === node.path || currentPath.startsWith(`${node.path}.`);
  const isExactMatch = currentPath === node.path;

  // Context info for top-level nodes
  const contextInfo = level === 0 ? CONTEXT_INFO[node.segment] : null;
  const Icon = contextInfo?.icon || ChevronRight;

  const handleClick = () => {
    if (hasChildren) {
      onToggle(node.path);
    }
    if (node.isLeaf) {
      onNavigate(node.path);
    }
  };

  return (
    <div>
      <button
        onClick={handleClick}
        className={`
          w-full flex items-center gap-2 px-3 py-1.5 text-sm
          hover:bg-gray-700/50 transition-colors rounded-md
          ${isExactMatch ? 'bg-gray-700/70 text-white' : 'text-gray-300'}
          ${isActive && !isExactMatch ? 'text-gray-200' : ''}
        `}
        style={{ paddingLeft: `${12 + level * 16}px` }}
      >
        {/* Expand/collapse icon */}
        {hasChildren ? (
          <motion.span
            animate={{ rotate: isExpanded ? 90 : 0 }}
            transition={{ duration: 0.15 }}
            className="flex-shrink-0"
          >
            <ChevronRight className="w-3 h-3 text-gray-500" />
          </motion.span>
        ) : (
          <span className="w-3" /> // Spacer
        )}

        {/* Icon for contexts */}
        {contextInfo && (
          <Icon className={`w-4 h-4 ${contextInfo.color}`} />
        )}

        {/* Label */}
        <span className="truncate">{node.segment}</span>

        {/* Leaf indicator */}
        {node.isLeaf && !hasChildren && (
          <span className="ml-auto text-xs text-gray-500">
            {node.aspects?.length || 0}
          </span>
        )}
      </button>

      {/* Children */}
      <AnimatePresence>
        {hasChildren && isExpanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.15 }}
            className="overflow-hidden"
          >
            {Array.from(node.children.values()).map((child) => (
              <TreeNodeItem
                key={child.path}
                node={child}
                level={level + 1}
                expandedPaths={expandedPaths}
                currentPath={currentPath}
                onToggle={onToggle}
                onNavigate={onNavigate}
              />
            ))}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
});

/** Crown Jewels shortcuts section */
function CrownJewelsSection({
  currentRoute,
  onNavigate,
}: {
  currentRoute: string;
  onNavigate: (route: string) => void;
}) {
  return (
    <div className="border-t border-gray-700/50 pt-3">
      <h3 className="px-3 mb-2 text-xs font-medium text-gray-500 uppercase tracking-wider">
        Crown Jewels
      </h3>
      <div className="space-y-0.5">
        {CROWN_JEWELS.map((jewel) => {
          const isActive = currentRoute === jewel.route ||
            currentRoute.startsWith(`${jewel.route}/`);
          const color = JEWEL_COLORS[jewel.name];
          const Icon = jewel.icon;

          return (
            <button
              key={jewel.name}
              onClick={() => onNavigate(jewel.route)}
              className={`
                w-full flex items-center gap-2 px-3 py-1.5 text-sm
                hover:bg-gray-700/50 transition-colors rounded-md
                ${isActive ? 'bg-gray-700/70' : ''}
              `}
            >
              <Icon
                className="w-4 h-4"
                style={{ color: color.primary }}
              />
              <span className={isActive ? 'text-white' : 'text-gray-300'}>
                {jewel.label}
              </span>
              <span className="ml-auto text-xs text-gray-500 font-mono">
                {jewel.path}
              </span>
            </button>
          );
        })}
      </div>
    </div>
  );
}

/** Gallery shortcuts section */
function GallerySection({
  currentRoute,
  onNavigate,
}: {
  currentRoute: string;
  onNavigate: (route: string) => void;
}) {
  const galleries = [
    { route: '/gallery', label: 'Projection Gallery' },
    { route: '/gallery/layout', label: 'Layout Gallery' },
  ];

  return (
    <div className="border-t border-gray-700/50 pt-3">
      <h3 className="px-3 mb-2 text-xs font-medium text-gray-500 uppercase tracking-wider">
        Gallery
      </h3>
      <div className="space-y-0.5">
        {galleries.map((gallery) => {
          const isActive = currentRoute === gallery.route;
          return (
            <button
              key={gallery.route}
              onClick={() => onNavigate(gallery.route)}
              className={`
                w-full flex items-center gap-2 px-3 py-1.5 text-sm
                hover:bg-gray-700/50 transition-colors rounded-md
                ${isActive ? 'bg-gray-700/70 text-white' : 'text-gray-300'}
              `}
            >
              <Layers className="w-4 h-4 text-gray-400" />
              <span>{gallery.label}</span>
            </button>
          );
        })}
      </div>
    </div>
  );
}

// =============================================================================
// Main Component
// =============================================================================

/**
 * NavigationTree - Sidebar tree navigation for AGENTESE ontology.
 *
 * Adapts to density:
 * - spacious: Full sidebar, always visible
 * - comfortable: Collapsible sidebar, toggle button
 * - compact: Hamburger menu, bottom drawer
 *
 * @example
 * ```tsx
 * // In Shell layout
 * <NavigationTree />
 * ```
 */
export function NavigationTree({ className = '' }: NavigationTreeProps) {
  const {
    density,
    navigationTreeExpanded,
    setNavigationTreeExpanded,
  } = useShell();
  const navigate = useNavigate();
  const location = useLocation();
  const { shouldAnimate } = useMotionPreferences();
  const { paths, loading } = useDiscovery();

  // Build tree from paths
  const tree = useMemo(() => buildTree(paths), [paths]);

  // Track expanded paths in tree
  const [expandedPaths, setExpandedPaths] = useState<Set<string>>(() => {
    // Default: expand all contexts
    return new Set(['world', 'self', 'concept', 'void', 'time']);
  });

  // Current AGENTESE path (derived from route)
  const currentPath = useMemo(() => {
    // Map routes to AGENTESE paths
    const routeToPath: Record<string, string> = {
      '/brain': 'self.memory',
      '/gestalt': 'world.codebase',
      '/gestalt/live': 'world.gestalt.live',
      '/gardener': 'concept.gardener',
      '/atelier': 'world.atelier',
      '/town': 'world.town',
      '/park': 'world.park',
      '/workshop': 'world.domain',
      '/emergence': 'world.emergence',
    };
    return routeToPath[location.pathname] || '';
  }, [location.pathname]);

  // Toggle tree node expansion
  const handleToggle = useCallback((path: string) => {
    setExpandedPaths((prev) => {
      const next = new Set(prev);
      if (next.has(path)) {
        next.delete(path);
      } else {
        next.add(path);
      }
      return next;
    });
  }, []);

  // Navigate to AGENTESE path
  const handleNavigateToPath = useCallback((path: string) => {
    // Map AGENTESE paths to routes
    const pathToRoute: Record<string, string> = {
      'self.memory': '/brain',
      'world.codebase': '/gestalt',
      'world.gestalt.live': '/gestalt/live',
      'concept.gardener': '/gardener',
      'world.atelier': '/atelier',
      'world.town': '/town',
      'world.park': '/park',
      'world.domain': '/workshop',
      'world.emergence': '/emergence',
    };
    const route = pathToRoute[path];
    if (route) {
      navigate(route);
      // Close on mobile after navigation
      if (density === 'compact') {
        setNavigationTreeExpanded(false);
      }
    }
  }, [navigate, density, setNavigationTreeExpanded]);

  // Navigate to route directly
  const handleNavigateToRoute = useCallback((route: string) => {
    navigate(route);
    // Close on mobile after navigation
    if (density === 'compact') {
      setNavigationTreeExpanded(false);
    }
  }, [navigate, density, setNavigationTreeExpanded]);

  // Sidebar width
  const width = SIDEBAR_WIDTH[density];

  // Compact: Hamburger button + bottom drawer
  if (density === 'compact') {
    return (
      <>
        {/* Hamburger button - rendered in header */}
        <button
          onClick={() => setNavigationTreeExpanded(true)}
          className="fixed top-0 left-0 z-50 p-3 bg-gray-800/80 backdrop-blur-sm"
          aria-label="Open navigation"
        >
          <Menu className="w-5 h-5 text-gray-400" />
        </button>

        {/* Bottom drawer */}
        <AnimatePresence>
          {navigationTreeExpanded && (
            <>
              {/* Backdrop */}
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                transition={{ duration: shouldAnimate ? 0.2 : 0 }}
                className="fixed inset-0 z-40 bg-black/50"
                onClick={() => setNavigationTreeExpanded(false)}
              />

              {/* Drawer */}
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
                {/* Handle */}
                <div className="sticky top-0 flex justify-center pt-2 pb-1 bg-gray-800">
                  <div className="w-10 h-1 rounded-full bg-gray-600" />
                </div>

                {/* Close button */}
                <button
                  onClick={() => setNavigationTreeExpanded(false)}
                  className="absolute top-2 right-2 p-2 hover:bg-gray-700 rounded-full"
                  aria-label="Close navigation"
                >
                  <X className="w-5 h-5 text-gray-400" />
                </button>

                {/* Content */}
                <div className="p-4 space-y-4">
                  <h2 className="text-sm font-semibold text-white">AGENTESE Paths</h2>
                  {loading ? (
                    <div className="py-4 text-center text-gray-500 text-sm">
                      Loading paths...
                    </div>
                  ) : (
                    <div className="space-y-1">
                      {Array.from(tree.values()).map((node) => (
                        <TreeNodeItem
                          key={node.path}
                          node={node}
                          level={0}
                          expandedPaths={expandedPaths}
                          currentPath={currentPath}
                          onToggle={handleToggle}
                          onNavigate={handleNavigateToPath}
                        />
                      ))}
                    </div>
                  )}

                  <CrownJewelsSection
                    currentRoute={location.pathname}
                    onNavigate={handleNavigateToRoute}
                  />

                  <GallerySection
                    currentRoute={location.pathname}
                    onNavigate={handleNavigateToRoute}
                  />
                </div>
              </motion.div>
            </>
          )}
        </AnimatePresence>
      </>
    );
  }

  // Comfortable: Collapsible sidebar
  if (density === 'comfortable') {
    return (
      <>
        {/* Toggle button */}
        {!navigationTreeExpanded && (
          <button
            onClick={() => setNavigationTreeExpanded(true)}
            className="fixed left-0 top-1/2 -translate-y-1/2 z-30 p-2 bg-gray-800/80 backdrop-blur-sm rounded-r-lg border border-l-0 border-gray-700/50 hover:bg-gray-700 transition-colors"
            aria-label="Open navigation sidebar"
          >
            <ChevronRight className="w-4 h-4 text-gray-400" />
          </button>
        )}

        {/* Sidebar */}
        <AnimatePresence>
          {navigationTreeExpanded && (
            <motion.aside
              initial={{ x: -(width || 240), opacity: 0 }}
              animate={{ x: 0, opacity: 1 }}
              exit={{ x: -(width || 240), opacity: 0 }}
              transition={{ duration: shouldAnimate ? 0.2 : 0, ease: 'easeOut' }}
              style={{ width: width || 240 }}
              className={`
                fixed left-0 top-10 bottom-0 z-30
                bg-gray-800/95 backdrop-blur-sm
                border-r border-gray-700/50
                overflow-y-auto
                ${className}
              `}
            >
              {/* Close button */}
              <button
                onClick={() => setNavigationTreeExpanded(false)}
                className="absolute top-2 right-2 p-1 hover:bg-gray-700 rounded"
                aria-label="Close navigation sidebar"
              >
                <X className="w-4 h-4 text-gray-400" />
              </button>

              {/* Content */}
              <div className="p-3 pt-8 space-y-4">
                <h2 className="px-3 text-xs font-medium text-gray-500 uppercase tracking-wider">
                  AGENTESE Paths
                </h2>
                {loading ? (
                  <div className="py-4 text-center text-gray-500 text-sm">
                    Loading...
                  </div>
                ) : (
                  <div className="space-y-1">
                    {Array.from(tree.values()).map((node) => (
                      <TreeNodeItem
                        key={node.path}
                        node={node}
                        level={0}
                        expandedPaths={expandedPaths}
                        currentPath={currentPath}
                        onToggle={handleToggle}
                        onNavigate={handleNavigateToPath}
                      />
                    ))}
                  </div>
                )}

                <CrownJewelsSection
                  currentRoute={location.pathname}
                  onNavigate={handleNavigateToRoute}
                />

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

  // Spacious: Fixed sidebar
  return (
    <aside
      style={{ width: width || 280 }}
      className={`
        flex-shrink-0 h-full
        bg-gray-800/50
        border-r border-gray-700/50
        overflow-y-auto
        ${className}
      `}
    >
      <div className="p-3 space-y-4">
        <h2 className="px-3 text-xs font-medium text-gray-500 uppercase tracking-wider">
          AGENTESE Paths
        </h2>
        {loading ? (
          <div className="py-4 text-center text-gray-500 text-sm">
            Loading paths...
          </div>
        ) : (
          <div className="space-y-1">
            {Array.from(tree.values()).map((node) => (
              <TreeNodeItem
                key={node.path}
                node={node}
                level={0}
                expandedPaths={expandedPaths}
                currentPath={currentPath}
                onToggle={handleToggle}
                onNavigate={handleNavigateToPath}
              />
            ))}
          </div>
        )}

        <CrownJewelsSection
          currentRoute={location.pathname}
          onNavigate={handleNavigateToRoute}
        />

        <GallerySection
          currentRoute={location.pathname}
          onNavigate={handleNavigateToRoute}
        />
      </div>
    </aside>
  );
}

export default NavigationTree;
