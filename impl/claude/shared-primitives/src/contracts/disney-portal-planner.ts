/**
 * Disney Portal Planner API Contracts
 *
 * CANONICAL SOURCE OF TRUTH for Disney Portal Planner API.
 *
 * Design Philosophy (from PROTO_SPEC):
 * - QA-1: Planning must feel like narrative design, not logistics spreadsheeting
 * - QA-2: The portal interface must invite curiosity while preserving clarity
 * - QA-3: A day should feel earned, not accidental
 * - QA-4: Email delivery must feel like a ceremonial handoff
 *
 * Flavor Laws (toddler-family):
 * - L-FLAV-1: One-handed operation support
 * - L-FLAV-2: Height requirements prominently displayed
 * - L-FLAV-3: Nap/meal as immovable constraints
 * - L-FLAV-4: Cold weather adaptations for late January
 * - L-FLAV-5: Cultural comfort zones acknowledged
 *
 * @layer L4 (Specification)
 * @see pilots/disney-portal-planner/PROTO_SPEC.md
 * @see pilots/CONTRACT_COHERENCE.md
 */

// =============================================================================
// Core Types
// =============================================================================

/**
 * Portal kinds - every type of experience at Disney
 * L13: Total Coverage Law - includes ALL park elements
 */
export type PortalKind =
  | 'attraction'      // Rides, dark rides, coasters
  | 'dining'          // Table service, quick service, snacks
  | 'entertainment'   // Parades, fireworks, stage shows
  | 'character'       // Meet & greets, cavalcades
  | 'experience'      // Play areas, interactive quests
  | 'service'         // Restrooms, first aid, baby care
  | 'hidden';         // Easter eggs, insider tips, hidden Mickeys

/**
 * Age appropriateness indicators
 * L-FLAV-2: Height requirements prominently displayed
 */
export interface AgeGuidance {
  /** Minimum height in inches (null = no requirement) */
  minHeightInches: number | null;
  /** Maximum suggested age (null = no limit) */
  maxSuggestedAge: number | null;
  /** Whether appropriate for toddlers (under 3) */
  toddlerFriendly: boolean;
  /** Whether appropriate for infants (under 2) */
  infantFriendly: boolean;
  /** Special notes about age/height */
  notes: string | null;
}

/**
 * A portal - a committable experience in the park
 * L1: Portal Commitment Law - expansion is a commitment
 */
export interface Portal {
  /** Unique identifier */
  id: string;
  /** Human-readable name */
  name: string;
  /** Portal category */
  kind: PortalKind;
  /** Park identifier */
  parkId: string;
  /** Location area within park */
  area: string;
  /** Brief description */
  description: string;
  /** Age/height guidance */
  ageGuidance: AgeGuidance;
  /** Whether this is indoors (L-FLAV-4: cold weather) */
  isIndoor: boolean;
  /** Duration in minutes */
  durationMinutes: number;
  /** Coordinates for map visualization */
  coordinates: { x: number; y: number };
  /** Current wait time in minutes (null if not applicable) */
  currentWaitMinutes: number | null;
  /** Whether live data is available (L6: Liveness Law) */
  isLiveData: boolean;
  /** Last data update timestamp */
  dataUpdatedAt: string;
  /** Tags for search/filter */
  tags: string[];
  /** Family-friendly food indicators (L-FLAV-5) */
  hasFamiliarFood?: boolean;
  /** Asian cuisine available (L-FLAV-5) */
  hasAsianCuisine?: boolean;
}

/**
 * A party member - individual with preferences and constraints
 * L8: Party Coherence Law
 */
export interface PartyMember {
  /** Unique identifier */
  id: string;
  /** Display name */
  name: string;
  /** Age in years (can be fractional for toddlers) */
  ageYears: number;
  /** Height in inches */
  heightInches: number;
  /** Whether this member requires nap time (L-FLAV-3) */
  needsNapTime: boolean;
  /** Preferred nap window start (24h format) */
  napStartHour?: number;
  /** Preferred nap duration in hours */
  napDurationHours?: number;
  /** Dietary preferences (L-FLAV-5) */
  dietaryPreferences: string[];
  /** Mobility constraints */
  mobilityNotes?: string;
}

/**
 * A trip party - group of travelers
 * L8: Party Coherence Law
 */
export interface Party {
  /** Unique identifier */
  id: string;
  /** Party name */
  name: string;
  /** Members of the party */
  members: PartyMember[];
  /** When this party was created */
  createdAt: string;
}

/**
 * A portal expansion - commitment to include portal in plan
 * L1: Portal Commitment Law - emit mark with intent and constraint
 */
