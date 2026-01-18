/**
 * Provenance Types — Anti-Sloppification System
 *
 * Grounded in: spec/ui/axioms.md — A2 (Sloppification Axiom)
 * "LLMs touching something inherently sloppifies it."
 *
 * The UI must make sloppification VISIBLE. Every AI-touched element
 * must be distinguishable from human-authored elements.
 */

/**
 * Author types for content provenance.
 * Maps to backend Mark.origin + CreateMarkRequest.author
 */
export type Author = 'kent' | 'claude' | 'fusion';

/**
 * Review status for AI-generated content.
 * AI content starts unreviewed and must be explicitly reviewed.
 */
export type ReviewStatus = 'unreviewed' | 'reviewed' | 'confirmed';

/**
 * Complete provenance information for a piece of content.
 */
export interface Provenance {
  /** Who created this content */
  author: Author;

  /** Confidence in authorship attribution (0-1) */
  confidence: number;

  /** Has human reviewed AI content? */
  reviewed: boolean;

  /** How likely is this content to be sloppy? (0-1) */
  sloppification_risk: number;

  /** Evidence for provenance assessment */
  evidence: string[];

  /** When was this content created? */
  created_at: string;

  /** When was it reviewed (if applicable)? */
  reviewed_at?: string;

  /** Who reviewed it? */
  reviewed_by?: string;

  /** If fusion, what dialectic decision produced it? */
  fusion_id?: string;
}

/**
 * Provenance for a specific line range in a document.
 */
export interface ProvenanceRange {
  /** Start line (1-indexed) */
  start: number;

  /** End line (1-indexed, inclusive) */
  end: number;

  /** Provenance for this range */
  provenance: Provenance;
}

/**
 * Visual encoding for provenance display.
 */
export const PROVENANCE_INTENSITY: Record<Author, string> = {
  kent: 'var(--fg-intense)', // Full intensity — human authored
  fusion: 'var(--fg-intense)', // Full intensity + marker — synthesis
  claude: 'var(--fg-secondary)', // Low intensity — AI generated
};

/**
 * Indicator symbols for provenance status.
 */
export const PROVENANCE_INDICATORS = {
  /** Fusion synthesis marker */
  fusion: '⚡',

  /** Reviewed AI content */
  reviewed: '◇',

  /** Unreviewed AI content (needs attention) */
  unreviewed: '◆',
} as const;

/**
 * CSS classes for provenance styling.
 */
export const PROVENANCE_CLASSES: Record<Author, string> = {
  kent: 'provenance-human',
  fusion: 'provenance-fusion',
  claude: 'provenance-ai',
};

/**
 * Create default provenance for human-authored content.
 */
export function createHumanProvenance(): Provenance {
  return {
    author: 'kent',
    confidence: 1.0,
    reviewed: true,
    sloppification_risk: 0,
    evidence: ['Human authored'],
    created_at: new Date().toISOString(),
  };
}

/**
 * Create default provenance for AI-generated content.
 */
export function createAIProvenance(): Provenance {
  return {
    author: 'claude',
    confidence: 0.9,
    reviewed: false,
    sloppification_risk: 0.5, // Moderate risk until reviewed
    evidence: ['AI generated', 'Awaiting review'],
    created_at: new Date().toISOString(),
  };
}

/**
 * Create provenance for fusion (dialectic synthesis).
 */
export function createFusionProvenance(fusionId: string): Provenance {
  return {
    author: 'fusion',
    confidence: 0.95,
    reviewed: true, // Fusion is inherently reviewed (dialectic process)
    sloppification_risk: 0.2, // Low risk — human involved in synthesis
    evidence: ['Dialectic synthesis', `Fusion ID: ${fusionId}`],
    created_at: new Date().toISOString(),
    fusion_id: fusionId,
  };
}

/**
 * Determine if content needs review based on provenance.
 */
export function needsReview(provenance: Provenance): boolean {
  return provenance.author === 'claude' && !provenance.reviewed;
}

/**
 * Get the appropriate CSS class for provenance display.
 */
export function getProvenanceClass(provenance: Provenance): string {
  if (provenance.author === 'claude' && !provenance.reviewed) {
    return 'provenance-ai-unreviewed';
  }
  if (provenance.author === 'claude' && provenance.reviewed) {
    return 'provenance-ai-reviewed';
  }
  return PROVENANCE_CLASSES[provenance.author];
}

/**
 * Get the indicator symbol for provenance display.
 */
export function getProvenanceIndicator(provenance: Provenance): string | null {
  if (provenance.author === 'fusion') {
    return PROVENANCE_INDICATORS.fusion;
  }
  if (provenance.author === 'claude') {
    return provenance.reviewed ? PROVENANCE_INDICATORS.reviewed : PROVENANCE_INDICATORS.unreviewed;
  }
  return null; // Human content has no indicator
}
