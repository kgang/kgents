/**
 * WASM Survivors - Upgrade UI (WILD UPGRADES)
 *
 * Level-up pause screen with WILD, game-changing upgrade choices.
 * "Each upgrade should be SERIOUSLY WILD, not simple stat improvements."
 *
 * DESIGN:
 * - Each upgrade has unique visual identity (icon, colors, particles)
 * - Synergy preview showing combos with owned upgrades
 * - Taglines that communicate the fantasy
 * - No boring stat upgrades - every choice changes gameplay
 *
 * THE EIGHT WILD UPGRADES:
 * 1. ECHO - Ghost hornet repeats all actions 0.5s later
 * 2. GRAVITY_WELL - Enemies orbit you, collide and explode
 * 3. METAMORPHOSIS - Transform into different creatures every 30s
 * 4. BLOOD_PRICE - Spend HP to supercharge; low HP = god mode
 * 5. TEMPORAL_DEBT - Freeze time 3s, then 2x speed for 6s
 * 6. SWARM_MIND - Split into 5 mini-hornets
 * 7. HONEY_TRAP - Sticky zones that chain enemies together
 * 8. ROYAL_DECREE - Mark enemy as "The King" that others attack
 *
 * @see pilots/wasm-survivors-game/systems/wild-upgrades.ts
 */

import { useState, useEffect, useCallback, memo } from 'react';
import type { Ghost } from '../types';
import { COLORS } from '../systems/juice';
import {
  type WildUpgradeType,
  type WildUpgrade,
  getWildUpgrade,
  getWildSynergy,
} from '../systems/wild-upgrades';

// =============================================================================
// Types
// =============================================================================

