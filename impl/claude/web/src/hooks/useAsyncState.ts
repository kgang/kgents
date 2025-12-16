/**
 * useAsyncState: Standardized async state management hook.
 *
 * Eliminates boilerplate for loading/error/data patterns across the app.
 * Each page previously implemented its own LoadingState type - this unifies them.
 *
 * @see plans/web-refactor/defensive-lifecycle.md
 */

import { useState, useCallback, useRef } from 'react';

// =============================================================================
// Types
// =============================================================================

export type AsyncStatus = 'idle' | 'loading' | 'success' | 'error';

export interface AsyncState<T> {
  /** The loaded data, null until success */
  data: T | null;
  /** True while loading */
  isLoading: boolean;
  /** Error message if failed */
  error: string | null;
  /** Explicit status for exhaustive checks */
  status: AsyncStatus;
}

export interface UseAsyncStateOptions<T> {
  /** Initial data (sets status to 'success' if provided) */
  initialData?: T;
  /** Callback on successful load */
  onSuccess?: (data: T) => void;
  /** Callback on error */
  onError?: (error: string) => void;
}

export interface UseAsyncStateReturn<T> {
  /** Current async state */
  state: AsyncState<T>;
  /** Execute a promise, managing loading/error/success states */
  execute: (promise: Promise<T>) => Promise<T | null>;
  /** Manually set data (useful for optimistic updates) */
  setData: (data: T) => void;
  /** Manually set error */
  setError: (error: string) => void;
  /** Reset to initial state, abort any pending request */
  reset: () => void;
}

// =============================================================================
// Hook
// =============================================================================

/**
 * Manage async operation state with automatic loading/error handling.
 *
 * @example
 * ```typescript
 * const { state, execute } = useAsyncState<Town>();
 *
 * // Load data
 * useEffect(() => {
 *   execute(townApi.get(townId));
 * }, [townId, execute]);
 *
 * // Render based on state
 * if (state.isLoading) return <Loading />;
 * if (state.error) return <Error message={state.error} />;
 * if (state.data) return <Town data={state.data} />;
 * ```
 */
export function useAsyncState<T>(
  options: UseAsyncStateOptions<T> = {}
): UseAsyncStateReturn<T> {
  const { initialData, onSuccess, onError } = options;

  const [state, setState] = useState<AsyncState<T>>(() => ({
    data: initialData ?? null,
    isLoading: false,
    error: null,
    status: initialData !== undefined ? 'success' : 'idle',
  }));

  // Track current request for cancellation
  const requestIdRef = useRef(0);

  const execute = useCallback(
    async (promise: Promise<T>): Promise<T | null> => {
      // Increment request ID to invalidate previous requests
      const currentRequestId = ++requestIdRef.current;

      setState((s) => ({
        ...s,
        isLoading: true,
        error: null,
        status: 'loading',
      }));

      try {
        const data = await promise;

        // Only update if this is still the current request
        if (currentRequestId !== requestIdRef.current) {
          return null;
        }

        setState({
          data,
          isLoading: false,
          error: null,
          status: 'success',
        });

        onSuccess?.(data);
        return data;
      } catch (err: unknown) {
        // Only update if this is still the current request
        if (currentRequestId !== requestIdRef.current) {
          return null;
        }

        // Extract error message
        let message = 'An error occurred';
        if (err instanceof Error) {
          message = err.message;
        } else if (typeof err === 'object' && err !== null) {
          // Handle axios-style errors
          const axiosErr = err as {
            response?: { data?: { detail?: string }; status?: number };
            message?: string;
          };
          if (axiosErr.response?.data?.detail) {
            message = axiosErr.response.data.detail;
          } else if (axiosErr.response?.status === 404) {
            message = 'Not found';
          } else if (axiosErr.message) {
            message = axiosErr.message;
          }
        }

        setState((s) => ({
          ...s,
          isLoading: false,
          error: message,
          status: 'error',
        }));

        onError?.(message);
        return null;
      }
    },
    [onSuccess, onError]
  );

  const setData = useCallback((data: T) => {
    setState({
      data,
      isLoading: false,
      error: null,
      status: 'success',
    });
  }, []);

  const setError = useCallback((error: string) => {
    setState((s) => ({
      ...s,
      isLoading: false,
      error,
      status: 'error',
    }));
  }, []);

  const reset = useCallback(() => {
    // Invalidate any pending requests
    requestIdRef.current++;

    setState({
      data: initialData ?? null,
      isLoading: false,
      error: null,
      status: initialData !== undefined ? 'success' : 'idle',
    });
  }, [initialData]);

  return { state, execute, setData, setError, reset };
}

export default useAsyncState;
