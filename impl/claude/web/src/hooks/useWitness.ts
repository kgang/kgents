/**
 * useWitness - Hook for witness mark CRUD operations.
 *
 * Provides:
 * - Recent marks fetching with filtering
 * - Mark creation
 * - Mark retraction
 * - Real-time updates via SSE integration
 *
 * @see plans/witness-fusion-ux-implementation.md
 */

import { useState, useEffect, useCallback } from 'react';
import type { Mark, CreateMarkRequest, MarkFilters } from '@/api/witness';
import {
  getRecentMarks,
  createMark as apiCreateMark,
  retractMark as apiRetractMark,
  subscribeToMarks,
} from '@/api/witness';

// =============================================================================
// Types
// =============================================================================

export interface UseWitnessOptions {
  /** Maximum marks to fetch */
  limit?: number;

  /** Filter by author */
  author?: 'kent' | 'claude' | 'system';

  /** Filter by principles */
  principles?: string[];

  /** Session ID filter */
  sessionId?: string;

  /** Only marks from today */
  today?: boolean;

  /** Enable real-time updates */
  realtime?: boolean;
}

export interface UseWitnessResult {
  /** Fetched marks */
  marks: Mark[];

  /** Loading state */
  isLoading: boolean;

  /** Error message if any */
  error: Error | null;

  /** Create a new mark */
  createMark: (request: CreateMarkRequest) => Promise<Mark>;

  /** Retract a mark */
  retractMark: (markId: string, reason: string) => Promise<void>;

  /** Refresh marks from server */
  refetch: () => Promise<void>;

  /** Whether currently connected to real-time updates */
  isConnected: boolean;
}

// =============================================================================
// Hook Implementation
// =============================================================================

export function useWitness(options: UseWitnessOptions = {}): UseWitnessResult {
  const {
    limit = 50,
    author,
    principles,
    sessionId,
    today = false,
    realtime = true,
  } = options;

  // State
  const [marks, setMarks] = useState<Mark[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);
  const [isConnected, setIsConnected] = useState(false);

  // Build filters
  const buildFilters = useCallback((): MarkFilters => {
    return {
      limit,
      author,
      principles,
      today,
    };
  }, [limit, author, principles, today]);

  // Fetch marks
  const fetchMarks = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      const filters = buildFilters();
      const fetchedMarks = await getRecentMarks(filters);

      // Filter by session if specified
      let result = fetchedMarks;
      if (sessionId) {
        result = fetchedMarks.filter((m) => m.session_id === sessionId);
      }

      setMarks(result);
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Failed to fetch marks'));
    } finally {
      setIsLoading(false);
    }
  }, [buildFilters, sessionId]);

  // Initial fetch
  useEffect(() => {
    fetchMarks();
  }, [fetchMarks]);

  // Real-time subscription
  useEffect(() => {
    if (!realtime) return;

    const cleanup = subscribeToMarks(
      (newMark) => {
        // Add new mark to the top of the list
        setMarks((prev) => {
          // Check if mark already exists (dedup)
          if (prev.some((m) => m.id === newMark.id)) {
            return prev;
          }

          // Apply filters
          if (author && newMark.author !== author) {
            return prev;
          }
          if (sessionId && newMark.session_id !== sessionId) {
            return prev;
          }
          if (today) {
            const markDate = new Date(newMark.timestamp);
            const todayDate = new Date();
            if (markDate.toDateString() !== todayDate.toDateString()) {
              return prev;
            }
          }

          // Add to front, trim to limit
          return [newMark, ...prev].slice(0, limit);
        });
      },
      {
        onConnect: () => setIsConnected(true),
        onDisconnect: () => setIsConnected(false),
      }
    );

    return cleanup;
  }, [realtime, author, sessionId, today, limit]);

  // Create mark
  const createMark = useCallback(async (request: CreateMarkRequest): Promise<Mark> => {
    const newMark = await apiCreateMark(request);

    // Optimistically add to list (if SSE fails to deliver)
    setMarks((prev) => {
      if (prev.some((m) => m.id === newMark.id)) {
        return prev;
      }
      return [newMark, ...prev].slice(0, limit);
    });

    return newMark;
  }, [limit]);

  // Retract mark
  const retractMark = useCallback(async (markId: string, reason: string): Promise<void> => {
    const updatedMark = await apiRetractMark(markId, reason);

    // Update in list
    setMarks((prev) =>
      prev.map((m) => (m.id === markId ? updatedMark : m))
    );
  }, []);

  return {
    marks,
    isLoading,
    error,
    createMark,
    retractMark,
    refetch: fetchMarks,
    isConnected,
  };
}

// =============================================================================
// Exports
// =============================================================================

export default useWitness;
