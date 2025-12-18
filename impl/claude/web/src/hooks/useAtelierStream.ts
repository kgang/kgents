/**
 * useAtelierStream: SSE streaming hook for Atelier sessions.
 *
 * Handles streaming events from commission, collaboration, and live session endpoints.
 * Uses fetch with ReadableStream since EventSource only supports GET.
 *
 * Events (Commission/Collaboration):
 * - commission_received: Commission accepted
 * - contemplating: Artisan thinking
 * - working: Creation in progress
 * - fragment: Partial content
 * - piece_complete: Final piece
 * - error: Error occurred
 *
 * Events (Live Session - Phase 2):
 * - spectator_joined: New spectator joined
 * - spectator_left: Spectator left
 * - cursor_update: Spectator cursor moved
 * - bid_submitted: New bid in queue
 * - bid_accepted: Bid accepted by builder
 * - content_update: Live content changed
 *
 * Example:
 *   const { commission, isStreaming, events, piece, error } = useAtelierStream();
 *   await commission('calligrapher', 'a haiku about APIs');
 *
 * @see plans/crown-jewels-genesis-phase2.md - Week 3: useAtelierStream enhancement
 */

import { useState, useCallback, useRef, useEffect } from 'react';
import type { AtelierEvent, Piece } from '@/api/atelier';

// =============================================================================
// Types
// =============================================================================

/** Spectator cursor for overlay display */
export interface SpectatorCursor {
  id: string;
  position: { x: number; y: number };
  citizenId?: string;
  eigenvector?: number[];
  lastUpdate: number;
  name?: string;
}

/** Session state for live FishbowlCanvas */
export interface SessionState {
  sessionId: string;
  isLive: boolean;
  spectatorCount: number;
  content: string;
  contentType: 'image' | 'text' | 'code';
  artisanId?: string;
  artisanName?: string;
}

interface UseAtelierStreamResult {
  /** All received events */
  events: AtelierEvent[];
  /** Completed piece (if any) */
  piece: Piece | null;
  /** Whether streaming is in progress */
  isStreaming: boolean;
  /** Current status message */
  status: 'idle' | 'contemplating' | 'working' | 'complete' | 'error';
  /** Error message if any */
  error: string | null;
  /** Progress (0-1) during fragment streaming */
  progress: number;
  /** Current fragment content */
  currentFragment: string;
  /** Start a commission */
  commission: (artisan: string, request: string, patron?: string) => Promise<Piece | null>;
  /** Start a collaboration */
  collaborate: (
    artisans: string[],
    request: string,
    mode?: string,
    patron?: string
  ) => Promise<Piece | null>;
  /** Cancel current stream */
  cancel: () => void;
  /** Reset state */
  reset: () => void;

  // === Phase 2: Live Session Support ===

  /** Current session state (for FishbowlCanvas) */
  sessionState: SessionState | null;
  /** Active spectator cursors */
  spectatorCursors: SpectatorCursor[];
  /** Subscribe to a live session */
  subscribeToSession: (sessionId: string) => void;
  /** Unsubscribe from live session */
  unsubscribeFromSession: () => void;
  /** Update own cursor position */
  updateCursor: (position: { x: number; y: number }) => void;
  /** Whether connected to a live session */
  isSessionLive: boolean;
}

// =============================================================================
// Hook Implementation
// =============================================================================

