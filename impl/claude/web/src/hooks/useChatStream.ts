/**
 * useChatStream - Hook for streaming chat responses via SSE
 *
 * Provides real-time token streaming from AGENTESE chat nodes.
 * Works with any node_path (self.soul, world.town.citizen.*, etc.)
 *
 * @see plans/agentese-node-overhaul-strategy.md Session 6
 */

import { useState, useCallback, useRef, useEffect } from 'react';

// === Types ===

/**
 * A single chunk in the streaming response
 */
export interface StreamChunk {
  content: string;
  session_id: string;
  turn_number: number;
  is_complete: boolean;
  tokens_so_far?: number;
  full_response?: string;
  tokens_in?: number;
  tokens_out?: number;
  error?: string;
}

/**
 * Options for useChatStream hook
 */
export interface UseChatStreamOptions {
  /** Session ID to use (creates new if not provided) */
  sessionId?: string;
  /** Node path for new sessions (default: "self.soul") */
  nodePath?: string;
  /** Callback when chunk received */
  onChunk?: (chunk: StreamChunk) => void;
  /** Callback when stream completes */
  onComplete?: (fullResponse: string, metrics: { tokensIn: number; tokensOut: number }) => void;
  /** Callback on error */
  onError?: (error: Error) => void;
}

/**
 * Return value from useChatStream hook
 */
export interface UseChatStreamResult {
  /** Send a message and stream the response */
  send: (message: string) => void;
  /** Accumulated chunks */
  chunks: StreamChunk[];
  /** Full response (accumulated content) */
  fullResponse: string;
  /** Whether currently streaming */
  isStreaming: boolean;
  /** Error if stream failed */
  error: Error | null;
  /** Current session ID */
  sessionId: string | null;
  /** Turn number for current stream */
  turnNumber: number | null;
  /** Stop the current stream */
  stop: () => void;
  /** Clear accumulated chunks */
  clear: () => void;
}

/**
 * Hook to stream chat responses via SSE
 *
 * @param options - Stream options
 * @returns Stream state and controls
 *
 * @example
 * // Basic usage
 * const { send, fullResponse, isStreaming } = useChatStream();
 * send('Hello, what is categorical composition?');
 *
 * // With custom node path
 * const { send, fullResponse } = useChatStream({ nodePath: 'world.town.citizen.kent_001' });
 *
 * // With callbacks
 * const { send } = useChatStream({
 *   onChunk: (chunk) => console.log('Token:', chunk.content),
 *   onComplete: (response) => console.log('Done:', response),
 * });
 */
