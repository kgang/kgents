/**
 * Dialectic Decision Types
 *
 * "Kent's view + Claude's view → a third thing, better than either."
 * "The proof IS the decision. The mark IS the witness."
 */

export interface DialecticPosition {
  /** Author of this position */
  author: 'kent' | 'claude';

  /** The position statement */
  content: string;

  /** Reasoning supporting this position */
  reasoning: string;
}

export interface DialecticDecision {
  /** Unique decision ID */
  id: string;

  /** ISO timestamp */
  timestamp: string;

  /** Kent's thesis */
  thesis: DialecticPosition;

  /** Claude's antithesis */
  antithesis: DialecticPosition;

  /** The synthesized resolution */
  synthesis: string;

  /** Justification for the synthesis */
  why: string;

  /** Whether Kent vetoed this fusion */
  vetoed?: boolean;

  /** Veto reasoning (if vetoed) */
  vetoReason?: string;

  /** Associated tags/principles */
  tags: string[];
}

export interface QuickDecisionInput {
  /** Single-line decision */
  decision: string;

  /** Quick reasoning */
  reasoning: string;

  /** Tags */
  tags?: string[];
}

export interface FullDialecticInput {
  /** Kent's position */
  thesis: Omit<DialecticPosition, 'author'>;

  /** Claude's position */
  antithesis: Omit<DialecticPosition, 'author'>;

  /** Synthesis */
  synthesis: string;

  /** Why this synthesis */
  why: string;

  /** Tags */
  tags?: string[];
}

export type DecisionInput = QuickDecisionInput | FullDialecticInput;

export function isQuickDecision(input: DecisionInput): input is QuickDecisionInput {
  return 'decision' in input;
}

export function isFullDialectic(input: DecisionInput): input is FullDialecticInput {
  return 'thesis' in input && 'antithesis' in input;
}
