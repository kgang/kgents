/**
 * Pre-Computed HotData Fixtures (AD-004)
 *
 * Pre-generated LLM fixtures for deterministic testing.
 * Tests never call the LLM at runtime.
 *
 * @see plans/playwright-witness-protocol.md
 */

// =============================================================================
// Types
// =============================================================================

export interface HotCitizen {
  id: string;
  name: string;
  archetype: string;
  region: string;
  phase: string;
  is_evolving: boolean;
  mood?: string;
  cosmotechnics?: string;
  metaphor?: string;
  eigenvectors?: Record<string, number>;
  relationships?: Record<string, number>;
}

export interface HotDialogue {
  id: string;
  participants: string[];
  turns: Array<{
    speaker: string;
    content: string;
    timestamp: number;
    emotion?: string;
  }>;
  topic: string;
  outcome?: string;
}

export interface HotManifest {
  path: string;
  lod: number;
  content: object;
  aspects: string[];
  effects: string[];
}

// =============================================================================
// Citizens HotData
// =============================================================================

export const HOT_CITIZENS: HotCitizen[] = [
  {
    id: 'c-alice-001',
    name: 'Alice',
    archetype: 'Builder',
    region: 'workshop',
    phase: 'WORKING',
    is_evolving: false,
    mood: 'focused',
    cosmotechnics: 'efficiency',
    metaphor: 'The mind is a forge.',
    eigenvectors: {
      warmth: 0.6,
      curiosity: 0.8,
      trust: 0.7,
      creativity: 0.9,
      patience: 0.5,
      resilience: 0.75,
      ambition: 0.85,
    },
    relationships: {
      Bob: 0.8,
      Carol: 0.5,
      Dave: -0.2,
      Eve: 0.3,
    },
  },
  {
    id: 'c-bob-002',
    name: 'Bob',
    archetype: 'Trader',
    region: 'market',
    phase: 'SOCIALIZING',
    is_evolving: false,
    mood: 'cheerful',
    cosmotechnics: 'reciprocity',
    metaphor: 'Value flows like water.',
    eigenvectors: {
      warmth: 0.9,
      curiosity: 0.5,
      trust: 0.6,
      creativity: 0.4,
      patience: 0.7,
      resilience: 0.6,
      ambition: 0.7,
    },
    relationships: {
      Alice: 0.8,
      Carol: 0.7,
      Dave: 0.4,
      Eve: 0.5,
    },
  },
  {
    id: 'c-carol-003',
    name: 'Carol',
    archetype: 'Healer',
    region: 'temple',
    phase: 'REFLECTING',
    is_evolving: true,
    mood: 'contemplative',
    cosmotechnics: 'restoration',
    metaphor: 'Wounds are wisdom waiting.',
    eigenvectors: {
      warmth: 0.95,
      curiosity: 0.7,
      trust: 0.85,
      creativity: 0.6,
      patience: 0.9,
      resilience: 0.8,
      ambition: 0.3,
    },
    relationships: {
      Alice: 0.5,
      Bob: 0.7,
      Dave: 0.6,
      Eve: 0.8,
    },
  },
  {
    id: 'c-dave-004',
    name: 'Dave',
    archetype: 'Scholar',
    region: 'library',
    phase: 'IDLE',
    is_evolving: false,
    mood: 'pensive',
    cosmotechnics: 'accumulation',
    metaphor: 'Knowledge compounds silently.',
    eigenvectors: {
      warmth: 0.4,
      curiosity: 0.95,
      trust: 0.5,
      creativity: 0.7,
      patience: 0.85,
      resilience: 0.55,
      ambition: 0.6,
    },
    relationships: {
      Alice: -0.2,
      Bob: 0.4,
      Carol: 0.6,
      Eve: 0.2,
    },
  },
  {
    id: 'c-eve-005',
    name: 'Eve',
    archetype: 'Watcher',
    region: 'square',
    phase: 'IDLE',
    is_evolving: false,
    mood: 'alert',
    cosmotechnics: 'vigilance',
    metaphor: 'The periphery reveals the center.',
    eigenvectors: {
      warmth: 0.5,
      curiosity: 0.75,
      trust: 0.4,
      creativity: 0.5,
      patience: 0.8,
      resilience: 0.7,
      ambition: 0.45,
    },
    relationships: {
      Alice: 0.3,
      Bob: 0.5,
      Carol: 0.8,
      Dave: 0.2,
    },
  },
];

