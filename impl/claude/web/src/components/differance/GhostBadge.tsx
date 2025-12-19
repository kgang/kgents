/**
 * GhostBadge — Ghost Count Badge for Crown Jewel Cards
 *
 * Shows a subtle count of unexplored alternatives ("ghosts") on Crown Jewel status cards.
 * The badge is the entry point to the Différance Engine's heritage exploration.
 *
 * Design: Living Earth palette, compact, tooltip on hover showing "X roads not taken"
 *
 * @see spec/protocols/differance.md
 * @see plans/differance-crown-jewel-wiring.md Phase 6D
 */

import { useState } from 'react';
import { GitBranch } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { GLOW, EARTH, GREEN } from '@/constants/livingEarth';

// =============================================================================
// Types
// =============================================================================

export interface GhostBadgeProps {
  /** Number of ghosts (unexplored alternatives) */
  count: number;
  /** Optional: Whether any ghosts are explorable */
  explorableCount?: number;
  /** Optional click handler */
  onClick?: () => void;
  /** Size variant */
  size?: 'sm' | 'md';
  /** Custom class name */
  className?: string;
}

// =============================================================================
// Component
// =============================================================================

/**
 * Ghost count badge showing roads not taken.
 *
 * Usage:
 * ```tsx
 * <GhostBadge count={3} onClick={() => setShowWhyPanel(true)} />
 * ```
 */
export function GhostBadge({
  count,
  explorableCount,
  onClick,
  size = 'sm',
  className = '',
}: GhostBadgeProps) {
  const [isHovered, setIsHovered] = useState(false);

  // Don't render if no ghosts
  if (count <= 0) return null;

  const isClickable = onClick !== undefined;
  const sizeClasses = size === 'sm' ? 'text-[10px] px-1.5 py-0.5' : 'text-xs px-2 py-1';
  const iconSize = size === 'sm' ? 'w-3 h-3' : 'w-3.5 h-3.5';

  const badgeStyles = {
    backgroundColor: `${GREEN.fern}40`,
    color: GREEN.sprout,
    border: `1px solid ${GREEN.sage}50`,
  };

  const badgeClassName = `
    flex items-center gap-1 rounded-full
    ${sizeClasses}
    transition-colors duration-200
    ${isClickable ? 'cursor-pointer hover:brightness-110' : 'cursor-default'}
  `;

  // Use span when non-interactive to avoid button-in-button DOM nesting issues
  const BadgeElement = isClickable ? motion.button : motion.span;

  return (
    <div className={`relative inline-block ${className}`}>
      <BadgeElement
        type={isClickable ? 'button' : undefined}
        onClick={onClick}
        onMouseEnter={() => setIsHovered(true)}
        onMouseLeave={() => setIsHovered(false)}
        whileHover={isClickable ? { scale: 1.05 } : undefined}
        whileTap={isClickable ? { scale: 0.95 } : undefined}
        className={badgeClassName}
        style={badgeStyles}
        title={`${count} road${count !== 1 ? 's' : ''} not taken`}
      >
        <GitBranch className={iconSize} />
        <span className="font-medium">{count}</span>
      </BadgeElement>

      {/* Tooltip on hover */}
      <AnimatePresence>
        {isHovered && (
          <motion.div
            initial={{ opacity: 0, y: 4 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 4 }}
            transition={{ duration: 0.15 }}
            className="absolute z-50 top-full left-1/2 -translate-x-1/2 mt-1"
          >
            <div
              className="px-2 py-1 rounded text-[10px] whitespace-nowrap"
              style={{
                backgroundColor: EARTH.bark,
                color: GLOW.lantern,
                border: `1px solid ${EARTH.clay}`,
                boxShadow: '0 2px 8px rgba(0,0,0,0.3)',
              }}
            >
              {count} road{count !== 1 ? 's' : ''} not taken
              {explorableCount !== undefined && explorableCount > 0 && (
                <span style={{ color: GREEN.sprout }}> • {explorableCount} explorable</span>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

export default GhostBadge;
