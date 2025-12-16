/**
 * Tests for useOnlineStatus hook.
 *
 * @see src/hooks/useOnlineStatus.ts
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { useOnlineStatus } from '@/hooks/useOnlineStatus';
import { useUIStore } from '@/stores/uiStore';

describe('useOnlineStatus', () => {
  // Store original navigator.onLine
  const originalOnLine = navigator.onLine;
  let addEventListenerSpy: ReturnType<typeof vi.spyOn>;
  let removeEventListenerSpy: ReturnType<typeof vi.spyOn>;

  beforeEach(() => {
    // Reset store
    useUIStore.setState({ notifications: [] });

    // Spy on event listeners
    addEventListenerSpy = vi.spyOn(window, 'addEventListener');
    removeEventListenerSpy = vi.spyOn(window, 'removeEventListener');
  });

  afterEach(() => {
    // Restore
    Object.defineProperty(navigator, 'onLine', {
      value: originalOnLine,
      writable: true,
      configurable: true,
    });
    vi.restoreAllMocks();
  });

  describe('initial state', () => {
    it('should return true when browser is online', () => {
      Object.defineProperty(navigator, 'onLine', {
        value: true,
        writable: true,
        configurable: true,
      });

      const { result } = renderHook(() => useOnlineStatus());
      expect(result.current).toBe(true);
    });

    it('should return false when browser is offline', () => {
      Object.defineProperty(navigator, 'onLine', {
        value: false,
        writable: true,
        configurable: true,
      });

      const { result } = renderHook(() => useOnlineStatus());
      expect(result.current).toBe(false);
    });
  });

  describe('event listeners', () => {
    it('should add online and offline event listeners', () => {
      renderHook(() => useOnlineStatus());

      expect(addEventListenerSpy).toHaveBeenCalledWith(
        'online',
        expect.any(Function)
      );
      expect(addEventListenerSpy).toHaveBeenCalledWith(
        'offline',
        expect.any(Function)
      );
    });

    it('should remove event listeners on unmount', () => {
      const { unmount } = renderHook(() => useOnlineStatus());

      unmount();

      expect(removeEventListenerSpy).toHaveBeenCalledWith(
        'online',
        expect.any(Function)
      );
      expect(removeEventListenerSpy).toHaveBeenCalledWith(
        'offline',
        expect.any(Function)
      );
    });
  });

  describe('online event', () => {
    it('should update to true when online event fires', () => {
      Object.defineProperty(navigator, 'onLine', {
        value: false,
        writable: true,
        configurable: true,
      });

      const { result } = renderHook(() => useOnlineStatus());
      expect(result.current).toBe(false);

      // Simulate coming online
      act(() => {
        window.dispatchEvent(new Event('online'));
      });

      expect(result.current).toBe(true);
    });

    it('should show success notification when coming online', () => {
      Object.defineProperty(navigator, 'onLine', {
        value: false,
        writable: true,
        configurable: true,
      });

      renderHook(() => useOnlineStatus());

      act(() => {
        window.dispatchEvent(new Event('online'));
      });

      const notifications = useUIStore.getState().notifications;
      expect(notifications).toHaveLength(1);
      expect(notifications[0].type).toBe('info');
      expect(notifications[0].title).toBe('Back Online');
    });
  });

  describe('offline event', () => {
    it('should update to false when offline event fires', () => {
      Object.defineProperty(navigator, 'onLine', {
        value: true,
        writable: true,
        configurable: true,
      });

      const { result } = renderHook(() => useOnlineStatus());
      expect(result.current).toBe(true);

      // Simulate going offline
      act(() => {
        window.dispatchEvent(new Event('offline'));
      });

      expect(result.current).toBe(false);
    });

    it('should show error notification when going offline', () => {
      Object.defineProperty(navigator, 'onLine', {
        value: true,
        writable: true,
        configurable: true,
      });

      renderHook(() => useOnlineStatus());

      act(() => {
        window.dispatchEvent(new Event('offline'));
      });

      const notifications = useUIStore.getState().notifications;
      expect(notifications).toHaveLength(1);
      expect(notifications[0].type).toBe('error');
      expect(notifications[0].title).toBe('Offline');
    });
  });
});
