/**
 * KGENTS GLYPH SYSTEM
 *
 * Philosophy:
 * - Mathematical notation + ancient glyphs aesthetic
 * - Flat geometric precision, monochrome + single accent
 * - Stillness then breath (4-7-8 asymmetric timing)
 * - AVOID: trends, 3D, glassmorphism, gradients, Y2K metallic
 * - EMBRACE: steel surfaces, categorical precision, earned glow
 *
 * Usage:
 *   import { GLYPHS } from './glyphs';
 *   const statusGlyph = GLYPHS.status.healthy; // '●'
 */

export const GLYPHS = {
  /**
   * Status indicators — geometric precision
   * ● = filled (active, healthy)
   * ◐ = half-filled (degraded, partial)
   * ○ = hollow (dormant, inactive)
   * ◆ = solid diamond (error, attention)
   * ◇ = hollow diamond (warning, caution)
   * ◎ = double circle (pending, processing)
   */
  status: {
    healthy: '●',
    degraded: '◐',
    dormant: '○',
    error: '◆',
    warning: '◇',
    pending: '◎',
  },

  /**
   * AGENTESE contexts — the five-fold ontology
   * world.* — The External (entities, environments, tools)
   * self.* — The Internal (memory, capability, state)
   * concept.* — The Abstract (platonics, definitions, logic)
   * void.* — The Accursed Share (entropy, serendipity, gratitude)
   * time.* — The Temporal (traces, forecasts, schedules)
   */
  contexts: {
    world: '∴',    // therefore (external causality)
    self: '∵',     // because (internal causality)
    concept: '⟨⟩',  // angle brackets (abstraction)
    void: '∅',     // empty set (the accursed share)
    time: '⟳',     // anticlockwise gapped circle arrow (temporal flow)
  },

  /**
   * Actions — proof-engine operations
   * ⊢ = turnstile (witness, proof)
   * ⊨ = double turnstile (decide, semantic consequence)
   * ∘ = ring operator (compose)
   * ⊕ = circled plus (save, add)
   * ⌕ = telephone location sign (search)
   * ⊛ = circled asterisk (analyze, star)
   * ⎔ = software-function symbol (edit)
   * ⊖ = circled minus (delete, remove)
   */
  actions: {
    witness: '⊢',
    decide: '⊨',
    compose: '∘',
    save: '⊕',
    search: '⌕',
    analyze: '⊛',
    edit: '⎔',
    delete: '⊖',
  },

  /**
   * Axioms — the seven principles
   * ◇ = white diamond (entity)
   * ◈ = white diamond containing black small diamond (morphism)
   * ◉ = fisheye (mirror)
   * ✧ = open star (tasteful)
   * ⊛ = circled asterisk (composable)
   * ⥮ = upwards harpoon with barb left from bar (heterarchical)
   * ⟐ = double not sign (generative)
   */
  axioms: {
    entity: '◇',
    morphism: '◈',
    mirror: '◉',
    tasteful: '✧',
    composable: '⊛',
    heterarchical: '⥮',
    generative: '⟐',
  },

  /**
   * Navigation — directional glyphs
   * Simple arrows for clarity
   */
  navigation: {
    back: '←',
    forward: '→',
    up: '↑',
    down: '↓',
    expand: '⌄',   // down-pointing wedge
    collapse: '⌃',  // up-pointing wedge
    menu: '☰',     // trigram for heaven
  },

  /**
   * Files — document types
   * ▫ = white small square (file)
   * ▪ = black small square (folder)
   * ◈ = white diamond containing black small diamond (spec)
   * ⟨⟩ = angle brackets (code)
   */
  files: {
    file: '▫',
    folder: '▪',
    spec: '◈',
    code: '⟨⟩',
  },

  /**
   * Crown Jewels — service identities
   * ◬ = white up-pointing triangle with dot (brain)
   * ⊢ = turnstile (witness)
   * ⌬ = benzene ring (atelier)
   * ◭ = white up-pointing triangle containing white triangle (liminal)
   */
  jewels: {
    brain: '◬',
    witness: '⊢',
    atelier: '⌬',
    liminal: '◭',
  },

  /**
   * Hypergraph modes — modal editing
   * ◇ = white diamond (normal)
   * ◈ = white diamond containing black small diamond (insert)
   * ⟡ = lozenge divided by horizontal rule (edge)
   * ◉ = fisheye (visual)
   * ⊢ = turnstile (witness)
   */
  modes: {
    normal: '◇',
    insert: '◈',
    edge: '⟡',
    visual: '◉',
    witness: '⊢',
  },
} as const;

/**
 * Type-safe glyph lookup by dot notation
 * Example: getGlyph('status.healthy') → '●'
 */
export function getGlyph(path: string): string | undefined {
  const parts = path.split('.');
  let current: any = GLYPHS;

  for (const part of parts) {
    if (current && typeof current === 'object' && part in current) {
      current = current[part];
    } else {
      return undefined;
    }
  }

  return typeof current === 'string' ? current : undefined;
}

/**
 * All glyph categories for iteration/exploration
 */
export const GLYPH_CATEGORIES = Object.keys(GLYPHS) as Array<keyof typeof GLYPHS>;

/**
 * Get all glyphs in a category
 */
export function getGlyphCategory(category: keyof typeof GLYPHS): Record<string, string> {
  return GLYPHS[category];
}
