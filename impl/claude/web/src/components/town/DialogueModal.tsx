/**
 * DialogueModal: Chat interface for citizen conversations.
 *
 * Phase 5: Town End-to-End (2D Renaissance)
 *
 * Features:
 * - Living Earth aesthetic (warm earth tones, organic feel)
 * - Mobile: BottomDrawer pattern
 * - Desktop: Centered modal
 * - Real-time conversation via AGENTESE
 * - LLM-generated citizen responses
 *
 * @see spec/protocols/2d-renaissance.md §5.4
 */

import { useState, useRef, useEffect, useCallback } from 'react';
import { useCitizenDialogue } from '@/hooks/useCitizenDialogue';
import { BottomDrawer } from '@/components/elastic/BottomDrawer';
import { InlineError, PersonalityLoading } from '@/components/joy';
import { celebrate } from '@/components/joy';
import { cn } from '@/lib/utils';
import { GREEN, GLOW, DARK_EARTH } from '@/constants/livingEarth';
import type { TurnSummary } from '@/api/types';

// =============================================================================
// Types
// =============================================================================

export interface DialogueModalProps {
  /** Town ID */
  townId: string;

  /** Citizen ID or name */
  citizenId: string;

  /** Citizen display name */
  citizenName: string;

  /** Citizen archetype for color coding */
  archetype: string;

  /** Close callback */
  onClose: () => void;

  /** Whether to use mobile layout */
  isMobile?: boolean;
}

// =============================================================================
// Archetype Colors (from Town patterns)
// =============================================================================

const ARCHETYPE_COLORS: Record<string, string> = {
  Builder: '#3b82f6', // blue
  Trader: '#f59e0b', // amber
  Healer: '#22c55e', // green
  Scholar: '#8b5cf6', // purple
  Watcher: '#06b6d4', // cyan
};

function getArchetypeColor(archetype: string): string {
  return ARCHETYPE_COLORS[archetype] || GLOW.amber;
}

// =============================================================================
// Message Component
// =============================================================================

interface MessageProps {
  turn: TurnSummary;
  archetype: string;
  citizenName: string;
}

function Message({ turn, archetype, citizenName }: MessageProps) {
  const isUser = turn.role === 'user';

  return (
    <div
      className={cn(
        'flex flex-col max-w-[85%] mb-3',
        isUser ? 'ml-auto items-end' : 'mr-auto items-start'
      )}
    >
      {/* Sender label */}
      <span className="text-xs text-gray-400 mb-1 px-1">{isUser ? 'You' : citizenName}</span>

      {/* Message bubble */}
      <div
        className={cn('px-4 py-2.5 rounded-2xl', isUser ? 'rounded-br-md' : 'rounded-bl-md')}
        style={{
          backgroundColor: isUser ? DARK_EARTH.wood : DARK_EARTH.bark,
          borderLeft: isUser ? 'none' : `3px solid ${getArchetypeColor(archetype)}`,
          borderRight: isUser ? `3px solid ${GLOW.amber}` : 'none',
        }}
      >
        <p className="text-sm text-white whitespace-pre-wrap">{turn.content}</p>
      </div>

      {/* Timestamp */}
      <span className="text-[10px] text-gray-500 mt-1 px-1">
        {new Date(turn.created_at).toLocaleTimeString([], {
          hour: '2-digit',
          minute: '2-digit',
        })}
      </span>
    </div>
  );
}

// =============================================================================
// Input Area Component
// =============================================================================

interface InputAreaProps {
  onSend: (content: string) => void;
  isLoading: boolean;
  disabled: boolean;
}

