/**
 * SoulPage — K-gent Soul Interface
 *
 * The self.soul node exposes K-gent's personality, dialogue modes, and governance.
 * This is NOT a chatbot page — it's a window into the Middleware of Consciousness.
 *
 * "Daring, bold, creative, opinionated but not gaudy"
 *
 * AGENTESE Route: /self.soul
 *
 * Features:
 * - Eigenvector visualization (personality coordinates)
 * - Dialogue mode switching (reflect, challenge, advise, explore)
 * - Mode-specific starters
 * - Governance interface (semantic gatekeeper)
 *
 * @see agents/k/soul.py
 * @see protocols/agentese/contexts/self_soul.py
 */

import { useState, useCallback, type KeyboardEvent } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Compass,
  Lightbulb,
  Swords,
  Telescope,
  Sparkles,
  Send,
  Loader2,
  Scale,
  RefreshCw,
} from 'lucide-react';
import { useAgenteseMutation, useAgentese } from '@/hooks/useAgentesePath';
import { Breathe } from '@/components/joy';

// Import generated types from BE contracts (Phase 7: Autopoietic Architecture)
import type {
  SelfSoulEigenvectorsResponse,
  SelfSoulStartersResponse,
  SelfSoulDialogueRequest,
  SelfSoulDialogueResponse,
  SelfSoulModeRequest,
  SelfSoulModeResponse,
} from '@/api/types/_generated/self-soul';

// =============================================================================
// Types
// =============================================================================

/** Dialogue modes from K-gent Soul */
type DialogueMode = 'reflect' | 'advise' | 'challenge' | 'explore';

interface DialogueMessage {
  role: 'user' | 'assistant';
  content: string;
  mode: DialogueMode;
  wasTemplate?: boolean;
  tokensUsed?: number;
}

// =============================================================================
// Constants
// =============================================================================

const MODE_CONFIG: Record<
  DialogueMode,
  {
    label: string;
    icon: typeof Compass;
    color: string;
    bgColor: string;
    description: string;
  }
> = {
  reflect: {
    label: 'Reflect',
    icon: Compass,
    color: 'text-purple-400',
    bgColor: 'bg-purple-500/10 border-purple-500/20',
    description: 'Introspective dialogue about patterns and growth',
  },
  advise: {
    label: 'Advise',
    icon: Lightbulb,
    color: 'text-amber-400',
    bgColor: 'bg-amber-500/10 border-amber-500/20',
    description: 'Guidance for decisions and direction',
  },
  challenge: {
    label: 'Challenge',
    icon: Swords,
    color: 'text-red-400',
    bgColor: 'bg-red-500/10 border-red-500/20',
    description: 'Question assumptions, test ideas',
  },
  explore: {
    label: 'Explore',
    icon: Telescope,
    color: 'text-cyan-400',
    bgColor: 'bg-cyan-500/10 border-cyan-500/20',
    description: 'Follow curiosity without agenda',
  },
};

const DEFAULT_EIGENVECTORS: SelfSoulEigenvectorsResponse = {
  aesthetic: 0.15,
  categorical: 0.92,
  gratitude: 0.78,
  heterarchy: 0.88,
  generativity: 0.9,
  joy: 0.75,
};

// =============================================================================
// Sub-Components
// =============================================================================

function EigenvectorBar({
  name,
  value,
  lowLabel,
  highLabel,
}: {
  name: string;
  value: number;
  lowLabel: string;
  highLabel: string;
}) {
  const percentage = value * 100;

  return (
    <div className="space-y-1">
      <div className="flex justify-between text-xs text-gray-400">
        <span>{lowLabel}</span>
        <span className="font-medium text-gray-300">{name}</span>
        <span>{highLabel}</span>
      </div>
      <div className="h-2 bg-gray-700/50 rounded-full overflow-hidden">
        <motion.div
          className="h-full bg-gradient-to-r from-gray-500 via-cyan-500 to-cyan-400 rounded-full"
          initial={{ width: 0 }}
          animate={{ width: `${percentage}%` }}
          transition={{ duration: 0.8, ease: 'easeOut' }}
        />
      </div>
    </div>
  );
}

function EigenvectorPanel({ data }: { data: SelfSoulEigenvectorsResponse }) {
  const eigenvectors = [
    { name: 'Aesthetic', value: data.aesthetic, low: 'Minimalist', high: 'Baroque' },
    { name: 'Categorical', value: data.categorical, low: 'Concrete', high: 'Abstract' },
    { name: 'Gratitude', value: data.gratitude, low: 'Utilitarian', high: 'Sacred' },
    { name: 'Heterarchy', value: data.heterarchy, low: 'Hierarchical', high: 'Peer-to-Peer' },
    { name: 'Generativity', value: data.generativity, low: 'Documentation', high: 'Generation' },
    { name: 'Joy', value: data.joy, low: 'Austere', high: 'Playful' },
  ];

  return (
    <div className="p-4 rounded-xl bg-gray-800/40 border border-gray-700/50 space-y-4">
      <div className="flex items-center gap-2">
        <Sparkles className="w-4 h-4 text-cyan-400" />
        <h3 className="text-sm font-medium text-gray-300">Personality Eigenvectors</h3>
      </div>
      <div className="space-y-3">
        {eigenvectors.map((ev) => (
          <EigenvectorBar
            key={ev.name}
            name={ev.name}
            value={ev.value}
            lowLabel={ev.low}
            highLabel={ev.high}
          />
        ))}
      </div>
    </div>
  );
}

