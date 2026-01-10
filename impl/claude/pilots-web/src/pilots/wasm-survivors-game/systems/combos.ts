/**
 * WASM Survivors - Combo System v3 (Hornet Siege)
 *
 * 12 Combos based on the new 36-ability hornet-themed system.
 * Combos emerge from stacking abilities within and across categories.
 *
 * DESIGN PHILOSOPHY:
 * > "If you have A and B, you get C. Simple."
 * > Combos reward themed builds: Bleeder, Pressure Zone, Predator Rush, etc.
 *
 * @see pilots/wasm-survivors-game/systems/abilities.ts
 */

import type { AbilityId, ActiveAbilities } from './abilities';

// =============================================================================
// Types
// =============================================================================

export type ComboTier = 'obvious' | 'common' | 'rare' | 'legendary';

export type SpecialCondition = 'none';

export interface Combo {
  id: string;
  name: string;
  tier: ComboTier;
  requires: AbilityId[];
  description: string;
  flavorText?: string;  // Optional thematic text
  announcement: string;
  color: string;
  icon: string;
  announceSound: 'fanfare' | 'epic';
  screenEffect?: 'flash' | 'pulse' | 'shake';
  effect: ComboEffect;
}

export interface ComboEffect {
  damageMultiplier?: number;
  speedMultiplier?: number;
  attackSpeedMultiplier?: number;
  healingMultiplier?: number;
  passiveEffect?: string;
  unique?: string;
}

export interface ComboState {
  activeComboIds: string[];
  discoveredComboIds: string[];
  discoveryHistory: ComboDiscovery[];
  orderTracker: AbilityId[];
  restraintTimers: Record<string, number>;
  thresholdValues: Record<string, number>;
}

export interface ComboDiscovery {
  comboId: string;
  timestamp: number;
  runNumber: number;
  wasFirstEver: boolean;
}

export interface ComboCheckResult {
  newCombos: Combo[];
  almostCombos: AlmostCombo[];
}

export interface AlmostCombo {
  combo: Combo;
  missingAbilities: AbilityId[];
  progress: number;
}

// =============================================================================
// COMBOS - 12 combos themed around hornet biology
// =============================================================================