export function useChatStream(options: UseChatStreamOptions = {}): UseChatStreamResult {
  const {
    sessionId: initialSessionId,
    nodePath = 'self.soul',
    onChunk,
    onComplete,
    onError,
  } = options;

  const [chunks, setChunks] = useState<StreamChunk[]>([]);
  const [fullResponse, setFullResponse] = useState('');
  const [isStreaming, setIsStreaming] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  const [sessionId, setSessionId] = useState<string | null>(initialSessionId ?? null);
  const [turnNumber, setTurnNumber] = useState<number | null>(null);

  const eventSourceRef = useRef<EventSource | null>(null);
  const abortControllerRef = useRef<AbortController | null>(null);

  const stop = useCallback(() => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
    }
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }
    setIsStreaming(false);
  }, []);

  const clear = useCallback(() => {
    setChunks([]);
    setFullResponse('');
    setError(null);
  }, []);

  const send = useCallback(
    async (message: string) => {
      // Clean up any previous stream
      stop();
      clear();
      setIsStreaming(true);
      setError(null);

      try {
        // Build the SSE URL for streaming
        // Pattern: POST to /agentese/self/chat/stream with body, then GET stream endpoint
        // For SSE, we use the /stream suffix on the aspect
        const streamUrl = new URL('/agentese/self/chat/stream/stream', window.location.origin);

        // Add query params for the request
        streamUrl.searchParams.set('message', message);
        if (sessionId) {
          streamUrl.searchParams.set('session_id', sessionId);
        }
        if (nodePath) {
          streamUrl.searchParams.set('node_path', nodePath);
        }

        // Create EventSource for SSE
        const eventSource = new EventSource(streamUrl.toString());
        eventSourceRef.current = eventSource;

        let accumulatedContent = '';
        let lastChunk: StreamChunk | null = null;

        eventSource.onopen = () => {
          // Connection established
        };

        eventSource.onmessage = (event) => {
          try {
            // Parse the SSE data envelope
            // Gateway wraps in: { data: chunk, meta: { status, stream: {...} } }
            const envelope = JSON.parse(event.data);
            const chunk: StreamChunk = envelope.data || envelope;

            lastChunk = chunk;

            if (chunk.session_id && !sessionId) {
              setSessionId(chunk.session_id);
            }
            if (chunk.turn_number) {
              setTurnNumber(chunk.turn_number);
            }

            if (chunk.error) {
              // Error chunk
              const err = new Error(chunk.error);
              setError(err);
              onError?.(err);
              eventSource.close();
              setIsStreaming(false);
              return;
            }

            if (chunk.content) {
              accumulatedContent += chunk.content;
              setFullResponse(accumulatedContent);
            }

            setChunks((prev) => [...prev, chunk]);
            onChunk?.(chunk);

            if (chunk.is_complete) {
              // Stream complete
              eventSource.close();
              setIsStreaming(false);
              onComplete?.(chunk.full_response || accumulatedContent, {
                tokensIn: chunk.tokens_in || 0,
                tokensOut: chunk.tokens_out || 0,
              });
            }
          } catch (e) {
            console.error('Failed to parse SSE chunk:', e, event.data);
          }
        };

        eventSource.addEventListener('complete', (event) => {
          // Gateway sends explicit complete event
          try {
            // Parse to validate format (may be empty)
            JSON.parse((event as MessageEvent).data);
            eventSource.close();
            setIsStreaming(false);

            if (lastChunk) {
              onComplete?.(lastChunk.full_response || accumulatedContent, {
                tokensIn: lastChunk.tokens_in || 0,
                tokensOut: lastChunk.tokens_out || 0,
              });
            }
          } catch {
            // Complete event may not have data
            eventSource.close();
            setIsStreaming(false);
          }
        });

        eventSource.addEventListener('error', (event) => {
          // Gateway sends explicit error event
          try {
            const envelope = JSON.parse((event as MessageEvent).data);
            const err = new Error(envelope.meta?.error?.message || 'Stream error');
            setError(err);
            onError?.(err);
          } catch {
            // Generic error
            const err = new Error('Stream connection failed');
            setError(err);
            onError?.(err);
          }
          eventSource.close();
          setIsStreaming(false);
        });

        eventSource.onerror = () => {
          // Network error or server closed connection
          if (eventSource.readyState === EventSource.CLOSED) {
            // Normal close, stream complete
            setIsStreaming(false);
          } else {
            // Actual error
            const err = new Error('Stream connection failed');
            setError(err);
            onError?.(err);
            eventSource.close();
            setIsStreaming(false);
          }
        };
      } catch (e) {
        const err = e instanceof Error ? e : new Error(String(e));
        setError(err);
        onError?.(err);
        setIsStreaming(false);
      }
    },
    [sessionId, nodePath, onChunk, onComplete, onError, stop, clear]
  );

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      stop();
    };
  }, [stop]);

  return {
    send,
    chunks,
    fullResponse,
    isStreaming,
    error,
    sessionId,
    turnNumber,
    stop,
    clear,
  };
}

/**
 * Alternative hook for POST-based streaming (uses fetch with ReadableStream)
 *
 * Use this when you need to send complex request bodies that don't fit in query params.
 */