export interface PortalExpansion {
  /** Unique identifier */
  id: string;
  /** The portal being expanded */
  portalId: string;
  /** Planned start time (ISO string) */
  plannedTime: string;
  /** Intent behind this expansion */
  intent: string;
  /** Constraints considered when adding */
  constraints: string[];
  /** Whether this is locked (harder to move) */
  isLocked: boolean;
  /** Witness mark ID for this expansion */
  markId?: string;
  /** When this was added */
  addedAt: string;
}

/**
 * Protected time window (nap, meal)
 * L-FLAV-3: Nap/meal as immovable constraints
 */
export interface ProtectedWindow {
  /** Unique identifier */
  id: string;
  /** Window type */
  type: 'nap' | 'meal' | 'rest';
  /** Start time (ISO string) */
  startTime: string;
  /** Duration in minutes */
  durationMinutes: number;
  /** Label (e.g., "Lunch", "Nap Time") */
  label: string;
  /** Members this applies to */
  memberIds: string[];
  /** Whether this is movable */
  isMovable: boolean;
}

/**
 * A day plan - collection of expansions for a single day
 * L2: Day Integrity Law
 */
export interface DayPlan {
  /** Unique identifier */
  id: string;
  /** Trip identifier this day belongs to */
  tripId: string;
  /** Day number in trip (1-indexed) */
  dayNumber: number;
  /** Date (ISO date string) */
  date: string;
  /** Park for this day */
  parkId: string;
  /** Expanded portals in order */
  expansions: PortalExpansion[];
  /** Protected windows */
  protectedWindows: ProtectedWindow[];
  /** Weather forecast (L-FLAV-4) */
  weather?: WeatherForecast;
  /** Total walking distance in miles */
  walkingDistanceMiles: number;
  /** Whether day is crystallized */
  isCrystallized: boolean;
  /** Crystal ID if crystallized */
  crystalId?: string;
}

/**
 * Weather forecast for a day
 * L-FLAV-4: Cold weather adaptations
 */
export interface WeatherForecast {
  /** High temperature in Fahrenheit */
  highF: number;
  /** Low temperature in Fahrenheit */
  lowF: number;
  /** Precipitation probability (0-1) */
  precipProbability: number;
  /** Condition summary */
  condition: string;
  /** Whether outdoor alternatives are advised */
  indoorAdvised: boolean;
}

/**
 * Constitutional tradeoff score
 * L3: Joy Transparency Law
 */
export interface TradeoffScore {
  /** Joy score (0-1) */
  joy: number;
  /** Composability score (0-1) */
  composability: number;
  /** Ethics score (0-1) */
  ethics: number;
  /** Physical comfort score (0-1) */
  comfort: number;
  /** Explanation of tradeoffs made */
  tradeoffExplanation: string;
}

/**
 * A trail node - step in derivation lineage
 * L4: Constraint Disclosure Law
 */
export interface TrailNode {
  /** Node identifier */
  id: string;
  /** Type of trail event */
  eventType: 'expand' | 'collapse' | 'reschedule' | 'protect' | 'adapt';
  /** Description of what happened */
  description: string;
  /** Reasoning for this action */
  reasoning: string;
  /** Constraints that influenced this */
  constraints: string[];
  /** Timestamp */
  timestamp: string;
  /** Related expansion ID */
  expansionId?: string;
  /** Related portal ID */
  portalId?: string;
  /** Witness mark ID */
  markId?: string;
}

/**
 * A trail - derivation lineage for a day
 * L2: Day Integrity Law - preserves ordering logic
 */
export interface Trail {
  /** Day ID this trail belongs to */
  dayId: string;
  /** Ordered trail nodes */
  nodes: TrailNode[];
  /** Total events in trail */
  totalEvents: number;
}

/**
 * A day crystal - narrative summary of a day
 * L5: Crystal Legibility Law - readable as standalone narrative
 * NOTE: Named DayCrystal to avoid collision with witness/Crystal
 */
export interface DayCrystal {
  /** Unique identifier */
  id: string;
  /** Day ID this crystal represents */
  dayId: string;
  /** Narrative title */
  title: string;
  /** The story of the day (markdown) */
  story: string;
  /** Key moments highlighted */
  highlights: string[];
  /** Constitutional tradeoffs made */
  tradeoffs: TradeoffScore;
  /** Photo placeholders/captions */
  photoMoments: string[];
  /** When crystallized */
  crystallizedAt: string;
  /** Whether this has been shared */
  isShared: boolean;
  /** Recipients if shared */
  sharedWith?: string[];
}

