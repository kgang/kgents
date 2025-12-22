/**
 * MarkCard: Display a single witness mark.
 *
 * A mark is a leaf falling in the garden of decisions.
 * Each mark breathes gently, showing vitality and presence.
 *
 * Living Earth Palette:
 * - Background: Soil (#2D1B14)
 * - Text: Wood (#6B4E3D)
 * - Accent: Copper (#C08552) for Kent, Sage (#4A6B4A) for Claude
 *
 * @see plans/witness-fusion-ux-design.md
 */

import { useState, type ReactNode } from 'react';
import { motion } from 'framer-motion';
import type { Mark } from '@/api/witness';

// =============================================================================
// Living Earth Palette
// =============================================================================

const LIVING_EARTH = {
  soil: '#2D1B14',
  soilLight: '#3D2B24',
  wood: '#6B4E3D',
  woodLight: '#8B6E5D',
  copper: '#C08552',
  copperLight: '#D09562',
  sage: '#4A6B4A',
  sageLight: '#5A7B5A',
  honey: '#E8C4A0',
  lantern: '#F5E6D3',
} as const;

// =============================================================================
// Types
// =============================================================================

export type MarkDensity = 'compact' | 'comfortable' | 'spacious';

export interface MarkCardProps {
  /** The mark to display */
  mark: Mark;

  /** Display density */
  density?: MarkDensity;

  /** Callback when retract is requested */
  onRetract?: (markId: string) => void;

  /** Whether the card is selected */
  isSelected?: boolean;

  /** Click handler */
  onClick?: () => void;

  /** Additional CSS classes */
  className?: string;
}

// =============================================================================
// Sub-components
// =============================================================================

interface AgentBadgeProps {
  author: 'kent' | 'claude' | 'system';
  size?: 'sm' | 'md' | 'lg';
}

function AgentBadge({ author, size = 'sm' }: AgentBadgeProps) {
  const sizeClasses = {
    sm: 'w-5 h-5 text-xs',
    md: 'w-6 h-6 text-sm',
    lg: 'w-8 h-8 text-base',
  };

  const config = {
    kent: {
      emoji: '\u{1F9D1}', // Person emoji
      bg: LIVING_EARTH.copper,
      label: 'Kent',
    },
    claude: {
      emoji: '\u{1F916}', // Robot emoji
      bg: LIVING_EARTH.sage,
      label: 'Claude',
    },
    system: {
      emoji: '\u2699\uFE0F', // Gear emoji
      bg: LIVING_EARTH.wood,
      label: 'System',
    },
  };

  const { emoji, bg, label } = config[author];

  return (
    <span
      className={`inline-flex items-center justify-center rounded-full ${sizeClasses[size]}`}
      style={{ backgroundColor: bg }}
      title={label}
      aria-label={label}
    >
      {emoji}
    </span>
  );
}

interface PrincipleChipProps {
  principle: string;
}

function PrincipleChip({ principle }: PrincipleChipProps) {
  return (
    <span
      className="inline-block px-2 py-0.5 text-xs rounded-full"
      style={{
        backgroundColor: `${LIVING_EARTH.honey}20`,
        color: LIVING_EARTH.honey,
        border: `1px solid ${LIVING_EARTH.honey}40`,
      }}
    >
      {principle}
    </span>
  );
}

// =============================================================================
// Main Component
// =============================================================================

