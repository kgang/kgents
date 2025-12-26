/**
 * Witness API Client
 *
 * Client for the Daily Lab backend endpoints.
 */

import type {
  CaptureRequest,
  CaptureResponse,
  TrailMark,
  TimeGap,
  Crystal,
  CompressionHonesty
} from '@kgents/shared-primitives';

export interface TrailResponse {
  marks: TrailMark[];
  gaps: TimeGap[];
  date: string;
}

export interface CrystalizeResponse {
  crystal: Crystal;
  honesty: CompressionHonesty;
}

// Backend routes are mounted at /api/witness/daily/
const API_BASE = '/api/witness/daily';

/**
 * Capture a new mark
 *
 * Uses the Daily Lab compatible endpoint that matches CaptureRequest interface.
 * Backend: POST /api/witness/daily/capture
 */
export async function captureMarkApi(request: CaptureRequest): Promise<CaptureResponse> {
  const response = await fetch(`${API_BASE}/capture`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    throw new Error(`Failed to capture mark: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Get today's trail
 * Backend: GET /api/witness/daily/trail
 */
export async function getTodayTrailApi(): Promise<TrailResponse> {
  const response = await fetch(`${API_BASE}/trail`);

  if (!response.ok) {
    throw new Error(`Failed to get trail: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Get marks for a specific date
 * Backend: GET /api/witness/daily/trail?target_date=YYYY-MM-DD
 */
export async function getMarksApi(date?: string): Promise<TrailMark[]> {
  const url = date ? `${API_BASE}/trail?target_date=${date}` : `${API_BASE}/trail`;
  const response = await fetch(url);

  if (!response.ok) {
    throw new Error(`Failed to get marks: ${response.statusText}`);
  }

  // Backend returns {marks: [], ...}, extract just marks for this legacy API
  const data = await response.json();
  return data.marks || [];
}

/**
 * Crystallize the day
 * Backend: POST /api/witness/daily/crystallize
 */
export async function crystallizeDayApi(date?: string): Promise<CrystalizeResponse | null> {
  const url = date
    ? `${API_BASE}/crystallize?target_date=${date}`
    : `${API_BASE}/crystallize`;

  const response = await fetch(url, { method: 'POST' });

  if (!response.ok) {
    if (response.status === 404) {
      return null; // Not enough marks
    }
    throw new Error(`Failed to crystallize: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Get crystals for a date range
 * Note: Backend provides export endpoint, not crystals list
 * Backend: GET /api/witness/daily/export
 */
export async function getCrystalsApi(_startDate?: string, _endDate?: string): Promise<Crystal[]> {
  // For now, return empty array - crystals list endpoint needs implementation
  // The primary flow uses crystallizeDayApi() which returns the crystal directly
  // Parameters prefixed with _ to indicate intentionally unused for future implementation
  console.warn('getCrystalsApi: crystals list endpoint not yet implemented, returning empty array');
  return [];
}

/**
 * Export the day's content
 * Backend: GET /api/witness/daily/export
 */
export async function exportDayApi(date?: string, format: 'markdown' | 'json' = 'markdown'): Promise<string> {
  const params = new URLSearchParams();
  if (date) params.set('target_date', date);
  params.set('format', format);

  const url = `${API_BASE}/export?${params}`;
  const response = await fetch(url);

  if (!response.ok) {
    throw new Error(`Failed to export: ${response.statusText}`);
  }

  const data = await response.json();
  return data.content;
}
