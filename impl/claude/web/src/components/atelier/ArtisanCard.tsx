/**
 * ArtisanCard: Display for an individual artisan.
 *
 * Theme: Orisinal.com aesthetic - whimsical, minimal, melancholic but hopeful.
 * Gentle borders, soft colors, understated animation.
 */

// React import not needed for JSX in modern React
import type { Artisan } from '@/api/atelier';

interface ArtisanCardProps {
  artisan: Artisan;
  selected?: boolean;
  onClick?: () => void;
  disabled?: boolean;
}

export function ArtisanCard({
  artisan,
  selected = false,
  onClick,
  disabled = false,
}: ArtisanCardProps) {
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
      {selected && (
        <div className="absolute top-2 right-2 w-2 h-2 rounded-full bg-amber-400" />
      )}

      {/* Artisan name */}
      <h3 className="font-medium text-stone-800 mb-1">{artisan.name}</h3>

      {/* Specialty */}
      <p className="text-sm text-stone-500 italic">{artisan.specialty}</p>

      {/* Personality preview (on hover) */}
      {artisan.personality && (
        <p className="mt-2 text-xs text-stone-400 opacity-0 group-hover:opacity-100 transition-opacity line-clamp-2">
          {artisan.personality}
        </p>
      )}
    </button>
  );
}

export default ArtisanCard;