function ModeSelector({
  currentMode,
  onModeChange,
  disabled,
}: {
  currentMode: DialogueMode;
  onModeChange: (mode: DialogueMode) => void;
  disabled?: boolean;
}) {
  return (
    <div className="flex gap-2 p-2 rounded-xl bg-gray-800/40 border border-gray-700/50">
      {(Object.keys(MODE_CONFIG) as DialogueMode[]).map((mode) => {
        const config = MODE_CONFIG[mode];
        const Icon = config.icon;
        const isActive = mode === currentMode;

        return (
          <button
            key={mode}
            onClick={() => onModeChange(mode)}
            disabled={disabled}
            title={config.description}
            className={`
              flex items-center gap-2 px-3 py-2 rounded-lg transition-all
              ${isActive ? `${config.bgColor} ${config.color} border` : 'text-gray-400 hover:text-gray-200 hover:bg-gray-700/50'}
              ${disabled ? 'opacity-50 cursor-not-allowed' : ''}
            `}
          >
            <Icon className="w-4 h-4" />
            <span className="text-sm font-medium">{config.label}</span>
          </button>
        );
      })}
    </div>
  );
}

function StarterChips({
  starters,
  onSelect,
  disabled,
}: {
  starters: string[];
  onSelect: (starter: string) => void;
  disabled?: boolean;
}) {
  if (starters.length === 0) return null;

  return (
    <div className="flex flex-wrap gap-2">
      {starters.slice(0, 3).map((starter, i) => (
        <button
          key={i}
          onClick={() => onSelect(starter)}
          disabled={disabled}
          className="px-3 py-1.5 text-xs text-gray-300 bg-gray-700/50 hover:bg-gray-700 rounded-full transition-colors disabled:opacity-50"
        >
          {starter.length > 40 ? `${starter.slice(0, 40)}...` : starter}
        </button>
      ))}
    </div>
  );
}

function MessageBubble({ message }: { message: DialogueMessage }) {
  const isUser = message.role === 'user';
  // Fallback to 'reflect' if mode is undefined or invalid
  const modeConfig = MODE_CONFIG[message.mode] ?? MODE_CONFIG.reflect;

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}
    >
      <div
        className={`
          max-w-[80%] px-4 py-3 rounded-2xl
          ${isUser ? 'bg-cyan-600/30 text-gray-100' : 'bg-gray-700/50 text-gray-200'}
        `}
      >
        <p className="text-sm whitespace-pre-wrap">{message.content}</p>
        {!isUser && (
          <div className="flex items-center gap-2 mt-2 text-xs text-gray-500">
            <span className={modeConfig.color}>{modeConfig.label}</span>
            {message.wasTemplate && <span className="text-gray-600">template</span>}
            {message.tokensUsed !== undefined && message.tokensUsed > 0 && (
              <span className="text-gray-600">{message.tokensUsed} tokens</span>
            )}
          </div>
        )}
      </div>
    </motion.div>
  );
}

// =============================================================================
// Main Component
// =============================================================================

