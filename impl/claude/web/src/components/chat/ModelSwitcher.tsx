/**
 * ModelSwitcher - AI Model Selection for Chat Sessions
 *
 * Allows users to switch between LLM models during a conversation.
 * Each tier offers different tradeoffs: speed vs capability vs cost.
 *
 * Design principles:
 * - "Daring, bold, creative, opinionated but not gaudy"
 * - Knowledge semantic color (cyan) for AI metadata
 * - Minimal chrome, maximum clarity
 *
 * AGENTESE Paths:
 * - self.chat:models - Get available models
 * - self.chat:set_model - Set session model
 *
 * @see services/chat/model_selector.py
 * @see docs/skills/crown-jewel-patterns.md - Pattern 14: Teaching Mode
 */

import { useState, useCallback, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Zap, Scale, Sparkles, ChevronDown, Check, Loader2 } from 'lucide-react';
import { useAgenteseMutation } from '@/hooks/useAgentesePath';
import type {
  SelfChatModelsResponse,
  SelfChatSet_modelResponse,
} from '@/api/types/_generated/self-chat';

// Inline type for model option (from response)
type SelfChatModelOption = SelfChatModelsResponse['models'][number];

// =============================================================================
// Types
// =============================================================================

export interface ModelSwitcherProps {
  /** Current session ID */
  sessionId: string | null;
  /** Current model (from session state) */
  currentModel?: string | null;
  /** Whether the user can switch models */
  canSwitch?: boolean;
  /** Callback when model changes */
  onModelChange?: (model: string) => void;
  /** Visual variant */
  variant?: 'dropdown' | 'pills' | 'compact';
  /** Size variant */
  size?: 'sm' | 'md';
  /** Additional CSS classes */
  className?: string;
}

// Tier metadata for visual styling
const TIER_META: Record<string, { icon: React.ReactNode; color: string; bgColor: string }> = {
  fast: {
    icon: <Zap className="w-3.5 h-3.5" />,
    color: 'text-emerald-400',
    bgColor: 'bg-emerald-500/10 border-emerald-500/20',
  },
  balanced: {
    icon: <Scale className="w-3.5 h-3.5" />,
    color: 'text-cyan-400',
    bgColor: 'bg-cyan-500/10 border-cyan-500/20',
  },
  powerful: {
    icon: <Sparkles className="w-3.5 h-3.5" />,
    color: 'text-violet-400',
    bgColor: 'bg-violet-500/10 border-violet-500/20',
  },
};

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

// =============================================================================
// Component
// =============================================================================

