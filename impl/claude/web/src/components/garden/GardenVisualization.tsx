/**
 * GardenVisualization: Main garden display component.
 *
 * Visualizes the Gardener-Logos state:
 * - Season indicator with plasticity and entropy
 * - Plot grid with progress and activity
 * - Gesture history for recent tending operations
 * - Health metrics and entropy budget
 *
 * @see plans/gardener-logos-enactment.md Phase 7
 */

import { useState } from 'react';
import type { GardenJSON, PlotJSON, TendingVerb, TransitionSuggestionJSON } from '@/reactive/types';
import { SeasonIndicator, SeasonBadge } from './SeasonIndicator';
import { PlotCard, PlotListItem } from './PlotCard';
import { GestureHistory, GestureList } from './GestureHistory';
import { TransitionSuggestionBanner } from './TransitionSuggestionBanner';

interface GardenVisualizationProps {
  garden: GardenJSON;
  onTend?: (verb: TendingVerb, target: string, reasoning?: string) => void;
  onPlotSelect?: (plotName: string) => void;
  className?: string;
  // Phase 8: Auto-Inducer
  transitionSuggestion?: TransitionSuggestionJSON | null;
  onAcceptTransition?: () => void;
  onDismissTransition?: () => void;
  isTransitionLoading?: boolean;
}

