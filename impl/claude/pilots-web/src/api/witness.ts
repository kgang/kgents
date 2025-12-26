/**
 * Daily Lab Witness API Client
 *
 * CANONICAL IMPORT: All types come from @kgents/shared-primitives
 * No local type definitions - contract coherence law (L6).
 *
 * @see pilots/CONTRACT_COHERENCE.md
 * @see pilots/trail-to-crystal-daily-lab/PROTO_SPEC.md
 */

// =============================================================================
// Type Imports - SINGLE SOURCE OF TRUTH
// =============================================================================

import type {
  CaptureRequest,
  CaptureResponse,
  TrailResponse,
  CrystallizeResponse,
} from '@kgents/shared-primitives';

import { normalizeTrailResponse } from '@kgents/shared-primitives';

// Re-export types for convenience (but still from single source)
export type { CaptureRequest, CaptureResponse, TrailResponse, CrystallizeResponse };

// =============================================================================
// API Base Path
// =============================================================================

const API_BASE = '/api/witness/daily';

// =============================================================================
// Export Response (local type - not in shared-primitives yet)
// =============================================================================

export interface ExportResponse {
  content: string;
  format: 'markdown' | 'json';
  date: string;
  warmth_response: string;
}

// =============================================================================
// API Error
// =============================================================================

export class WitnessApiError extends Error {
  constructor(
    public readonly status: number,
    public readonly detail: string
  ) {
    super(`Witness API Error (${status}): ${detail}`);
    this.name = 'WitnessApiError';
  }
}

// =============================================================================
// API Client
// =============================================================================

/**
 * Capture a new daily mark.
 *
 * Endpoints: POST /api/witness/daily/capture
 */
export async function captureMark(request: CaptureRequest): Promise<CaptureResponse> {
  const response = await fetch(`${API_BASE}/capture`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new WitnessApiError(response.status, error.detail ?? 'Capture failed');
  }

  return response.json();
}

/**
 * Get today's trail of marks.
 *
 * Endpoints: GET /api/witness/daily/trail
 *
 * Uses defensive normalizeTrailResponse() to handle potential backend drift.
 */
export async function getTrail(options?: {
  date?: string;
  importantOnly?: boolean;
}): Promise<TrailResponse> {
  const params = new URLSearchParams();

  if (options?.date) {
    params.set('target_date', options.date);
  }
  if (options?.importantOnly) {
    params.set('important_only', 'true');
  }

  const url = params.toString()
    ? `${API_BASE}/trail?${params.toString()}`
    : `${API_BASE}/trail`;

  const response = await fetch(url);

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new WitnessApiError(response.status, error.detail ?? 'Failed to fetch trail');
  }

  // DEFENSIVE: Use normalizeTrailResponse to handle potential backend drift
  const data: unknown = await response.json();
  return normalizeTrailResponse(data);
}

/**
 * Crystallize the day's marks into a compressed insight.
 *
 * Endpoints: POST /api/witness/daily/crystallize
 */
export async function crystallizeDay(options?: {
  date?: string;
}): Promise<CrystallizeResponse> {
  const params = new URLSearchParams();

  if (options?.date) {
    params.set('target_date', options.date);
  }

  const url = params.toString()
    ? `${API_BASE}/crystallize?${params.toString()}`
    : `${API_BASE}/crystallize`;

  const response = await fetch(url, {
    method: 'POST',
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new WitnessApiError(response.status, error.detail ?? 'Crystallization failed');
  }

  return response.json();
}

/**
 * Export the day's work.
 *
 * Endpoints: GET /api/witness/daily/export
 */
export async function exportDay(options?: {
  date?: string;
  format?: 'markdown' | 'json';
  includeCrystal?: boolean;
}): Promise<ExportResponse> {
  const params = new URLSearchParams();

  if (options?.date) {
    params.set('target_date', options.date);
  }
  if (options?.format) {
    params.set('format', options.format);
  }
  if (options?.includeCrystal !== undefined) {
    params.set('include_crystal', String(options.includeCrystal));
  }

  const url = params.toString()
    ? `${API_BASE}/export?${params.toString()}`
    : `${API_BASE}/export`;

  const response = await fetch(url);

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new WitnessApiError(response.status, error.detail ?? 'Export failed');
  }

  return response.json();
}

// =============================================================================
// Convenience Hooks (React Query-style, but pure fetch)
// =============================================================================

/**
 * Create a mark capture handler for use with MarkCaptureInput.
 *
 * @example
 * const handleCapture = createCaptureHandler({
 *   onSuccess: (response) => refetchTrail(),
 *   onError: (error) => toast.error(error.message),
 * });
 *
 * <MarkCaptureInput onCapture={handleCapture} />
 */
export function createCaptureHandler(options?: {
  onSuccess?: (response: CaptureResponse) => void;
  onError?: (error: WitnessApiError | Error) => void;
}): (request: CaptureRequest) => Promise<CaptureResponse | void> {
  return async (request: CaptureRequest) => {
    try {
      const response = await captureMark(request);
      options?.onSuccess?.(response);
      return response;
    } catch (error) {
      if (error instanceof WitnessApiError) {
        options?.onError?.(error);
      } else {
        options?.onError?.(error instanceof Error ? error : new Error(String(error)));
      }
    }
  };
}
