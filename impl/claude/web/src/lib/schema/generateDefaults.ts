/**
 * Five-Source Default Generation
 *
 * Generates intelligent defaults for form fields using the five AGENTESE contexts:
 * 1. world.*   - Entity context (editing? use current value)
 * 2. self.*    - User history (last used values)
 * 3. concept.* - Schema defaults
 * 4. void.*    - Entropy (creative suggestions)
 * 5. time.*    - Temporal (today's date, session start)
 *
 * Core insight: Intelligent defaults are an act of hospitality.
 *
 * @see spec/protocols/aspect-form-projection.md - Part III
 * @see docs/skills/aspect-form-projection.md - Pattern 3
 */

import type { FieldDescriptor } from '../form/FieldProjectionRegistry';

// =============================================================================
// Types
// =============================================================================

/**
 * Observer information for default generation.
 */
export interface Observer {
  /** Observer's archetype affects default strategy */
  archetype: 'guest' | 'developer' | 'creator' | 'admin';

  /** Optional user ID for history lookup */
  userId?: string;

  /** Optional session ID */
  sessionId?: string;
}

/**
 * Context for default generation.
 */
export interface DefaultContext {
  /** AGENTESE path being invoked */
  path: string;

  /** Aspect being invoked */
  aspect: string;

  /** Entity being edited (if any) - provides world.* defaults */
  entity?: Record<string, unknown>;

  /** Whether this is an edit operation */
  isEdit?: boolean;
}

/**
 * Options for default generation.
 */
export interface GenerateDefaultsOptions {
  /** Skip entropy generation (faster, deterministic) */
  skipEntropy?: boolean;

  /** Skip history lookup (faster) */
  skipHistory?: boolean;

  /** Override temporal source (for testing) */
  now?: Date;
}

// =============================================================================
// Default Source Implementations
// =============================================================================

/**
 * Source 1: world.* - Entity Context
 *
 * When editing an entity, use its current value as the default.
 */
function getWorldDefault(field: FieldDescriptor, context: DefaultContext): unknown | undefined {
  if (!context.entity || !context.isEdit) {
    return undefined;
  }

  return context.entity[field.name];
}

/**
 * Source 2: self.* - User History
 *
 * Look up the user's last-used value for this field type.
 * Currently a stub - will integrate with persistence layer.
 */
async function getSelfDefault(
  _field: FieldDescriptor,
  _observer: Observer,
  _context: DefaultContext
): Promise<unknown | undefined> {
  // TODO: Integrate with user preference storage
  // For now, return undefined to fall through to other sources
  //
  // Future implementation:
  // const key = `${observer.userId}:${field.context?.join('.')}:${field.name}`;
  // return await preferenceStore.get(key);
  return undefined;
}

/**
 * Source 3: concept.* - Schema Defaults
 *
 * Use the default value from the JSON Schema.
 */
function getConceptDefault(field: FieldDescriptor): unknown | undefined {
  return field.default;
}

/**
 * Source 4: void.* - Entropy (Creative Suggestions)
 *
 * For creator archetype, generate creative suggestions.
 * This adds serendipity and delight to the form experience.
 */
async function getVoidDefault(
  field: FieldDescriptor,
  observer: Observer,
  _context: DefaultContext
): Promise<unknown | undefined> {
  // Only activate for creator archetype
  if (observer.archetype !== 'creator') {
    return undefined;
  }

  // Generate creative defaults based on field context
  const context = field.context || [];

  // Name fields get whimsical suggestions
  if (field.name === 'name') {
    // Check context for entity type
    if (context.includes('citizen')) {
      return getWhimsicalCitizenName();
    }
    if (context.includes('town')) {
      return getWhimsicalTownName();
    }
    if (context.includes('coalition')) {
      return getWhimsicalCoalitionName();
    }
  }

  // Description fields get poetic prompts
  if (field.name === 'description' && field.type === 'string') {
    return getCreativePrompt(context);
  }

  return undefined;
}

