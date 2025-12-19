/**
 * MiniPolynomial - Compact visualization of polynomial functor structure
 *
 * Priority 3: Mini Polynomial from Habitat 2.0
 *
 * This component makes AD-002 (Polynomial Generalization) visible and interactive.
 * Every agent has a polynomial functor P[S, A, B] where:
 * - S is the set of positions (states)
 * - E(s) is the directions available from each position
 *
 * This visualizes S and E, allowing users to click transitions to invoke aspects.
 *
 * Layout: Simple vertical stack (Option A from plan)
 * - Position badges stacked vertically
 * - Current position highlighted in emerald
 * - Directions shown as clickable buttons below each position
 *
 * @see spec/principles.md - AD-002: Polynomial Generalization
 * @see plans/habitat-2.0.md - Priority 3: Mini Polynomial
 */

import { memo } from 'react';
import { motion } from 'framer-motion';
import { Circle, ArrowRight } from 'lucide-react';

// =============================================================================
// Types
// =============================================================================

export interface MiniPolynomialProps {
  /** Set of positions (states) in the polynomial */
  positions: string[];
  /** Current active position */
  current: string;
  /** Directions available from each position (aspect names) */
  directions: Record<string, string[]>;
  /** Called when user clicks a direction (aspect) */
  onTransitionClick?: (position: string, direction: string) => void;
  /** Additional CSS classes */
  className?: string;
}

// =============================================================================
// Component
// =============================================================================

/**
 * MiniPolynomial renders a compact polynomial functor visualization.
 *
 * Shows positions (states) vertically with their available directions (aspects).
 * The current position is highlighted. Clicking a direction invokes that aspect.
 *
 * @example
 * ```tsx
 * <MiniPolynomial
 *   positions={['default']}
 *   current="default"
 *   directions={{ default: ['manifest', 'witness', 'affordances'] }}
 *   onTransitionClick={(pos, dir) => invokeAspect(dir)}
 * />
 * ```
 */
export const MiniPolynomial = memo(function MiniPolynomial({
  positions,
  current,
  directions,
  onTransitionClick,
  className = '',
}: MiniPolynomialProps) {
  return (
    <div className={`space-y-3 ${className}`}>
      {positions.map((position, index) => {
        const isCurrent = position === current;
        const posDirections = directions[position] || [];

        return (
          <motion.div
            key={position}
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: index * 0.05 }}
            className="space-y-2"
          >
            {/* Position Badge */}
            <div className="flex items-center gap-2">
              <Circle
                className={`w-3 h-3 ${
                  isCurrent ? 'fill-emerald-400 text-emerald-400' : 'fill-gray-500 text-gray-500'
                }`}
              />
              <span
                className={`text-sm font-mono font-medium ${
                  isCurrent ? 'text-emerald-400' : 'text-gray-400'
                }`}
              >
                {position}
              </span>
              {isCurrent && (
                <span className="text-xs text-emerald-500/70">(current)</span>
              )}
            </div>

            {/* Directions (Aspects) */}
            {posDirections.length > 0 && (
              <div className="ml-5 pl-3 border-l border-gray-700/50 space-y-1">
                {posDirections.map((direction) => (
                  <button
                    key={direction}
                    type="button"
                    onClick={() => onTransitionClick?.(position, direction)}
                    className={`
                      flex items-center gap-2 px-2 py-1 rounded text-xs font-mono
                      transition-colors duration-150
                      ${
                        isCurrent
                          ? 'text-gray-300 hover:text-emerald-300 hover:bg-emerald-900/20'
                          : 'text-gray-500 hover:text-gray-300 hover:bg-gray-700/30'
                      }
                    `}
                  >
                    <ArrowRight className="w-3 h-3" />
                    {direction}
                  </button>
                ))}
              </div>
            )}
          </motion.div>
        );
      })}
    </div>
  );
});

export default MiniPolynomial;
