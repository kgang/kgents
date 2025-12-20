/**
 * WitnessOverlay - Floating panel showing live Witness thought stream.
 *
 * Phase 2: Witness Integration for Self.Garden.
 *
 * Features:
 * - Floating panel showing latest thoughts
 * - Uses Breathe animation for "alive" indicator
 * - Collapsible (doesn't obstruct garden view)
 * - Shows witness state (DORMANT/WITNESSING/CRYSTALLIZING)
 *
 * @see plans/melodic-toasting-octopus.md - Phase 2
 */

import { useState, useCallback, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Breathe } from '@/components/joy/Breathe';
import { UnfurlPanel } from '@/components/joy/UnfurlPanel';
import { LIVING_EARTH } from '@/constants';
import type { Density } from '@/components/elastic/types';
import type { WitnessThought, WitnessStreamStatus } from '@/hooks/useWitnessStream';

// =============================================================================
// Types
// =============================================================================

export type WitnessState = 'DORMANT' | 'WITNESSING' | 'CRYSTALLIZING';

export interface WitnessOverlayProps {
  /** All thoughts from the stream */
  thoughts: WitnessThought[];
  /** Whether the stream is actively receiving */
  isWitnessing: boolean;
  /** Connection status */
  status: WitnessStreamStatus;
  /** UI density mode */
  density: Density;
  /** Callback when user wants to mark a moment */
  onMarkMoment?: () => void;
  /** Callback when user wants to crystallize thoughts */
  onCrystallize?: () => void;
  /** Additional CSS class */
  className?: string;
}

// =============================================================================
// Constants
// =============================================================================

const STATE_COLORS: Record<WitnessState, string> = {
  DORMANT: LIVING_EARTH.clay,
  WITNESSING: LIVING_EARTH.sage,
  CRYSTALLIZING: LIVING_EARTH.amber,
};

const STATE_LABELS: Record<WitnessState, string> = {
  DORMANT: 'Dormant',
  WITNESSING: 'Witnessing',
  CRYSTALLIZING: 'Crystallizing',
};

const DENSITY_CONFIG = {
  compact: { maxThoughts: 3, showTags: false, showTimestamp: false },
  comfortable: { maxThoughts: 5, showTags: true, showTimestamp: false },
  spacious: { maxThoughts: 8, showTags: true, showTimestamp: true },
};

// =============================================================================
// Component
// =============================================================================

