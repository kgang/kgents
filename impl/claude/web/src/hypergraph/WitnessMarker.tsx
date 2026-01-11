/**
 * WitnessMarker — Displays witness type indicators with colored glow
 *
 * "The proof IS the decision. The mark IS the witness."
 *
 * Each witness type has a distinct icon and color:
 * - COMPOSITION: Links/chains (cyan)
 * - GALOIS: Mathematical/precise (purple)
 * - PRINCIPLE: Core values (blue diamond)
 * - EMPIRICAL: Evidence/testing (amber)
 * - AESTHETIC: Beauty/design (pink)
 * - SOMATIC: Felt sense/intuition (magenta)
 *
 * Modes:
 * - Full: Icon + confidence + optional click
 * - Compact: Small badge with count
 * - Inline: Tiny marker for path nodes
 */

import { memo, useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import './WitnessMarker.css';

// =============================================================================
// Types
// =============================================================================

export type WitnessType =
  | 'COMPOSITION'
  | 'GALOIS'
  | 'PRINCIPLE'
  | 'EMPIRICAL'
  | 'AESTHETIC'
  | 'SOMATIC';

export interface WitnessMarkerProps {
  /** Witness type determines icon and color */
  type: WitnessType;
  /** Confidence score (0-1) */
  confidence: number;
  /** Number of witnesses of this type (for compact mode) */
  count?: number;
  /** Compact mode shows smaller badge with count */
  compact?: boolean;
  /** Click handler for expanding details */
  onClick?: () => void;
  /** Additional class name */
  className?: string;
  /** Show tooltip on hover */
  showTooltip?: boolean;
  /** Custom tooltip content */
  tooltipContent?: string;
}

// =============================================================================
// Constants
// =============================================================================

export const WITNESS_CONFIG: Record<
  WitnessType,
  { icon: string; color: string; bgColor: string; label: string }
> = {
  COMPOSITION: {
    icon: '🔗',
    color: '#06b6d4', // cyan-500
    bgColor: 'rgba(6, 182, 212, 0.15)',
    label: 'Composition',
  },
  GALOIS: {
    icon: '📐',
    color: '#a855f7', // purple-500
    bgColor: 'rgba(168, 85, 247, 0.15)',
    label: 'Galois Connection',
  },
  PRINCIPLE: {
    icon: '💎',
    color: '#3b82f6', // blue-500
    bgColor: 'rgba(59, 130, 246, 0.15)',
    label: 'Principle',
  },
  EMPIRICAL: {
    icon: '🧪',
    color: '#f59e0b', // amber-500
    bgColor: 'rgba(245, 158, 11, 0.15)',
    label: 'Empirical',
  },
  AESTHETIC: {
    icon: '🎨',
    color: '#ec4899', // pink-500
    bgColor: 'rgba(236, 72, 153, 0.15)',
    label: 'Aesthetic',
  },
  SOMATIC: {
    icon: '💜',
    color: '#a855f7', // purple-500 (magenta-ish)
    bgColor: 'rgba(168, 85, 247, 0.15)',
    label: 'Somatic',
  },
};

// Animation variants
const markerVariants = {
  initial: { scale: 0.8, opacity: 0 },
  animate: { scale: 1, opacity: 1 },
  hover: { scale: 1.1 },
  tap: { scale: 0.95 },
};

const tooltipVariants = {
  hidden: { opacity: 0, y: 5, scale: 0.95 },
  visible: { opacity: 1, y: 0, scale: 1 },
};

// =============================================================================
// Helper Functions
// =============================================================================

/**
 * Get confidence level class for styling
 */
function getConfidenceClass(confidence: number): string {
  if (confidence >= 0.8) return 'witness-marker--high';
  if (confidence >= 0.6) return 'witness-marker--medium';
  return 'witness-marker--low';
}

/**
 * Format confidence as percentage
 */
function formatConfidence(confidence: number): string {
  return `${Math.round(confidence * 100)}%`;
}

// =============================================================================
// Tooltip Subcomponent
// =============================================================================

interface WitnessTooltipProps {
  type: WitnessType;
  confidence: number;
  content?: string;
}

const WitnessTooltip = memo(function WitnessTooltip({
  type,
  confidence,
  content,
}: WitnessTooltipProps) {
  const config = WITNESS_CONFIG[type];

  return (
    <motion.div
      className="witness-marker__tooltip"
      variants={tooltipVariants}
      initial="hidden"
      animate="visible"
      exit="hidden"
    >
      <div className="witness-marker__tooltip-header">
        <span className="witness-marker__tooltip-icon">{config.icon}</span>
        <span className="witness-marker__tooltip-type" style={{ color: config.color }}>
          {config.label}
        </span>
      </div>
      <div className="witness-marker__tooltip-confidence">
        <span>Confidence:</span>
        <span
          className={`witness-marker__tooltip-value ${getConfidenceClass(confidence)}`}
          style={{ color: config.color }}
        >
          {formatConfidence(confidence)}
        </span>
      </div>
      {content && <div className="witness-marker__tooltip-content">{content}</div>}
    </motion.div>
  );
});

// =============================================================================
// Main Component
// =============================================================================

export const WitnessMarker = memo(function WitnessMarker({
  type,
  confidence,
  count,
  compact = false,
  onClick,
  className = '',
  showTooltip = true,
  tooltipContent,
}: WitnessMarkerProps) {
  const [isHovered, setIsHovered] = useState(false);
  const config = WITNESS_CONFIG[type];
  const confidenceClass = getConfidenceClass(confidence);

  const handleMouseEnter = useCallback(() => {
    setIsHovered(true);
  }, []);

  const handleMouseLeave = useCallback(() => {
    setIsHovered(false);
  }, []);

  const handleClick = useCallback(() => {
    if (onClick) {
      onClick();
    }
  }, [onClick]);

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      if (onClick && (e.key === 'Enter' || e.key === ' ')) {
        e.preventDefault();
        onClick();
      }
    },
    [onClick]
  );

  // Build class names
  const classNames = [
    'witness-marker',
    compact ? 'witness-marker--compact' : '',
    confidenceClass,
    onClick ? 'witness-marker--clickable' : '',
    className,
  ]
    .filter(Boolean)
    .join(' ');

  return (
    <motion.div
      className={classNames}
      style={
        {
          '--witness-color': config.color,
          '--witness-bg': config.bgColor,
        } as React.CSSProperties
      }
      variants={markerVariants}
      initial="initial"
      animate="animate"
      whileHover={onClick ? 'hover' : undefined}
      whileTap={onClick ? 'tap' : undefined}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
      onClick={handleClick}
      onKeyDown={handleKeyDown}
      role={onClick ? 'button' : undefined}
      tabIndex={onClick ? 0 : undefined}
      aria-label={`${config.label} witness, ${formatConfidence(confidence)} confidence${count ? `, ${count} instances` : ''}`}
    >
      <span className="witness-marker__icon" aria-hidden="true">
        {config.icon}
      </span>

      {!compact && (
        <span className="witness-marker__confidence">{formatConfidence(confidence)}</span>
      )}

      {compact && count !== undefined && count > 1 && (
        <span className="witness-marker__count">{count}</span>
      )}

      {/* Glow effect */}
      <span className="witness-marker__glow" aria-hidden="true" />

      {/* Tooltip */}
      <AnimatePresence>
        {showTooltip && isHovered && (
          <WitnessTooltip type={type} confidence={confidence} content={tooltipContent} />
        )}
      </AnimatePresence>
    </motion.div>
  );
});

