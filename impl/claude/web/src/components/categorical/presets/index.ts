/**
 * Polynomial Presets: Domain-specific state machine configurations.
 *
 * Each preset defines positions, edges, valid inputs, and teaching content
 * for the PolynomialPlayground component.
 *
 * @see plans/park-town-design-overhaul.md
 * @see docs/skills/polynomial-agent.md
 */

// =============================================================================
// Types
// =============================================================================

export interface Position {
  id: string;
  label: string;
  description: string;
  color: string;
  is_current: boolean;
}

export interface Edge {
  source: string;
  target: string;
  label: string;
  is_valid: boolean;
}

export interface PolynomialPreset {
  name: string;
  description: string;
  positions: Position[];
  edges: Edge[];
  valid_inputs: string[];
  teaching: string;
  /** Special behavior flag */
  right_to_rest?: boolean;
  /** Jewel this preset belongs to */
  jewel?: 'town' | 'park' | 'gallery';
  /** Category for filtering */
  category?: 'example' | 'citizen' | 'crisis' | 'director';
}

// =============================================================================
// Color Palette (consistent with design system)
// =============================================================================

const COLORS = {
  // Grays
  slate: '#64748b',
  // Primary
  blue: '#3b82f6',
  purple: '#8b5cf6',
  pink: '#ec4899',
  // Semantic
  green: '#22c55e',
  amber: '#f59e0b',
  red: '#dc2626',
  orange: '#f97316',
  // Extended
  cyan: '#06b6d4',
  indigo: '#6366f1',
  teal: '#14b8a6',
};

// =============================================================================
// Gallery Presets (Teaching Examples)
// =============================================================================

export const TRAFFIC_LIGHT: PolynomialPreset = {
  name: 'Traffic Light',
  description: 'Classic state machine with timed transitions',
  jewel: 'gallery',
  category: 'example',
  positions: [
    { id: 'RED', label: 'Red', description: 'Stop', color: COLORS.red, is_current: true },
    { id: 'YELLOW', label: 'Yellow', description: 'Caution', color: COLORS.amber, is_current: false },
    { id: 'GREEN', label: 'Green', description: 'Go', color: COLORS.green, is_current: false },
  ],
  edges: [
    { source: 'RED', target: 'GREEN', label: 'tick', is_valid: true },
    { source: 'GREEN', target: 'YELLOW', label: 'tick', is_valid: true },
    { source: 'YELLOW', target: 'RED', label: 'tick', is_valid: true },
  ],
  valid_inputs: ['tick', 'reset'],
  teaching: 'PolyAgent[S, A, B] captures mode-dependent behavior. Each position determines valid inputs.',
};

export const VENDING_MACHINE: PolynomialPreset = {
  name: 'Vending Machine',
  description: 'State machine with value-dependent transitions',
  jewel: 'gallery',
  category: 'example',
  positions: [
    { id: 'IDLE', label: 'Idle', description: 'Waiting for coins', color: COLORS.slate, is_current: true },
    { id: 'COIN_25', label: '25c', description: 'One quarter', color: COLORS.blue, is_current: false },
    { id: 'COIN_50', label: '50c', description: 'Two quarters', color: COLORS.purple, is_current: false },
    { id: 'DISPENSING', label: 'Dispense', description: 'Product coming', color: COLORS.green, is_current: false },
  ],
  edges: [
    { source: 'IDLE', target: 'COIN_25', label: 'insert_coin', is_valid: true },
    { source: 'COIN_25', target: 'COIN_50', label: 'insert_coin', is_valid: true },
    { source: 'COIN_50', target: 'DISPENSING', label: 'select', is_valid: true },
    { source: 'DISPENSING', target: 'IDLE', label: 'complete', is_valid: true },
    { source: 'COIN_25', target: 'IDLE', label: 'refund', is_valid: true },
    { source: 'COIN_50', target: 'IDLE', label: 'refund', is_valid: true },
  ],
  valid_inputs: ['insert_coin', 'select', 'refund'],
  teaching: 'Directions encode what inputs are valid at each state. The polynomial functor maps states to input sets.',
};

// =============================================================================
// Town Presets (Citizen Lifecycle)
// =============================================================================

