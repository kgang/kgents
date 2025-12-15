import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import {
  useInhabitSession,
  type InhabitStatus,
  type InhabitResponse,
} from '@/hooks/useInhabitSession';

// Mock the API client
vi.mock('@/api/client', () => ({
  inhabitApi: {
    start: vi.fn(),
    getStatus: vi.fn(),
    suggest: vi.fn(),
    force: vi.fn(),
    apologize: vi.fn(),
    end: vi.fn(),
  },
}));

import { inhabitApi } from '@/api/client';

// Helper to create mock status
const createMockStatus = (overrides: Partial<InhabitStatus> = {}): InhabitStatus => ({
  citizen: 'Alice',
  tier: 'CITIZEN',
  duration: 300,
  time_remaining: 280,
  consent: {
    debt: 0.2,
    status: 'granted',
    at_rupture: false,
    can_force: true,
    cooldown: 0,
  },
  force: {
    enabled: true,
    used: 0,
    remaining: 3,
    limit: 3,
  },
  expired: false,
  actions_count: 1,
  ...overrides,
});

// Helper to create mock response
const createMockResponse = (overrides: Partial<InhabitResponse> = {}): InhabitResponse => ({
  type: 'enact',
  message: 'Alice nods in agreement',
  inner_voice: 'This feels right',
  cost: 10,
  alignment_score: 0.8,
  status: createMockStatus(),
  success: true,
  ...overrides,
});

