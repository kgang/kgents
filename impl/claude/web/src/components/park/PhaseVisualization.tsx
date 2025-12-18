/**
 * PhaseVisualization: Crisis phase state machine with embedded polynomial visualization.
 *
 * Phase 3 of park-town-design-overhaul: Replaces the simple PhaseTransition
 * with a rich state machine visualization showing:
 * - Current phase with glow effect
 * - Valid transitions derived from polynomial directions
 * - Teaching callouts explaining the crisis flow
 * - Transition history trace
 *
 * @see plans/park-town-design-overhaul.md (Phase 3: Park Enhancement)
 * @see spec/park/index.md (polynomial specification)
 */

import { useMemo } from 'react';
import { cn } from '@/lib/utils';
import type { ParkCrisisPhase, ParkScenarioState } from '@/api/types';
import { PARK_PHASE_CONFIG } from '@/api/types';
import { TeachingCallout, TEACHING_MESSAGES } from '@/components/categorical/TeachingCallout';
import { CrisisPhaseIndicator } from '@/components/categorical/StateIndicator';
import { CRISIS_PHASE as CRISIS_PRESET } from '@/components/categorical/presets';

// =============================================================================
// Types
// =============================================================================

export interface PhaseVisualizationProps {
  currentPhase: ParkCrisisPhase;
  availableTransitions: ParkCrisisPhase[];
  phaseTransitions: ParkScenarioState['phase_transitions'];
  consentDebt: number;
  onTransition?: (phase: ParkCrisisPhase) => void;
  disabled?: boolean;
  compact?: boolean;
  showTeaching?: boolean;
  className?: string;
}

// =============================================================================
// Sub-components
// =============================================================================

interface PhaseNodeProps {
  position: typeof CRISIS_PRESET.positions[0];
  isCurrent: boolean;
  isAvailable: boolean;
  onClick?: () => void;
  disabled?: boolean;
  compact?: boolean;
}

function PhaseNode({
  position,
  isCurrent,
  isAvailable,
  onClick,
  disabled,
  compact,
}: PhaseNodeProps) {
  const canClick = isAvailable && !disabled && onClick;

  return (
    <button
      onClick={canClick ? onClick : undefined}
      disabled={disabled || !isAvailable}
      className={cn(
        'relative flex flex-col items-center justify-center rounded-xl border-2 transition-all duration-300',
        compact ? 'w-14 h-14' : 'w-20 h-20',
        isCurrent && 'scale-105',
        canClick && 'hover:scale-110 cursor-pointer',
        !isAvailable && !isCurrent && 'opacity-40'
      )}
      style={{
        backgroundColor: `${position.color}15`,
        borderColor: isCurrent ? position.color : `${position.color}50`,
        boxShadow: isCurrent ? `0 0 20px ${position.color}40, 0 0 0 3px ${position.color}` : 'none',
      }}
    >
      {/* Position label */}
      <span
        className={cn(
          'font-bold transition-colors',
          compact ? 'text-xs' : 'text-sm'
        )}
        style={{ color: isCurrent ? position.color : `${position.color}80` }}
      >
        {compact ? position.label.slice(0, 3) : position.label}
      </span>

      {/* Available indicator */}
      {isAvailable && !isCurrent && !disabled && (
        <span className="absolute -bottom-1 text-[10px] text-gray-400">
          click
        </span>
      )}

      {/* Current glow pulse */}
      {isCurrent && (
        <div
          className="absolute inset-0 rounded-xl animate-pulse opacity-30"
          style={{ backgroundColor: position.color }}
        />
      )}
    </button>
  );
}

interface PhaseArrowProps {
  active: boolean;
  compact?: boolean;
}

function PhaseArrow({ active, compact }: PhaseArrowProps) {
  return (
    <div className={cn('flex items-center justify-center', compact ? 'w-3' : 'w-6')}>
      <svg
        viewBox="0 0 24 24"
        className={cn('transition-colors', compact ? 'w-3 h-3' : 'w-4 h-4')}
        fill="none"
        stroke={active ? '#22c55e' : '#374151'}
        strokeWidth={2}
      >
        <path d="M5 12h14m-6-6l6 6-6 6" />
      </svg>
    </div>
  );
}

// =============================================================================
// Main Component
// =============================================================================

