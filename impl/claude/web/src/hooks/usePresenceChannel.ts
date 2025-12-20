/**
 * usePresenceChannel - SSE streaming hook for agent presence updates.
 *
 * CLI v7 Phase 4: Collaborative Canvas.
 *
 * Provides:
 * - Real-time cursor state streaming via SSE
 * - Connection management with automatic reconnection
 * - Agent cursor tracking (following, exploring, working, suggesting, waiting)
 * - Multiple agent support
 *
 * The PresenceChannel in presence.py is the source of truth.
 * The web layer subscribes via SSE - it doesn't own cursor state.
 *
 * Voice Anchor:
 * "Agents pretending to be there with their cursors moving,
 *  kinda following my cursor, kinda doing its own thing."
 *
 * @example
 * const { cursors, isConnected, latestCursor } = usePresenceChannel({
 *   autoConnect: true,
 * });
 */

import { useState, useEffect, useCallback, useRef } from 'react';

// =============================================================================
// Types - Mirror the Python AgentCursor dataclass
// =============================================================================

/** Cursor state - how the agent appears in shared space */
export type CursorState =
  | 'following' // Tracks user's focus with slight lag
  | 'exploring' // Moves independently through the graph
  | 'working' // Animates at a specific node
  | 'suggesting' // Pulses gently near a node
  | 'waiting'; // Stationary with breathing animation

/** Agent behavior patterns - personality expressed through movement */
export type CursorBehavior =
  | 'follower' // Follows human with slight delay
  | 'explorer' // Independent exploration
  | 'assistant' // Follows but occasionally suggests
  | 'autonomous'; // Does its own thing entirely

/** Agent cursor data from the PresenceChannel */
export interface AgentCursor {
  /** Unique agent identifier */
  agent_id: string;
  /** Human-readable name */
  display_name: string;
  /** Unique cursor ID for this session */
  cursor_id: string;
  /** Current cursor state */
  state: CursorState;
  /** Behavior pattern */
  behavior: CursorBehavior;
  /** AGENTESE path being focused (e.g., "self.memory.crystals") */
  focus_path: string | null;
  /** Brief activity description */
  activity: string;
  /** ISO timestamp of last update */
  last_updated: string;
}

/** Presence update event from SSE */
export interface PresenceEvent {
  type: 'cursor_update' | 'cursor_removed' | 'connected' | 'heartbeat';
  cursor?: AgentCursor;
  agent_id?: string;
  message?: string;
  timestamp: string;
}

/** Connection status for the presence channel */
export type PresenceStatus = 'disconnected' | 'connecting' | 'connected' | 'reconnecting' | 'error';

// =============================================================================
// Hook Options and Return Types
// =============================================================================

export interface UsePresenceChannelOptions {
  /** Whether to connect automatically on mount (default: true) */
  autoConnect?: boolean;
  /** Reconnection delay in ms (default: 3000) */
  reconnectDelay?: number;
  /** Maximum reconnect attempts (default: 5) */
  maxReconnectAttempts?: number;
  /** Callback when a cursor updates */
  onCursorUpdate?: (cursor: AgentCursor) => void;
  /** Callback when a cursor is removed */
  onCursorRemoved?: (agentId: string) => void;
  /** Callback on connection open */
  onConnect?: () => void;
  /** Callback on connection close */
  onDisconnect?: () => void;
}

export interface UsePresenceChannelReturn {
  /** Map of agent_id → cursor state */
  cursors: Map<string, AgentCursor>;
  /** All cursors as an array (for iteration) */
  cursorList: AgentCursor[];
  /** Connection status */
  status: PresenceStatus;
  /** Whether connected and receiving */
  isConnected: boolean;
  /** Most recently updated cursor */
  latestCursor: AgentCursor | null;
  /** Last update timestamp */
  lastUpdate: Date | null;
  /** Error message if any */
  error: string | null;
  /** Manually connect */
  connect: () => void;
  /** Manually disconnect */
  disconnect: () => void;
  /** Manually reconnect */
  reconnect: () => void;
}

