/**
 * Tests for useCitizenDialogue hook.
 *
 * Phase 5: Town End-to-End (2D Renaissance)
 *
 * @see src/hooks/useCitizenDialogue.ts
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, act, waitFor } from '@testing-library/react';
import { useCitizenDialogue } from '@/hooks/useCitizenDialogue';
import { townApi } from '@/api/client';
import type { ConversationDetail, TurnSummary, ConversationSummary } from '@/api/types';

// Mock the townApi
vi.mock('@/api/client', () => ({
  townApi: {
    converse: vi.fn(),
    turn: vi.fn(),
    getHistory: vi.fn(),
  },
}));

// Test fixtures
const mockConversation: ConversationDetail = {
  id: 'conv-123',
  citizen_id: 'citizen-456',
  citizen_name: 'Alice',
  topic: 'General chat',
  summary: null,
  turn_count: 0,
  is_active: true,
  created_at: '2025-12-18T10:00:00Z',
  turns: [],
};

const mockCitizenTurn: TurnSummary = {
  id: 'turn-789',
  turn_number: 2,
  role: 'citizen',
  content: 'Hello! Nice to meet you.',
  sentiment: 'positive',
  emotion: 'friendly',
  created_at: '2025-12-18T10:01:00Z',
};

const mockHistory: ConversationSummary[] = [
  {
    id: 'conv-old-1',
    topic: 'Previous topic',
    summary: 'Discussed the weather',
    turn_count: 4,
    is_active: false,
    created_at: '2025-12-17T10:00:00Z',
  },
];

describe('useCitizenDialogue', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('initial state', () => {
    it('should start with no conversation', () => {
      const { result } = renderHook(() => useCitizenDialogue('citizen-456'));

      expect(result.current.conversation).toBeNull();
      expect(result.current.isLoading).toBe(false);
      expect(result.current.isStarting).toBe(false);
      expect(result.current.error).toBeNull();
      expect(result.current.history).toEqual([]);
    });
  });

  describe('startConversation', () => {
    it('should start a conversation successfully', async () => {
      vi.mocked(townApi.converse).mockResolvedValueOnce(mockConversation);

      const { result } = renderHook(() => useCitizenDialogue('citizen-456'));

      await act(async () => {
        await result.current.startConversation('General chat');
      });

      expect(townApi.converse).toHaveBeenCalledWith('citizen-456', 'General chat');
      expect(result.current.conversation).toEqual(mockConversation);
      expect(result.current.error).toBeNull();
    });

    it('should handle errors when starting conversation', async () => {
      vi.mocked(townApi.converse).mockRejectedValueOnce(new Error('Network error'));

      const { result } = renderHook(() => useCitizenDialogue('citizen-456'));

      await act(async () => {
        await result.current.startConversation();
      });

      expect(result.current.conversation).toBeNull();
      expect(result.current.error).toBe('Network error');
    });

    it('should set isStarting during conversation start', async () => {
      let resolvePromise: (value: ConversationDetail) => void;
      vi.mocked(townApi.converse).mockReturnValueOnce(
        new Promise((resolve) => {
          resolvePromise = resolve;
        })
      );

      const { result } = renderHook(() => useCitizenDialogue('citizen-456'));

      act(() => {
        result.current.startConversation();
      });

      expect(result.current.isStarting).toBe(true);

      await act(async () => {
        resolvePromise!(mockConversation);
      });

      expect(result.current.isStarting).toBe(false);
    });
  });

  describe('sendMessage', () => {
    it('should send a message and receive citizen response', async () => {
      vi.mocked(townApi.converse).mockResolvedValueOnce(mockConversation);
      vi.mocked(townApi.turn).mockResolvedValueOnce(mockCitizenTurn);

      const { result } = renderHook(() => useCitizenDialogue('citizen-456'));

      // Start conversation first
      await act(async () => {
        await result.current.startConversation();
      });

      // Send message
      await act(async () => {
        await result.current.sendMessage('Hello!');
      });

      expect(townApi.turn).toHaveBeenCalledWith('conv-123', 'Hello!');
      // Should have user message + citizen response
      expect(result.current.conversation?.turns).toHaveLength(2);
      expect(result.current.conversation?.turns[1]).toEqual(mockCitizenTurn);
    });

    it('should not send message without active conversation', async () => {
      const { result } = renderHook(() => useCitizenDialogue('citizen-456'));

      await act(async () => {
        await result.current.sendMessage('Hello!');
      });

      expect(townApi.turn).not.toHaveBeenCalled();
      expect(result.current.error).toBe('No active conversation');
    });

    it('should handle send errors and rollback optimistic update', async () => {
      vi.mocked(townApi.converse).mockResolvedValueOnce(mockConversation);
      vi.mocked(townApi.turn).mockRejectedValueOnce(new Error('Send failed'));

      const { result } = renderHook(() => useCitizenDialogue('citizen-456'));

      await act(async () => {
        await result.current.startConversation();
      });

      await act(async () => {
        await result.current.sendMessage('Hello!');
      });

      expect(result.current.error).toBe('Send failed');
      // Should rollback - no turns after error
      expect(result.current.conversation?.turns).toHaveLength(0);
    });
  });

  describe('endConversation', () => {
    it('should clear the conversation', async () => {
      vi.mocked(townApi.converse).mockResolvedValueOnce(mockConversation);

      const { result } = renderHook(() => useCitizenDialogue('citizen-456'));

      await act(async () => {
        await result.current.startConversation();
      });

      expect(result.current.conversation).not.toBeNull();

      act(() => {
        result.current.endConversation();
      });

      expect(result.current.conversation).toBeNull();
      expect(result.current.error).toBeNull();
    });
  });

  describe('loadHistory', () => {
    it('should load conversation history', async () => {
      vi.mocked(townApi.getHistory).mockResolvedValueOnce(mockHistory);

      const { result } = renderHook(() => useCitizenDialogue('citizen-456'));

      await act(async () => {
        await result.current.loadHistory();
      });

      expect(townApi.getHistory).toHaveBeenCalledWith('citizen-456', 10);
      expect(result.current.history).toEqual(mockHistory);
    });

    it('should handle history errors gracefully', async () => {
      vi.mocked(townApi.getHistory).mockRejectedValueOnce(new Error('History failed'));
      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});

      const { result } = renderHook(() => useCitizenDialogue('citizen-456'));

      await act(async () => {
        await result.current.loadHistory();
      });

      // Should not throw - errors are logged
      expect(consoleSpy).toHaveBeenCalled();
      expect(result.current.history).toEqual([]);

      consoleSpy.mockRestore();
    });
  });
});
