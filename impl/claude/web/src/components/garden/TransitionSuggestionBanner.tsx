/**
 * TransitionSuggestionBanner: Auto-Inducer UI component.
 *
 * Displays season transition suggestions from the garden's auto-inducer.
 * Users can accept or dismiss suggestions.
 *
 * @see plans/gardener-logos-enactment.md Phase 8
 */

import { useState } from 'react';
import type { GardenSeason, TransitionSuggestionJSON } from '@/reactive/types';
import { SEASON_COLORS } from '@/constants';

// Season configuration with emojis and colors
const SEASON_CONFIG: Record<GardenSeason, { emoji: string; color: string; label: string }> = {
  DORMANT: { emoji: '💤', color: SEASON_COLORS.dormant, label: 'Dormant' },
  SPROUTING: { emoji: '🌱', color: SEASON_COLORS.sprouting, label: 'Sprouting' },
  BLOOMING: { emoji: '🌸', color: SEASON_COLORS.blooming, label: 'Blooming' },
  HARVEST: { emoji: '🌾', color: SEASON_COLORS.harvest, label: 'Harvest' },
  COMPOSTING: { emoji: '🍂', color: SEASON_COLORS.composting, label: 'Composting' },
};

interface TransitionSuggestionBannerProps {
  suggestion: TransitionSuggestionJSON;
  onAccept: () => void;
  onDismiss: () => void;
  isLoading?: boolean;
}

export function TransitionSuggestionBanner({
  suggestion,
  onAccept,
  onDismiss,
  isLoading = false,
}: TransitionSuggestionBannerProps) {
  const [showDetails, setShowDetails] = useState(false);

  const fromConfig = SEASON_CONFIG[suggestion.from_season];
  const toConfig = SEASON_CONFIG[suggestion.to_season];
  const confidencePercent = (suggestion.confidence * 100).toFixed(0);

  return (
    <div className="bg-gradient-to-r from-amber-900/30 to-amber-800/20 border border-amber-600/50 rounded-lg p-4 shadow-lg animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <span className="text-amber-400 animate-pulse">✨</span>
          <h3 className="font-semibold text-amber-300">Season Transition Suggested</h3>
        </div>
        <div className="flex items-center gap-2 text-sm">
          <span className="text-gray-400">Confidence:</span>
          <span
            className={`font-mono ${
              suggestion.confidence >= 0.8
                ? 'text-green-400'
                : suggestion.confidence >= 0.7
                ? 'text-amber-400'
                : 'text-gray-400'
            }`}
          >
            {confidencePercent}%
          </span>
        </div>
      </div>

      {/* Transition Visual */}
      <div className="flex items-center justify-center gap-4 py-3">
        {/* From Season */}
        <div className="flex flex-col items-center">
          <span className="text-3xl mb-1">{fromConfig.emoji}</span>
          <span className="text-sm text-gray-400">{fromConfig.label}</span>
        </div>

        {/* Arrow */}
        <div className="flex items-center gap-1">
          <div className="w-12 h-0.5 bg-gradient-to-r from-gray-600 to-amber-500" />
          <span className="text-2xl text-amber-400">→</span>
          <div className="w-12 h-0.5 bg-gradient-to-l from-gray-600 to-amber-500" />
        </div>

        {/* To Season */}
        <div className="flex flex-col items-center">
          <span className="text-3xl mb-1">{toConfig.emoji}</span>
          <span className="text-sm" style={{ color: toConfig.color }}>
            {toConfig.label}
          </span>
        </div>
      </div>

      {/* Reason */}
      <p className="text-sm text-gray-300 text-center mb-3">{suggestion.reason}</p>

      {/* Action Buttons */}
      <div className="flex gap-3 justify-center">
        <button
          onClick={onAccept}
          disabled={isLoading}
          className={`
            px-4 py-2 rounded-lg font-medium transition-colors
            ${
              isLoading
                ? 'bg-gray-600 text-gray-400 cursor-not-allowed'
                : 'bg-green-600 hover:bg-green-500 text-white'
            }
          `}
        >
          {isLoading ? 'Transitioning...' : 'Accept Transition'}
        </button>

        <button
          onClick={onDismiss}
          disabled={isLoading}
          className="px-4 py-2 rounded-lg font-medium bg-gray-700 hover:bg-gray-600 text-gray-300 transition-colors"
        >
          Dismiss
        </button>

        <button
          onClick={() => setShowDetails(!showDetails)}
          className="px-3 py-2 rounded-lg text-gray-400 hover:text-white hover:bg-gray-700 transition-colors"
          title="View details"
        >
          {showDetails ? '▲' : '▼'}
        </button>
      </div>

      {/* Details Panel */}
      {showDetails && (
        <div className="mt-4 pt-4 border-t border-gray-700">
          <h4 className="text-xs font-semibold text-gray-500 uppercase mb-2">Transition Signals</h4>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-xs">
            <SignalItem
              label="Gesture Frequency"
              value={`${suggestion.signals.gesture_frequency.toFixed(1)}/hr`}
            />
            <SignalItem
              label="Gesture Diversity"
              value={`${suggestion.signals.gesture_diversity} types`}
            />
            <SignalItem
              label="Time in Season"
              value={`${suggestion.signals.time_in_season_hours.toFixed(1)}h`}
            />
            <SignalItem
              label="Entropy Ratio"
              value={`${(suggestion.signals.entropy_spent_ratio * 100).toFixed(0)}%`}
            />
            <SignalItem
              label="Progress Delta"
              value={`${(suggestion.signals.plot_progress_delta * 100).toFixed(0)}%`}
            />
            <SignalItem
              label="Artifacts Created"
              value={`${suggestion.signals.artifacts_created}`}
            />
            <SignalItem
              label="Reflect Count"
              value={`${suggestion.signals.reflect_count}`}
            />
            <SignalItem
              label="Session Active"
              value={suggestion.signals.session_active ? 'Yes' : 'No'}
            />
          </div>
          <p className="text-xs text-gray-500 mt-2">
            Triggered at: {new Date(suggestion.triggered_at).toLocaleTimeString()}
          </p>
        </div>
      )}
    </div>
  );
}

