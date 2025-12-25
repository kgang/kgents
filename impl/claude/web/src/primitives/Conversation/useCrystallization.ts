/**
 * useCrystallization - Hook for session crystallization logic
 *
 * Manages trailing session state and crystallization actions.
 * Implements spec §9.4 and §9.4b
 *
 * @see spec/protocols/chat-web.md §9.4, §9.4b
 */

import { useState, useCallback, useEffect, useRef } from 'react';
import type { SessionCrystal, Turn } from './store';

// =============================================================================
// Types
// =============================================================================

export interface CrystallizationTrigger {
  type: 'inactivity' | 'context_overflow' | 'explicit_close' | 'browser_unload' | 'evidence_threshold';
  gracePeriod: number; // seconds
  detected_at: string;
}

export interface UseCrystallizationOptions {
  /** Session ID */
  sessionId: string;

  /** Current session turns */
  turns: Turn[];

  /** Inactivity delay before crystallization (seconds) */
  crystallizationDelay?: number;

  /** Context usage threshold (0-1) for overflow trigger */
  contextThreshold?: number;

  /** Evidence threshold for auto-stop (0-1) */
  evidenceThreshold?: number;

  /** Number of turns with high evidence before suggesting stop */
  evidenceThresholdTurns?: number;

  /** Callback when session crystallizes */
  onCrystallize?: (crystal: SessionCrystal) => void;

  /** Backend API base URL */
  apiUrl?: string;
}

export interface UseCrystallizationResult {
  /** The crystallized session (null if not crystallized) */
  crystallizedSession: SessionCrystal | null;

  /** Trailing turns (not in active context) */
  trailingTurns: Turn[];

  /** Whether session is in trailing state */
  isTrailing: boolean;

  /** Re-hydrate trailing turns into active context */
  continueSession: () => Promise<void>;

  /** Start fresh session with crystal as reference */
  startFresh: () => void;

  /** Open crystal view panel */
  viewCrystal: () => void;

  /** Dismiss trailing section */
  dismiss: () => void;

  /** Manually trigger crystallization */
  triggerCrystallization: (trigger: CrystallizationTrigger['type']) => Promise<void>;

  /** Current trigger (if any) */
  currentTrigger: CrystallizationTrigger | null;

  /** Whether crystal panel is open */
  isCrystalOpen: boolean;
}

// =============================================================================
// Hook
// =============================================================================

/**
 * useCrystallization
 *
 * Manages session crystallization lifecycle.
 * Detects triggers, manages grace periods, and provides continuation affordances.
 *
 * @example
 * ```tsx
 * const {
 *   crystallizedSession,
 *   trailingTurns,
 *   isTrailing,
 *   continueSession,
 *   startFresh,
 *   viewCrystal,
 * } = useCrystallization({
 *   sessionId: 'session-123',
 *   turns: currentTurns,
 *   onCrystallize: handleCrystallize,
 * });
 *
 * {isTrailing && (
 *   <TrailingSession
 *     crystal={crystallizedSession}
 *     trailingTurns={trailingTurns}
 *     onContinue={continueSession}
 *     onStartFresh={startFresh}
 *     onViewCrystal={viewCrystal}
 *   />
 * )}
 * ```
 */
