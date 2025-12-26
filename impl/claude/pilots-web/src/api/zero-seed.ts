/**
 * Zero Seed Personal Governance API Client
 *
 * CANONICAL IMPORT: All types come from @kgents/shared-primitives
 * No local type definitions - contract coherence law (L6).
 *
 * Personality: "archaeology, not construction"
 * - We surface axioms, we don't create them
 * - Language emphasizes discovery over prescription
 *
 * @see pilots/zero-seed-personal-governance-lab/PROTO_SPEC.md
 * @see pilots/CONTRACT_COHERENCE.md
 */

// =============================================================================
// Type Imports - SINGLE SOURCE OF TRUTH
// =============================================================================

import type {
  DiscoveredAxiom,
  DiscoveryReport,
  ValidationResult,
  Constitution,
  ConstitutionContradiction,
  ContradictionReport,
  DiscoverAxiomsRequest,
  ValidateAxiomRequest,
  AddAxiomRequest,
  RetireAxiomRequest,
} from '@kgents/shared-primitives';

import { normalizeDiscoveryReport } from '@kgents/shared-primitives';

// Re-export types for convenience (but still from single source)
export type {
  DiscoveredAxiom,
  DiscoveryReport,
  ValidationResult,
  Constitution,
  ConstitutionContradiction,
  ContradictionReport,
};

// =============================================================================
// API Base Path
// =============================================================================

const API_BASE = '/api/zero-seed';

// =============================================================================
// API Error
// =============================================================================

export class ZeroSeedApiError extends Error {
  constructor(
    public readonly status: number,
    public readonly detail: string
  ) {
    super(`Zero Seed API Error (${status}): ${detail}`);
    this.name = 'ZeroSeedApiError';
  }
}

/**
 * Extract error message from FastAPI error response.
 *
 * FastAPI can return:
 * - { detail: "string message" }
 * - { detail: [{ type: "...", loc: [...], msg: "..." }, ...] } (validation errors)
 */
function extractErrorMessage(error: unknown, fallback: string): string {
  if (!error || typeof error !== 'object') return fallback;

  const e = error as Record<string, unknown>;

  // If detail is a string, use it directly
  if (typeof e.detail === 'string') {
    return e.detail;
  }

  // If detail is an array (validation errors), extract messages
  if (Array.isArray(e.detail)) {
    const messages = e.detail
      .map((item: unknown) => {
        if (typeof item === 'object' && item !== null) {
          const i = item as Record<string, unknown>;
          if (typeof i.msg === 'string') {
            const loc = Array.isArray(i.loc) ? i.loc.join('.') : '';
            return loc ? `${loc}: ${i.msg}` : i.msg;
          }
        }
        return null;
      })
      .filter(Boolean);

    return messages.length > 0 ? messages.join('; ') : fallback;
  }

  return fallback;
}

// =============================================================================
// Normalizers for Defensive Coding
// =============================================================================

/**
 * Normalize a ValidationResult response.
 */
function normalizeValidationResult(data: unknown): ValidationResult {
  const r = data as Partial<ValidationResult>;
  return {
    is_axiom:
      typeof r.is_axiom === 'boolean' ? r.is_axiom : false,
    is_fixed_point:
      typeof r.is_fixed_point === 'boolean' ? r.is_fixed_point : false,
    loss: typeof r.loss === 'number' ? Math.max(0, Math.min(1, r.loss)) : 1,
    stability:
      typeof r.stability === 'number'
        ? Math.max(0, Math.min(1, r.stability))
        : 1,
    iterations: typeof r.iterations === 'number' ? r.iterations : 0,
    losses: Array.isArray(r.losses) ? r.losses : [],
  };
}

/**
 * Normalize a ConstitutionContradiction response.
 */
function normalizeContradiction(
  data: unknown
): ConstitutionContradiction {
  const c = data as Partial<ConstitutionContradiction>;
  return {
    axiom_a_id: typeof c.axiom_a_id === 'string' ? c.axiom_a_id : '',
    axiom_b_id: typeof c.axiom_b_id === 'string' ? c.axiom_b_id : '',
    axiom_a_content:
      typeof c.axiom_a_content === 'string' ? c.axiom_a_content : '',
    axiom_b_content:
      typeof c.axiom_b_content === 'string' ? c.axiom_b_content : '',
    strength: typeof c.strength === 'number' ? c.strength : 0,
    type:
      c.type === 'none' || c.type === 'weak' ||
      c.type === 'moderate' || c.type === 'strong'
        ? c.type
        : 'none',
    synthesis_hint:
      typeof c.synthesis_hint === 'string' ? c.synthesis_hint : undefined,
    detected_at: typeof c.detected_at === 'string' ? c.detected_at : '',
    resolved: typeof c.resolved === 'boolean' ? c.resolved : false,
    resolution: typeof c.resolution === 'string' ? c.resolution : undefined,
  };
}

