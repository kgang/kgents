/**
 * useCitizenDialogue - Hook for managing citizen dialogue lifecycle.
 *
 * Phase 5: Town End-to-End (2D Renaissance)
 *
 * Handles:
 * - Starting conversations with citizens
 * - Sending messages and receiving LLM-generated responses
 * - Loading conversation history
 * - Error and loading states
 *
 * @example
 * const {
 *   conversation,
 *   isLoading,
 *   error,
 *   startConversation,
 *   sendMessage,
 *   endConversation,
 *   history,
 *   loadHistory,
 * } = useCitizenDialogue(townId, citizenId);
 */

import { useState, useCallback, useRef } from 'react';
import { townApi } from '../api/client';
import type { ConversationDetail, ConversationSummary, TurnSummary } from '../api/types';

export interface UseCitizenDialogueResult {
  /** Current active conversation (null if none) */
  conversation: ConversationDetail | null;

  /** Whether a message is being sent or conversation is loading */
  isLoading: boolean;

  /** Whether the initial conversation is being started */
  isStarting: boolean;

  /** Error message if an operation failed */
  error: string | null;

  /** Start a new conversation with the citizen */
  startConversation: (topic?: string) => Promise<void>;

  /** Send a message to the citizen (triggers LLM response) */
  sendMessage: (content: string) => Promise<void>;

  /** End the current conversation (clears local state) */
  endConversation: () => void;

  /** Previous conversations with this citizen */
  history: ConversationSummary[];

  /** Whether history is loading */
  historyLoading: boolean;

  /** Load conversation history */
  loadHistory: () => Promise<void>;
}

export function useCitizenDialogue(citizenId: string): UseCitizenDialogueResult {
  // Conversation state
  const [conversation, setConversation] = useState<ConversationDetail | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isStarting, setIsStarting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // History state
  const [history, setHistory] = useState<ConversationSummary[]>([]);
  const [historyLoading, setHistoryLoading] = useState(false);

  // Prevent duplicate requests
  const pendingRef = useRef(false);

  /**
   * Start a new conversation with the citizen.
   */
  const startConversation = useCallback(
    async (topic?: string) => {
      if (pendingRef.current) return;
      pendingRef.current = true;

      setIsStarting(true);
      setError(null);

      try {
        const conv = await townApi.converse(citizenId, topic);
        setConversation(conv);
      } catch (err: unknown) {
        const axiosErr = err as { response?: { data?: { detail?: string } }; message?: string };
        const message =
          axiosErr.response?.data?.detail || axiosErr.message || 'Failed to start conversation';
        setError(message);
      } finally {
        setIsStarting(false);
        // eslint-disable-next-line require-atomic-updates -- Safe: ref reset in finally block
        pendingRef.current = false;
      }
    },
    [citizenId]
  );

  /**
   * Send a message to the citizen.
   * The backend will store the user's message and generate a citizen response via LLM.
   */
  const sendMessage = useCallback(
    async (content: string) => {
      if (!conversation) {
        setError('No active conversation');
        return;
      }

      if (pendingRef.current) return;
      pendingRef.current = true;

      setIsLoading(true);
      setError(null);

      try {
        // Add optimistic user message
        const userTurn: TurnSummary = {
          id: `temp-${Date.now()}`,
          turn_number: conversation.turns.length + 1,
          role: 'user',
          content,
          sentiment: null,
          emotion: null,
          created_at: new Date().toISOString(),
        };

        setConversation((prev) => {
          if (!prev) return prev;
          return {
            ...prev,
            turns: [...prev.turns, userTurn],
            turn_count: prev.turn_count + 1,
          };
        });

        // Send to backend and get citizen response
        const citizenTurn = await townApi.turn(conversation.id, content);

        // Update with real citizen response
        setConversation((prev) => {
          if (!prev) return prev;
          return {
            ...prev,
            turns: [...prev.turns, citizenTurn],
            turn_count: prev.turn_count + 1,
          };
        });
      } catch (err: unknown) {
        const axiosErr = err as { response?: { data?: { detail?: string } }; message?: string };
        const message =
          axiosErr.response?.data?.detail || axiosErr.message || 'Failed to send message';
        setError(message);

        // Remove optimistic update on error
        setConversation((prev) => {
          if (!prev) return prev;
          return {
            ...prev,
            turns: prev.turns.slice(0, -1),
            turn_count: prev.turn_count - 1,
          };
        });
      } finally {
        setIsLoading(false);
        // eslint-disable-next-line require-atomic-updates -- Safe: ref reset in finally block
        pendingRef.current = false;
      }
    },
    [conversation]
  );

  /**
   * End the current conversation (clears local state).
   * The conversation persists on the backend for history.
   */
  const endConversation = useCallback(() => {
    setConversation(null);
    setError(null);
  }, []);

  /**
   * Load previous conversation history for this citizen.
   */
  const loadHistory = useCallback(async () => {
    setHistoryLoading(true);

    try {
      const conversations = await townApi.getHistory(citizenId, 10);
      setHistory(conversations);
    } catch (err: unknown) {
      // History errors are non-critical, just log
      console.error('Failed to load dialogue history:', err);
    } finally {
      setHistoryLoading(false);
    }
  }, [citizenId]);

  return {
    conversation,
    isLoading,
    isStarting,
    error,
    startConversation,
    sendMessage,
    endConversation,
    history,
    historyLoading,
    loadHistory,
  };
}

export default useCitizenDialogue;
