/**
 * GhostPanel - Display alternative aspects (ghosts) for Différance visibility
 *
 * After invoking an aspect, show the paths not taken. Clicking a ghost invokes it.
 * Discovery through serendipity.
 *
 * Design:
 * - Purple/violet theming to distinguish from normal content
 * - Ghost emoji with aspect name and hint
 * - Framer motion animations
 * - Accessible button semantics
 *
 * @see plans/habitat-2.0.md - Priority 1: Ghost Integration
 * @see spec/protocols/differance.md
 */

import { motion, AnimatePresence } from 'framer-motion';
import { Ghost as GhostIcon, Sparkles } from 'lucide-react';
import { useMotionPreferences } from '@/components/joy/useMotionPreferences';

// =============================================================================
// Types
// =============================================================================

export interface Ghost {
  aspect: string;
  hint: string;
  category: string;
}

export interface GhostPanelProps {
  /** List of alternative aspects (ghosts) */
  alternatives: Ghost[];
  /** Callback when a ghost is clicked */
  onGhostClick: (aspect: string) => void;
  /** Optional CSS class */
  className?: string;
}

// =============================================================================
// Animation Variants
// =============================================================================

const containerVariants = {
  hidden: { opacity: 0, y: 10 },
  visible: {
    opacity: 1,
    y: 0,
    transition: {
      staggerChildren: 0.08,
      delayChildren: 0.1,
    },
  },
};

const ghostVariants = {
  hidden: { opacity: 0, scale: 0.9, x: -10 },
  visible: {
    opacity: 1,
    scale: 1,
    x: 0,
    transition: {
      type: 'spring' as const,
      stiffness: 200,
      damping: 20,
    },
  },
  hover: {
    scale: 1.03,
    x: 4,
    transition: {
      type: 'spring' as const,
      stiffness: 400,
      damping: 10,
    },
  },
  tap: { scale: 0.97 },
};

// =============================================================================
// Category Colors
// =============================================================================

const CATEGORY_COLORS: Record<string, { bg: string; border: string; text: string }> = {
  PERCEPTION: {
    bg: 'bg-emerald-900/20',
    border: 'border-emerald-600/40',
    text: 'text-emerald-300',
  },
  MUTATION: {
    bg: 'bg-amber-900/20',
    border: 'border-amber-600/40',
    text: 'text-amber-300',
  },
  COMPOSITION: {
    bg: 'bg-cyan-900/20',
    border: 'border-cyan-600/40',
    text: 'text-cyan-300',
  },
  INTROSPECTION: {
    bg: 'bg-purple-900/20',
    border: 'border-purple-600/40',
    text: 'text-purple-300',
  },
  GENERATION: {
    bg: 'bg-pink-900/20',
    border: 'border-pink-600/40',
    text: 'text-pink-300',
  },
  ENTROPY: {
    bg: 'bg-violet-900/20',
    border: 'border-violet-600/40',
    text: 'text-violet-300',
  },
  UNKNOWN: {
    bg: 'bg-gray-900/20',
    border: 'border-gray-600/40',
    text: 'text-gray-300',
  },
};

// =============================================================================
// Component
// =============================================================================

/**
 * GhostPanel displays alternative aspects that could have been invoked.
 *
 * These are the "ghosts" of Différance—the paths not taken. Clicking a ghost
 * invokes that aspect, enabling serendipitous discovery.
 *
 * @example
 * ```tsx
 * <GhostPanel
 *   alternatives={[
 *     { aspect: 'witness', hint: 'View historical traces', category: 'PERCEPTION' },
 *     { aspect: 'refine', hint: 'Dialectical challenge', category: 'GENERATION' },
 *   ]}
 *   onGhostClick={(aspect) => invokeAspect(aspect)}
 * />
 * ```
 */
export function GhostPanel({ alternatives, onGhostClick, className = '' }: GhostPanelProps) {
  const { shouldAnimate } = useMotionPreferences();

  // Don't render if no alternatives
  if (!alternatives || alternatives.length === 0) {
    return null;
  }

  const getColorScheme = (category: string) => {
    return CATEGORY_COLORS[category] || CATEGORY_COLORS.UNKNOWN;
  };

  return (
    <motion.div
      className={`mt-4 p-4 bg-violet-950/30 border border-violet-700/30 rounded-lg ${className}`}
      variants={containerVariants}
      initial={shouldAnimate ? 'hidden' : 'visible'}
      animate="visible"
    >
      {/* Header */}
      <div className="flex items-center gap-2 mb-3">
        <GhostIcon className="w-4 h-4 text-violet-400" />
        <h3 className="text-sm font-medium text-violet-300">Paths Not Taken</h3>
        <Sparkles className="w-3 h-3 text-violet-500/60" />
      </div>

      {/* Ghost List */}
      <div className="space-y-2">
        <AnimatePresence mode="popLayout">
          {alternatives.map((ghost) => {
            const colors = getColorScheme(ghost.category);
            return (
              <motion.button
                key={ghost.aspect}
                variants={ghostVariants}
                initial={shouldAnimate ? 'hidden' : 'visible'}
                animate="visible"
                exit="hidden"
                whileHover={shouldAnimate ? 'hover' : undefined}
                whileTap={shouldAnimate ? 'tap' : undefined}
                onClick={() => onGhostClick(ghost.aspect)}
                className={`
                  w-full p-3 rounded-md
                  ${colors.bg} border ${colors.border}
                  flex items-start gap-3
                  transition-colors
                  hover:bg-violet-900/30 focus:outline-none focus:ring-2 focus:ring-violet-500/50
                `}
                aria-label={`Invoke ${ghost.aspect} aspect`}
              >
                {/* Ghost Icon */}
                <div className="flex-shrink-0 pt-0.5">
                  <span className="text-lg" role="img" aria-label="ghost">
                    👻
                  </span>
                </div>

                {/* Content */}
                <div className="flex-1 text-left">
                  <div className="flex items-baseline gap-2">
                    <span className={`font-mono text-sm font-medium ${colors.text}`}>
                      {ghost.aspect}
                    </span>
                    <span className="text-xs text-violet-500/70 uppercase tracking-wide">
                      {ghost.category}
                    </span>
                  </div>
                  <p className="text-xs text-violet-300/80 mt-1">{ghost.hint}</p>
                </div>
              </motion.button>
            );
          })}
        </AnimatePresence>
      </div>

      {/* Footer hint */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.4 }}
        className="mt-3 pt-3 border-t border-violet-700/20"
      >
        <p className="text-xs text-violet-400/60 text-center">
          Click a ghost to explore that path
        </p>
      </motion.div>
    </motion.div>
  );
}

export default GhostPanel;