export const CITIZEN: PolynomialPreset = {
  name: 'Citizen',
  description: 'Agent Town life cycle with Right to Rest',
  jewel: 'town',
  category: 'citizen',
  positions: [
    { id: 'IDLE', label: 'Idle', description: 'Ready', color: COLORS.slate, is_current: true },
    { id: 'SOCIALIZING', label: 'Social', description: 'With others', color: COLORS.pink, is_current: false },
    { id: 'WORKING', label: 'Work', description: 'Task focus', color: COLORS.amber, is_current: false },
    { id: 'REFLECTING', label: 'Reflect', description: 'Self-analysis', color: COLORS.purple, is_current: false },
    { id: 'RESTING', label: 'Rest', description: 'Right to Rest', color: COLORS.green, is_current: false },
  ],
  edges: [
    { source: 'IDLE', target: 'SOCIALIZING', label: 'greet', is_valid: true },
    { source: 'IDLE', target: 'WORKING', label: 'task', is_valid: true },
    { source: 'IDLE', target: 'REFLECTING', label: 'ponder', is_valid: true },
    { source: 'IDLE', target: 'RESTING', label: 'rest', is_valid: true },
    { source: 'SOCIALIZING', target: 'WORKING', label: 'focus', is_valid: true },
    { source: 'SOCIALIZING', target: 'IDLE', label: 'farewell', is_valid: true },
    { source: 'SOCIALIZING', target: 'RESTING', label: 'tired', is_valid: true },
    { source: 'WORKING', target: 'REFLECTING', label: 'complete', is_valid: true },
    { source: 'WORKING', target: 'IDLE', label: 'break', is_valid: true },
    { source: 'WORKING', target: 'RESTING', label: 'exhaust', is_valid: true },
    { source: 'REFLECTING', target: 'RESTING', label: 'tired', is_valid: true },
    { source: 'REFLECTING', target: 'IDLE', label: 'energized', is_valid: true },
    { source: 'RESTING', target: 'IDLE', label: 'wake', is_valid: true },
  ],
  valid_inputs: ['greet', 'task', 'ponder', 'rest', 'wake'],
  right_to_rest: true,
  teaching: "RESTING only accepts 'wake' - the Right to Rest enforced by directions. Citizens cannot be disturbed while resting.",
};

// =============================================================================
// Park Presets (Crisis & Director)
// =============================================================================

export const CRISIS_PHASE: PolynomialPreset = {
  name: 'Crisis Phase',
  description: 'Punchdrunk Park crisis lifecycle',
  jewel: 'park',
  category: 'crisis',
  positions: [
    { id: 'NORMAL', label: 'Normal', description: 'Steady state', color: COLORS.green, is_current: true },
    { id: 'INCIDENT', label: 'Incident', description: 'Crisis detected', color: COLORS.amber, is_current: false },
    { id: 'RESPONSE', label: 'Response', description: 'Active handling', color: COLORS.orange, is_current: false },
    { id: 'RECOVERY', label: 'Recovery', description: 'Stabilizing', color: COLORS.blue, is_current: false },
  ],
  edges: [
    { source: 'NORMAL', target: 'INCIDENT', label: 'breach', is_valid: true },
    { source: 'INCIDENT', target: 'RESPONSE', label: 'respond', is_valid: true },
    { source: 'INCIDENT', target: 'NORMAL', label: 'false_alarm', is_valid: true },
    { source: 'RESPONSE', target: 'RECOVERY', label: 'resolve', is_valid: true },
    { source: 'RESPONSE', target: 'INCIDENT', label: 'escalate', is_valid: true },
    { source: 'RECOVERY', target: 'NORMAL', label: 'complete', is_valid: true },
    { source: 'RECOVERY', target: 'INCIDENT', label: 'relapse', is_valid: true },
  ],
  valid_inputs: ['breach', 'respond', 'resolve', 'complete'],
  teaching: 'The crisis polynomial defines valid transitions. Force spending affects consent debt, which constrains future options.',
};

export const TIMER_STATE: PolynomialPreset = {
  name: 'Timer State',
  description: 'Compliance timer lifecycle',
  jewel: 'park',
  category: 'crisis',
  positions: [
    { id: 'PENDING', label: 'Pending', description: 'Not started', color: COLORS.slate, is_current: true },
    { id: 'ACTIVE', label: 'Active', description: 'Running', color: COLORS.blue, is_current: false },
    { id: 'WARNING', label: 'Warning', description: '< 25% remaining', color: COLORS.amber, is_current: false },
    { id: 'CRITICAL', label: 'Critical', description: '< 10% remaining', color: COLORS.orange, is_current: false },
    { id: 'EXPIRED', label: 'Expired', description: 'Time exhausted', color: COLORS.red, is_current: false },
  ],
  edges: [
    { source: 'PENDING', target: 'ACTIVE', label: 'start', is_valid: true },
    { source: 'ACTIVE', target: 'WARNING', label: 'tick', is_valid: true },
    { source: 'ACTIVE', target: 'PENDING', label: 'pause', is_valid: true },
    { source: 'WARNING', target: 'CRITICAL', label: 'tick', is_valid: true },
    { source: 'WARNING', target: 'PENDING', label: 'resolve', is_valid: true },
    { source: 'CRITICAL', target: 'EXPIRED', label: 'tick', is_valid: true },
    { source: 'CRITICAL', target: 'PENDING', label: 'resolve', is_valid: true },
  ],
  valid_inputs: ['start', 'tick', 'pause', 'resolve'],
  teaching: 'Timers are polynomial agents - their phase determines valid operations. At CRITICAL, force becomes more expensive.',
};

