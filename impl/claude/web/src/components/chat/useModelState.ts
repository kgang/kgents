/**
 * useModelState - Hook for managing model selection state
 *
 * Provides a clean interface for fetching and setting models,
 * with optimistic updates and error handling.
 *
 * @see ModelSwitcher.tsx for the UI component
 */

import { useState, useCallback, useEffect, useRef } from 'react';
import { useAgenteseMutation } from '@/hooks/useAgentesePath';
import type {
  SelfChatModelsResponse,
  SelfChatSet_modelResponse,
} from '@/api/types/_generated/self-chat';

// Inline type for model option (from response)
type SelfChatModelOption = SelfChatModelsResponse['models'][number];

// Default models when API unavailable
const DEFAULT_MODELS: SelfChatModelOption[] = [
  {
    id: 'claude-3-haiku-20240307',
    name: 'Haiku',
    description: 'Fast responses, lower cost',
    tier: 'fast',
  },
  {
    id: 'claude-sonnet-4-20250514',
    name: 'Sonnet',
    description: 'Balanced speed and capability',
    tier: 'balanced',
  },
  {
    id: 'claude-opus-4-20250514',
    name: 'Opus',
    description: 'Most capable, highest quality',
    tier: 'powerful',
  },
];

export function useModelState(sessionId: string | null) {
  const [models, setModels] = useState<SelfChatModelOption[]>(DEFAULT_MODELS);
  const [currentModel, setCurrentModel] = useState<string | null>(null);
  const [canSwitch, setCanSwitch] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const lastSessionIdRef = useRef<string | null>(null);

  const { mutate: fetchModels } = useAgenteseMutation<
    { session_id?: string | null },
    SelfChatModelsResponse
  >('self.chat:models');

  const { mutate: setModelApi } = useAgenteseMutation<
    { session_id: string; model: string },
    SelfChatSet_modelResponse
  >('self.chat:set_model');

  // Refresh model state
  const refresh = useCallback(async () => {
    if (!sessionId) return;
    setIsLoading(true);
    try {
      const response = await fetchModels({ session_id: sessionId });
      if (response) {
        setModels(response.models);
        setCurrentModel(response.current_model ?? null);
        setCanSwitch(response.can_switch ?? false);
      }
    } finally {
      setIsLoading(false);
    }
  }, [sessionId, fetchModels]);

  // Set model
  const setModel = useCallback(
    async (modelId: string) => {
      if (!sessionId || !canSwitch) return false;
      setIsLoading(true);
      try {
        const response = await setModelApi({ session_id: sessionId, model: modelId });
        if (response?.success) {
          setCurrentModel(modelId);
          return true;
        }
        return false;
      } finally {
        setIsLoading(false);
      }
    },
    [sessionId, canSwitch, setModelApi]
  );

  // Load on mount only when sessionId changes
  useEffect(() => {
    if (sessionId && sessionId !== lastSessionIdRef.current) {
      lastSessionIdRef.current = sessionId;
      refresh();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [sessionId]);

  return {
    models,
    currentModel,
    canSwitch,
    isLoading,
    setModel,
    refresh,
  };
}

export default useModelState;