export function useChatStreamPost(options: UseChatStreamOptions = {}): UseChatStreamResult {
  const {
    sessionId: initialSessionId,
    nodePath = 'self.soul',
    onChunk,
    onComplete,
    onError,
  } = options;

  const [chunks, setChunks] = useState<StreamChunk[]>([]);
  const [fullResponse, setFullResponse] = useState('');
  const [isStreaming, setIsStreaming] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  const [sessionId, setSessionId] = useState<string | null>(initialSessionId ?? null);
  const [turnNumber, setTurnNumber] = useState<number | null>(null);

  const abortControllerRef = useRef<AbortController | null>(null);

  const stop = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }
    setIsStreaming(false);
  }, []);

  const clear = useCallback(() => {
    setChunks([]);
    setFullResponse('');
    setError(null);
  }, []);

  const send = useCallback(
    async (message: string) => {
      stop();
      clear();
      setIsStreaming(true);
      setError(null);

      const controller = new AbortController();
      abortControllerRef.current = controller;

      try {
        // Use POST for streaming with body
        const response = await fetch('/agentese/self/chat/stream/stream', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Accept: 'text/event-stream',
          },
          body: JSON.stringify({
            message,
            session_id: sessionId,
            node_path: nodePath,
          }),
          signal: controller.signal,
        });

        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const reader = response.body?.getReader();
        if (!reader) {
          throw new Error('Response body is not readable');
        }

        const decoder = new TextDecoder();
        let buffer = '';
        let accumulatedContent = '';
        let lastChunk: StreamChunk | null = null;

        while (true) {
          const { done, value } = await reader.read();

          if (done) {
            setIsStreaming(false);
            if (lastChunk) {
              onComplete?.(lastChunk.full_response || accumulatedContent, {
                tokensIn: lastChunk.tokens_in || 0,
                tokensOut: lastChunk.tokens_out || 0,
              });
            }
            break;
          }

          buffer += decoder.decode(value, { stream: true });

          // Parse SSE events from buffer
          const lines = buffer.split('\n');
          buffer = lines.pop() || ''; // Keep incomplete line in buffer

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              try {
                const data = JSON.parse(line.slice(6));
                const chunk: StreamChunk = data.data || data;

                lastChunk = chunk;

                if (chunk.session_id && !sessionId) {
                  setSessionId(chunk.session_id);
                }
                if (chunk.turn_number) {
                  setTurnNumber(chunk.turn_number);
                }

                if (chunk.error) {
                  const err = new Error(chunk.error);
                  setError(err);
                  onError?.(err);
                  reader.cancel();
                  setIsStreaming(false);
                  return;
                }

                if (chunk.content) {
                  accumulatedContent += chunk.content;
                  setFullResponse(accumulatedContent);
                }

                setChunks((prev) => [...prev, chunk]);
                onChunk?.(chunk);

                if (chunk.is_complete) {
                  reader.cancel();
                  setIsStreaming(false);
                  onComplete?.(chunk.full_response || accumulatedContent, {
                    tokensIn: chunk.tokens_in || 0,
                    tokensOut: chunk.tokens_out || 0,
                  });
                  return;
                }
              } catch (e) {
                console.error('Failed to parse SSE data:', e);
              }
            }
          }
        }
      } catch (e) {
        if (e instanceof Error && e.name === 'AbortError') {
          // User cancelled, not an error
          setIsStreaming(false);
          return;
        }
        const err = e instanceof Error ? e : new Error(String(e));
        setError(err);
        onError?.(err);
        setIsStreaming(false);
      }
    },
    [sessionId, nodePath, onChunk, onComplete, onError, stop, clear]
  );

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      stop();
    };
  }, [stop]);

  return {
    send,
    chunks,
    fullResponse,
    isStreaming,
    error,
    sessionId,
    turnNumber,
    stop,
    clear,
  };
}

export default useChatStream;