// =============================================================================
// Inline Witness Badge (for path nodes)
// =============================================================================

export interface WitnessBadgeProps {
  /** Array of witness types present */
  witnesses: Array<{ type: WitnessType; confidence: number }>;
  /** Maximum badges to show before collapsing to count */
  maxVisible?: number;
  /** Click handler */
  onClick?: () => void;
  /** Additional class name */
  className?: string;
}

export const WitnessBadge = memo(function WitnessBadge({
  witnesses,
  maxVisible = 3,
  onClick,
  className = '',
}: WitnessBadgeProps) {
  const [showTooltip, setShowTooltip] = useState(false);

  // Hooks must be called unconditionally before any returns
  const handleMouseEnter = useCallback(() => setShowTooltip(true), []);
  const handleMouseLeave = useCallback(() => setShowTooltip(false), []);

  if (witnesses.length === 0) return null;

  const visibleWitnesses = witnesses.slice(0, maxVisible);
  const hiddenCount = witnesses.length - maxVisible;
  const avgConfidence = witnesses.reduce((sum, w) => sum + w.confidence, 0) / witnesses.length;

  return (
    <motion.div
      className={`witness-badge ${onClick ? 'witness-badge--clickable' : ''} ${className}`}
      onClick={onClick}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
      role={onClick ? 'button' : undefined}
      tabIndex={onClick ? 0 : undefined}
      aria-label={`${witnesses.length} witnesses, average confidence ${Math.round(avgConfidence * 100)}%`}
      initial={{ opacity: 0, scale: 0.8 }}
      animate={{ opacity: 1, scale: 1 }}
      whileHover={onClick ? { scale: 1.05 } : undefined}
    >
      <span className="witness-badge__icons">
        {visibleWitnesses.map((w, i) => (
          <span
            key={`${w.type}-${i}`}
            className="witness-badge__icon"
            style={{ '--witness-color': WITNESS_CONFIG[w.type].color } as React.CSSProperties}
          >
            {WITNESS_CONFIG[w.type].icon}
          </span>
        ))}
      </span>

      {hiddenCount > 0 && <span className="witness-badge__more">+{hiddenCount}</span>}

      <span className="witness-badge__count">{witnesses.length}w</span>

      {/* Tooltip listing all witnesses */}
      <AnimatePresence>
        {showTooltip && (
          <motion.div
            className="witness-badge__tooltip"
            variants={tooltipVariants}
            initial="hidden"
            animate="visible"
            exit="hidden"
          >
            <div className="witness-badge__tooltip-header">
              {witnesses.length} Witness{witnesses.length !== 1 ? 'es' : ''}
            </div>
            <ul className="witness-badge__tooltip-list">
              {witnesses.map((w, i) => (
                <li key={`${w.type}-${i}`} className="witness-badge__tooltip-item">
                  <span style={{ color: WITNESS_CONFIG[w.type].color }}>
                    {WITNESS_CONFIG[w.type].icon}
                  </span>
                  <span className="witness-badge__tooltip-type">
                    {WITNESS_CONFIG[w.type].label}
                  </span>
                  <span className="witness-badge__tooltip-confidence">
                    {Math.round(w.confidence * 100)}%
                  </span>
                </li>
              ))}
            </ul>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
});

// =============================================================================
// Exports
// =============================================================================

export default WitnessMarker;