const ALL_COMBOS: Combo[] = [
  // ===========================================================================
  // DAMAGE COMBOS (3) - Pure damage stacking
  // ===========================================================================
  {
    id: 'damage_stack',
    name: 'DAMAGE STACK',
    tier: 'common',
    requires: ['sharpened_mandibles', 'crushing_bite', 'venomous_strike'],
    description: 'Pure damage + Poison = Everything melts',
    flavorText: 'They melt before they can scream.',
    announcement: 'DAMAGE STACK!',
    color: '#FF3333',
    icon: 'droplet',
    announceSound: 'fanfare',
    screenEffect: 'pulse',
    effect: {
      damageMultiplier: 1.15,
      passiveEffect: 'Poison damage increased by 50%',
    },
  },
  {
    id: 'double_tap',
    name: 'DOUBLE TAP',
    tier: 'common',
    requires: ['double_strike', 'critical_sting', 'quick_strikes'],
    description: 'Double hit + Crit + Speed = Murder machine',
    flavorText: 'Hit them again. Just to be sure.',
    announcement: 'DOUBLE TAP!',
    color: '#6666FF',
    icon: 'lock',
    announceSound: 'fanfare',
    effect: {
      passiveEffect: 'Double strikes can both crit independently',
    },
  },
  {
    id: 'predator_hunt',
    name: 'PREDATOR HUNT',
    tier: 'rare',
    requires: ['feeding_efficiency', 'territorial_mark', 'trophy_scent'],
    description: 'Kill bonuses + Damage zones + Permanent stacks',
    flavorText: 'The hunt is all.',
    announcement: 'PREDATOR HUNT!',
    color: '#FFAA00',
    icon: 'saw',
    announceSound: 'epic',
    screenEffect: 'shake',
    effect: {
      attackSpeedMultiplier: 1.2,
      passiveEffect: 'Trophy bonuses doubled in territorial zones',
    },
  },

  // ===========================================================================
  // PHEROMONE COMBOS (2) - Debuffs and area control
  // ===========================================================================
  {
    id: 'toxic_cloud',
    name: 'TOXIC CLOUD',
    tier: 'common',
    requires: ['threat_aura', 'confusion_cloud', 'rally_scent'],
    description: 'Slow + Miss chance + Damage reduction = Safe zone',
    flavorText: 'Breathe deep. It gets worse.',
    announcement: 'TOXIC CLOUD!',
    color: '#88FF00',
    icon: 'cloud',
    announceSound: 'fanfare',
    effect: {
      passiveEffect: 'Confused enemies also slowed by 15%',
    },
  },
  {
    id: 'death_zone',
    name: 'DEATH ZONE',
    tier: 'rare',
    requires: ['death_marker', 'aggro_pulse', 'bitter_taste'],
    description: 'Slow zones + Aggro pull + Counter-damage',
    flavorText: 'They come to die.',
    announcement: 'DEATH ZONE!',
    color: '#9933FF',
    icon: 'brain',
    announceSound: 'epic',
    screenEffect: 'pulse',
    effect: {
      passiveEffect: 'Death markers last twice as long',
    },
  },

  // ===========================================================================
  // WING COMBOS (2) - Movement creates effects
  // ===========================================================================
  {
    id: 'pressure_zone',
    name: 'PRESSURE ZONE',
    tier: 'common',
    requires: ['hover_pressure', 'buzz_field', 'threat_aura'],
    description: 'Proximity damage + stationary damage + enemy debuff',
    flavorText: 'Stand still. Watch them melt.',
    announcement: 'PRESSURE ZONE!',
    color: '#FF9900',
    icon: 'target',
    announceSound: 'fanfare',
    effect: {
      passiveEffect: 'Aura effects stack: enemies in all 3 zones take 3x damage',
    },
  },
  {
    id: 'thermal_hunter',
    name: 'THERMAL HUNTER',
    tier: 'rare',
    requires: ['thermal_wake', 'updraft', 'rally_scent'],
    description: 'Trail slow + kill speed + more trail slow',
    flavorText: 'Your path is their grave.',
    announcement: 'THERMAL HUNTER!',
    color: '#FF8844',  // Bright orange-red for thermal (distinct from player #CC5500)
    icon: 'flame',
    announceSound: 'epic',
    screenEffect: 'flash',
    effect: {
      speedMultiplier: 1.2,
      passiveEffect: 'Trail slow stacks (10% from both sources)',
    },
  },

  // ===========================================================================
  // PREDATOR COMBOS (2) - Kill triggers
  // ===========================================================================
  {
    id: 'apex_predator',
    name: 'APEX PREDATOR',
    tier: 'legendary',
    requires: ['trophy_scent', 'corpse_heat', 'clean_kill', 'territorial_mark'],
    description: 'Permanent damage + corpse bonus + explosions + damage zones',
    flavorText: 'The apex of the food chain.',
    announcement: 'APEX PREDATOR!',
    color: '#FFDD00',
    icon: 'crown',
    announceSound: 'epic',
    screenEffect: 'shake',
    effect: {
      damageMultiplier: 1.3,
      passiveEffect: 'Clean Kill explosions create territorial marks',
    },
  },
  {
    id: 'pack_hunter',
    name: 'PACK HUNTER',
    tier: 'common',
    requires: ['pack_signal', 'feeding_efficiency'],
    description: 'Enemy hesitation + attack speed on kill',
    flavorText: 'They freeze. You accelerate.',
    announcement: 'PACK HUNTER!',
    color: '#FF4444',
    icon: 'wolf',
    announceSound: 'fanfare',
    effect: {
      attackSpeedMultiplier: 1.15,
      passiveEffect: 'Hesitation duration doubled on multi-kills',
    },
  },

  // ===========================================================================
  // SURVIVAL COMBO - Defense stacking
  // ===========================================================================
  {
    id: 'fear_aura',
    name: 'FEAR AURA',
    tier: 'common',
    requires: ['threat_aura', 'bitter_taste', 'confusion_cloud'],
    description: 'Damage reduction + attacker debuff + miss chance',
    flavorText: 'They fear to approach.',
    announcement: 'FEAR AURA!',
    color: '#880088',
    icon: 'ghost',
    announceSound: 'fanfare',
    effect: {
      passiveEffect: 'Enemies in threat aura have 15% miss chance',
    },
  },

  // ===========================================================================
  // CHITIN COMBOS (1) - Body modifications
  // ===========================================================================
  {
    id: 'living_weapon',
    name: 'LIVING WEAPON',
    tier: 'legendary',
    requires: ['barbed_chitin', 'molting_burst', 'heat_retention', 'compound_eyes'],
    description: 'Touch damage + emergency burst + low HP speed + better vision',
    flavorText: 'My body is the weapon.',
    announcement: 'LIVING WEAPON!',
    color: '#FF0000',
    icon: 'diamond',
    announceSound: 'epic',
    screenEffect: 'shake',
    effect: {
      damageMultiplier: 1.25,
      passiveEffect: 'Barbed Chitin damage doubled when below 50% HP',
    },
  },
];