export const CONSENT_DEBT: PolynomialPreset = {
  name: 'Consent Debt',
  description: 'Ethical constraint state machine',
  jewel: 'park',
  category: 'crisis',
  positions: [
    { id: 'HEALTHY', label: 'Healthy', description: '< 25% debt', color: COLORS.green, is_current: true },
    { id: 'ELEVATED', label: 'Elevated', description: '25-50% debt', color: COLORS.amber, is_current: false },
    { id: 'HIGH', label: 'High', description: '50-75% debt', color: COLORS.orange, is_current: false },
    { id: 'CRITICAL', label: 'Critical', description: '> 75% debt', color: COLORS.red, is_current: false },
  ],
  edges: [
    { source: 'HEALTHY', target: 'ELEVATED', label: 'force', is_valid: true },
    { source: 'ELEVATED', target: 'HIGH', label: 'force', is_valid: true },
    { source: 'HIGH', target: 'CRITICAL', label: 'force', is_valid: true },
    { source: 'ELEVATED', target: 'HEALTHY', label: 'recover', is_valid: true },
    { source: 'HIGH', target: 'ELEVATED', label: 'recover', is_valid: true },
    { source: 'CRITICAL', target: 'HIGH', label: 'recover', is_valid: true },
  ],
  valid_inputs: ['force', 'recover'],
  teaching: 'At HIGH debt: force costs 3x tokens, injections require mask consent, citizens may refuse interactions.',
};

export const DIRECTOR: PolynomialPreset = {
  name: 'Director',
  description: 'Invisible director state machine',
  jewel: 'park',
  category: 'director',
  positions: [
    { id: 'OBSERVING', label: 'Observe', description: 'Passive monitoring', color: COLORS.slate, is_current: true },
    { id: 'BUILDING', label: 'Build', description: 'Building tension', color: COLORS.amber, is_current: false },
    { id: 'INJECTING', label: 'Inject', description: 'Executing injection', color: COLORS.purple, is_current: false },
    { id: 'COOLING', label: 'Cool', description: 'Post-injection cooldown', color: COLORS.blue, is_current: false },
    { id: 'INTERVENING', label: 'Intervene', description: 'Difficulty adjustment', color: COLORS.red, is_current: false },
  ],
  edges: [
    { source: 'OBSERVING', target: 'BUILDING', label: 'build_tension', is_valid: true },
    { source: 'OBSERVING', target: 'INTERVENING', label: 'intervene', is_valid: true },
    { source: 'BUILDING', target: 'INJECTING', label: 'inject', is_valid: true },
    { source: 'BUILDING', target: 'OBSERVING', label: 'abort', is_valid: true },
    { source: 'INJECTING', target: 'COOLING', label: 'complete', is_valid: true },
    { source: 'COOLING', target: 'OBSERVING', label: 'cooldown_complete', is_valid: true },
    { source: 'INTERVENING', target: 'OBSERVING', label: 'complete', is_valid: true },
  ],
  valid_inputs: ['build_tension', 'inject', 'intervene', 'abort'],
  teaching: 'The director is invisible - guests never feel directed. Serendipity appears as lucky coincidence, not orchestration.',
};

// =============================================================================
// Preset Registry
// =============================================================================

export type PresetKey =
  | 'traffic_light'
  | 'vending_machine'
  | 'citizen'
  | 'crisis_phase'
  | 'timer_state'
  | 'consent_debt'
  | 'director';

export const PRESETS: Record<PresetKey, PolynomialPreset> = {
  traffic_light: TRAFFIC_LIGHT,
  vending_machine: VENDING_MACHINE,
  citizen: CITIZEN,
  crisis_phase: CRISIS_PHASE,
  timer_state: TIMER_STATE,
  consent_debt: CONSENT_DEBT,
  director: DIRECTOR,
};

/** Get presets by jewel */
export function getPresetsByJewel(jewel: 'town' | 'park' | 'gallery'): PolynomialPreset[] {
  return Object.values(PRESETS).filter((p) => p.jewel === jewel);
}

/** Get presets by category */
export function getPresetsByCategory(category: string): PolynomialPreset[] {
  return Object.values(PRESETS).filter((p) => p.category === category);
}

/** Get all preset keys */
export function getAllPresetKeys(): PresetKey[] {
  return Object.keys(PRESETS) as PresetKey[];
}

export default PRESETS;