export function WitnessOverlay({
  thoughts,
  isWitnessing,
  status,
  density,
  onMarkMoment,
  onCrystallize,
  className = '',
}: WitnessOverlayProps) {
  const [isExpanded, setIsExpanded] = useState(true);

  // Derive witness state
  const witnessState: WitnessState = useMemo(() => {
    if (status === 'error' || status === 'disconnected') return 'DORMANT';
    if (isWitnessing && thoughts.length > 0) return 'WITNESSING';
    return 'DORMANT';
  }, [status, isWitnessing, thoughts.length]);

  // Get config for current density
  const config = DENSITY_CONFIG[density];

  // Get visible thoughts (most recent first, limited by density)
  const visibleThoughts = useMemo(() => {
    const reversed = [...thoughts].reverse();
    return reversed.slice(0, config.maxThoughts);
  }, [thoughts, config.maxThoughts]);

  // Toggle expand/collapse
  const toggleExpanded = useCallback(() => {
    setIsExpanded((prev) => !prev);
  }, []);

  // Format timestamp
  const formatTimestamp = (timestamp: string | null): string => {
    if (!timestamp) return '';
    try {
      const date = new Date(timestamp);
      return date.toLocaleTimeString(undefined, {
        hour: '2-digit',
        minute: '2-digit',
      });
    } catch {
      return '';
    }
  };

  // Source icons
  const getSourceIcon = (source: string): string => {
    switch (source) {
      case 'gardener':
        return '🌱';
      case 'git':
        return '📝';
      case 'tests':
        return '🧪';
      case 'system':
        return '⚙️';
      default:
        return '💭';
    }
  };

  return (
    <div
      className={`
        fixed right-4 bottom-4 z-40
        max-w-sm w-full
        ${className}
      `}
      style={{
        maxWidth: density === 'compact' ? '280px' : density === 'comfortable' ? '320px' : '360px',
      }}
    >
      {/* Header - Always visible */}
      <button
        onClick={toggleExpanded}
        className="
          w-full flex items-center justify-between
          px-4 py-3 rounded-t-lg
          transition-colors duration-200
          hover:bg-white/5
        "
        style={{
          background: LIVING_EARTH.bark,
          borderBottom: isExpanded ? `1px solid ${LIVING_EARTH.wood}` : 'none',
          borderRadius: isExpanded ? '0.5rem 0.5rem 0 0' : '0.5rem',
        }}
      >
        <div className="flex items-center gap-3">
          {/* Witness Eye with Breathe */}
          <Breathe
            intensity={witnessState === 'WITNESSING' ? 0.5 : 0}
            speed="slow"
            disabled={witnessState !== 'WITNESSING'}
          >
            <div
              className="w-6 h-6 rounded-full flex items-center justify-center"
              style={{
                background: STATE_COLORS[witnessState],
                boxShadow:
                  witnessState === 'WITNESSING' ? `0 0 8px ${STATE_COLORS[witnessState]}` : 'none',
              }}
            >
              <span className="text-sm" role="img" aria-label="witness">
                👁️
              </span>
            </div>
          </Breathe>

          {/* Status Label */}
          <span className="text-sm font-medium" style={{ color: LIVING_EARTH.lantern }}>
            {STATE_LABELS[witnessState]}
          </span>

          {/* Thought Count */}
          {thoughts.length > 0 && (
            <span
              className="text-xs px-2 py-0.5 rounded-full"
              style={{
                background: LIVING_EARTH.wood,
                color: LIVING_EARTH.sand,
              }}
            >
              {thoughts.length}
            </span>
          )}
        </div>

        {/* Expand/Collapse Icon */}
        <motion.svg
          className="w-4 h-4"
          style={{ color: LIVING_EARTH.clay }}
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          animate={{ rotate: isExpanded ? 180 : 0 }}
          transition={{ duration: 0.2 }}
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </motion.svg>
      </button>

      {/* Thought List - Collapsible */}
      <UnfurlPanel isOpen={isExpanded} direction="down" duration={250}>
        <div className="rounded-b-lg overflow-hidden" style={{ background: LIVING_EARTH.bark }}>
          {/* Thoughts */}
          <div className="max-h-64 overflow-y-auto">
            <AnimatePresence mode="popLayout">
              {visibleThoughts.length === 0 ? (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="px-4 py-6 text-center"
                  style={{ color: LIVING_EARTH.clay }}
                >
                  <span className="text-2xl mb-2 block">🔮</span>
                  <span className="text-sm">Awaiting thoughts...</span>
                </motion.div>
              ) : (
                visibleThoughts.map((thought, index) => (
                  <motion.div
                    key={`${thought.timestamp}-${index}`}
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, height: 0 }}
                    transition={{ duration: 0.2 }}
                    className="px-4 py-3 border-b last:border-b-0"
                    style={{ borderColor: LIVING_EARTH.wood }}
                  >
                    {/* Source & Timestamp */}
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-sm" role="img" aria-label={thought.source}>
                        {getSourceIcon(thought.source)}
                      </span>
                      <span className="text-xs font-medium" style={{ color: LIVING_EARTH.clay }}>
                        {thought.source}
                      </span>
                      {config.showTimestamp && thought.timestamp && (
                        <span className="text-xs ml-auto" style={{ color: LIVING_EARTH.clay }}>
                          {formatTimestamp(thought.timestamp)}
                        </span>
                      )}
                    </div>

                    {/* Content */}
                    <p className="text-sm line-clamp-2" style={{ color: LIVING_EARTH.sand }}>
                      {thought.content}
                    </p>

                    {/* Tags */}
                    {config.showTags && thought.tags.length > 0 && (
                      <div className="flex flex-wrap gap-1 mt-2">
                        {thought.tags.slice(0, 3).map((tag) => (
                          <span
                            key={tag}
                            className="text-xs px-2 py-0.5 rounded"
                            style={{
                              background: LIVING_EARTH.wood,
                              color: LIVING_EARTH.clay,
                            }}
                          >
                            {tag}
                          </span>
                        ))}
                      </div>
                    )}
                  </motion.div>
                ))
              )}
            </AnimatePresence>
          </div>

          {/* Actions */}
          {(onMarkMoment || onCrystallize) && (
            <div
              className="flex gap-2 px-4 py-3 border-t"
              style={{ borderColor: LIVING_EARTH.wood }}
            >
              {onMarkMoment && (
                <button
                  onClick={onMarkMoment}
                  className="
                    flex-1 px-3 py-2 rounded text-sm font-medium
                    transition-colors duration-200
                    hover:opacity-80
                  "
                  style={{
                    background: LIVING_EARTH.wood,
                    color: LIVING_EARTH.lantern,
                  }}
                >
                  📌 Mark Moment
                </button>
              )}
              {onCrystallize && (
                <button
                  onClick={onCrystallize}
                  className="
                    flex-1 px-3 py-2 rounded text-sm font-medium
                    transition-colors duration-200
                    hover:opacity-80
                  "
                  style={{
                    background: LIVING_EARTH.amber,
                    color: LIVING_EARTH.bark,
                  }}
                >
                  💎 Crystallize
                </button>
              )}
            </div>
          )}

          {/* Connection Status (if error) */}
          {status === 'error' && (
            <div
              className="px-4 py-2 text-xs text-center"
              style={{
                background: LIVING_EARTH.copper,
                color: LIVING_EARTH.lantern,
              }}
            >
              Connection lost. Reconnecting...
            </div>
          )}
        </div>
      </UnfurlPanel>
    </div>
  );
}

export default WitnessOverlay;
