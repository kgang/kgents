/**
 * SpriteGallery - Grid of all created sprites
 *
 * L1: Visual-First Law - Sprites always visible.
 * L2: Backstory-Trace Law - Click sprite to see its origins.
 * L-FLAV-1: Every sprite includes fox, kitten, or seal elements.
 *
 * QA-4: Watching idle animation makes you want to know more.
 */

import { useState } from 'react';
import type { Sprite, AestheticWeight } from '@kgents/shared-primitives';
import { SpriteCanvas } from './SpriteCanvas';

interface SpriteGalleryProps {
  sprites: Sprite[];
  selectedSpriteId?: string;
  onSelectSprite: (sprite: Sprite) => void;
  onExportSprite?: (sprite: Sprite) => void;
}

/**
 * Display a gallery of sprite characters.
 */
export function SpriteGallery({
  sprites,
  selectedSpriteId,
  onSelectSprite,
  onExportSprite,
}: SpriteGalleryProps) {
  const [hoveredId, setHoveredId] = useState<string | null>(null);

  // Detect animal theme from sprite (by ID prefix or palette)
  const getAnimalTheme = (sprite: Sprite): 'fox' | 'kitten' | 'seal' | null => {
    const id = sprite.id.toLowerCase();
    if (id.includes('fox')) return 'fox';
    if (id.includes('kitten')) return 'kitten';
    if (id.includes('seal')) return 'seal';

    // Fallback: detect by dominant palette color
    const palette = sprite.palette.join('');
    if (palette.includes('D35400') || palette.includes('E67E22')) return 'fox';
    if (palette.includes('95A5A6') || palette.includes('F5B041')) return 'kitten';
    if (palette.includes('34495E') || palette.includes('5D6D7E')) return 'seal';

    return null;
  };

  const getThemeEmoji = (theme: 'fox' | 'kitten' | 'seal' | null): string => {
    if (theme === 'fox') return '🦊';
    if (theme === 'kitten') return '🐱';
    if (theme === 'seal') return '🦭';
    return '✨';
  };

  const getThemeBadgeColor = (theme: 'fox' | 'kitten' | 'seal' | null): string => {
    if (theme === 'fox') return 'bg-orange-500/20 text-orange-300';
    if (theme === 'kitten') return 'bg-pink-500/20 text-pink-300';
    if (theme === 'seal') return 'bg-blue-500/20 text-blue-300';
    return 'bg-slate-500/20 text-slate-300';
  };

  // Get primary weight for display
  const getPrimaryWeight = (weights: AestheticWeight[]): AestheticWeight | null => {
    if (!weights.length) return null;
    return weights.reduce((max, w) => (w.value > max.value ? w : max), weights[0]);
  };

  return (
    <div className="bg-slate-800 rounded-xl p-4">
      <h3 className="text-lg font-bold text-amber-300 mb-4 flex items-center gap-2">
        <span>🎨</span> Character Gallery
      </h3>

      {sprites.length === 0 ? (
        <div className="text-center py-12">
          <div className="text-4xl mb-4">🦊 🐱 🦭</div>
          <p className="text-slate-400">
            No characters yet. Create your first fox, kitten, or seal!
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          {sprites.map((sprite) => {
            const isSelected = sprite.id === selectedSpriteId;
            const isHovered = sprite.id === hoveredId;
            const theme = getAnimalTheme(sprite);
            const primaryWeight = getPrimaryWeight(sprite.weights);

            return (
              <div
                key={sprite.id}
                onClick={() => onSelectSprite(sprite)}
                onMouseEnter={() => setHoveredId(sprite.id)}
                onMouseLeave={() => setHoveredId(null)}
                className={`bg-slate-700 rounded-lg p-3 cursor-pointer transition-all ${
                  isSelected
                    ? 'ring-2 ring-amber-400 bg-slate-600'
                    : 'hover:bg-slate-650 hover:scale-105'
                }`}
              >
                {/* Sprite canvas (animates on hover) */}
                <div className="flex justify-center mb-3">
                  <SpriteCanvas
                    sprite={sprite}
                    scale={8}
                    animating={isHovered || isSelected}
                  />
                </div>

                {/* Name and theme */}
                <div className="flex items-center justify-between mb-2">
                  <span className="text-slate-200 text-sm font-medium truncate">
                    {sprite.name}
                  </span>
                  <span
                    className={`text-xs px-1.5 py-0.5 rounded ${getThemeBadgeColor(
                      theme
                    )}`}
                  >
                    {getThemeEmoji(theme)}
                  </span>
                </div>

                {/* Primary aesthetic weight */}
                {primaryWeight && (
                  <div className="flex items-center gap-2 text-xs text-slate-400">
                    <span className="capitalize">{primaryWeight.dimension}:</span>
                    <div className="flex-1 h-1 bg-slate-600 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-amber-400"
                        style={{ width: `${primaryWeight.value * 100}%` }}
                      />
                    </div>
                    <span>{Math.round(primaryWeight.value * 100)}%</span>
                  </div>
                )}

                {/* Vocabulary hint */}
                {primaryWeight?.vocabulary && (
                  <div className="text-xs text-slate-500 mt-1 italic">
                    "{primaryWeight.vocabulary}"
                  </div>
                )}

                {/* Export button (on hover) */}
                {isHovered && onExportSprite && (
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      onExportSprite(sprite);
                    }}
                    className="w-full mt-2 py-1 bg-slate-600 hover:bg-slate-500 text-slate-300 text-xs rounded transition-colors"
                  >
                    Export PNG
                  </button>
                )}
              </div>
            );
          })}
        </div>
      )}

      {/* Gallery stats */}
      {sprites.length > 0 && (
        <div className="mt-4 pt-4 border-t border-slate-700 flex items-center justify-between text-xs text-slate-500">
          <span>{sprites.length} characters created</span>
          <div className="flex items-center gap-3">
            <span>
              🦊 {sprites.filter((s) => getAnimalTheme(s) === 'fox').length}
            </span>
            <span>
              🐱 {sprites.filter((s) => getAnimalTheme(s) === 'kitten').length}
            </span>
            <span>
              🦭 {sprites.filter((s) => getAnimalTheme(s) === 'seal').length}
            </span>
          </div>
        </div>
      )}
    </div>
  );
}

export default SpriteGallery;