export function MarkCard({
  mark,
  density = 'comfortable',
  onRetract,
  isSelected = false,
  onClick,
  className = '',
}: MarkCardProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  const [isHovered, setIsHovered] = useState(false);

  // Format timestamp
  const timestamp = new Date(mark.timestamp);
  const timeStr = timestamp.toLocaleTimeString([], {
    hour: '2-digit',
    minute: '2-digit',
  });

  // Is this mark retracted?
  const isRetracted = !!mark.retracted_at;

  // Breathing animation (subtle scale pulse when hovered)
  const breatheVariants = {
    idle: { scale: 1 },
    hover: {
      scale: 1.02,
      transition: {
        duration: 0.3,
        ease: 'easeOut' as const,
      },
    },
  };

  // Handle expand toggle
  const toggleExpand = () => {
    if (density !== 'compact') {
      setIsExpanded(!isExpanded);
    }
  };

  // Handle retract
  const handleRetract = (e: React.MouseEvent) => {
    e.stopPropagation();
    onRetract?.(mark.id);
  };

  // Render based on density
  const renderContent = (): ReactNode => {
    switch (density) {
      case 'compact':
        // Single line: timestamp + action (truncated)
        return (
          <div className="flex items-center gap-2 py-1.5 px-3">
            <span
              className="text-xs flex-shrink-0"
              style={{ color: LIVING_EARTH.woodLight }}
            >
              {timeStr}
            </span>
            <AgentBadge author={mark.author} size="sm" />
            <span
              className="text-sm truncate flex-1"
              style={{ color: LIVING_EARTH.lantern }}
              title={mark.action}
            >
              {mark.action}
            </span>
            {mark.principles.length > 0 && (
              <span
                className="text-xs flex-shrink-0"
                style={{ color: LIVING_EARTH.honey }}
              >
                [{mark.principles.length}]
              </span>
            )}
          </div>
        );

      case 'comfortable':
        // Two lines: header + action, expand for reasoning
        return (
          <div className="py-2 px-3">
            <div className="flex items-center gap-2 mb-1">
              <span
                className="text-xs"
                style={{ color: LIVING_EARTH.woodLight }}
              >
                🍂 {timeStr}
              </span>
              <AgentBadge author={mark.author} size="sm" />
              {mark.principles.slice(0, 2).map((p) => (
                <PrincipleChip key={p} principle={p} />
              ))}
              {mark.principles.length > 2 && (
                <span
                  className="text-xs"
                  style={{ color: LIVING_EARTH.woodLight }}
                >
                  +{mark.principles.length - 2}
                </span>
              )}
            </div>
            <p
              className="text-sm"
              style={{ color: LIVING_EARTH.lantern }}
            >
              {mark.action}
            </p>
            {isExpanded && mark.reasoning && (
              <motion.p
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                className="text-xs mt-2 pl-2 border-l-2"
                style={{
                  color: LIVING_EARTH.woodLight,
                  borderColor: LIVING_EARTH.wood,
                }}
              >
                \u21B3 {mark.reasoning}
              </motion.p>
            )}
          </div>
        );

      case 'spacious':
        // Full display: all fields visible
        return (
          <div className="py-3 px-4">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2">
                <span
                  className="text-xs"
                  style={{ color: LIVING_EARTH.woodLight }}
                >
                  🍂 {timeStr}
                </span>
                <AgentBadge author={mark.author} size="md" />
              </div>
              {onRetract && !isRetracted && (
                <button
                  onClick={handleRetract}
                  className="text-xs px-2 py-1 rounded opacity-50 hover:opacity-100 transition-opacity"
                  style={{
                    backgroundColor: `${LIVING_EARTH.copper}20`,
                    color: LIVING_EARTH.copper,
                  }}
                >
                  Retract
                </button>
              )}
            </div>
            <p
              className="text-base mb-2"
              style={{ color: LIVING_EARTH.lantern }}
            >
              {mark.action}
            </p>
            {mark.reasoning && (
              <p
                className="text-sm mb-2 pl-3 border-l-2"
                style={{
                  color: LIVING_EARTH.woodLight,
                  borderColor: LIVING_EARTH.wood,
                }}
              >
                \u21B3 {mark.reasoning}
              </p>
            )}
            {mark.principles.length > 0 && (
              <div className="flex flex-wrap gap-1 mt-2">
                {mark.principles.map((p) => (
                  <PrincipleChip key={p} principle={p} />
                ))}
              </div>
            )}
            {mark.parent_mark_id && (
              <p
                className="text-xs mt-2"
                style={{ color: LIVING_EARTH.wood }}
              >
                \u2514\u2500 child of {mark.parent_mark_id.slice(0, 12)}...
              </p>
            )}
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <motion.div
      className={`rounded-lg border cursor-pointer select-none ${className}`}
      style={{
        backgroundColor: isRetracted
          ? `${LIVING_EARTH.soil}80`
          : LIVING_EARTH.soilLight,
        borderColor: isSelected
          ? LIVING_EARTH.copper
          : isHovered
          ? LIVING_EARTH.wood
          : `${LIVING_EARTH.wood}40`,
        opacity: isRetracted ? 0.6 : 1,
        textDecoration: isRetracted ? 'line-through' : 'none',
      }}
      variants={breatheVariants}
      initial="idle"
      animate={isHovered ? 'hover' : 'idle'}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      onClick={onClick || toggleExpand}
      role="article"
      aria-label={`Mark: ${mark.action}`}
      data-testid="mark-card"
      data-density={density}
      data-author={mark.author}
    >
      {renderContent()}
    </motion.div>
  );
}

// =============================================================================
// Exports
// =============================================================================

export { AgentBadge, PrincipleChip };
export default MarkCard;
