import { useState, useCallback, useEffect, useRef } from 'react';
import { inhabitApi } from '@/api/client';

// =============================================================================
// Helpers
// =============================================================================

interface AxiosLikeError {
  response?: {
    data?: { detail?: string };
    status?: number;
  };
  message?: string;
}

/**
 * Extract error message from unknown error type.
 * Handles axios-style errors and standard Error objects.
 */
function extractErrorMessage(err: unknown, fallback: string): string {
  if (err instanceof Error) {
    return err.message;
  }
  if (typeof err === 'object' && err !== null) {
    const axiosErr = err as AxiosLikeError;
    if (axiosErr.response?.data?.detail) {
      return axiosErr.response.data.detail;
    }
    if (axiosErr.message) {
      return axiosErr.message;
    }
  }
  return fallback;
}

// =============================================================================
// Types
// =============================================================================

export interface InhabitStatus {
  citizen: string;
  tier: string;
  duration: number;
  time_remaining: number;
  consent: {
    debt: number;
    status: string;
    at_rupture: boolean;
    can_force: boolean;
    cooldown: number;
  };
  force: {
    enabled: boolean;
    used: number;
    remaining: number;
    limit: number;
  };
  expired: boolean;
  actions_count: number;
}

export interface InhabitResponse {
  type: 'enact' | 'resist' | 'negotiate' | 'exit';
  message: string;
  inner_voice: string;
  cost?: number;
  alignment_score?: number;
  suggested_rephrase?: string;
  status: InhabitStatus;
  success?: boolean;
}

interface UseInhabitSessionOptions {
  townId: string;
  citizenName: string;
  forceEnabled?: boolean;
  onSessionEnd?: () => void;
  onRupture?: () => void;
}

interface UseInhabitSessionReturn {
  // State
  status: InhabitStatus | null;
  isLoading: boolean;
  error: string | null;
  lastResponse: InhabitResponse | null;
  history: InhabitResponse[];

  // Actions
  start: () => Promise<void>;
  submitAction: (action: string) => Promise<InhabitResponse | null>;
  forceAction: (action: string, severity?: number) => Promise<InhabitResponse | null>;
  apologize: (sincerity?: number) => Promise<InhabitResponse | null>;
  end: () => Promise<void>;

  // Computed
  timeRemaining: number;
  consentDebt: number;
  canForce: boolean;
  isRuptured: boolean;
  isExpired: boolean;
}

// =============================================================================
// Hook
// =============================================================================

export function useInhabitSession({
  townId,
  citizenName,
  forceEnabled = false,
  onSessionEnd,
  onRupture,
}: UseInhabitSessionOptions): UseInhabitSessionReturn {
  // State
  const [status, setStatus] = useState<InhabitStatus | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastResponse, setLastResponse] = useState<InhabitResponse | null>(null);
  const [history, setHistory] = useState<InhabitResponse[]>([]);

  // Refs for cleanup
  const statusIntervalRef = useRef<number | null>(null);

  // Start session
  const start = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await inhabitApi.start(townId, citizenName, forceEnabled);
      setStatus(response.data as InhabitStatus);
    } catch (err: unknown) {
      const message = extractErrorMessage(err, 'Failed to start INHABIT session');
      setError(message);
      throw new Error(message);
    } finally {
      setIsLoading(false);
    }
  }, [townId, citizenName, forceEnabled]);

  // Submit action (suggest)
  const submitAction = useCallback(async (action: string): Promise<InhabitResponse | null> => {
    if (!status) {
      setError('No active session');
      return null;
    }

    setIsLoading(true);
    setError(null);

    try {
      const response = await inhabitApi.suggest(townId, citizenName, action);
      const data = response.data as InhabitResponse;

      setLastResponse(data);
      setHistory((prev) => [...prev, data]);
      setStatus(data.status);

      // Check for rupture
      if (data.status.consent.at_rupture) {
        onRupture?.();
      }

      // Check for session end
      if (data.type === 'exit') {
        onSessionEnd?.();
      }

      return data;
    } catch (err: unknown) {
      const message = extractErrorMessage(err, 'Failed to submit action');
      setError(message);
      return null;
    } finally {
      setIsLoading(false);
    }
  }, [townId, citizenName, status, onRupture, onSessionEnd]);

  // Force action
  const forceAction = useCallback(async (
    action: string,
    severity: number = 0.2
  ): Promise<InhabitResponse | null> => {
    if (!status) {
      setError('No active session');
      return null;
    }

    setIsLoading(true);
    setError(null);

    try {
      const response = await inhabitApi.force(townId, citizenName, action, severity);
      const data = response.data as InhabitResponse;

      setLastResponse(data);
      setHistory((prev) => [...prev, data]);
      setStatus(data.status);

      // Check for rupture
      if (data.status.consent.at_rupture) {
        onRupture?.();
      }

      return data;
    } catch (err: unknown) {
      const message = extractErrorMessage(err, 'Cannot force action');
      setError(message);
      return null;
    } finally {
      setIsLoading(false);
    }
  }, [townId, citizenName, status, onRupture]);

  // Apologize
  const apologize = useCallback(async (sincerity: number = 0.3): Promise<InhabitResponse | null> => {
    if (!status) {
      setError('No active session');
      return null;
    }

    setIsLoading(true);
    setError(null);

    try {
      const response = await inhabitApi.apologize(townId, citizenName, sincerity);
      const data = response.data as InhabitResponse;

      setLastResponse(data);
      setHistory((prev) => [...prev, data]);
      setStatus(data.status);

      return data;
    } catch (err: unknown) {
      const message = extractErrorMessage(err, 'Failed to apologize');
      setError(message);
      return null;
    } finally {
      setIsLoading(false);
    }
  }, [townId, citizenName, status]);

  // End session
  const end = useCallback(async () => {
    if (!status) return;

    setIsLoading(true);

    try {
      await inhabitApi.end(townId, citizenName);
      setStatus(null);
      onSessionEnd?.();
    } catch {
      // Session might already be ended
      setStatus(null);
      onSessionEnd?.();
    } finally {
      setIsLoading(false);
    }
  }, [townId, citizenName, status, onSessionEnd]);

  // Poll status periodically
  useEffect(() => {
    if (!status) return;

    const pollStatus = async () => {
      try {
        const response = await inhabitApi.getStatus(townId, citizenName);
        const data = response.data as InhabitStatus;
        setStatus(data);

        // Check for expiration
        if (data.expired) {
          onSessionEnd?.();
        }
      } catch {
        // Session might have ended
        setStatus(null);
      }
    };

    // Poll every 5 seconds
    statusIntervalRef.current = window.setInterval(pollStatus, 5000);

    return () => {
      if (statusIntervalRef.current) {
        clearInterval(statusIntervalRef.current);
      }
    };
  }, [townId, citizenName, status, onSessionEnd]);

  // Computed values
  const timeRemaining = status?.time_remaining ?? 0;
  const consentDebt = status?.consent.debt ?? 0;
  const canForce = status?.consent.can_force ?? false;
  const isRuptured = status?.consent.at_rupture ?? false;
  const isExpired = status?.expired ?? false;

  return {
    status,
    isLoading,
    error,
    lastResponse,
    history,

    start,
    submitAction,
    forceAction,
    apologize,
    end,

    timeRemaining,
    consentDebt,
    canForce,
    isRuptured,
    isExpired,
  };
}

export default useInhabitSession;
