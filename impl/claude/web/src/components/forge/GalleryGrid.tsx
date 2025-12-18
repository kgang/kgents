/**
 * GalleryGrid: Masonry-style grid of gallery pieces.
 *
 * Features:
 * - Responsive grid layout
 * - Loading states
 * - Empty states
 * - Artisan/form filtering
 *
 * Theme: Orisinal.com aesthetic - airy spacing, gentle transitions.
 */

// React import not needed for JSX in modern React
import type { PieceSummary } from '@/api/forge';
import { PieceCard } from './PieceCard';

interface GalleryGridProps {
  pieces: PieceSummary[];
  isLoading?: boolean;
  onPieceClick?: (pieceId: string) => void;
  emptyMessage?: string;
}

export function GalleryGrid({
  pieces,
  isLoading = false,
  onPieceClick,
  emptyMessage = 'The gallery awaits its first piece.',
}: GalleryGridProps) {
  // Loading skeleton
  if (isLoading) {
    return (
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {Array.from({ length: 6 }).map((_, i) => (
          <div key={i} className="h-32 rounded-lg bg-stone-100 animate-pulse" />
        ))}
      </div>
    );
  }

  // Empty state
  if (pieces.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-16 text-center">
        <span className="text-4xl text-stone-200 mb-4">◇</span>
        <p className="text-stone-400 text-sm italic">{emptyMessage}</p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
      {pieces.map((piece) => (
        <PieceCard key={piece.id} piece={piece} onClick={() => onPieceClick?.(piece.id)} />
      ))}
    </div>
  );
}

export default GalleryGrid;
