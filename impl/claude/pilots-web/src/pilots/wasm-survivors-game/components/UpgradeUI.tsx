/**
 * WASM Survivors - Upgrade UI (Simplified Ability System)
 *
 * Level-up pause screen with clear, impactful ability choices.
 * "Every ability should make you go 'oh hell yes'."
 *
 * DESIGN:
 * - Category-based visual theming (damage/speed/defense/special)
 * - Animated preview effects on hover
 * - Synergy hints showing combos with owned abilities
 * - Stack indicators for stackable abilities
 * - Trigger text preview showing what you'll see in-game
 *
 * @see pilots/wasm-survivors-game/systems/abilities.ts
 */

import { useState, useEffect, useCallback, memo } from 'react';
import type { Ghost } from '../types';
import { COLORS } from '../systems/juice';
import {
  getAbility,
  getAbilityLevel,
  type Ability,
  type AbilityId,
  type AbilityCategory,
  type ActiveAbilities,
} from '../systems/abilities';

// =============================================================================
// Types
// =============================================================================

interface UpgradeUIProps {
  level: number;
  choices: string[];
  currentAbilities: AbilityId[];
  abilities?: ActiveAbilities;
  recentGhosts: Ghost[];
  onSelect: (upgradeId: string, alternatives: string[]) => void;
}

// =============================================================================
// Category Configuration - Updated for simplified system
// =============================================================================

const CATEGORY_CONFIG: Record<AbilityCategory, {
  icon: string;
  color: string;
  label: string;
  description: string;
}> = {
  damage: {
    icon: '🗡️',
    color: '#FF6600',
    label: 'DAMAGE',
    description: 'Make your bite hurt more',
  },
  speed: {
    icon: '⚡',
    color: '#FFDD00',
    label: 'SPEED',
    description: 'Attack faster, move faster',
  },
  defense: {
    icon: '🛡️',
    color: '#00FF88',
    label: 'DEFENSE',
    description: 'Take less damage, heal more',
  },
  special: {
    icon: '✨',
    color: '#FF44FF',
    label: 'SPECIAL',
    description: 'Unique powerful effects',
  },
  wing: {
    icon: '🦋',
    color: '#00D4FF',
    label: 'WING',
    description: 'Movement creates effects',
  },
  predator: {
    icon: '🦅',
    color: '#FF9900',
    label: 'PREDATOR',
    description: 'Kill triggers stack damage',
  },
  pheromone: {
    icon: '💨',
    color: '#9966FF',
    label: 'PHEROMONE',
    description: 'Area denial and debuffs',
  },
  chitin: {
    icon: '🪲',
    color: '#8B4513',
    label: 'CHITIN',
    description: 'Body modifications for survival',
  },
};

// =============================================================================
// Synergy Definitions - Which abilities combo well together
// =============================================================================

