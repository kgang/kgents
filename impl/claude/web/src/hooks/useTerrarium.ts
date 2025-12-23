/**
 * useTerrarium — Global State for the Living Gallery
 *
 * The Terrarium is not a catalogue—it is a living demonstration
 * of the categorical ground. This hook manages:
 *
 * - Entropy: Global chaos level (0.0 = calm, 1.0 = chaotic)
 * - Phase: Current polynomial state (BROWSING → INSPECTING → SIMULATING → VERIFYING)
 *
 * All creatures in the Terrarium respond to entropy changes.
 * The phase indicator shows the categorical ground.
 *
 * @see spec/gallery/gallery-v2.md
 */

import { create } from 'zustand';

/**
 * Gallery polynomial phases.
 * Maps to GalleryPolynomial in agents/gallery/polynomial.py
 */
export type TerrariumPhase = 'BROWSING' | 'INSPECTING' | 'SIMULATING' | 'VERIFYING';

/**
 * Terrarium state shape.
 */
export interface TerrariumState {
  /** Global entropy level (0.0 - 1.0). Controls animation intensity across all creatures. */
  entropy: number;

  /** Current polynomial phase. Visible in the phase indicator. */
  phase: TerrariumPhase;

  /** Set entropy (clamped to 0-1). */
  setEntropy: (e: number) => void;

  /** Set polynomial phase. */
  setPhase: (p: TerrariumPhase) => void;

  /** Increment entropy by delta. */
  nudgeEntropy: (delta: number) => void;

  /** Cycle to next phase. */
  nextPhase: () => void;
}

/**
 * Phase order for cycling.
 */
const PHASE_ORDER: TerrariumPhase[] = ['BROWSING', 'INSPECTING', 'SIMULATING', 'VERIFYING'];

/**
 * The Terrarium store.
 *
 * Default entropy: 0.3 (calm but alive)
 * Default phase: BROWSING (initial state)
 */
export const useTerrarium = create<TerrariumState>((set, get) => ({
  entropy: 0.3,
  phase: 'BROWSING',

  setEntropy: (entropy) =>
    set({
      entropy: Math.max(0, Math.min(1, entropy)),
    }),

  setPhase: (phase) => set({ phase }),

  nudgeEntropy: (delta) => {
    const current = get().entropy;
    set({
      entropy: Math.max(0, Math.min(1, current + delta)),
    });
  },

  nextPhase: () => {
    const current = get().phase;
    const currentIndex = PHASE_ORDER.indexOf(current);
    const nextIndex = (currentIndex + 1) % PHASE_ORDER.length;
    set({ phase: PHASE_ORDER[nextIndex] });
  },
}));

/**
 * Entropy level descriptions for teaching callouts.
 */
export function describeEntropy(entropy: number): string {
  if (entropy < 0.15) return 'Still. Almost frozen.';
  if (entropy < 0.3) return 'Calm. Gentle breathing.';
  if (entropy < 0.5) return 'Active. Personality emerges.';
  if (entropy < 0.7) return 'Excited. Animation quickens.';
  if (entropy < 0.85) return 'Chaotic. Beautiful disorder.';
  return 'Maximum entropy. The edge of chaos.';
}

/**
 * Short entropy label for compact display.
 */
export function entropyLabel(entropy: number): string {
  if (entropy < 0.2) return 'Calm';
  if (entropy < 0.5) return 'Active';
  if (entropy < 0.8) return 'Excited';
  return 'Chaotic';
}

export default useTerrarium;