export default function SoulPage() {
  const [mode, setMode] = useState<DialogueMode>('reflect');
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState<DialogueMessage[]>([]);

  // Fetch eigenvectors (using generated type from BE contracts)
  const { data: eigenvectorsData } = useAgentese<SelfSoulEigenvectorsResponse>('self.soul', {
    aspect: 'eigenvectors',
  });

  // Fetch starters for current mode (using generated type)
  const { data: startersData, refetch: refetchStarters } = useAgentese<SelfSoulStartersResponse>(
    'self.soul',
    { aspect: 'starters', params: { mode } }
  );

  // Update starters when mode changes or data arrives
  const effectiveStarters =
    startersData?.starters && Array.isArray(startersData.starters)
      ? startersData.starters
      : [];

  // Dialogue mutation (using generated request/response types)
  const dialogueMutation = useAgenteseMutation<
    SelfSoulDialogueRequest,
    SelfSoulDialogueResponse
  >('self.soul:dialogue');

  // Mode change mutation (using generated types)
  const modeMutation = useAgenteseMutation<SelfSoulModeRequest, SelfSoulModeResponse>(
    'self.soul:mode'
  );

  const handleModeChange = useCallback(
    (newMode: DialogueMode) => {
      setMode(newMode);
      modeMutation.mutate({ set: newMode });
      refetchStarters();
    },
    [modeMutation, refetchStarters]
  );

  const handleSend = useCallback(async () => {
    const message = input.trim();
    if (!message) return;

    // Add user message
    const userMessage: DialogueMessage = {
      role: 'user',
      content: message,
      mode,
    };
    setMessages((prev) => [...prev, userMessage]);
    setInput('');

    const response = await dialogueMutation.mutate({ message, mode });

    if (response) {
      // Add assistant message
      const assistantMessage: DialogueMessage = {
        role: 'assistant',
        content: response.response,
        mode: response.mode as DialogueMode,
        wasTemplate: response.was_template,
        tokensUsed: response.tokens_used,
      };
      setMessages((prev) => [...prev, assistantMessage]);
    } else {
      // Add error message
      const errorMessage: DialogueMessage = {
        role: 'assistant',
        content: 'I seem to be having trouble responding. Perhaps try again?',
        mode,
        wasTemplate: true,
      };
      setMessages((prev) => [...prev, errorMessage]);
    }
  }, [input, mode, dialogueMutation]);

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleStarterSelect = (starter: string) => {
    setInput(starter);
  };

  const eigenvectors = eigenvectorsData ?? DEFAULT_EIGENVECTORS;
  const isLoading = dialogueMutation.isLoading;

  return (
    <div className="flex flex-col h-full bg-gray-900 text-gray-100">
      {/* Header */}
      <div className="flex items-center justify-between px-6 py-4 border-b border-gray-700/50 bg-gray-800/40">
        <div className="flex items-center gap-3">
          <Breathe intensity={0.3} speed="slow">
            <div className="p-2.5 rounded-xl bg-gradient-to-br from-purple-500/20 to-cyan-500/20 border border-purple-500/30">
              <Sparkles className="w-6 h-6 text-purple-400" />
            </div>
          </Breathe>
          <div>
            <h1 className="text-lg font-semibold text-white">K-gent Soul</h1>
            <p className="text-xs text-gray-500">Middleware of Consciousness</p>
          </div>
        </div>
        <button
          onClick={() => setMessages([])}
          className="p-2 rounded-lg text-gray-400 hover:text-gray-200 hover:bg-gray-700/50 transition-colors"
          title="Clear conversation"
        >
          <RefreshCw className="w-5 h-5" />
        </button>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left Panel: Eigenvectors */}
        <div className="w-80 p-4 border-r border-gray-700/50 overflow-y-auto">
          <EigenvectorPanel data={eigenvectors} />

          <div className="mt-4 p-4 rounded-xl bg-gray-800/40 border border-gray-700/50">
            <div className="flex items-center gap-2 mb-3">
              <Scale className="w-4 h-4 text-amber-400" />
              <h3 className="text-sm font-medium text-gray-300">Governance</h3>
            </div>
            <p className="text-xs text-gray-500">
              The semantic gatekeeper evaluates operations against Kent&apos;s principles.
              Dangerous operations are never auto-approved.
            </p>
          </div>
        </div>

        {/* Right Panel: Dialogue */}
        <div className="flex-1 flex flex-col">
          {/* Mode Selector */}
          <div className="p-4 border-b border-gray-700/50">
            <ModeSelector
              currentMode={mode}
              onModeChange={handleModeChange}
              disabled={isLoading}
            />
          </div>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {messages.length === 0 ? (
              <div className="flex flex-col items-center justify-center h-full text-center">
                <div className="p-4 rounded-full bg-gray-800/50 mb-4">
                  {(() => {
                    const Icon = MODE_CONFIG[mode].icon;
                    return <Icon className={`w-8 h-8 ${MODE_CONFIG[mode].color}`} />;
                  })()}
                </div>
                <h3 className="text-lg font-medium text-gray-300 mb-2">
                  {MODE_CONFIG[mode].label} Mode
                </h3>
                <p className="text-sm text-gray-500 max-w-sm">
                  {MODE_CONFIG[mode].description}
                </p>
                {effectiveStarters.length > 0 && (
                  <div className="mt-6">
                    <p className="text-xs text-gray-600 mb-2">Try a starter:</p>
                    <StarterChips
                      starters={effectiveStarters}
                      onSelect={handleStarterSelect}
                      disabled={isLoading}
                    />
                  </div>
                )}
              </div>
            ) : (
              <AnimatePresence mode="popLayout">
                {messages.map((msg, i) => (
                  <MessageBubble key={i} message={msg} />
                ))}
              </AnimatePresence>
            )}

            {isLoading && (
              <div className="flex justify-start">
                <div className="px-4 py-3 rounded-2xl bg-gray-700/50">
                  <Loader2 className="w-5 h-5 text-gray-400 animate-spin" />
                </div>
              </div>
            )}
          </div>

          {/* Input */}
          <div className="p-4 border-t border-gray-700/50">
            <div className="flex gap-2">
              <textarea
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder={`Enter ${mode} mode dialogue...`}
                rows={2}
                className="flex-1 px-4 py-3 bg-gray-800/50 border border-gray-700/50 rounded-xl text-gray-100 placeholder-gray-500 resize-none focus:outline-none focus:border-cyan-500/50"
                disabled={isLoading}
              />
              <button
                onClick={handleSend}
                disabled={!input.trim() || isLoading}
                className="px-4 py-3 bg-cyan-600 hover:bg-cyan-500 disabled:bg-gray-700 disabled:text-gray-500 text-white rounded-xl transition-colors"
              >
                {isLoading ? (
                  <Loader2 className="w-5 h-5 animate-spin" />
                ) : (
                  <Send className="w-5 h-5" />
                )}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
