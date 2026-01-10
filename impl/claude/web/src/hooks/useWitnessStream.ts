/**
 * useWitnessStream — Real-time SSE connection to witness events
 *
 * Connects to /api/witness/stream and emits events as they arrive.
 * Handles reconnection and connection status.
 *
 * "The proof IS the decision."
 */

import { useCallback, useEffect, useRef, useState } from 'react';

// =============================================================================
// Types
// =============================================================================

/**
 * Witness SSE event types.
 *
 * MUST MATCH services/witness/bus.py WitnessEventType enum.
 *
 * When adding a new type:
 * 1. Add to this union
 * 2. Add to VISIBLE_EVENT_TYPES if it needs UI handling
 * 3. Add to eventTypes array in useWitnessStream
 */
export type WitnessEventType =
  // Core events (always visible in witness stream)
  | 'mark'
  | 'thought'
  | 'crystal'
  | 'kblock'
  | 'trail'
  // Domain events
  | 'spec'
  | 'sovereign'
  | 'director'
  | 'git'
  | 'agentese'
  | 'constitutional'
  | 'proxy'
  // Lifecycle events (internal)
  | 'daemon'
  // Connection events (special)
  | 'connected'
  | 'heartbeat';

/**
 * Event types that require SSE handlers.
 * Excludes: connected (handled by onopen), heartbeat (skipped), daemon (internal).
 */
const VISIBLE_EVENT_TYPES: readonly WitnessEventType[] = [
  'mark',
  'thought',
  'crystal',
  'kblock',
  'trail',
  'spec',
  'sovereign',
  'director',
  'git',
  'agentese',
  'constitutional',
  'proxy',
] as const;

// Semantic delta from K-Block edits
export interface SemanticDelta {
  kind: string;
  token_id: string;
  token_kind: string;
  token_value: string;
  old_value?: string;
  new_value?: string;
}

export interface WitnessEvent {
  id: string;
  type: WitnessEventType;
  timestamp: Date;

  // Mark fields
  action?: string;
  reasoning?: string;
  principles?: string[];
  author?: string;

  // Thought fields
  content?: string;
  source?: string;
  tags?: string[];

  // Crystal fields
  level?: string;
  insight?: string;
  significance?: number;

  // K-Block fields (editing IS witnessing)
  blockId?: string;
  path?: string;
  actor?: string;
  semanticDeltas?: SemanticDelta[];
  contentChanged?: boolean;

  // Spec Ledger fields (Living Spec integration)
  specAction?: string; // 'scan' | 'deprecate' | 'evidence_added'
  specPaths?: string[];
  specSummary?: Record<string, number>;
  orphanCount?: number;

  // AGENTESE fields (Law 3: Every invocation emits Mark)
  agentesePath?: string;
  agenteseAspect?: string;

  // Git fields
  commitHash?: string;
  commitMessage?: string;
  filesChanged?: number;

  // Director fields
  directorStatus?: string;

  // Topic (included for debugging/transparency)
  topic?: string;
}

export interface UseWitnessStream {
  events: WitnessEvent[];
  connected: boolean;
  reconnect: () => void;
  clear: () => void;
}

// =============================================================================
// Hook
// =============================================================================

const MAX_EVENTS = 100;
const INITIAL_RECONNECT_DELAY = 1000;
const MAX_RECONNECT_DELAY = 30000; // Cap at 30 seconds
const MAX_RECONNECT_ATTEMPTS = 10; // Stop retrying after 10 attempts

// Check if witness stream is disabled via env var
const STREAM_DISABLED = import.meta.env.VITE_DISABLE_WITNESS_STREAM === 'true';