export function GardenVisualization({
  garden,
  onTend,
  onPlotSelect,
  className = '',
  // Phase 8: Auto-Inducer
  transitionSuggestion,
  onAcceptTransition,
  onDismissTransition,
  isTransitionLoading = false,
}: GardenVisualizationProps) {
  const [selectedPlot, setSelectedPlot] = useState<string | null>(garden.active_plot);

  const handlePlotSelect = (plotName: string) => {
    setSelectedPlot(plotName === selectedPlot ? null : plotName);
    onPlotSelect?.(plotName);
  };

  const plots = Object.values(garden.plots);
  const selectedPlotData = selectedPlot ? garden.plots[selectedPlot] : null;

  return (
    <div className={`flex flex-col h-full ${className}`}>
      {/* Header */}
      <GardenHeader garden={garden} />

      {/* Phase 8: Transition Suggestion Banner */}
      {transitionSuggestion && onAcceptTransition && onDismissTransition && (
        <div className="flex-shrink-0 px-4 pt-4">
          <TransitionSuggestionBanner
            suggestion={transitionSuggestion}
            onAccept={onAcceptTransition}
            onDismiss={onDismissTransition}
            isLoading={isTransitionLoading}
          />
        </div>
      )}

      {/* Main Content */}
      <div className="flex-1 overflow-hidden flex">
        {/* Left: Season + Plots */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {/* Season Indicator */}
          <SeasonIndicator
            season={garden.season}
            plasticity={garden.computed.season_plasticity}
            entropyMultiplier={garden.computed.season_entropy_multiplier}
            seasonSince={garden.season_since}
          />

          {/* Health Metrics */}
          <HealthMetrics garden={garden} />

          {/* Plot Grid */}
          <div>
            <h3 className="text-sm font-semibold text-gray-400 mb-3">
              Plots ({garden.computed.active_plot_count}/{garden.computed.total_plot_count} active)
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {plots.map((plot) => (
                <PlotCard
                  key={plot.name}
                  plot={plot}
                  isActive={plot.name === garden.active_plot}
                  gardenSeason={garden.season}
                  onSelect={handlePlotSelect}
                />
              ))}
            </div>
          </div>
        </div>

        {/* Right: Details Panel */}
        <div className="w-80 border-l border-gray-700 overflow-y-auto">
          {selectedPlotData ? (
            <PlotDetails
              plot={selectedPlotData}
              gardenSeason={garden.season}
              onTend={onTend}
              onClose={() => setSelectedPlot(null)}
            />
          ) : (
            <div className="p-4">
              <h3 className="text-sm font-semibold text-gray-400 mb-3">Recent Gestures</h3>
              <GestureHistory gestures={garden.recent_gestures} maxDisplay={10} />

              {/* Quick Tending Actions */}
              {onTend && (
                <div className="mt-4">
                  <h4 className="text-xs font-semibold text-gray-500 mb-2">Quick Actions</h4>
                  <QuickTendActions onTend={onTend} target="concept.gardener" />
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

// =============================================================================
// Sub-components
// =============================================================================

function GardenHeader({ garden }: { garden: GardenJSON }) {
  return (
    <div className="flex-shrink-0 bg-gray-800/50 border-b border-gray-700 px-4 py-3">
      <div className="flex items-center justify-between">
        {/* Left: Garden info */}
        <div className="flex items-center gap-3">
          <span className="text-2xl">🌱</span>
          <div>
            <h1 className="font-semibold text-lg">{garden.name}</h1>
            <div className="flex items-center gap-2 text-xs text-gray-400">
              <span>ID: {garden.garden_id.slice(0, 8)}</span>
              <span>·</span>
              <span>Last tended: {formatRelativeTime(garden.last_tended)}</span>
            </div>
          </div>
        </div>

        {/* Right: Season badge + health */}
        <div className="flex items-center gap-4">
          <div className="text-right">
            <div className="text-sm text-gray-400">Health</div>
            <div className={`text-lg font-semibold ${getHealthColor(garden.computed.health_score)}`}>
              {(garden.computed.health_score * 100).toFixed(0)}%
            </div>
          </div>
          <SeasonBadge season={garden.season} />
        </div>
      </div>
    </div>
  );
}

function HealthMetrics({ garden }: { garden: GardenJSON }) {
  const { computed, metrics } = garden;

  return (
    <div className="grid grid-cols-3 gap-3">
      {/* Health Score */}
      <MetricCard
        label="Health"
        value={`${(computed.health_score * 100).toFixed(0)}%`}
        color={getHealthColor(computed.health_score)}
      />

      {/* Entropy Budget */}
      <MetricCard
        label="Entropy"
        value={`${computed.entropy_remaining.toFixed(2)} / ${metrics.entropy_budget.toFixed(1)}`}
        subValue={`${(computed.entropy_percentage * 100).toFixed(0)}% remaining`}
        color={computed.entropy_percentage > 0.3 ? 'text-green-400' : 'text-amber-400'}
      />

      {/* Active Plots */}
      <MetricCard
        label="Active Plots"
        value={`${computed.active_plot_count}/${computed.total_plot_count}`}
        color="text-blue-400"
      />
    </div>
  );
}

function MetricCard({
  label,
  value,
  subValue,
  color = 'text-white',
}: {
  label: string;
  value: string;
  subValue?: string;
  color?: string;
}) {
  return (
    <div className="bg-gray-800/50 rounded-lg p-3">
      <div className="text-xs text-gray-500 mb-1">{label}</div>
      <div className={`text-lg font-semibold ${color}`}>{value}</div>
      {subValue && <div className="text-[10px] text-gray-500">{subValue}</div>}
    </div>
  );
}

function PlotDetails({
  plot,
  gardenSeason: _gardenSeason,
  onTend,
  onClose,
}: {
  plot: PlotJSON;
  gardenSeason: GardenJSON['season'];
  onTend?: GardenVisualizationProps['onTend'];
  onClose: () => void;
}) {
  return (
    <div className="p-4">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold">{formatPlotName(plot.name)}</h3>
        <button onClick={onClose} className="text-gray-500 hover:text-white text-lg">
          ×
        </button>
      </div>

      {/* Plot info */}
      <div className="space-y-3">
        <p className="text-sm text-gray-400">{plot.description}</p>

        {/* AGENTESE path */}
        <div>
          <span className="text-xs text-gray-500">Path: </span>
          <code className="text-xs text-green-400 bg-gray-800 px-1.5 py-0.5 rounded">
            {plot.path}
          </code>
        </div>

        {/* Progress */}
        <div>
          <div className="flex justify-between text-xs mb-1">
            <span className="text-gray-500">Progress</span>
            <span className="text-gray-400">{(plot.progress * 100).toFixed(0)}%</span>
          </div>
          <div className="h-2 bg-gray-700 rounded-full overflow-hidden">
            <div
              className="h-full bg-green-500 transition-all"
              style={{ width: `${plot.progress * 100}%` }}
            />
          </div>
        </div>

        {/* Season override */}
        {plot.season_override && (
          <div className="flex items-center gap-2">
            <span className="text-xs text-gray-500">Season override:</span>
            <SeasonBadge season={plot.season_override} className="text-[10px]" />
          </div>
        )}

        {/* Plan link */}
        {plot.plan_path && (
          <div className="text-xs">
            <span className="text-gray-500">Plan: </span>
            <span className="text-blue-400">{plot.plan_path}</span>
          </div>
        )}

        {/* Tending actions */}
        {onTend && (
          <div className="pt-3 border-t border-gray-700">
            <h4 className="text-xs font-semibold text-gray-500 mb-2">Tend this plot</h4>
            <QuickTendActions onTend={onTend} target={plot.path} />
          </div>
        )}
      </div>
    </div>
  );
}

function QuickTendActions({
  onTend,
  target,
}: {
  onTend: GardenVisualizationProps['onTend'];
  target: string;
}) {
  const actions: { verb: TendingVerb; emoji: string; label: string }[] = [
    { verb: 'OBSERVE', emoji: '👁️', label: 'Observe' },
    { verb: 'WATER', emoji: '💧', label: 'Water' },
    { verb: 'GRAFT', emoji: '🌿', label: 'Graft' },
    { verb: 'PRUNE', emoji: '✂️', label: 'Prune' },
    { verb: 'ROTATE', emoji: '🔄', label: 'Rotate' },
    { verb: 'WAIT', emoji: '⏳', label: 'Wait' },
  ];

  return (
    <div className="grid grid-cols-3 gap-2">
      {actions.map(({ verb, emoji, label }) => (
        <button
          key={verb}
          onClick={() => onTend?.(verb, target)}
          className="flex flex-col items-center gap-1 p-2 rounded bg-gray-800 hover:bg-gray-700 transition-colors"
        >
          <span className="text-lg">{emoji}</span>
          <span className="text-[10px] text-gray-400">{label}</span>
        </button>
      ))}
    </div>
  );
}

// =============================================================================
// Compact Garden Display (for embedding)
// =============================================================================

export function GardenCompact({
  garden,
  onPlotSelect,
  className = '',
}: {
  garden: GardenJSON;
  onPlotSelect?: (plotName: string) => void;
  className?: string;
}) {
  const plots = Object.values(garden.plots);

  return (
    <div className={`bg-gray-900 rounded-lg p-4 ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <span className="text-lg">🌱</span>
          <span className="font-medium">{garden.name}</span>
        </div>
        <SeasonBadge season={garden.season} className="text-[10px]" />
      </div>

      {/* Metrics row */}
      <div className="flex items-center gap-4 mb-3 text-xs">
        <span className={getHealthColor(garden.computed.health_score)}>
          Health: {(garden.computed.health_score * 100).toFixed(0)}%
        </span>
        <span className="text-gray-500">|</span>
        <span className="text-gray-400">
          Plots: {garden.computed.active_plot_count}/{garden.computed.total_plot_count}
        </span>
      </div>

      {/* Plot list */}
      <div className="space-y-1">
        {plots.slice(0, 5).map((plot) => (
          <PlotListItem
            key={plot.name}
            plot={plot}
            isActive={plot.name === garden.active_plot}
            onSelect={onPlotSelect}
          />
        ))}
        {plots.length > 5 && (
          <p className="text-xs text-gray-500 text-center py-1">+{plots.length - 5} more plots</p>
        )}
      </div>

      {/* Recent gestures */}
      <div className="mt-3 pt-3 border-t border-gray-800">
        <h4 className="text-xs text-gray-500 mb-2">Recent gestures</h4>
        <GestureList gestures={garden.recent_gestures} maxDisplay={3} />
      </div>
    </div>
  );
}

// =============================================================================
// Helpers
// =============================================================================

function formatRelativeTime(isoDate: string): string {
  const date = new Date(isoDate);
  const now = new Date();
  const diff = now.getTime() - date.getTime();
  const minutes = Math.floor(diff / (1000 * 60));
  const hours = Math.floor(minutes / 60);
  const days = Math.floor(hours / 24);

  if (days > 0) return `${days}d ago`;
  if (hours > 0) return `${hours}h ago`;
  if (minutes > 0) return `${minutes}m ago`;
  return 'just now';
}

function formatPlotName(name: string): string {
  return name
    .split('-')
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
}

function getHealthColor(score: number): string {
  if (score >= 0.7) return 'text-green-400';
  if (score >= 0.4) return 'text-yellow-400';
  return 'text-red-400';
}

export default GardenVisualization;
