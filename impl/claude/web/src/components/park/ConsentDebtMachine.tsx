/**
 * ConsentDebtMachine: Consent debt as polynomial state machine.
 *
 * Phase 3 of park-town-design-overhaul: Enhances ConsentMeter to visualize
 * debt levels as polynomial phases with constraint previews.
 *
 * Features:
 * - Debt levels as state machine positions (HEALTHY → ELEVATED → HIGH → CRITICAL)
 * - Force tokens with usage tracking
 * - Constraint preview at each debt level
 * - Connection to DIRECTOR_OPERAD consent_constraint law
 *
 * @see plans/park-town-design-overhaul.md (Journey 6: Consent Debt as Polynomial)
 * @see spec/park/index.md (consent_constraint law)
 */

import { useMemo } from 'react';
import { cn } from '@/lib/utils';
import { ConsentDebtIndicator } from '@/components/categorical/StateIndicator';
import { TeachingCallout, TEACHING_MESSAGES } from '@/components/categorical/TeachingCallout';
import { CONSENT_DEBT as CONSENT_PRESET } from '@/components/categorical/presets';
import { getHealthColor } from '@/constants';

// =============================================================================
// Types
// =============================================================================

export interface ConsentDebtMachineProps {
  consentDebt: number;
  forcesUsed: number;
  forcesRemaining: number;
  onForce?: () => void;
  forceDisabled?: boolean;
  showStateMachine?: boolean;
  showTeaching?: boolean;
  compact?: boolean;
  className?: string;
}

type DebtLevel = 'HEALTHY' | 'ELEVATED' | 'HIGH' | 'CRITICAL';

// =============================================================================
// Helpers
// =============================================================================

/**
 * Determine debt level from continuous value.
 */
function getDebtLevel(debt: number): DebtLevel {
  if (debt <= 0.25) return 'HEALTHY';
  if (debt <= 0.5) return 'ELEVATED';
  if (debt <= 0.75) return 'HIGH';
  return 'CRITICAL';
}

/**
 * Get constraints for each debt level.
 */
const DEBT_CONSTRAINTS: Record<DebtLevel, string[]> = {
  HEALTHY: ['All operations available', 'Serendipity flows freely', 'Normal force costs'],
  ELEVATED: ['Minor serendipity reduction', 'Standard force costs', 'Some delays possible'],
  HIGH: ['Force costs 3x tokens', 'Injections require mask consent', 'Citizens may refuse'],
  CRITICAL: ['Forces blocked', 'Minimal serendipity', 'Risk of scenario rupture'],
};

/**
 * Get valid inputs from current debt level.
 */
function getValidInputs(level: DebtLevel): string[] {
  const inputs: string[] = [];
  for (const edge of CONSENT_PRESET.edges) {
    if (edge.source === level) {
      inputs.push(edge.label);
    }
  }
  return [...new Set(inputs)];
}

// =============================================================================
// Sub-components
// =============================================================================

interface DebtStateMachineProps {
  currentLevel: DebtLevel;
  compact?: boolean;
}

function DebtStateMachine({ currentLevel, compact = false }: DebtStateMachineProps) {
  return (
    <div className={cn('flex gap-1 justify-center', compact ? 'py-1' : 'py-2')}>
      {CONSENT_PRESET.positions.map((position) => {
        const isCurrent = position.id === currentLevel;
        return (
          <div
            key={position.id}
            className={cn(
              'relative flex flex-col items-center justify-center rounded-lg transition-all duration-300',
              compact ? 'w-10 h-10' : 'w-14 h-14',
              isCurrent && 'scale-105'
            )}
            style={{
              backgroundColor: `${position.color}15`,
              border: `2px solid ${isCurrent ? position.color : position.color + '30'}`,
              boxShadow: isCurrent ? `0 0 12px ${position.color}40, 0 0 0 2px ${position.color}` : 'none',
            }}
            title={`${position.label}: ${position.description}`}
          >
            <span
              className={cn('font-bold', compact ? 'text-[8px]' : 'text-xs')}
              style={{ color: isCurrent ? position.color : position.color + '60' }}
            >
              {compact ? position.label[0] : position.label.slice(0, 3)}
            </span>
          </div>
        );
      })}
    </div>
  );
}

