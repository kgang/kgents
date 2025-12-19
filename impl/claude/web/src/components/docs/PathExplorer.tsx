/**
 * PathExplorer - Navigate AGENTESE paths like a filesystem.
 *
 * Grouped by the five contexts:
 * - world.* (green) - The External
 * - self.* (cyan) - The Internal
 * - concept.* (violet) - The Abstract
 * - void.* (pink) - The Accursed Share
 * - time.* (amber) - The Temporal
 */

import { useState, useMemo, useCallback, useEffect, memo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Globe,
  User,
  BookOpen,
  Sparkles,
  Clock,
  ChevronRight,
  Search,
  type LucideIcon,
} from 'lucide-react';
import type { Density } from '@/hooks/useDesignPolynomial';
import type { PathMetadata } from './useAgenteseDiscovery';
import { Shimmer } from '@/components/joy';

// =============================================================================
// Types
// =============================================================================

interface PathExplorerProps {
  paths: string[];
  metadata: Record<string, PathMetadata>;
  selectedPath: string | null;
  onSelectPath: (path: string) => void;
  loading?: boolean;
  error?: string | null;
  density: Density;
}

interface TreeNode {
  segment: string;
  path: string;
  children: Map<string, TreeNode>;
  isRegistered: boolean;
  metadata?: PathMetadata;
}

// =============================================================================
// Context Configuration
// =============================================================================

interface ContextInfo {
  icon: LucideIcon;
  label: string;
  description: string;
  color: string;
  bgColor: string;
}

const CONTEXTS: Record<string, ContextInfo> = {
  world: {
    icon: Globe,
    label: 'World',
    description: 'External entities and environments',
    color: 'text-green-400',
    bgColor: 'bg-green-500/10',
  },
  self: {
    icon: User,
    label: 'Self',
    description: 'Internal memory and capability',
    color: 'text-cyan-400',
    bgColor: 'bg-cyan-500/10',
  },
  concept: {
    icon: BookOpen,
    label: 'Concept',
    description: 'Abstract definitions and logic',
    color: 'text-violet-400',
    bgColor: 'bg-violet-500/10',
  },
  void: {
    icon: Sparkles,
    label: 'Void',
    description: 'Entropy and serendipity',
    color: 'text-pink-400',
    bgColor: 'bg-pink-500/10',
  },
  time: {
    icon: Clock,
    label: 'Time',
    description: 'Traces and schedules',
    color: 'text-amber-400',
    bgColor: 'bg-amber-500/10',
  },
};

// =============================================================================
// Component
// =============================================================================

