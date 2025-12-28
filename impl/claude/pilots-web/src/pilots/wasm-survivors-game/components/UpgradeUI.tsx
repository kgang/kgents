/**
 * WASM Survivors - Upgrade UI (DD-6)
 *
 * Level-up pause screen with verb-based upgrade choices.
 * Implements DD-2: Ghost as Honor - shows unchosen alternatives with neutral language.
 * Implements DD-5: Fun Floor - level-up = pause + fanfare.
 * Implements DD-6: Upgrades are Verbs - each upgrade changes how you play.
 *
 * @see pilots/wasm-survivors-game/.outline.md
 */

import { useState, useEffect, useCallback } from 'react';
import type { Ghost } from '@kgents/shared-primitives';
import { COLORS } from '../systems/juice';
import { getUpgrade, type VerbUpgrade, type UpgradeType } from '../systems/upgrades';

// =============================================================================
// Types
// =============================================================================

interface UpgradeUIProps {
  level: number;
  choices: string[];
  currentUpgrades: string[];
  recentGhosts: Ghost[];
  onSelect: (upgradeId: string, alternatives: string[]) => void;
}

// =============================================================================
// Component
// =============================================================================

export function UpgradeUI({
  level,
  choices,
  currentUpgrades,
  recentGhosts,
  onSelect,
}: UpgradeUIProps) {
  const [selectedIndex, setSelectedIndex] = useState<number | null>(null);
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

      // Delay to show selection animation
      setTimeout(() => {
        const selectedId = choices[index];
        const alternatives = choices.filter((_, i) => i !== index);
        onSelect(selectedId, alternatives);
      }, 300);
    },
    [choices, onSelect]
  );

  // Get upgrade details for each choice
  const upgradeOptions = choices.map((id) => {
    const upgrade = getUpgrade(id as UpgradeType);
    if (!upgrade) {
      // Fallback for legacy upgrades
      return {
        id,
        name: id.replace(/_/g, ' '),
        description: 'Unknown upgrade',
        verb: 'do',
        icon: '?',
        color: '#888888',
        isVerb: false,
      } as VerbUpgrade & { isVerb: boolean };
    }

    return { ...upgrade, isVerb: true };
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
          {upgradeOptions.map((upgrade, index) => (
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
                      : 'border-gray-700 bg-gray-900 hover:border-gray-500 hover:bg-gray-800'
                }
              `}
              style={{
                borderColor:
                  selectedIndex === index ? COLORS.xp : undefined,
              }}
            >
              {/* Keyboard hint */}
              <div className="absolute top-2 left-2 w-6 h-6 rounded bg-gray-800 text-gray-400 text-sm flex items-center justify-center">
                {index + 1}
              </div>

              {/* Verb tag - DD-6 */}
              {'verb' in upgrade && upgrade.verb && (
                <div
                  className="absolute top-2 right-2 px-2 py-1 rounded text-xs font-medium uppercase tracking-wider"
                  style={{ backgroundColor: `${upgrade.color}33`, color: upgrade.color }}
                >
                  {upgrade.verb}
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
              <div className="text-gray-400 text-sm mb-4">
                {upgrade.description}
              </div>

              {/* Already owned indicator */}
              {currentUpgrades.includes(upgrade.id) && (
                <div className="text-xs text-yellow-500">
                  ⬆ UPGRADED
                </div>
              )}
            </button>
          ))}
        </div>

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
                  <span>Chose {formatUpgradeName(ghost.chosen)}</span>
                  <span className="text-gray-600">|</span>
                  <span className="text-gray-500">
                    Alternative: {ghost.unchosen.map(formatUpgradeName).join(', ')}
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
      `}</style>
    </div>
  );
}

// =============================================================================
// Helpers
// =============================================================================

function formatUpgradeName(id: string): string {
  const upgrade = getUpgrade(id as UpgradeType);
  return upgrade?.name || id.replace(/_/g, ' ');
}

export default UpgradeUI;
