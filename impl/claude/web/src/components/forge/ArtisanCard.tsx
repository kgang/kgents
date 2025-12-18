/**
 * ArtisanCard: Display for an individual artisan.
 *
 * Theme: Orisinal.com aesthetic - whimsical, minimal, melancholic but hopeful.
 * Gentle borders, soft colors, understated animation.
 *
 * Wave 2: Enhanced with eigenvector personality visualization.
 */

import { useState } from 'react';
import type { Artisan } from '@/api/atelier';
import { EigenvectorRadar, EigenvectorBars } from '@/components/eigenvector';

interface ArtisanCardProps {
  artisan: Artisan;
  selected?: boolean;
  onClick?: () => void;
  disabled?: boolean;
  showEigenvector?: boolean;
  compactEigenvector?: boolean;
}

export function ArtisanCard({
  artisan,
  selected = false,
  onClick,
  disabled = false,
  showEigenvector = false,
  compactEigenvector = true,
}: ArtisanCardProps) {
  const [showRadar, setShowRadar] = useState(false);

  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={`
        group relative p-4 rounded-lg border text-left transition-all duration-200
        ${
          selected
            ? 'border-amber-400 bg-amber-50/50 shadow-sm'
            : 'border-stone-200 bg-white hover:border-stone-300 hover:shadow-sm'
        }
        ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
      `}
    >
      {/* Selection indicator */}
      {selected && <div className="absolute top-2 right-2 w-2 h-2 rounded-full bg-amber-400" />}

      {/* Artisan name */}
      <h3 className="font-medium text-stone-800 mb-1">{artisan.name}</h3>

      {/* Specialty */}
      <p className="text-sm text-stone-500 italic">{artisan.specialty}</p>

      {/* Eigenvector visualization (Wave 2) */}
      {showEigenvector && artisan.eigenvector && (
        <div className="mt-3">
          {compactEigenvector ? (
            <EigenvectorBars
              dimensions={artisan.eigenvector}
              compact
              showLabels
              className="group-hover:opacity-100 opacity-70 transition-opacity"
            />
          ) : (
            <div className="relative">
              {/* Toggle button */}
              <button
                type="button"
                onClick={(e) => {
                  e.stopPropagation();
                  setShowRadar(!showRadar);
                }}
                className="absolute top-0 right-0 text-xs text-stone-400 hover:text-stone-600"
              >
                {showRadar ? '◐' : '◑'}
              </button>

              {showRadar ? (
                <EigenvectorRadar
                  dimensions={artisan.eigenvector}
                  size={120}
                  showLabels={false}
                  animated
                  className="mx-auto"
                />
              ) : (
                <EigenvectorBars
                  dimensions={artisan.eigenvector}
                  showLabels
                  className="group-hover:opacity-100 opacity-70 transition-opacity"
                />
              )}
            </div>
          )}
        </div>
      )}

      {/* Personality preview (on hover, when eigenvector not shown) */}
      {!showEigenvector && artisan.personality && (
        <p className="mt-2 text-xs text-stone-400 opacity-0 group-hover:opacity-100 transition-opacity line-clamp-2">
          {artisan.personality}
        </p>
      )}
    </button>
  );
}

export default ArtisanCard;