export const PathExplorer = memo(function PathExplorer({
  paths,
  metadata,
  selectedPath,
  onSelectPath,
  loading = false,
  error = null,
  density,
}: PathExplorerProps) {
  const [expandedPaths, setExpandedPaths] = useState<Set<string>>(new Set());
  const [searchQuery, setSearchQuery] = useState('');
  const [debouncedQuery, setDebouncedQuery] = useState('');

  // Debounce search query (300ms) for performance with large path lists
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedQuery(searchQuery);
    }, 300);
    return () => clearTimeout(timer);
  }, [searchQuery]);

  // Build tree structure from flat paths
  const tree = useMemo(() => buildTree(paths, metadata), [paths, metadata]);

  // Filter paths by search query (uses debounced value for performance)
  const filteredPaths = useMemo(() => {
    if (!debouncedQuery.trim()) return paths;
    const query = debouncedQuery.toLowerCase();
    return paths.filter((p) => p.toLowerCase().includes(query));
  }, [paths, debouncedQuery]);

  // Group by context
  const groupedPaths = useMemo(() => {
    const groups: Record<string, string[]> = {
      world: [],
      self: [],
      concept: [],
      void: [],
      time: [],
    };

    for (const path of filteredPaths) {
      const context = path.split('.')[0];
      if (context in groups) {
        groups[context].push(path);
      }
    }

    return groups;
  }, [filteredPaths]);

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

  // Auto-expand to selected path
  // NOTE: This is useEffect, not useMemo—useMemo with side effects is an anti-pattern
  useEffect(() => {
    if (!selectedPath) return;
    const segments = selectedPath.split('.');
    const pathsToExpand: string[] = [];
    for (let i = 1; i <= segments.length; i++) {
      pathsToExpand.push(segments.slice(0, i).join('.'));
    }
    setExpandedPaths((prev) => {
      const next = new Set(prev);
      pathsToExpand.forEach((p) => next.add(p));
      return next;
    });
  }, [selectedPath]);

  if (loading) {
    return (
      <div className="p-4 space-y-4">
        {[1, 2, 3, 4, 5].map((i) => (
          <Shimmer key={i}>
            <div className="h-8 bg-gray-700 rounded-md" />
          </Shimmer>
        ))}
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-4 text-center">
        <div className="text-pink-400 mb-2">Failed to load paths</div>
        <div className="text-gray-500 text-sm">{error}</div>
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col">
      {/* Search */}
      <div className="p-3 border-b border-gray-700">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search paths..."
            className="w-full pl-9 pr-4 py-2 bg-gray-700/50 rounded-lg text-sm
                       placeholder-gray-500 text-white
                       focus:outline-none focus:ring-1 focus:ring-cyan-500/50"
          />
        </div>
      </div>

      {/* Path Tree */}
      <div className="flex-1 overflow-y-auto p-2">
        {Object.entries(CONTEXTS).map(([contextKey, contextInfo]) => {
          const contextPaths = groupedPaths[contextKey] || [];
          if (contextPaths.length === 0 && searchQuery) return null;

          const contextNode = tree.get(contextKey);
          const isExpanded = expandedPaths.has(contextKey);
          const Icon = contextInfo.icon;

          return (
            <div key={contextKey} className="mb-2">
              {/* Context header */}
              <button
                onClick={() => handleToggle(contextKey)}
                className={`
                  w-full flex items-center gap-2 px-3 py-2 rounded-lg
                  transition-colors group
                  ${isExpanded ? contextInfo.bgColor : 'hover:bg-gray-700/30'}
                `}
              >
                <motion.span
                  animate={{ rotate: isExpanded ? 90 : 0 }}
                  transition={{ duration: 0.15 }}
                >
                  <ChevronRight className="w-4 h-4 text-gray-500" />
                </motion.span>
                <Icon className={`w-5 h-5 ${contextInfo.color}`} />
                <span className={`font-medium ${contextInfo.color}`}>{contextInfo.label}</span>
                <span className="ml-auto text-xs text-gray-500">{contextPaths.length}</span>
              </button>

              {/* Context children */}
              <AnimatePresence>
                {isExpanded && contextNode && (
                  <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: 'auto', opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    transition={{ duration: 0.15 }}
                    className="overflow-hidden ml-6"
                  >
                    {Array.from(contextNode.children.values()).map((child) => (
                      <PathNode
                        key={child.path}
                        node={child}
                        level={1}
                        expandedPaths={expandedPaths}
                        selectedPath={selectedPath}
                        onToggle={handleToggle}
                        onSelect={onSelectPath}
                        density={density}
                        contextColor={contextInfo.color}
                      />
                    ))}
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          );
        })}

        {filteredPaths.length === 0 && debouncedQuery && (
          <div className="text-center text-gray-500 py-8">No paths match "{debouncedQuery}"</div>
        )}
      </div>
    </div>
  );
});

// =============================================================================
// Subcomponents
// =============================================================================

interface PathNodeProps {
  node: TreeNode;
  level: number;
  expandedPaths: Set<string>;
  selectedPath: string | null;
  onToggle: (path: string) => void;
  onSelect: (path: string) => void;
  density: Density;
  contextColor: string;
}

const PathNode = memo(function PathNode({
  node,
  level,
  expandedPaths,
  selectedPath,
  onToggle,
  onSelect,
  density,
  contextColor,
}: PathNodeProps) {
  const hasChildren = node.children.size > 0;
  const isExpanded = expandedPaths.has(node.path);
  const isSelected = selectedPath === node.path;
  const canNavigate = node.isRegistered;

  const handleClick = () => {
    if (canNavigate) {
      onSelect(node.path);
    } else if (hasChildren) {
      onToggle(node.path);
    }
  };

  return (
    <div>
      <button
        onClick={handleClick}
        className={`
          w-full flex items-center gap-2 py-1.5 px-2 rounded-md text-sm
          transition-colors text-left
          ${isSelected ? 'bg-cyan-900/40 ring-1 ring-cyan-500/30' : ''}
          ${canNavigate ? 'hover:bg-gray-700/50 cursor-pointer' : 'cursor-default'}
        `}
        style={{ paddingLeft: `${8 + level * 12}px` }}
      >
        {hasChildren && (
          <motion.span
            animate={{ rotate: isExpanded ? 90 : 0 }}
            transition={{ duration: 0.15 }}
            onClick={(e) => {
              e.stopPropagation();
              onToggle(node.path);
            }}
            className="hover:bg-gray-600/50 rounded p-0.5"
          >
            <ChevronRight className="w-3 h-3 text-gray-500" />
          </motion.span>
        )}
        {!hasChildren && <span className="w-4" />}

        {/* Path marker */}
        {canNavigate && (
          <span
            className={`w-1.5 h-1.5 rounded-full ${
              isSelected
                ? 'bg-cyan-400'
                : contextColor.replace('text-', 'bg-').replace('400', '500/50')
            }`}
          />
        )}

        <span
          className={`truncate ${
            isSelected ? 'text-white font-medium' : canNavigate ? 'text-gray-300' : 'text-gray-500'
          }`}
        >
          {node.segment}
        </span>

        {/* Aspect count badge */}
        {node.metadata && density !== 'compact' && (
          <span className="ml-auto text-xs text-gray-500">{node.metadata.aspects.length}</span>
        )}
      </button>

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
              <PathNode
                key={child.path}
                node={child}
                level={level + 1}
                expandedPaths={expandedPaths}
                selectedPath={selectedPath}
                onToggle={onToggle}
                onSelect={onSelect}
                density={density}
                contextColor={contextColor}
              />
            ))}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
});

// =============================================================================
// Helpers
// =============================================================================

function buildTree(paths: string[], metadata: Record<string, PathMetadata>): Map<string, TreeNode> {
  const root = new Map<string, TreeNode>();

  for (const path of paths) {
    const segments = path.split('.');
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

      const node = currentLevel.get(segment)!;

      if (i === segments.length - 1) {
        node.isRegistered = true;
        node.metadata = metadata[path];
      }

      currentLevel = node.children;
    }
  }

  return root;
}

export default PathExplorer;
