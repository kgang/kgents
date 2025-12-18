/**
 * GestaltTreeNode - Recursive tree node with health metrics.
 *
 * Follows NavigationTree's patterns:
 * - Memoized for performance
 * - AnimatePresence for expand/collapse
 * - Depth-based indentation
 * - Animated chevron rotation
 *
 * Living Earth aesthetic:
 * - Healthy nodes breathe (via HealthBadge)
 * - Violations show amber warning
 * - Growing animation on expand
 *
 * @see impl/claude/web/src/shell/NavigationTree.tsx - Pattern source
 */

import { memo, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronRight, AlertTriangle } from 'lucide-react';
import { useMotionPreferences } from '@/components/joy/useMotionPreferences';
import { HealthBadge } from './HealthBadge';
import type { GestaltTreeNodeProps } from './types';

// =============================================================================
// Constants
// =============================================================================

/** Base left padding in pixels */
const BASE_INDENT = 12;

/** Indentation per level in pixels */
const INDENT_PER_LEVEL = 16;

/** Animation duration in seconds */
const ANIMATION_DURATION = 0.15;

// =============================================================================
// Component
// =============================================================================

/**
 * GestaltTreeNode - Recursive tree node component.
 *
 * Memoized to prevent cascade re-renders through recursive tree.
 */
export const GestaltTreeNode = memo(function GestaltTreeNode({
  node,
  level,
  expandedPaths,
  selectedModule,
  onToggle,
  onSelect,
  compact = false,
}: GestaltTreeNodeProps) {
  const { shouldAnimate } = useMotionPreferences();

  const hasChildren = node.children.size > 0;
  const isExpanded = expandedPaths.has(node.path);
  const isSelected = node.module?.id === selectedModule;
  const isHealthy = (node.healthGrade === 'A+' || node.healthGrade === 'A') && !node.hasViolation;

  // Handle click: toggle expansion and/or select module
  const handleClick = useCallback(() => {
    if (hasChildren) {
      onToggle(node.path);
    }
    if (node.isLeaf && node.module) {
      onSelect(node.module.id);
    }
  }, [hasChildren, node.path, node.isLeaf, node.module, onToggle, onSelect]);

  // Sort children: violations first, then by grade (worst first), then alphabetically
  const sortedChildren = Array.from(node.children.values()).sort((a, b) => {
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
    // Then alphabetically
    return a.segment.localeCompare(b.segment);
  });

  return (
    <div>
      {/* Row: clickable button with all info */}
      <button
        onClick={handleClick}
        className={`
          w-full flex items-center gap-2 py-1.5
          text-left transition-colors rounded-md
          hover:bg-gray-700/50
          ${isSelected ? 'bg-[#4A6B4A]/30 ring-1 ring-[#4A6B4A]/50' : ''}
          ${compact ? 'text-xs' : 'text-sm'}
        `}
        style={{ paddingLeft: `${BASE_INDENT + level * INDENT_PER_LEVEL}px` }}
        title={
          node.isLeaf
            ? `${node.segment} (${node.healthGrade}) - ${node.linesOfCode} LoC`
            : undefined
        }
      >
        {/* Chevron (animated rotation) */}
        {hasChildren ? (
          <motion.span
            animate={{ rotate: isExpanded ? 90 : 0 }}
            transition={{ duration: shouldAnimate ? ANIMATION_DURATION : 0 }}
            className="flex-shrink-0"
          >
            <ChevronRight className={`text-gray-500 ${compact ? 'w-3 h-3' : 'w-4 h-4'}`} />
          </motion.span>
        ) : (
          <span className={compact ? 'w-3' : 'w-4'} /> // Spacer for alignment
        )}

        {/* Health Badge (breathing when healthy) */}
        <HealthBadge
          grade={node.healthGrade}
          score={node.healthScore}
          hasViolation={node.hasViolation}
          breathing={isHealthy && !compact}
          compact={compact}
        />

        {/* Label */}
        <span
          className={`
            truncate flex-1
            ${isSelected ? 'text-white font-medium' : 'text-gray-300'}
          `}
        >
          {node.segment}
        </span>

        {/* Module count (non-leaf only) */}
        {!node.isLeaf && node.moduleCount > 0 && (
          <span className={`text-gray-500 ${compact ? 'text-[10px]' : 'text-xs'}`}>
            {node.moduleCount}
          </span>
        )}

        {/* Lines of code (leaf only, non-compact) */}
        {node.isLeaf && !compact && (
          <span className="text-[10px] text-gray-500">{node.linesOfCode.toLocaleString()} LoC</span>
        )}

        {/* Violation indicator */}
        {node.hasViolation && (
          <span className="flex items-center gap-0.5 text-amber-400">
            <AlertTriangle className={compact ? 'w-3 h-3' : 'w-3.5 h-3.5'} />
            {node.violationCount > 1 && !compact && (
              <span className="text-[10px]">{node.violationCount}</span>
            )}
          </span>
        )}
      </button>

      {/* Children (animated expand/collapse) */}
      <AnimatePresence>
        {hasChildren && isExpanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: shouldAnimate ? ANIMATION_DURATION : 0 }}
            className="overflow-hidden"
          >
            {sortedChildren.map((child) => (
              <GestaltTreeNode
                key={child.path}
                node={child}
                level={level + 1}
                expandedPaths={expandedPaths}
                selectedModule={selectedModule}
                onToggle={onToggle}
                onSelect={onSelect}
                compact={compact}
              />
            ))}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
});

export default GestaltTreeNode;
