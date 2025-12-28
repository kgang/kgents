/**
 * TasteGravityField - Visual representation of style attraction
 *
 * L1: Taste Gravity Law - The system reveals pull toward the attractor.
 * "The artist sees the field."
 *
 * This component visualizes the aesthetic weight space and shows
 * where the current style sits relative to the canonical attractor.
 *
 * Flavor vocabulary: playful, cunning, graceful, sleek, agile, curious.
 */

import { useMemo } from 'react';
import type { TasteAttractor, AestheticWeight } from '@kgents/shared-primitives';

interface TasteGravityFieldProps {
  attractor: TasteAttractor;
  currentWeights?: AestheticWeight[];
  wildThreshold?: number;
}

/**
 * Render a gravity field visualization for taste space.
 */
export function TasteGravityField({
  attractor,
  currentWeights,
  wildThreshold = 0.3,
}: TasteGravityFieldProps) {
  // Compute all dimensions to display
  const dimensions = useMemo(() => {
    const allDimensions = new Set<string>();

    attractor.canonical_weights.forEach((w) => allDimensions.add(w.dimension));
    currentWeights?.forEach((w) => allDimensions.add(w.dimension));

    return Array.from(allDimensions);
  }, [attractor, currentWeights]);

  // Get weight value for a dimension
  const getWeight = (weights: AestheticWeight[], dimension: string): number => {
    const weight = weights.find((w) => w.dimension === dimension);
    return weight?.value ?? 0.5;
  };

  // Get vocabulary for a dimension
  const getVocab = (weights: AestheticWeight[], dimension: string): string | undefined => {
    const weight = weights.find((w) => w.dimension === dimension);
    return weight?.vocabulary;
  };

  return (
    <div className="bg-slate-800 rounded-xl p-4">
      {/* Header with stability indicator */}
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-bold text-amber-300 flex items-center gap-2">
          <span>✨</span> Style Attractor
        </h3>
        <div className="flex items-center gap-2">
          <span className="text-slate-400 text-sm">Stability:</span>
          <div className="w-24 h-2 bg-slate-700 rounded-full overflow-hidden">
            <div
              className={`h-full transition-all ${
                attractor.stability > 0.7
                  ? 'bg-green-400'
                  : attractor.stability > 0.4
                  ? 'bg-amber-400'
                  : 'bg-red-400'
              }`}
              style={{ width: `${attractor.stability * 100}%` }}
            />
          </div>
          <span className="text-slate-300 text-sm font-mono">
            {Math.round(attractor.stability * 100)}%
          </span>
        </div>
      </div>

      {/* Style description */}
      <p className="text-slate-300 text-sm mb-4 italic">
        "{attractor.style_description}"
      </p>

      {/* Dimension bars */}
      <div className="space-y-3">
        {dimensions.map((dimension) => {
          const canonicalValue = getWeight(attractor.canonical_weights, dimension);
          const currentValue = currentWeights
            ? getWeight(currentWeights, dimension)
            : canonicalValue;
          const vocab =
            getVocab(attractor.canonical_weights, dimension) ||
            getVocab(currentWeights || [], dimension);

          const drift = Math.abs(canonicalValue - currentValue);
          const isWild = drift > wildThreshold;

          return (
            <div key={dimension} className="space-y-1">
              {/* Label row */}
              <div className="flex items-center justify-between">
                <span className="text-slate-300 text-sm capitalize">
                  {dimension}
                  {vocab && (
                    <span className="text-slate-500 text-xs ml-2">
                      ({vocab})
                    </span>
                  )}
                </span>
                {isWild && (
                  <span className="text-purple-400 text-xs animate-pulse">
                    🌀 wild drift
                  </span>
                )}
              </div>

              {/* Bar */}
              <div className="relative h-3 bg-slate-700 rounded-full overflow-hidden">
                {/* Canonical position marker */}
                <div
                  className="absolute top-0 bottom-0 w-0.5 bg-amber-400 z-10"
                  style={{ left: `${canonicalValue * 100}%` }}
                />

                {/* Current position fill */}
                <div
                  className={`h-full transition-all ${
                    isWild ? 'bg-purple-500' : 'bg-green-500'
                  }`}
                  style={{ width: `${currentValue * 100}%` }}
                />

                {/* Current position dot */}
                <div
                  className={`absolute top-1/2 -translate-y-1/2 w-3 h-3 rounded-full border-2 transition-all ${
                    isWild
                      ? 'bg-purple-400 border-purple-200'
                      : 'bg-green-400 border-green-200'
                  }`}
                  style={{ left: `calc(${currentValue * 100}% - 6px)` }}
                />
              </div>

              {/* Scale labels */}
              <div className="flex justify-between text-[10px] text-slate-500">
                <span>low</span>
                <span>high</span>
              </div>
            </div>
          );
        })}
      </div>

      {/* Emergent vocabulary */}
      {attractor.emergent_vocabulary.length > 0 && (
        <div className="mt-4 pt-4 border-t border-slate-700">
          <span className="text-slate-400 text-xs block mb-2">
            Emergent vocabulary:
          </span>
          <div className="flex flex-wrap gap-2">
            {attractor.emergent_vocabulary.map((word) => (
              <span
                key={word}
                className="px-2 py-1 bg-slate-700 text-slate-300 text-xs rounded-full"
              >
                {word}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Wild threshold indicator */}
      <div className="mt-4 pt-4 border-t border-slate-700 text-xs text-slate-500">
        <span className="flex items-center gap-2">
          <span
            className="w-2 h-2 rounded-full"
            style={{ background: `rgba(168, 85, 247, 0.5)` }}
          />
          Wild threshold: {Math.round(wildThreshold * 100)}% drift from canon
        </span>
      </div>
    </div>
  );
}

export default TasteGravityField;
