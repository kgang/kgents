import { useEffect, useRef, useCallback } from 'react';
import { useTownStore } from '@/stores/townStore';
import type { TownEvent, TownPhase } from '@/api/types';

interface SSEOptions {
  townId: string;
  speed?: number;
  phases?: number;
  autoConnect?: boolean;
  onConnect?: () => void;
  onDisconnect?: () => void;
  onError?: (error: Event) => void;
}

/**
 * Hook for SSE streaming of town events.
 *
 * Connects to /v1/town/{id}/live and updates the town store
 * with real-time events.
 */
export function useTownStream({
  townId,
  speed = 1.0,
  phases = 4,
  autoConnect = false,
  onConnect,
  onDisconnect,
  onError,
}: SSEOptions) {
  const eventSourceRef = useRef<EventSource | null>(null);
  const {
    addEvent,
    addInteraction,
    clearInteraction,
    setPhase,
    incrementDay,
    setPlaying,
    isPlaying,
  } = useTownStore();

  // Use ref to avoid stale closure in event handlers
  const handlersRef = useRef({ addEvent, addInteraction, clearInteraction, setPhase, incrementDay, setPlaying });
  handlersRef.current = { addEvent, addInteraction, clearInteraction, setPhase, incrementDay, setPlaying };

  const connect = useCallback(() => {
    if (!townId) {
      console.log('[SSE] No townId, skipping connect');
      return;
    }

    if (eventSourceRef.current) {
      console.log('[SSE] Closing existing connection');
      eventSourceRef.current.close();
    }

    const url = `/v1/town/${townId}/live?speed=${speed}&phases=${phases}`;
    console.log('[SSE] Connecting to:', url);
    const eventSource = new EventSource(url);
    eventSourceRef.current = eventSource;

    eventSource.onopen = () => {
      console.log('[SSE] Connected to town stream');
      onConnect?.();
    };

    // Handle live.start event
    eventSource.addEventListener('live.start', (e) => {
      const data = JSON.parse(e.data);
      console.log('[SSE] Stream started:', data);
      handlersRef.current.setPlaying(true);
    });

    // Handle live.event event (main simulation events)
    eventSource.addEventListener('live.event', (e) => {
      const event: TownEvent = JSON.parse(e.data);
      console.log('[SSE] Event:', event.operation, event.participants);

      // Add to event store
      handlersRef.current.addEvent(event);

      // Create interaction line for binary operations
      if (event.participants?.length >= 2) {
        const interactionId = `${event.tick}-${event.operation}`;

        handlersRef.current.addInteraction({
          id: interactionId,
          participants: event.participants,
          operation: event.operation,
          startTick: event.tick,
          fadeProgress: 0,
        });

        // Fade out interaction after 2 seconds
        let progress = 0;
        const fadeInterval = setInterval(() => {
          progress += 0.05;
          if (progress >= 1) {
            clearInterval(fadeInterval);
            handlersRef.current.clearInteraction(interactionId);
          }
        }, 100);
      }
    });

    // Handle live.phase event (phase transitions)
    eventSource.addEventListener('live.phase', (e) => {
      const data = JSON.parse(e.data);
      const newPhase = data.phase as TownPhase;
      console.log('[SSE] Phase change:', newPhase);
      handlersRef.current.setPhase(newPhase);
    });

    // Handle live.end event
    eventSource.addEventListener('live.end', (e) => {
      const data = JSON.parse(e.data);
      console.log('[SSE] Stream ended:', data);
      handlersRef.current.setPlaying(false);
      onDisconnect?.();
    });

    eventSource.onerror = (error) => {
      console.error('[SSE] Error:', error);
      onError?.(error);

      if (eventSource.readyState === EventSource.CLOSED) {
        console.log('[SSE] Connection closed');
        handlersRef.current.setPlaying(false);
        onDisconnect?.();
      }
    };

    return eventSource;
  }, [townId, speed, phases, onConnect, onDisconnect, onError]);

  const disconnect = useCallback(() => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
      setPlaying(false);
      onDisconnect?.();
    }
  }, [setPlaying, onDisconnect]);

  // Auto-connect when isPlaying changes
  useEffect(() => {
    console.log('[SSE] Effect running - autoConnect:', autoConnect, 'isPlaying:', isPlaying, 'townId:', townId);
    if (autoConnect && isPlaying && townId) {
      connect();
    } else if (!isPlaying) {
      disconnect();
    }

    return () => {
      disconnect();
    };
  }, [autoConnect, isPlaying, townId, connect, disconnect]);

  return {
    connect,
    disconnect,
    isConnected: !!eventSourceRef.current && eventSourceRef.current.readyState === EventSource.OPEN,
  };
}

/**
 * Hook for reconnecting SSE with exponential backoff.
 */
export function useReconnectingStream(options: SSEOptions & { maxRetries?: number }) {
  const { maxRetries = 5, ...sseOptions } = options;
  const retriesRef = useRef(0);
  const { connect, disconnect, isConnected } = useTownStream({
    ...sseOptions,
    onConnect: () => {
      retriesRef.current = 0;
      sseOptions.onConnect?.();
    },
    onError: (error) => {
      sseOptions.onError?.(error);
      if (retriesRef.current < maxRetries) {
        retriesRef.current++;
        const delay = Math.min(1000 * Math.pow(2, retriesRef.current), 30000);
        console.log(`[SSE] Reconnecting in ${delay}ms (attempt ${retriesRef.current}/${maxRetries})`);
        setTimeout(connect, delay);
      }
    },
  });

  return { connect, disconnect, isConnected };
}
