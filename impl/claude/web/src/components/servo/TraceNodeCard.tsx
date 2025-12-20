/**
 * TraceNodeCard - Renders a TRACE-kind SceneNode
 *
 * Displays a TraceNode with:
 * - Stimulus preview as header
 * - Response content
 * - Phase indicator
 * - Breathing animation when active
 *
 * @see protocols/agentese/projection/warp_converters.py - trace_node_to_scene()
 */

import { BreathingContainer, type BreathingPeriod } from '@/components/genesis/BreathingContainer';
import { SERVO_BG_CLASSES, SERVO_BORDER_CLASSES } from './theme';

// =============================================================================
// Types (matching SceneNode content from warp_converters.py)
// =============================================================================

export interface TraceNodeContent {
  trace_id: string;
  origin: string;
  stimulus: {
    kind: string;
    content: string;
    source: string;
  };
  response: {
    kind: string;
    content: string;
    success: boolean;
  };
  timestamp: string;
  phase: string | null;
  tags: string[];
}

export interface TraceNodeCardProps {
  /** The trace content from SceneNode.content */
  content: TraceNodeContent;
  /** Node label (truncated stimulus) */
  label: string;
  /** Whether the node should breathe */
  breathing?: boolean;
  /** Whether this card is selected */
  isSelected?: boolean;
  /** Click handler */
  onClick?: () => void;
  /** Additional className */
  className?: string;
}

// =============================================================================
// Component
// =============================================================================

export function TraceNodeCard({
  content,
  label,
  breathing = false,
  isSelected = false,
  onClick,
  className = '',
}: TraceNodeCardProps) {
  // Graceful degradation: handle missing/malformed content
  const origin = content?.origin ?? 'unknown';
  const response = content?.response ?? { kind: 'unknown', content: '', success: true };
  const phase = content?.phase ?? null;
  const tags = content?.tags ?? [];
  const success = response?.success ?? true;

  // Determine breathing period based on success
  const breathingPeriod: BreathingPeriod = success ? 'calm' : 'urgent';

  const card = (
    <div
      className={`
        relative rounded-lg border-2 px-3 py-2
        min-w-[140px] max-w-[220px]
        cursor-pointer select-none
        transition-all duration-200
        hover:scale-[1.02] hover:shadow-lg
        ${SERVO_BG_CLASSES.sage}
        ${SERVO_BORDER_CLASSES.sage}
        ${isSelected ? 'ring-2 ring-white/50 scale-105' : ''}
        ${!success ? 'border-red-500/50' : ''}
        ${className}
      `}
      onClick={onClick}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => e.key === 'Enter' && onClick?.()}
    >
      {/* Origin badge */}
      <div className="absolute -top-2 -right-2 px-1.5 py-0.5 text-[10px] rounded-full bg-emerald-900 text-emerald-200 border border-emerald-700/50">
        {origin}
      </div>

      {/* Label (truncated stimulus) */}
      <div className="font-medium text-sm text-white truncate pr-8">
        {label}
      </div>

      {/* Response preview */}
      <div className="text-xs text-gray-300 mt-1 line-clamp-2">
        {response.content.slice(0, 80)}
        {response.content.length > 80 ? '...' : ''}
      </div>

      {/* Phase indicator */}
      {phase && (
        <div className="mt-2 flex items-center gap-1">
          <span
            className={`
              inline-block w-2 h-2 rounded-full
              ${phase === 'SENSE' ? 'bg-blue-400' : ''}
              ${phase === 'ACT' ? 'bg-amber-400' : ''}
              ${phase === 'REFLECT' ? 'bg-purple-400' : ''}
            `}
          />
          <span className="text-[10px] text-gray-400">{phase}</span>
        </div>
      )}

      {/* Tags */}
      {tags.length > 0 && (
        <div className="mt-1 flex flex-wrap gap-1">
          {tags.slice(0, 3).map((tag) => (
            <span
              key={tag}
              className="text-[9px] px-1 py-0.5 rounded bg-emerald-900/50 text-emerald-300"
            >
              {tag}
            </span>
          ))}
          {tags.length > 3 && (
            <span className="text-[9px] text-gray-500">+{tags.length - 3}</span>
          )}
        </div>
      )}

      {/* Success/Error indicator */}
      <div
        className={`
          absolute -bottom-1 left-1/2 transform -translate-x-1/2
          w-2 h-2 rounded-full
          ${success ? 'bg-emerald-400' : 'bg-red-400'}
        `}
      />
    </div>
  );

  // Wrap with breathing animation if enabled
  if (breathing) {
    return (
      <BreathingContainer
        intensity={success ? 'subtle' : 'emphatic'}
        period={breathingPeriod}
      >
        {card}
      </BreathingContainer>
    );
  }

  return card;
}

TraceNodeCard.displayName = 'TraceNodeCard';