/**
 * A trip - multi-day experience
 * L11: Trip Integrity Law
 */
export interface Trip {
  /** Unique identifier */
  id: string;
  /** Trip name */
  name: string;
  /** Party for this trip */
  partyId: string;
  /** Days in this trip */
  days: DayPlan[];
  /** Trip start date */
  startDate: string;
  /** Trip end date */
  endDate: string;
  /** Trip crystal (narrative summary) */
  tripCrystalId?: string;
  /** When created */
  createdAt: string;
  /** When last updated */
  updatedAt: string;
}

/**
 * A park
 */
export interface Park {
  /** Unique identifier */
  id: string;
  /** Park name */
  name: string;
  /** Short name */
  shortName: string;
  /** Park icon/emoji */
  icon: string;
  /** Today's hours */
  hoursToday?: { open: string; close: string };
  /** Whether park data is live */
  isLive: boolean;
}

// =============================================================================
// API Response Models
// =============================================================================

/**
 * GET /api/disney-portal-planner/parks response
 */
export interface ParksResponse {
  parks: Park[];
  dataFreshness: 'live' | 'cached' | 'stale';
  updatedAt: string;
}

/**
 * GET /api/disney-portal-planner/parks/{id}/portals response
 */
export interface PortalsResponse {
  parkId: string;
  portals: Portal[];
  /** Portals filtered for party member heights */
  accessibleForParty?: Portal[];
  dataFreshness: 'live' | 'cached' | 'stale';
  updatedAt: string;
}

/**
 * GET /api/disney-portal-planner/trip/{id} response
 */
export interface TripResponse {
  trip: Trip;
  party: Party;
  crystals: DayCrystal[];
}

/**
 * GET /api/disney-portal-planner/plan/trail response
 */
export interface DisneyTrailResponse {
  trail: Trail;
  dayId: string;
}

/**
 * POST /api/disney-portal-planner/plan/crystallize response
 */
export interface DisneyPlanCrystallizeResponse {
  crystal: DayCrystal;
  dayId: string;
  markId: string;
}

/**
 * Handoff recipient
 */
export interface HandoffRecipient {
  email: string;
  name?: string;
}

/**
 * POST /api/disney-portal-planner/plan/handoff response
 */
export interface HandoffResponse {
  success: boolean;
  sentTo: string[];
  crystalUrl: string;
  markId: string;
}

/**
 * Adaptation suggestion
 * L12: Adaptation Law
 */
export interface AdaptationSuggestion {
  /** Suggestion ID */
  id: string;
  /** What triggered this suggestion */
  trigger: 'ride_closure' | 'weather' | 'fatigue' | 'timing';
  /** Description of the issue */
  issue: string;
  /** Proposed changes */
  proposedChanges: Array<{
    type: 'add' | 'remove' | 'reschedule';
    portalId?: string;
    reason: string;
  }>;
  /** Explanation of reasoning */
  reasoning: string;
  /** Impact on tradeoffs */
  tradeoffImpact: Partial<TradeoffScore>;
}

/**
 * GET /api/disney-portal-planner/plan/suggestions response
 */
export interface SuggestionsResponse {
  suggestions: AdaptationSuggestion[];
  dayId: string;
  currentConditions: {
    closures: string[];
    weather: WeatherForecast;
    crowdLevel: 'low' | 'moderate' | 'high';
  };
}

// =============================================================================
// Request Models (HQ-1: Always use Pydantic request models)
// =============================================================================

/**
 * POST /api/disney-portal-planner/party request
 */
export interface CreatePartyRequest {
  name: string;
  members: Omit<PartyMember, 'id'>[];
}

/**
 * POST /api/disney-portal-planner/trip request
 */
export interface CreateTripRequest {
  name: string;
  partyId: string;
  startDate: string;
  endDate: string;
  parkIds: string[];
}

/**
 * POST /api/disney-portal-planner/plan/expand request
 */
export interface ExpandPortalRequest {
  tripId: string;
  dayId: string;
  portalId: string;
  plannedTime: string;
  intent: string;
  constraints?: string[];
}

/**
 * POST /api/disney-portal-planner/plan/collapse request
 */
export interface CollapsePortalRequest {
  tripId: string;
  dayId: string;
  expansionId: string;
  reason: string;
}

/**
 * POST /api/disney-portal-planner/plan/protect request
 */
export interface ProtectWindowRequest {
  tripId: string;
  dayId: string;
  type: 'nap' | 'meal' | 'rest';
  startTime: string;
  durationMinutes: number;
  label: string;
  memberIds: string[];
}