const SYNERGIES: Partial<Record<AbilityId, AbilityId[]>> = {
  // Damage synergies
  sharpened_mandibles: ['crushing_bite', 'double_strike', 'critical_sting'],
  crushing_bite: ['sharpened_mandibles', 'savage_blow', 'momentum'],
  venomous_strike: ['double_strike', 'quick_strikes', 'venom_architect'],
  double_strike: ['sharpened_mandibles', 'venomous_strike', 'critical_sting', 'lifesteal'],
  savage_blow: ['crushing_bite', 'execution', 'momentum'],
  giant_killer: ['quick_strikes', 'frenzy', 'chain_lightning'],
  // Speed synergies
  quick_strikes: ['double_strike', 'venomous_strike', 'frenzy'],
  frenzy: ['quick_strikes', 'berserker_pace', 'lifesteal'],
  swift_wings: ['hunters_rush', 'berserker_pace', 'momentum'],
  hunters_rush: ['swift_wings', 'momentum', 'chain_lightning'],
  berserker_pace: ['frenzy', 'swift_wings', 'glass_cannon'],
  bullet_time: ['sweeping_arc', 'chain_lightning', 'momentum'],
  // Defense synergies
  thick_carapace: ['hardened_shell', 'regeneration', 'last_stand'],
  hardened_shell: ['thick_carapace', 'last_stand', 'lifesteal'],
  regeneration: ['thick_carapace', 'lifesteal', 'second_wind'],
  lifesteal: ['double_strike', 'frenzy', 'regeneration'],
  last_stand: ['thick_carapace', 'hardened_shell', 'second_wind'],
  second_wind: ['last_stand', 'regeneration', 'glass_cannon'],
  // Special synergies
  critical_sting: ['sharpened_mandibles', 'double_strike', 'glass_cannon'],
  execution: ['savage_blow', 'execution_chain', 'momentum'],
  sweeping_arc: ['frenzy', 'quick_strikes', 'bullet_time'],
  chain_lightning: ['giant_killer', 'hunters_rush', 'momentum'],
  momentum: ['chain_lightning', 'savage_blow', 'hunters_rush'],
  glass_cannon: ['critical_sting', 'berserker_pace', 'second_wind'],
  // Skill-gated synergies
  graze_frenzy: ['swift_wings', 'frenzy', 'momentum'],
  thermal_momentum: ['swift_wings', 'berserker_pace', 'hunters_rush'],
  execution_chain: ['execution', 'savage_blow', 'chain_lightning'],
  glass_cannon_mastery: ['glass_cannon', 'critical_sting', 'lifesteal'],
  venom_architect: ['venomous_strike', 'double_strike', 'chain_lightning'],
  // Wing synergies
  draft: ['swift_wings', 'hunters_rush', 'hover_pressure'],
  buzz_field: ['thermal_wake', 'hover_pressure', 'territorial_mark'],
  thermal_wake: ['buzz_field', 'draft', 'corpse_heat'],
  scatter_dust: ['updraft', 'swift_wings', 'berserker_pace'],
  updraft: ['scatter_dust', 'feeding_efficiency', 'momentum'],
  hover_pressure: ['buzz_field', 'draft', 'trophy_scent'],
  // Predator synergies
  feeding_efficiency: ['updraft', 'frenzy', 'quick_strikes'],
  territorial_mark: ['corpse_heat', 'trophy_scent', 'momentum'],
  trophy_scent: ['hover_pressure', 'territorial_mark', 'chain_lightning'],
  pack_signal: ['clean_kill', 'feeding_efficiency', 'execution'],
  corpse_heat: ['thermal_wake', 'territorial_mark', 'savage_blow'],
  clean_kill: ['pack_signal', 'execution', 'giant_killer'],
};

// =============================================================================
// Styles - Enhanced with preview animations
// =============================================================================

const styles = `
  @keyframes fade-in {
    from { opacity: 0; transform: scale(0.95); }
    to { opacity: 1; transform: scale(1); }
  }
  .animate-fade-in {
    animation: fade-in 0.3s ease-out;
  }

  @keyframes glow-pulse {
    0%, 100% { opacity: 0.4; }
    50% { opacity: 0.8; }
  }

  .upgrade-card:hover .card-glow {
    animation: glow-pulse 1.5s ease-in-out infinite;
  }

  @keyframes stack-flash {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.7; }
  }
  .stack-indicator {
    animation: stack-flash 2s ease-in-out infinite;
  }

  @keyframes particle-float {
    0% { transform: translateY(0) scale(1); opacity: 1; }
    100% { transform: translateY(-30px) scale(0.5); opacity: 0; }
  }
  .preview-particle {
    animation: particle-float 1s ease-out infinite;
  }

  @keyframes trigger-text-pop {
    0% { transform: scale(0.8); opacity: 0; }
    50% { transform: scale(1.1); opacity: 1; }
    100% { transform: scale(1); opacity: 1; }
  }
  .trigger-text {
    animation: trigger-text-pop 0.3s ease-out;
  }

  @keyframes icon-bounce {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-4px); }
  }
  .upgrade-card:hover .ability-icon {
    animation: icon-bounce 0.6s ease-in-out infinite;
  }

  @keyframes synergy-glow {
    0%, 100% { box-shadow: 0 0 4px currentColor; }
    50% { box-shadow: 0 0 12px currentColor; }
  }
  .synergy-badge {
    animation: synergy-glow 1.5s ease-in-out infinite;
  }

  @keyframes risk-pulse {
    0%, 100% { border-color: rgba(255, 0, 0, 0.3); }
    50% { border-color: rgba(255, 0, 0, 0.8); }
  }
  .risk-reward-card {
    animation: risk-pulse 1s ease-in-out infinite;
  }
`;

