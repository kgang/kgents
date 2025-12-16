/**
 * useAtelierStream: SSE streaming hook for Atelier commissions.
 *
 * Handles streaming events from commission and collaboration endpoints.
 * Uses fetch with ReadableStream since EventSource only supports GET.
 *
 * Events:
 * - commission_received: Commission accepted
 * - contemplating: Artisan thinking
 * - working: Creation in progress
 * - fragment: Partial content
 * - piece_complete: Final piece
 * - error: Error occurred
 *
 * Example:
 *   const { commission, isStreaming, events, piece, error } = useAtelierStream();
 *   await commission('calligrapher', 'a haiku about APIs');
 */

import { useState, useCallback, useRef } from 'react';
import type { AtelierEvent, Piece } from '@/api/atelier';

// =============================================================================
// Types
// =============================================================================

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
}

// =============================================================================
// Hook Implementation
// =============================================================================

export function useAtelierStream(): UseAtelierStreamResult {
  // State
  const [events, setEvents] = useState<AtelierEvent[]>([]);
  const [piece, setPiece] = useState<Piece | null>(null);
  const [isStreaming, setIsStreaming] = useState(false);
  const [status, setStatus] = useState<'idle' | 'contemplating' | 'working' | 'complete' | 'error'>(
    'idle'
  );
  const [error, setError] = useState<string | null>(null);
  const [progress, setProgress] = useState(0);
  const [currentFragment, setCurrentFragment] = useState('');

  // Ref for abort controller
  const abortRef = useRef<AbortController | null>(null);

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

  return {
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
  };
}

// =============================================================================
// Exports
// =============================================================================

export type { UseAtelierStreamResult };
