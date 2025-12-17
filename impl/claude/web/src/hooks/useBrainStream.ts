/**
 * useBrainStream: WebSocket streaming hook for Brain real-time updates.
 *
 * Phase 1 of Crown Jewels completion: Real-time Brain updates.
 *
 * Connects to the Brain WebSocket endpoint and receives:
 * - crystal_formed: New crystal captured (from CLI or API)
 * - memory_surfaced: Ghost memory activated
 * - vault_imported: Bulk import completed
 *
 * Features:
 * - Auto-reconnect with exponential backoff
 * - Subscription filtering (subscribe/unsubscribe to event types)
 * - Connection state tracking
 * - Event callbacks for UI updates
 *
 * Example:
 *   const { isConnected, latestCapture, events, connect } = useBrainStream({
 *     autoConnect: true,
 *     onCrystalFormed: (data) => refetchTopology(),
 *   });
 */

import { useState, useEffect, useRef, useCallback } from 'react';

// =============================================================================
// Types
// =============================================================================

export interface BrainEvent {
  type: string;
  data: {
    source_id: string;
    payload: {
      content_preview?: string;
      content_type?: string;
      [key: string]: unknown;
    };
    correlation_id: string;
  };
  timestamp: string;
}

interface UseBrainStreamOptions {
  /** Connect automatically on mount */
  autoConnect?: boolean;
  /** WebSocket URL (defaults to ws://localhost:8000/ws/brain) */
  wsUrl?: string;
  /** Event types to subscribe to */
  subscribeEvents?: string[];
  /** Callback when crystal is formed */
  onCrystalFormed?: (data: BrainEvent['data']) => void;
  /** Callback when memory is surfaced */
  onMemorySurfaced?: (data: BrainEvent['data']) => void;
  /** Callback when vault is imported */
  onVaultImported?: (data: BrainEvent['data']) => void;
  /** Callback on any event */
  onEvent?: (event: BrainEvent) => void;
  /** Callback on connection open */
  onConnect?: () => void;
  /** Callback on connection close */
  onDisconnect?: () => void;
  /** Callback on error */
  onError?: (error: Event) => void;
  /** Max reconnect attempts (default: 5) */
  maxReconnectAttempts?: number;
}

interface UseBrainStreamResult {
  /** Whether WebSocket is connected */
  isConnected: boolean;
  /** Session ID from server */
  sessionId: string | null;
  /** Latest crystal formed event */
  latestCapture: BrainEvent['data'] | null;
  /** Recent events (max 50) */
  events: BrainEvent[];
  /** Error message if any */
  error: string | null;
  /** Connect to WebSocket */
  connect: () => void;
  /** Disconnect from WebSocket */
  disconnect: () => void;
  /** Subscribe to event types */
  subscribe: (events: string[]) => void;
  /** Unsubscribe from event types */
  unsubscribe: (events: string[]) => void;
}

// =============================================================================
// Hook Implementation
// =============================================================================

