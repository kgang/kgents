/**
 * PhaseTransition: Crisis phase state machine visualization.
 *
 * Wave 3: Punchdrunk Park crisis practice.
 *
 * Shows the crisis polynomial: NORMAL -> INCIDENT -> RESPONSE -> RECOVERY -> NORMAL
 *
 * Features:
 * - Visual state machine diagram (Lucide icons per visual-system.md)
 * - Current phase highlight
 * - Valid transition buttons
 * - Transition history
 */

import type { ParkCrisisPhase, ParkScenarioState } from '../../api/types';
import { PARK_PHASE_CONFIG } from '../../api/types';
import { STATE_COLORS, GRAYS, getCrisisPhaseIcon } from '../../constants';

interface PhaseTransitionProps {
  currentPhase: ParkCrisisPhase;
  availableTransitions: ParkCrisisPhase[];
  phaseTransitions: ParkScenarioState['phase_transitions'];
  onTransition?: (phase: ParkCrisisPhase) => void;
  disabled?: boolean;
  compact?: boolean;
  className?: string;
}

const PHASE_ORDER: ParkCrisisPhase[] = ['NORMAL', 'INCIDENT', 'RESPONSE', 'RECOVERY'];

/**
 * Single phase node in the diagram.
 */
interface PhaseNodeProps {
  phase: ParkCrisisPhase;
  isCurrent: boolean;
  isAvailable: boolean;
  onClick?: () => void;
  disabled?: boolean;
  compact?: boolean;
}

function PhaseNode({
  phase,
  isCurrent,
  isAvailable,
  onClick,
  disabled,
  compact,
}: PhaseNodeProps) {
  const config = PARK_PHASE_CONFIG[phase];
  const PhaseIcon = getCrisisPhaseIcon(phase);
  const canClick = isAvailable && !disabled && onClick;

  return (
    <button
      onClick={canClick ? onClick : undefined}
      disabled={disabled || !isAvailable}
      className={`
        relative flex flex-col items-center justify-center
        ${compact ? 'w-16 h-16' : 'w-20 h-20'}
        rounded-lg border-2 transition-all duration-200
        ${isCurrent
          ? 'border-white bg-gray-700 shadow-lg scale-110'
          : isAvailable && !disabled
            ? 'border-dashed border-gray-500 hover:border-white hover:bg-gray-700/50 cursor-pointer'
            : 'border-gray-700 bg-gray-800/50'
        }
        ${canClick ? 'hover:scale-105' : ''}
      `}
      style={{
        borderColor: isCurrent ? config.color : undefined,
        boxShadow: isCurrent ? `0 0 20px ${config.color}40` : undefined,
      }}
    >
      <PhaseIcon
        className={`${compact ? 'w-5 h-5' : 'w-6 h-6'}`}
        style={{ color: isCurrent ? config.color : '#9ca3af' }}
      />
      <span
        className={`font-medium ${compact ? 'text-[10px]' : 'text-xs'} mt-1`}
        style={{ color: isCurrent ? config.color : '#9ca3af' }}
      >
        {config.label}
      </span>
      {isAvailable && !isCurrent && !disabled && (
        <span className="absolute -bottom-1 left-1/2 -translate-x-1/2 text-[10px] text-gray-400">
          click
        </span>
      )}
    </button>
  );
}

/**
 * Arrow between phases.
 */
function PhaseArrow({ active, compact }: { active: boolean; compact?: boolean }) {
  return (
    <div
      className={`flex items-center justify-center ${compact ? 'w-4' : 'w-6'}`}
    >
      <svg
        viewBox="0 0 24 24"
        className={`${compact ? 'w-3 h-3' : 'w-4 h-4'} transition-colors`}
        fill="none"
        stroke={active ? STATE_COLORS.success : GRAYS[700]}
        strokeWidth={2}
      >
        <path d="M5 12h14m-6-6l6 6-6 6" />
      </svg>
    </div>
  );
}

export function PhaseTransition({
  currentPhase,
  availableTransitions = [],
  phaseTransitions,
  onTransition,
  disabled = false,
  compact = false,
  className = '',
}: PhaseTransitionProps) {
  const currentIndex = PHASE_ORDER.indexOf(currentPhase);

  // Safeguard: ensure availableTransitions is an array
  const transitions = availableTransitions ?? [];

  // Check if a phase is available for transition
  const isAvailable = (phase: ParkCrisisPhase) =>
    transitions.includes(phase);

  return (
    <div className={`${className}`}>
      {/* Phase diagram */}
      <div className="flex items-center justify-center gap-1 mb-4">
        {PHASE_ORDER.map((phase, index) => (
          <div key={phase} className="flex items-center">
            <PhaseNode
              phase={phase}
              isCurrent={currentPhase === phase}
              isAvailable={isAvailable(phase)}
              onClick={isAvailable(phase) ? () => onTransition?.(phase) : undefined}
              disabled={disabled}
              compact={compact}
            />
            {index < PHASE_ORDER.length - 1 && (
              <PhaseArrow
                active={currentIndex === index}
                compact={compact}
              />
            )}
          </div>
        ))}
        {/* Loop back arrow */}
        {!compact && (
          <div className="flex items-center ml-2">
            <svg
              viewBox="0 0 24 24"
              className="w-4 h-4"
              fill="none"
              stroke={currentPhase === 'RECOVERY' ? STATE_COLORS.success : GRAYS[700]}
              strokeWidth={2}
            >
              <path d="M19 12H5m6-6l-6 6 6 6" />
            </svg>
          </div>
        )}
      </div>

      {/* Available transitions hint */}
      {transitions.length > 0 && !disabled && (
        <p className="text-center text-xs text-gray-400 mb-4">
          Available: {transitions.map(p => PARK_PHASE_CONFIG[p].label).join(', ')}
        </p>
      )}

      {/* Transition history */}
      {phaseTransitions.length > 0 && !compact && (
        <div className="mt-4">
          <p className="text-xs text-gray-500 mb-2">
            Transition History ({phaseTransitions.length})
          </p>
          <div className="space-y-1 max-h-32 overflow-y-auto">
            {phaseTransitions.slice(-5).reverse().map((transition, i) => (
              <div
                key={i}
                className="flex items-center gap-2 text-xs text-gray-400 bg-gray-800/30 rounded px-2 py-1"
              >
                <span style={{ color: PARK_PHASE_CONFIG[transition.from].color }}>
                  {PARK_PHASE_CONFIG[transition.from].label}
                </span>
                <span>-&gt;</span>
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
    </div>
  );
}

/**
 * Compact inline phase indicator.
 */
interface PhaseIndicatorProps {
  currentPhase: ParkCrisisPhase;
  className?: string;
}

export function PhaseIndicator({ currentPhase, className = '' }: PhaseIndicatorProps) {
  const config = PARK_PHASE_CONFIG[currentPhase];
  const PhaseIcon = getCrisisPhaseIcon(currentPhase);

  return (
    <div
      className={`inline-flex items-center gap-1.5 px-2 py-1 rounded-full ${className}`}
      style={{
        backgroundColor: `${config.color}22`,
        color: config.color,
      }}
    >
      <PhaseIcon className="w-4 h-4" />
      <span className="text-xs font-medium">{config.label}</span>
    </div>
  );
}

export default PhaseTransition;
