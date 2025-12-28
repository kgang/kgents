/**
 * Sprite Procedural Taste Lab API Client
 *
 * "Every character has a story. The pixels are just how you hear it."
 *
 * This client integrates with the witness and galois APIs to:
 * - Emit mutation marks with rationale (L3: Mutation Justification Law)
 * - Compute Galois loss for style drift
 * - Create crystals for style stability proof
 *
 * CANONICAL IMPORT: All types from @kgents/shared-primitives
 *
 * @see pilots/sprite-procedural-taste-lab/PROTO_SPEC.md
 * @see pilots/CONTRACT_COHERENCE.md
 */

import type {
  Sprite,
  Mutation,
  MutationRationale,
  StyleBranch,
  StyleTrace,
  StyleCrystal,
  TasteAttractor,
  ProposeMutationRequest,
  ProposeMutationResponse,
  AcceptMutationRequest,
  CreateWildBranchRequest,
  CollapseBranchRequest,
  CrystallizeRequest,
} from '@kgents/shared-primitives';

import {
  normalizeMutation,
  normalizeTasteAttractor,
  DEMO_SPRITES,
  DEMO_TRACE,
} from '@kgents/shared-primitives';

// =============================================================================
// Re-exports for convenience
// =============================================================================

export type {
  Sprite,
  Mutation,
  MutationRationale,
  StyleBranch,
  StyleTrace,
  StyleCrystal,
  TasteAttractor,
  ProposeMutationRequest,
  ProposeMutationResponse,
  AcceptMutationRequest,
  CreateWildBranchRequest,
  CollapseBranchRequest,
  CrystallizeRequest,
};

export { normalizeMutation, normalizeTasteAttractor, DEMO_SPRITES, DEMO_TRACE };

// =============================================================================
// API Base
// =============================================================================

const WITNESS_API = '/api/witness';
const GALOIS_API = '/api/galois';

// =============================================================================
// Error Handling (HQ-2 Compliant)
// =============================================================================

export class SpriteApiError extends Error {
  constructor(
    public readonly status: number,
    public readonly detail: string
  ) {
    super(`Sprite API Error (${status}): ${detail}`);
    this.name = 'SpriteApiError';
  }
}

/**
 * Extract error message from API response (HQ-2: Error Normalization Law)
 */
export function extractErrorMessage(error: unknown, fallback: string): string {
  const e = error as Record<string, unknown>;

  // String detail (normal error)
  if (typeof e?.detail === 'string') return e.detail;

  // Array detail (FastAPI validation errors)
  if (Array.isArray(e?.detail)) {
    return e.detail.map((i: { msg?: string }) => i.msg).filter(Boolean).join('; ');
  }

  // Error with message property
  if (e instanceof Error) return e.message;

  return fallback;
}

// =============================================================================
// Witness Integration - Mutation Marks
// =============================================================================

interface MarkRequest {
  action: string;
  reasoning: string;
  principles: string[];
  domain: string;
}

interface MarkResponse {
  id: string;
  action: string;
  reasoning?: string;
  principles: string[];
  timestamp: string;
}

/**
 * Emit a witness mark for a mutation decision.
 * L3: Every accepted mutation has a stated reason.
 */
export async function emitMutationMark(
  mutation: Mutation,
  rationale: MutationRationale,
  status: 'accepted' | 'rejected' | 'wild'
): Promise<MarkResponse> {
  const action = `[SPRITE-TASTE] Mutation ${status}: ${mutation.change_description}`;
  const reasoning = rationale.reason;
  const principles = ['taste-evolution', ...rationale.affected_dimensions];

  const response = await fetch(`${WITNESS_API}/marks`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      action,
      reasoning,
      principles,
      domain: 'sprite-procedural-taste-lab',
    } satisfies MarkRequest),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new SpriteApiError(response.status, extractErrorMessage(error, 'Failed to emit mark'));
  }

  return response.json();
}

/**
 * Emit a crystal creation mark.
 * L5: Style Continuity Law - crystal justifies stability.
 */
export async function emitCrystalMark(crystal: StyleCrystal): Promise<MarkResponse> {
  const action = `[SPRITE-TASTE] Crystal created: ${crystal.journey_summary.slice(0, 80)}...`;
  const reasoning = crystal.stability_justification;

  const response = await fetch(`${WITNESS_API}/marks`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      action,
      reasoning,
      principles: ['style-continuity', 'taste-gravity'],
      domain: 'sprite-procedural-taste-lab',
    } satisfies MarkRequest),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new SpriteApiError(response.status, extractErrorMessage(error, 'Failed to emit crystal mark'));
  }

  return response.json();
}

// =============================================================================
// Galois Integration - Style Loss
// =============================================================================

interface GaloisLossRequest {
  content: string;
}

interface GaloisLossResponse {
  loss: number;
  method: string;
  cached: boolean;
}

/**
 * Compute Galois loss for a mutation relative to current style.
 * Used to determine if a mutation is canonical or wild.
 */
export async function computeStyleLoss(
  currentStyle: string,
  proposedChange: string
): Promise<number> {
  const content = `Current style: ${currentStyle}\n\nProposed change: ${proposedChange}`;

  const response = await fetch(`${GALOIS_API}/loss`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ content } satisfies GaloisLossRequest),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new SpriteApiError(response.status, extractErrorMessage(error, 'Failed to compute loss'));
  }

  const result: GaloisLossResponse = await response.json();
  return result.loss;
}

// =============================================================================
// Local State Management (Simulated API)
// =============================================================================

// For this implementation, we store state locally but emit real marks
// Future: full backend with persistent storage

