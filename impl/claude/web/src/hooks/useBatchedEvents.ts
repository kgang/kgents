/**
 * useBatchedEvents: Hook for batching high-frequency events.
 *
 * Reduces render frequency by collecting events and processing them
 * in batches at a configurable interval.
 *
 * @example
 *   const addEvent = useBatchedEvents<TownEvent>(
 *     (events) => {
 *       // Process batch of events
 *       setEvents((prev) => [...events, ...prev]);
 *     },
 *     50 // ms delay
 *   );
 *
 *   // In SSE handler:
 *   es.addEventListener('live.event', (e) => {
 *     addEvent(JSON.parse(e.data));
 *   });
 */

import { useRef, useCallback, useEffect } from 'react';

export function useBatchedEvents<T>(
  onBatch: (events: T[]) => void,
  delay = 50
): (event: T) => void {
  const batchRef = useRef<T[]>([]);
  const timeoutRef = useRef<number | null>(null);
  const onBatchRef = useRef(onBatch);

  // Keep callback ref fresh
  onBatchRef.current = onBatch;

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (timeoutRef.current !== null) {
        window.clearTimeout(timeoutRef.current);
        // Flush remaining events on unmount
        if (batchRef.current.length > 0) {
          onBatchRef.current(batchRef.current);
          batchRef.current = [];
        }
      }
    };
  }, []);

  const addEvent = useCallback((event: T) => {
    batchRef.current.push(event);

    if (timeoutRef.current === null) {
      timeoutRef.current = window.setTimeout(() => {
        const batch = batchRef.current;
        batchRef.current = [];
        timeoutRef.current = null;
        onBatchRef.current(batch);
      }, delay);
    }
  }, [delay]);

  return addEvent;
}

export default useBatchedEvents;