/**
 * Source 5: time.* - Temporal Defaults
 *
 * Generate time-based defaults (today's date, session start, etc.)
 */
function getTimeDefault(
  field: FieldDescriptor,
  _context: DefaultContext,
  now: Date = new Date()
): unknown | undefined {
  // Date fields default to today
  if (field.format === 'date') {
    return now.toISOString().split('T')[0]; // YYYY-MM-DD
  }

  // DateTime fields default to now
  if (field.format === 'date-time') {
    return now.toISOString();
  }

  // Fields named with temporal hints
  const temporalNames = ['start_date', 'end_date', 'due_date', 'scheduled_at', 'created_at'];
  if (temporalNames.includes(field.name)) {
    if (field.type === 'string') {
      return now.toISOString().split('T')[0];
    }
  }

  return undefined;
}

// =============================================================================
// Creative Default Generators (void.*)
// =============================================================================

/**
 * Pool of whimsical citizen names.
 * Mix of cultures and styles for variety.
 */
const CITIZEN_NAMES = [
  'Zephyr Chen',
  'Luna Okonkwo',
  'Sage Williams',
  'River Nakamura',
  'Phoenix Garcia',
  'Wren Patel',
  'Atlas Kim',
  'Juniper Singh',
  'Indigo Müller',
  'Storm Kowalski',
  'Ember Johansson',
  'Onyx Dubois',
  'Solstice Park',
  'Nebula Santos',
  'Cypress Lee',
];

/**
 * Pool of whimsical town names.
 */
const TOWN_NAMES = [
  'Willowmere',
  'Starfall Crossing',
  'Ember Heights',
  'Twilight Hollow',
  'Crystal Springs',
  'Moonvale',
  'Sunridge',
  'Mistwood',
  'Thornbrook',
  'Silverdale',
  'Ashenvale',
  'Frostpine',
  'Goldleaf',
  'Stormwatch',
  'Petalwind',
];

/**
 * Pool of whimsical coalition names.
 */
const COALITION_NAMES = [
  'The Dreamweavers',
  'Circle of Embers',
  'The Stargazers',
  'Guild of Whispers',
  'The Pathfinders',
  'Order of the Phoenix',
  'The Wayfarers',
  'Council of Echoes',
  'The Harmonists',
  'League of Shadows',
];

/**
 * Creative prompts for description fields.
 */
const CREATIVE_PROMPTS: Record<string, string[]> = {
  citizen: [
    'A curious soul who...',
    'Known throughout the town for...',
    'Carries secrets that...',
    'Dreams of...',
  ],
  town: [
    'A place where...',
    'Founded on the principle that...',
    'Known far and wide for...',
    'Travelers speak of...',
  ],
  default: ['Something wonderful...', 'An idea taking shape...', 'A beginning...'],
};

function getWhimsicalCitizenName(): string {
  return CITIZEN_NAMES[Math.floor(Math.random() * CITIZEN_NAMES.length)];
}

function getWhimsicalTownName(): string {
  return TOWN_NAMES[Math.floor(Math.random() * TOWN_NAMES.length)];
}

function getWhimsicalCoalitionName(): string {
  return COALITION_NAMES[Math.floor(Math.random() * COALITION_NAMES.length)];
}

function getCreativePrompt(context: string[]): string {
  const entityType = context.find((c) => CREATIVE_PROMPTS[c]) || 'default';
  const prompts = CREATIVE_PROMPTS[entityType];
  return prompts[Math.floor(Math.random() * prompts.length)];
}

// =============================================================================
// Type-Based Fallback Defaults
// =============================================================================

/**
 * Get a sensible fallback default based on field type.
 * This is the last resort when all five sources return undefined.
 */
function getTypeFallback(field: FieldDescriptor): unknown {
  switch (field.type) {
    case 'string':
      return '';
    case 'number':
    case 'integer':
      return field.min ?? 0;
    case 'boolean':
      return false;
    case 'array':
      return [];
    case 'object':
      return {};
    default:
      return null;
  }
}

