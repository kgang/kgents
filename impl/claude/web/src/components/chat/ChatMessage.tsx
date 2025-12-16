/**
 * ChatMessage: Individual message bubble in INHABIT chat.
 *
 * Types:
 * - user: Player suggestions
 * - citizen: Citizen responses
 * - refusal: Citizen declined suggestion
 * - system: System notifications
 */

import { cn } from '@/lib/utils';

export type MessageType = 'user' | 'citizen' | 'refusal' | 'system';

export interface ChatMessageProps {
  type: MessageType;
  content: string;
  timestamp: Date;
  innerVoice?: string;
  alignment?: number;
  wasForced?: boolean;
  citizenName?: string;
  className?: string;
}

export function ChatMessage({
  type,
  content,
  timestamp,
  innerVoice,
  alignment,
  wasForced,
  citizenName,
  className,
}: ChatMessageProps) {
  const isUser = type === 'user';
  const isSystem = type === 'system';
  const isRefusal = type === 'refusal';

  if (isSystem) {
    return (
      <div className={cn('flex justify-center', className)}>
        <div className="bg-town-surface/30 px-4 py-2 rounded-full text-xs text-gray-400 text-center max-w-[80%]">
          {content}
        </div>
      </div>
    );
  }

  return (
    <div
      className={cn(
        'flex',
        isUser ? 'justify-end' : 'justify-start',
        className
      )}
    >
      <div className={cn('max-w-[85%] space-y-1', isUser ? 'items-end' : 'items-start')}>
        {/* Sender label */}
        {!isUser && (
          <div className="flex items-center gap-2 text-xs text-gray-500 ml-1">
            <span>{citizenName || 'Citizen'}</span>
            {wasForced && (
              <span className="text-amber-400" title="This action was forced">
                ⚠️ Forced
              </span>
            )}
          </div>
        )}

        {/* Message bubble */}
        <div
          className={cn(
            'rounded-2xl px-4 py-2',
            isUser
              ? 'bg-town-highlight text-white rounded-br-sm'
              : isRefusal
                ? 'bg-red-500/20 text-red-200 border border-red-500/30 rounded-bl-sm'
                : 'bg-town-surface/50 text-gray-200 rounded-bl-sm'
          )}
        >
          <p className="text-sm whitespace-pre-wrap">{content}</p>
        </div>

        {/* Inner voice (citizen thoughts) */}
        {innerVoice && !isUser && (
          <InnerVoiceBubble content={innerVoice} wasForced={wasForced} />
        )}

        {/* Alignment indicator */}
        {alignment !== undefined && !isUser && (
          <AlignmentIndicator value={alignment} />
        )}

        {/* Timestamp */}
        <div
          className={cn(
            'text-xs text-gray-600',
            isUser ? 'text-right mr-1' : 'ml-1'
          )}
        >
          {formatTime(timestamp)}
        </div>
      </div>
    </div>
  );
}

// =============================================================================
// Sub-components
// =============================================================================

function InnerVoiceBubble({
  content,
  wasForced,
}: {
  content: string;
  wasForced?: boolean;
}) {
  return (
    <div
      className={cn(
        'flex items-start gap-2 ml-2 mt-1',
        wasForced ? 'opacity-70' : ''
      )}
    >
      <span className="text-purple-400 text-sm">💭</span>
      <p
        className={cn(
          'text-xs italic text-purple-300/80 bg-purple-500/10 px-3 py-1.5 rounded-lg',
          wasForced && 'text-amber-300/80 bg-amber-500/10'
        )}
      >
        {content}
      </p>
    </div>
  );
}

function AlignmentIndicator({ value }: { value: number }) {
  // Alignment: -1 to 1, where positive = aligned, negative = misaligned
  const isPositive = value > 0;
  const absValue = Math.abs(value);

  if (absValue < 0.1) return null;

  return (
    <div className="flex items-center gap-1 ml-2 mt-1">
      <span className="text-xs text-gray-500">Alignment:</span>
      <div className="flex items-center gap-0.5">
        {Array.from({ length: 5 }).map((_, i) => {
          const threshold = (i + 1) * 0.2;
          const isFilled = absValue >= threshold;
          return (
            <div
              key={i}
              className={cn(
                'w-1.5 h-3 rounded-sm',
                isFilled
                  ? isPositive
                    ? 'bg-green-500'
                    : 'bg-red-500'
                  : 'bg-gray-700'
              )}
            />
          );
        })}
      </div>
      <span
        className={cn(
          'text-xs font-mono',
          isPositive ? 'text-green-400' : 'text-red-400'
        )}
      >
        {isPositive ? '+' : ''}
        {value.toFixed(2)}
      </span>
    </div>
  );
}

// =============================================================================
// Helpers
// =============================================================================

function formatTime(date: Date): string {
  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

export default ChatMessage;