// Lookup map
const COMBO_MAP = new Map<string, Combo>(
  ALL_COMBOS.map(c => [c.id, c])
);

export const COMBO_POOL = ALL_COMBOS;

// =============================================================================
// Combo Functions
// =============================================================================

export function getCombo(id: string): Combo | undefined {
  return COMBO_MAP.get(id);
}

export function getCombosByTier(tier: ComboTier): Combo[] {
  return ALL_COMBOS.filter(c => c.tier === tier);
}

export function createInitialComboState(): ComboState {
  return {
    activeComboIds: [],
    discoveredComboIds: [],
    discoveryHistory: [],
    orderTracker: [],
    restraintTimers: {},
    thresholdValues: {},
  };
}

export function checkForCombos(
  abilities: ActiveAbilities,
  comboState: ComboState,
  _runNumber: number = 1,
  _currentTime: number = Date.now()
): ComboCheckResult {
  const newCombos: Combo[] = [];
  const almostCombos: AlmostCombo[] = [];

  for (const combo of ALL_COMBOS) {
    if (comboState.activeComboIds.includes(combo.id)) continue;

    const hasAll = combo.requires.every(id => abilities.owned.includes(id));

    if (hasAll) {
      newCombos.push(combo);
    } else {
      const owned = combo.requires.filter(id => abilities.owned.includes(id));
      const missing = combo.requires.filter(id => !abilities.owned.includes(id));
      const progress = owned.length / combo.requires.length;

      if (progress >= 0.5) {
        almostCombos.push({ combo, missingAbilities: missing, progress });
      }
    }
  }

  return { newCombos, almostCombos };
}

export function checkDeathCombos(
  _abilities: ActiveAbilities,
  _comboState: ComboState
): Combo[] {
  return [];  // No death combos in simplified system
}

export function activateCombo(
  comboState: ComboState,
  combo: Combo,
  runNumber: number
): ComboState {
  const wasFirstEver = !comboState.discoveredComboIds.includes(combo.id);

  return {
    ...comboState,
    activeComboIds: [...comboState.activeComboIds, combo.id],
    discoveredComboIds: wasFirstEver
      ? [...comboState.discoveredComboIds, combo.id]
      : comboState.discoveredComboIds,
    discoveryHistory: [
      ...comboState.discoveryHistory,
      {
        comboId: combo.id,
        timestamp: Date.now(),
        runNumber,
        wasFirstEver,
      },
    ],
  };
}

export const applyComboDiscovery = activateCombo;

export function trackAbilityOrder(
  comboState: ComboState,
  abilityId: AbilityId
): ComboState {
  if (comboState.orderTracker.includes(abilityId)) {
    return comboState;
  }
  return {
    ...comboState,
    orderTracker: [...comboState.orderTracker, abilityId],
  };
}

export function getPossibleCombos(abilities: ActiveAbilities): Combo[] {
  return ALL_COMBOS.filter(combo =>
    combo.requires.every(id => abilities.owned.includes(id))
  );
}

export function getComboHint(
  abilities: ActiveAbilities,
  comboState: ComboState
): AlmostCombo | null {
  const { almostCombos } = checkForCombos(abilities, comboState);
  almostCombos.sort((a, b) => b.progress - a.progress);
  return almostCombos[0] || null;
}