interface UpgradeUIProps {
  level: number;
  choices: string[];
  currentAbilities: WildUpgradeType[];
  recentGhosts: Ghost[];
  onSelect: (upgradeId: string, alternatives: string[]) => void;
}

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

  // Get wild upgrade details for each choice
  const upgradeOptions = choices.map((id) => {
    const upgrade = getWildUpgrade(id as WildUpgradeType);
    if (!upgrade) {
      // Fallback for unknown upgrades
      return {
        id,
        name: id.replace(/_/g, ' ').toUpperCase(),
        tagline: 'Unknown power',
        description: 'A mysterious upgrade',
        icon: '?',
        color: '#888888',
        colorSecondary: '#666666',
        particleSystem: 'default',
        screenEffect: 'none',
        soundTheme: 'default',
        synergies: {},
      } as WildUpgrade;
    }
    return upgrade;
  });

  // Check if upgrade is already owned (wild upgrades are one-time, not stackable)
  const isOwned = (upgradeId: string) => {
    return currentAbilities.includes(upgradeId as WildUpgradeType);
  };

  // Find synergies with owned upgrades
  const getSynergiesWithOwned = (upgradeId: WildUpgradeType) => {
    const synergies: Array<{ name: string; description: string }> = [];
    for (const owned of currentAbilities) {
      const synergy = getWildSynergy(upgradeId, owned);
      if (synergy && synergy.name !== 'Self') {
        synergies.push({ name: synergy.name, description: synergy.description });
      }
    }
    return synergies;
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
          <p className="text-gray-400 text-lg">Choose your WILD power</p>
          <p className="text-gray-600 text-sm mt-1">
            Press 1, 2, or 3 to select | G for history
          </p>
        </div>

        {/* Upgrade Cards */}
        <div className="grid grid-cols-3 gap-6 mb-8">
          {upgradeOptions.map((upgrade, index) => {
            const owned = isOwned(upgrade.id);
            const synergiesWithOwned = getSynergiesWithOwned(upgrade.id as WildUpgradeType);
            const hasSynergy = synergiesWithOwned.length > 0;
            const isHovered = hoveredIndex === index;

            return (
              <button
                key={upgrade.id}
                onClick={() => handleSelect(index)}
                onMouseEnter={() => setHoveredIndex(index)}
                onMouseLeave={() => setHoveredIndex(null)}
                disabled={selectedIndex !== null || owned}
                className={`
                  upgrade-card relative rounded-xl border-2 transition-all duration-200
                  ${
                    selectedIndex === index
                      ? 'scale-105 border-yellow-400'
                      : selectedIndex !== null
                        ? 'opacity-40 border-gray-700'
                        : owned
                          ? 'opacity-50 border-gray-600 cursor-not-allowed'
                          : 'border-gray-700 hover:border-gray-500 hover:scale-102'
                  }
                `}
                style={{
                  backgroundColor: 'rgba(20, 20, 25, 0.95)',
                  borderColor: selectedIndex === index
                    ? COLORS.xp
                    : owned
                      ? `${upgrade.color}44`
                      : hasSynergy
                        ? `${upgrade.color}66`
                        : undefined,
                }}
              >
                {/* Upgrade-colored glow effect */}
                <div
                  className="card-glow absolute inset-0 rounded-xl pointer-events-none"
                  style={{
                    background: `radial-gradient(ellipse at center, ${upgrade.color}20 0%, transparent 70%)`,
                    opacity: isHovered ? 0.8 : 0,
                  }}
                />

                {/* Card content */}
                <div className="relative p-5">
                  {/* Keyboard hint */}
                  <div className="absolute top-3 left-3 w-7 h-7 rounded bg-gray-800 text-gray-400 text-sm flex items-center justify-center font-mono font-bold">
                    {index + 1}
                  </div>

                  {/* WILD badge */}
                  <div
                    className="absolute top-3 right-3 px-2 py-1 rounded text-xs font-bold uppercase tracking-wider"
                    style={{
                      backgroundColor: `${upgrade.color}22`,
                      color: upgrade.color,
                    }}
                  >
                    WILD
                  </div>

                  {/* Already owned indicator */}
                  {owned && (
                    <div
                      className="absolute -top-2 left-1/2 -translate-x-1/2 px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider"
                      style={{
                        backgroundColor: '#44444488',
                        color: '#888888',
                      }}
                    >
                      OWNED
                    </div>
                  )}

                  {/* Upgrade icon and name */}
                  <div className="mt-10 mb-2 flex items-center gap-3">
                    <span
                      className="ability-icon text-4xl"
                      style={{ filter: isHovered ? `drop-shadow(0 0 12px ${upgrade.color})` : 'none' }}
                    >
                      {upgrade.icon}
                    </span>
                    <h3
                      className="text-2xl font-black tracking-wide"
                      style={{ color: upgrade.color, fontFamily: 'Rajdhani, sans-serif' }}
                    >
                      {upgrade.name}
                    </h3>
                  </div>

                  {/* Tagline - the hook */}
                  <p
                    className="text-sm italic mb-2"
                    style={{ color: upgrade.colorSecondary }}
                  >
                    "{upgrade.tagline}"
                  </p>

                  {/* Horizontal divider */}
                  <div
                    className="h-0.5 mb-3 opacity-30"
                    style={{ backgroundColor: upgrade.color }}
                  />

                  {/* Description - what it actually does */}
                  <p
                    className="text-sm mb-3"
                    style={{ color: '#CCCCCC' }}
                  >
                    {upgrade.description}
                  </p>

                  {/* Synergy preview on hover */}
                  {hasSynergy && (
                    <div
                      className="synergy-badge mt-2 px-2 py-1 rounded text-xs font-bold"
                      style={{
                        backgroundColor: '#FFD70022',
                        color: '#FFD700',
                        border: '1px solid #FFD70044',
                      }}
                    >
                      SYNERGY: {synergiesWithOwned.map(s => s.name).join(', ')}
                    </div>
                  )}

                  {/* Show synergy detail on hover */}
                  {isHovered && hasSynergy && (
                    <div className="mt-2 text-xs text-gray-400">
                      {synergiesWithOwned[0]?.description}
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
                {isHovered && !owned && (
                  <div className="absolute inset-0 pointer-events-none overflow-hidden rounded-xl">
                    {[...Array(5)].map((_, i) => (
                      <div
                        key={i}
                        className="preview-particle absolute w-2 h-2 rounded-full"
                        style={{
                          backgroundColor: upgrade.color,
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

        {/* Currently owned wild upgrades summary */}
        {currentAbilities.length > 0 && (
          <div className="text-center mb-4">
            <span className="text-gray-500 text-sm">
              Current powers:{' '}
              {currentAbilities.map((id, i) => {
                const u = getWildUpgrade(id);
                return (
                  <span key={id}>
                    {i > 0 && ', '}
                    <span style={{ color: u?.color || '#888' }}>{u?.icon} {u?.name}</span>
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
                  <span>Chose {formatUpgradeName(ghost.chosen)}</span>
                  <span className="text-gray-600">|</span>
                  <span className="text-gray-500">
                    Passed: {ghost.unchosen.map(formatUpgradeName).join(', ')}
                  </span>
                </div>
              ))}
            </div>
            <p className="text-xs text-gray-600 mt-3 italic">
              Every path holds its own power.
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

function formatUpgradeName(id: string): string {
  const upgrade = getWildUpgrade(id as WildUpgradeType);
  return upgrade?.name || id.replace(/_/g, ' ').toUpperCase();
}

export default UpgradeUI;
