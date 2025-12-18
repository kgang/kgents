/**
 * SessionPolynomial - Inline SENSE -> ACT -> REFLECT State Machine
 *
 * The session cycle lives INSIDE the garden, not separate.
 * Shows the polynomial state machine with valid transitions.
 *
 * @see spec/protocols/2d-renaissance.md - Section 3.4C
 * @see docs/creative/visual-system.md - NO EMOJIS policy
 */

import { Eye, Zap, MessageSquare, ChevronRight, RotateCcw } from 'lucide-react';
import { Breathe, celebrate } from '@/components/joy';
import type { GardenerSessionState, GardenerPhase } from '@/api/types';

// =============================================================================
// Types
// =============================================================================

export interface SessionPolynomialProps {
  /** Session state from AGENTESE */
  session: GardenerSessionState;
  /** Callback when phase changes */
  onPhaseChange?: (phase: GardenerPhase) => void;
  /** Compact mode for mobile */
  compact?: boolean;
  /** Custom class name */
  className?: string;
}

// =============================================================================
// Phase Configuration (Living Earth + Lucide Icons)
// =============================================================================

const PHASES: {
  id: GardenerPhase;
  Icon: typeof Eye;
  label: string;
  action: string;
  color: string;
  bgColor: string;
}[] = [
  {
    id: 'SENSE',
    Icon: Eye,
    label: 'Sense',
    action: 'Gathering context',
    color: '#06B6D4', // Cyan
    bgColor: '#06B6D420',
  },
  {
    id: 'ACT',
    Icon: Zap,
    label: 'Act',
    action: 'Executing intent',
    color: '#D4A574', // Amber
    bgColor: '#D4A57420',
  },
  {
    id: 'REFLECT',
    Icon: MessageSquare,
    label: 'Reflect',
    action: 'Consolidating',
    color: '#8B5CF6', // Violet (existing)
    bgColor: '#8B5CF620',
  },
];

// =============================================================================
// Main Component
// =============================================================================

export function SessionPolynomial({
  session,
  onPhaseChange,
  compact = false,
  className = '',
}: SessionPolynomialProps) {
  const currentPhaseIndex = PHASES.findIndex((p) => p.id === session.phase);

  // Handle phase advance
  const handleAdvance = (toPhase: GardenerPhase) => {
    // Celebrate cycle completion
    if (toPhase === 'SENSE' && session.phase === 'REFLECT') {
      celebrate({ intensity: 'normal' });
    }
    onPhaseChange?.(toPhase);
  };

  // Valid next phases
  const validNextPhases: GardenerPhase[] =
    session.phase === 'SENSE'
      ? ['ACT']
      : session.phase === 'ACT'
        ? ['REFLECT', 'SENSE']
        : ['SENSE'];

  return (
    <div className={`bg-[#4A3728]/30 rounded-lg ${compact ? 'p-3' : 'p-4'} ${className}`}>
      {/* Header */}
      <h3
        className={`font-semibold text-[#AB9080] uppercase tracking-wide mb-3 ${
          compact ? 'text-[10px]' : 'text-xs'
        }`}
      >
        Session Cycle
      </h3>

      {/* Phase Diagram */}
      <div className={`flex items-center justify-center ${compact ? 'gap-1' : 'gap-2'} mb-4`}>
        {PHASES.map((phase, index) => {
          const isCurrent = phase.id === session.phase;
          const isValid = validNextPhases.includes(phase.id);
          const isPast = index < currentPhaseIndex;

          return (
            <div key={phase.id} className="flex items-center">
              {/* Phase Node */}
              <PhaseNode
                phase={phase}
                isCurrent={isCurrent}
                isValid={isValid}
                isPast={isPast}
                compact={compact}
                onClick={isValid && onPhaseChange ? () => handleAdvance(phase.id) : undefined}
              />

              {/* Arrow to next (except last) */}
              {index < PHASES.length - 1 && (
                <ChevronRight
                  className={`${compact ? 'w-4 h-4' : 'w-5 h-5'} mx-1`}
                  style={{
                    color: index < currentPhaseIndex ? '#8BAB8B' : '#4A3728',
                  }}
                />
              )}
            </div>
          );
        })}

        {/* Cycle arrow back */}
        <div className={`flex items-center ${compact ? 'ml-1' : 'ml-2'}`}>
          <RotateCcw
            className={`${compact ? 'w-4 h-4' : 'w-5 h-5'}`}
            style={{
              color: session.phase === 'REFLECT' ? '#8B5CF6' : '#4A3728',
            }}
          />
        </div>
      </div>

      {/* Current Phase Info */}
      <div className="text-center mb-4">
        <p className={`text-[#F5E6D3] ${compact ? 'text-xs' : 'text-sm'}`}>
          {PHASES[currentPhaseIndex]?.action}
        </p>
        {validNextPhases.length > 0 && (
          <p className={`text-[#6B4E3D] mt-1 ${compact ? 'text-[10px]' : 'text-xs'}`}>
            Valid: [{validNextPhases.join(', ')}]
          </p>
        )}
      </div>

      {/* Stats Row */}
      <div className={`grid ${compact ? 'grid-cols-4 gap-1' : 'grid-cols-3 gap-3'}`}>
        {[
          { label: 'Artifacts', value: session.artifacts_count, color: '#8BAB8B' },
          { label: 'Learnings', value: session.learnings_count, color: '#8B5CF6' },
          { label: 'Cycles', value: session.reflect_count, color: '#06B6D4' },
          ...(compact ? [] : [{ label: 'Senses', value: session.sense_count, color: '#6B4E3D' }]),
        ].map((stat) => (
          <div key={stat.label} className="text-center">
            <div
              className={`font-bold ${compact ? 'text-base' : 'text-xl'}`}
              style={{ color: stat.color }}
            >
              {stat.value}
            </div>
            <div className={`text-[#6B4E3D] ${compact ? 'text-[10px]' : 'text-xs'}`}>
              {stat.label}
            </div>
          </div>
        ))}
      </div>

      {/* Action Buttons */}
      {onPhaseChange && !compact && (
        <div className="flex flex-wrap gap-2 mt-4 pt-3 border-t border-[#4A3728]">
          {session.phase === 'SENSE' && (
            <ActionButton
              label="Advance to Act"
              onClick={() => handleAdvance('ACT')}
              color="#D4A574"
            />
          )}
          {session.phase === 'ACT' && (
            <>
              <ActionButton
                label="Advance to Reflect"
                onClick={() => handleAdvance('REFLECT')}
                color="#8B5CF6"
              />
              <ActionButton
                label="Back to Sense"
                onClick={() => handleAdvance('SENSE')}
                color="#6B4E3D"
                secondary
              />
            </>
          )}
          {session.phase === 'REFLECT' && (
            <ActionButton
              label="Start New Cycle"
              onClick={() => handleAdvance('SENSE')}
              color="#06B6D4"
            />
          )}
        </div>
      )}
    </div>
  );
}

