/**
 * AnimatedCursor: Spring-physics cursor with behavior personality.
 *
 * CLI v7 Phase 5: Collaborative Canvas.
 *
 * Voice Anchor:
 * "Agents pretending to be there with their cursors moving,
 *  kinda following my cursor, kinda doing its own thing."
 *
 * The magic: Each CursorBehavior has distinct spring feel:
 * - FOLLOWER: High stiffness (300), high damping (25) -> snappy, responsive
 * - EXPLORER: Low stiffness (150), low damping (15) -> loose, wandering
 * - ASSISTANT: Medium (200/20) -> balanced, attentive
 * - AUTONOMOUS: Very low (100/10) -> slow, deliberate
 *
 * Circadian modulation: Night tempo (0.3) slows animations.
 * Morning tempo (1.0) keeps them energetic.
 *
 * Pattern Applied:
 * - Joy-Inducing (P4): Movement has personality
 * - Heterarchical (P6): Different behaviors, same dignity
 * - Composable (P5): CursorBehavior x CircadianPhase -> SpringConfig
 *
 * @see services/conductor/behaviors.py - CursorBehavior enum
 * @see services/conductor/presence.py - CircadianPhase
 */

import { useMemo } from 'react';
import { motion, useSpring } from 'framer-motion';
import type { AgentCursor, CursorBehavior, CursorState } from '@/hooks/usePresenceChannel';

// =============================================================================
// Spring Configuration by Behavior
// =============================================================================

/**
 * Spring physics tuned per behavior personality.
 *
 * These values are opinionated—they encode character:
 * - FOLLOWER: Loyal dog, tracks with empathetic timing
 * - EXPLORER: Butterfly, drifts with curiosity
 * - ASSISTANT: Helpful partner, present but not clingy
 * - AUTONOMOUS: Sage, moves with purpose
 */
const BEHAVIOR_SPRINGS: Record<CursorBehavior, { stiffness: number; damping: number }> = {
  follower: { stiffness: 300, damping: 25 },
  explorer: { stiffness: 150, damping: 15 },
  assistant: { stiffness: 200, damping: 20 },
  autonomous: { stiffness: 100, damping: 10 },
};

/**
 * State-based opacity and scale modulation.
 *
 * WORKING pulses larger, WAITING fades slightly.
 */
const STATE_STYLE: Record<CursorState, { opacity: number; scale: number }> = {
  following: { opacity: 0.95, scale: 1.0 },
  exploring: { opacity: 0.9, scale: 1.05 },
  working: { opacity: 1.0, scale: 1.15 },
  suggesting: { opacity: 1.0, scale: 1.1 },
  waiting: { opacity: 0.6, scale: 0.95 },
};

// =============================================================================
// State Colors & Emojis
// =============================================================================

const STATE_COLORS: Record<CursorState, string> = {
  following: '#22d3ee', // cyan-400
  exploring: '#3b82f6', // blue-500
  working: '#eab308', // yellow-500
  suggesting: '#22c55e', // green-500
  waiting: '#9ca3af', // gray-400
};

const STATE_EMOJIS: Record<CursorState, string> = {
  following: '',
  exploring: '',
  working: '',
  suggesting: '',
  waiting: '',
};

const BEHAVIOR_EMOJIS: Record<CursorBehavior, string> = {
  follower: '',
  explorer: '',
  assistant: '',
  autonomous: '',
};

// =============================================================================
// Component Props
// =============================================================================

export interface AnimatedCursorProps {
  /** The agent cursor data */
  cursor: AgentCursor;
  /** Target position (where cursor should animate to) */
  targetPosition: { x: number; y: number };
  /** Circadian tempo modifier (0.0-1.0), higher = faster animations */
  circadianTempo?: number;
  /** Whether to show the name label */
  showLabel?: boolean;
  /** Whether to show the activity text */
  showActivity?: boolean;
}

// =============================================================================
// Main Component
// =============================================================================

