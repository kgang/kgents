/**
 * GestaltTree - Living Architecture Navigator
 *
 * A hierarchical tree view of codebase modules with health metrics.
 * Combines NavigationTree's navigation patterns with Living Earth aesthetic.
 *
 * Features:
 * - Hybrid toggle: Layer-first (default) vs Full-path views
 * - Health aggregation: Worst grade bubbles up
 * - Violation propagation: Warnings visible at ancestor nodes
 * - Breathing animation: Healthy nodes pulse subtly
 * - Density-adaptive: Compact/comfortable/spacious
 *
 * @see creative/crown-jewels-genesis-moodboard.md - Visual aesthetic
 * @see impl/claude/web/src/shell/NavigationTree.tsx - Pattern source
 */

import { useState, useMemo, useCallback } from 'react';
import { Layers, FolderTree, Network } from 'lucide-react';
import { useShell } from '@/shell';
import { Breathe } from '@/components/joy';
import { buildLayerTree, buildPathTree } from './buildGestaltTree';
import { GestaltTreeNode } from './GestaltTreeNode';
import { HealthBadgeLarge } from './HealthBadge';
import type { GestaltTreeProps, TreeMode, GestaltNode } from './types';
import { getWorstGrade } from './types';

// =============================================================================
// Helper Functions
// =============================================================================

/**
 * Get all parent paths that should be expanded by default.
 * For spacious density, expand first 2 levels.
 */
function getDefaultExpanded(tree: Map<string, GestaltNode>, depth: number): Set<string> {
  const expanded = new Set<string>();

  function traverse(nodes: Map<string, GestaltNode>, currentDepth: number) {
    if (currentDepth >= depth) return;

    for (const node of nodes.values()) {
      expanded.add(node.path);
      if (node.children.size > 0) {
        traverse(node.children, currentDepth + 1);
      }
    }
  }

  traverse(tree, 0);
  return expanded;
}

/**
 * Calculate aggregate stats for the header.
 */
function calculateTreeStats(tree: Map<string, GestaltNode>) {
  let totalModules = 0;
  let totalViolations = 0;
  let totalLoC = 0;
  const grades: string[] = [];

  for (const node of tree.values()) {
    totalModules += node.moduleCount;
    totalViolations += node.violationCount;
    totalLoC += node.linesOfCode;
    grades.push(node.healthGrade);
  }

  const overallGrade = getWorstGrade(grades);
  const healthyCount = Array.from(tree.values()).filter(
    (n) => n.healthGrade.startsWith('A') && !n.hasViolation
  ).length;

  return {
    totalModules,
    totalViolations,
    totalLoC,
    overallGrade,
    healthyCount,
    layerCount: tree.size,
  };
}

// =============================================================================
// Component
// =============================================================================

/**
 * GestaltTree - Main tree container component.
 */
