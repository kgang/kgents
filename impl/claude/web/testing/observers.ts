/**
 * Observer Umwelt Fixtures
 *
 * Observer tiers are first-class fixtures: Tourist/Resident/Citizen.
 * Each fixture sets API routes, feature flags, and entitlements.
 *
 * @see plans/playwright-witness-protocol.md
 */

import { Page } from '@playwright/test';

// =============================================================================
// Types
// =============================================================================

export const OBSERVER_TIERS = ['TOURIST', 'RESIDENT', 'CITIZEN'] as const;
export type ObserverTier = (typeof OBSERVER_TIERS)[number];

export interface ObserverConfig {
  tier: ObserverTier;
  credits: number;
  maxLOD: number;
  canInhabit: boolean;
  canForce: boolean;
  features: string[];
}

export const OBSERVER_CONFIGS: Record<ObserverTier, ObserverConfig> = {
  TOURIST: {
    tier: 'TOURIST',
    credits: 0,
    maxLOD: 1,
    canInhabit: false,
    canForce: false,
    features: ['browse', 'view_lod0', 'view_lod1'],
  },
  RESIDENT: {
    tier: 'RESIDENT',
    credits: 100,
    maxLOD: 3,
    canInhabit: true,
    canForce: false,
    features: ['browse', 'view_lod0', 'view_lod1', 'view_lod2', 'view_lod3', 'inhabit'],
  },
  CITIZEN: {
    tier: 'CITIZEN',
    credits: 1000,
    maxLOD: 4,
    canInhabit: true,
    canForce: true,
    features: [
      'browse',
      'view_lod0',
      'view_lod1',
      'view_lod2',
      'view_lod3',
      'view_lod4',
      'inhabit',
      'force',
      'dialogue',
    ],
  },
};

// =============================================================================
// Mock Data by Tier
// =============================================================================

export const MOCK_BUDGETS: Record<ObserverTier, object> = {
  TOURIST: {
    user_id: 'user-tourist',
    subscription_tier: 'TOURIST',
    credits: 0,
    monthly_usage: {},
  },
  RESIDENT: {
    user_id: 'user-resident',
    subscription_tier: 'RESIDENT',
    credits: 100,
    monthly_usage: { lod3_views: 5 },
  },
  CITIZEN: {
    user_id: 'user-citizen',
    subscription_tier: 'CITIZEN',
    credits: 1000,
    monthly_usage: { lod4_views: 2, inhabit_sessions: 3 },
  },
};

// =============================================================================
// Setup Functions
// =============================================================================

/**
 * Setup API mocks for a specific observer tier.
 */
export async function setupObserverMocks(page: Page, tier: ObserverTier): Promise<void> {
  const config = OBSERVER_CONFIGS[tier];
  const budget = MOCK_BUDGETS[tier];

  // User budget endpoint
  await page.route('**/v1/user/budget', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(budget),
    });
  });

  // LOD-gated citizen manifest endpoint
  await page.route('**/v1/town/*/citizen/**', async (route) => {
    const url = new URL(route.request().url());
    const lodParam = url.searchParams.get('lod');
    const lod = lodParam ? parseInt(lodParam, 10) : 0;

    // Check tier-based LOD access
    if (lod > config.maxLOD) {
      await route.fulfill({
        status: 402,
        contentType: 'application/json',
        body: JSON.stringify({
          detail: `LOD ${lod} requires higher tier`,
          current_tier: tier,
          required_tier: lod >= 4 ? 'CITIZEN' : lod >= 3 ? 'RESIDENT' : 'TOURIST',
          upgrade_options: getUpgradeOptions(tier, lod),
        }),
      });
      return;
    }

    // Return manifest at requested LOD
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        lod,
        citizen: getMockCitizenAtLOD(lod),
        cost_credits: lod >= 3 ? 10 : 0,
      }),
    });
  });

  // Inhabit endpoint gating
  await page.route('**/v1/town/*/inhabit/*/start', async (route) => {
    if (!config.canInhabit) {
      await route.fulfill({
        status: 403,
        contentType: 'application/json',
        body: JSON.stringify({
          detail: 'INHABIT requires RESIDENT tier or higher',
          current_tier: tier,
        }),
      });
      return;
    }

    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        citizen: 'Alice',
        tier,
        duration: 300,
        time_remaining: 300,
        consent: { debt: 0, status: 'granted', at_rupture: false, can_force: config.canForce },
        force: { enabled: config.canForce, used: 0, remaining: config.canForce ? 3 : 0, limit: 3 },
        expired: false,
        actions_count: 0,
      }),
    });
  });

  // Force endpoint gating
  await page.route('**/v1/town/*/inhabit/*/force', async (route) => {
    if (!config.canForce) {
      await route.fulfill({
        status: 403,
        contentType: 'application/json',
        body: JSON.stringify({
          detail: 'FORCE requires CITIZEN tier',
          current_tier: tier,
        }),
      });
      return;
    }

    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        type: 'enact',
        message: 'Alice reluctantly complies.',
        inner_voice: 'I must do this...',
        cost: 30,
        alignment_score: 0.3,
        success: true,
      }),
    });
  });
}

