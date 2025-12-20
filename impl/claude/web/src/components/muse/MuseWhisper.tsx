/**
 * MuseWhisper - Floating whisper card from The Muse.
 *
 * Phase 3: Muse Integration for Self.Garden.
 *
 * Features:
 * - Ephemeral floating card that appears with contextual suggestions
 * - Uses UnfurlPanel for entrance animation
 * - Auto-fades after 30s if not interacted with
 * - Dismiss/Accept buttons
 * - Category-colored border (encouragement=green, reframe=blue, etc.)
 *
 * Philosophy:
 *   "I see the arc of your work. I know when you're rising, when you're
 *    stuck, when you're about to break through. I whisper—never shout."
 *
 * @see plans/melodic-toasting-octopus.md - Phase 3
 */

import { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Breathe } from '@/components/joy/Breathe';
import { LIVING_EARTH } from '@/constants';
import type { MuseWhisper as MuseWhisperType } from '@/hooks/useMuseStream';

// =============================================================================
// Types
// =============================================================================

export interface MuseWhisperProps {
  /** The whisper to display */
  whisper: MuseWhisperType;
  /** Current story arc phase */
  arcPhase?: string;
  /** Callback when user dismisses */
  onDismiss: () => void;
  /** Callback when user accepts/acknowledges */
  onAccept: () => void;
  /** Auto-dismiss timeout in ms (default: 30000) */
  autoHideTimeout?: number;
  /** Additional CSS class */
  className?: string;
}

// =============================================================================
// Constants
// =============================================================================

const CATEGORY_COLORS: Record<string, string> = {
  ENCOURAGEMENT: '#4ade80', // Green
  REFRAME: '#60a5fa', // Blue
  OBSERVATION: LIVING_EARTH.amber, // Amber
  RITUAL: '#c084fc', // Purple
  TECHNICAL: LIVING_EARTH.lantern, // Lantern yellow
  NARRATIVE: LIVING_EARTH.sage, // Sage
  SUGGESTION: LIVING_EARTH.clay, // Clay (default)
};

const CATEGORY_ICONS: Record<string, string> = {
  ENCOURAGEMENT: '🌟',
  REFRAME: '🔮',
  OBSERVATION: '👁️',
  RITUAL: '🌿',
  TECHNICAL: '⚙️',
  NARRATIVE: '📖',
  SUGGESTION: '💭',
};

const ARC_PHASE_LABELS: Record<string, string> = {
  EXPOSITION: 'Understanding',
  RISING_ACTION: 'Building',
  CLIMAX: 'Breakthrough',
  FALLING_ACTION: 'Refining',
  DENOUEMENT: 'Reflecting',
};

// =============================================================================
// Component
// =============================================================================

export function MuseWhisper({
  whisper,
  arcPhase: _arcPhase, // Kept for future use
  onDismiss,
  onAccept,
  autoHideTimeout = 30000,
  className = '',
}: MuseWhisperProps) {
  // arcPhase from props can be used for additional context in future
  void _arcPhase;
  const [isVisible, setIsVisible] = useState(true);
  const [isHovered, setIsHovered] = useState(false);

  // Get category color and icon
  const categoryColor = CATEGORY_COLORS[whisper.category] || CATEGORY_COLORS.SUGGESTION;
  const categoryIcon = CATEGORY_ICONS[whisper.category] || CATEGORY_ICONS.SUGGESTION;
  const arcLabel = ARC_PHASE_LABELS[whisper.arc_phase] || whisper.arc_phase;

  // Auto-hide timer
  useEffect(() => {
    if (isHovered) return; // Don't auto-hide while hovered

    const timer = setTimeout(() => {
      setIsVisible(false);
      // Give animation time to complete before dismiss
      setTimeout(onDismiss, 300);
    }, autoHideTimeout);

    return () => clearTimeout(timer);
  }, [autoHideTimeout, isHovered, onDismiss]);

  // Handle dismiss
  const handleDismiss = useCallback(() => {
    setIsVisible(false);
    setTimeout(onDismiss, 300);
  }, [onDismiss]);

  // Handle accept
  const handleAccept = useCallback(() => {
    setIsVisible(false);
    setTimeout(onAccept, 300);
  }, [onAccept]);

  return (
    <AnimatePresence>
      {isVisible && (
        <motion.div
          initial={{ opacity: 0, y: 20, scale: 0.95 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          exit={{ opacity: 0, y: -10, scale: 0.95 }}
          transition={{ duration: 0.3, ease: 'easeOut' }}
          className={`
            fixed bottom-20 left-4 z-50
            max-w-sm w-full
            ${className}
          `}
          onMouseEnter={() => setIsHovered(true)}
          onMouseLeave={() => setIsHovered(false)}
        >
          <div
            className="rounded-lg overflow-hidden shadow-lg"
            style={{
              background: LIVING_EARTH.bark,
              borderLeft: `4px solid ${categoryColor}`,
            }}
          >
            {/* Header */}
            <div
              className="px-4 py-3 flex items-center justify-between"
              style={{ borderBottom: `1px solid ${LIVING_EARTH.wood}` }}
            >
              <div className="flex items-center gap-2">
                {/* Muse Icon with Breathe */}
                <Breathe intensity={0.3} speed="slow">
                  <span className="text-lg" role="img" aria-label="muse">
                    {categoryIcon}
                  </span>
                </Breathe>

                {/* Category Label */}
                <span
                  className="text-xs font-medium uppercase tracking-wide"
                  style={{ color: categoryColor }}
                >
                  {whisper.category.toLowerCase()}
                </span>

                {/* Arc Phase Badge */}
                <span
                  className="text-xs px-2 py-0.5 rounded-full"
                  style={{
                    background: LIVING_EARTH.wood,
                    color: LIVING_EARTH.clay,
                  }}
                >
                  {arcLabel}
                </span>
              </div>

              {/* Confidence Indicator */}
              <div
                className="text-xs"
                style={{ color: LIVING_EARTH.clay }}
                title={`Confidence: ${Math.round(whisper.confidence * 100)}%`}
              >
                {whisper.confidence > 0.7 ? '●●●' : whisper.confidence > 0.4 ? '●●○' : '●○○'}
              </div>
            </div>

            {/* Content */}
            <div className="px-4 py-4">
              <p className="text-sm leading-relaxed" style={{ color: LIVING_EARTH.sand }}>
                {whisper.content}
              </p>
            </div>

            {/* Actions */}
            <div
              className="flex gap-2 px-4 py-3"
              style={{ borderTop: `1px solid ${LIVING_EARTH.wood}` }}
            >
              <button
                onClick={handleDismiss}
                className="
                  flex-1 px-3 py-2 rounded text-sm font-medium
                  transition-all duration-200
                  hover:bg-white/5
                "
                style={{
                  background: 'transparent',
                  color: LIVING_EARTH.clay,
                  border: `1px solid ${LIVING_EARTH.wood}`,
                }}
              >
                Dismiss
              </button>
              <button
                onClick={handleAccept}
                className="
                  flex-1 px-3 py-2 rounded text-sm font-medium
                  transition-all duration-200
                  hover:opacity-90
                "
                style={{
                  background: categoryColor,
                  color: LIVING_EARTH.bark,
                }}
              >
                Got it
              </button>
            </div>

            {/* Progress bar for auto-hide */}
            {!isHovered && (
              <motion.div
                initial={{ width: '100%' }}
                animate={{ width: '0%' }}
                transition={{ duration: autoHideTimeout / 1000, ease: 'linear' }}
                className="h-0.5"
                style={{ background: categoryColor, opacity: 0.5 }}
              />
            )}
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}

export default MuseWhisper;