// =============================================================================
// Hook Implementation
// =============================================================================

const API_BASE = import.meta.env.VITE_API_URL || '';

export function usePresenceChannel(
  options: UsePresenceChannelOptions = {}
): UsePresenceChannelReturn {
  const {
    autoConnect = true,
    reconnectDelay = 3000,
    maxReconnectAttempts = 5,
    onCursorUpdate,
    onCursorRemoved,
    onConnect,
    onDisconnect,
  } = options;

  // State
  const [cursors, setCursors] = useState<Map<string, AgentCursor>>(new Map());
  const [status, setStatus] = useState<PresenceStatus>('disconnected');
  const [error, setError] = useState<string | null>(null);
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null);
  const [latestCursor, setLatestCursor] = useState<AgentCursor | null>(null);

  // Refs for cleanup
  const streamRef = useRef<EventSource | null>(null);
  const reconnectTimeoutRef = useRef<number | null>(null);
  const reconnectAttempts = useRef(0);
  const mountedRef = useRef(true);
  const hasAutoConnected = useRef(false);

  // Stable callback refs
  const callbacksRef = useRef({
    onCursorUpdate,
    onCursorRemoved,
    onConnect,
    onDisconnect,
  });

  useEffect(() => {
    callbacksRef.current = {
      onCursorUpdate,
      onCursorRemoved,
      onConnect,
      onDisconnect,
    };
  }, [onCursorUpdate, onCursorRemoved, onConnect, onDisconnect]);

  // Build endpoint URL
  const buildEndpoint = useCallback(() => {
    return `${API_BASE}/agentese/self/presence/stream`;
  }, []);

  // Handle cursor update
  const handleCursorUpdate = useCallback((cursor: AgentCursor) => {
    setCursors((prev) => {
      const next = new Map(prev);
      next.set(cursor.agent_id, cursor);
      return next;
    });
    setLatestCursor(cursor);
    setLastUpdate(new Date());
    callbacksRef.current.onCursorUpdate?.(cursor);
  }, []);

  // Handle cursor removed
  const handleCursorRemoved = useCallback((agentId: string) => {
    setCursors((prev) => {
      const next = new Map(prev);
      next.delete(agentId);
      return next;
    });
    callbacksRef.current.onCursorRemoved?.(agentId);
  }, []);

  // Connect to SSE stream
  const connect = useCallback(() => {
    if (!mountedRef.current) return;

    // Close existing
    if (streamRef.current) {
      streamRef.current.close();
    }

    setStatus('connecting');
    setError(null);

    try {
      const endpoint = buildEndpoint();
      console.log('[Presence] Connecting to:', endpoint);
      const source = new EventSource(endpoint);
      streamRef.current = source;

      source.onopen = () => {
        if (mountedRef.current) {
          console.log('[Presence] Connected');
          setStatus('connected');
          setError(null);
          reconnectAttempts.current = 0;
          callbacksRef.current.onConnect?.();
        }
      };

      source.onmessage = (event) => {
        if (!mountedRef.current) return;

        try {
          const data = JSON.parse(event.data) as PresenceEvent;

          switch (data.type) {
            case 'cursor_update':
              if (data.cursor) {
                handleCursorUpdate(data.cursor);
              }
              break;

            case 'cursor_removed':
              if (data.agent_id) {
                handleCursorRemoved(data.agent_id);
              }
              break;

            case 'connected':
              console.log('[Presence] Server acknowledged connection');
              break;

            case 'heartbeat':
              // Keep-alive, no action needed
              break;

            default:
              console.warn('[Presence] Unknown event type:', data.type);
          }
        } catch (e) {
          console.error('[Presence] Failed to parse event:', e);
        }
      };

      source.onerror = () => {
        if (!mountedRef.current) return;

        console.warn('[Presence] Stream error, reconnecting...');
        setStatus('reconnecting');

        source.close();
        streamRef.current = null;

        // Auto-reconnect with backoff
        if (reconnectAttempts.current < maxReconnectAttempts) {
          const delay = Math.min(reconnectDelay * Math.pow(2, reconnectAttempts.current), 30000);
          console.log(
            `[Presence] Reconnecting in ${delay}ms (attempt ${reconnectAttempts.current + 1})`
          );
          reconnectAttempts.current += 1;
          reconnectTimeoutRef.current = window.setTimeout(connect, delay);
        } else {
          setStatus('error');
          setError('Max reconnection attempts reached');
        }
      };
    } catch (e) {
      console.error('[Presence] Failed to create stream:', e);
      setStatus('error');
      setError('Failed to connect to presence stream');
    }
  }, [
    buildEndpoint,
    handleCursorUpdate,
    handleCursorRemoved,
    reconnectDelay,
    maxReconnectAttempts,
  ]);

  // Disconnect
  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current !== null) {
      window.clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }
    if (streamRef.current) {
      console.log('[Presence] Disconnecting');
      streamRef.current.close();
      streamRef.current = null;
    }
    reconnectAttempts.current = 0;
    setStatus('disconnected');
    callbacksRef.current.onDisconnect?.();
  }, []);

  // Reconnect
  const reconnect = useCallback(() => {
    disconnect();
    connect();
  }, [disconnect, connect]);

  // Lifecycle - auto-connect on mount
  useEffect(() => {
    mountedRef.current = true;

    if (autoConnect && !hasAutoConnected.current) {
      hasAutoConnected.current = true;
      // Small delay to allow component mount
      const timer = setTimeout(connect, 100);
      return () => {
        clearTimeout(timer);
        mountedRef.current = false;
        disconnect();
        hasAutoConnected.current = false;
      };
    }

    return () => {
      mountedRef.current = false;
      disconnect();
    };
  }, [autoConnect, connect, disconnect]);

  // Derived state
  const cursorList = Array.from(cursors.values());
  const isConnected = status === 'connected';

  return {
    cursors,
    cursorList,
    status,
    isConnected,
    latestCursor,
    lastUpdate,
    error,
    connect,
    disconnect,
    reconnect,
  };
}

