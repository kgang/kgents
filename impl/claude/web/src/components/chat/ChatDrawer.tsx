/**
 * ChatDrawer: Slide-in panel for INHABIT mode interaction.
 *
 * Right-side drawer with:
 * - Chat messages (user suggestions + citizen responses)
 * - Consent debt indicator
 * - Force/apologize controls
 * - Inner voice toggle
 */

import { useState, useEffect, useRef, useCallback } from 'react';
import { inhabitApi } from '@/api/client';
import { cn } from '@/lib/utils';
import { ChatMessage, type MessageType } from './ChatMessage';
import { ChatInput } from './ChatInput';
import type { InhabitStatus, InhabitActionResult, ConsentState, ForceState } from '@/api/types';

export interface ChatDrawerProps {
  townId: string;
  citizenId: string;
  citizenName: string;
  isOpen: boolean;
  onClose: () => void;
  className?: string;
}

interface Message {
  id: string;
  type: MessageType;
  content: string;
  timestamp: Date;
  innerVoice?: string;
  alignment?: number;
  wasForced?: boolean;
}

export function ChatDrawer({
  townId,
  citizenId,
  citizenName,
  isOpen,
  onClose,
  className,
}: ChatDrawerProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [status, setStatus] = useState<InhabitStatus | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showInnerVoice, setShowInnerVoice] = useState(true);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Fetch initial status
  useEffect(() => {
    if (!isOpen || !townId || !citizenId) return;

    const fetchStatus = async () => {
      try {
        const res = await inhabitApi.getStatus(townId, citizenId);
        setStatus(res.data);

        // Add welcome message
        setMessages([
          {
            id: 'welcome',
            type: 'system',
            content: `You are now inhabiting ${citizenName}. Suggest actions or observe their inner voice.`,
            timestamp: new Date(),
          },
        ]);
      } catch (err) {
        console.error('Failed to fetch inhabit status:', err);
        setError('Failed to connect to citizen');
      }
    };

    fetchStatus();
  }, [isOpen, townId, citizenId, citizenName]);

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Handle suggestion
  const handleSuggest = useCallback(
    async (action: string) => {
      if (!status) return;

      const userMsg: Message = {
        id: `user-${Date.now()}`,
        type: 'user',
        content: action,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, userMsg]);
      setLoading(true);
      setError(null);

      try {
        const res = await inhabitApi.suggest(townId, citizenId, action);
        const result = res.data as InhabitActionResult;

        const responseMsg: Message = {
          id: `citizen-${Date.now()}`,
          type: result.success ? 'citizen' : 'refusal',
          content: result.message,
          timestamp: new Date(),
          innerVoice: generateInnerVoice(action, result.success),
          alignment: result.debt,
        };
        setMessages((prev) => [...prev, responseMsg]);

        // Update status
        const statusRes = await inhabitApi.getStatus(townId, citizenId);
        setStatus(statusRes.data);
      } catch (err) {
        setError('Failed to send suggestion');
      } finally {
        setLoading(false);
      }
    },
    [townId, citizenId, status]
  );

  // Handle force
  const handleForce = useCallback(
    async (action: string) => {
      if (!status || !status.force.enabled || status.force.remaining <= 0) return;

      const userMsg: Message = {
        id: `user-${Date.now()}`,
        type: 'user',
        content: `[FORCE] ${action}`,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, userMsg]);
      setLoading(true);

      try {
        const res = await inhabitApi.force(townId, citizenId, action);
        const result = res.data as InhabitActionResult;

        const responseMsg: Message = {
          id: `citizen-${Date.now()}`,
          type: 'citizen',
          content: result.message,
          timestamp: new Date(),
          innerVoice: generateForcedInnerVoice(),
          wasForced: true,
        };
        setMessages((prev) => [...prev, responseMsg]);

        // Update status
        const statusRes = await inhabitApi.getStatus(townId, citizenId);
        setStatus(statusRes.data);
      } catch (err) {
        setError('Failed to force action');
      } finally {
        setLoading(false);
      }
    },
    [townId, citizenId, status]
  );

  // Handle apologize
  const handleApologize = useCallback(async () => {
    if (!status) return;

    setLoading(true);
    try {
      await inhabitApi.apologize(townId, citizenId, 0.3);

      const sysMsg: Message = {
        id: `sys-${Date.now()}`,
        type: 'system',
        content: 'You apologized to the citizen. Consent debt reduced.',
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, sysMsg]);

      // Update status
      const statusRes = await inhabitApi.getStatus(townId, citizenId);
      setStatus(statusRes.data);
    } catch (err) {
      setError('Failed to apologize');
    } finally {
      setLoading(false);
    }
  }, [townId, citizenId, status]);

  // Handle end session
  const handleEnd = useCallback(async () => {
    try {
      await inhabitApi.end(townId, citizenId);
      onClose();
    } catch (err) {
      console.error('Failed to end session:', err);
      onClose(); // Close anyway
    }
  }, [townId, citizenId, onClose]);

  if (!isOpen) return null;

  return (
    <div
      className={cn(
        'fixed inset-y-0 right-0 w-96 bg-town-bg border-l border-town-accent/30',
        'flex flex-col shadow-2xl z-50 transform transition-transform duration-300',
        isOpen ? 'translate-x-0' : 'translate-x-full',
        className
      )}
    >
      {/* Header */}
      <ChatHeader
        citizenName={citizenName}
        status={status}
        showInnerVoice={showInnerVoice}
        onToggleInnerVoice={() => setShowInnerVoice(!showInnerVoice)}
        onEnd={handleEnd}
        onClose={onClose}
      />

      {/* Consent Status Bar */}
      {status && <ConsentBar consent={status.consent} force={status.force} />}

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((msg) => (
          <ChatMessage
            key={msg.id}
            type={msg.type}
            content={msg.content}
            timestamp={msg.timestamp}
            innerVoice={showInnerVoice ? msg.innerVoice : undefined}
            alignment={msg.alignment}
            wasForced={msg.wasForced}
            citizenName={citizenName}
          />
        ))}
        {loading && (
          <div className="flex items-center gap-2 text-gray-500 text-sm">
            <span className="animate-pulse">Thinking...</span>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Error */}
      {error && (
        <div className="px-4 py-2 bg-red-500/10 text-red-400 text-sm">{error}</div>
      )}

      {/* Input */}
      <ChatInput
        onSuggest={handleSuggest}
        onForce={handleForce}
        onApologize={handleApologize}
        canForce={status?.force.enabled && (status?.force.remaining ?? 0) > 0}
        canApologize={status?.consent.debt !== undefined && status.consent.debt > 0}
        disabled={loading || status?.expired}
      />
    </div>
  );
}

