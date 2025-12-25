/**
 * CrystallizationTrigger - Automatic trigger detection component
 *
 * Monitors session state for crystallization triggers:
 * - Inactivity (no input for N minutes)
 * - Context overflow (context > 95%)
 * - Evidence threshold (should_stop for 3+ turns)
 *
 * Implements spec §9.4
 *
 * @see spec/protocols/chat-web.md §9.4
 */

import { useEffect, useRef, useCallback } from 'react';
import type { CrystallizationTrigger as TriggerType } from './useCrystallization';

// =============================================================================
// Types
// =============================================================================

export interface CrystallizationTriggerProps {
  /** Current context usage (0-1) */
  contextUsage: number;

  /** Evidence "should_stop" values for recent turns */
  recentShouldStop: boolean[];

  /** Last activity timestamp */
  lastActivity: Date;

  /** Inactivity delay in seconds */
  inactivityDelay?: number;

  /** Context overflow threshold (0-1) */
  contextThreshold?: number;

  /** Evidence threshold turns required */
  evidenceThresholdTurns?: number;

  /** Callback when trigger detected */
  onTrigger: (trigger: TriggerType['type']) => void;

  /** Whether trigger detection is enabled */
  enabled?: boolean;
}

// =============================================================================
// Component
// =============================================================================

/**
 * CrystallizationTrigger
 *
 * Invisible component that monitors for crystallization triggers.
 * Invokes callback when trigger conditions are met.
 *
 * @example
 * ```tsx
 * <CrystallizationTrigger
 *   contextUsage={0.82}
 *   recentShouldStop={[false, true, true, true]}
 *   lastActivity={lastActivityTimestamp}
 *   onTrigger={handleCrystallizationTrigger}
 * />
 * ```
 */
export function CrystallizationTrigger({
  contextUsage,
  recentShouldStop,
  lastActivity,
  inactivityDelay = 300, // 5 minutes
  contextThreshold = 0.95,
  evidenceThresholdTurns = 3,
  onTrigger,
  enabled = true,
}: CrystallizationTriggerProps) {
  const inactivityTimerRef = useRef<number | null>(null);
  const hasTriggeredRef = useRef<Set<TriggerType['type']>>(new Set());

  // =============================================================================
  // Trigger Handlers
  // =============================================================================

  const trigger = useCallback(
    (type: TriggerType['type']) => {
      if (!enabled) return;
      if (hasTriggeredRef.current.has(type)) return;

      hasTriggeredRef.current.add(type);
      onTrigger(type);
    },
    [enabled, onTrigger]
  );

  // =============================================================================
  // Inactivity Detection
  // =============================================================================

  useEffect(() => {
    if (!enabled) return;

    // Clear existing timer
    if (inactivityTimerRef.current) {
      clearTimeout(inactivityTimerRef.current);
    }

    // Calculate time until inactivity trigger
    const timeSinceActivity = Date.now() - lastActivity.getTime();
    const timeRemaining = Math.max(0, inactivityDelay * 1000 - timeSinceActivity);

    // Set timer
    inactivityTimerRef.current = window.setTimeout(() => {
      trigger('inactivity');
    }, timeRemaining);

    return () => {
      if (inactivityTimerRef.current) {
        clearTimeout(inactivityTimerRef.current);
      }
    };
  }, [lastActivity, inactivityDelay, trigger, enabled]);

  // =============================================================================
  // Context Overflow Detection
  // =============================================================================

  useEffect(() => {
    if (!enabled) return;

    if (contextUsage >= contextThreshold) {
      trigger('context_overflow');
    }
  }, [contextUsage, contextThreshold, trigger, enabled]);

  // =============================================================================
  // Evidence Threshold Detection
  // =============================================================================

  useEffect(() => {
    if (!enabled) return;

    // Check if last N turns all have should_stop = true
    const recentTurns = recentShouldStop.slice(-evidenceThresholdTurns);

    if (
      recentTurns.length >= evidenceThresholdTurns &&
      recentTurns.every(shouldStop => shouldStop === true)
    ) {
      trigger('evidence_threshold');
    }
  }, [recentShouldStop, evidenceThresholdTurns, trigger, enabled]);

  // Reset triggered set when re-enabled
  useEffect(() => {
    if (enabled) {
      hasTriggeredRef.current.clear();
    }
  }, [enabled]);

  // No visual output
  return null;
}

// =============================================================================
// Default Export
// =============================================================================

export default CrystallizationTrigger;