// =============================================================================
// Main Export
// =============================================================================

/**
 * Generate intelligent defaults for a set of fields.
 *
 * Uses the five-source cascade to find the best default for each field:
 * 1. world.*   - Entity value (if editing)
 * 2. self.*    - User history
 * 3. concept.* - Schema default
 * 4. void.*    - Entropy (creator archetype)
 * 5. time.*    - Temporal defaults
 *
 * Falls back to type-based defaults if all sources return undefined.
 *
 * @param fields - FieldDescriptor array from analyzeContract
 * @param observer - Observer information
 * @param context - Invocation context
 * @param options - Generation options
 * @returns Record mapping field names to default values
 *
 * @example
 * const defaults = await generateDefaults(fields, observer, {
 *   path: 'world.town.citizen',
 *   aspect: 'create'
 * });
 */
export async function generateDefaults(
  fields: FieldDescriptor[],
  observer: Observer,
  context: DefaultContext,
  options: GenerateDefaultsOptions = {}
): Promise<Record<string, unknown>> {
  const { skipEntropy = false, skipHistory = false, now } = options;

  const defaults: Record<string, unknown> = {};

  for (const field of fields) {
    // Try sources in priority order
    let value: unknown | undefined;

    // 1. world.* - Entity context (synchronous)
    value = getWorldDefault(field, context);

    // 2. self.* - User history (async, can skip)
    if (value === undefined && !skipHistory) {
      value = await getSelfDefault(field, observer, context);
    }

    // 3. concept.* - Schema default (synchronous)
    if (value === undefined) {
      value = getConceptDefault(field);
    }

    // 4. void.* - Entropy (async, can skip)
    if (value === undefined && !skipEntropy) {
      value = await getVoidDefault(field, observer, context);
    }

    // 5. time.* - Temporal default (synchronous)
    if (value === undefined) {
      value = getTimeDefault(field, context, now);
    }

    // 6. Type fallback (last resort)
    if (value === undefined) {
      value = getTypeFallback(field);
    }

    defaults[field.name] = value;
  }

  return defaults;
}

/**
 * Synchronous version for simple cases (skips async sources).
 * Faster but misses history and entropy.
 */
export function generateDefaultsSync(
  fields: FieldDescriptor[],
  _observer: Observer, // Unused in sync version (skips self.* and void.* sources)
  context: DefaultContext,
  options: GenerateDefaultsOptions = {}
): Record<string, unknown> {
  const { now } = options;
  const defaults: Record<string, unknown> = {};

  for (const field of fields) {
    let value: unknown | undefined;

    // 1. world.*
    value = getWorldDefault(field, context);

    // 3. concept.* (skip 2. self.*)
    if (value === undefined) {
      value = getConceptDefault(field);
    }

    // 5. time.* (skip 4. void.*)
    if (value === undefined) {
      value = getTimeDefault(field, context, now);
    }

    // 6. Type fallback
    if (value === undefined) {
      value = getTypeFallback(field);
    }

    defaults[field.name] = value;
  }

  return defaults;
}

// =============================================================================
// Developer Utilities
// =============================================================================

/**
 * Auto-generate a UUID for developer archetype.
 */
export function generateUUID(): string {
  // Simple UUID v4 generation
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
    const r = (Math.random() * 16) | 0;
    const v = c === 'x' ? r : (r & 0x3) | 0x8;
    return v.toString(16);
  });
}

/**
 * Apply developer enhancements to defaults.
 * - Auto-generate UUIDs for uuid-format fields
 * - Fill in technical metadata
 */
export function enhanceForDeveloper(
  defaults: Record<string, unknown>,
  fields: FieldDescriptor[]
): Record<string, unknown> {
  const enhanced = { ...defaults };

  for (const field of fields) {
    // Auto-generate UUIDs
    if (field.format === 'uuid' && !enhanced[field.name]) {
      enhanced[field.name] = generateUUID();
    }
  }

  return enhanced;
}