/**
 * POST /api/disney-portal-planner/plan/crystallize request
 */
export interface DisneyPlanCrystallizeRequest {
  tripId: string;
  dayId: string;
}

/**
 * POST /api/disney-portal-planner/plan/handoff request
 */
export interface HandoffRequest {
  tripId: string;
  dayId: string;
  recipients: HandoffRecipient[];
  personalMessage?: string;
}

/**
 * POST /api/disney-portal-planner/plan/adapt request
 */
export interface AdaptRequest {
  tripId: string;
  dayId: string;
  suggestionId: string;
  approved: boolean;
}

// =============================================================================
// Contract Invariants
// =============================================================================

/**
 * Runtime invariant checks for Portal.
 */
export const PORTAL_INVARIANTS = {
  'has id': (p: Portal) => typeof p.id === 'string' && p.id.length > 0,
  'has name': (p: Portal) => typeof p.name === 'string' && p.name.length > 0,
  'kind is valid': (p: Portal) =>
    ['attraction', 'dining', 'entertainment', 'character', 'experience', 'service', 'hidden'].includes(p.kind),
  'duration positive': (p: Portal) => p.durationMinutes > 0,
  'wait non-negative': (p: Portal) => p.currentWaitMinutes === null || p.currentWaitMinutes >= 0,
} as const;

/**
 * Runtime invariant checks for DayPlan.
 */
export const DAY_PLAN_INVARIANTS = {
  'has id': (d: DayPlan) => typeof d.id === 'string' && d.id.length > 0,
  'has date': (d: DayPlan) => /^\d{4}-\d{2}-\d{2}$/.test(d.date),
  'expansions is array': (d: DayPlan) => Array.isArray(d.expansions),
  'protected windows is array': (d: DayPlan) => Array.isArray(d.protectedWindows),
  'day number positive': (d: DayPlan) => d.dayNumber >= 1,
} as const;

/**
 * Runtime invariant checks for DayCrystal.
 */
export const DAY_CRYSTAL_INVARIANTS = {
  'has id': (c: DayCrystal) => typeof c.id === 'string' && c.id.length > 0,
  'has title': (c: DayCrystal) => typeof c.title === 'string' && c.title.length > 0,
  'has story': (c: DayCrystal) => typeof c.story === 'string' && c.story.length > 0,
  'highlights is array': (c: DayCrystal) => Array.isArray(c.highlights),
  'tradeoffs present': (c: DayCrystal) => c.tradeoffs !== null && typeof c.tradeoffs === 'object',
} as const;

/**
 * Runtime invariant checks for PartyMember.
 */
export const PARTY_MEMBER_INVARIANTS = {
  'has id': (m: PartyMember) => typeof m.id === 'string' && m.id.length > 0,
  'has name': (m: PartyMember) => typeof m.name === 'string' && m.name.length > 0,
  'age non-negative': (m: PartyMember) => m.ageYears >= 0,
  'height positive': (m: PartyMember) => m.heightInches > 0,
} as const;

// =============================================================================
// Normalizers (defensive coding - HQ-2)
// =============================================================================

/**
 * Extract error message from API error response.
 * HQ-2: Error Normalization Law
 * NOTE: Exported as extractDisneyError to avoid collision with wasm-survivors
 */
export function extractDisneyError(error: unknown, fallback: string): string {
  const e = error as Record<string, unknown>;

  // String detail (normal error)
  if (typeof e?.detail === 'string') return e.detail;

  // Array detail (FastAPI validation errors)
  if (Array.isArray(e?.detail)) {
    return e.detail.map((i: { msg?: string }) => i.msg).filter(Boolean).join('; ');
  }

  // Error object with message
  if (error instanceof Error) return error.message;

  return fallback;
}

/**
 * Normalize a potentially malformed Portal.
 */
export function normalizePortal(data: unknown): Portal {
  const p = data as Partial<Portal>;
  return {
    id: typeof p.id === 'string' ? p.id : '',
    name: typeof p.name === 'string' ? p.name : 'Unknown',
    kind: p.kind ?? 'attraction',
    parkId: typeof p.parkId === 'string' ? p.parkId : '',
    area: typeof p.area === 'string' ? p.area : '',
    description: typeof p.description === 'string' ? p.description : '',
    ageGuidance: normalizeAgeGuidance(p.ageGuidance),
    isIndoor: p.isIndoor ?? false,
    durationMinutes: typeof p.durationMinutes === 'number' ? p.durationMinutes : 30,
    coordinates: p.coordinates ?? { x: 0, y: 0 },
    currentWaitMinutes: p.currentWaitMinutes ?? null,
    isLiveData: p.isLiveData ?? false,
    dataUpdatedAt: typeof p.dataUpdatedAt === 'string' ? p.dataUpdatedAt : new Date().toISOString(),
    tags: Array.isArray(p.tags) ? p.tags : [],
    hasFamiliarFood: p.hasFamiliarFood,
    hasAsianCuisine: p.hasAsianCuisine,
  };
}

