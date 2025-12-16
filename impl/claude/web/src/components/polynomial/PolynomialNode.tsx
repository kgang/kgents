/**
 * PolynomialNode: A single position (state) in a polynomial state machine.
 *
 * Foundation 3: Visible Polynomial State
 *
 * This component renders an individual node in the state machine diagram,
 * with visual feedback for current state, valid transitions, and history.
 */

import { motion } from 'framer-motion';
import type { PolynomialPosition } from '../../api/types';
import { POLYNOMIAL_CONFIG } from '../../api/types';

export interface PolynomialNodeProps {
  position: PolynomialPosition;
  /** Whether this node can be transitioned to from current state */
  isReachable?: boolean;
  /** Called when user clicks to transition to this state */
  onTransition?: (positionId: string) => void;
  /** Visual variant */
  variant?: 'default' | 'compact' | 'detailed';
  /** Custom size (default: 64px for default, 48px for compact) */
  size?: number;
}

/**
 * Get the color for a position based on its state.
 */
function getNodeColor(position: PolynomialPosition, isReachable?: boolean): string {
  if (position.color) return position.color;
  if (position.is_current) return POLYNOMIAL_CONFIG.colors.current;
  if (position.is_terminal) return POLYNOMIAL_CONFIG.colors.terminal;
  if (isReachable) return POLYNOMIAL_CONFIG.colors.available;
  return POLYNOMIAL_CONFIG.colors.default;
}

/**
 * PolynomialNode component for rendering a single state in the diagram.
 */
export function PolynomialNode({
  position,
  isReachable = false,
  onTransition,
  variant = 'default',
  size,
}: PolynomialNodeProps) {
  const nodeSize = size ?? (variant === 'compact' ? 48 : 64);
  const color = getNodeColor(position, isReachable);
  const canClick = isReachable && !position.is_current && onTransition;

  return (
    <motion.div
      className="relative flex flex-col items-center gap-1"
      initial={{ scale: 0, opacity: 0 }}
      animate={{ scale: 1, opacity: 1 }}
      exit={{ scale: 0, opacity: 0 }}
      transition={{ type: 'spring', stiffness: 300, damping: 20 }}
    >
      {/* Node circle */}
      <motion.button
        type="button"
        disabled={!canClick}
        onClick={() => canClick && onTransition(position.id)}
        className={`
          relative rounded-full flex items-center justify-center
          transition-all duration-200 ease-out
          ${canClick ? 'cursor-pointer hover:scale-110 active:scale-95' : 'cursor-default'}
          ${position.is_current ? 'ring-2 ring-white/30 ring-offset-2 ring-offset-gray-900' : ''}
        `}
        style={{
          width: nodeSize,
          height: nodeSize,
          backgroundColor: color,
          boxShadow: position.is_current
            ? `0 0 20px ${color}60, 0 0 40px ${color}30`
            : `0 2px 8px ${color}30`,
        }}
        whileHover={canClick ? { scale: 1.1 } : undefined}
        whileTap={canClick ? { scale: 0.95 } : undefined}
      >
        {/* Emoji or label initial */}
        <span className="text-lg select-none">
          {position.emoji || position.label.charAt(0).toUpperCase()}
        </span>

        {/* Current state indicator - breathing animation */}
        {position.is_current && (
          <motion.div
            className="absolute inset-0 rounded-full"
            style={{ backgroundColor: color }}
            animate={{
              opacity: [0.3, 0.6, 0.3],
              scale: [1, 1.15, 1],
            }}
            transition={{
              duration: 2,
              repeat: Infinity,
              ease: 'easeInOut',
            }}
          />
        )}

        {/* Reachable indicator - pulse */}
        {isReachable && !position.is_current && (
          <motion.div
            className="absolute inset-0 rounded-full border-2"
            style={{ borderColor: color }}
            animate={{
              opacity: [0.5, 1, 0.5],
            }}
            transition={{
              duration: 1.5,
              repeat: Infinity,
              ease: 'easeInOut',
            }}
          />
        )}
      </motion.button>

      {/* Label */}
      <span
        className={`
          text-center font-medium
          ${variant === 'compact' ? 'text-xs' : 'text-sm'}
          ${position.is_current ? 'text-white' : 'text-gray-400'}
        `}
      >
        {position.label}
      </span>

      {/* Description tooltip on hover - only for detailed variant */}
      {variant === 'detailed' && position.description && (
        <span className="text-xs text-gray-500 text-center max-w-[100px]">
          {position.description}
        </span>
      )}
    </motion.div>
  );
}

export default PolynomialNode;