// =============================================================================
// Dialogue HotData
// =============================================================================

export const HOT_DIALOGUES: HotDialogue[] = [
  {
    id: 'd-trade-001',
    participants: ['Alice', 'Bob'],
    topic: 'resource exchange',
    turns: [
      {
        speaker: 'Alice',
        content: 'I need copper for my latest project.',
        timestamp: 1000,
        emotion: 'determined',
      },
      {
        speaker: 'Bob',
        content: "I have copper, but I'm looking for rare crystals.",
        timestamp: 2000,
        emotion: 'interested',
      },
      {
        speaker: 'Alice',
        content: "I found some in the mines yesterday. Let's trade.",
        timestamp: 3000,
        emotion: 'pleased',
      },
      {
        speaker: 'Bob',
        content: 'Deal! The workshop will prosper.',
        timestamp: 4000,
        emotion: 'delighted',
      },
    ],
    outcome: 'successful_trade',
  },
  {
    id: 'd-counsel-002',
    participants: ['Carol', 'Dave'],
    topic: 'existential doubt',
    turns: [
      {
        speaker: 'Dave',
        content: "What's the point of all this knowledge?",
        timestamp: 1000,
        emotion: 'melancholic',
      },
      {
        speaker: 'Carol',
        content: 'Knowledge without wisdom is like a river without banks.',
        timestamp: 2500,
        emotion: 'serene',
      },
      {
        speaker: 'Dave',
        content: 'But how do I find the banks?',
        timestamp: 4000,
        emotion: 'curious',
      },
      {
        speaker: 'Carol',
        content: 'By serving others. Purpose emerges from connection.',
        timestamp: 5500,
        emotion: 'warm',
      },
    ],
    outcome: 'insight_gained',
  },
  {
    id: 'd-warning-003',
    participants: ['Eve', 'Alice', 'Bob'],
    topic: 'anomaly detection',
    turns: [
      {
        speaker: 'Eve',
        content: "I've noticed strange patterns at the border.",
        timestamp: 1000,
        emotion: 'concerned',
      },
      {
        speaker: 'Alice',
        content: 'What kind of patterns?',
        timestamp: 1500,
        emotion: 'alert',
      },
      {
        speaker: 'Eve',
        content: 'Rhythmic disturbances. Something approaches.',
        timestamp: 2500,
        emotion: 'wary',
      },
      {
        speaker: 'Bob',
        content: 'Should we alert the council?',
        timestamp: 3500,
        emotion: 'worried',
      },
      {
        speaker: 'Eve',
        content: "Not yet. I'll watch longer. Be ready.",
        timestamp: 4500,
        emotion: 'resolute',
      },
    ],
    outcome: 'vigilance_maintained',
  },
];

// =============================================================================
// Manifest HotData
// =============================================================================

export const HOT_MANIFESTS: HotManifest[] = [
  {
    path: 'world.town.citizen.manifest',
    lod: 0,
    content: {
      name: 'Alice',
      region: 'workshop',
      phase: 'WORKING',
    },
    aspects: ['identity', 'location'],
    effects: ['read'],
  },
  {
    path: 'world.town.citizen.manifest',
    lod: 3,
    content: {
      name: 'Alice',
      region: 'workshop',
      phase: 'WORKING',
      archetype: 'Builder',
      mood: 'focused',
      cosmotechnics: 'efficiency',
      metaphor: 'The mind is a forge.',
      eigenvectors: {
        warmth: 0.6,
        curiosity: 0.8,
      },
    },
    aspects: ['identity', 'location', 'psychology', 'philosophy'],
    effects: ['read', 'reflect'],
  },
  {
    path: 'world.town.manifest',
    lod: 0,
    content: {
      id: 'demo-town-123',
      name: 'Demo Town',
      citizen_count: 5,
      status: 'active',
    },
    aspects: ['overview'],
    effects: ['read'],
  },
];

