/**
 * PhaseIndicator — The Polynomial Made Visible
 *
 * Shows the current phase of the GalleryPolynomial state machine.
 * Making the categorical ground visible teaches the pattern.
 *
 * Phases: BROWSING → INSPECTING → SIMULATING → VERIFYING
 *
 * @see agents/gallery/polynomial.py
 */

import type { CSSProperties } from 'react';
import type { TerrariumPhase } from '@/hooks/useTerrarium';

export interface PhaseIndicatorProps {
  /** Current polynomial phase */
  phase: TerrariumPhase;
  /** Called when user clicks a phase (optional interactivity) */
  onPhaseClick?: (phase: TerrariumPhase) => void;
  /** Additional CSS classes */
  className?: string;
  /** Additional inline styles */
  style?: CSSProperties;
}

const PHASES: TerrariumPhase[] = ['BROWSING', 'INSPECTING', 'SIMULATING', 'VERIFYING'];

const PHASE_ICONS: Record<TerrariumPhase, string> = {
  BROWSING: '◎',
  INSPECTING: '◉',
  SIMULATING: '◈',
  VERIFYING: '◇',
};

const PHASE_DESCRIPTIONS: Record<TerrariumPhase, string> = {
  BROWSING: 'Viewing the grid',
  INSPECTING: 'Examining detail',
  SIMULATING: 'Stepping through',
  VERIFYING: 'Checking laws',
};

export function PhaseIndicator({
  phase,
  onPhaseClick,
  className = '',
  style,
}: PhaseIndicatorProps) {
  const currentIndex = PHASES.indexOf(phase);

  return (
    <div
      className={`phase-indicator ${className}`}
      style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        gap: '0.5rem',
        padding: '0.75rem 1rem',
        background: 'var(--surface-2)',
        borderRadius: '0.5rem',
        ...style,
      }}
      role="navigation"
      aria-label="Gallery polynomial phases"
    >
      {PHASES.map((p, i) => {
        const isActive = p === phase;
        const isPast = i < currentIndex;
        const isFuture = i > currentIndex;

        return (
          <div key={p} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            {/* Phase node */}
            <button
              onClick={() => onPhaseClick?.(p)}
              disabled={!onPhaseClick}
              style={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                gap: '0.25rem',
                padding: '0.5rem',
                background: 'transparent',
                border: 'none',
                cursor: onPhaseClick ? 'pointer' : 'default',
                opacity: isFuture ? 0.4 : 1,
                transition: 'opacity 0.2s ease',
              }}
              aria-current={isActive ? 'step' : undefined}
              title={PHASE_DESCRIPTIONS[p]}
            >
              {/* Icon */}
              <span
                style={{
                  fontSize: '1.25rem',
                  color: isActive
                    ? 'var(--copper-500)'
                    : isPast
                      ? 'var(--sage-500)'
                      : 'var(--text-tertiary)',
                  transition: 'color 0.2s ease',
                }}
              >
                {PHASE_ICONS[p]}
              </span>

              {/* Label */}
              <span
                style={{
                  fontFamily: 'var(--font-mono)',
                  fontSize: '0.625rem',
                  fontWeight: isActive ? 600 : 400,
                  color: isActive ? 'var(--text-primary)' : 'var(--text-tertiary)',
                  textTransform: 'uppercase',
                  letterSpacing: '0.05em',
                  transition: 'color 0.2s ease',
                }}
              >
                {p}
              </span>
            </button>

            {/* Connector line (not after last) */}
            {i < PHASES.length - 1 && (
              <div
                style={{
                  width: '2rem',
                  height: '2px',
                  background: isPast ? 'var(--sage-500)' : 'var(--surface-3)',
                  borderRadius: '1px',
                  transition: 'background 0.2s ease',
                }}
                aria-hidden="true"
              />
            )}
          </div>
        );
      })}
    </div>
  );
}

export default PhaseIndicator;