export function AnimatedCursor({
  cursor,
  targetPosition,
  circadianTempo = 1.0,
  showLabel = true,
  showActivity = true,
}: AnimatedCursorProps) {
  // Get spring config for this behavior
  const springConfig = useMemo(() => {
    const base = BEHAVIOR_SPRINGS[cursor.behavior] || BEHAVIOR_SPRINGS.assistant;

    // Apply circadian modulation: slower at night
    // Tempo 0.3 (night) -> stiffness * 0.65, Tempo 1.0 (morning) -> stiffness * 1.0
    const tempoFactor = 0.5 + circadianTempo * 0.5;

    return {
      stiffness: base.stiffness * tempoFactor,
      damping: base.damping,
      mass: 1,
    };
  }, [cursor.behavior, circadianTempo]);

  // Animated position with spring physics
  const x = useSpring(targetPosition.x, springConfig);
  const y = useSpring(targetPosition.y, springConfig);

  // State-based visual modulation
  const stateStyle = STATE_STYLE[cursor.state] || STATE_STYLE.waiting;
  const color = STATE_COLORS[cursor.state] || STATE_COLORS.waiting;
  const stateEmoji = STATE_EMOJIS[cursor.state] || '';
  const behaviorEmoji = BEHAVIOR_EMOJIS[cursor.behavior] || '';

  // Compute glow intensity based on state
  const glowIntensity = useMemo(() => {
    if (cursor.state === 'suggesting') return 0.4;
    if (cursor.state === 'working') return 0.35;
    return 0.25;
  }, [cursor.state]);

  // Compute glow size based on state
  const glowSize = useMemo(() => {
    if (cursor.state === 'suggesting') return 40;
    if (cursor.state === 'working') return 36;
    return 32;
  }, [cursor.state]);

  return (
    <motion.div
      className="absolute pointer-events-none select-none z-30"
      style={{
        x,
        y,
        translateX: '-50%',
        translateY: '-50%',
      }}
    >
      {/* Cursor body */}
      <motion.div
        className="relative flex items-center justify-center"
        initial={{ scale: 0, opacity: 0 }}
        animate={{
          scale: stateStyle.scale,
          opacity: stateStyle.opacity,
        }}
        transition={{
          type: 'spring',
          stiffness: 400,
          damping: 30,
        }}
        style={{ color }}
      >
        {/* Outer glow - intensity varies by state */}
        <motion.div
          className="absolute rounded-full blur-sm"
          style={{
            backgroundColor: color,
            width: glowSize,
            height: glowSize,
            opacity: glowIntensity,
          }}
          animate={
            cursor.state === 'working'
              ? {
                  scale: [1, 1.2, 1],
                  opacity: [glowIntensity, glowIntensity * 1.3, glowIntensity],
                }
              : cursor.state === 'suggesting'
                ? {
                    scale: [1, 1.1, 1],
                    opacity: [glowIntensity, glowIntensity * 1.2, glowIntensity],
                  }
                : undefined
          }
          transition={
            cursor.state === 'working'
              ? { duration: 0.8, repeat: Infinity, ease: 'easeInOut' }
              : cursor.state === 'suggesting'
                ? { duration: 2.5, repeat: Infinity, ease: 'easeInOut' }
                : undefined
          }
        />

        {/* Inner ring */}
        <motion.div
          className="relative w-6 h-6 rounded-full border-2 flex items-center justify-center text-[10px] font-bold"
          style={{
            borderColor: color,
            backgroundColor: `${color}20`,
            boxShadow:
              cursor.state === 'suggesting'
                ? `0 0 12px ${color}60`
                : cursor.state === 'working'
                  ? `0 0 8px ${color}40`
                  : 'none',
          }}
          animate={
            cursor.state === 'waiting'
              ? {
                  scale: [0.95, 1.05, 0.95],
                  opacity: [0.6, 1, 0.6],
                }
              : undefined
          }
          transition={
            cursor.state === 'waiting'
              ? { duration: 4, repeat: Infinity, ease: 'easeInOut' }
              : undefined
          }
        >
          {stateEmoji}
        </motion.div>

        {/* Focus line (when working/exploring/suggesting) */}
        {cursor.focus_path && cursor.state !== 'waiting' && cursor.state !== 'following' && (
          <motion.div
            className="absolute w-0.5 h-4 -bottom-4"
            style={{
              backgroundColor: color,
              opacity: cursor.state === 'working' ? 0.8 : 0.5,
            }}
            initial={{ scaleY: 0 }}
            animate={{ scaleY: 1 }}
            transition={{ duration: 0.2 }}
          />
        )}
      </motion.div>

      {/* Labels */}
      {(showLabel || showActivity) && (
        <motion.div
          className="absolute top-full left-1/2 mt-2 whitespace-nowrap"
          style={{
            x: '-50%',
            color,
            opacity: cursor.state === 'waiting' ? 0.7 : 1,
          }}
          initial={{ opacity: 0, y: -5 }}
          animate={{ opacity: cursor.state === 'waiting' ? 0.7 : 1, y: 0 }}
          transition={{ delay: 0.1 }}
        >
          {showLabel && (
            <div className="text-[10px] font-medium text-center flex items-center justify-center gap-1">
              {behaviorEmoji && <span className="opacity-70">{behaviorEmoji}</span>}
              <span>{cursor.display_name}</span>
            </div>
          )}
          {showActivity && cursor.activity && (
            <div className="text-[9px] opacity-70 text-center max-w-[100px] truncate">
              {cursor.activity}
            </div>
          )}
        </motion.div>
      )}
    </motion.div>
  );
}

// =============================================================================
// Exports
// =============================================================================

export default AnimatedCursor;