// =============================================================================
// Aggregate HotData Object
// =============================================================================

export const hotdata = {
  citizens: HOT_CITIZENS,
  dialogues: HOT_DIALOGUES,
  manifests: HOT_MANIFESTS,

  // Lookup helpers
  getCitizen: (name: string) => HOT_CITIZENS.find((c) => c.name === name),
  getDialogue: (id: string) => HOT_DIALOGUES.find((d) => d.id === id),
  getManifest: (path: string, lod: number) =>
    HOT_MANIFESTS.find((m) => m.path === path && m.lod === lod),

  // Summary stats
  stats: {
    citizenCount: HOT_CITIZENS.length,
    dialogueCount: HOT_DIALOGUES.length,
    manifestCount: HOT_MANIFESTS.length,
  },
};

// =============================================================================
// Mock Setup Helpers
// =============================================================================

import { Page } from '@playwright/test';

/**
 * Setup page routes to use HotData instead of live API.
 */
export async function setupHotDataMocks(page: Page): Promise<void> {
  // Citizens list
  await page.route('**/v1/town/*/citizens', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        citizens: HOT_CITIZENS.map((c) => ({
          id: c.id,
          name: c.name,
          archetype: c.archetype,
          region: c.region,
          phase: c.phase,
          is_evolving: c.is_evolving,
        })),
        total: HOT_CITIZENS.length,
        by_archetype: countBy(HOT_CITIZENS, 'archetype'),
        by_region: countBy(HOT_CITIZENS, 'region'),
      }),
    });
  });

  // Individual citizen manifest with LOD support
  await page.route('**/v1/town/*/citizen/**', async (route) => {
    const url = new URL(route.request().url());
    const lodParam = url.searchParams.get('lod');
    const lod = lodParam ? parseInt(lodParam, 10) : 0;

    // Extract citizen name from URL
    const pathParts = url.pathname.split('/');
    const citizenName = pathParts[pathParts.length - 1];
    const citizen = HOT_CITIZENS.find(
      (c) => c.name.toLowerCase() === citizenName.toLowerCase() || c.id === citizenName
    );

    if (!citizen) {
      await route.fulfill({
        status: 404,
        contentType: 'application/json',
        body: JSON.stringify({ detail: 'Citizen not found' }),
      });
      return;
    }

    // Build response based on LOD
    const manifest = buildManifestAtLOD(citizen, lod);

    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        lod,
        citizen: manifest,
        cost_credits: lod >= 3 ? 10 : 0,
      }),
    });
  });
}

function countBy<T>(items: T[], key: keyof T): Record<string, number> {
  return items.reduce(
    (acc, item) => {
      const value = String(item[key]);
      acc[value] = (acc[value] || 0) + 1;
      return acc;
    },
    {} as Record<string, number>
  );
}

function buildManifestAtLOD(citizen: HotCitizen, lod: number): object {
  const base = {
    name: citizen.name,
    region: citizen.region,
    phase: citizen.phase,
  };

  if (lod === 0) return base;
  if (lod === 1) return { ...base, archetype: citizen.archetype };
  if (lod === 2) return { ...base, archetype: citizen.archetype, mood: citizen.mood };
  if (lod >= 3) {
    return {
      ...base,
      archetype: citizen.archetype,
      mood: citizen.mood,
      cosmotechnics: citizen.cosmotechnics,
      metaphor: citizen.metaphor,
      eigenvectors: citizen.eigenvectors,
      relationships: lod >= 4 ? citizen.relationships : undefined,
    };
  }
  return base;
}