// =============================================================================
// Helper Functions
// =============================================================================

/**
 * Get the display color for a cursor state.
 */
export function getCursorColor(state: CursorState): string {
  switch (state) {
    case 'following':
      return 'cyan';
    case 'exploring':
      return 'blue';
    case 'working':
      return 'yellow';
    case 'suggesting':
      return 'green';
    case 'waiting':
      return 'gray';
    default:
      return 'gray';
  }
}

/**
 * Get the emoji for a cursor state.
 */
export function getCursorEmoji(state: CursorState): string {
  switch (state) {
    case 'following':
      return '👁️';
    case 'exploring':
      return '🔍';
    case 'working':
      return '⚡';
    case 'suggesting':
      return '💡';
    case 'waiting':
      return '⏳';
    default:
      return '○';
  }
}

/**
 * Format cursor as a human-readable status text.
 */
export function formatCursorStatus(cursor: AgentCursor): string {
  switch (cursor.state) {
    case 'exploring':
      return `${cursor.display_name} is exploring${cursor.focus_path ? ` ${cursor.focus_path}` : ''}...`;
    case 'working':
      return `${cursor.display_name} is working${cursor.focus_path ? ` on ${cursor.focus_path}` : ''}...`;
    case 'suggesting':
      return `${cursor.display_name} suggests${cursor.focus_path ? `: ${cursor.focus_path}` : ''}`;
    case 'following':
      return `${cursor.display_name} is following...`;
    case 'waiting':
      return `${cursor.display_name} is ready`;
    default:
      return cursor.activity || cursor.display_name;
  }
}

// =============================================================================
// Exports
// =============================================================================

export default usePresenceChannel;
