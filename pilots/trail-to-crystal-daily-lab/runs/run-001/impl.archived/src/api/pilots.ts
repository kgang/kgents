/**
 * Pilots API Client
 *
 * Client for discovering and querying available pilots.
 */

export interface PilotManifest {
  id: string;
  name: string;
  description: string;
  status: 'active' | 'coming_soon' | 'experimental';
  route: string;
  primitives: string[];
  joy_dimension: 'FLOW' | 'WARMTH' | 'SURPRISE';
}

const API_BASE = '/api/pilots';

/**
 * Fallback pilots when API is unreachable.
 * These match the backend registry but serve as a graceful degradation.
 */
export const FALLBACK_PILOTS: PilotManifest[] = [
  {
    id: 'daily-lab',
    name: 'Trail to Crystal',
    description: 'Turn your day into proof of intention',
    status: 'active',
    route: '/daily-lab',
    primitives: ['mark', 'trace', 'crystal', 'compass', 'trail'],
    joy_dimension: 'FLOW',
  },
  {
    id: 'zero-seed',
    name: 'Zero Seed Governance',
    description: 'Personal constitution from axioms',
    status: 'coming_soon',
    route: '/zero-seed',
    primitives: ['galois', 'constitution', 'amendment'],
    joy_dimension: 'SURPRISE',
  },
  {
    id: 'wasm-survivors',
    name: 'WASM Survivors',
    description: 'Witnessed run through procedural challenges',
    status: 'coming_soon',
    route: '/wasm-survivors',
    primitives: ['witness', 'procedural', 'challenge'],
    joy_dimension: 'FLOW',
  },
  {
    id: 'disney-portal',
    name: 'Disney Portal Planner',
    description: 'Plan magical days with warmth',
    status: 'coming_soon',
    route: '/disney-portal',
    primitives: ['planner', 'portal', 'warmth'],
    joy_dimension: 'WARMTH',
  },
  {
    id: 'rap-coach',
    name: 'Rap Coach Flow Lab',
    description: 'Find your flow state in freestyle',
    status: 'coming_soon',
    route: '/rap-coach',
    primitives: ['flow', 'rhythm', 'feedback'],
    joy_dimension: 'SURPRISE',
  },
];

/**
 * List all available pilots.
 */
export async function listPilots(): Promise<PilotManifest[]> {
  const response = await fetch(API_BASE);

  if (!response.ok) {
    throw new Error(`Failed to list pilots: ${response.statusText}`);
  }

  return response.json();
}

/**
 * List only active pilots.
 */
export async function listActivePilots(): Promise<PilotManifest[]> {
  const response = await fetch(`${API_BASE}/active`);

  if (!response.ok) {
    throw new Error(`Failed to list active pilots: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Get a specific pilot by ID.
 */
export async function getPilot(id: string): Promise<PilotManifest> {
  const response = await fetch(`${API_BASE}/${encodeURIComponent(id)}`);

  if (!response.ok) {
    if (response.status === 404) {
      throw new Error(`Pilot not found: ${id}`);
    }
    throw new Error(`Failed to get pilot: ${response.statusText}`);
  }

  return response.json();
}