/**
 * Normalize a Constitution response.
 */
function normalizeConstitution(data: unknown): Constitution {
  const c = data as Partial<Constitution>;
  return {
    id: typeof c.id === 'string' ? c.id : '',
    name: typeof c.name === 'string' ? c.name : 'Personal Constitution',
    axioms:
      typeof c.axioms === 'object' && c.axioms !== null ? c.axioms : {},
    contradictions: Array.isArray(c.contradictions)
      ? c.contradictions.map(normalizeContradiction)
      : [],
    snapshots: Array.isArray(c.snapshots) ? c.snapshots : [],
    active_count: typeof c.active_count === 'number' ? c.active_count : 0,
    average_loss:
      typeof c.average_loss === 'number'
        ? Math.max(0, Math.min(1, c.average_loss))
        : 0,
    created_at: typeof c.created_at === 'string' ? c.created_at : '',
    updated_at: typeof c.updated_at === 'string' ? c.updated_at : '',
  };
}

/**
 * Normalize a ContradictionReport response.
 */
function normalizeContradictionReport(data: unknown): ContradictionReport {
  const r = data as Partial<ContradictionReport>;
  return {
    contradictions: Array.isArray(r.contradictions)
      ? r.contradictions.map(normalizeContradiction)
      : [],
    total_axioms: typeof r.total_axioms === 'number' ? r.total_axioms : 0,
    pairs_checked: typeof r.pairs_checked === 'number' ? r.pairs_checked : 0,
  };
}

// =============================================================================
// API Client Functions
// =============================================================================

/**
 * Discover axioms from a corpus of text.
 *
 * This surfaces patterns that qualify as semantic fixed points.
 * Language: "We found traces of..." not "You should believe..."
 *
 * Endpoint: POST /api/zero-seed/discover-axioms
 */
export async function discoverAxioms(
  request?: DiscoverAxiomsRequest
): Promise<DiscoveryReport> {
  // Build request body - decisions array is required by backend
  // If no mark_ids provided, we send an empty array for demo
  const body = {
    decisions: request?.mark_ids ?? [],
    min_pattern_occurrences: request?.min_occurrences ?? 2,
  };

  const response = await fetch(`${API_BASE}/discover-axioms`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(body),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new ZeroSeedApiError(
      response.status,
      extractErrorMessage(error, 'Failed to discover axioms')
    );
  }

  // DEFENSIVE: Use normalizeDiscoveryReport to handle potential backend drift
  const data: unknown = await response.json();
  return normalizeDiscoveryReport(data);
}

/**
 * Discover axioms from raw text corpus.
 *
 * Surfaces patterns from journal entries, decisions, or other text.
 *
 * Endpoint: POST /api/zero-seed/discover-axioms
 */
export async function discoverAxiomsFromText(
  texts: string[],
  options?: {
    minOccurrences?: number;
  }
): Promise<DiscoveryReport> {
  const body = {
    decisions: texts,
    min_pattern_occurrences: options?.minOccurrences ?? 2,
  };

  const response = await fetch(`${API_BASE}/discover-axioms`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(body),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new ZeroSeedApiError(
      response.status,
      extractErrorMessage(error, 'Failed to discover axioms from text')
    );
  }

  const data: unknown = await response.json();
  return normalizeDiscoveryReport(data);
}

/**
 * Validate a single axiom candidate.
 *
 * Checks if content qualifies as a semantic fixed point (L < 0.05).
 *
 * Endpoint: POST /api/zero-seed/validate-axiom
 */
export async function validateAxiom(
  content: string,
  options?: ValidateAxiomRequest
): Promise<ValidationResult> {
  const params = new URLSearchParams();
  params.set('content', content);

  if (options?.threshold !== undefined) {
    params.set('threshold', String(options.threshold));
  }

  const response = await fetch(
    `${API_BASE}/validate-axiom?${params.toString()}`,
    {
      method: 'POST',
    }
  );

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new ZeroSeedApiError(
      response.status,
      extractErrorMessage(error, 'Failed to validate axiom')
    );
  }

  const data: unknown = await response.json();
  return normalizeValidationResult(data);
}

