import { Page, Route } from '@playwright/test';

/**
 * API fixtures for E2E tests.
 *
 * Provides mock data and API interception utilities for testing
 * Agent Town flows without a running backend.
 */

// =============================================================================
// Mock Data
// =============================================================================

export const mockTown = {
  id: 'demo-town-123',
  name: 'Demo Town',
  citizen_count: 8,
  region_count: 5,
  coalition_count: 2,
  total_token_spend: 0,
  status: 'active' as const,
};

export const mockCitizens = [
  {
    id: 'c1',
    name: 'Alice',
    archetype: 'Builder',
    region: 'workshop',
    phase: 'WORKING',
    is_evolving: false,
  },
  {
    id: 'c2',
    name: 'Bob',
    archetype: 'Trader',
    region: 'market',
    phase: 'SOCIALIZING',
    is_evolving: false,
  },
  {
    id: 'c3',
    name: 'Carol',
    archetype: 'Healer',
    region: 'temple',
    phase: 'REFLECTING',
    is_evolving: true,
  },
  {
    id: 'c4',
    name: 'Dave',
    archetype: 'Scholar',
    region: 'library',
    phase: 'IDLE',
    is_evolving: false,
  },
  {
    id: 'c5',
    name: 'Eve',
    archetype: 'Watcher',
    region: 'square',
    phase: 'IDLE',
    is_evolving: false,
  },
];

export const mockManifestLOD0 = {
  name: 'Alice',
  region: 'workshop',
  phase: 'WORKING',
  nphase: { current: 'IMPLEMENT', cycle_count: 2 },
};

export const mockManifestLOD3 = {
  ...mockManifestLOD0,
  archetype: 'Builder',
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
};

export const mockUserBudget = {
  user_id: 'user-1',
  subscription_tier: 'TOURIST' as const,
  credits: 0,
  monthly_usage: {},
};

export const mockResidentBudget = {
  user_id: 'user-1',
  subscription_tier: 'RESIDENT' as const,
  credits: 100,
  monthly_usage: {},
};

export const mockCheckoutSession = {
  session_id: 'cs_test_123',
  session_url: 'https://checkout.stripe.com/pay/cs_test_123',
  expires_at: new Date(Date.now() + 30 * 60 * 1000).toISOString(),
};

export const mockInhabitStatus = {
  citizen: 'Alice',
  tier: 'RESIDENT',
  duration: 300,
  time_remaining: 280,
  consent: {
    debt: 0.2,
    status: 'granted',
    at_rupture: false,
    can_force: true,
    cooldown: 0,
  },
  force: {
    enabled: false,
    used: 0,
    remaining: 3,
    limit: 3,
  },
  expired: false,
  actions_count: 0,
};

// =============================================================================
// API Interceptors
// =============================================================================

/**
 * Setup API mocks for tourist flow (no auth, limited access).
 */
export async function setupTouristMocks(page: Page) {
  // Match both /api/v1 and /v1 patterns
  await page.route('**/v1/town', async (route) => {
    if (route.request().method() === 'POST') {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(mockTown),
      });
    } else if (route.request().method() === 'GET') {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(mockTown),
      });
    } else {
      await route.continue();
    }
  });

  // GET /v1/town/{id}
  await page.route('**/v1/town/*', async (route) => {
    const url = route.request().url();
    // Skip if this is a more specific route (citizens, live, etc)
    if (url.includes('/citizens') || url.includes('/live') || url.includes('/citizen/')) {
      await route.continue();
      return;
    }

    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(mockTown),
    });
  });

  await page.route('**/v1/town/*/citizens', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        citizens: mockCitizens,
        total: mockCitizens.length,
        by_archetype: { Builder: 1, Trader: 1, Healer: 1, Scholar: 1, Watcher: 1 },
        by_region: { workshop: 1, market: 1, temple: 1, library: 1, square: 1 },
      }),
    });
  });

  await page.route('**/v1/town/*/citizen/**', async (route) => {
    const url = new URL(route.request().url());
    const lodParam = url.searchParams.get('lod');
    const lod = lodParam ? parseInt(lodParam) : 0;

    // Tourists only get LOD 0-1
    if (lod >= 3) {
      await route.fulfill({
        status: 402,
        contentType: 'application/json',
        body: JSON.stringify({
          detail: 'LOD 3 requires RESIDENT tier or credits',
          upgrade_options: [
            { type: 'subscription', tier: 'RESIDENT', price_usd: 9.99, unlocks: 'LOD 3 access' },
            { type: 'credits', credits: 500, price_usd: 4.99, unlocks: '50 LOD 3 views' },
          ],
        }),
      });
      return;
    }

    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        lod,
        citizen: mockManifestLOD0,
        cost_credits: 0,
      }),
    });
  });

  await page.route('**/v1/user/budget', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(mockUserBudget),
    });
  });
}

/**
 * Setup API mocks for resident flow (authenticated, more access).
 */
export async function setupResidentMocks(page: Page) {
  // Start with tourist mocks, then override
  await setupTouristMocks(page);

  // Override user budget to be RESIDENT
  await page.route('**/v1/user/budget', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(mockResidentBudget),
    });
  });

  // LOD 3 now accessible
  await page.route('**/v1/town/*/citizen/**', async (route) => {
    const url = new URL(route.request().url());
    const lodParam = url.searchParams.get('lod');
    const lod = lodParam ? parseInt(lodParam) : 0;

    // Residents get LOD 0-3
    if (lod >= 4) {
      await route.fulfill({
        status: 402,
        contentType: 'application/json',
        body: JSON.stringify({
          detail: 'LOD 4 requires CITIZEN tier or credits',
          upgrade_options: [
            { type: 'subscription', tier: 'CITIZEN', price_usd: 29.99, unlocks: 'LOD 4 access' },
            { type: 'credits', credits: 100, price_usd: 9.99, unlocks: '1 LOD 4 view' },
          ],
        }),
      });
      return;
    }

    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        lod,
        citizen: lod >= 3 ? mockManifestLOD3 : mockManifestLOD0,
        cost_credits: lod >= 3 ? 10 : 0,
      }),
    });
  });
}