let currentTrace: StyleTrace = { ...DEMO_TRACE };
let currentSprites: Sprite[] = [...DEMO_SPRITES];

/**
 * Get the current style trace.
 */
export function getStyleTrace(): StyleTrace {
  return currentTrace;
}

/**
 * Get all sprites.
 */
export function getSprites(): Sprite[] {
  return currentSprites;
}

/**
 * Get a sprite by ID.
 */
export function getSprite(id: string): Sprite | undefined {
  return currentSprites.find((s) => s.id === id);
}

/**
 * Update the style trace (local mutation).
 */
export function updateStyleTrace(trace: StyleTrace): void {
  currentTrace = trace;
}

/**
 * Add a sprite.
 */
export function addSprite(sprite: Sprite): void {
  currentSprites = [...currentSprites, sprite];
}

/**
 * Update a sprite.
 */
export function updateSprite(sprite: Sprite): void {
  currentSprites = currentSprites.map((s) => (s.id === sprite.id ? sprite : s));
}

// =============================================================================
// Flavor-Specific: Fox/Kitten/Seal Characters (L-FLAV Laws)
// =============================================================================

export type AnimalTheme = 'fox' | 'kitten' | 'seal';

export interface AnimalTraits {
  theme: AnimalTheme;
  colorBase: string[];
  movementStyle: string;
  personalityTraits: string[];
  idleAnimation: string;
}

/**
 * Animal theme definitions for L-FLAV-1 through L-FLAV-4.
 */
export const ANIMAL_THEMES: Record<AnimalTheme, AnimalTraits> = {
  fox: {
    theme: 'fox',
    colorBase: ['#D35400', '#E67E22', '#F39C12', '#FDEBD0', '#FFFFFF'],
    movementStyle: 'cunning, quick, agile with sudden pauses',
    personalityTraits: ['clever', 'mischievous', 'curious', 'alert'],
    idleAnimation: 'ears twitch, tail sways, occasional quick glance',
  },
  kitten: {
    theme: 'kitten',
    colorBase: ['#95A5A6', '#BDC3C7', '#ECF0F1', '#FAD7A0', '#F5B041'],
    movementStyle: 'playful, bouncy, bursts of energy then stillness',
    personalityTraits: ['playful', 'curious', 'energetic', 'affectionate'],
    idleAnimation: 'paw kneads, tail flicks, wide curious eyes',
  },
  seal: {
    theme: 'seal',
    colorBase: ['#34495E', '#5D6D7E', '#85929E', '#D5DBDB', '#F8F9F9'],
    movementStyle: 'graceful, flowing, smooth undulation',
    personalityTraits: ['graceful', 'sleek', 'aquatic', 'gentle'],
    idleAnimation: 'gentle sway, whiskers wiggle, content expression',
  },
};

/**
 * Get random demo sprite with animal theme.
 */
export function createThemedDemoSprite(theme: AnimalTheme): Sprite {
  const traits = ANIMAL_THEMES[theme];
  const id = `${theme}-${Date.now()}`;

  return {
    id,
    name: `${theme.charAt(0).toUpperCase() + theme.slice(1)} Character`,
    width: 8,
    height: 8,
    palette: traits.colorBase,
    pixels: generateThemedPixels(theme),
    weights: [
      { dimension: 'warmth', value: theme === 'kitten' ? 0.8 : 0.5 },
      { dimension: 'agility', value: theme === 'fox' ? 0.9 : 0.6 },
      { dimension: 'grace', value: theme === 'seal' ? 0.9 : 0.5 },
    ],
  };
}

/**
 * Generate themed pixel data for a simple 8x8 character.
 */
function generateThemedPixels(theme: AnimalTheme): number[] {
  // Simple procedural patterns based on animal silhouettes
  const patterns: Record<AnimalTheme, number[]> = {
    fox: [
      // Fox silhouette with pointed ears
      0, 1, 0, 0, 0, 0, 1, 0,
      1, 2, 1, 0, 0, 1, 2, 1,
      0, 2, 2, 2, 2, 2, 2, 0,
      0, 1, 3, 2, 2, 3, 1, 0,
      0, 0, 2, 2, 2, 2, 0, 0,
      0, 0, 1, 2, 2, 1, 0, 0,
      0, 1, 0, 1, 1, 0, 1, 0,
      1, 0, 0, 0, 0, 0, 0, 1,
    ],
    kitten: [
      // Kitten with round face and ears
      0, 1, 0, 0, 0, 0, 1, 0,
      0, 1, 1, 0, 0, 1, 1, 0,
      0, 1, 2, 2, 2, 2, 1, 0,
      0, 2, 3, 2, 2, 3, 2, 0,
      0, 2, 2, 4, 4, 2, 2, 0,
      0, 0, 2, 2, 2, 2, 0, 0,
      0, 0, 1, 2, 2, 1, 0, 0,
      0, 1, 0, 0, 0, 0, 1, 0,
    ],
    seal: [
      // Seal with smooth, rounded body
      0, 0, 1, 2, 2, 1, 0, 0,
      0, 1, 2, 3, 3, 2, 1, 0,
      0, 2, 3, 4, 4, 3, 2, 0,
      0, 2, 2, 3, 3, 2, 2, 0,
      0, 1, 2, 2, 2, 2, 1, 0,
      0, 0, 1, 2, 2, 1, 0, 0,
      0, 0, 0, 1, 1, 0, 0, 0,
      0, 0, 0, 0, 0, 0, 0, 0,
    ],
  };

  return patterns[theme];
}
