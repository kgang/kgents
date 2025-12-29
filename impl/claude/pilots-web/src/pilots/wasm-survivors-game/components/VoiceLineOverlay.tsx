/**
 * WASM Survivors - Voice Line Overlay
 *
 * Displays the hornet's personality voice lines during gameplay.
 *
 * From PROTO_SPEC Part VII (The Hornet's Personality):
 * - Never begs, never whines, never seems unfairly treated
 * - KNOWS what this is and does it anyway
 * - Swagger before the fall
 * - Respect for the colony in death
 *
 * Voice lines appear as brief text overlays that:
 * - Fade in quickly, hold, fade out
 * - Don't obstruct gameplay
 * - Have subtle animation for presence
 * - Match the current arc phase in tone
 *
 * @see pilots/wasm-survivors-game/PROTO_SPEC.md (Part VII)
 * @see systems/contrast.ts
 */

import { useState, useEffect, useRef } from 'react';
import type { VoiceLine, ArcPhase } from '../systems/contrast';

// =============================================================================
// Types
// =============================================================================

interface VoiceLineOverlayProps {
  voiceLine: VoiceLine | null;
  arcPhase: ArcPhase;
  onComplete?: () => void;
}

// =============================================================================
// Constants
// =============================================================================

const FADE_IN_MS = 200;
const HOLD_MS = 2500;
const FADE_OUT_MS = 500;
// Total duration: FADE_IN_MS + HOLD_MS + FADE_OUT_MS = 3200ms

// Colors based on arc phase
const PHASE_COLORS: Record<ArcPhase, { text: string; glow: string }> = {
  POWER: { text: '#FFD700', glow: 'rgba(255, 215, 0, 0.3)' },     // Golden swagger
  FLOW: { text: '#00D4FF', glow: 'rgba(0, 212, 255, 0.3)' },      // Cool blue focus
  CRISIS: { text: '#FF8800', glow: 'rgba(255, 136, 0, 0.3)' },    // Warning orange
  TRAGEDY: { text: '#CC3333', glow: 'rgba(204, 51, 51, 0.3)' },   // Deep red acceptance
};

// =============================================================================
// Component
// =============================================================================

export function VoiceLineOverlay({
  voiceLine,
  arcPhase,
  onComplete,
}: VoiceLineOverlayProps) {
  const [visible, setVisible] = useState(false);
  const [opacity, setOpacity] = useState(0);
  const [currentLine, setCurrentLine] = useState<VoiceLine | null>(null);
  const timeoutRef = useRef<NodeJS.Timeout | null>(null);

  // Handle new voice line
  useEffect(() => {
    if (voiceLine && voiceLine !== currentLine) {
      // Clear any existing timeout
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }

      // Start showing the new line
      setCurrentLine(voiceLine);
      setVisible(true);
      setOpacity(0);

      // Fade in
      requestAnimationFrame(() => {
        setOpacity(1);
      });

      // Schedule fade out
      timeoutRef.current = setTimeout(() => {
        setOpacity(0);

        // Hide completely after fade out
        timeoutRef.current = setTimeout(() => {
          setVisible(false);
          setCurrentLine(null);
          onComplete?.();
        }, FADE_OUT_MS);
      }, FADE_IN_MS + HOLD_MS);
    }
  }, [voiceLine, currentLine, onComplete]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, []);

  if (!visible || !currentLine) {
    return null;
  }

  const colors = PHASE_COLORS[arcPhase];

  return (
    <div
      className="absolute inset-0 pointer-events-none flex items-end justify-center pb-24"
      style={{
        zIndex: 100,
      }}
    >
      <div
        className="relative"
        style={{
          opacity,
          transform: `translateY(${(1 - opacity) * 10}px)`,
          transition: `opacity ${opacity === 1 ? FADE_IN_MS : FADE_OUT_MS}ms ease-out, transform ${opacity === 1 ? FADE_IN_MS : FADE_OUT_MS}ms ease-out`,
        }}
      >
        {/* Glow background */}
        <div
          className="absolute inset-0 blur-xl"
          style={{
            background: colors.glow,
            transform: 'scale(1.5)',
          }}
        />

        {/* Voice line text */}
        <div
          className="relative px-6 py-3 text-center"
          style={{
            color: colors.text,
            fontFamily: 'system-ui, sans-serif',
            fontSize: '1.5rem',
            fontWeight: 600,
            fontStyle: 'italic',
            textShadow: `0 0 20px ${colors.glow}, 0 2px 4px rgba(0,0,0,0.8)`,
            letterSpacing: '0.02em',
          }}
        >
          "{currentLine.text}"
        </div>
      </div>
    </div>
  );
}