export function PhaseVisualization({
  currentPhase,
  availableTransitions = [],
  phaseTransitions,
  consentDebt,
  onTransition,
  disabled = false,
  compact = false,
  showTeaching = true,
  className = '',
}: PhaseVisualizationProps) {
  const normalizedPhase = currentPhase.toUpperCase();

  // Calculate valid inputs from current state using preset edges
  const validInputs = useMemo(() => {
    const inputs: string[] = [];
    for (const edge of CRISIS_PRESET.edges) {
      if (edge.source === normalizedPhase) {
        inputs.push(edge.label);
      }
    }
    return [...new Set(inputs)];
  }, [normalizedPhase]);

  // Map phase to position index for arrow highlighting
  const currentIndex = CRISIS_PRESET.positions.findIndex(
    (p) => p.id === normalizedPhase
  );

  // Determine debt level for teaching message
  const debtLevel = consentDebt <= 0.25 ? 'low' : consentDebt <= 0.6 ? 'moderate' : 'high';

  return (
    <div className={cn('space-y-4', className)}>
      {/* Header with phase indicator */}
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-medium text-gray-300">Crisis Phase Machine</h3>
        <CrisisPhaseIndicator state={currentPhase} size="sm" />
      </div>

      {/* State machine diagram */}
      <div className="bg-gray-800/50 rounded-xl p-4 border border-gray-700">
        <div className="flex items-center justify-center gap-1 flex-wrap">
          {CRISIS_PRESET.positions.map((position, index) => {
            const isCurrent = position.id === normalizedPhase;
            const isAvailable = availableTransitions.includes(
              position.id as ParkCrisisPhase
            );

            return (
              <div key={position.id} className="flex items-center">
                <PhaseNode
                  position={position}
                  isCurrent={isCurrent}
                  isAvailable={isAvailable}
                  onClick={
                    isAvailable
                      ? () => onTransition?.(position.id as ParkCrisisPhase)
                      : undefined
                  }
                  disabled={disabled}
                  compact={compact}
                />
                {index < CRISIS_PRESET.positions.length - 1 && (
                  <PhaseArrow active={currentIndex === index} compact={compact} />
                )}
              </div>
            );
          })}
        </div>

        {/* Valid inputs display */}
        <div className="mt-4 flex flex-wrap gap-2 items-center justify-center">
          <span className="text-xs text-gray-500">Valid:</span>
          {validInputs.length > 0 ? (
            validInputs.map((input) => (
              <span
                key={input}
                className="px-2 py-0.5 text-xs rounded-full bg-park-highlight/30 text-park-highlight border border-park-highlight/50"
              >
                {input}
              </span>
            ))
          ) : (
            <span className="text-xs text-gray-500 italic">No valid transitions</span>
          )}
        </div>
      </div>

      {/* Available transitions buttons */}
      {availableTransitions.length > 0 && !disabled && (
        <div className="flex flex-wrap gap-2">
          {availableTransitions.map((phase) => {
            const config = PARK_PHASE_CONFIG[phase];
            return (
              <button
                key={phase}
                onClick={() => onTransition?.(phase)}
                className="flex items-center gap-2 px-3 py-2 text-sm rounded-lg border border-dashed transition-all hover:scale-105"
                style={{
                  borderColor: config.color,
                  backgroundColor: `${config.color}15`,
                  color: config.color,
                }}
              >
                <span className="text-xs">→</span>
                {config.label}
              </button>
            );
          })}
        </div>
      )}

      {/* Transition history (compact only shows if not compact) */}
      {phaseTransitions.length > 0 && !compact && (
        <div className="bg-gray-800/30 rounded-lg p-3">
          <p className="text-xs text-gray-500 mb-2">
            Transition History ({phaseTransitions.length})
          </p>
          <div className="space-y-1 max-h-24 overflow-y-auto">
            {phaseTransitions.slice(-5).reverse().map((transition, i) => (
              <div
                key={i}
                className="flex items-center gap-2 text-xs text-gray-400"
              >
                <span style={{ color: PARK_PHASE_CONFIG[transition.from].color }}>
                  {PARK_PHASE_CONFIG[transition.from].label}
                </span>
                <span>→</span>
                <span style={{ color: PARK_PHASE_CONFIG[transition.to].color }}>
                  {PARK_PHASE_CONFIG[transition.to].label}
                </span>
                <span className="text-gray-600 ml-auto">
                  debt: {Math.round(transition.consent_debt * 100)}%
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Teaching callout */}
      {showTeaching && !compact && (
        <TeachingCallout category="categorical" compact>
          {TEACHING_MESSAGES.crisis_polynomial}
          {debtLevel === 'high' && (
            <span className="text-red-400 ml-2">
              High consent debt is constraining options.
            </span>
          )}
        </TeachingCallout>
      )}
    </div>
  );
}

export default PhaseVisualization;
