/**
 * StyleCrystalView - Compressed proof of style stability
 *
 * L5: Style Continuity Law - Crystal justifies why style is stable.
 * "Stability is earned, not assumed."
 *
 * QA-3: Difference between first and final should be dramatic.
 * QA-5: System's rationale makes you say "oh, that's clever."
 */

import type { StyleCrystal } from '@kgents/shared-primitives';

interface StyleCrystalViewProps {
  crystal: StyleCrystal;
  onClose?: () => void;
}

/**
 * Display a style crystal - the compressed proof of a style journey.
 */
export function StyleCrystalView({ crystal, onClose }: StyleCrystalViewProps) {
  // Format percentage
  const pct = (v: number) => `${Math.round(v * 100)}%`;

  // Calculate acceptance rate
  const acceptanceRate =
    crystal.mutations_explored > 0
      ? crystal.mutations_accepted / crystal.mutations_explored
      : 0;

  return (
    <div className="bg-gradient-to-br from-slate-800 to-slate-900 rounded-xl p-6 border border-amber-500/30 shadow-lg shadow-amber-500/10">
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-3">
          <span className="text-4xl">💎</span>
          <div>
            <h3 className="text-xl font-bold text-amber-300">Style Crystal</h3>
            <p className="text-slate-400 text-sm">
              {new Date(crystal.created_at).toLocaleDateString()}
            </p>
          </div>
        </div>
        {onClose && (
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-white text-xl"
          >
            ×
          </button>
        )}
      </div>

      {/* Journey Summary (L5) */}
      <div className="bg-slate-700/50 rounded-lg p-4 mb-4">
        <h4 className="text-amber-300 text-sm font-medium mb-2">The Journey</h4>
        <p className="text-slate-200 text-sm leading-relaxed">
          {crystal.journey_summary}
        </p>
      </div>

      {/* Stability Justification (L5) */}
      <div className="bg-slate-700/50 rounded-lg p-4 mb-4">
        <h4 className="text-amber-300 text-sm font-medium mb-2 flex items-center gap-2">
          <span>✨</span> Why This Style is Stable
        </h4>
        <p className="text-slate-200 text-sm leading-relaxed italic">
          "{crystal.stability_justification}"
        </p>
      </div>

      {/* Key Decisions */}
      {crystal.key_decisions.length > 0 && (
        <div className="mb-4">
          <h4 className="text-amber-300 text-sm font-medium mb-2">
            Key Decisions
          </h4>
          <ul className="space-y-2">
            {crystal.key_decisions.map((decision, index) => (
              <li
                key={index}
                className="flex items-start gap-2 text-sm text-slate-300"
              >
                <span className="text-amber-400">→</span>
                <span>{decision}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Final Aesthetic Weights */}
      <div className="mb-4">
        <h4 className="text-amber-300 text-sm font-medium mb-2">
          Final Aesthetic Signature
        </h4>
        <div className="grid grid-cols-2 gap-2">
          {crystal.final_weights.map((weight) => (
            <div
              key={weight.dimension}
              className="bg-slate-700 rounded-lg p-2 flex items-center justify-between"
            >
              <span className="text-slate-300 text-sm capitalize">
                {weight.dimension}
              </span>
              <div className="flex items-center gap-2">
                <div className="w-16 h-1.5 bg-slate-600 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-amber-400"
                    style={{ width: pct(weight.value) }}
                  />
                </div>
                <span className="text-slate-400 text-xs font-mono w-8">
                  {pct(weight.value)}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
        <div className="bg-slate-700 rounded-lg p-3 text-center">
          <div className="text-2xl font-bold text-amber-300">
            {crystal.mutations_explored}
          </div>
          <div className="text-xs text-slate-400">Mutations Explored</div>
        </div>
        <div className="bg-slate-700 rounded-lg p-3 text-center">
          <div className="text-2xl font-bold text-green-400">
            {crystal.mutations_accepted}
          </div>
          <div className="text-xs text-slate-400">Accepted</div>
        </div>
        <div className="bg-slate-700 rounded-lg p-3 text-center">
          <div className="text-2xl font-bold text-purple-400">
            {crystal.wild_branches}
          </div>
          <div className="text-xs text-slate-400">Wild Branches</div>
        </div>
        <div className="bg-slate-700 rounded-lg p-3 text-center">
          <div className="text-2xl font-bold text-blue-400">
            {crystal.branches_explored}
          </div>
          <div className="text-xs text-slate-400">Branches</div>
        </div>
      </div>

      {/* Final Loss Indicator */}
      <div className="flex items-center justify-between bg-slate-700/50 rounded-lg p-3">
        <span className="text-slate-300 text-sm">Final Style Coherence</span>
        <div className="flex items-center gap-2">
          <div className="w-24 h-2 bg-slate-600 rounded-full overflow-hidden">
            <div
              className={`h-full ${
                crystal.final_loss < 0.1
                  ? 'bg-green-400'
                  : crystal.final_loss < 0.3
                  ? 'bg-amber-400'
                  : 'bg-red-400'
              }`}
              style={{ width: `${(1 - crystal.final_loss) * 100}%` }}
            />
          </div>
          <span className="text-slate-300 text-sm font-mono">
            {pct(1 - crystal.final_loss)}
          </span>
        </div>
      </div>

      {/* Acceptance rate insight */}
      <div className="mt-4 text-center text-slate-500 text-xs">
        {acceptanceRate > 0.5 ? (
          <span>
            ✨ Convergent journey: {pct(acceptanceRate)} of explorations enriched
            the canon
          </span>
        ) : acceptanceRate > 0.2 ? (
          <span>
            🌿 Explorative journey: many paths tried, fewer chosen
          </span>
        ) : (
          <span>
            🌀 Wild journey: most paths diverged, finding canon was hard-won
          </span>
        )}
      </div>
    </div>
  );
}

export default StyleCrystalView;
