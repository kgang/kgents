/**
 * WASM Survivors - Upgrade UI (DD-6)
 *
 * Level-up pause screen with verb-based ability choices.
 * Implements DD-2: Ghost as Honor - shows unchosen alternatives with neutral language.
 * Implements DD-5: Fun Floor - level-up = pause + fanfare.
 * Implements DD-6: Upgrades are Verbs - each ability changes how you play.
 *
 * @see pilots/wasm-survivors-game/.outline.md
 */

import { useState, useEffect, useCallback, useMemo } from 'react';
import type { Ghost } from '../types';
import { COLORS } from '../systems/juice';
import { getAbility, type Ability, type AbilityId, type AbilityCategory } from '../systems/abilities';
import { checkForCombos, createInitialComboState, type Combo, type ComboState } from '../systems/combos';

// =============================================================================
// Types
// =============================================================================

interface UpgradeUIProps {
  level: number;
  choices: string[];
  currentAbilities: AbilityId[];
  comboState?: ComboState;
  recentGhosts: Ghost[];
  onSelect: (upgradeId: string, alternatives: string[]) => void;
}

/**
 * Combo tier badge colors
 */
const COMBO_TIER_STYLES: Record<string, { bg: string; text: string; label: string }> = {
  obvious: { bg: '#4488FF33', text: '#4488FF', label: 'COMBO!' },
  common: { bg: '#FF880033', text: '#FF8800', label: 'COMBO!' },
  rare: { bg: '#9944FF33', text: '#9944FF', label: 'RARE COMBO!' },
  legendary: { bg: '#FFD70033', text: '#FFD700', label: 'LEGENDARY!' },
};

// =============================================================================
// Component
// =============================================================================