export function useAtelierStream(): UseAtelierStreamResult {
  // State - Commission/Collaboration
  const [events, setEvents] = useState<AtelierEvent[]>([]);
  const [piece, setPiece] = useState<Piece | null>(null);
  const [isStreaming, setIsStreaming] = useState(false);
  const [status, setStatus] = useState<'idle' | 'contemplating' | 'working' | 'complete' | 'error'>(
    'idle'
  );
  const [error, setError] = useState<string | null>(null);
  const [progress, setProgress] = useState(0);
  const [currentFragment, setCurrentFragment] = useState('');

  // State - Live Session (Phase 2)
  const [sessionState, setSessionState] = useState<SessionState | null>(null);
  const [spectatorCursors, setSpectatorCursors] = useState<SpectatorCursor[]>([]);
  const [isSessionLive, setIsSessionLive] = useState(false);

  // Refs for abort controllers
  const abortRef = useRef<AbortController | null>(null);
  const sessionAbortRef = useRef<AbortController | null>(null);
  const spectatorIdRef = useRef<string | null>(null);

  // Parse SSE event from text
  const parseSSEEvent = useCallback((text: string): AtelierEvent | null => {
    const lines = text.trim().split('\n');
    let data = '';

    for (const line of lines) {
      if (line.startsWith('data:')) {
        data = line.slice(6).trim();
      }
    }

    if (data) {
      try {
        const parsed = JSON.parse(data);
        return parsed as AtelierEvent;
      } catch {
        console.warn('[Atelier Stream] Failed to parse SSE data:', data);
        return null;
      }
    }
    return null;
  }, []);

  // Process incoming event
  const processEvent = useCallback((event: AtelierEvent) => {
    setEvents((prev) => [...prev, event]);

    switch (event.event_type) {
      case 'commission_received':
        setStatus('contemplating');
        break;
      case 'contemplating':
        setStatus('contemplating');
        break;
      case 'working':
        setStatus('working');
        break;
      case 'fragment':
        setProgress((event.data?.accumulated_length as number) || 0);
        setCurrentFragment((event.data?.fragment as string) || '');
        break;
      case 'piece_complete':
        setStatus('complete');
        setProgress(1);
        if (event.data?.piece) {
          setPiece(event.data.piece as Piece);
        }
        break;
      case 'error':
        setStatus('error');
        setError(event.message || 'Unknown error');
        break;
    }
  }, []);

  // Stream from SSE endpoint
  const streamFromEndpoint = useCallback(
    async (url: string, body: Record<string, unknown>): Promise<Piece | null> => {
      // Reset state
      setEvents([]);
      setPiece(null);
      setIsStreaming(true);
      setStatus('idle');
      setError(null);
      setProgress(0);
      setCurrentFragment('');

      // Create abort controller
      abortRef.current = new AbortController();

      let resultPiece: Piece | null = null;

      try {
        const response = await fetch(url, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-API-Key': localStorage.getItem('api_key') || '',
          },
          body: JSON.stringify(body),
          signal: abortRef.current.signal,
        });

        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const reader = response.body?.getReader();
        if (!reader) {
          throw new Error('No response body');
        }

        const decoder = new TextDecoder();
        let buffer = '';

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          buffer += decoder.decode(value, { stream: true });

          // Process complete SSE messages
          const messages = buffer.split('\n\n');
          buffer = messages.pop() || ''; // Keep incomplete message in buffer

          for (const message of messages) {
            if (message.trim()) {
              const event = parseSSEEvent(message);
              if (event) {
                processEvent(event);
                if (event.event_type === 'piece_complete' && event.data?.piece) {
                  resultPiece = event.data.piece as Piece;
                }
              }
            }
          }
        }

        // Process any remaining buffer
        if (buffer.trim()) {
          const event = parseSSEEvent(buffer);
          if (event) {
            processEvent(event);
            if (event.event_type === 'piece_complete' && event.data?.piece) {
              resultPiece = event.data.piece as Piece;
            }
          }
        }

        return resultPiece;
      } catch (err) {
        if ((err as Error).name === 'AbortError') {
          console.log('[Atelier Stream] Cancelled');
        } else {
          console.error('[Atelier Stream] Error:', err);
          setStatus('error');
          setError((err as Error).message);
        }
        return null;
      } finally {
        setIsStreaming(false);
        abortRef.current = null;
      }
    },
    [parseSSEEvent, processEvent]
  );

  // Commission an artisan
  const commission = useCallback(
    async (artisan: string, request: string, patron?: string): Promise<Piece | null> => {
      return streamFromEndpoint('/api/atelier/commission', {
        artisan,
        request,
        patron: patron || 'wanderer',
      });
    },
    [streamFromEndpoint]
  );

  // Collaborate with multiple artisans
  const collaborate = useCallback(
    async (
      artisans: string[],
      request: string,
      mode: string = 'duet',
      patron?: string
    ): Promise<Piece | null> => {
      return streamFromEndpoint('/api/atelier/collaborate', {
        artisans,
        request,
        mode,
        patron: patron || 'wanderer',
      });
    },
    [streamFromEndpoint]
  );

  // Cancel current stream
  const cancel = useCallback(() => {
    if (abortRef.current) {
      abortRef.current.abort();
    }
  }, []);

  // Reset state
  const reset = useCallback(() => {
    cancel();
    setEvents([]);
    setPiece(null);
    setIsStreaming(false);
    setStatus('idle');
    setError(null);
    setProgress(0);
    setCurrentFragment('');
  }, [cancel]);

  // ==========================================================================
  // Phase 2: Live Session Support
  // ==========================================================================

  // Process session event
  const processSessionEvent = useCallback((event: AtelierEvent) => {
    switch (event.event_type) {
      case 'spectator_joined':
        setSessionState((prev) =>
          prev
            ? { ...prev, spectatorCount: prev.spectatorCount + 1 }
            : null
        );
        break;

      case 'spectator_left':
        setSessionState((prev) =>
          prev
            ? { ...prev, spectatorCount: Math.max(0, prev.spectatorCount - 1) }
            : null
        );
        // Remove cursor for departed spectator
        if (event.data?.spectator_id) {
          setSpectatorCursors((prev) =>
            prev.filter((c) => c.id !== event.data?.spectator_id)
          );
        }
        break;

      case 'cursor_update':
        if (event.data?.spectator_id && event.data?.position) {
          const { spectator_id, position, citizen_id, eigenvector, name } = event.data as {
            spectator_id: string;
            position: { x: number; y: number };
            citizen_id?: string;
            eigenvector?: number[];
            name?: string;
          };
          setSpectatorCursors((prev) => {
            const existing = prev.findIndex((c) => c.id === spectator_id);
            const newCursor: SpectatorCursor = {
              id: spectator_id,
              position,
              citizenId: citizen_id,
              eigenvector,
              lastUpdate: Date.now(),
              name,
            };
            if (existing >= 0) {
              const updated = [...prev];
              updated[existing] = newCursor;
              return updated;
            }
            return [...prev, newCursor];
          });
        }
        break;

      case 'content_update':
        if (event.data?.content !== undefined) {
          setSessionState((prev) =>
            prev
              ? {
                  ...prev,
                  content: event.data?.content as string,
                  contentType: (event.data?.content_type as 'image' | 'text' | 'code') || prev.contentType,
                }
              : null
          );
        }
        break;

      case 'session_ended':
        setIsSessionLive(false);
        setSessionState((prev) => (prev ? { ...prev, isLive: false } : null));
        break;
    }
  }, []);

  // Subscribe to live session
  const subscribeToSession = useCallback(
    async (sessionId: string) => {
      // Cancel any existing subscription
      if (sessionAbortRef.current) {
        sessionAbortRef.current.abort();
      }

      sessionAbortRef.current = new AbortController();
      setIsSessionLive(true);
      setSessionState({
        sessionId,
        isLive: true,
        spectatorCount: 0,
        content: '',
        contentType: 'text',
      });
      setSpectatorCursors([]);

      try {
        const response = await fetch(`/api/atelier/session/${sessionId}/stream`, {
          method: 'GET',
          headers: {
            'Accept': 'text/event-stream',
            'X-API-Key': localStorage.getItem('api_key') || '',
          },
          signal: sessionAbortRef.current.signal,
        });

        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const reader = response.body?.getReader();
        if (!reader) {
          throw new Error('No response body');
        }

        const decoder = new TextDecoder();
        let buffer = '';

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          buffer += decoder.decode(value, { stream: true });

          const messages = buffer.split('\n\n');
          buffer = messages.pop() || '';

          for (const message of messages) {
            if (message.trim()) {
              const event = parseSSEEvent(message);
              if (event) {
                processSessionEvent(event);
              }
            }
          }
        }
      } catch (err) {
        if ((err as Error).name !== 'AbortError') {
          console.error('[Atelier Session] Error:', err);
          setError((err as Error).message);
        }
      } finally {
        setIsSessionLive(false);
        sessionAbortRef.current = null;
      }
    },
    [parseSSEEvent, processSessionEvent]
  );

  // Unsubscribe from live session
  const unsubscribeFromSession = useCallback(() => {
    if (sessionAbortRef.current) {
      sessionAbortRef.current.abort();
      sessionAbortRef.current = null;
    }
    setIsSessionLive(false);
    setSessionState(null);
    setSpectatorCursors([]);
    spectatorIdRef.current = null;
  }, []);

  // Update own cursor position
  const updateCursor = useCallback(
    async (position: { x: number; y: number }) => {
      if (!sessionState?.sessionId || !spectatorIdRef.current) return;

      try {
        await fetch('/api/atelier/session/cursor', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-API-Key': localStorage.getItem('api_key') || '',
          },
          body: JSON.stringify({
            session_id: sessionState.sessionId,
            spectator_id: spectatorIdRef.current,
            position_x: position.x,
            position_y: position.y,
          }),
        });
      } catch (err) {
        console.warn('[Atelier Cursor] Failed to update cursor:', err);
      }
    },
    [sessionState?.sessionId]
  );

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (sessionAbortRef.current) {
        sessionAbortRef.current.abort();
      }
    };
  }, []);

  return {
    // Commission/Collaboration
    events,
    piece,
    isStreaming,
    status,
    error,
    progress,
    currentFragment,
    commission,
    collaborate,
    cancel,
    reset,

    // Phase 2: Live Session
    sessionState,
    spectatorCursors,
    subscribeToSession,
    unsubscribeFromSession,
    updateCursor,
    isSessionLive,
  };
}

// =============================================================================
// Exports
// =============================================================================

export type { UseAtelierStreamResult, SpectatorCursor, SessionState };