// =============================================================================
// Phase Node Component
// =============================================================================

interface PhaseNodeProps {
  phase: (typeof PHASES)[number];
  isCurrent: boolean;
  isValid: boolean;
  isPast: boolean;
  compact: boolean;
  onClick?: () => void;
}

function PhaseNode({ phase, isCurrent, isValid, isPast, compact, onClick }: PhaseNodeProps) {
  const { Icon, label, color, bgColor } = phase;

  const size = compact ? 'w-10 h-10' : 'w-14 h-14';
  const iconSize = compact ? 'w-4 h-4' : 'w-6 h-6';

  const baseClasses = `
    ${size} rounded-full flex flex-col items-center justify-center
    transition-all duration-300 border-2
    ${onClick && isValid ? 'cursor-pointer hover:scale-110' : ''}
    ${isCurrent ? 'ring-2 ring-offset-2 ring-offset-[#2D1B14]' : ''}
  `;

  const content = (
    <div
      className={baseClasses}
      style={{
        backgroundColor: isCurrent ? bgColor : isPast ? `${color}10` : '#2D1B1480',
        borderColor: isCurrent ? color : isPast ? `${color}40` : '#4A3728',
        // Ring color via CSS variable for Tailwind
        ['--tw-ring-color' as string]: isCurrent ? color : undefined,
      }}
      onClick={onClick}
      role={onClick ? 'button' : undefined}
      tabIndex={onClick ? 0 : undefined}
      onKeyDown={
        onClick
          ? (e) => {
              if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                onClick();
              }
            }
          : undefined
      }
    >
      <Icon className={iconSize} style={{ color: isCurrent || isPast ? color : '#6B4E3D' }} />
      {!compact && (
        <span
          className="text-[10px] mt-0.5"
          style={{ color: isCurrent || isPast ? color : '#6B4E3D' }}
        >
          {label}
        </span>
      )}
    </div>
  );

  // Wrap current phase in Breathe
  if (isCurrent) {
    return (
      <Breathe intensity={0.3} speed="slow">
        {content}
      </Breathe>
    );
  }

  return content;
}

// =============================================================================
// Action Button Component
// =============================================================================

interface ActionButtonProps {
  label: string;
  onClick: () => void;
  color: string;
  secondary?: boolean;
}

function ActionButton({ label, onClick, color, secondary = false }: ActionButtonProps) {
  return (
    <button
      onClick={onClick}
      className={`
        px-3 py-1.5 rounded-lg text-sm font-medium transition-all
        ${
          secondary
            ? 'bg-transparent border border-current hover:bg-current/10'
            : 'hover:brightness-110'
        }
      `}
      style={{
        backgroundColor: secondary ? 'transparent' : color,
        color: secondary ? color : '#F5E6D3',
        borderColor: secondary ? color : 'transparent',
      }}
    >
      {label}
    </button>
  );
}

export default SessionPolynomial;
