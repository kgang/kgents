/**
 * ConsentMeter: Consent debt and force mechanics display.
 *
 * Wave 3: Punchdrunk Park crisis practice.
 *
 * From Punchdrunk principles:
 * - Consent debt accumulates with forced actions
 * - Forces are limited (3 per scenario)
 * - High consent debt reduces serendipity
 */

import { getHealthColor } from '../../constants';

interface ConsentMeterProps {
  consentDebt: number;
  forcesUsed: number;
  forcesRemaining: number;
  onForce?: () => void;
  forceDisabled?: boolean;
  compact?: boolean;
  className?: string;
}

/**
 * Visual debt bar with gradient.
 * Uses inverted health colors (low debt = healthy, high debt = critical)
 */
function DebtBar({ debt, className = '' }: { debt: number; className?: string }) {
  // Consent debt uses inverted health: 0 = healthy (green), 1 = critical (red)
  // We invert the health score so low debt shows as healthy
  const color = getHealthColor(1 - debt);

  return (
    <div className={`relative h-3 bg-gray-700 rounded-full overflow-hidden ${className}`}>
      <div
        className="absolute inset-y-0 left-0 rounded-full transition-all duration-300"
        style={{
          width: `${debt * 100}%`,
          backgroundColor: color,
        }}
      />
      {/* Threshold markers */}
      <div className="absolute inset-0 flex justify-between px-px">
        <div className="w-px h-full" />
        <div className="w-px h-full bg-gray-500 opacity-50" style={{ marginLeft: '30%' }} />
        <div className="w-px h-full bg-gray-500 opacity-50" style={{ marginLeft: '30%' }} />
        <div className="w-px h-full" />
      </div>
    </div>
  );
}

/**
 * Force tokens display.
 */
function ForceTokens({
  used,
  remaining,
  compact = false,
}: {
  used: number;
  remaining: number;
  compact?: boolean;
}) {
  const total = used + remaining;

  return (
    <div className={`flex items-center ${compact ? 'gap-1' : 'gap-2'}`}>
      {Array.from({ length: total }).map((_, i) => {
        const isUsed = i < used;
        return (
          <div
            key={i}
            className={`
              ${compact ? 'w-4 h-4' : 'w-6 h-6'}
              rounded-full border-2 flex items-center justify-center
              transition-all duration-200
              ${isUsed
                ? 'border-red-500 bg-red-900/50'
                : 'border-gray-500 bg-gray-800'
              }
            `}
          >
            {isUsed && (
              <span className={`text-red-400 ${compact ? 'text-[8px]' : 'text-xs'}`}>!</span>
            )}
          </div>
        );
      })}
    </div>
  );
}

export function ConsentMeter({
  consentDebt,
  forcesUsed,
  forcesRemaining,
  onForce,
  forceDisabled = false,
  compact = false,
  className = '',
}: ConsentMeterProps) {
  const debtPercent = Math.round(consentDebt * 100);
  const isHighDebt = consentDebt > 0.6;

  if (compact) {
    return (
      <div className={`flex items-center gap-3 ${className}`}>
        <div className="flex-1">
          <div className="flex items-center justify-between text-xs text-gray-400 mb-1">
            <span>Debt</span>
            <span className={isHighDebt ? 'text-red-400' : ''}>{debtPercent}%</span>
          </div>
          <DebtBar debt={consentDebt} />
        </div>
        <ForceTokens used={forcesUsed} remaining={forcesRemaining} compact />
      </div>
    );
  }

  return (
    <div className={`bg-gray-800/50 rounded-lg p-4 ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-sm font-medium text-gray-200">Consent Mechanics</h3>
        {isHighDebt && (
          <span className="text-xs text-red-400 animate-pulse">High Debt!</span>
        )}
      </div>

      {/* Consent Debt */}
      <div className="mb-4">
        <div className="flex items-center justify-between text-xs text-gray-400 mb-2">
          <span>Consent Debt</span>
          <span className={isHighDebt ? 'text-red-400 font-medium' : ''}>
            {debtPercent}%
          </span>
        </div>
        <DebtBar debt={consentDebt} />
        <p className="text-xs text-gray-500 mt-1">
          {consentDebt <= 0.3
            ? 'Low debt - serendipity flows freely'
            : consentDebt <= 0.6
              ? 'Moderate debt - some serendipity blocked'
              : 'High debt - serendipity severely reduced'
          }
        </p>
      </div>

      {/* Forces */}
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
              disabled={forceDisabled || forcesRemaining === 0}
              className={`
                px-3 py-1.5 text-xs font-medium rounded transition-colors
                ${forcesRemaining > 0 && !forceDisabled
                  ? 'bg-red-600 hover:bg-red-700 text-white'
                  : 'bg-gray-700 text-gray-500 cursor-not-allowed'
                }
              `}
            >
              Use Force
            </button>
          )}
        </div>
        <p className="text-xs text-gray-500 mt-2">
          Force increases consent debt by 20%
        </p>
      </div>

      {/* Warning when at rupture point */}
      {consentDebt >= 0.8 && (
        <div className="mt-4 p-2 bg-red-900/30 border border-red-800 rounded text-xs text-red-300">
          At rupture point - further forcing may break the scenario
        </div>
      )}
    </div>
  );
}

export default ConsentMeter;