/**
 * Get the current personal constitution.
 *
 * Returns all axioms with their status and metadata.
 *
 * Endpoint: GET /api/zero-seed/constitution
 */
export async function getConstitution(): Promise<Constitution> {
  const response = await fetch(`${API_BASE}/constitution`);

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new ZeroSeedApiError(
      response.status,
      extractErrorMessage(error, 'Failed to fetch constitution')
    );
  }

  const data: unknown = await response.json();
  return normalizeConstitution(data);
}

/**
 * Add an axiom to the personal constitution.
 *
 * First validates the content, then adds it.
 * Optionally checks for contradictions with existing axioms.
 *
 * Endpoint: POST /api/zero-seed/constitution/add
 */
export async function addAxiomToConstitution(
  axiom: DiscoveredAxiom,
  options?: Omit<AddAxiomRequest, 'axiom'>
): Promise<Constitution> {
  const params = new URLSearchParams();
  params.set('content', axiom.content);

  if (options?.check_contradictions !== undefined) {
    params.set('check_contradictions', String(options.check_contradictions));
  }

  const response = await fetch(
    `${API_BASE}/constitution/add?${params.toString()}`,
    {
      method: 'POST',
    }
  );

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new ZeroSeedApiError(
      response.status,
      extractErrorMessage(error, 'Failed to add axiom to constitution')
    );
  }

  const data: unknown = await response.json();
  return normalizeConstitution(data);
}

/**
 * Retire an axiom from the personal constitution.
 *
 * Requires a reason for retirement (reflection, not arbitrary deletion).
 *
 * Endpoint: POST /api/zero-seed/constitution/retire
 */
export async function retireAxiom(
  request: RetireAxiomRequest
): Promise<Constitution> {
  const response = await fetch(`${API_BASE}/constitution/retire`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new ZeroSeedApiError(
      response.status,
      extractErrorMessage(error, 'Failed to retire axiom')
    );
  }

  const data: unknown = await response.json();
  return normalizeConstitution(data);
}

/**
 * Detect contradictions between axioms in the constitution.
 *
 * Uses super-additive loss: L(A U B) > L(A) + L(B) + tau
 * Surfaces tensions for exploration, not judgment.
 *
 * Endpoint: POST /api/zero-seed/detect-contradictions
 */
export async function detectContradictions(
  tolerance?: number
): Promise<ContradictionReport> {
  const params = new URLSearchParams();

  if (tolerance !== undefined) {
    params.set('tolerance', String(tolerance));
  }

  const url = params.toString()
    ? `${API_BASE}/detect-contradictions?${params.toString()}`
    : `${API_BASE}/detect-contradictions`;

  const response = await fetch(url, {
    method: 'POST',
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new ZeroSeedApiError(
      response.status,
      extractErrorMessage(error, 'Failed to detect contradictions')
    );
  }

  const data: unknown = await response.json();
  return normalizeContradictionReport(data);
}

// =============================================================================
// Convenience Helpers
// =============================================================================

/**
 * Get loss classification label.
 *
 * Archaeology language: describes what was found, not what to believe.
 */
export function getLossClassification(loss: number): {
  label: string;
  description: string;
  tier: 'axiom' | 'strong' | 'moderate' | 'weak';
} {
  if (loss < 0.05) {
    return {
      label: 'Axiom',
      description: 'This pattern survived all restructuring unchanged',
      tier: 'axiom',
    };
  } else if (loss < 0.2) {
    return {
      label: 'Strong Value',
      description: 'This pattern is highly stable across contexts',
      tier: 'strong',
    };
  } else if (loss < 0.5) {
    return {
      label: 'Emerging Pattern',
      description: 'This pattern appears frequently but varies by context',
      tier: 'moderate',
    };
  } else {
    return {
      label: 'Surface Preference',
      description: 'This pattern changes with context',
      tier: 'weak',
    };
  }
}

/**
 * Get contradiction type description.
 *
 * Clarifying, not judgmental language.
 */
export function getContradictionDescription(
  type: ConstitutionContradiction['type']
): string {
  switch (type) {
    case 'strong':
      return 'These patterns pull strongly in different directions';
    case 'moderate':
      return 'There is some tension between these patterns';
    case 'weak':
      return 'These patterns have a slight tension worth noting';
    case 'none':
    default:
      return 'No significant tension detected';
  }
}