export function useWitnessStream(): UseWitnessStream {
  const [events, setEvents] = useState<WitnessEvent[]>([]);
  const [connected, setConnected] = useState(false);
  const eventSourceRef = useRef<EventSource | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const reconnectAttemptRef = useRef(0);
  const hasLoggedDisabledRef = useRef(false);
  const hasLoggedMaxAttemptsRef = useRef(false);

  const connect = useCallback(() => {
    // Skip if stream is disabled via env var
    if (STREAM_DISABLED) {
      if (!hasLoggedDisabledRef.current) {
        console.debug('[useWitnessStream] Disabled via VITE_DISABLE_WITNESS_STREAM');
        hasLoggedDisabledRef.current = true;
      }
      return;
    }

    // Stop retrying after max attempts
    if (reconnectAttemptRef.current >= MAX_RECONNECT_ATTEMPTS) {
      if (!hasLoggedMaxAttemptsRef.current) {
        console.debug(
          '[useWitnessStream] Max reconnection attempts reached. Backend may not be running. ' +
            'Set VITE_DISABLE_WITNESS_STREAM=true to disable.'
        );
        hasLoggedMaxAttemptsRef.current = true;
      }
      return;
    }

    // Clean up existing connection
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
    }
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }

    const eventSource = new EventSource('/api/witness/stream');
    eventSourceRef.current = eventSource;

    eventSource.onopen = () => {
      setConnected(true);
      // Reset reconnection attempts on successful connection
      reconnectAttemptRef.current = 0;
      hasLoggedMaxAttemptsRef.current = false;
      // Add connection event
      const connectionEvent: WitnessEvent = {
        id: `conn-${Date.now()}`,
        type: 'connected',
        timestamp: new Date(),
        content: 'Witness stream connected',
      };
      setEvents((prev) => [connectionEvent, ...prev].slice(0, MAX_EVENTS));
    };

    // Helper to process incoming events
    const processEvent = (e: MessageEvent, eventType: WitnessEventType) => {
      try {
        const data = JSON.parse(e.data);

        // Skip heartbeats in the event list (but they confirm connection)
        if (data.type === 'heartbeat' || eventType === 'heartbeat') {
          return;
        }

        const event: WitnessEvent = {
          id: data.id || `evt-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`,
          type: eventType,
          timestamp: new Date(data.timestamp || Date.now()),
          // Mark fields
          action: data.action,
          reasoning: data.reasoning,
          principles: data.principles,
          author: data.author,
          // Thought fields
          content: data.content,
          source: data.source,
          tags: data.tags,
          // Crystal fields
          level: data.level,
          insight: data.insight,
          significance: data.significance,
          // K-Block fields
          blockId: data.block_id,
          path: data.path,
          actor: data.actor,
          semanticDeltas: data.semantic_deltas,
          contentChanged: data.content_changed,
          // Spec Ledger fields
          specAction: data.action,
          specPaths: data.paths,
          specSummary: data.summary,
          orphanCount: data.orphan_count,
          // AGENTESE fields
          agentesePath: data.stimulus?.metadata?.path,
          agenteseAspect: data.stimulus?.metadata?.aspect,
          // Git fields
          commitHash: data.commit_hash,
          commitMessage: data.message,
          filesChanged: data.files_changed,
          // Director fields
          directorStatus: data.status,
          // Topic (for debugging/transparency)
          topic: data.topic,
        };

        setEvents((prev) => [event, ...prev].slice(0, MAX_EVENTS));
      } catch (error) {
        console.error('Failed to parse witness event:', error);
      }
    };

    // SSE uses NAMED events (event: mark\ndata: {...})
    // We must use addEventListener for each event type, NOT onmessage
    // onmessage only catches unnamed events or "message" events
    // Note: 'connected' is handled by onopen, 'heartbeat' is skipped, 'daemon' is internal
    // Use VISIBLE_EVENT_TYPES as the single source of truth
    VISIBLE_EVENT_TYPES.forEach((eventType) => {
      eventSource.addEventListener(eventType, (e) => processEvent(e as MessageEvent, eventType));
    });

    // Also handle any unnamed events (fallback)
    eventSource.onmessage = (e) => processEvent(e, 'mark');

    eventSource.onerror = () => {
      setConnected(false);
      eventSource.close();

      // Increment attempt counter
      reconnectAttemptRef.current += 1;

      // Stop if max attempts reached
      if (reconnectAttemptRef.current >= MAX_RECONNECT_ATTEMPTS) {
        if (!hasLoggedMaxAttemptsRef.current) {
          console.debug(
            '[useWitnessStream] Max reconnection attempts reached. Backend may not be running.'
          );
          hasLoggedMaxAttemptsRef.current = true;
        }
        return;
      }

      // Exponential backoff: 1s, 2s, 4s, 8s, 16s, capped at 30s
      const delay = Math.min(
        INITIAL_RECONNECT_DELAY * Math.pow(2, reconnectAttemptRef.current - 1),
        MAX_RECONNECT_DELAY
      );

      // Only log first few attempts to avoid spam
      if (reconnectAttemptRef.current <= 3) {
        console.debug(
          `[useWitnessStream] Connection failed, retry ${reconnectAttemptRef.current}/${MAX_RECONNECT_ATTEMPTS} in ${delay}ms`
        );
      }

      reconnectTimeoutRef.current = setTimeout(() => {
        connect();
      }, delay);
    };
  }, []);

  const reconnect = useCallback(() => {
    // Reset attempt counter on manual reconnect
    reconnectAttemptRef.current = 0;
    hasLoggedMaxAttemptsRef.current = false;
    connect();
  }, [connect]);

  const clear = useCallback(() => {
    setEvents([]);
  }, []);

  // Connect on mount
  useEffect(() => {
    connect();

    return () => {
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
      }
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
    };
  }, [connect]);

  return {
    events,
    connected,
    reconnect,
    clear,
  };
}