export function ModelSwitcher({
  sessionId,
  currentModel,
  canSwitch = true,
  onModelChange,
  variant = 'dropdown',
  size = 'md',
  className = '',
}: ModelSwitcherProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [models, setModels] = useState<SelfChatModelOption[]>(DEFAULT_MODELS);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const lastSessionIdRef = useRef<string | null>(null);
  // Track whether user has explicitly selected a model this session
  const userSelectedRef = useRef(false);

  // Fetch available models
  const { mutate: fetchModels, isLoading: isLoadingModels } = useAgenteseMutation<
    { session_id?: string | null },
    SelfChatModelsResponse
  >('self.chat:models');

  // Set model mutation
  const { mutate: setModel, isLoading: isSettingModel } = useAgenteseMutation<
    { session_id: string; model: string },
    SelfChatSet_modelResponse
  >('self.chat:set_model');

  // Load models only when sessionId actually changes (not on every render)
  useEffect(() => {
    // Skip if sessionId hasn't changed
    if (sessionId === lastSessionIdRef.current) {
      return;
    }
    lastSessionIdRef.current = sessionId;
    // Reset user selection tracking when session changes
    userSelectedRef.current = false;

    if (!sessionId) return;

    const loadModels = async () => {
      const response = await fetchModels({ session_id: sessionId });
      if (response?.models) {
        setModels(response.models);
        // Only set model from backend if user hasn't explicitly selected one
        // AND parent doesn't already have a model set
        if (response.current_model && !currentModel && !userSelectedRef.current) {
          onModelChange?.(response.current_model);
        }
      }
    };
    loadModels();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [sessionId]);

  // Close dropdown on outside click
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Handle model selection
  const handleSelectModel = useCallback(
    async (modelId: string) => {
      if (!sessionId || !canSwitch || modelId === currentModel) {
        setIsOpen(false);
        return;
      }

      // Mark that user has explicitly selected a model
      userSelectedRef.current = true;

      const response = await setModel({ session_id: sessionId, model: modelId });
      if (response?.success) {
        // Lift state up to parent - parent is the single source of truth
        onModelChange?.(modelId);
      }
      setIsOpen(false);
    },
    [sessionId, canSwitch, currentModel, setModel, onModelChange]
  );

  // Get current model info - use prop (single source of truth)
  const currentModelInfo = models.find((m) => m.id === currentModel) || models[1]; // Default to Sonnet
  const tierMeta = TIER_META[currentModelInfo?.tier || 'balanced'];

  // Size classes
  const sizeClasses = size === 'sm' ? 'text-xs px-2 py-1' : 'text-sm px-3 py-1.5';

  // If user can't switch, show read-only indicator
  if (!canSwitch) {
    return (
      <div className={`flex items-center gap-1.5 ${className}`}>
        <span className={`${tierMeta.color} ${sizeClasses}`}>{tierMeta.icon}</span>
        <span className="text-gray-400 text-xs">{currentModelInfo?.name || 'Sonnet'}</span>
      </div>
    );
  }

  // Dropdown variant (default)
  if (variant === 'dropdown') {
    return (
      <div ref={dropdownRef} className={`relative ${className}`}>
        {/* Trigger button */}
        <button
          onClick={() => setIsOpen(!isOpen)}
          disabled={isLoadingModels || isSettingModel}
          className={`
            flex items-center gap-2 rounded-lg border transition-all duration-200
            ${tierMeta.bgColor}
            ${sizeClasses}
            ${isOpen ? 'ring-1 ring-cyan-500/50' : ''}
            hover:bg-gray-700/50
            disabled:opacity-50 disabled:cursor-not-allowed
          `}
        >
          <span className={tierMeta.color}>{tierMeta.icon}</span>
          <span className="text-gray-200 font-medium">{currentModelInfo?.name || 'Model'}</span>
          {isSettingModel ? (
            <Loader2 className="w-3.5 h-3.5 text-gray-400 animate-spin" />
          ) : (
            <ChevronDown
              className={`w-3.5 h-3.5 text-gray-400 transition-transform ${isOpen ? 'rotate-180' : ''}`}
            />
          )}
        </button>

        {/* Dropdown menu */}
        <AnimatePresence>
          {isOpen && (
            <motion.div
              initial={{ opacity: 0, y: -4 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -4 }}
              transition={{ duration: 0.15 }}
              className="absolute top-full left-0 mt-1.5 w-56 bg-gray-800 border border-gray-700 rounded-lg shadow-xl z-50 overflow-hidden"
            >
              <div className="py-1">
                {models.map((model) => {
                  const meta = TIER_META[model.tier];
                  const isSelected = model.id === currentModel;
                  return (
                    <button
                      key={model.id}
                      onClick={() => handleSelectModel(model.id)}
                      className={`
                        w-full flex items-start gap-3 px-3 py-2.5 text-left
                        transition-colors duration-100
                        ${isSelected ? 'bg-gray-700/50' : 'hover:bg-gray-700/30'}
                      `}
                    >
                      <span className={`mt-0.5 ${meta.color}`}>{meta.icon}</span>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2">
                          <span className="font-medium text-gray-100">{model.name}</span>
                          {isSelected && <Check className="w-3.5 h-3.5 text-cyan-400" />}
                        </div>
                        <p className="text-xs text-gray-500 mt-0.5">{model.description}</p>
                      </div>
                    </button>
                  );
                })}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    );
  }

  // Pills variant
  if (variant === 'pills') {
    return (
      <div className={`flex items-center gap-1.5 ${className}`}>
        {models.map((model) => {
          const meta = TIER_META[model.tier];
          const isSelected = model.id === currentModel;
          return (
            <button
              key={model.id}
              onClick={() => handleSelectModel(model.id)}
              disabled={isSettingModel}
              title={model.description}
              className={`
                flex items-center gap-1.5 rounded-full transition-all duration-200
                ${sizeClasses}
                ${
                  isSelected
                    ? `${meta.bgColor} ${meta.color} border shadow-sm`
                    : 'text-gray-400 hover:text-gray-200 hover:bg-gray-700/50 border border-transparent'
                }
                disabled:opacity-50 disabled:cursor-not-allowed
              `}
            >
              {meta.icon}
              <span className="font-medium">{model.name}</span>
            </button>
          );
        })}
      </div>
    );
  }

  // Compact variant (icon only with tooltip)
  return (
    <div className={`flex items-center gap-0.5 ${className}`}>
      {models.map((model) => {
        const meta = TIER_META[model.tier];
        const isSelected = model.id === currentModel;
        return (
          <button
            key={model.id}
            onClick={() => handleSelectModel(model.id)}
            disabled={isSettingModel}
            title={`${model.name}: ${model.description}`}
            className={`
              p-1.5 rounded transition-all duration-200
              ${
                isSelected
                  ? `${meta.color} bg-gray-700/50`
                  : 'text-gray-500 hover:text-gray-300 hover:bg-gray-700/30'
              }
              disabled:opacity-50 disabled:cursor-not-allowed
            `}
          >
            {meta.icon}
          </button>
        );
      })}
    </div>
  );
}

export default ModelSwitcher;
