/**
 * WalkCard - Renders a WALK-kind SceneNode
 *
 * Displays a Walk with:
 * - Name and goal
 * - Phase indicator
 * - Status badge
 * - Trace count
 * - Breathing animation when active
 *
 * @see protocols/agentese/projection/warp_converters.py - walk_to_scene()
 */

// React types auto-imported for JSX
import { BreathingContainer, type BreathingPeriod } from '@/components/genesis/BreathingContainer';
import { SERVO_BG_CLASSES, SERVO_BORDER_CLASSES } from './theme';

// =============================================================================
// Types (matching SceneNode content from warp_converters.py)
// =============================================================================

export interface WalkContent {
  walk_id: string;
  name: string;
  goal: string | null;
  phase: string;
  status: 'ACTIVE' | 'PAUSED' | 'COMPLETE' | 'ABANDONED';
  trace_count: number;
  participants: string[];
  duration_seconds: number;
  started_at: string;
}

export interface WalkCardProps {
  /** The walk content from SceneNode.content */
  content: WalkContent;
  /** Node label */
  label: string;
  /** Whether this card is selected */
  isSelected?: boolean;
  /** Click handler */
  onClick?: () => void;
  /** Additional className */
  className?: string;
}

// =============================================================================
// Status Configuration
// =============================================================================

const STATUS_STYLES: Record<WalkContent['status'], {
  bg: string;
  border: string;
  text: string;
  icon: string;
}> = {
  ACTIVE: {
    bg: SERVO_BG_CLASSES.living_green,
    border: SERVO_BORDER_CLASSES.living_green,
    text: 'text-emerald-200',
    icon: '▶',
  },
  PAUSED: {
    bg: SERVO_BG_CLASSES.amber_glow,
    border: SERVO_BORDER_CLASSES.amber_glow,
    text: 'text-amber-200',
    icon: '⏸',
  },
  COMPLETE: {
    bg: SERVO_BG_CLASSES.sage,
    border: SERVO_BORDER_CLASSES.sage,
    text: 'text-green-200',
    icon: '✓',
  },
  ABANDONED: {
    bg: SERVO_BG_CLASSES.twilight,
    border: SERVO_BORDER_CLASSES.twilight,
    text: 'text-purple-200',
    icon: '✗',
  },
};

// =============================================================================
// Helpers
// =============================================================================

function formatDuration(seconds: number): string {
  if (seconds < 60) return `${Math.round(seconds)}s`;
  if (seconds < 3600) return `${Math.round(seconds / 60)}m`;
  return `${Math.round(seconds / 3600)}h ${Math.round((seconds % 3600) / 60)}m`;
}

// =============================================================================
// Component
// =============================================================================

export function WalkCard({
  content,
  label,
  isSelected = false,
  onClick,
  className = '',
}: WalkCardProps) {
  // Graceful degradation: handle missing/malformed content
  const name = content?.name ?? label ?? 'Unnamed Walk';
  const goal = content?.goal ?? null;
  const phase = content?.phase ?? 'SENSE';
  const status = content?.status ?? 'ACTIVE';
  const trace_count = content?.trace_count ?? 0;
  const participants = content?.participants ?? [];
  const duration_seconds = content?.duration_seconds ?? 0;

  const statusStyle = STATUS_STYLES[status] ?? STATUS_STYLES.ACTIVE;
  const isActive = status === 'ACTIVE';

  // Determine breathing settings
  const breathingPeriod: BreathingPeriod = isActive ? 'normal' : 'calm';

  const card = (
    <div
      className={`
        relative rounded-lg border-2 p-3
        min-w-[180px] max-w-[280px]
        cursor-pointer select-none
        transition-all duration-200
        hover:scale-[1.02] hover:shadow-lg
        ${statusStyle.bg}
        ${statusStyle.border}
        ${isSelected ? 'ring-2 ring-white/50 scale-105' : ''}
        ${className}
      `}
      onClick={onClick}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => e.key === 'Enter' && onClick?.()}
    >
      {/* Status badge */}
      <div
        className={`
          absolute -top-2 -right-2 px-2 py-0.5 text-xs rounded-full
          font-medium ${statusStyle.text}
          bg-gray-900/80 border border-gray-700/50
        `}
      >
        {statusStyle.icon} {status}
      </div>

      {/* Name */}
      <div className="font-medium text-base text-white truncate pr-16">
        {name || label}
      </div>

      {/* Goal */}
      {goal && (
        <div className="text-sm text-gray-300 mt-1 line-clamp-2">
          {goal}
        </div>
      )}

      {/* Phase indicator */}
      <div className="mt-3 flex items-center gap-2">
        <div
          className={`
            px-2 py-0.5 text-xs rounded-full font-medium
            ${phase === 'SENSE' ? 'bg-blue-500/30 text-blue-200' : ''}
            ${phase === 'ACT' ? 'bg-amber-500/30 text-amber-200' : ''}
            ${phase === 'REFLECT' ? 'bg-purple-500/30 text-purple-200' : ''}
          `}
        >
          {phase}
        </div>
        <div className="text-xs text-gray-400">
          {trace_count} trace{trace_count !== 1 ? 's' : ''}
        </div>
      </div>

      {/* Footer: Duration and participants */}
      <div className="mt-2 flex items-center justify-between text-[10px] text-gray-400">
        <span>{formatDuration(duration_seconds)}</span>
        {participants.length > 0 && (
          <span>
            {participants.length} participant{participants.length !== 1 ? 's' : ''}
          </span>
        )}
      </div>

      {/* Active indicator glow */}
      {isActive && (
        <div className="absolute inset-0 rounded-lg pointer-events-none animate-pulse opacity-20 bg-emerald-400" />
      )}
    </div>
  );

  // Wrap with breathing animation if active
  if (isActive) {
    return (
      <BreathingContainer intensity="subtle" period={breathingPeriod}>
        {card}
      </BreathingContainer>
    );
  }

  return card;
}

WalkCard.displayName = 'WalkCard';
