/**
 * Tests for useHistoricalMode hook.
 *
 * Manages historical replay functionality:
 * - Mode switching (live ↔ historical)
 * - Timeline navigation (seek, step)
 * - Playback controls (play/pause, speed)
 * - Snapshot caching
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { useHistoricalMode } from '@/hooks/useHistoricalMode';

// =============================================================================
// Mock Fetch
// =============================================================================

const mockFetch = vi.fn();

// =============================================================================
// Test Setup
// =============================================================================

describe('useHistoricalMode', () => {
  beforeEach(() => {
    vi.useFakeTimers();
    vi.stubGlobal('fetch', mockFetch);
    mockFetch.mockReset();
  });

  afterEach(() => {
    vi.useRealTimers();
    vi.unstubAllGlobals();
  });

  // ===========================================================================
  // Initialization Tests
  // ===========================================================================

  describe('initialization', () => {
    it('initializes in live mode', () => {
      const { result } = renderHook(() =>
        useHistoricalMode({ townId: 'test-town' })
      );

      expect(result.current.mode).toBe('live');
    });

    it('initializes with currentTick at initialMaxTick', () => {
      const { result } = renderHook(() =>
        useHistoricalMode({ townId: 'test-town', initialMaxTick: 100 })
      );

      expect(result.current.currentTick).toBe(100);
      expect(result.current.maxTick).toBe(100);
    });

    it('initializes with isPlaying=false', () => {
      const { result } = renderHook(() =>
        useHistoricalMode({ townId: 'test-town' })
      );

      expect(result.current.isPlaying).toBe(false);
    });

    it('initializes with playbackSpeed=1', () => {
      const { result } = renderHook(() =>
        useHistoricalMode({ townId: 'test-town' })
      );

      expect(result.current.playbackSpeed).toBe(1);
    });

    it('initializes with isLoading=false', () => {
      const { result } = renderHook(() =>
        useHistoricalMode({ townId: 'test-town' })
      );

      expect(result.current.isLoading).toBe(false);
    });

    it('initializes with error=null', () => {
      const { result } = renderHook(() =>
        useHistoricalMode({ townId: 'test-town' })
      );

      expect(result.current.error).toBeNull();
    });
  });

  // ===========================================================================
  // Mode Management Tests
  // ===========================================================================

  describe('mode management', () => {
    it('enterHistorical switches to historical mode', () => {
      const { result } = renderHook(() =>
        useHistoricalMode({ townId: 'test-town', initialMaxTick: 100 })
      );

      act(() => result.current.enterHistorical());

      expect(result.current.mode).toBe('historical');
    });

    it('enterHistorical sets currentTick to maxTick by default', () => {
      const { result } = renderHook(() =>
        useHistoricalMode({ townId: 'test-town', initialMaxTick: 100 })
      );

      act(() => result.current.enterHistorical());

      expect(result.current.currentTick).toBe(100);
    });

    it('enterHistorical accepts specific tick', () => {
      const { result } = renderHook(() =>
        useHistoricalMode({ townId: 'test-town', initialMaxTick: 100 })
      );

      act(() => result.current.enterHistorical(50));

      expect(result.current.currentTick).toBe(50);
    });

    it('enterHistorical stops playback', () => {
      const { result } = renderHook(() =>
        useHistoricalMode({ townId: 'test-town', initialMaxTick: 100 })
      );

      act(() => result.current.enterHistorical());

      expect(result.current.isPlaying).toBe(false);
    });

    it('returnToLive switches to live mode', () => {
      const { result } = renderHook(() =>
        useHistoricalMode({ townId: 'test-town', initialMaxTick: 100 })
      );

      act(() => result.current.enterHistorical());
      act(() => result.current.returnToLive());

      expect(result.current.mode).toBe('live');
    });

    it('returnToLive sets currentTick to maxTick', () => {
      const { result } = renderHook(() =>
        useHistoricalMode({ townId: 'test-town', initialMaxTick: 100 })
      );

      act(() => result.current.enterHistorical(50));
      act(() => result.current.returnToLive());

      expect(result.current.currentTick).toBe(100);
    });

    it('returnToLive stops playback', () => {
      const { result } = renderHook(() =>
        useHistoricalMode({ townId: 'test-town', initialMaxTick: 100 })
      );

      act(() => {
        result.current.enterHistorical();
        result.current.togglePlay();
      });

      act(() => result.current.returnToLive());

      expect(result.current.isPlaying).toBe(false);
    });

    it('calls onModeChange when entering historical', () => {
      const onModeChange = vi.fn();
      const { result } = renderHook(() =>
        useHistoricalMode({ townId: 'test-town', onModeChange })
      );

      act(() => result.current.enterHistorical());

      expect(onModeChange).toHaveBeenCalledWith('historical');
    });

    it('calls onModeChange when returning to live', () => {
      const onModeChange = vi.fn();
      const { result } = renderHook(() =>
        useHistoricalMode({ townId: 'test-town', onModeChange })
      );

      act(() => result.current.enterHistorical());
      act(() => result.current.returnToLive());

      expect(onModeChange).toHaveBeenCalledWith('live');
    });
  });

  // ===========================================================================
  // Navigation Tests
  // ===========================================================================

  describe('navigation', () => {
    it('seekTo updates currentTick', () => {
      const { result } = renderHook(() =>
        useHistoricalMode({ townId: 'test-town', initialMaxTick: 100 })
      );

      act(() => result.current.seekTo(50));

      expect(result.current.currentTick).toBe(50);
    });

    it('seekTo clamps to 0 for negative values', () => {
      const { result } = renderHook(() =>
        useHistoricalMode({ townId: 'test-town', initialMaxTick: 100 })
      );

      act(() => result.current.seekTo(-10));

      expect(result.current.currentTick).toBe(0);
    });

    it('seekTo clamps to maxTick for values above max', () => {
      const { result } = renderHook(() =>
        useHistoricalMode({ townId: 'test-town', initialMaxTick: 100 })
      );

      act(() => result.current.seekTo(200));

      expect(result.current.currentTick).toBe(100);
    });

    it('seekTo calls onTickChange', () => {
      const onTickChange = vi.fn();
      const { result } = renderHook(() =>
        useHistoricalMode({ townId: 'test-town', initialMaxTick: 100, onTickChange })
      );

      act(() => result.current.seekTo(50));

      expect(onTickChange).toHaveBeenCalledWith(50);
    });

    it('stepForward increments currentTick by 1', () => {
      const { result } = renderHook(() =>
        useHistoricalMode({ townId: 'test-town', initialMaxTick: 100 })
      );

      act(() => result.current.seekTo(50));
      act(() => result.current.stepForward());

      expect(result.current.currentTick).toBe(51);
    });

    it('stepBackward decrements currentTick by 1', () => {
      const { result } = renderHook(() =>
        useHistoricalMode({ townId: 'test-town', initialMaxTick: 100 })
      );

      act(() => result.current.seekTo(50));
      act(() => result.current.stepBackward());

      expect(result.current.currentTick).toBe(49);
    });

    it('stepForward respects maxTick boundary', () => {
      const { result } = renderHook(() =>
        useHistoricalMode({ townId: 'test-town', initialMaxTick: 100 })
      );

      act(() => result.current.seekTo(100));
      act(() => result.current.stepForward());

      expect(result.current.currentTick).toBe(100);
    });

    it('stepBackward respects 0 boundary', () => {
      const { result } = renderHook(() =>
        useHistoricalMode({ townId: 'test-town', initialMaxTick: 100 })
      );

      act(() => result.current.seekTo(0));
      act(() => result.current.stepBackward());

      expect(result.current.currentTick).toBe(0);
    });
  });

  // ===========================================================================
  // Playback Tests
  // ===========================================================================

  describe('playback', () => {
    it('togglePlay starts playback', () => {
      const { result } = renderHook(() =>
        useHistoricalMode({ townId: 'test-town', initialMaxTick: 100 })
      );

      act(() => result.current.togglePlay());

      expect(result.current.isPlaying).toBe(true);
    });

    it('togglePlay stops playback when already playing', () => {
      const { result } = renderHook(() =>
        useHistoricalMode({ townId: 'test-town', initialMaxTick: 100 })
      );

      act(() => result.current.togglePlay());
      act(() => result.current.togglePlay());

      expect(result.current.isPlaying).toBe(false);
    });

    it('setPlaybackSpeed updates playback speed', () => {
      const { result } = renderHook(() =>
        useHistoricalMode({ townId: 'test-town', initialMaxTick: 100 })
      );

      act(() => result.current.setPlaybackSpeed(2));

      expect(result.current.playbackSpeed).toBe(2);
    });

    it('playback advances tick automatically in historical mode', async () => {
      const { result } = renderHook(() =>
        useHistoricalMode({ townId: 'test-town', initialMaxTick: 100 })
      );

      act(() => {
        result.current.enterHistorical(10);
        result.current.togglePlay();
      });

      // Advance time by 1 second (playbackSpeed=1 means 1 tick per second)
      await act(async () => {
        vi.advanceTimersByTime(1000);
      });

      expect(result.current.currentTick).toBe(11);
    });

    it('playback stops at maxTick', async () => {
      const { result } = renderHook(() =>
        useHistoricalMode({ townId: 'test-town', initialMaxTick: 5 })
      );

      act(() => {
        result.current.enterHistorical(3);
        result.current.togglePlay();
      });

      // Advance past max
      await act(async () => {
        vi.advanceTimersByTime(5000);
      });

      expect(result.current.currentTick).toBe(5);
      expect(result.current.isPlaying).toBe(false);
    });

    it('playback respects playback speed', async () => {
      const { result } = renderHook(() =>
        useHistoricalMode({ townId: 'test-town', initialMaxTick: 100 })
      );

      act(() => {
        result.current.enterHistorical(10);
        result.current.setPlaybackSpeed(2);
        result.current.togglePlay();
      });

      // At 2x speed, 1 second should advance 2 ticks
      await act(async () => {
        vi.advanceTimersByTime(500); // Half second at 2x
      });

      expect(result.current.currentTick).toBe(11);
    });
  });

  // ===========================================================================
  // Max Tick Management Tests
  // ===========================================================================

  describe('maxTick management', () => {
    it('updateMaxTick increases maxTick', () => {
      const { result } = renderHook(() =>
        useHistoricalMode({ townId: 'test-town', initialMaxTick: 100 })
      );

      act(() => result.current.updateMaxTick(150));

      expect(result.current.maxTick).toBe(150);
    });

    it('updateMaxTick does not decrease maxTick', () => {
      const { result } = renderHook(() =>
        useHistoricalMode({ townId: 'test-town', initialMaxTick: 100 })
      );

      act(() => result.current.updateMaxTick(50));

      expect(result.current.maxTick).toBe(100);
    });

    it('updateMaxTick updates currentTick in live mode', () => {
      const { result } = renderHook(() =>
        useHistoricalMode({ townId: 'test-town', initialMaxTick: 100 })
      );

      act(() => result.current.updateMaxTick(150));

      expect(result.current.currentTick).toBe(150);
    });

    it('updateMaxTick does not change currentTick in historical mode', () => {
      const { result } = renderHook(() =>
        useHistoricalMode({ townId: 'test-town', initialMaxTick: 100 })
      );

      act(() => result.current.enterHistorical(50));
      act(() => result.current.updateMaxTick(150));

      expect(result.current.currentTick).toBe(50);
      expect(result.current.maxTick).toBe(150);
    });
  });

  // ===========================================================================
  // Snapshot Fetching Tests
  // ===========================================================================

  describe('snapshot fetching', () => {
    it('getSnapshot fetches from API', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ citizens: [], phase: 'MORNING' }),
      });

      const { result } = renderHook(() =>
        useHistoricalMode({ townId: 'test-town' })
      );

      let snapshot;
      await act(async () => {
        snapshot = await result.current.getSnapshot(50);
      });

      expect(mockFetch).toHaveBeenCalledWith('/api/v1/town/test-town/snapshot/50');
      expect(snapshot).toEqual({ citizens: [], phase: 'MORNING' });
    });

    it('getSnapshot returns data on success', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ citizens: [], phase: 'MORNING' }),
      });

      const { result } = renderHook(() =>
        useHistoricalMode({ townId: 'test-town' })
      );

      let snapshot;
      await act(async () => {
        snapshot = await result.current.getSnapshot(50);
      });

      expect(mockFetch).toHaveBeenCalledWith('/api/v1/town/test-town/snapshot/50');
      expect(snapshot).toEqual({ citizens: [], phase: 'MORNING' });
    });

    it('getSnapshot caches results', async () => {
      mockFetch.mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({ citizens: [], phase: 'MORNING' }),
      });

      const { result } = renderHook(() =>
        useHistoricalMode({ townId: 'test-town' })
      );

      await act(async () => {
        await result.current.getSnapshot(50);
        await result.current.getSnapshot(50);
      });

      // Should only fetch once
      expect(mockFetch).toHaveBeenCalledTimes(1);
    });

    it('getSnapshot returns cached value', async () => {
      const snapshot = { citizens: [], phase: 'MORNING' };
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(snapshot),
      });

      const { result } = renderHook(() =>
        useHistoricalMode({ townId: 'test-town' })
      );

      let firstResult, secondResult;
      await act(async () => {
        firstResult = await result.current.getSnapshot(50);
        secondResult = await result.current.getSnapshot(50);
      });

      expect(firstResult).toEqual(snapshot);
      expect(secondResult).toEqual(snapshot);
    });

    it('getSnapshot sets error on fetch failure', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 404,
      });

      const { result } = renderHook(() =>
        useHistoricalMode({ townId: 'test-town' })
      );

      await act(async () => {
        await result.current.getSnapshot(50);
      });

      expect(result.current.error).toBe('Failed to fetch snapshot: 404');
    });

    it('getSnapshot returns null on error', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
      });

      const { result } = renderHook(() =>
        useHistoricalMode({ townId: 'test-town' })
      );

      let snapshot;
      await act(async () => {
        snapshot = await result.current.getSnapshot(50);
      });

      expect(snapshot).toBeNull();
    });
  });
});