export function UpgradeUI({
  level,
  choices,
  currentAbilities,
  comboState,
  recentGhosts,
  onSelect,
}: UpgradeUIProps) {
  const [selectedIndex, setSelectedIndex] = useState<number | null>(null);
  const [showGhosts, setShowGhosts] = useState(false);
  const [newComboAnnouncement, setNewComboAnnouncement] = useState<Combo | null>(null);

  // Check which upgrades would discover combos
  const comboCompletions = useMemo(() => {
    const completions: Record<string, Combo[]> = {};
    for (const id of choices) {
      // Simulate adding this ability
      const simulatedOwned = [...currentAbilities, id as AbilityId];
      const mockAbilities = {
        owned: simulatedOwned,
        levels: {} as Record<AbilityId, number>,
        computed: {
          // Damage
          damageMultiplier: 1,
          flatDamage: 0,
          lowHpBonusDamage: 0,
          highHpBonusDamage: 0,
          poisonDamage: 0,
          doubleHitChance: 0,
          // Speed
          attackSpeedBonus: 0,
          speedMultiplier: 1,
          // Defense
          maxHpBonus: 0,
          damageReduction: 0,
          hpPerSecond: 0,
          lifestealPercent: 0,
          lowHpDefenseBonus: 0,
          hasRevive: false,
          // Special
          critChance: 0,
          critDamageMultiplier: 2.0,
          executeThreshold: 0,
          hasFullArc: false,
          hasChainKill: false,
          killStreakDamage: 0,
          // Status flags
          hasRiskReward: false,
          hasDoubleHit: false,
          hasExecution: false,
          // Skill-gated ability flags
          hasGrazeFrenzy: false,
          hasThermalMomentum: false,
          hasExecutionChain: false,
          hasGlassCannonMastery: false,
          hasVenomArchitect: false,
          // Legacy compatibility
          diveSpeedMultiplier: 1,
          hoverAttackSpeedBonus: 0,
          bleedEnabled: false,
          bleedDamage: 0,
          venomEnabled: false,
          venomType: 'none' as const,
          heatReduction: 0,
          activeFrenzyStacks: 0,
          isHollowCarapace: false,
          isBerserker: false,
        },
      };
      const tempState = comboState || createInitialComboState();
      const { newCombos } = checkForCombos(mockAbilities, tempState);
      completions[id] = newCombos;
    }
    return completions;
  }, [choices, currentAbilities, comboState]);

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

      // Check if this triggers a combo
      const completedCombos = comboCompletions[selectedId];
      if (completedCombos && completedCombos.length > 0) {
        // Show the first (most significant) combo
        setNewComboAnnouncement(completedCombos[0]);
        // Show combo announcement, then complete selection
        setTimeout(() => {
          setNewComboAnnouncement(null);
          const alternatives = choices.filter((_, i) => i !== index);
          onSelect(selectedId, alternatives);
        }, 1200); // Longer delay for combo announcement
      } else {
        // Normal selection delay
        setTimeout(() => {
          const alternatives = choices.filter((_, i) => i !== index);
          onSelect(selectedId, alternatives);
        }, 300);
      }
    },
    [choices, onSelect, comboCompletions]
  );

  // Get ability details for each choice
  const upgradeOptions = choices.map((id) => {
    const ability = getAbility(id as AbilityId);
    if (!ability) {
      // Fallback for unknown abilities
      return {
        id,
        name: id.replace(/_/g, ' '),
        description: 'Unknown ability',
        verb: 'Use',
        icon: '?',
        color: '#888888',
        category: 'special' as AbilityCategory,
        comboPotential: 'low' as const,
        effect: {},
      } as Ability;
    }
    return ability;
  });

  return (
    <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 animate-fade-in">
      <div className="max-w-4xl w-full mx-4">
        {/* Header */}
        <div className="text-center mb-8">
          <div
            className="text-6xl font-bold mb-2 animate-pulse"
            style={{ color: COLORS.xp }}
          >
            LEVEL {level}
          </div>
          <p className="text-gray-400 text-lg">Choose your ability</p>
          <p className="text-gray-600 text-sm mt-1">
            Press 1, 2, or 3 to select | G to view past choices
          </p>
        </div>

        {/* Upgrade Cards */}
        <div className="grid grid-cols-3 gap-4 mb-8">
          {upgradeOptions.map((upgrade, index) => {
            const completingCombos = comboCompletions[upgrade.id] || [];
            const hasComboGlow = completingCombos.length > 0;
            const firstCombo = completingCombos[0];

            return (
              <button
                key={upgrade.id}
                onClick={() => handleSelect(index)}
                disabled={selectedIndex !== null}
                className={`
                  relative p-6 rounded-xl border-2 transition-all duration-200
                  ${
                    selectedIndex === index
                      ? 'border-yellow-400 bg-yellow-400/20 scale-105'
                      : selectedIndex !== null
                        ? 'opacity-50 border-gray-700 bg-gray-900'
                        : hasComboGlow
                          ? 'border-orange-500 bg-gray-900 hover:bg-gray-800 combo-glow'
                          : 'border-gray-700 bg-gray-900 hover:border-gray-500 hover:bg-gray-800'
                  }
                `}
                style={{
                  borderColor:
                    selectedIndex === index ? COLORS.xp : hasComboGlow ? '#FF8800' : undefined,
                  boxShadow: hasComboGlow && selectedIndex === null
                    ? '0 0 20px rgba(255, 136, 0, 0.4), 0 0 40px rgba(255, 136, 0, 0.2)'
                    : undefined,
                }}
              >
                {/* Keyboard hint */}
                <div className="absolute top-2 left-2 w-6 h-6 rounded bg-gray-800 text-gray-400 text-sm flex items-center justify-center">
                  {index + 1}
                </div>

                {/* Verb tag */}
                {upgrade.verb && (
                  <div
                    className="absolute top-2 right-2 px-2 py-1 rounded text-xs font-medium uppercase tracking-wider"
                    style={{ backgroundColor: `${upgrade.color}33`, color: upgrade.color }}
                  >
                    {upgrade.verb}
                  </div>
                )}

                {/* Combo completion indicator */}
                {firstCombo && (
                  <div
                    className="absolute -top-3 left-1/2 -translate-x-1/2 px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider animate-pulse"
                    style={{
                      backgroundColor: COMBO_TIER_STYLES[firstCombo.tier].bg,
                      color: COMBO_TIER_STYLES[firstCombo.tier].text,
                      border: `1px solid ${COMBO_TIER_STYLES[firstCombo.tier].text}`,
                    }}
                  >
                    {COMBO_TIER_STYLES[firstCombo.tier].label}
                  </div>
                )}

                {/* Icon */}
                <div
                  className="text-4xl mb-4"
                  style={{ color: upgrade.color }}
                >
                  {upgrade.icon}
                </div>

                {/* Name */}
                <div className="text-xl font-bold text-white mb-2">
                  {upgrade.name}
                </div>

                {/* Description */}
                <div className="text-gray-400 text-sm mb-2">
                  {upgrade.description}
                </div>

                {/* Combo preview */}
                {firstCombo && (
                  <div
                    className="text-xs mt-2 px-2 py-1 rounded"
                    style={{
                      backgroundColor: COMBO_TIER_STYLES[firstCombo.tier].bg,
                      color: COMBO_TIER_STYLES[firstCombo.tier].text,
                    }}
                  >
                    + {firstCombo.name}: {firstCombo.description}
                  </div>
                )}

                {/* Risk/Reward indicator */}
                {upgrade.isRiskReward && (
                  <div className="flex gap-1 mt-2 flex-wrap justify-center">
                    <span
                      className="text-xs px-1.5 py-0.5 rounded"
                      style={{
                        backgroundColor: '#FF000022',
                        color: '#FF4444',
                      }}
                    >
                      RISK/REWARD
                    </span>
                  </div>
                )}

                {/* Already owned indicator (stacking) */}
                {currentAbilities.includes(upgrade.id) && (
                  <div className="text-xs text-yellow-500 mt-2">
                    + STACKING
                  </div>
                )}
              </button>
            );
          })}
        </div>

        {/* Combo announcement overlay */}
        {newComboAnnouncement && (
          <div className="fixed inset-0 flex items-center justify-center z-60 pointer-events-none">
            <div
              className="text-center animate-combo-burst"
              style={{ color: COMBO_TIER_STYLES[newComboAnnouncement.tier].text }}
            >
              <div className="text-5xl font-black mb-2 tracking-wider">
                {newComboAnnouncement.announcement}
              </div>
              <div className="text-2xl font-medium opacity-80">
                {newComboAnnouncement.description}
              </div>
            </div>
          </div>
        )}

        {/* Ghost Preview Section (DD-2: Ghost as Honor) */}
        {showGhosts && recentGhosts.length > 0 && (
          <div className="bg-gray-900/80 rounded-lg p-4 border border-gray-700">
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
                    Alternative: {ghost.unchosen.map(formatAbilityName).join(', ')}
                  </span>
                </div>
              ))}
            </div>
            <p className="text-xs text-gray-600 mt-3 italic">
              Every path holds its own wisdom. These alternatives were equally
              valid.
            </p>
          </div>
        )}

        {/* Ghost toggle hint */}
        {recentGhosts.length > 0 && !showGhosts && (
          <div className="text-center">
            <button
              onClick={() => setShowGhosts(true)}
              className="text-gray-500 text-sm hover:text-gray-400 transition-colors"
            >
              Press G to view past choices
            </button>
          </div>
        )}
      </div>

      <style>{`
        @keyframes fade-in {
          from { opacity: 0; transform: scale(0.95); }
          to { opacity: 1; transform: scale(1); }
        }
        .animate-fade-in {
          animation: fade-in 0.3s ease-out;
        }
        @keyframes combo-burst {
          0% { opacity: 0; transform: scale(0.5); }
          20% { opacity: 1; transform: scale(1.1); }
          40% { transform: scale(1); }
          80% { opacity: 1; }
          100% { opacity: 0; transform: scale(1.05); }
        }
        .animate-combo-burst {
          animation: combo-burst 1.2s ease-out forwards;
        }
        @keyframes combo-glow-pulse {
          0%, 100% { box-shadow: 0 0 20px rgba(255, 136, 0, 0.4), 0 0 40px rgba(255, 136, 0, 0.2); }
          50% { box-shadow: 0 0 30px rgba(255, 136, 0, 0.6), 0 0 60px rgba(255, 136, 0, 0.3); }
        }
        .combo-glow {
          animation: combo-glow-pulse 1.5s ease-in-out infinite;
        }
      `}</style>
    </div>
  );
}

// =============================================================================
// Helpers
// =============================================================================

function formatAbilityName(id: string): string {
  const ability = getAbility(id as AbilityId);
  return ability?.name || id.replace(/_/g, ' ');
}

export default UpgradeUI;