// =============================================================================
// Component
// =============================================================================

export const UpgradeUI = memo(function UpgradeUI({
  level,
  choices,
  currentAbilities,
  abilities,
  recentGhosts,
  onSelect,
}: UpgradeUIProps) {
  const [selectedIndex, setSelectedIndex] = useState<number | null>(null);
  const [hoveredIndex, setHoveredIndex] = useState<number | null>(null);
  const [showGhosts, setShowGhosts] = useState(false);

  // Keyboard navigation
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      switch (e.key) {
        case '1':
          handleSelect(0);
          break;
        case '2':
          handleSelect(1);
          break;
        case '3':
          handleSelect(2);
          break;
        case '4':
          handleSelect(3);
          break;
        case 'g':
        case 'G':
          setShowGhosts((prev) => !prev);
          break;
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [choices]);

  const handleSelect = useCallback(
    (index: number) => {
      if (index >= choices.length) return;

      setSelectedIndex(index);
      const selectedId = choices[index];

      // Short delay for visual feedback before closing
      setTimeout(() => {
        const alternatives = choices.filter((_, i) => i !== index);
        onSelect(selectedId, alternatives);
      }, 300);
    },
    [choices, onSelect]
  );

  // Get ability details for each choice
  const upgradeOptions = choices.map((id) => {
    const ability = getAbility(id as AbilityId);
    if (!ability) {
      // Fallback for unknown abilities
      return {
        id,
        name: id.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase()),
        description: 'Unknown ability',
        verb: 'Select',
        category: 'damage' as AbilityCategory,
        icon: '?',
        color: '#888888',
        effect: {},
        juiceConfig: { visual: 'Unknown effect' },
      } as Ability;
    }
    return ability;
  });

  // Get current level for each choice
  const getLevel = (abilityId: string) => {
    if (abilities) {
      return getAbilityLevel(abilities, abilityId as AbilityId);
    }
    return currentAbilities.filter(id => id === abilityId).length;
  };

  // Find synergies with owned abilities
  const getSynergies = (abilityId: AbilityId): AbilityId[] => {
    const synergiesForAbility = SYNERGIES[abilityId] || [];
    const ownedAbilities = abilities?.owned || currentAbilities;
    return synergiesForAbility.filter(id => ownedAbilities.includes(id));
  };

  return (
    <div className="fixed inset-0 bg-black/90 flex items-center justify-center z-50 animate-fade-in">
      <style>{styles}</style>

      <div className="max-w-5xl w-full mx-4">
        {/* Header */}
        <div className="text-center mb-8">
          <div
            className="text-6xl font-bold mb-2 animate-pulse"
            style={{ color: COLORS.xp, fontFamily: 'Rajdhani, sans-serif' }}
          >
            LEVEL {level}
          </div>
          <p className="text-gray-400 text-lg">Choose your power</p>
          <p className="text-gray-600 text-sm mt-1">
            Press 1, 2, or 3 to select | G for history
          </p>
        </div>

        {/* Upgrade Cards */}
        <div className="grid grid-cols-3 gap-6 mb-8">
          {upgradeOptions.map((ability, index) => {
            const categoryConfig = CATEGORY_CONFIG[ability.category];
            const currentLevel = getLevel(ability.id);
            const isOwned = currentLevel > 0;
            const maxStacks = ability.maxStacks || 1;
            const isMaxed = currentLevel >= maxStacks;
            const synergies = getSynergies(ability.id as AbilityId);
            const hasSynergy = synergies.length > 0;
            const isHovered = hoveredIndex === index;
            const isRiskReward = ability.isRiskReward;

            return (
              <button
                key={ability.id}
                onClick={() => handleSelect(index)}
                onMouseEnter={() => setHoveredIndex(index)}
                onMouseLeave={() => setHoveredIndex(null)}
                disabled={selectedIndex !== null}
                className={`
                  upgrade-card relative rounded-xl border-2 transition-all duration-200
                  ${isRiskReward ? 'risk-reward-card' : ''}
                  ${
                    selectedIndex === index
                      ? 'scale-105 border-yellow-400'
                      : selectedIndex !== null
                        ? 'opacity-40 border-gray-700'
                        : 'border-gray-700 hover:border-gray-500 hover:scale-102'
                  }
                `}
                style={{
                  backgroundColor: 'rgba(20, 20, 25, 0.95)',
                  borderColor: selectedIndex === index
                    ? COLORS.xp
                    : isOwned
                      ? `${ability.color}66`
                      : isRiskReward
                        ? '#FF000033'
                        : undefined,
                }}
              >
                {/* Category-colored glow effect */}
                <div
                  className="card-glow absolute inset-0 rounded-xl pointer-events-none"
                  style={{
                    background: `radial-gradient(ellipse at center, ${ability.color}20 0%, transparent 70%)`,
                    opacity: isHovered ? 0.8 : 0,
                  }}
                />

                {/* Card content */}
                <div className="relative p-5">
                  {/* Keyboard hint */}
                  <div className="absolute top-3 left-3 w-7 h-7 rounded bg-gray-800 text-gray-400 text-sm flex items-center justify-center font-mono font-bold">
                    {index + 1}
                  </div>

                  {/* Category badge */}
                  <div
                    className="absolute top-3 right-3 px-2 py-1 rounded text-xs font-bold uppercase tracking-wider flex items-center gap-1"
                    style={{
                      backgroundColor: `${categoryConfig.color}22`,
                      color: categoryConfig.color,
                    }}
                  >
                    <span>{categoryConfig.icon}</span>
                    <span>{categoryConfig.label}</span>
                  </div>

                  {/* Stack indicator (if owned and stackable) */}
                  {isOwned && maxStacks > 1 && !isMaxed && (
                    <div
                      className="stack-indicator absolute -top-2 left-1/2 -translate-x-1/2 px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider"
                      style={{
                        backgroundColor: `${ability.color}33`,
                        color: ability.color,
                        border: `1px solid ${ability.color}`,
                      }}
                    >
                      Level {currentLevel + 1}/{maxStacks}
                    </div>
                  )}

                  {/* Ability icon and name */}
                  <div className="mt-10 mb-3 flex items-center gap-3">
                    <span
                      className="ability-icon text-3xl"
                      style={{ filter: isHovered ? 'drop-shadow(0 0 8px currentColor)' : 'none' }}
                    >
                      {ability.icon}
                    </span>
                    <h3
                      className="text-xl font-bold tracking-wide"
                      style={{ color: ability.color, fontFamily: 'Rajdhani, sans-serif' }}
                    >
                      {ability.name}
                    </h3>
                  </div>

                  {/* Description - clear and simple */}
                  <p
                    className="text-lg font-semibold mb-3"
                    style={{ color: '#FFFFFF' }}
                  >
                    {ability.description}
                  </p>

                  {/* Horizontal divider */}
                  <div
                    className="h-0.5 mb-3 opacity-30"
                    style={{ backgroundColor: ability.color }}
                  />

                  {/* Visual effect preview */}
                  {ability.juiceConfig && (
                    <div className="mb-3">
                      <div className="text-xs text-gray-500 mb-1">VISUAL EFFECT:</div>
                      <div
                        className="text-sm"
                        style={{ color: `${ability.color}CC` }}
                      >
                        {ability.juiceConfig.visual}
                      </div>
                    </div>
                  )}

                  {/* Trigger text preview (what you see in-game) */}
                  {ability.juiceConfig?.triggerText && isHovered && (
                    <div
                      className="trigger-text absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 text-2xl font-black pointer-events-none"
                      style={{
                        color: ability.color,
                        textShadow: `0 0 20px ${ability.color}`,
                      }}
                    >
                      {ability.juiceConfig.triggerText}
                    </div>
                  )}

                  {/* Synergy indicator */}
                  {hasSynergy && (
                    <div
                      className="synergy-badge mt-2 px-2 py-1 rounded text-xs font-bold"
                      style={{
                        backgroundColor: '#FFD70022',
                        color: '#FFD700',
                        border: '1px solid #FFD70044',
                      }}
                    >
                      SYNERGY with: {synergies.map(id => {
                        const synAbility = getAbility(id);
                        return synAbility?.name || id;
                      }).join(', ')}
                    </div>
                  )}

                  {/* Risk/Reward warning */}
                  {isRiskReward && (
                    <div
                      className="mt-2 px-2 py-1 rounded text-xs font-bold"
                      style={{
                        backgroundColor: '#FF000022',
                        color: '#FF4444',
                        border: '1px solid #FF000044',
                      }}
                    >
                      HIGH RISK / HIGH REWARD
                    </div>
                  )}

                  {/* Combo potential indicator */}
                  {ability.comboPotential === 'high' && !hasSynergy && (
                    <div
                      className="mt-2 text-xs"
                      style={{ color: '#888888' }}
                    >
                      High combo potential
                    </div>
                  )}
                </div>

                {/* Selection highlight overlay */}
                {selectedIndex === index && (
                  <div
                    className="absolute inset-0 rounded-xl"
                    style={{
                      background: `linear-gradient(135deg, ${COLORS.xp}33 0%, transparent 50%)`,
                    }}
                  />
                )}

                {/* Animated preview particles on hover */}
                {isHovered && (
                  <div className="absolute inset-0 pointer-events-none overflow-hidden rounded-xl">
                    {[...Array(5)].map((_, i) => (
                      <div
                        key={i}
                        className="preview-particle absolute w-2 h-2 rounded-full"
                        style={{
                          backgroundColor: ability.color,
                          left: `${20 + i * 15}%`,
                          bottom: '20%',
                          animationDelay: `${i * 0.2}s`,
                        }}
                      />
                    ))}
                  </div>
                )}
              </button>
            );
          })}
        </div>

        {/* Currently owned abilities summary */}
        {(abilities?.owned?.length || currentAbilities.length) > 0 && (
          <div className="text-center mb-4">
            <span className="text-gray-500 text-sm">
              Current abilities:{' '}
              {(abilities?.owned || currentAbilities).map((id, i) => {
                const a = getAbility(id as AbilityId);
                return (
                  <span key={id}>
                    {i > 0 && ', '}
                    <span style={{ color: a?.color || '#888' }}>{a?.icon} {a?.name}</span>
                  </span>
                );
              })}
            </span>
          </div>
        )}

        {/* Ghost toggle hint */}
        <div className="text-center text-gray-600 text-sm">
          Press G to {showGhosts ? 'hide' : 'show'} previous choices
        </div>

        {/* Ghost Preview Section */}
        {showGhosts && recentGhosts.length > 0 && (
          <div className="mt-6 bg-gray-900/80 rounded-lg p-4 border border-gray-700">
            <h3
              className="text-sm font-medium mb-3"
              style={{ color: COLORS.ghost }}
            >
              Previous Paths Not Taken
            </h3>
            <div className="space-y-2">
              {recentGhosts.slice(-3).map((ghost, index) => (
                <div
                  key={index}
                  className="flex items-center gap-3 text-sm"
                  style={{ color: COLORS.ghost }}
                >
                  <span className="text-gray-500">Level {ghost.context.wave}:</span>
                  <span>Chose {formatAbilityName(ghost.chosen)}</span>
                  <span className="text-gray-600">|</span>
                  <span className="text-gray-500">
                    Passed: {ghost.unchosen.map(formatAbilityName).join(', ')}
                  </span>
                </div>
              ))}
            </div>
            <p className="text-xs text-gray-600 mt-3 italic">
              Every path holds its own wisdom.
            </p>
          </div>
        )}
      </div>
    </div>
  );
});

// =============================================================================
// Helpers
// =============================================================================

function formatAbilityName(id: string): string {
  const ability = getAbility(id as AbilityId);
  return ability?.name || id.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
}

export default UpgradeUI;