interface ForceTokensProps {
  used: number;
  remaining: number;
  compact?: boolean;
}

function ForceTokens({ used, remaining, compact = false }: ForceTokensProps) {
  const total = used + remaining;

  return (
    <div className={cn('flex items-center', compact ? 'gap-1' : 'gap-2')}>
      {Array.from({ length: total }).map((_, i) => {
        const isUsed = i < used;
        return (
          <div
            key={i}
            className={cn(
              'rounded-full border-2 flex items-center justify-center transition-all duration-200',
              compact ? 'w-5 h-5' : 'w-7 h-7',
              isUsed
                ? 'border-red-500 bg-red-900/50'
                : 'border-gray-500 bg-gray-800 hover:border-gray-400'
            )}
          >
            {isUsed && (
              <span className={cn('text-red-400', compact ? 'text-[8px]' : 'text-xs')}>
                ×
              </span>
            )}
          </div>
        );
      })}
    </div>
  );
}

interface DebtBarProps {
  debt: number;
  className?: string;
}

function DebtBar({ debt, className = '' }: DebtBarProps) {
  // Inverted health: 0 = healthy (green), 1 = critical (red)
  const color = getHealthColor(1 - debt);

  return (
    <div className={cn('relative h-4 bg-gray-700 rounded-full overflow-hidden', className)}>
      <div
        className="absolute inset-y-0 left-0 rounded-full transition-all duration-300"
        style={{
          width: `${debt * 100}%`,
          backgroundColor: color,
        }}
      />
      {/* Threshold markers */}
      <div className="absolute inset-0 flex">
        <div className="w-[25%] border-r border-gray-500/30" />
        <div className="w-[25%] border-r border-gray-500/30" />
        <div className="w-[25%] border-r border-gray-500/30" />
        <div className="w-[25%]" />
      </div>
    </div>
  );
}

// =============================================================================
// Main Component
// =============================================================================