/**
 * Setup checkout flow mocks.
 */
export async function setupCheckoutMocks(page: Page) {
  await page.route('**/v1/payments/subscription/checkout', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(mockCheckoutSession),
    });
  });

  await page.route('**/v1/payments/credits/checkout', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(mockCheckoutSession),
    });
  });
}

/**
 * Setup INHABIT flow mocks.
 */
export async function setupInhabitMocks(page: Page) {
  await page.route('**/v1/town/*/inhabit/*/start', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(mockInhabitStatus),
    });
  });

  await page.route('**/v1/town/*/inhabit/*/status', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(mockInhabitStatus),
    });
  });

  await page.route('**/v1/town/*/inhabit/*/suggest', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        type: 'enact',
        message: 'Alice nods in agreement.',
        inner_voice: 'This feels right.',
        cost: 10,
        alignment_score: 0.8,
        status: {
          ...mockInhabitStatus,
          actions_count: 1,
          consent: { ...mockInhabitStatus.consent, debt: 0.25 },
        },
        success: true,
      }),
    });
  });

  await page.route('**/v1/town/*/inhabit/*/force', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        type: 'enact',
        message: 'Alice reluctantly complies.',
        inner_voice: 'I must do this...',
        cost: 30,
        alignment_score: 0.3,
        status: {
          ...mockInhabitStatus,
          actions_count: 1,
          force: { ...mockInhabitStatus.force, used: 1, remaining: 2 },
          consent: { ...mockInhabitStatus.consent, debt: 0.5 },
        },
        success: true,
      }),
    });
  });

  await page.route('**/v1/town/*/inhabit/*/end', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ success: true }),
    });
  });
}

// =============================================================================
// N-Phase Mock Data (Wave 5)
// =============================================================================

export const mockNPhaseContext = {
  session_id: 'nphase-session-123',
  current_phase: 'UNDERSTAND' as const,
  cycle_count: 1,
  checkpoint_count: 0,
  handle_count: 0,
};

export const mockNPhaseTransitions = [
  {
    tick: 15,
    from_phase: 'UNDERSTAND',
    to_phase: 'ACT',
    session_id: 'nphase-session-123',
    cycle_count: 1,
    trigger: 'town_phase:EVENING',
  },
  {
    tick: 28,
    from_phase: 'ACT',
    to_phase: 'REFLECT',
    session_id: 'nphase-session-123',
    cycle_count: 1,
    trigger: 'town_phase:NIGHT',
  },
];

export const mockLiveStartWithNPhase = {
  town_id: 'demo-town-123',
  phases: 4,
  speed: 1.0,
  nphase_enabled: true,
  nphase: mockNPhaseContext,
};

export const mockLiveEndWithNPhase = {
  town_id: 'demo-town-123',
  total_ticks: 40,
  status: 'completed',
  nphase_summary: {
    session_id: 'nphase-session-123',
    final_phase: 'REFLECT',
    current_phase: 'REFLECT',
    cycle_count: 1,
    checkpoint_count: 2,
    handle_count: 5,
    ledger_entries: 12,
  },
};

/**
 * Setup N-Phase SSE mock for live stream.
 *
 * Simulates the town live endpoint with N-Phase events.
 */
export async function setupNPhaseMocks(page: Page) {
  // Start with tourist mocks for basic API
  await setupTouristMocks(page);

  // Mock the live SSE endpoint
  await page.route('**/v1/town/*/live*', async (route) => {
    const url = new URL(route.request().url());
    const nphaseEnabled = url.searchParams.get('nphase_enabled') === 'true';

    // Generate SSE events
    let events = `event: live.start\ndata: ${JSON.stringify({
      ...mockLiveStartWithNPhase,
      nphase_enabled: nphaseEnabled,
      nphase: nphaseEnabled ? mockNPhaseContext : undefined,
    })}\n\n`;

    // Simulate some events with phase transitions
    if (nphaseEnabled) {
      // First transition at tick 15
      events += `event: live.event\ndata: ${JSON.stringify({
        tick: 15,
        phase: 'EVENING',
        operation: 'trade',
        participants: ['Alice', 'Bob'],
        success: true,
        message: 'Alice trades with Bob',
        tokens_used: 0,
        timestamp: new Date().toISOString(),
      })}\n\n`;

      events += `event: live.nphase\ndata: ${JSON.stringify(mockNPhaseTransitions[0])}\n\n`;

      // Second transition at tick 28
      events += `event: live.event\ndata: ${JSON.stringify({
        tick: 28,
        phase: 'NIGHT',
        operation: 'reflect',
        participants: ['Carol'],
        success: true,
        message: 'Carol reflects on the day',
        tokens_used: 0,
        timestamp: new Date().toISOString(),
      })}\n\n`;

      events += `event: live.nphase\ndata: ${JSON.stringify(mockNPhaseTransitions[1])}\n\n`;
    }

    // End event
    events += `event: live.end\ndata: ${JSON.stringify({
      ...mockLiveEndWithNPhase,
      nphase_summary: nphaseEnabled ? mockLiveEndWithNPhase.nphase_summary : undefined,
    })}\n\n`;

    await route.fulfill({
      status: 200,
      contentType: 'text/event-stream',
      headers: {
        'Cache-Control': 'no-cache',
        Connection: 'keep-alive',
      },
      body: events,
    });
  });
}
