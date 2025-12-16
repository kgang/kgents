/**
 * useHistoricalMode: State management for historical replay.
 *
 * Manages switching between live and historical modes, timeline
 * navigation, and snapshot caching for efficient replay.
 *
 * @see plans/web-refactor/interaction-patterns.md
 */

import { useState, useCallback, useRef, useEffect } from 'react';
import type { ColonyDashboardJSON } from '@/reactive/types';

// =============================================================================
// Types
// =============================================================================

export type HistoryMode = 'live' | 'historical';

export interface HistoricalState {
  /** Current mode */
  mode: HistoryMode;

  /** Current tick position */
  currentTick: number;

  /** Maximum tick (latest known) */
  maxTick: number;

  /** Whether timeline is playing */
  isPlaying: boolean;

  /** Playback speed (1 = normal, 2 = 2x, 0.5 = half speed) */
  playbackSpeed: number;

  /** Whether we're loading a snapshot */
  isLoading: boolean;

  /** Error message if loading failed */
  error: string | null;
}

export interface HistoricalActions {
  /** Enter historical mode at a specific tick */
  enterHistorical: (tick?: number) => void;

  /** Return to live mode */
  returnToLive: () => void;

  /** Seek to a specific tick */
  seekTo: (tick: number) => void;

  /** Step forward one tick */
  stepForward: () => void;

  /** Step backward one tick */
  stepBackward: () => void;

  /** Toggle play/pause */
  togglePlay: () => void;

  /** Set playback speed */
  setPlaybackSpeed: (speed: number) => void;

  /** Update max tick (called when new events arrive) */
  updateMaxTick: (tick: number) => void;

  /** Get snapshot at tick (from cache or fetch) */
  getSnapshot: (tick: number) => Promise<ColonyDashboardJSON | null>;
}

export interface UseHistoricalModeOptions {
  /** Town ID for fetching snapshots */
  townId: string;

  /** Initial max tick */
  initialMaxTick?: number;

  /** Callback when mode changes */
  onModeChange?: (mode: HistoryMode) => void;

  /** Callback when tick changes */
  onTickChange?: (tick: number) => void;
}

// =============================================================================
// Hook
// =============================================================================

export function useHistoricalMode({
  townId,
  initialMaxTick = 0,
  onModeChange,
  onTickChange,
}: UseHistoricalModeOptions): HistoricalState & HistoricalActions {
  // State
  const [state, setState] = useState<HistoricalState>({
    mode: 'live',
    currentTick: initialMaxTick,
    maxTick: initialMaxTick,
    isPlaying: false,
    playbackSpeed: 1,
    isLoading: false,
    error: null,
  });

  // Snapshot cache
  const snapshotCache = useRef<Map<number, ColonyDashboardJSON>>(new Map());

  // Playback interval
  const playbackInterval = useRef<NodeJS.Timeout | null>(null);

  // ==========================================================================
  // Mode Management
  // ==========================================================================

  const enterHistorical = useCallback((tick?: number) => {
    const targetTick = tick ?? state.maxTick;
    setState((s) => ({
      ...s,
      mode: 'historical',
      currentTick: targetTick,
      isPlaying: false,
    }));
    onModeChange?.('historical');
  }, [state.maxTick, onModeChange]);

  const returnToLive = useCallback(() => {
    // Stop playback if playing
    if (playbackInterval.current) {
      clearInterval(playbackInterval.current);
      playbackInterval.current = null;
    }

    setState((s) => ({
      ...s,
      mode: 'live',
      currentTick: s.maxTick,
      isPlaying: false,
    }));
    onModeChange?.('live');
  }, [onModeChange]);

  // ==========================================================================
  // Navigation
  // ==========================================================================

  const seekTo = useCallback((tick: number) => {
    const clampedTick = Math.max(0, Math.min(tick, state.maxTick));
    setState((s) => ({
      ...s,
      currentTick: clampedTick,
    }));
    onTickChange?.(clampedTick);
  }, [state.maxTick, onTickChange]);

  const stepForward = useCallback(() => {
    seekTo(state.currentTick + 1);
  }, [state.currentTick, seekTo]);

  const stepBackward = useCallback(() => {
    seekTo(state.currentTick - 1);
  }, [state.currentTick, seekTo]);

  // ==========================================================================
  // Playback
  // ==========================================================================

  const togglePlay = useCallback(() => {
    setState((s) => ({ ...s, isPlaying: !s.isPlaying }));
  }, []);

  const setPlaybackSpeed = useCallback((speed: number) => {
    setState((s) => ({ ...s, playbackSpeed: speed }));
  }, []);

  // Handle playback
  useEffect(() => {
    if (state.mode === 'historical' && state.isPlaying) {
      const interval = 1000 / state.playbackSpeed;

      playbackInterval.current = setInterval(() => {
        setState((s) => {
          if (s.currentTick >= s.maxTick) {
            // Reached end, stop playing
            return { ...s, isPlaying: false };
          }
          const nextTick = s.currentTick + 1;
          onTickChange?.(nextTick);
          return { ...s, currentTick: nextTick };
        });
      }, interval);

      return () => {
        if (playbackInterval.current) {
          clearInterval(playbackInterval.current);
          playbackInterval.current = null;
        }
      };
    }
  }, [state.mode, state.isPlaying, state.playbackSpeed, onTickChange]);

  // ==========================================================================
  // Max Tick Management
  // ==========================================================================

  const updateMaxTick = useCallback((tick: number) => {
    setState((s) => {
      const newMax = Math.max(s.maxTick, tick);
      return {
        ...s,
        maxTick: newMax,
        // If in live mode, also update current tick
        currentTick: s.mode === 'live' ? newMax : s.currentTick,
      };
    });
  }, []);

  // ==========================================================================
  // Snapshot Management
  // ==========================================================================

  const getSnapshot = useCallback(async (tick: number): Promise<ColonyDashboardJSON | null> => {
    // Check cache first
    if (snapshotCache.current.has(tick)) {
      return snapshotCache.current.get(tick)!;
    }

    // Fetch from API
    setState((s) => ({ ...s, isLoading: true, error: null }));

    try {
      const response = await fetch(`/api/v1/town/${townId}/snapshot/${tick}`);
      if (!response.ok) {
        throw new Error(`Failed to fetch snapshot: ${response.status}`);
      }

      const snapshot = await response.json() as ColonyDashboardJSON;

      // Cache the result
      snapshotCache.current.set(tick, snapshot);

      // Limit cache size (keep last 100 snapshots)
      if (snapshotCache.current.size > 100) {
        const firstKey = snapshotCache.current.keys().next().value;
        if (firstKey !== undefined) {
          snapshotCache.current.delete(firstKey);
        }
      }

      setState((s) => ({ ...s, isLoading: false }));
      return snapshot;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Unknown error';
      setState((s) => ({ ...s, isLoading: false, error: message }));
      return null;
    }
  }, [townId]);

  // ==========================================================================
  // Return
  // ==========================================================================

  return {
    ...state,
    enterHistorical,
    returnToLive,
    seekTo,
    stepForward,
    stepBackward,
    togglePlay,
    setPlaybackSpeed,
    updateMaxTick,
    getSnapshot,
  };
}

export default useHistoricalMode;
