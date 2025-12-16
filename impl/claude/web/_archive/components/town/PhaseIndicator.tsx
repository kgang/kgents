/**
 * PhaseIndicator: Visual N-Phase cycle indicator for Town UI.
 *
 * Wave 5: N-Phase Native Integration
 * ===================================
 *
 * Shows the current phase in the UNDERSTAND → ACT → REFLECT cycle
 * with visual indicators, cycle count, and checkpoint information.
 *
 * Design:
 * ┌─────────────────────────────────────────────────┐
 * │  ◉ UNDERSTAND ──── ○ ACT ──── ○ REFLECT        │
 * │  Cycle 1 • 3 checkpoints • 5 handles           │
 * └─────────────────────────────────────────────────┘
 *
 * Features:
 * - Three-phase indicator with active highlight
 * - Animated transitions between phases
 * - Cycle count and metrics display
 * - Tooltip with phase descriptions
 * - Compact and full display modes
 */

import { useMemo } from 'react';
import type { NPhaseType, NPhaseState } from '@/api/types';
import { NPHASE_CONFIG } from '@/api/types';

// =============================================================================
// Types
// =============================================================================

interface PhaseIndicatorProps {
  /** N-Phase state from useNPhaseStream */
  nphase: NPhaseState | null;
  /** Display mode: 'compact' shows only phases, 'full' includes metrics */
  mode?: 'compact' | 'full';
  /** Additional CSS classes */
  className?: string;
  /** Show animation on phase change */
  animate?: boolean;
}

// =============================================================================
// Phase Order
// =============================================================================

const PHASES: NPhaseType[] = ['UNDERSTAND', 'ACT', 'REFLECT'];

// =============================================================================
// Component
// =============================================================================

export function PhaseIndicator({
  nphase,
  mode = 'full',
  className = '',
  animate = true,
}: PhaseIndicatorProps) {
  // Derive phase index
  const currentPhaseIndex = useMemo(() => {
    if (!nphase) return -1;
    return PHASES.indexOf(nphase.currentPhase);
  }, [nphase]);

  // Not enabled or no state
  if (!nphase || !nphase.enabled) {
    return (
      <div className={`flex items-center gap-2 text-gray-500 text-sm ${className}`}>
        <span className="opacity-50">N-Phase disabled</span>
      </div>
    );
  }

  return (
    <div className={`${className}`}>
      {/* Phase Pills */}
      <div className="flex items-center gap-1">
        {PHASES.map((phase, index) => {
          const isActive = index === currentPhaseIndex;
          const isPast = index < currentPhaseIndex;
          const color = NPHASE_CONFIG.colors[phase];
          const icon = NPHASE_CONFIG.icons[phase];
          const description = NPHASE_CONFIG.descriptions[phase];

          return (
            <div key={phase} className="flex items-center">
              {/* Phase Node */}
              <div
                className={`
                  relative group flex items-center gap-1.5 px-2.5 py-1 rounded-full
                  text-xs font-medium transition-all duration-300
                  ${isActive
                    ? 'text-white shadow-lg'
                    : isPast
                      ? 'text-gray-400 bg-gray-800/50'
                      : 'text-gray-500 bg-gray-800/30'
                  }
                  ${animate && isActive ? 'scale-105' : ''}
                `}
                style={{
                  backgroundColor: isActive ? color : undefined,
                  boxShadow: isActive ? `0 0 12px ${color}40` : undefined,
                }}
                title={description}
              >
                {/* Pulse ring for active phase */}
                {isActive && animate && (
                  <span
                    className="absolute inset-0 rounded-full animate-ping opacity-20"
                    style={{ backgroundColor: color }}
                  />
                )}

                {/* Icon */}
                <span className={`relative ${isActive ? '' : 'opacity-60'}`}>
                  {isPast ? '✓' : icon}
                </span>

                {/* Label */}
                <span className="relative hidden sm:inline">
                  {phase}
                </span>

                {/* Tooltip */}
                <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 px-2 py-1
                  bg-gray-900 text-gray-200 text-xs rounded shadow-lg whitespace-nowrap
                  opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none z-10">
                  {description}
                  <div className="absolute top-full left-1/2 -translate-x-1/2 -mt-1
                    border-4 border-transparent border-t-gray-900" />
                </div>
              </div>

              {/* Connector */}
              {index < PHASES.length - 1 && (
                <div
                  className={`w-4 h-0.5 mx-0.5 transition-colors duration-300 ${
                    isPast ? 'bg-gray-500' : 'bg-gray-700'
                  }`}
                />
              )}
            </div>
          );
        })}
      </div>

      {/* Metrics Row (full mode only) */}
      {mode === 'full' && (
        <div className="flex items-center gap-3 mt-1.5 text-xs text-gray-500">
          <MetricBadge
            label="Cycle"
            value={nphase.cycleCount}
            color={NPHASE_CONFIG.colors[nphase.currentPhase]}
          />
          {nphase.checkpointCount > 0 && (
            <MetricBadge
              label="Checkpoints"
              value={nphase.checkpointCount}
              icon="📍"
            />
          )}
          {nphase.handleCount > 0 && (
            <MetricBadge
              label="Handles"
              value={nphase.handleCount}
              icon="🔗"
            />
          )}
          {nphase.transitions.length > 0 && (
            <MetricBadge
              label="Transitions"
              value={nphase.transitions.length}
              icon="↔️"
            />
          )}
        </div>
      )}
    </div>
  );
}

// =============================================================================
// Sub-components
// =============================================================================

interface MetricBadgeProps {
  label: string;
  value: number;
  icon?: string;
  color?: string;
}

function MetricBadge({ label, value, icon, color }: MetricBadgeProps) {
  return (
    <span
      className="flex items-center gap-1 px-1.5 py-0.5 rounded bg-gray-800/50"
      title={label}
    >
      {icon && <span className="text-[10px]">{icon}</span>}
      <span style={{ color: color || 'inherit' }}>{value}</span>
      <span className="hidden sm:inline text-gray-600">{label.toLowerCase()}</span>
    </span>
  );
}

// =============================================================================
// Compact Variant
// =============================================================================

/**
 * PhaseIndicatorCompact: Minimal N-Phase indicator.
 *
 * Shows only the current phase with icon and cycle count.
 * Use in space-constrained areas like headers.
 */
export function PhaseIndicatorCompact({
  nphase,
  className = '',
}: Pick<PhaseIndicatorProps, 'nphase' | 'className'>) {
  if (!nphase || !nphase.enabled) {
    return null;
  }

  const color = NPHASE_CONFIG.colors[nphase.currentPhase];
  const icon = NPHASE_CONFIG.icons[nphase.currentPhase];

  return (
    <div
      className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-xs font-medium ${className}`}
      style={{ backgroundColor: `${color}20`, color }}
      title={`N-Phase: ${nphase.currentPhase} (Cycle ${nphase.cycleCount})`}
    >
      <span>{icon}</span>
      <span>{nphase.currentPhase}</span>
      {nphase.cycleCount > 1 && (
        <span className="opacity-70">#{nphase.cycleCount}</span>
      )}
    </div>
  );
}

// =============================================================================
// Exports
// =============================================================================

export default PhaseIndicator;
