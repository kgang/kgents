/**
 * useAgentesePath - Hook for AGENTESE path invocation
 *
 * Invokes AGENTESE paths via the gateway and returns typed responses.
 * The URL IS the API call.
 *
 * @see spec/protocols/agentese-as-route.md
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import { apiClient } from '@/api/client';

/**
 * Response envelope from AGENTESE gateway
 */
interface AgenteseResponse<T = unknown> {
  path: string;
  aspect: string;
  responseType: string;
  result: T;
}

/**
 * Options for useAgentese hook
 */
interface UseAgenteseOptions {
  /** Aspect to invoke (default: "manifest") */
  aspect?: string;
  /** Query parameters */
  params?: Record<string, string>;
  /** Whether to skip the initial fetch */
  skip?: boolean;
  /** Polling interval in ms (0 = no polling) */
  pollInterval?: number;
  /** Cache key override */
  cacheKey?: string;
}

/**
 * Return value from useAgentese hook
 */
interface UseAgenteseResult<T> {
  /** Response data */
  data: T | null;
  /** Response type name (from contracts) */
  responseType: string | null;
  /** Loading state */
  isLoading: boolean;
  /** Error state */
  error: Error | null;
  /** Refetch function */
  refetch: () => Promise<void>;
  /** Full path that was invoked */
  path: string;
  /** Aspect that was invoked */
  aspect: string;
}

/**
 * Simple in-memory cache for AGENTESE responses
 */
const responseCache = new Map<string, { data: unknown; responseType: string; timestamp: number }>();
const CACHE_TTL_MS = 30000; // 30 seconds

function getCacheKey(path: string, aspect: string, params?: Record<string, string>): string {
  const paramStr = params ? JSON.stringify(params) : '';
  return `${path}:${aspect}:${paramStr}`;
}

/**
 * Hook to invoke an AGENTESE path and get typed responses
 *
 * @param path - AGENTESE path (e.g., "world.town.citizen.kent_001")
 * @param options - Invocation options
 * @returns Data, loading state, and error
 *
 * @example
 * // Basic usage
 * const { data, isLoading } = useAgentese('world.town.citizen.kent_001');
 *
 * // With aspect
 * const { data } = useAgentese('world.town.citizen.kent_001', { aspect: 'polynomial' });
 *
 * // With params
 * const { data } = useAgentese('time.differance.recent', { params: { limit: '20' } });
 */
export function useAgentese<T = unknown>(
  path: string,
  options: UseAgenteseOptions = {}
): UseAgenteseResult<T> {
  const { aspect = 'manifest', params, skip = false, pollInterval = 0 } = options;

  const [data, setData] = useState<T | null>(null);
  const [responseType, setResponseType] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(!skip);
  const [error, setError] = useState<Error | null>(null);

  const mountedRef = useRef(true);
  const pollTimeoutRef = useRef<ReturnType<typeof setTimeout>>();

  const cacheKey = getCacheKey(path, aspect, params);

  const fetchData = useCallback(async () => {
    if (!path || skip) return;

    // Check cache first
    const cached = responseCache.get(cacheKey);
    if (cached && Date.now() - cached.timestamp < CACHE_TTL_MS) {
      setData(cached.data as T);
      setResponseType(cached.responseType);
      setIsLoading(false);
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      // Build URL: /agentese/{path}/manifest or /agentese/{path}/{aspect}
      const pathSegments = path.replace(/\./g, '/');
      let url = `/agentese/${pathSegments}/${aspect}`;

      // Add query params
      if (params && Object.keys(params).length > 0) {
        url += '?' + new URLSearchParams(params).toString();
      }

      const response = await apiClient.get<AgenteseResponse<T>>(url);

      if (!mountedRef.current) return;

      const result = response.data.result;
      const respType = response.data.responseType;

      // Update cache
      responseCache.set(cacheKey, {
        data: result,
        responseType: respType,
        timestamp: Date.now(),
      });

      setData(result);
      setResponseType(respType);
      setError(null);
    } catch (e) {
      if (!mountedRef.current) return;
      setError(e instanceof Error ? e : new Error(String(e)));
    } finally {
      if (mountedRef.current) {
        setIsLoading(false);
      }
    }
  }, [path, aspect, params, skip, cacheKey]);

  // Initial fetch
  useEffect(() => {
    mountedRef.current = true;
    fetchData();

    return () => {
      mountedRef.current = false;
    };
  }, [fetchData]);

  // Polling
  useEffect(() => {
    if (pollInterval > 0 && !skip) {
      pollTimeoutRef.current = setInterval(fetchData, pollInterval);
    }

    return () => {
      if (pollTimeoutRef.current) {
        clearInterval(pollTimeoutRef.current);
      }
    };
  }, [pollInterval, skip, fetchData]);

  return {
    data,
    responseType,
    isLoading,
    error,
    refetch: fetchData,
    path,
    aspect,
  };
}

