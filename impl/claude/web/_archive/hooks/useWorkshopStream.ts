import { useEffect, useRef, useCallback } from 'react';
import { useWorkshopStore } from '@/stores/workshopStore';
import type { WorkshopEvent, WorkshopPhase, WorkshopMetrics } from '@/api/types';

interface SSEOptions {
  speed?: number;
  autoConnect?: boolean;
  onConnect?: () => void;
  onDisconnect?: () => void;
  onError?: (error: Event) => void;
}

/**
 * Hook for SSE streaming of workshop events.
 *
 * Connects to /v1/workshop/stream and updates the workshop store
 * with real-time events.
 */
export function useWorkshopStream({
  speed = 1.0,
  autoConnect = false,
  onConnect,
  onDisconnect,
  onError,
}: SSEOptions = {}) {
  const eventSourceRef = useRef<EventSource | null>(null);
  const { addEvent, setPhase, setRunning, setMetrics, isRunning } = useWorkshopStore();

  // Use ref to avoid stale closure in event handlers
  const handlersRef = useRef({ addEvent, setPhase, setRunning, setMetrics });
  handlersRef.current = { addEvent, setPhase, setRunning, setMetrics };

  const connect = useCallback(() => {
    if (eventSourceRef.current) {
      console.log('[Workshop SSE] Closing existing connection');
      eventSourceRef.current.close();
    }

    const url = `/v1/workshop/stream?speed=${speed}`;
    console.log('[Workshop SSE] Connecting to:', url);
    const eventSource = new EventSource(url);
    eventSourceRef.current = eventSource;

    eventSource.onopen = () => {
      console.log('[Workshop SSE] Connected');
      onConnect?.();
    };

    // Handle workshop.start event
    eventSource.addEventListener('workshop.start', (e) => {
      const data = JSON.parse(e.data);
      console.log('[Workshop SSE] Start:', data);
      handlersRef.current.setRunning(true);
      if (data.phase) {
        handlersRef.current.setPhase(data.phase as WorkshopPhase);
      }
    });

    // Handle workshop.event event (main workshop events)
    eventSource.addEventListener('workshop.event', (e) => {
      const event: WorkshopEvent = JSON.parse(e.data);
      console.log('[Workshop SSE] Event:', event.type, event.builder);
      handlersRef.current.addEvent(event);
    });

    // Handle workshop.phase event (phase transitions)
    eventSource.addEventListener('workshop.phase', (e) => {
      const data = JSON.parse(e.data);
      const newPhase = data.phase as WorkshopPhase;
      console.log('[Workshop SSE] Phase change:', newPhase);
      handlersRef.current.setPhase(newPhase);
    });

    // Handle workshop.idle event (workshop not running)
    eventSource.addEventListener('workshop.idle', () => {
      console.log('[Workshop SSE] Workshop idle');
      handlersRef.current.setRunning(false);
    });

    // Handle workshop.end event
    eventSource.addEventListener('workshop.end', (e) => {
      const data = JSON.parse(e.data);
      console.log('[Workshop SSE] End:', data);
      handlersRef.current.setRunning(false);
      if (data.metrics) {
        handlersRef.current.setMetrics(data.metrics as WorkshopMetrics);
      }
      onDisconnect?.();
    });

    eventSource.onerror = (error) => {
      console.error('[Workshop SSE] Error:', error);
      onError?.(error);

      if (eventSource.readyState === EventSource.CLOSED) {
        console.log('[Workshop SSE] Connection closed');
        handlersRef.current.setRunning(false);
        onDisconnect?.();
      }
    };

    return eventSource;
  }, [speed, onConnect, onDisconnect, onError]);

  const disconnect = useCallback(() => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
      setRunning(false);
      onDisconnect?.();
    }
  }, [setRunning, onDisconnect]);

  // Auto-connect when requested
  useEffect(() => {
    if (autoConnect && isRunning) {
      connect();
    }

    return () => {
      disconnect();
    };
  }, [autoConnect, isRunning, connect, disconnect]);

  return {
    connect,
    disconnect,
    isConnected: !!eventSourceRef.current && eventSourceRef.current.readyState === EventSource.OPEN,
  };
}

/**
 * Hook for reconnecting SSE with exponential backoff.
 */
export function useReconnectingWorkshopStream(options: SSEOptions & { maxRetries?: number }) {
  const { maxRetries = 5, ...sseOptions } = options;
  const retriesRef = useRef(0);
  const { connect, disconnect, isConnected } = useWorkshopStream({
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
        console.log(
          `[Workshop SSE] Reconnecting in ${delay}ms (attempt ${retriesRef.current}/${maxRetries})`
        );
        setTimeout(connect, delay);
      }
    },
  });

  return { connect, disconnect, isConnected };
}
