import { useWorkshopStore } from '@/stores/workshopStore';
import { BUILDER_COLORS, BUILDER_ICONS } from '@/api/types';
import type { BuilderArchetype } from '@/api/types';
import { cn } from '@/lib/utils';

/**
 * CompletionSummary - Shows summary when a task completes.
 *
 * Displays:
 * - Task that was completed
 * - Metrics (duration, steps, handoffs)
 * - Artifacts produced
 * - Builder contributions
 */

interface CompletionSummaryProps {
  onNewTask: () => void;
  onResetAll: () => void;
  className?: string;
}

export function CompletionSummary({ onNewTask, onResetAll, className }: CompletionSummaryProps) {
  const { activeTask, metrics, artifacts, events, builders } = useWorkshopStore();

  // Calculate builder contributions from events
  const builderContributions = builders.map((builder) => {
    const builderEvents = events.filter((e) => e.builder === builder.archetype);
    return {
      archetype: builder.archetype,
      eventCount: builderEvents.length,
      artifactCount: artifacts.filter((a) => a.builder === builder.archetype).length,
    };
  });

  return (
    <div className={cn('bg-emerald-900/20 border border-emerald-500/30 rounded-lg p-4', className)}>
      {/* Header */}
      <div className="flex items-center gap-3 mb-4">
        <span className="text-3xl">🎉</span>
        <div>
          <h2 className="font-semibold text-lg text-emerald-400">Task Complete!</h2>
          {activeTask && <p className="text-gray-400 text-sm">{activeTask.description}</p>}
        </div>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-4 gap-3 mb-4">
        <MetricBox label="Duration" value={formatDuration(metrics.duration_seconds)} />
        <MetricBox label="Steps" value={metrics.total_steps.toString()} />
        <MetricBox label="Handoffs" value={metrics.handoffs.toString()} />
        <MetricBox label="Artifacts" value={metrics.artifacts_produced.toString()} />
      </div>

      {/* Builder Contributions */}
      <div className="mb-4">
        <h3 className="text-sm font-medium text-gray-400 mb-2">Builder Contributions</h3>
        <div className="flex gap-2 flex-wrap">
          {builderContributions.map((contrib) => (
            <div
              key={contrib.archetype}
              className="flex items-center gap-1.5 bg-town-surface/50 rounded px-2 py-1 text-xs"
            >
              <span>{BUILDER_ICONS[contrib.archetype as BuilderArchetype]}</span>
              <span style={{ color: BUILDER_COLORS[contrib.archetype as BuilderArchetype] }}>
                {contrib.archetype}
              </span>
              <span className="text-gray-500">
                {contrib.eventCount}e / {contrib.artifactCount}a
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Artifacts Summary */}
      {artifacts.length > 0 && (
        <div className="mb-4">
          <h3 className="text-sm font-medium text-gray-400 mb-2">
            Artifacts Produced ({artifacts.length})
          </h3>
          <div className="space-y-1 max-h-32 overflow-y-auto">
            {artifacts.map((artifact, idx) => (
              <div
                key={artifact.id}
                className="flex items-center gap-2 text-xs bg-town-surface/30 rounded px-2 py-1"
              >
                <span>{BUILDER_ICONS[artifact.builder as BuilderArchetype]}</span>
                <span style={{ color: BUILDER_COLORS[artifact.builder as BuilderArchetype] }}>
                  {artifact.builder}
                </span>
                <span className="text-gray-500">•</span>
                <span className={getPhaseColor(artifact.phase)}>{artifact.phase}</span>
                <span className="text-gray-500 ml-auto">#{idx + 1}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Actions */}
      <div className="flex gap-3">
        <button
          onClick={onNewTask}
          className="flex-1 px-4 py-2 bg-town-highlight hover:bg-town-highlight/80 rounded-lg font-medium transition-colors"
        >
          New Task
        </button>
        <button
          onClick={onResetAll}
          className="px-4 py-2 bg-town-surface/50 hover:bg-town-surface text-gray-300 rounded-lg font-medium transition-colors"
        >
          Reset All
        </button>
      </div>
    </div>
  );
}

interface MetricBoxProps {
  label: string;
  value: string;
}

function MetricBox({ label, value }: MetricBoxProps) {
  return (
    <div className="bg-town-surface/30 rounded p-2 text-center">
      <div className="text-lg font-semibold text-white">{value}</div>
      <div className="text-xs text-gray-500">{label}</div>
    </div>
  );
}

function formatDuration(seconds: number): string {
  if (seconds < 60) return `${Math.round(seconds)}s`;
  const mins = Math.floor(seconds / 60);
  const secs = Math.round(seconds % 60);
  return `${mins}m ${secs}s`;
}

function getPhaseColor(phase: string): string {
  switch (phase) {
    case 'EXPLORING':
      return 'text-green-400';
    case 'DESIGNING':
      return 'text-purple-400';
    case 'PROTOTYPING':
      return 'text-amber-400';
    case 'REFINING':
      return 'text-blue-400';
    case 'INTEGRATING':
      return 'text-pink-400';
    default:
      return 'text-gray-400';
  }
}

export default CompletionSummary;