describe('useInhabitSession', () => {
  const defaultOptions = {
    townId: 'test-town',
    citizenName: 'Alice',
    forceEnabled: false,
    onSessionEnd: vi.fn(),
    onRupture: vi.fn(),
  };

  beforeEach(() => {
    vi.clearAllMocks();
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  describe('initial state', () => {
    it('should initialize with null status', () => {
      const { result } = renderHook(() => useInhabitSession(defaultOptions));

      expect(result.current.status).toBeNull();
      expect(result.current.isLoading).toBe(false);
      expect(result.current.error).toBeNull();
      expect(result.current.lastResponse).toBeNull();
      expect(result.current.history).toEqual([]);
    });

    it('should have computed values default to zero/false', () => {
      const { result } = renderHook(() => useInhabitSession(defaultOptions));

      expect(result.current.timeRemaining).toBe(0);
      expect(result.current.consentDebt).toBe(0);
      expect(result.current.canForce).toBe(false);
      expect(result.current.isRuptured).toBe(false);
      expect(result.current.isExpired).toBe(false);
    });
  });

  describe('start session', () => {
    it('should start a session successfully', async () => {
      const mockStatus = createMockStatus();
      vi.mocked(inhabitApi.start).mockResolvedValueOnce({ data: mockStatus } as any);

      const { result } = renderHook(() => useInhabitSession(defaultOptions));

      await act(async () => {
        await result.current.start();
      });

      expect(inhabitApi.start).toHaveBeenCalledWith('test-town', 'Alice', false);
      expect(result.current.status).toEqual(mockStatus);
      expect(result.current.isLoading).toBe(false);
    });

    it('should start session with force enabled', async () => {
      const mockStatus = createMockStatus();
      vi.mocked(inhabitApi.start).mockResolvedValueOnce({ data: mockStatus } as any);

      const { result } = renderHook(() =>
        useInhabitSession({ ...defaultOptions, forceEnabled: true })
      );

      await act(async () => {
        await result.current.start();
      });

      expect(inhabitApi.start).toHaveBeenCalledWith('test-town', 'Alice', true);
    });

    it('should handle start error', async () => {
      const errorMessage = 'Citizen is busy';
      vi.mocked(inhabitApi.start).mockRejectedValueOnce({
        response: { data: { detail: errorMessage } },
      });

      const { result } = renderHook(() => useInhabitSession(defaultOptions));

      await act(async () => {
        try {
          await result.current.start();
        } catch {
          // Expected to throw
        }
      });

      expect(result.current.error).toBe(errorMessage);
      expect(result.current.status).toBeNull();
    });

    it('should handle start error without detail', async () => {
      vi.mocked(inhabitApi.start).mockRejectedValueOnce(new Error('Network error'));

      const { result } = renderHook(() => useInhabitSession(defaultOptions));

      await act(async () => {
        try {
          await result.current.start();
        } catch {
          // Expected to throw
        }
      });

      expect(result.current.error).toBe('Failed to start INHABIT session');
    });

    it('should set loading during start', async () => {
      let resolvePromise: (value: any) => void;
      const promise = new Promise((resolve) => {
        resolvePromise = resolve;
      });
      vi.mocked(inhabitApi.start).mockReturnValueOnce(promise as any);

      const { result } = renderHook(() => useInhabitSession(defaultOptions));

      act(() => {
        result.current.start();
      });

      expect(result.current.isLoading).toBe(true);

      await act(async () => {
        resolvePromise!({ data: createMockStatus() });
        await promise;
      });

      expect(result.current.isLoading).toBe(false);
    });
  });

  describe('submitAction', () => {
    it('should submit action successfully', async () => {
      const mockStatus = createMockStatus();
      const mockResponse = createMockResponse();

      vi.mocked(inhabitApi.start).mockResolvedValueOnce({ data: mockStatus } as any);
      vi.mocked(inhabitApi.suggest).mockResolvedValueOnce({ data: mockResponse } as any);

      const { result } = renderHook(() => useInhabitSession(defaultOptions));

      await act(async () => {
        await result.current.start();
      });

      let response: InhabitResponse | null = null;
      await act(async () => {
        response = await result.current.submitAction('greet Bob');
      });

      expect(inhabitApi.suggest).toHaveBeenCalledWith('test-town', 'Alice', 'greet Bob');
      expect(response).toEqual(mockResponse);
      expect(result.current.lastResponse).toEqual(mockResponse);
      expect(result.current.history).toHaveLength(1);
    });

    it('should return null without active session', async () => {
      const { result } = renderHook(() => useInhabitSession(defaultOptions));

      let response: InhabitResponse | null = null;
      await act(async () => {
        response = await result.current.submitAction('greet Bob');
      });

      expect(response).toBeNull();
      expect(result.current.error).toBe('No active session');
    });

    it('should trigger onRupture callback when at rupture', async () => {
      const mockStatus = createMockStatus();
      const rupturedResponse = createMockResponse({
        type: 'resist',
        status: createMockStatus({
          consent: {
            debt: 1.0,
            status: 'ruptured',
            at_rupture: true,
            can_force: false,
            cooldown: 60,
          },
        }),
      });

      vi.mocked(inhabitApi.start).mockResolvedValueOnce({ data: mockStatus } as any);
      vi.mocked(inhabitApi.suggest).mockResolvedValueOnce({ data: rupturedResponse } as any);

      const onRupture = vi.fn();
      const { result } = renderHook(() => useInhabitSession({ ...defaultOptions, onRupture }));

      await act(async () => {
        await result.current.start();
      });

      await act(async () => {
        await result.current.submitAction('something rude');
      });

      expect(onRupture).toHaveBeenCalled();
      expect(result.current.isRuptured).toBe(true);
    });

    it('should trigger onSessionEnd when type is exit', async () => {
      const mockStatus = createMockStatus();
      const exitResponse = createMockResponse({ type: 'exit' });

      vi.mocked(inhabitApi.start).mockResolvedValueOnce({ data: mockStatus } as any);
      vi.mocked(inhabitApi.suggest).mockResolvedValueOnce({ data: exitResponse } as any);

      const onSessionEnd = vi.fn();
      const { result } = renderHook(() => useInhabitSession({ ...defaultOptions, onSessionEnd }));

      await act(async () => {
        await result.current.start();
      });

      await act(async () => {
        await result.current.submitAction('goodbye');
      });

      expect(onSessionEnd).toHaveBeenCalled();
    });

    it('should handle submit error', async () => {
      const mockStatus = createMockStatus();
      vi.mocked(inhabitApi.start).mockResolvedValueOnce({ data: mockStatus } as any);
      vi.mocked(inhabitApi.suggest).mockRejectedValueOnce({
        response: { data: { detail: 'Action rejected' } },
      });

      const { result } = renderHook(() => useInhabitSession(defaultOptions));

      await act(async () => {
        await result.current.start();
      });

      let response: InhabitResponse | null = null;
      await act(async () => {
        response = await result.current.submitAction('bad action');
      });

      expect(response).toBeNull();
      expect(result.current.error).toBe('Action rejected');
    });
  });

  describe('forceAction', () => {
    it('should force action successfully', async () => {
      const mockStatus = createMockStatus();
      const mockResponse = createMockResponse({
        type: 'enact',
        message: 'Alice reluctantly agrees',
        status: createMockStatus({
          force: { enabled: true, used: 1, remaining: 2, limit: 3 },
          consent: {
            debt: 0.5,
            status: 'strained',
            at_rupture: false,
            can_force: true,
            cooldown: 0,
          },
        }),
      });

      vi.mocked(inhabitApi.start).mockResolvedValueOnce({ data: mockStatus } as any);
      vi.mocked(inhabitApi.force).mockResolvedValueOnce({ data: mockResponse } as any);

      const { result } = renderHook(() => useInhabitSession(defaultOptions));

      await act(async () => {
        await result.current.start();
      });

      let response: InhabitResponse | null = null;
      await act(async () => {
        response = await result.current.forceAction('do this now', 0.3);
      });

      expect(inhabitApi.force).toHaveBeenCalledWith('test-town', 'Alice', 'do this now', 0.3);
      expect(response).toEqual(mockResponse);
    });

    it('should use default severity', async () => {
      const mockStatus = createMockStatus();
      const mockResponse = createMockResponse();

      vi.mocked(inhabitApi.start).mockResolvedValueOnce({ data: mockStatus } as any);
      vi.mocked(inhabitApi.force).mockResolvedValueOnce({ data: mockResponse } as any);

      const { result } = renderHook(() => useInhabitSession(defaultOptions));

      await act(async () => {
        await result.current.start();
      });

      await act(async () => {
        await result.current.forceAction('do this');
      });

      expect(inhabitApi.force).toHaveBeenCalledWith('test-town', 'Alice', 'do this', 0.2);
    });

    it('should return null without active session', async () => {
      const { result } = renderHook(() => useInhabitSession(defaultOptions));

      let response: InhabitResponse | null;
      await act(async () => {
        response = await result.current.forceAction('action');
      });

      expect(response!).toBeNull();
      expect(result.current.error).toBe('No active session');
    });

    it('should trigger onRupture when forcing causes rupture', async () => {
      const mockStatus = createMockStatus();
      const rupturedResponse = createMockResponse({
        status: createMockStatus({
          consent: {
            debt: 1.0,
            status: 'ruptured',
            at_rupture: true,
            can_force: false,
            cooldown: 120,
          },
        }),
      });

      vi.mocked(inhabitApi.start).mockResolvedValueOnce({ data: mockStatus } as any);
      vi.mocked(inhabitApi.force).mockResolvedValueOnce({ data: rupturedResponse } as any);

      const onRupture = vi.fn();
      const { result } = renderHook(() => useInhabitSession({ ...defaultOptions, onRupture }));

      await act(async () => {
        await result.current.start();
      });

      await act(async () => {
        await result.current.forceAction('aggressive action', 0.8);
      });

      expect(onRupture).toHaveBeenCalled();
    });
  });

  describe('apologize', () => {
    it('should apologize successfully', async () => {
      const mockStatus = createMockStatus({
        consent: {
          debt: 0.6,
          status: 'strained',
          at_rupture: false,
          can_force: false,
          cooldown: 0,
        },
      });
      const mockResponse = createMockResponse({
        type: 'negotiate',
        message: 'Alice accepts your apology',
        status: createMockStatus({
          consent: {
            debt: 0.3,
            status: 'recovering',
            at_rupture: false,
            can_force: true,
            cooldown: 0,
          },
        }),
      });

      vi.mocked(inhabitApi.start).mockResolvedValueOnce({ data: mockStatus } as any);
      vi.mocked(inhabitApi.apologize).mockResolvedValueOnce({ data: mockResponse } as any);

      const { result } = renderHook(() => useInhabitSession(defaultOptions));

      await act(async () => {
        await result.current.start();
      });

      let response: InhabitResponse | null = null;
      await act(async () => {
        response = await result.current.apologize(0.5);
      });

      expect(inhabitApi.apologize).toHaveBeenCalledWith('test-town', 'Alice', 0.5);
      expect(response).toEqual(mockResponse);
      expect(result.current.consentDebt).toBe(0.3);
    });

    it('should use default sincerity', async () => {
      const mockStatus = createMockStatus();
      const mockResponse = createMockResponse();

      vi.mocked(inhabitApi.start).mockResolvedValueOnce({ data: mockStatus } as any);
      vi.mocked(inhabitApi.apologize).mockResolvedValueOnce({ data: mockResponse } as any);

      const { result } = renderHook(() => useInhabitSession(defaultOptions));

      await act(async () => {
        await result.current.start();
      });

      await act(async () => {
        await result.current.apologize();
      });

      expect(inhabitApi.apologize).toHaveBeenCalledWith('test-town', 'Alice', 0.3);
    });

    it('should return null without active session', async () => {
      const { result } = renderHook(() => useInhabitSession(defaultOptions));

      let response: InhabitResponse | null;
      await act(async () => {
        response = await result.current.apologize();
      });

      expect(response!).toBeNull();
      expect(result.current.error).toBe('No active session');
    });
  });

  describe('end session', () => {
    it('should end session successfully', async () => {
      const mockStatus = createMockStatus();

      vi.mocked(inhabitApi.start).mockResolvedValueOnce({ data: mockStatus } as any);
      vi.mocked(inhabitApi.end).mockResolvedValueOnce({} as any);

      const onSessionEnd = vi.fn();
      const { result } = renderHook(() => useInhabitSession({ ...defaultOptions, onSessionEnd }));

      await act(async () => {
        await result.current.start();
      });

      expect(result.current.status).not.toBeNull();

      await act(async () => {
        await result.current.end();
      });

      expect(inhabitApi.end).toHaveBeenCalledWith('test-town', 'Alice');
      expect(result.current.status).toBeNull();
      expect(onSessionEnd).toHaveBeenCalled();
    });

    it('should do nothing without active session', async () => {
      const { result } = renderHook(() => useInhabitSession(defaultOptions));

      await act(async () => {
        await result.current.end();
      });

      expect(inhabitApi.end).not.toHaveBeenCalled();
    });

    it('should handle end error gracefully', async () => {
      const mockStatus = createMockStatus();

      vi.mocked(inhabitApi.start).mockResolvedValueOnce({ data: mockStatus } as any);
      vi.mocked(inhabitApi.end).mockRejectedValueOnce(new Error('Session already ended'));

      const onSessionEnd = vi.fn();
      const { result } = renderHook(() => useInhabitSession({ ...defaultOptions, onSessionEnd }));

      await act(async () => {
        await result.current.start();
      });

      await act(async () => {
        await result.current.end();
      });

      // Should call callback even when error occurs
      expect(onSessionEnd).toHaveBeenCalled();
    });
  });

  describe('status polling', () => {
    it('should poll status every 5 seconds when session active', async () => {
      const mockStatus = createMockStatus({ time_remaining: 280 });
      const updatedStatus = createMockStatus({ time_remaining: 275, actions_count: 2 });

      vi.mocked(inhabitApi.start).mockResolvedValueOnce({ data: mockStatus } as any);
      vi.mocked(inhabitApi.getStatus).mockResolvedValue({ data: updatedStatus } as any);

      const { result, unmount } = renderHook(() => useInhabitSession(defaultOptions));

      await act(async () => {
        await result.current.start();
      });

      expect(result.current.timeRemaining).toBe(280);

      // Advance timer by 5 seconds and wait for promise
      await act(async () => {
        vi.advanceTimersByTime(5000);
        // Wait for the async poll to complete
        await Promise.resolve();
        await Promise.resolve();
      });

      expect(inhabitApi.getStatus).toHaveBeenCalledWith('test-town', 'Alice');

      // Clean up to stop the interval
      unmount();
    });

    it('should trigger onSessionEnd when session expires', async () => {
      const mockStatus = createMockStatus();
      const expiredStatus = createMockStatus({ expired: true, time_remaining: 0 });

      vi.mocked(inhabitApi.start).mockResolvedValueOnce({ data: mockStatus } as any);
      vi.mocked(inhabitApi.getStatus).mockResolvedValueOnce({ data: expiredStatus } as any);

      const onSessionEnd = vi.fn();
      const { result, unmount } = renderHook(() =>
        useInhabitSession({ ...defaultOptions, onSessionEnd })
      );

      await act(async () => {
        await result.current.start();
      });

      // Advance timer to trigger poll and wait for promise
      await act(async () => {
        vi.advanceTimersByTime(5000);
        await Promise.resolve();
        await Promise.resolve();
      });

      expect(onSessionEnd).toHaveBeenCalled();
      expect(result.current.isExpired).toBe(true);

      unmount();
    });

    it('should clear status when getStatus fails', async () => {
      const mockStatus = createMockStatus();

      vi.mocked(inhabitApi.start).mockResolvedValueOnce({ data: mockStatus } as any);
      vi.mocked(inhabitApi.getStatus).mockRejectedValueOnce(new Error('Session not found'));

      const { result, unmount } = renderHook(() => useInhabitSession(defaultOptions));

      await act(async () => {
        await result.current.start();
      });

      expect(result.current.status).not.toBeNull();

      // Advance timer to trigger poll and wait for promise
      await act(async () => {
        vi.advanceTimersByTime(5000);
        await Promise.resolve();
        await Promise.resolve();
      });

      expect(result.current.status).toBeNull();

      unmount();
    });
  });

  describe('computed values', () => {
    it('should compute timeRemaining from status', async () => {
      const mockStatus = createMockStatus({ time_remaining: 150 });
      vi.mocked(inhabitApi.start).mockResolvedValueOnce({ data: mockStatus } as any);

      const { result } = renderHook(() => useInhabitSession(defaultOptions));

      await act(async () => {
        await result.current.start();
      });

      expect(result.current.timeRemaining).toBe(150);
    });

    it('should compute consentDebt from status', async () => {
      const mockStatus = createMockStatus({
        consent: {
          debt: 0.7,
          status: 'strained',
          at_rupture: false,
          can_force: false,
          cooldown: 0,
        },
      });
      vi.mocked(inhabitApi.start).mockResolvedValueOnce({ data: mockStatus } as any);

      const { result } = renderHook(() => useInhabitSession(defaultOptions));

      await act(async () => {
        await result.current.start();
      });

      expect(result.current.consentDebt).toBe(0.7);
    });

    it('should compute canForce from status', async () => {
      const mockStatus = createMockStatus({
        consent: { debt: 0.2, status: 'granted', at_rupture: false, can_force: true, cooldown: 0 },
      });
      vi.mocked(inhabitApi.start).mockResolvedValueOnce({ data: mockStatus } as any);

      const { result } = renderHook(() => useInhabitSession(defaultOptions));

      await act(async () => {
        await result.current.start();
      });

      expect(result.current.canForce).toBe(true);
    });

    it('should compute isRuptured from status', async () => {
      const mockStatus = createMockStatus({
        consent: {
          debt: 1.0,
          status: 'ruptured',
          at_rupture: true,
          can_force: false,
          cooldown: 120,
        },
      });
      vi.mocked(inhabitApi.start).mockResolvedValueOnce({ data: mockStatus } as any);

      const { result } = renderHook(() => useInhabitSession(defaultOptions));

      await act(async () => {
        await result.current.start();
      });

      expect(result.current.isRuptured).toBe(true);
    });

    it('should compute isExpired from status', async () => {
      const mockStatus = createMockStatus({ expired: true });
      vi.mocked(inhabitApi.start).mockResolvedValueOnce({ data: mockStatus } as any);

      const { result } = renderHook(() => useInhabitSession(defaultOptions));

      await act(async () => {
        await result.current.start();
      });

      expect(result.current.isExpired).toBe(true);
    });
  });

  describe('history tracking', () => {
    it('should accumulate responses in history', async () => {
      // Use real timers for this test since it doesn't involve polling
      vi.useRealTimers();

      const mockStatus = createMockStatus();
      const response1 = createMockResponse({ message: 'First response' });
      const response2 = createMockResponse({ message: 'Second response' });
      const response3 = createMockResponse({ message: 'Third response' });

      vi.mocked(inhabitApi.start).mockResolvedValueOnce({ data: mockStatus } as any);
      // Mock getStatus to prevent polling errors
      vi.mocked(inhabitApi.getStatus).mockResolvedValue({ data: mockStatus } as any);
      vi.mocked(inhabitApi.suggest)
        .mockResolvedValueOnce({ data: response1 } as any)
        .mockResolvedValueOnce({ data: response2 } as any)
        .mockResolvedValueOnce({ data: response3 } as any);

      const { result, unmount } = renderHook(() => useInhabitSession(defaultOptions));

      await act(async () => {
        await result.current.start();
      });

      await act(async () => {
        await result.current.submitAction('action 1');
      });

      await act(async () => {
        await result.current.submitAction('action 2');
      });

      await act(async () => {
        await result.current.submitAction('action 3');
      });

      expect(result.current.history).toHaveLength(3);
      expect(result.current.history[0].message).toBe('First response');
      expect(result.current.history[2].message).toBe('Third response');

      // Clean up
      unmount();

      // Restore fake timers for subsequent tests
      vi.useFakeTimers();
    });
  });
});