export function useBrainStream({
  autoConnect = false,
  wsUrl,
  subscribeEvents = ['crystal_formed', 'memory_surfaced', 'vault_imported'],
  onCrystalFormed,
  onMemorySurfaced,
  onVaultImported,
  onEvent,
  onConnect,
  onDisconnect,
  onError,
  maxReconnectAttempts = 5,
}: UseBrainStreamOptions = {}): UseBrainStreamResult {
  // State
  const [isConnected, setIsConnected] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [latestCapture, setLatestCapture] = useState<BrainEvent['data'] | null>(null);
  const [events, setEvents] = useState<BrainEvent[]>([]);
  const [error, setError] = useState<string | null>(null);

  // Refs
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectAttempts = useRef(0);
  const reconnectTimeout = useRef<NodeJS.Timeout | null>(null);
  const callbacksRef = useRef({
    onCrystalFormed,
    onMemorySurfaced,
    onVaultImported,
    onEvent,
    onConnect,
    onDisconnect,
    onError,
  });

  // Update callbacks ref on change
  useEffect(() => {
    callbacksRef.current = {
      onCrystalFormed,
      onMemorySurfaced,
      onVaultImported,
      onEvent,
      onConnect,
      onDisconnect,
      onError,
    };
  }, [onCrystalFormed, onMemorySurfaced, onVaultImported, onEvent, onConnect, onDisconnect, onError]);

  // Determine WebSocket URL
  const getWsUrl = useCallback(() => {
    if (wsUrl) return wsUrl;
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.hostname;
    // In development, Vite runs on 3000 but backend is on 8000
    // Use 8000 for dev (3000 or empty port), otherwise use actual port
    const currentPort = window.location.port;
    const port = !currentPort || currentPort === '3000' ? '8000' : currentPort;
    return `${protocol}//${host}:${port}/ws/brain`;
  }, [wsUrl]);

  // Send message to WebSocket
  const sendMessage = useCallback((type: string, data: Record<string, unknown> = {}) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ type, ...data }));
    }
  }, []);

  // Subscribe to event types
  const subscribe = useCallback(
    (eventTypes: string[]) => {
      sendMessage('subscribe', { events: eventTypes });
    },
    [sendMessage]
  );

  // Unsubscribe from event types
  const unsubscribe = useCallback(
    (eventTypes: string[]) => {
      sendMessage('unsubscribe', { events: eventTypes });
    },
    [sendMessage]
  );

  // Process incoming message
  const processMessage = useCallback((message: BrainEvent) => {
    // Add to events list (max 50)
    setEvents((prev) => [message, ...prev].slice(0, 50));

    // Call event callback
    callbacksRef.current.onEvent?.(message);

    // Handle specific event types
    switch (message.type) {
      case 'connected':
        setSessionId(message.data?.source_id || null);
        break;

      case 'crystal_formed':
        setLatestCapture(message.data);
        callbacksRef.current.onCrystalFormed?.(message.data);
        break;

      case 'memory_surfaced':
        callbacksRef.current.onMemorySurfaced?.(message.data);
        break;

      case 'vault_imported':
        callbacksRef.current.onVaultImported?.(message.data);
        break;

      case 'error':
        setError(message.data?.payload?.message as string || 'Unknown error');
        break;

      case 'pong':
      case 'status':
        // Keepalive - no action needed
        break;
    }
  }, []);

  // Connect to WebSocket
  const connect = useCallback(() => {
    // Close existing connection
    if (wsRef.current) {
      wsRef.current.close();
    }

    // Clear reconnect timeout
    if (reconnectTimeout.current) {
      clearTimeout(reconnectTimeout.current);
      reconnectTimeout.current = null;
    }

    const url = getWsUrl();
    console.log('[Brain Stream] Connecting to:', url);

    try {
      const ws = new WebSocket(url);
      wsRef.current = ws;

      ws.onopen = () => {
        console.log('[Brain Stream] Connected');
        setIsConnected(true);
        setError(null);
        reconnectAttempts.current = 0;
        callbacksRef.current.onConnect?.();

        // Subscribe to desired events
        if (subscribeEvents.length > 0) {
          subscribe(subscribeEvents);
        }
      };

      ws.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data) as BrainEvent;
          processMessage(message);
        } catch (err) {
          console.warn('[Brain Stream] Failed to parse message:', event.data);
        }
      };

      ws.onerror = (event) => {
        console.error('[Brain Stream] Error:', event);
        setError('WebSocket error');
        callbacksRef.current.onError?.(event);
      };

      ws.onclose = (event) => {
        console.log('[Brain Stream] Disconnected:', event.code, event.reason);
        setIsConnected(false);
        wsRef.current = null;
        callbacksRef.current.onDisconnect?.();

        // Auto-reconnect with exponential backoff
        if (reconnectAttempts.current < maxReconnectAttempts && !event.wasClean) {
          const delay = Math.min(1000 * Math.pow(2, reconnectAttempts.current), 30000);
          console.log(`[Brain Stream] Reconnecting in ${delay}ms (attempt ${reconnectAttempts.current + 1})`);
          reconnectAttempts.current += 1;
          reconnectTimeout.current = setTimeout(connect, delay);
        }
      };
    } catch (err) {
      console.error('[Brain Stream] Connection failed:', err);
      setError((err as Error).message);
    }
  }, [getWsUrl, processMessage, subscribe, subscribeEvents, maxReconnectAttempts]);

  // Disconnect from WebSocket
  const disconnect = useCallback(() => {
    // Clear reconnect timeout
    if (reconnectTimeout.current) {
      clearTimeout(reconnectTimeout.current);
      reconnectTimeout.current = null;
    }

    // Reset reconnect attempts to prevent auto-reconnect
    reconnectAttempts.current = maxReconnectAttempts;

    if (wsRef.current) {
      console.log('[Brain Stream] Disconnecting');
      wsRef.current.close(1000, 'User disconnect');
      wsRef.current = null;
      setIsConnected(false);
    }
  }, [maxReconnectAttempts]);

  // Auto-connect effect
  useEffect(() => {
    if (autoConnect) {
      connect();
    }

    // Cleanup on unmount
    return () => {
      disconnect();
    };
  }, [autoConnect, connect, disconnect]);

  // Keepalive ping every 25 seconds
  useEffect(() => {
    if (!isConnected) return;

    const pingInterval = setInterval(() => {
      sendMessage('ping');
    }, 25000);

    return () => clearInterval(pingInterval);
  }, [isConnected, sendMessage]);

  return {
    isConnected,
    sessionId,
    latestCapture,
    events,
    error,
    connect,
    disconnect,
    subscribe,
    unsubscribe,
  };
}

// =============================================================================
// Exports
// =============================================================================

export type { UseBrainStreamOptions, UseBrainStreamResult };
