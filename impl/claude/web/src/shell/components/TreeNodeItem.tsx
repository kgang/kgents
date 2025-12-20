/**
 * TreeNodeItem - Individual tree node with split click zones
 *
 * Renders a single node in the navigation tree with:
 * - Expand/collapse button (chevron)
 * - Navigable label area
 * - Context icon for top-level nodes
 * - Child count indicator
 * - Keyboard focus support
 *
 * @see NavigationTree.tsx
 */

import { memo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronRight, type LucideIcon } from 'lucide-react';

// =============================================================================
// Types
// =============================================================================

export interface TreeNode {
  /** Node path segment */
  segment: string;
  /** Full AGENTESE path */
  path: string;
  /** Child nodes */
  children: Map<string, TreeNode>;
  /** Is this a registered path (not just an intermediate segment) */
  isRegistered: boolean;
  /** Description from discovery */
  description?: string;
  /** Available aspects (affordances) */
  aspects?: string[];
}

export interface ContextInfo {
  icon: LucideIcon;
  label: string;
  color: string;
  description: string;
}

export interface TreeNodeItemProps {
  node: TreeNode;
  level: number;
  expandedPaths: Set<string>;
  currentPath: string;
  ancestorPaths: Set<string>;
  focusedPath: string | null;
  onToggle: (path: string) => void;
  onNavigate: (path: string) => void;
  onFocus: (path: string) => void;
  contextInfo?: Record<string, ContextInfo>;
}

// =============================================================================
// Component
// =============================================================================

export const TreeNodeItem = memo(function TreeNodeItem({
  node,
  level,
  expandedPaths,
  currentPath,
  ancestorPaths,
  focusedPath,
  onToggle,
  onNavigate,
  onFocus,
  contextInfo,
}: TreeNodeItemProps) {
  const hasChildren = node.children.size > 0;
  const isExpanded = expandedPaths.has(node.path);
  const isExactMatch = currentPath === node.path;
  const isAncestor = ancestorPaths.has(node.path);
  const isFocused = focusedPath === node.path;
  const canNavigate = node.isRegistered; // Only registered paths are navigable

  // Context info for top-level nodes
  const context = level === 0 && contextInfo ? contextInfo[node.segment] : null;
  const Icon = context?.icon || null;

  // Handle expand/collapse (chevron click)
  const handleToggle = (e: React.MouseEvent) => {
    e.stopPropagation();
    onToggle(node.path);
  };

  // Handle navigation (label click)
  const handleNavigate = () => {
    if (canNavigate) {
      onNavigate(node.path);
    } else if (hasChildren) {
      // If not navigable, toggle instead
      onToggle(node.path);
    }
  };

  // Handle focus on mouse enter (for keyboard nav coordination)
  const handleMouseEnter = () => {
    onFocus(node.path);
  };

  return (
    <div>
      <div
        className={`
          flex items-center text-sm rounded-md transition-colors
          ${isExactMatch ? 'bg-cyan-900/40 text-white font-medium ring-1 ring-cyan-500/30' : ''}
          ${isAncestor && !isExactMatch ? 'text-cyan-300 bg-gray-700/30' : ''}
          ${!isExactMatch && !isAncestor ? 'text-gray-300' : ''}
          ${isFocused && !isExactMatch ? 'ring-1 ring-gray-500/50' : ''}
        `}
        style={{ paddingLeft: `${8 + level * 14}px` }}
        onMouseEnter={handleMouseEnter}
        data-path={node.path}
      >
        {/* Expand/collapse button (separate click zone) */}
        {hasChildren ? (
          <button
            onClick={handleToggle}
            className="p-1.5 hover:bg-gray-600/50 rounded transition-colors flex-shrink-0"
            aria-label={isExpanded ? 'Collapse' : 'Expand'}
            tabIndex={-1}
          >
            <motion.span
              animate={{ rotate: isExpanded ? 90 : 0 }}
              transition={{ duration: 0.15 }}
              className="block"
            >
              <ChevronRight className="w-3 h-3 text-gray-500" />
            </motion.span>
          </button>
        ) : (
          <span className="w-6" /> // Spacer to align with expandable nodes
        )}

        {/* Navigable label area */}
        <button
          onClick={handleNavigate}
          className={`
            flex-1 flex items-center gap-2 py-1.5 pr-2 text-left
            ${canNavigate ? 'hover:text-white cursor-pointer' : 'cursor-default opacity-60'}
            transition-colors truncate
          `}
          tabIndex={-1}
        >
          {/* Icon for contexts */}
          {Icon && <Icon className={`w-4 h-4 flex-shrink-0 ${context?.color}`} />}

          {/* Destination indicator - small dot for navigable paths */}
          {canNavigate && !Icon && (
            <span className="w-1.5 h-1.5 rounded-full flex-shrink-0 bg-cyan-400/70" />
          )}

          {/* Label */}
          <span className="truncate">{node.segment}</span>

          {/* Child count for nodes with children */}
          {hasChildren && (
            <span className="ml-auto text-xs text-gray-500 flex-shrink-0">
              {node.children.size}
            </span>
          )}
        </button>
      </div>

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
                ancestorPaths={ancestorPaths}
                focusedPath={focusedPath}
                onToggle={onToggle}
                onNavigate={onNavigate}
                onFocus={onFocus}
                contextInfo={contextInfo}
              />
            ))}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
});

export default TreeNodeItem;
