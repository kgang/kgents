/**
 * PieceCard: Preview card for a gallery piece.
 *
 * Shows:
 * - Content preview
 * - Artisan attribution
 * - Form type
 * - Creation date
 */

// React import not needed for JSX in modern React
import type { PieceSummary } from '@/api/forge';

interface PieceCardProps {
  piece: PieceSummary;
  onClick?: () => void;
}

export function PieceCard({ piece, onClick }: PieceCardProps) {
  return (
    <button
      onClick={onClick}
      className="
        group w-full text-left p-4 rounded-lg border border-stone-200
        hover:border-amber-300 hover:shadow-sm
        transition-all duration-200 bg-white
      "
    >
      {/* Content Preview */}
      <p className="text-stone-700 text-sm line-clamp-3 mb-3 min-h-[3.5em]">{piece.preview}</p>

      {/* Meta Row */}
      <div className="flex items-center justify-between text-xs">
        <div className="flex items-center gap-2">
          {/* Artisan */}
          <span className="text-stone-600 font-medium">{piece.artisan}</span>
          {/* Form */}
          <span className="text-stone-400">· {piece.form}</span>
        </div>

        {/* Date */}
        <span className="text-stone-300">
          {new Date(piece.created_at).toLocaleDateString('en-US', {
            month: 'short',
            day: 'numeric',
          })}
        </span>
      </div>

      {/* Interpretation (on hover) */}
      <p className="mt-2 text-xs text-stone-400 italic opacity-0 group-hover:opacity-100 transition-opacity line-clamp-2">
        {piece.interpretation}
      </p>
    </button>
  );
}

export default PieceCard;
