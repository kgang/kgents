/**
 * Daily Lab API Contracts
 *
 * CANONICAL SOURCE OF TRUTH for Daily Lab API aggregate response types.
 * Core types (TrailMark, TimeGap, CaptureRequest, CaptureResponse) are
 * defined in witness components and imported here.
 *
 * @layer L4 (Specification)
 * @backend protocols/api/daily_lab.py
 * @frontend pilots-web/src/api/witness.ts
 *
 * @see pilots/CONTRACT_COHERENCE.md
 * @see pilots/trail-to-crystal-daily-lab/PROTO_SPEC.md (L6, QA-5/6/7)
 */

// =============================================================================
// Core Types (imported from witness components)
// =============================================================================

// These types are the source of truth, defined in witness components
import type { TrailMark, TimeGap } from '../witness/TrailTimeline';
import type { CaptureResponse } from '../witness/MarkCaptureInput';

// =============================================================================
// API Response Contracts (aggregate types not in witness components)
// =============================================================================

/**
 * GET /api/witness/daily/trail response
 *
 * @invariant marks is array (may be empty)
 * @invariant gaps is array (may be empty)
 * @invariant date is ISO date string (YYYY-MM-DD)
 *
 * Backend: protocols/api/daily_lab.py:TrailResponse
 * Frontend: pilots-web/src/api/witness.ts:TrailResponse
 */
export interface TrailResponse {
  /** Marks for the day, sorted by timestamp */
  marks: TrailMark[];

  /** Computed gaps between marks (gaps > threshold) */
  gaps: TimeGap[];

  /** ISO date string (YYYY-MM-DD) */
  date: string;

  // Optional fields (have defaults on backend)
  total?: number;
  position?: number;
  gap_minutes?: number; // Legacy, deprecated - use gaps array
  review_prompt?: string;
}

/**
 * POST /api/witness/daily/crystallize response
 */
export interface CrystallizeResponse {
  crystal_id?: string;
  summary?: string;
  insight?: string;
  significance?: string;
  disclosure: string;
  compression_honesty?: CompressionHonestyResponse;
  success: boolean;
}

/**
 * Compression honesty disclosure
 */
export interface CompressionHonestyResponse {
  dropped_count: number;
  dropped_tags: string[];
  dropped_summaries: string[];
  galois_loss: number;
}

// =============================================================================
// Contract Invariants (for test verification)
// =============================================================================

/**
 * Runtime invariant checks for TrailResponse.
 *
 * Use in tests:
 * ```typescript
 * for (const [name, check] of Object.entries(TRAIL_RESPONSE_INVARIANTS)) {
 *   expect(check(response)).toBe(true);
 * }
 * ```
 */
export const TRAIL_RESPONSE_INVARIANTS = {
  'marks is array': (r: TrailResponse) => Array.isArray(r.marks),
  'gaps is array': (r: TrailResponse) => Array.isArray(r.gaps),
  'date is ISO string': (r: TrailResponse) =>
    typeof r.date === 'string' && /^\d{4}-\d{2}-\d{2}$/.test(r.date),
  'all marks have mark_id': (r: TrailResponse) =>
    r.marks.every((m) => typeof m.mark_id === 'string' && m.mark_id.length > 0),
  'all marks have timestamp': (r: TrailResponse) =>
    r.marks.every((m) => typeof m.timestamp === 'string'),
  'all gaps have positive duration': (r: TrailResponse) =>
    r.gaps.every((g) => typeof g.duration_minutes === 'number' && g.duration_minutes >= 0),
} as const;

/**
 * Runtime invariant checks for CaptureResponse.
 */
export const CAPTURE_RESPONSE_INVARIANTS = {
  'has mark_id': (r: CaptureResponse) =>
    typeof r.mark_id === 'string' && r.mark_id.length > 0,
  'has timestamp': (r: CaptureResponse) => typeof r.timestamp === 'string',
  'has warmth_response': (r: CaptureResponse) => typeof r.warmth_response === 'string',
} as const;

// =============================================================================
// Type Guards (for defensive coding)
// =============================================================================

/**
 * Type guard for TrailResponse.
 * Use when receiving data from API to ensure type safety.
 */
export function isTrailResponse(data: unknown): data is TrailResponse {
  if (!data || typeof data !== 'object') return false;
  const r = data as Record<string, unknown>;
  return (
    Array.isArray(r.marks) &&
    Array.isArray(r.gaps) &&
    typeof r.date === 'string'
  );
}

/**
 * Normalize a potentially malformed TrailResponse.
 * Ensures gaps is always an array (defensive for backend drift).
 */
export function normalizeTrailResponse(data: unknown): TrailResponse {
  const r = data as Partial<TrailResponse> & { marks?: unknown; gaps?: unknown; date?: unknown };
  return {
    marks: Array.isArray(r.marks) ? r.marks : [],
    gaps: Array.isArray(r.gaps) ? r.gaps : [],
    date: typeof r.date === 'string' ? r.date : new Date().toISOString().split('T')[0],
    total: typeof r.total === 'number' ? r.total : undefined,
    position: typeof r.position === 'number' ? r.position : undefined,
    gap_minutes: typeof r.gap_minutes === 'number' ? r.gap_minutes : undefined,
    review_prompt: typeof r.review_prompt === 'string' ? r.review_prompt : undefined,
  };
}