function SignalItem({ label, value }: { label: string; value: string }) {
  return (
    <div className="bg-gray-800/50 rounded px-2 py-1">
      <div className="text-gray-500">{label}</div>
      <div className="text-gray-300 font-mono">{value}</div>
    </div>
  );
}

/**
 * Compact toast-style version for minimal UI
 */
export function TransitionSuggestionToast({
  suggestion,
  onAccept,
  onDismiss,
}: TransitionSuggestionBannerProps) {
  const fromConfig = SEASON_CONFIG[suggestion.from_season];
  const toConfig = SEASON_CONFIG[suggestion.to_season];

  return (
    <div className="fixed bottom-4 right-4 bg-gray-900 border border-amber-600/50 rounded-lg p-3 shadow-xl max-w-sm animate-slide-up z-50">
      <div className="flex items-center gap-3">
        <div className="flex items-center gap-1">
          <span>{fromConfig.emoji}</span>
          <span className="text-gray-500">→</span>
          <span>{toConfig.emoji}</span>
        </div>
        <div className="flex-1 min-w-0">
          <p className="text-sm text-gray-300 truncate">{suggestion.reason}</p>
        </div>
        <div className="flex gap-1">
          <button
            onClick={onAccept}
            className="p-1.5 rounded bg-green-600 hover:bg-green-500 text-white text-xs"
            title="Accept"
          >
            ✓
          </button>
          <button
            onClick={onDismiss}
            className="p-1.5 rounded bg-gray-700 hover:bg-gray-600 text-gray-300 text-xs"
            title="Dismiss"
          >
            ✕
          </button>
        </div>
      </div>
    </div>
  );
}

export default TransitionSuggestionBanner;