export function GestaltTree({
  modules,
  links,
  selectedModule,
  onModuleSelect,
  compact = false,
  className = '',
}: GestaltTreeProps) {
  const { density } = useShell();

  // Tree mode: layer-first vs full-path
  const [treeMode, setTreeMode] = useState<TreeMode>('layer');

  // Build both trees (memoized)
  const layerTree = useMemo(() => buildLayerTree(modules, links), [modules, links]);
  const pathTree = useMemo(() => buildPathTree(modules, links), [modules, links]);

  // Select active tree based on mode
  const activeTree = treeMode === 'layer' ? layerTree : pathTree;

  // Stats for header
  const stats = useMemo(() => calculateTreeStats(activeTree), [activeTree]);

  // Expansion state
  const [expandedPaths, setExpandedPaths] = useState<Set<string>>(() => {
    // Default expansion based on density
    const defaultDepth = density === 'spacious' ? 2 : density === 'comfortable' ? 1 : 0;
    return getDefaultExpanded(activeTree, defaultDepth);
  });

  // Toggle expansion
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

  // Sort tree nodes: violations first, then by grade
  const sortedNodes = useMemo(() => {
    return Array.from(activeTree.values()).sort((a, b) => {
      // Violations first
      if (a.hasViolation !== b.hasViolation) {
        return a.hasViolation ? -1 : 1;
      }
      // Then by grade (worst first)
      const gradeOrder = ['F', 'D', 'C', 'C+', 'B', 'B+', 'A', 'A+'];
      const aGrade = gradeOrder.indexOf(a.healthGrade);
      const bGrade = gradeOrder.indexOf(b.healthGrade);
      if (aGrade !== bGrade) {
        return aGrade - bGrade;
      }
      // Then by module count (larger first)
      return b.moduleCount - a.moduleCount;
    });
  }, [activeTree]);

  const isHealthy = stats.overallGrade.startsWith('A') && stats.totalViolations === 0;

  return (
    <div className={`flex flex-col h-full ${className}`}>
      {/* Header */}
      <header className="flex-shrink-0 bg-[#2a2a2a] border-b border-gray-700 px-4 py-3">
        <div className="flex items-center justify-between">
          {/* Left: Title + Stats */}
          <div className="flex items-center gap-3">
            <Breathe intensity={isHealthy ? 0.3 : 0} speed="slow">
              <Network className={`w-5 h-5 ${isHealthy ? 'text-[#4A6B4A]' : 'text-amber-400'}`} />
            </Breathe>
            <div>
              <h2 className={`font-semibold text-white ${compact ? 'text-sm' : 'text-base'}`}>
                Architecture Tree
              </h2>
              <p className={`text-gray-500 ${compact ? 'text-[10px]' : 'text-xs'}`}>
                {stats.totalModules} modules &middot; {stats.layerCount} layers
              </p>
            </div>
          </div>

          {/* Right: Mode toggle + Grade */}
          <div className="flex items-center gap-3">
            {/* Tree mode toggle */}
            {!compact && (
              <div className="flex items-center gap-1 bg-gray-800 rounded-md p-0.5">
                <button
                  onClick={() => setTreeMode('layer')}
                  className={`
                    flex items-center gap-1 px-2 py-1 rounded text-xs transition-colors
                    ${
                      treeMode === 'layer'
                        ? 'bg-gray-700 text-white'
                        : 'text-gray-400 hover:text-gray-300'
                    }
                  `}
                  title="Group by architectural layer"
                >
                  <Layers className="w-3 h-3" />
                  Layer
                </button>
                <button
                  onClick={() => setTreeMode('path')}
                  className={`
                    flex items-center gap-1 px-2 py-1 rounded text-xs transition-colors
                    ${
                      treeMode === 'path'
                        ? 'bg-gray-700 text-white'
                        : 'text-gray-400 hover:text-gray-300'
                    }
                  `}
                  title="Show full module path hierarchy"
                >
                  <FolderTree className="w-3 h-3" />
                  Path
                </button>
              </div>
            )}

            {/* Overall grade */}
            {!compact ? (
              <HealthBadgeLarge
                grade={stats.overallGrade}
                score={stats.healthyCount / Math.max(stats.layerCount, 1)}
                hasViolation={stats.totalViolations > 0}
              />
            ) : (
              <div className="text-right">
                <div className="text-lg font-bold text-white">{stats.overallGrade}</div>
                {stats.totalViolations > 0 && (
                  <div className="text-[10px] text-amber-400">
                    {stats.totalViolations} violations
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </header>

      {/* Tree Content */}
      <div className="flex-1 overflow-y-auto px-2 py-2">
        {modules.length === 0 ? (
          <div className="flex items-center justify-center h-full text-gray-500 text-sm">
            No modules found
          </div>
        ) : (
          <div className="space-y-0.5">
            {sortedNodes.map((node) => (
              <GestaltTreeNode
                key={node.path}
                node={node}
                level={0}
                expandedPaths={expandedPaths}
                selectedModule={selectedModule}
                onToggle={handleToggle}
                onSelect={onModuleSelect}
                compact={compact}
              />
            ))}
          </div>
        )}
      </div>

      {/* Footer: Quick stats */}
      {!compact && (
        <footer className="flex-shrink-0 bg-[#2a2a2a] border-t border-gray-700 px-4 py-2">
          <div className="flex items-center justify-between text-xs text-gray-500">
            <span>{stats.totalLoC.toLocaleString()} lines of code</span>
            <span>
              {stats.healthyCount}/{stats.layerCount} layers healthy
            </span>
          </div>
        </footer>
      )}
    </div>
  );
}

export default GestaltTree;
