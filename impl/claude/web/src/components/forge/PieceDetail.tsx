/**
 * PieceDetail: Full view of a gallery piece with provenance.
 *
 * Shows:
 * - Full content
 * - Artisan attribution
 * - Provenance (interpretation, considerations, choices, inspirations)
 * - Metadata (form, date)
 * - Delete action
 *
 * Theme: Orisinal.com aesthetic - minimal, gentle, content-first.
 */

// React import not needed for JSX in modern React
import type { Piece } from '@/api/atelier';

interface PieceDetailProps {
  piece: Piece;
  onDelete?: () => void;
  onInspiration?: (pieceId: string) => void;
}

export function PieceDetail({ piece, onDelete, onInspiration }: PieceDetailProps) {
  // Render content based on form
  const renderContent = () => {
    if (typeof piece.content === 'string') {
      return (
        <p className="text-stone-700 whitespace-pre-wrap font-serif text-lg leading-relaxed">
          {piece.content}
        </p>
      );
    }
    // For non-string content (like maps), render as formatted JSON
    return (
      <pre className="text-stone-600 text-sm font-mono bg-stone-50 p-4 rounded-lg overflow-x-auto">
        {JSON.stringify(piece.content, null, 2)}
      </pre>
    );
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <span className="text-xs font-medium text-stone-400 uppercase tracking-wide">
            {piece.form}
          </span>
          <h2 className="mt-1 text-lg font-medium text-stone-800">by {piece.artisan}</h2>
        </div>
        <span className="text-xs text-stone-300">
          {new Date(piece.created_at).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
          })}
        </span>
      </div>

      {/* Content */}
      <div className="py-6 border-y border-stone-100">{renderContent()}</div>

      {/* Provenance */}
      <div className="space-y-4">
        <h3 className="text-xs font-medium text-stone-400 uppercase tracking-wide">Provenance</h3>

        {/* Interpretation */}
        <div>
          <h4 className="text-sm font-medium text-stone-600 mb-1">Interpretation</h4>
          <p className="text-sm text-stone-500 italic">{piece.provenance.interpretation}</p>
        </div>

        {/* Considerations */}
        {piece.provenance.considerations.length > 0 && (
          <div>
            <h4 className="text-sm font-medium text-stone-600 mb-1">Considerations</h4>
            <ul className="list-disc list-inside text-sm text-stone-500 space-y-1">
              {piece.provenance.considerations.map((c, i) => (
                <li key={i}>{c}</li>
              ))}
            </ul>
          </div>
        )}

        {/* Choices */}
        {piece.provenance.choices.length > 0 && (
          <div>
            <h4 className="text-sm font-medium text-stone-600 mb-2">Creative Choices</h4>
            <div className="space-y-3">
              {piece.provenance.choices.map((choice, i) => (
                <div key={i} className="p-3 rounded-lg bg-stone-50 border border-stone-100">
                  <p className="text-sm text-stone-700 font-medium">{choice.decision}</p>
                  <p className="text-xs text-stone-500 mt-1">{choice.reason}</p>
                  {choice.alternatives.length > 0 && (
                    <p className="text-xs text-stone-400 mt-1">
                      Alternatives considered: {choice.alternatives.join(', ')}
                    </p>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Inspirations */}
        {piece.provenance.inspirations.length > 0 && (
          <div>
            <h4 className="text-sm font-medium text-stone-600 mb-1">Inspirations</h4>
            <div className="flex flex-wrap gap-2">
              {piece.provenance.inspirations.map((id) => (
                <button
                  key={id}
                  onClick={() => onInspiration?.(id)}
                  className="
                    px-2 py-1 text-xs rounded bg-amber-50 text-amber-700
                    hover:bg-amber-100 transition-colors
                  "
                >
                  {id.slice(0, 8)}...
                </button>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Actions */}
      <div className="pt-4 border-t border-stone-100 flex items-center justify-between">
        <span className="text-xs text-stone-300 font-mono">{piece.id}</span>
        {onDelete && (
          <button
            onClick={onDelete}
            className="
              px-3 py-1.5 text-xs text-stone-400 hover:text-red-500
              hover:bg-red-50 rounded transition-colors
            "
          >
            Delete
          </button>
        )}
      </div>
    </div>
  );
}

export default PieceDetail;
