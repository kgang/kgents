/**
 * ExplorationBreadcrumb - Track the exploration trail through AGENTESE
 *
 * Shows the last 5 path.aspect combinations visited.
 * Clickable to navigate back. Fades older items for visual hierarchy.
 *
 * Design:
 * - Compact horizontal layout
 * - Fade gradient for older items
 * - Violet theming to match ghost integration
 * - Accessible navigation semantics
 *
 * @see plans/habitat-2.0.md - Priority 1: Ghost Integration
 */

import { motion, AnimatePresence } from 'framer-motion';
import { ChevronRight, Home } from 'lucide-react';
import { useMotionPreferences } from '@/components/joy/useMotionPreferences';

// =============================================================================
// Types
// =============================================================================

export interface BreadcrumbItem {
  path: string;
  aspect: string;
  timestamp: number;
}

export interface ExplorationBreadcrumbProps {
  /** Trail of visited path.aspect combinations (max 5) */
  trail: BreadcrumbItem[];
  /** Callback when clicking a breadcrumb */
  onNavigate: (item: BreadcrumbItem) => void;
  /** Optional home click handler */
  onHome?: () => void;
  /** Optional CSS class */
  className?: string;
}

// =============================================================================
// Animation Variants
// =============================================================================

const itemVariants = {
  hidden: { opacity: 0, x: -10, scale: 0.9 },
  visible: {
    opacity: 1,
    x: 0,
    scale: 1,
    transition: {
      type: 'spring' as const,
      stiffness: 300,
      damping: 25,
    },
  },
  exit: {
    opacity: 0,
    x: 10,
    scale: 0.9,
    transition: { duration: 0.2 },
  },
};

// =============================================================================
// Component
// =============================================================================

/**
 * ExplorationBreadcrumb shows the trail of AGENTESE invocations.
 *
 * Allows users to see where they've been and navigate back to previous states.
 * Older items fade out to create a visual hierarchy.
 *
 * @example
 * ```tsx
 * <ExplorationBreadcrumb
 *   trail={[
 *     { path: 'world.garden', aspect: 'manifest', timestamp: Date.now() - 3000 },
 *     { path: 'world.garden', aspect: 'witness', timestamp: Date.now() },
 *   ]}
 *   onNavigate={(item) => invoke(item.path, item.aspect)}
 *   onHome={() => navigate('/')}
 * />
 * ```
 */
export function ExplorationBreadcrumb({
  trail,
  onNavigate,
  onHome,
  className = '',
}: ExplorationBreadcrumbProps) {
  const { shouldAnimate } = useMotionPreferences();

  // Don't render if no trail
  if (!trail || trail.length === 0) {
    return null;
  }

  // Calculate opacity for each item (older = more faded)
  const getOpacity = (index: number): number => {
    const position = trail.length - 1 - index; // 0 = most recent
    return Math.max(0.3, 1 - position * 0.15);
  };

  return (
    <div className={`flex items-center gap-1 px-2 py-1 ${className}`}>
      {/* Home button */}
      {onHome && (
        <>
          <motion.button
            onClick={onHome}
            whileHover={shouldAnimate ? { scale: 1.1 } : undefined}
            whileTap={shouldAnimate ? { scale: 0.95 } : undefined}
            className="p-1 rounded hover:bg-violet-900/30 transition-colors"
            aria-label="Go home"
          >
            <Home className="w-3 h-3 text-violet-400/70" />
          </motion.button>
          <ChevronRight className="w-3 h-3 text-violet-500/40" />
        </>
      )}

      {/* Breadcrumb trail */}
      <div className="flex items-center gap-1 overflow-x-auto scrollbar-thin scrollbar-thumb-violet-700/30">
        <AnimatePresence mode="popLayout">
          {trail.map((item, index) => (
            <motion.div
              key={`${item.path}-${item.aspect}-${item.timestamp}`}
              variants={itemVariants}
              initial={shouldAnimate ? 'hidden' : 'visible'}
              animate="visible"
              exit={shouldAnimate ? 'exit' : undefined}
              style={{ opacity: getOpacity(index) }}
              className="flex items-center gap-1 flex-shrink-0"
            >
              {index > 0 && <ChevronRight className="w-3 h-3 text-violet-500/40" />}
              <motion.button
                onClick={() => onNavigate(item)}
                whileHover={shouldAnimate ? { scale: 1.05 } : undefined}
                whileTap={shouldAnimate ? { scale: 0.95 } : undefined}
                className={`
                  px-2 py-1 rounded text-xs font-mono
                  transition-colors
                  ${
                    index === trail.length - 1
                      ? 'bg-violet-900/40 text-violet-200'
                      : 'text-violet-400/90 hover:bg-violet-900/20'
                  }
                `}
                aria-label={`Navigate to ${item.path}:${item.aspect}`}
              >
                <span className="opacity-60">{item.path}</span>
                <span className="mx-1 opacity-40">:</span>
                <span>{item.aspect}</span>
              </motion.button>
            </motion.div>
          ))}
        </AnimatePresence>
      </div>
    </div>
  );
}

export default ExplorationBreadcrumb;
