/**
 * Voice Anchors — Kent's authentic voice preserved
 *
 * These phrases are from _focus.md. Quote them directly — never paraphrase.
 * The Anti-Sausage Protocol exists because LLM processing smooths rough edges.
 * These anchors preserve the daring, opinionated stance.
 *
 * @see CLAUDE.md Anti-Sausage Protocol
 * @see plans/_focus.md Kent's wishes
 */

export interface VoiceAnchor {
  /** The exact quote — no paraphrasing */
  quote: string;
  /** When to invoke this anchor */
  use: string;
  /** Source attribution */
  source: string;
}

/**
 * Kent's voice anchors — the core principles that guide kgents.
 * Rotating display keeps the garden alive.
 */
export const VOICE_ANCHORS: readonly VoiceAnchor[] = [
  {
    quote: 'Daring, bold, creative, opinionated but not gaudy',
    use: 'Making aesthetic decisions',
    source: '_focus.md',
  },
  {
    quote: 'The Mirror Test: Does K-gent feel like me on my best day?',
    use: 'Evaluating if something feels right',
    source: '_focus.md',
  },
  {
    quote: 'Tasteful > feature-complete',
    use: 'Scoping work',
    source: '_focus.md',
  },
  {
    quote: 'The persona is a garden, not a museum',
    use: 'Discussing evolution vs. preservation',
    source: '_focus.md',
  },
  {
    quote: 'Depth over breadth',
    use: 'Prioritizing work',
    source: '_focus.md',
  },
  {
    quote: 'Joy-inducing > merely functional',
    use: 'Always',
    source: '_focus.md',
  },
] as const;

/**
 * Session Start Ritual checklist items.
 * Claude grounds in these before suggesting work.
 */
export const SESSION_RITUAL_ITEMS = [
  { id: 'ground', label: 'Ground in voice anchors', detail: 'Read a rotating quote, feel the intent' },
  { id: 'now', label: 'Check NOW.md for context', detail: "What's happening in the project?" },
  { id: 'review', label: 'Review what needs doing', detail: 'Status of Crown Jewels, open work' },
  { id: 'anti-sausage', label: 'Remember Anti-Sausage Check at end', detail: "Don't smooth the rough edges" },
] as const;

/**
 * Anti-Sausage Check questions.
 * Before ending a session, ask these to preserve voice.
 */
export const ANTI_SAUSAGE_QUESTIONS = [
  { id: 'smooth', question: 'Did I smooth anything that should stay rough?' },
  { id: 'words', question: "Did I add words Kent wouldn't use?" },
  { id: 'stance', question: 'Did I lose any opinionated stances?' },
  { id: 'safe', question: 'Is this still daring, bold, creative—or did I make it safe?' },
] as const;

/**
 * Get a random voice anchor for display.
 * Weighted to avoid immediate repeats via optional exclusion.
 */
export function getRandomAnchor(excludeQuote?: string): VoiceAnchor {
  const available = excludeQuote
    ? VOICE_ANCHORS.filter((a) => a.quote !== excludeQuote)
    : VOICE_ANCHORS;

  const index = Math.floor(Math.random() * available.length);
  return available[index] ?? VOICE_ANCHORS[0];
}