export function useCrystallization(
  options: UseCrystallizationOptions
): UseCrystallizationResult {
  const {
    sessionId,
    turns,
    crystallizationDelay = 300, // 5 minutes default
    onCrystallize,
    apiUrl = '/api/chat',
  } = options;

  const [crystallizedSession, setCrystallizedSession] = useState<SessionCrystal | null>(null);
  const [trailingTurns, setTrailingTurns] = useState<Turn[]>([]);
  const [isTrailing, setIsTrailing] = useState(false);
  const [currentTrigger, setCurrentTrigger] = useState<CrystallizationTrigger | null>(null);
  const [isCrystalOpen, setIsCrystalOpen] = useState(false);

  const inactivityTimerRef = useRef<number | null>(null);
  const lastActivityRef = useRef<Date>(new Date());

  // =============================================================================
  // Crystallization Logic
  // =============================================================================

  const crystallize = useCallback(async (trigger: CrystallizationTrigger['type']) => {
    try {
      // Call backend to crystallize session
      const response = await fetch(`${apiUrl}/${sessionId}/crystallize`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ trigger }),
      });

      if (!response.ok) {
        throw new Error('Failed to crystallize session');
      }

      const crystal: SessionCrystal = await response.json();

      // Transition to trailing state
      setCrystallizedSession(crystal);
      setTrailingTurns(turns);
      setIsTrailing(true);
      setCurrentTrigger(null);

      onCrystallize?.(crystal);
    } catch (error) {
      console.error('Crystallization failed:', error);
    }
  }, [sessionId, turns, apiUrl, onCrystallize]);

  const triggerCrystallization = useCallback(async (triggerType: CrystallizationTrigger['type']) => {
    const trigger: CrystallizationTrigger = {
      type: triggerType,
      gracePeriod: getGracePeriod(triggerType),
      detected_at: new Date().toISOString(),
    };

    setCurrentTrigger(trigger);

    if (trigger.gracePeriod > 0) {
      // Wait grace period, then check if user resumed
      await new Promise<void>(resolve => {
        setTimeout(() => resolve(), trigger.gracePeriod * 1000);
      });

      // Check if activity occurred during grace period
      const timeSinceActivity = Date.now() - lastActivityRef.current.getTime();
      if (timeSinceActivity < trigger.gracePeriod * 1000) {
        // User resumed, don't crystallize
        setCurrentTrigger(null);
        return;
      }
    }

    // Crystallize
    await crystallize(triggerType);
  }, [crystallize]);

  // =============================================================================
  // Inactivity Detection
  // =============================================================================

  useEffect(() => {
    // Reset inactivity timer on any turn change
    lastActivityRef.current = new Date();

    if (inactivityTimerRef.current) {
      clearTimeout(inactivityTimerRef.current);
    }

    // Set new inactivity timer
    inactivityTimerRef.current = window.setTimeout(() => {
      triggerCrystallization('inactivity');
    }, crystallizationDelay * 1000);

    return () => {
      if (inactivityTimerRef.current) {
        clearTimeout(inactivityTimerRef.current);
      }
    };
  }, [turns.length, crystallizationDelay, triggerCrystallization]);

  // =============================================================================
  // Browser Unload Detection
  // =============================================================================

  useEffect(() => {
    const handleBeforeUnload = () => {
      // Best-effort crystallization using sendBeacon
      if (turns.length > 0) {
        navigator.sendBeacon(
          `${apiUrl}/${sessionId}/crystallize`,
          JSON.stringify({ trigger: 'browser_unload' })
        );
      }
    };

    window.addEventListener('beforeunload', handleBeforeUnload);

    return () => {
      window.removeEventListener('beforeunload', handleBeforeUnload);
    };
  }, [sessionId, turns.length, apiUrl]);

  // =============================================================================
  // User Actions
  // =============================================================================

  const continueSession = useCallback(async () => {
    try {
      // Re-hydrate session
      const response = await fetch(`${apiUrl}/${sessionId}/rehydrate`, {
        method: 'POST',
      });

      if (!response.ok) {
        throw new Error('Failed to rehydrate session');
      }

      // Restore turns to active context
      setTrailingTurns(prev => prev.map(t => ({ ...t, in_context: true, trailing: false })));
      setIsTrailing(false);
      setCrystallizedSession(null);

      // Reset activity
      lastActivityRef.current = new Date();
    } catch (error) {
      console.error('Failed to continue session:', error);
    }
  }, [sessionId, apiUrl]);

  const startFresh = useCallback(() => {
    // Create new session with crystal as reference
    // This would typically navigate to a new session page with @mention reference
    if (crystallizedSession) {
      // Implementation depends on routing setup
      console.log('Starting fresh session with crystal reference:', crystallizedSession.session_id);
      // Example: router.push(`/chat/new?reference=${crystallizedSession.session_id}`);
    }
  }, [crystallizedSession]);

  const viewCrystal = useCallback(() => {
    setIsCrystalOpen(true);
  }, []);

  const dismiss = useCallback(() => {
    setIsTrailing(false);
    setTrailingTurns([]);
    setCrystallizedSession(null);
  }, []);

  // =============================================================================
  // Return
  // =============================================================================

  return {
    crystallizedSession,
    trailingTurns,
    isTrailing,
    continueSession,
    startFresh,
    viewCrystal,
    dismiss,
    triggerCrystallization,
    currentTrigger,
    isCrystalOpen,
  };
}

// =============================================================================
// Utilities
// =============================================================================

/**
 * Get grace period for trigger type (from spec §9.4)
 */
function getGracePeriod(trigger: CrystallizationTrigger['type']): number {
  switch (trigger) {
    case 'inactivity':
      return 30; // 30 seconds
    case 'context_overflow':
      return 0; // Immediate
    case 'explicit_close':
      return 0; // Immediate
    case 'browser_unload':
      return 0; // Best-effort, no grace period
    case 'evidence_threshold':
      return 60; // 60 seconds
    default:
      return 0;
  }
}

// =============================================================================
// Default Export
// =============================================================================

export default useCrystallization;