// =============================================================================
// Helper Functions
// =============================================================================

function getUpgradeOptions(
  currentTier: ObserverTier,
  requestedLOD: number
): Array<{ type: string; tier?: string; credits?: number; price_usd: number; unlocks: string }> {
  const options: Array<{
    type: string;
    tier?: string;
    credits?: number;
    price_usd: number;
    unlocks: string;
  }> = [];

  if (currentTier === 'TOURIST') {
    options.push({
      type: 'subscription',
      tier: 'RESIDENT',
      price_usd: 9.99,
      unlocks: 'LOD 3 access + INHABIT',
    });
  }

  if (requestedLOD >= 4 && currentTier !== 'CITIZEN') {
    options.push({
      type: 'subscription',
      tier: 'CITIZEN',
      price_usd: 29.99,
      unlocks: 'LOD 4 access + FORCE',
    });
  }

  options.push({
    type: 'credits',
    credits: 500,
    price_usd: 4.99,
    unlocks: `50 LOD ${requestedLOD} views`,
  });

  return options;
}

function getMockCitizenAtLOD(lod: number): object {
  const base = {
    name: 'Alice',
    region: 'workshop',
    phase: 'WORKING',
  };

  if (lod === 0) return base;

  if (lod === 1) {
    return {
      ...base,
      archetype: 'Builder',
    };
  }

  if (lod === 2) {
    return {
      ...base,
      archetype: 'Builder',
      mood: 'focused',
      nphase: { current: 'IMPLEMENT', cycle_count: 2 },
    };
  }

  if (lod >= 3) {
    return {
      ...base,
      archetype: 'Builder',
      mood: 'focused',
      cosmotechnics: 'efficiency',
      metaphor: 'The mind is a forge.',
      nphase: { current: 'IMPLEMENT', cycle_count: 2 },
      eigenvectors: {
        warmth: 0.6,
        curiosity: 0.8,
        trust: 0.7,
        creativity: 0.9,
        patience: 0.5,
        resilience: 0.75,
        ambition: 0.85,
      },
      relationships: lod >= 4 ? { Bob: 0.8, Carol: 0.5, Dave: -0.2, Eve: 0.3 } : undefined,
    };
  }

  return base;
}

// =============================================================================
// Test Assertions
// =============================================================================

/**
 * Assert that a tier-specific feature is accessible.
 */
export function tierHasFeature(tier: ObserverTier, feature: string): boolean {
  return OBSERVER_CONFIGS[tier].features.includes(feature);
}

/**
 * Get all features available to a tier but not to a lower tier.
 */
export function getExclusiveFeatures(tier: ObserverTier): string[] {
  // Base tier has no exclusive features (nothing to upgrade FROM)
  if (tier === 'TOURIST') return [];

  const config = OBSERVER_CONFIGS[tier];
  const lowerTierFeatures = new Set<string>();

  if (tier === 'RESIDENT') {
    for (const f of OBSERVER_CONFIGS.TOURIST.features) {
      lowerTierFeatures.add(f);
    }
  } else if (tier === 'CITIZEN') {
    for (const f of OBSERVER_CONFIGS.TOURIST.features) {
      lowerTierFeatures.add(f);
    }
    for (const f of OBSERVER_CONFIGS.RESIDENT.features) {
      lowerTierFeatures.add(f);
    }
  }

  return config.features.filter((f) => !lowerTierFeatures.has(f));
}