/**
 * Normalize age guidance.
 */
export function normalizeAgeGuidance(data: unknown): AgeGuidance {
  const a = data as Partial<AgeGuidance>;
  return {
    minHeightInches: a?.minHeightInches ?? null,
    maxSuggestedAge: a?.maxSuggestedAge ?? null,
    toddlerFriendly: a?.toddlerFriendly ?? true,
    infantFriendly: a?.infantFriendly ?? true,
    notes: a?.notes ?? null,
  };
}

/**
 * Normalize a DayPlan.
 */
export function normalizeDayPlan(data: unknown): DayPlan {
  const d = data as Partial<DayPlan>;
  return {
    id: typeof d.id === 'string' ? d.id : '',
    tripId: typeof d.tripId === 'string' ? d.tripId : '',
    dayNumber: typeof d.dayNumber === 'number' ? d.dayNumber : 1,
    date: typeof d.date === 'string' ? d.date : new Date().toISOString().split('T')[0],
    parkId: typeof d.parkId === 'string' ? d.parkId : '',
    expansions: Array.isArray(d.expansions) ? d.expansions : [],
    protectedWindows: Array.isArray(d.protectedWindows) ? d.protectedWindows : [],
    weather: d.weather,
    walkingDistanceMiles: typeof d.walkingDistanceMiles === 'number' ? d.walkingDistanceMiles : 0,
    isCrystallized: d.isCrystallized ?? false,
    crystalId: d.crystalId,
  };
}

/**
 * Normalize a DayCrystal.
 */
export function normalizeDayCrystal(data: unknown): DayCrystal {
  const c = data as Partial<DayCrystal>;
  return {
    id: typeof c.id === 'string' ? c.id : '',
    dayId: typeof c.dayId === 'string' ? c.dayId : '',
    title: typeof c.title === 'string' ? c.title : 'Untitled Day',
    story: typeof c.story === 'string' ? c.story : '',
    highlights: Array.isArray(c.highlights) ? c.highlights : [],
    tradeoffs: normalizeTradeoffScore(c.tradeoffs),
    photoMoments: Array.isArray(c.photoMoments) ? c.photoMoments : [],
    crystallizedAt: typeof c.crystallizedAt === 'string' ? c.crystallizedAt : new Date().toISOString(),
    isShared: c.isShared ?? false,
    sharedWith: c.sharedWith,
  };
}

/**
 * Normalize tradeoff score.
 */
export function normalizeTradeoffScore(data: unknown): TradeoffScore {
  const t = data as Partial<TradeoffScore>;
  return {
    joy: typeof t?.joy === 'number' ? t.joy : 0.5,
    composability: typeof t?.composability === 'number' ? t.composability : 0.5,
    ethics: typeof t?.ethics === 'number' ? t.ethics : 0.5,
    comfort: typeof t?.comfort === 'number' ? t.comfort : 0.5,
    tradeoffExplanation: typeof t?.tradeoffExplanation === 'string' ? t.tradeoffExplanation : '',
  };
}

// =============================================================================
// Type Guards
// =============================================================================

/**
 * Type guard for Portal.
 */
export function isPortal(data: unknown): data is Portal {
  if (!data || typeof data !== 'object') return false;
  const p = data as Record<string, unknown>;
  return (
    typeof p.id === 'string' &&
    typeof p.name === 'string' &&
    typeof p.kind === 'string' &&
    typeof p.parkId === 'string'
  );
}

/**
 * Type guard for DayPlan.
 */
export function isDayPlan(data: unknown): data is DayPlan {
  if (!data || typeof data !== 'object') return false;
  const d = data as Record<string, unknown>;
  return (
    typeof d.id === 'string' &&
    typeof d.date === 'string' &&
    Array.isArray(d.expansions)
  );
}

/**
 * Type guard for DayCrystal.
 */
export function isDayCrystal(data: unknown): data is DayCrystal {
  if (!data || typeof data !== 'object') return false;
  const c = data as Record<string, unknown>;
  return (
    typeof c.id === 'string' &&
    typeof c.title === 'string' &&
    typeof c.story === 'string'
  );
}
