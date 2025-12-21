/**
 * ContextOverviewProjection - Gateway to an AGENTESE Context
 *
 * When navigating to a context-level path (e.g., /self, /world), this component
 * provides a warm, inviting overview of all paths within that context.
 *
 * "The context overview should feel like arriving at a garden's main gate -
 * you see all the paths you can explore, with warm, inviting copy."
 * — AD-010: The Habitat Guarantee
 *
 * @see spec/protocols/agentese-as-route.md
 * @see spec/principles.md - AD-010
 */

import { useState, useEffect, useMemo, memo, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { ChevronRight, Loader2 } from 'lucide-react';
import { apiClient } from '@/api/client';
import { CONTEXT_INFO, getContextInfo } from '@/constants/contexts';
import { formatPathLabel } from '@/utils/parseAgentesePath';
import { useShell } from '@/shell/ShellProvider';
import { useMotionPreferences } from '@/components/joy/useMotionPreferences';
import type { AgenteseContext } from '@/utils/parseAgentesePath';

// =============================================================================
// Types
// =============================================================================

export interface ContextOverviewProjectionProps {
  /** The context to display (world, self, concept, void, time) */
  context: AgenteseContext;
}

interface DiscoveredPath {
  path: string;
  description?: string;
  aspects?: string[];
}

// =============================================================================
// Constants
// =============================================================================

/**
 * Welcome messages for each context - warm, inviting, garden-like
 */
const CONTEXT_WELCOME: Record<AgenteseContext, string> = {
  world: "The external realm of entities, environments, and tools. Here lie the towns, parks, and forges where agents interact with the world around them.",
  self: "The inner landscape of memory, soul, and capability. This is where reflection happens, where memories crystallize, and where the soul speaks.",
  concept: "The abstract plane of definitions, logic, and platonic forms. Here ideas take shape, grammar is defined, and principles are established.",
  void: "The accursed share—entropy, serendipity, and gratitude. The void embraces uncertainty and transforms it into creative possibility.",
  time: "The temporal dimension of traces, forecasts, and schedules. Here the past meets the future through différance and temporal navigation.",
};

/**
 * Density-aware spacing
 */
const DENSITY_CONFIG = {
  compact: {
    gridCols: 'grid-cols-1',
    cardPadding: 'p-3',
    gap: 'gap-3',
    headerPadding: 'p-4',
  },
  comfortable: {
    gridCols: 'grid-cols-1 md:grid-cols-2',
    cardPadding: 'p-4',
    gap: 'gap-4',
    headerPadding: 'p-6',
  },
  spacious: {
    gridCols: 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3',
    cardPadding: 'p-5',
    gap: 'gap-5',
    headerPadding: 'p-8',
  },
};

// =============================================================================
// Sub-components
// =============================================================================

/**
 * A single path card - clickable, with hover animation
 */
const PathCard = memo(function PathCard({
  path,
  description,
  contextColor,
  onClick,
}: {
  path: string;
  description?: string;
  contextColor: string;
  onClick: () => void;
}) {
  const { shouldAnimate } = useMotionPreferences();
  const { density } = useShell();
  const config = DENSITY_CONFIG[density];

  // Extract the display name from the path
  const label = formatPathLabel(path);

  // Get the path segments after context
  const segments = path.split('.');
  const displayPath = segments.slice(1).join('.');

  return (
    <motion.button
      onClick={onClick}
      className={`
        w-full text-left ${config.cardPadding}
        bg-gray-800/40 hover:bg-gray-800/60
        border border-gray-700/50 hover:border-gray-600/50
        rounded-lg transition-colors
        group cursor-pointer
      `}
      whileHover={shouldAnimate ? { scale: 1.01, y: -2 } : {}}
      whileTap={shouldAnimate ? { scale: 0.99 } : {}}
    >
      <div className="flex items-start justify-between gap-3">
        <div className="flex-1 min-w-0">
          {/* Path label */}
          <h3 className={`font-medium text-gray-100 group-hover:${contextColor} transition-colors`}>
            {label}
          </h3>

          {/* Full path */}
          <code className="text-xs text-gray-500 font-mono block mt-1 truncate">
            {displayPath || path}
          </code>

          {/* Description if available */}
          {description && (
            <p className="text-sm text-gray-400 mt-2 line-clamp-2">
              {description}
            </p>
          )}
        </div>

        {/* Arrow indicator */}
        <ChevronRight
          className={`
            w-5 h-5 text-gray-600 group-hover:${contextColor}
            transform group-hover:translate-x-1 transition-all
            flex-shrink-0 mt-0.5
          `}
        />
      </div>
    </motion.button>
  );
});

/**
 * Loading state for the context overview
 */
const ContextLoading = memo(function ContextLoading({
  context
}: {
  context: AgenteseContext
}) {
  const info = getContextInfo(context);

  return (
    <div className="flex flex-col items-center justify-center min-h-[40vh] p-8">
      <motion.div
        animate={{
          scale: [1, 1.1, 1],
          opacity: [0.6, 1, 0.6],
        }}
        transition={{
          duration: 2,
          repeat: Infinity,
          ease: 'easeInOut',
        }}
      >
        <Loader2 className={`w-12 h-12 ${info.color} animate-spin`} />
      </motion.div>
      <p className="mt-4 text-gray-400">
        Discovering paths in {info.label}...
      </p>
    </div>
  );
});

// =============================================================================
// Main Component
// =============================================================================

/**
 * ContextOverviewProjection - The main gate to an AGENTESE context
 *
 * Renders a warm, inviting overview of all registered paths within a context.
 * Uses the /agentese/discover endpoint with context filtering.
 *
 * @example
 * <ContextOverviewProjection context="self" />
 */
export const ContextOverviewProjection = memo(function ContextOverviewProjection({
  context,
}: ContextOverviewProjectionProps) {
  const navigate = useNavigate();
  const { density } = useShell();
  const { shouldAnimate } = useMotionPreferences();
  const config = DENSITY_CONFIG[density];

  // State
  const [paths, setPaths] = useState<DiscoveredPath[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  // Get context metadata
  const contextInfo = useMemo(() => CONTEXT_INFO[context], [context]);
  const Icon = contextInfo.icon;

  // Fetch paths for this context
  useEffect(() => {
    let mounted = true;

    async function fetchPaths() {
      try {
        setLoading(true);
        setError(null);

        const response = await apiClient.get<{
          paths: string[];
          stats: { registered_nodes: number; contexts: string[] };
        }>('/agentese/discover', {
          params: { context },
        });

        if (!mounted) return;

        // Filter and format paths
        const discoveredPaths: DiscoveredPath[] = response.data.paths
          .filter((p) => p.startsWith(context + '.'))
          .map((p) => ({ path: p }));

        setPaths(discoveredPaths);
        setLoading(false);

        // Optionally fetch descriptions in background
        // (Could add this later if needed)
      } catch (e) {
        if (!mounted) return;
        setError(e as Error);
        setLoading(false);
      }
    }

    fetchPaths();

    return () => {
      mounted = false;
    };
  }, [context]);

  // Handle path click
  const handlePathClick = useCallback(
    (path: string) => {
      navigate(`/${path}`);
    },
    [navigate]
  );

  // Group paths by their first sub-segment (holon)
  const groupedPaths = useMemo(() => {
    const groups = new Map<string, DiscoveredPath[]>();

    for (const pathInfo of paths) {
      const segments = pathInfo.path.split('.');
      // Get the holon (first segment after context)
      const holon = segments.length > 1 ? segments[1] : '';

      const existing = groups.get(holon);
      if (existing) {
        existing.push(pathInfo);
      } else {
        groups.set(holon, [pathInfo]);
      }
    }

    return groups;
  }, [paths]);

  // Loading state
  if (loading) {
    return <ContextLoading context={context} />;
  }

  // Error state
  if (error) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[40vh] p-8 text-center">
        <p className="text-red-400 mb-2">Failed to discover paths</p>
        <code className="text-sm text-gray-500">{error.message}</code>
      </div>
    );
  }

  return (
    <div className="h-full overflow-auto bg-surface-canvas">
      <div className={`max-w-5xl mx-auto ${config.headerPadding}`}>
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: shouldAnimate ? 0.3 : 0 }}
          className="mb-8"
        >
          {/* Context icon and title */}
          <div className="flex items-center gap-4 mb-4">
            <div className={`p-4 rounded-xl ${contextInfo.bgColor}`}>
              <Icon className={`w-10 h-10 ${contextInfo.color}`} />
            </div>
            <div>
              <h1 className={`text-3xl font-bold ${contextInfo.color}`}>
                {contextInfo.label}
              </h1>
              <code className="text-sm text-gray-500 font-mono">
                {context}.*
              </code>
            </div>
          </div>

          {/* Welcome message */}
          <p className="text-gray-300 text-lg leading-relaxed max-w-2xl">
            {CONTEXT_WELCOME[context]}
          </p>

          {/* Stats */}
          <div className="mt-4 flex items-center gap-4 text-sm text-gray-500">
            <span>{paths.length} registered paths</span>
            <span className="w-1 h-1 rounded-full bg-gray-600" />
            <span>{groupedPaths.size} holons</span>
          </div>
        </motion.div>

        {/* Path list */}
        {paths.length === 0 ? (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="text-center py-12"
          >
            <p className="text-gray-400">
              No paths registered in this context yet.
            </p>
            <p className="text-sm text-gray-500 mt-2">
              This garden awaits cultivation.
            </p>
          </motion.div>
        ) : (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: shouldAnimate ? 0.3 : 0, delay: 0.1 }}
            className={`grid ${config.gridCols} ${config.gap}`}
          >
            {Array.from(groupedPaths.entries()).map(([holon, holonPaths]) => (
              <div key={holon} className="space-y-3">
                {/* Holon header */}
                <h2 className="text-sm font-medium text-gray-400 uppercase tracking-wide px-1">
                  {holon || 'Root'}
                </h2>

                {/* Paths in this holon */}
                <div className="space-y-2">
                  {holonPaths.map((pathInfo) => (
                    <PathCard
                      key={pathInfo.path}
                      path={pathInfo.path}
                      description={pathInfo.description}
                      contextColor={contextInfo.color}
                      onClick={() => handlePathClick(pathInfo.path)}
                    />
                  ))}
                </div>
              </div>
            ))}
          </motion.div>
        )}
      </div>
    </div>
  );
});

export default ContextOverviewProjection;