function InputArea({ onSend, isLoading, disabled }: InputAreaProps) {
  const [content, setContent] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleSend = useCallback(() => {
    const trimmed = content.trim();
    if (!trimmed || isLoading || disabled) return;

    onSend(trimmed);
    setContent('');

    // Refocus textarea
    textareaRef.current?.focus();
  }, [content, isLoading, disabled, onSend]);

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        handleSend();
      }
    },
    [handleSend]
  );

  return (
    <div
      className="flex gap-2 p-3 border-t"
      style={{
        backgroundColor: DARK_EARTH.soil,
        borderColor: DARK_EARTH.clay,
      }}
    >
      <textarea
        ref={textareaRef}
        value={content}
        onChange={(e) => setContent(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="Type a message..."
        disabled={disabled || isLoading}
        rows={1}
        className={cn(
          'flex-1 px-3 py-2 rounded-lg resize-none',
          'text-white placeholder-gray-500',
          'focus:outline-none focus:ring-2 transition-all',
          'disabled:opacity-50 disabled:cursor-not-allowed'
        )}
        style={{
          backgroundColor: DARK_EARTH.bark,
          borderColor: DARK_EARTH.clay,
          border: `1px solid ${DARK_EARTH.clay}`,
        }}
        onFocus={(e) => {
          e.currentTarget.style.borderColor = GREEN.sage;
          e.currentTarget.style.boxShadow = `0 0 0 2px ${GREEN.sage}40`;
        }}
        onBlur={(e) => {
          e.currentTarget.style.borderColor = DARK_EARTH.clay;
          e.currentTarget.style.boxShadow = 'none';
        }}
      />

      <button
        onClick={handleSend}
        disabled={!content.trim() || isLoading || disabled}
        className={cn(
          'px-4 py-2 rounded-lg font-medium transition-all',
          'disabled:opacity-50 disabled:cursor-not-allowed',
          'min-w-[80px]'
        )}
        style={{
          backgroundColor: isLoading ? GLOW.amber : GREEN.sage,
          color: 'white',
        }}
      >
        {isLoading ? <span className="inline-block animate-pulse">...</span> : 'Send'}
      </button>
    </div>
  );
}

// =============================================================================
// Modal Content (Shared between mobile and desktop)
// =============================================================================

interface ModalContentProps {
  citizenId: string;
  citizenName: string;
  archetype: string;
  onClose: () => void;
}

function ModalContent({ citizenId, citizenName, archetype, onClose }: ModalContentProps) {
  const { conversation, isLoading, isStarting, error, startConversation, sendMessage } =
    useCitizenDialogue(citizenId);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const hasStartedRef = useRef(false);
  const hasCelebratedRef = useRef(false);

  // Auto-start conversation on mount
  useEffect(() => {
    if (!hasStartedRef.current) {
      hasStartedRef.current = true;
      startConversation();
    }
  }, [startConversation]);

  // Celebrate on first successful message exchange
  useEffect(() => {
    if (conversation && conversation.turns.length >= 2 && !hasCelebratedRef.current) {
      hasCelebratedRef.current = true;
      celebrate({ intensity: 'subtle' });
    }
  }, [conversation]);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    if (messagesEndRef.current && typeof messagesEndRef.current.scrollIntoView === 'function') {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [conversation?.turns.length]);

  const handleSend = useCallback(
    async (content: string) => {
      await sendMessage(content);
    },
    [sendMessage]
  );

  // Starting state
  if (isStarting && !conversation) {
    return (
      <div className="flex-1 flex items-center justify-center p-8">
        <PersonalityLoading jewel="coalition" size="md" action="manifest" />
      </div>
    );
  }

  // Error state
  if (error && !conversation) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center p-8 gap-4">
        <InlineError message={error} />
        <button
          onClick={() => {
            hasStartedRef.current = false;
            startConversation();
          }}
          className="px-4 py-2 rounded-lg text-white transition-colors"
          style={{ backgroundColor: GREEN.sage }}
        >
          Try Again
        </button>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full">
      {/* Header with archetype badge */}
      <div
        className="flex items-center gap-3 px-4 py-3 border-b"
        style={{
          backgroundColor: DARK_EARTH.bark,
          borderColor: DARK_EARTH.clay,
        }}
      >
        <div
          className="w-10 h-10 rounded-full flex items-center justify-center text-white font-bold"
          style={{ backgroundColor: getArchetypeColor(archetype) }}
        >
          {citizenName[0]?.toUpperCase()}
        </div>
        <div>
          <h3 className="font-semibold text-white">{citizenName}</h3>
          <span
            className="text-xs px-2 py-0.5 rounded-full"
            style={{
              backgroundColor: `${getArchetypeColor(archetype)}30`,
              color: getArchetypeColor(archetype),
            }}
          >
            {archetype}
          </span>
        </div>
        <button
          onClick={onClose}
          className="ml-auto text-gray-400 hover:text-white p-2 rounded-lg hover:bg-gray-700 transition-colors"
          style={{ minWidth: 48, minHeight: 48 }}
          aria-label="Close dialogue"
        >
          ✕
        </button>
      </div>

      {/* Messages area */}
      <div className="flex-1 overflow-y-auto p-4" style={{ backgroundColor: DARK_EARTH.soil }}>
        {conversation?.turns.length === 0 && (
          <div className="text-center text-gray-400 py-8">
            <p>Start a conversation with {citizenName}.</p>
            <p className="text-sm mt-2">
              They&apos;ll respond based on their personality and memories.
            </p>
          </div>
        )}

        {conversation?.turns.map((turn) => (
          <Message key={turn.id} turn={turn} archetype={archetype} citizenName={citizenName} />
        ))}

        {/* Loading indicator for citizen response */}
        {isLoading && (
          <div className="flex items-center gap-2 text-gray-400 mb-3">
            <div
              className="w-8 h-8 rounded-full flex items-center justify-center animate-pulse"
              style={{ backgroundColor: getArchetypeColor(archetype) }}
            >
              {citizenName[0]?.toUpperCase()}
            </div>
            <span className="text-sm">{citizenName} is thinking...</span>
          </div>
        )}

        {/* Error inline */}
        {error && conversation && (
          <div className="text-center py-2">
            <InlineError message={error} />
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input area */}
      <InputArea onSend={handleSend} isLoading={isLoading} disabled={!conversation} />
    </div>
  );
}

// =============================================================================
// Main Component
// =============================================================================

export function DialogueModal({
  townId: _townId,
  citizenId,
  citizenName,
  archetype,
  onClose,
  isMobile = false,
}: DialogueModalProps) {
  // Note: townId is passed for future multi-town support but not currently used
  void _townId;
  // Detect mobile if not explicitly set
  const [detectedMobile, setDetectedMobile] = useState(false);

  useEffect(() => {
    const checkMobile = () => {
      setDetectedMobile(window.innerWidth < 768);
    };
    checkMobile();
    window.addEventListener('resize', checkMobile);
    return () => window.removeEventListener('resize', checkMobile);
  }, []);

  const useMobileLayout = isMobile || detectedMobile;

  // Mobile: Use BottomDrawer
  if (useMobileLayout) {
    return (
      <BottomDrawer
        isOpen={true}
        onClose={onClose}
        title={`Talking to ${citizenName}`}
        maxHeightPercent={85}
        className="!bg-transparent"
        contentClassName="!p-0"
      >
        <div className="h-[70vh]" style={{ backgroundColor: DARK_EARTH.soil }}>
          <ModalContent
            citizenId={citizenId}
            citizenName={citizenName}
            archetype={archetype}
            onClose={onClose}
          />
        </div>
      </BottomDrawer>
    );
  }

  // Desktop: Centered modal
  return (
    <>
      {/* Backdrop */}
      <div className="fixed inset-0 bg-black/60 z-40" onClick={onClose} aria-hidden="true" />

      {/* Modal */}
      <div
        className="fixed inset-0 z-50 flex items-center justify-center p-4"
        role="dialog"
        aria-modal="true"
        aria-label={`Dialogue with ${citizenName}`}
      >
        <div
          className="w-full max-w-lg h-[600px] rounded-xl shadow-2xl overflow-hidden flex flex-col animate-in fade-in zoom-in-95 duration-200"
          style={{ backgroundColor: DARK_EARTH.soil }}
        >
          <ModalContent
            citizenId={citizenId}
            citizenName={citizenName}
            archetype={archetype}
            onClose={onClose}
          />
        </div>
      </div>
    </>
  );
}

export default DialogueModal;
