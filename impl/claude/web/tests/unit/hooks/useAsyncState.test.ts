/**
 * Tests for useAsyncState hook.
 *
 * @see src/hooks/useAsyncState.ts
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { useAsyncState } from '@/hooks/useAsyncState';

describe('useAsyncState', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('initial state', () => {
    it('should start with idle status when no initial data', () => {
      const { result } = renderHook(() => useAsyncState<string>());

      expect(result.current.state).toEqual({
        data: null,
        isLoading: false,
        error: null,
        status: 'idle',
      });
    });

    it('should start with success status when initial data provided', () => {
      const { result } = renderHook(() =>
        useAsyncState<string>({ initialData: 'hello' })
      );

      expect(result.current.state).toEqual({
        data: 'hello',
        isLoading: false,
        error: null,
        status: 'success',
      });
    });
  });

  describe('execute', () => {
    it('should set loading state during execution', async () => {
      const { result } = renderHook(() => useAsyncState<string>());

      // Start a slow promise
      let resolvePromise: (value: string) => void;
      const slowPromise = new Promise<string>((resolve) => {
        resolvePromise = resolve;
      });

      act(() => {
        result.current.execute(slowPromise);
      });

      // Should be loading
      expect(result.current.state.isLoading).toBe(true);
      expect(result.current.state.status).toBe('loading');

      // Resolve and verify success
      await act(async () => {
        resolvePromise!('done');
        await slowPromise;
      });

      expect(result.current.state.isLoading).toBe(false);
      expect(result.current.state.status).toBe('success');
      expect(result.current.state.data).toBe('done');
    });

    it('should set data on success', async () => {
      const { result } = renderHook(() => useAsyncState<{ name: string }>());

      await act(async () => {
        await result.current.execute(Promise.resolve({ name: 'test' }));
      });

      expect(result.current.state).toEqual({
        data: { name: 'test' },
        isLoading: false,
        error: null,
        status: 'success',
      });
    });

    it('should set error on failure with Error object', async () => {
      const { result } = renderHook(() => useAsyncState<string>());

      await act(async () => {
        await result.current.execute(Promise.reject(new Error('Failed!')));
      });

      expect(result.current.state).toEqual({
        data: null,
        isLoading: false,
        error: 'Failed!',
        status: 'error',
      });
    });

    it('should handle axios-style errors', async () => {
      const { result } = renderHook(() => useAsyncState<string>());

      const axiosError = {
        response: {
          data: { detail: 'Town not found' },
          status: 404,
        },
      };

      await act(async () => {
        await result.current.execute(Promise.reject(axiosError));
      });

      expect(result.current.state.error).toBe('Town not found');
    });

    it('should handle 404 status without detail', async () => {
      const { result } = renderHook(() => useAsyncState<string>());

      const axiosError = {
        response: {
          status: 404,
        },
      };

      await act(async () => {
        await result.current.execute(Promise.reject(axiosError));
      });

      expect(result.current.state.error).toBe('Not found');
    });

    it('should call onSuccess callback', async () => {
      const onSuccess = vi.fn();
      const { result } = renderHook(() =>
        useAsyncState<string>({ onSuccess })
      );

      await act(async () => {
        await result.current.execute(Promise.resolve('data'));
      });

      expect(onSuccess).toHaveBeenCalledWith('data');
    });

    it('should call onError callback', async () => {
      const onError = vi.fn();
      const { result } = renderHook(() => useAsyncState<string>({ onError }));

      await act(async () => {
        await result.current.execute(Promise.reject(new Error('oops')));
      });

      expect(onError).toHaveBeenCalledWith('oops');
    });

    it('should return data on success', async () => {
      const { result } = renderHook(() => useAsyncState<string>());

      let returnValue: string | null = null;
      await act(async () => {
        returnValue = await result.current.execute(Promise.resolve('result'));
      });

      expect(returnValue).toBe('result');
    });

    it('should return null on error', async () => {
      const { result } = renderHook(() => useAsyncState<string>());

      let returnValue: string | null = 'not null';
      await act(async () => {
        returnValue = await result.current.execute(
          Promise.reject(new Error('fail'))
        );
      });

      expect(returnValue).toBeNull();
    });
  });

  describe('request cancellation', () => {
    it('should ignore stale requests', async () => {
      const { result } = renderHook(() => useAsyncState<string>());

      let resolve1: (value: string) => void;
      let resolve2: (value: string) => void;
      const promise1 = new Promise<string>((r) => {
        resolve1 = r;
      });
      const promise2 = new Promise<string>((r) => {
        resolve2 = r;
      });

      // Start first request
      act(() => {
        result.current.execute(promise1);
      });

      // Start second request (should invalidate first)
      act(() => {
        result.current.execute(promise2);
      });

      // Resolve first request (should be ignored)
      await act(async () => {
        resolve1!('first');
        await promise1;
      });

      // Should still be loading (waiting for second)
      expect(result.current.state.isLoading).toBe(true);

      // Resolve second request
      await act(async () => {
        resolve2!('second');
        await promise2;
      });

      // Should have second result
      expect(result.current.state.data).toBe('second');
    });
  });

  describe('setData', () => {
    it('should manually set data and success status', () => {
      const { result } = renderHook(() => useAsyncState<string>());

      act(() => {
        result.current.setData('manual');
      });

      expect(result.current.state).toEqual({
        data: 'manual',
        isLoading: false,
        error: null,
        status: 'success',
      });
    });

    it('should clear previous error', () => {
      const { result } = renderHook(() => useAsyncState<string>());

      // Set an error first
      act(() => {
        result.current.setError('oops');
      });

      // Now set data
      act(() => {
        result.current.setData('fixed');
      });

      expect(result.current.state.error).toBeNull();
      expect(result.current.state.data).toBe('fixed');
    });
  });

  describe('setError', () => {
    it('should manually set error', () => {
      const { result } = renderHook(() => useAsyncState<string>());

      act(() => {
        result.current.setError('Something broke');
      });

      expect(result.current.state.error).toBe('Something broke');
      expect(result.current.state.status).toBe('error');
    });

    it('should preserve existing data', () => {
      const { result } = renderHook(() =>
        useAsyncState<string>({ initialData: 'keep me' })
      );

      act(() => {
        result.current.setError('partial failure');
      });

      expect(result.current.state.data).toBe('keep me');
      expect(result.current.state.error).toBe('partial failure');
    });
  });

  describe('reset', () => {
    it('should reset to initial state without initialData', () => {
      const { result } = renderHook(() => useAsyncState<string>());

      // Load some data
      act(() => {
        result.current.setData('loaded');
      });

      // Reset
      act(() => {
        result.current.reset();
      });

      expect(result.current.state).toEqual({
        data: null,
        isLoading: false,
        error: null,
        status: 'idle',
      });
    });

    it('should reset to initialData if provided', () => {
      const { result } = renderHook(() =>
        useAsyncState<string>({ initialData: 'default' })
      );

      // Change data
      act(() => {
        result.current.setData('changed');
      });

      // Reset
      act(() => {
        result.current.reset();
      });

      expect(result.current.state.data).toBe('default');
      expect(result.current.state.status).toBe('success');
    });

    it('should invalidate pending requests', async () => {
      const { result } = renderHook(() => useAsyncState<string>());

      let resolvePromise: (value: string) => void;
      const slowPromise = new Promise<string>((resolve) => {
        resolvePromise = resolve;
      });

      // Start request
      act(() => {
        result.current.execute(slowPromise);
      });

      // Reset while loading
      act(() => {
        result.current.reset();
      });

      // Resolve the promise
      await act(async () => {
        resolvePromise!('too late');
        await slowPromise;
      });

      // Should still be in idle state (request was invalidated)
      expect(result.current.state.status).toBe('idle');
      expect(result.current.state.data).toBeNull();
    });
  });
});