export function ConsentDebtMachine({
  consentDebt,
  forcesUsed,
  forcesRemaining,
  onForce,
  forceDisabled = false,
  showStateMachine = true,
  showTeaching = true,
  compact = false,
  className = '',
}: ConsentDebtMachineProps) {
  const debtLevel = useMemo(() => getDebtLevel(consentDebt), [consentDebt]);
  const debtPercent = Math.round(consentDebt * 100);
  const validInputs = useMemo(() => getValidInputs(debtLevel), [debtLevel]);
  const constraints = DEBT_CONSTRAINTS[debtLevel];
  const isCritical = debtLevel === 'CRITICAL';
  const isHighDebt = debtLevel === 'HIGH' || debtLevel === 'CRITICAL';

  if (compact) {
    return (
      <div className={cn('bg-gray-800/50 rounded-lg p-3', className)}>
        {/* Header */}
        <div className="flex items-center justify-between mb-2">
          <span className="text-xs font-medium text-gray-300">Consent Debt</span>
          <ConsentDebtIndicator state={debtLevel} size="sm" />
        </div>

        {/* Debt bar */}
        <DebtBar debt={consentDebt} className="mb-2" />

        {/* Compact stats */}
        <div className="flex items-center justify-between">
          <span className={cn('text-sm font-medium', isHighDebt && 'text-red-400')}>
            {debtPercent}%
          </span>
          <ForceTokens used={forcesUsed} remaining={forcesRemaining} compact />
        </div>

        {/* Mini state machine */}
        {showStateMachine && <DebtStateMachine currentLevel={debtLevel} compact />}
      </div>
    );
  }

  return (
    <div
      className={cn(
        'bg-gray-800/50 rounded-xl p-4 border transition-all duration-300',
        isCritical ? 'border-red-500/50' : 'border-gray-700',
        className
      )}
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-medium text-gray-200">Consent Debt Machine</h3>
        <div className="flex items-center gap-2">
          {isHighDebt && (
            <span className="text-xs text-red-400 animate-pulse">High Debt!</span>
          )}
          <ConsentDebtIndicator state={debtLevel} size="sm" />
        </div>
      </div>

      {/* Debt bar with percentage */}
      <div className="mb-4">
        <div className="flex items-center justify-between text-xs text-gray-400 mb-2">
          <span>Current Debt</span>
          <span className={cn(isHighDebt && 'text-red-400 font-medium')}>
            {debtPercent}%
          </span>
        </div>
        <DebtBar debt={consentDebt} />
      </div>

      {/* State machine visualization */}
      {showStateMachine && (
        <div className="bg-gray-800/30 rounded-lg p-3 mb-4">
          <div className="text-xs text-gray-500 mb-2 text-center">Debt Levels</div>
          <DebtStateMachine currentLevel={debtLevel} />

          {/* Valid inputs */}
          <div className="flex flex-wrap gap-1.5 items-center justify-center mt-2">
            <span className="text-xs text-gray-500">Valid:</span>
            {validInputs.map((input) => (
              <span
                key={input}
                className={cn(
                  'px-2 py-0.5 text-xs rounded-full border',
                  input === 'force'
                    ? 'bg-red-500/20 text-red-400 border-red-500/30'
                    : 'bg-green-500/20 text-green-400 border-green-500/30'
                )}
              >
                {input}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Current constraints preview */}
      <div className="bg-gray-800/20 rounded-lg p-3 mb-4">
        <div className="text-xs text-gray-500 mb-2">Constraints at {debtLevel}</div>
        <ul className="space-y-1">
          {constraints.map((constraint, i) => (
            <li
              key={i}
              className={cn(
                'text-xs flex items-center gap-2',
                isHighDebt ? 'text-red-300' : 'text-gray-400'
              )}
            >
              <span className={isHighDebt ? 'text-red-400' : 'text-green-400'}>
                {isHighDebt ? '⚠' : '✓'}
              </span>
              {constraint}
            </li>
          ))}
        </ul>
      </div>

      {/* Forces section */}
      <div>
        <div className="flex items-center justify-between mb-2">
          <span className="text-xs text-gray-400">Forces Available</span>
          <span className="text-xs text-gray-500">{forcesRemaining}/3</span>
        </div>
        <div className="flex items-center justify-between">
          <ForceTokens used={forcesUsed} remaining={forcesRemaining} />
          {onForce && (
            <button
              onClick={onForce}
              disabled={forceDisabled || forcesRemaining === 0 || isCritical}
              className={cn(
                'px-3 py-1.5 text-xs font-medium rounded transition-colors',
                forcesRemaining > 0 && !forceDisabled && !isCritical
                  ? 'bg-red-600 hover:bg-red-700 text-white'
                  : 'bg-gray-700 text-gray-500 cursor-not-allowed'
              )}
            >
              {isCritical ? 'Blocked' : 'Use Force'}
            </button>
          )}
        </div>
        {debtLevel === 'HIGH' && (
          <p className="text-xs text-amber-400 mt-2">Force costs 3x tokens at HIGH debt</p>
        )}
      </div>

      {/* Rupture warning */}
      {isCritical && (
        <div className="mt-4 p-3 bg-red-900/30 border border-red-800 rounded-lg">
          <p className="text-xs text-red-300">
            At rupture point — further forcing may break the scenario
          </p>
        </div>
      )}

      {/* Teaching callout */}
      {showTeaching && (
        <div className="mt-4">
          <TeachingCallout category="conceptual" compact>
            {TEACHING_MESSAGES.consent_debt}
          </TeachingCallout>
        </div>
      )}
    </div>
  );
}

export default ConsentDebtMachine;
