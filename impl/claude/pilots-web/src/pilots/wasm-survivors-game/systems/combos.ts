/**
 * WASM Survivors - Simplified Combo System (Run 036 v2)
 *
 * 12 Combos that are easy to discover and clearly powerful.
 * No hidden requirements, no wiki knowledge needed.
 *
 * DESIGN PHILOSOPHY:
 * > "If you have A and B, you get C. Simple."
 *
 * @see pilots/wasm-survivors-game/runs/run-036
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
// COMBOS - 12 simple, clear combos
// =============================================================================

const ALL_COMBOS: Combo[] = [
  // DAMAGE COMBOS (4)
  {
    id: 'berserker',
    name: 'BERSERKER',
    tier: 'common',
    requires: ['crushing_bite', 'frenzy'],
    description: 'High damage + High speed = Unstoppable',
    announcement: 'BERSERKER MODE!',
    color: '#FF4400',
    icon: '⚔️💨',
    announceSound: 'fanfare',
    screenEffect: 'shake',
    effect: {
      damageMultiplier: 1.25,
      attackSpeedMultiplier: 1.25,
    },
  },
  {
    id: 'assassin',
    name: 'ASSASSIN',
    tier: 'common',
    requires: ['savage_blow', 'execution'],
    description: 'Execute + Low HP bonus = Delete enemies',
    announcement: 'ASSASSIN UNLOCKED!',
    color: '#880000',
    icon: '🔥⚰️',
    announceSound: 'fanfare',
    effect: {
      passiveEffect: 'Execute threshold raised to 25%',
    },
  },
  {
    id: 'crit_machine',
    name: 'CRIT MACHINE',
    tier: 'rare',
    requires: ['critical_sting', 'double_strike'],
    description: 'Double hits can both crit',
    announcement: 'CRIT MACHINE!',
    color: '#FFAA00',
    icon: '💥⚔️',
    announceSound: 'epic',
    screenEffect: 'flash',
    effect: {
      passiveEffect: 'Each hit of double strike can crit independently',
    },
  },
  {
    id: 'poison_master',
    name: 'POISON MASTER',
    tier: 'common',
    requires: ['venomous_strike', 'chain_lightning'],
    description: 'Chain kills spread poison',
    announcement: 'POISON MASTER!',
    color: '#88FF00',
    icon: '☠️⚡',
    announceSound: 'fanfare',
    effect: {
      passiveEffect: 'Chain kills apply poison to targets',
    },
  },

  // SPEED COMBOS (3)
  {
    id: 'flash',
    name: 'THE FLASH',
    tier: 'rare',
    requires: ['swift_wings', 'quick_strikes', 'berserker_pace'],
    description: 'Maximum speed everything',
    announcement: 'SPEED FORCE!',
    color: '#FFFF00',
    icon: '⚡🦋🔄',
    announceSound: 'epic',
    screenEffect: 'flash',
    effect: {
      speedMultiplier: 1.5,
      attackSpeedMultiplier: 1.5,
    },
  },
  {
    id: 'blitz',
    name: 'BLITZ',
    tier: 'common',
    requires: ['hunters_rush', 'momentum'],
    description: 'Rush in, build kill streak faster',
    announcement: 'BLITZ!',
    color: '#FF4444',
    icon: '🏃🚀',
    announceSound: 'fanfare',
    effect: {
      passiveEffect: 'Kill streak builds 2x faster while rushing',
    },
  },
  {
    id: 'bullet_hell',
    name: 'BULLET HELL',
    tier: 'rare',
    requires: ['bullet_time', 'sweeping_arc'],
    description: 'Time slows, you hit everything',
    announcement: 'BULLET HELL!',
    color: '#9999FF',
    icon: '⏱️🌀',
    announceSound: 'epic',
    effect: {
      passiveEffect: 'Enemies move 50% slower in your attack range',
    },
  },

  // DEFENSE COMBOS (3)
  {
    id: 'immortal',
    name: 'IMMORTAL',
    tier: 'legendary',
    requires: ['second_wind', 'lifesteal', 'regeneration'],
    description: 'You just... don\'t die',
    announcement: 'IMMORTAL!',
    color: '#FFDD88',
    icon: '✨🧛💚',
    announceSound: 'epic',
    screenEffect: 'pulse',
    effect: {
      healingMultiplier: 2.0,
      passiveEffect: 'Revive heals to 100% instead of 50%',
    },
  },
  {
    id: 'tank',
    name: 'TANK',
    tier: 'common',
    requires: ['thick_carapace', 'hardened_shell'],
    description: 'Maximum toughness',
    announcement: 'TANK MODE!',
    color: '#888888',
    icon: '🛡️🐢',
    announceSound: 'fanfare',
    effect: {
      passiveEffect: 'Take 10% less damage per 50 bonus HP',
    },
  },
  {
    id: 'comeback',
    name: 'COMEBACK KING',
    tier: 'rare',
    requires: ['last_stand', 'lifesteal'],
    description: 'Low HP = massive healing',
    announcement: 'COMEBACK KING!',
    color: '#880000',
    icon: '💀🧛',
    announceSound: 'epic',
    effect: {
      passiveEffect: 'Lifesteal doubled when below 30% HP',
    },
  },

  // SPECIAL COMBOS (2)
  {
    id: 'glass_god',
    name: 'GLASS GOD',
    tier: 'legendary',
    requires: ['glass_cannon', 'critical_sting', 'execution'],
    description: 'One shot or be one shot',
    announcement: 'GLASS GOD!',
    color: '#FF0000',
    icon: '💎💥⚰️',
    announceSound: 'epic',
    screenEffect: 'shake',
    effect: {
      damageMultiplier: 1.5,
      passiveEffect: 'Crits instantly kill non-boss enemies',
    },
  },
  {
    id: 'reaper',
    name: 'THE REAPER',
    tier: 'legendary',
    requires: ['execution', 'chain_lightning', 'momentum'],
    description: 'Executions chain indefinitely',
    announcement: 'REAPER MODE!',
    color: '#440044',
    icon: '⚰️⚡🚀',
    announceSound: 'epic',
    screenEffect: 'pulse',
    effect: {
      unique: 'Execute kills chain to ALL nearby enemies below execute threshold',
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