// =============================================================================
// Arc Phase Indicator (Optional Enhancement)
// =============================================================================

interface ArcPhaseIndicatorProps {
  phase: ArcPhase;
  phasesVisited: ArcPhase[];
}

/**
 * Small HUD element showing current arc phase.
 * Only visible after the first phase transition.
 */
export function ArcPhaseIndicator({ phase, phasesVisited }: ArcPhaseIndicatorProps) {
  // Don't show if still in POWER and nothing else visited
  if (phasesVisited.length <= 1 && phase === 'POWER') {
    return null;
  }

  const colors = PHASE_COLORS[phase];

  const PHASE_DESCRIPTIONS: Record<ArcPhase, string> = {
    POWER: 'THE HUNT',
    FLOW: 'THE RHYTHM',
    CRISIS: 'THE TURNING',
    TRAGEDY: 'THE END',
  };

  return (
    <div
      className="absolute top-2 left-1/2 -translate-x-1/2 pointer-events-none"
      style={{ zIndex: 90 }}
    >
      <div
        className="px-4 py-1 rounded-full text-xs font-bold uppercase tracking-wider"
        style={{
          color: colors.text,
          backgroundColor: 'rgba(0, 0, 0, 0.6)',
          border: `1px solid ${colors.text}`,
          textShadow: `0 0 10px ${colors.glow}`,
        }}
      >
        {PHASE_DESCRIPTIONS[phase]}
      </div>
    </div>
  );
}

// =============================================================================
// Contrast Indicator (Optional Enhancement)
// =============================================================================

interface ContrastIndicatorProps {
  contrastsVisited: number;
}

/**
 * Shows progress toward the 3-contrast goal (GD-1).
 * Appears after first contrast is fully visited.
 */
export function ContrastIndicator({ contrastsVisited }: ContrastIndicatorProps) {
  if (contrastsVisited === 0) {
    return null;
  }

  // Show checkmarks for visited contrasts (target: 3)
  const targetContrasts = 3;
  const checks = Array(targetContrasts).fill(false).map((_, i) => i < contrastsVisited);

  return (
    <div
      className="absolute bottom-2 left-1/2 -translate-x-1/2 pointer-events-none"
      style={{ zIndex: 90 }}
    >
      <div
        className="flex gap-1 px-3 py-1 rounded-full text-xs"
        style={{
          backgroundColor: 'rgba(0, 0, 0, 0.6)',
        }}
      >
        {checks.map((checked, i) => (
          <div
            key={i}
            className="w-2 h-2 rounded-full"
            style={{
              backgroundColor: checked ? '#FFD700' : 'rgba(255, 255, 255, 0.3)',
              boxShadow: checked ? '0 0 6px rgba(255, 215, 0, 0.5)' : 'none',
            }}
          />
        ))}
        <span
          className="ml-2"
          style={{
            color: contrastsVisited >= targetContrasts ? '#FFD700' : 'rgba(255, 255, 255, 0.6)',
          }}
        >
          {contrastsVisited}/{targetContrasts} contrasts
        </span>
      </div>
    </div>
  );
}

export default VoiceLineOverlay;