// =============================================================================
// Sub-components
// =============================================================================

interface ChatHeaderProps {
  citizenName: string;
  status: InhabitStatus | null;
  showInnerVoice: boolean;
  onToggleInnerVoice: () => void;
  onEnd: () => void;
  onClose: () => void;
}

function ChatHeader({
  citizenName,
  status,
  showInnerVoice,
  onToggleInnerVoice,
  onEnd,
  onClose,
}: ChatHeaderProps) {
  return (
    <div className="p-4 border-b border-town-accent/30">
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-full bg-town-highlight/20 flex items-center justify-center">
            🎭
          </div>
          <div>
            <h2 className="font-bold">{citizenName}</h2>
            <p className="text-xs text-gray-400">INHABIT Mode</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={onToggleInnerVoice}
            className={cn(
              'p-2 rounded transition-colors text-sm',
              showInnerVoice
                ? 'bg-purple-500/20 text-purple-400'
                : 'text-gray-500 hover:text-gray-300'
            )}
            title={showInnerVoice ? 'Hide inner voice' : 'Show inner voice'}
          >
            💭
          </button>
          <button
            onClick={onEnd}
            className="px-3 py-1 text-xs bg-red-500/20 text-red-400 rounded hover:bg-red-500/30 transition-colors"
          >
            End
          </button>
          <button
            onClick={onClose}
            className="p-2 hover:bg-town-accent/20 rounded transition-colors"
          >
            ✕
          </button>
        </div>
      </div>

      {/* Session info */}
      {status && (
        <div className="flex items-center gap-4 text-xs text-gray-500">
          <span>Tier: {status.tier}</span>
          <span>Actions: {status.actions_count}</span>
          {status.time_remaining > 0 && (
            <span>Time: {Math.floor(status.time_remaining / 60)}m</span>
          )}
        </div>
      )}
    </div>
  );
}

interface ConsentBarProps {
  consent: ConsentState;
  force: ForceState;
}

function ConsentBar({ consent, force }: ConsentBarProps) {
  const debtPercent = Math.min(consent.debt * 100, 100);
  const isAtRupture = consent.at_rupture;

  return (
    <div className="px-4 py-2 bg-town-surface/30 border-b border-town-accent/20">
      <div className="flex items-center justify-between mb-1">
        <span className="text-xs text-gray-400">Consent Debt</span>
        <span className="text-xs font-mono">
          {consent.debt.toFixed(2)}
          {isAtRupture && (
            <span className="ml-2 text-red-400">⚠️ At Rupture</span>
          )}
        </span>
      </div>
      <div className="h-1.5 bg-town-surface rounded-full overflow-hidden">
        <div
          className={cn(
            'h-full transition-all',
            debtPercent > 70 ? 'bg-red-500' : debtPercent > 40 ? 'bg-yellow-500' : 'bg-green-500'
          )}
          style={{ width: `${debtPercent}%` }}
        />
      </div>

      {/* Force tokens */}
      <div className="flex items-center justify-between mt-2 text-xs">
        <span className="text-gray-500">Force Tokens</span>
        <div className="flex gap-1">
          {Array.from({ length: force.limit }).map((_, i) => (
            <div
              key={i}
              className={cn(
                'w-4 h-4 rounded',
                i < force.remaining
                  ? 'bg-amber-500'
                  : 'bg-gray-700'
              )}
            />
          ))}
        </div>
      </div>
    </div>
  );
}

// =============================================================================
// Helpers
// =============================================================================

function generateInnerVoice(_action: string, accepted: boolean): string {
  const acceptedThoughts = [
    'This aligns with my values...',
    'I can see the wisdom in this approach.',
    "Yes, this feels right to me.",
    'My instincts say this is a good path.',
  ];

  const refusedThoughts = [
    "Something about this doesn't sit well with me...",
    "I need to trust my own judgment here.",
    "This conflicts with what I believe.",
    "I can't do this in good conscience.",
  ];

  const thoughts = accepted ? acceptedThoughts : refusedThoughts;
  return thoughts[Math.floor(Math.random() * thoughts.length)];
}

function generateForcedInnerVoice(): string {
  const thoughts = [
    "I... I suppose I must comply...",
    "*reluctantly* ...as you wish.",
    "My agency feels compromised...",
    "This wasn't my choice...",
  ];
  return thoughts[Math.floor(Math.random() * thoughts.length)];
}

export default ChatDrawer;