/**
 * Hook for AGENTESE mutations (POST/PUT/DELETE)
 */
interface UseAgenteseMutationOptions {
  /** Callback on success */
  onSuccess?: (data: unknown) => void;
  /** Callback on error */
  onError?: (error: Error) => void;
}

interface UseAgenteseMutationResult<TRequest, TResponse> {
  /** Execute the mutation */
  mutate: (data?: TRequest) => Promise<TResponse | null>;
  /** Mutation in progress */
  isLoading: boolean;
  /** Mutation error */
  error: Error | null;
  /** Last response */
  data: TResponse | null;
}

/**
 * Hook to invoke AGENTESE mutations (write operations)
 *
 * @param path - AGENTESE path with aspect (e.g., "world.town.citizen.kent_001:dialogue")
 * @param options - Mutation options
 *
 * @example
 * const { mutate, isLoading } = useAgenteseMutation('self.memory:capture');
 * await mutate({ content: 'Remember this', tags: ['work'] });
 */
export function useAgenteseMutation<TRequest = unknown, TResponse = unknown>(
  pathWithAspect: string,
  options: UseAgenteseMutationOptions = {}
): UseAgenteseMutationResult<TRequest, TResponse> {
  const { onSuccess, onError } = options;

  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  const [data, setData] = useState<TResponse | null>(null);

  const mutate = useCallback(
    async (requestData?: TRequest): Promise<TResponse | null> => {
      setIsLoading(true);
      setError(null);

      try {
        // Parse path:aspect
        const [path, aspect = 'manifest'] = pathWithAspect.split(':');
        const pathSegments = path.replace(/\./g, '/');
        const url = `/agentese/${pathSegments}/${aspect}`;

        const response = await apiClient.post<AgenteseResponse<TResponse>>(url, requestData);

        const result = response.data.result;
        setData(result);
        onSuccess?.(result);

        // Invalidate related cache entries
        for (const key of responseCache.keys()) {
          if (key.startsWith(path)) {
            responseCache.delete(key);
          }
        }

        return result;
      } catch (e) {
        const err = e instanceof Error ? e : new Error(String(e));
        setError(err);
        onError?.(err);
        return null;
      } finally {
        setIsLoading(false);
      }
    },
    [pathWithAspect, onSuccess, onError]
  );

  return { mutate, isLoading, error, data };
}

/**
 * Hook for AGENTESE SSE streams
 */
interface UseAgenteseStreamResult<T> {
  /** Stream events */
  events: T[];
  /** Connection status */
  isConnected: boolean;
  /** Stream error */
  error: Error | null;
  /** Close the stream */
  close: () => void;
}

/**
 * Hook to subscribe to AGENTESE streaming aspects
 *
 * @param pathWithAspect - Path with :stream aspect (e.g., "world.town.simulation.sim_001:stream")
 *
 * @example
 * const { events, isConnected } = useAgenteseStream('world.town.simulation.sim_001:stream');
 */
export function useAgenteseStream<T = unknown>(pathWithAspect: string): UseAgenteseStreamResult<T> {
  const [events, setEvents] = useState<T[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const eventSourceRef = useRef<EventSource | null>(null);

  const close = useCallback(() => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
      setIsConnected(false);
    }
  }, []);

  useEffect(() => {
    // Parse path:aspect
    const [path, aspect = 'stream'] = pathWithAspect.split(':');
    const pathSegments = path.replace(/\./g, '/');
    const url = `/agentese/${pathSegments}/${aspect}/stream`;

    const eventSource = new EventSource(url);
    eventSourceRef.current = eventSource;

    eventSource.onopen = () => {
      setIsConnected(true);
      setError(null);
    };

    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data) as T;
        setEvents((prev) => [...prev, data]);
      } catch (e) {
        console.error('Failed to parse SSE event:', e);
      }
    };

    eventSource.onerror = () => {
      setError(new Error('Stream connection failed'));
      setIsConnected(false);
    };

    return () => {
      eventSource.close();
    };
  }, [pathWithAspect]);

  return { events, isConnected, error, close };
}

/**
 * Clear the AGENTESE response cache
 */
export function clearAgenteseCache(pathPrefix?: string): void {
  if (pathPrefix) {
    for (const key of responseCache.keys()) {
      if (key.startsWith(pathPrefix)) {
        responseCache.delete(key);
      }
    }
  } else {
    responseCache.clear();
  }
}

export default useAgentese;
