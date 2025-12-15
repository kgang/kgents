/**
 * TypeScript types for Agent Town API.
 * Generated from backend Pydantic models.
 */

// =============================================================================
// Subscription & Tiers
// =============================================================================

export type SubscriptionTier = 'TOURIST' | 'RESIDENT' | 'CITIZEN' | 'FOUNDER';

export type TownPhase = 'MORNING' | 'AFTERNOON' | 'EVENING' | 'NIGHT';

export type CitizenPhase = 'IDLE' | 'WORKING' | 'SOCIALIZING' | 'REFLECTING' | 'RESTING';

export type Archetype = 'Builder' | 'Trader' | 'Healer' | 'Scholar' | 'Watcher';

// =============================================================================
// Town
// =============================================================================

export interface Town {
  id: string;
  name: string;
  citizen_count: number;
  region_count: number;
  coalition_count: number;
  total_token_spend: number;
  status: 'active' | 'paused' | 'stopped';
}

export interface CreateTownRequest {
  name?: string;
  phase?: number;
  similarity_threshold?: number;
  enable_dialogue?: boolean;
}

export interface TownResponse extends Town {}

// =============================================================================
// Citizen
// =============================================================================

export interface Eigenvectors {
  warmth: number;
  curiosity: number;
  trust: number;
  creativity: number;
  patience: number;
  resilience: number;
  ambition: number;
}

export interface CitizenSummary {
  id: string;
  name: string;
  archetype: Archetype;
  region: string;
  phase: CitizenPhase;
  is_evolving: boolean;
}

export interface CitizensResponse {
  citizens: CitizenSummary[];
  total: number;
  by_archetype: Record<string, number>;
  by_region: Record<string, number>;
}

export interface CitizenManifest {
  // LOD 0: Silhouette
  name: string;
  region: string;
  phase: string;
  nphase?: { current: string; cycle_count: number };

  // LOD 1: Posture
  archetype?: string;
  mood?: string;

  // LOD 2: Dialogue
  cosmotechnics?: string;
  metaphor?: string;

  // LOD 3: Memory
  eigenvectors?: Eigenvectors;
  relationships?: Record<string, number>;

  // LOD 4: Psyche
  accursed_surplus?: number;
  id?: string;

  // LOD 5: Abyss
  opacity?: {
    statement: string;
    message: string;
  };
}

export interface CitizenDetailResponse {
  lod: number;
  citizen: CitizenManifest;
  cost_credits: number;
}

// =============================================================================
// Events
// =============================================================================

export interface TownEvent {
  tick: number;
  phase: TownPhase;
  operation: string;
  participants: string[];
  success: boolean;
  message: string;
  tokens_used: number;
  timestamp: string;
  dialogue?: {
    text: string;
    tokens: number;
    model: string;
    was_template: boolean;
    grounded_memories: string[];
  };
}

// =============================================================================
// Coalition
// =============================================================================

export interface Coalition {
  id: string;
  name: string;
  members: string[];
  size: number;
  strength: number;
}

export interface CoalitionsResponse {
  coalitions: Coalition[];
  bridge_citizens: string[];
}

// =============================================================================
// Paywall
// =============================================================================

export interface UpgradeOption {
  type: 'subscription' | 'credits';
  tier?: SubscriptionTier;
  credits?: number;
  price_usd: number;
  unlocks: string;
}

export interface PaywallResult {
  allowed: boolean;
  reason?: string;
  cost_credits: number;
  uses_included: boolean;
  upgrade_options: UpgradeOption[];
}

// =============================================================================
// User & Budget
// =============================================================================

export interface UserBudget {
  user_id: string;
  subscription_tier: SubscriptionTier;
  credits: number;
  monthly_usage: Record<string, number>;
}

// =============================================================================
// INHABIT
// =============================================================================

export interface ConsentState {
  debt: number;
  status: string;
  at_rupture: boolean;
  can_force: boolean;
  cooldown: number;
}

export interface ForceState {
  enabled: boolean;
  used: number;
  remaining: number;
  limit: number;
}

export interface InhabitStatus {
  citizen: string;
  tier: string;
  duration: number;
  time_remaining: number;
  consent: ConsentState;
  force: ForceState;
  expired: boolean;
  actions_count: number;
}

export interface InhabitActionResult {
  success: boolean;
  action: string;
  message: string;
  debt?: number;
  forces_remaining?: number;
}

// =============================================================================
// Payments
// =============================================================================

export interface CheckoutSession {
  session_id: string;
  session_url: string;
  expires_at: string;
}

export interface CreditPack {
  name: string;
  credits: number;
  price_usd: number;
}

export const CREDIT_PACKS: CreditPack[] = [
  { name: 'Starter', credits: 500, price_usd: 4.99 },
  { name: 'Explorer', credits: 2500, price_usd: 19.99 },
  { name: 'Adventurer', credits: 10000, price_usd: 59.99 },
];

export const SUBSCRIPTION_TIERS = {
  TOURIST: { price: 0, lod: [0, 1], inhabit: false, branching: false },
  RESIDENT: { price: 9.99, lod: [0, 1, 2, 3], inhabit: 'basic', branching: false },
  CITIZEN: { price: 29.99, lod: [0, 1, 2, 3, 4], inhabit: 'full', branching: 3 },
  FOUNDER: { price: 99.99, lod: [0, 1, 2, 3, 4, 5], inhabit: 'unlimited', branching: 'unlimited' },
} as const;

// =============================================================================
// LOD Credit Costs (from unified-v2.md)
// =============================================================================

export const LOD_COSTS: Record<number, number> = {
  0: 0,
  1: 0,
  2: 0,
  3: 10,
  4: 100,
  5: 400,
};

export const LOD_INCLUDED_BY_TIER: Record<SubscriptionTier, number[]> = {
  TOURIST: [0, 1],
  RESIDENT: [0, 1, 2, 3],
  CITIZEN: [0, 1, 2, 3, 4],
  FOUNDER: [0, 1, 2, 3, 4, 5],
};
