import { useCallback, useState } from 'react';

export interface FeedbackMessage {
  type: 'success' | 'warning' | 'error';
  text: string;
}

interface UseFeedbackMessageReturn {
  feedbackMessage: FeedbackMessage | null;
  showFeedback: (message: FeedbackMessage, duration?: number) => void;
  showSuccess: (text: string, duration?: number) => void;
  showWarning: (text: string, duration?: number) => void;
  showError: (text: string, duration?: number) => void;
  clearFeedback: () => void;
}

const DEFAULT_SUCCESS_DURATION = 3000;
const DEFAULT_WARNING_DURATION = 3000;
const DEFAULT_ERROR_DURATION = 4000;

export function useFeedbackMessage(): UseFeedbackMessageReturn {
  const [feedbackMessage, setFeedbackMessage] = useState<FeedbackMessage | null>(null);

  const showFeedback = useCallback((message: FeedbackMessage, duration?: number) => {
    setFeedbackMessage(message);
    if (duration !== 0) {
      const timeout = duration ?? (
        message.type === 'error' ? DEFAULT_ERROR_DURATION :
        message.type === 'warning' ? DEFAULT_WARNING_DURATION :
        DEFAULT_SUCCESS_DURATION
      );
      setTimeout(() => setFeedbackMessage(null), timeout);
    }
  }, []);

  const showSuccess = useCallback((text: string, duration?: number) => {
    showFeedback({ type: 'success', text }, duration ?? DEFAULT_SUCCESS_DURATION);
  }, [showFeedback]);

  const showWarning = useCallback((text: string, duration?: number) => {
    showFeedback({ type: 'warning', text }, duration ?? DEFAULT_WARNING_DURATION);
  }, [showFeedback]);

  const showError = useCallback((text: string, duration?: number) => {
    showFeedback({ type: 'error', text }, duration ?? DEFAULT_ERROR_DURATION);
  }, [showFeedback]);

  const clearFeedback = useCallback(() => {
    setFeedbackMessage(null);
  }, []);

  return {
    feedbackMessage,
    showFeedback,
    showSuccess,
    showWarning,
    showError,
    clearFeedback,
  };
}
