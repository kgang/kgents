import { useWorkshopStore, selectPhaseProgress } from '@/stores/workshopStore';
import { BUILDER_COLORS, BUILDER_ICONS } from '@/api/types';
import type { WorkshopPhase, BuilderArchetype } from '@/api/types';

const PHASES: Array<{ phase: WorkshopPhase; archetype: BuilderArchetype }> = [
  { phase: 'EXPLORING', archetype: 'Scout' },
  { phase: 'DESIGNING', archetype: 'Sage' },
  { phase: 'PROTOTYPING', archetype: 'Spark' },
  { phase: 'REFINING', archetype: 'Steady' },
  { phase: 'INTEGRATING', archetype: 'Sync' },
];

/**
 * TaskProgress displays the workshop pipeline progress bar.
 */
export function TaskProgress() {
  const { currentPhase, activeTask, metrics } = useWorkshopStore();
  const progress = useWorkshopStore(selectPhaseProgress());

  const currentPhaseIndex = PHASES.findIndex((p) => p.phase === currentPhase);

  return (
    <div className="bg-town-surface/30 border-b border-town-accent/30 px-4 py-2">
      {/* Task Description */}
      {activeTask && (
        <div className="text-sm text-gray-300 mb-2 flex items-center gap-2">
          <span className="font-medium">Task:</span>
          <span className="truncate">{activeTask.description}</span>
          <span className="text-gray-500">
            (Priority {activeTask.priority})
          </span>
        </div>
      )}

      {/* Pipeline Progress */}
      <div className="flex items-center gap-1">
        {PHASES.map(({ phase, archetype }, index) => {
          const color = BUILDER_COLORS[archetype];
          const icon = BUILDER_ICONS[archetype];
          const isCompleted = index < currentPhaseIndex;
          const isCurrent = index === currentPhaseIndex;
          const isPending = index > currentPhaseIndex;

          return (
            <div
              key={phase}
              className="flex items-center flex-1"
            >
              {/* Phase Node */}
              <div
                className={`flex items-center justify-center w-8 h-8 rounded-full border-2 transition-all ${
                  isCompleted
                    ? 'bg-green-500/20 border-green-500'
                    : isCurrent
                    ? 'border-current animate-pulse'
                    : 'border-gray-600 bg-gray-800/50'
                }`}
                style={{
                  borderColor: isCurrent ? color : undefined,
                  backgroundColor: isCurrent ? `${color}20` : undefined,
                }}
                title={`${archetype}: ${phase}`}
              >
                <span
                  className={`text-xs ${
                    isCompleted || isCurrent ? '' : 'opacity-50'
                  }`}
                >
                  {isCompleted ? '✓' : icon}
                </span>
              </div>

              {/* Connector Line */}
              {index < PHASES.length - 1 && (
                <div
                  className={`flex-1 h-0.5 mx-1 transition-colors ${
                    isCompleted ? 'bg-green-500' : 'bg-gray-700'
                  }`}
                />
              )}
            </div>
          );
        })}

        {/* Complete indicator */}
        <div
          className={`flex items-center justify-center w-8 h-8 rounded-full border-2 transition-all ${
            currentPhase === 'COMPLETE'
              ? 'bg-emerald-500/20 border-emerald-500'
              : 'border-gray-600 bg-gray-800/50'
          }`}
        >
          <span
            className={currentPhase === 'COMPLETE' ? 'text-emerald-400' : 'text-gray-500'}
          >
            🎉
          </span>
        </div>
      </div>

      {/* Metrics Row */}
      <div className="flex items-center gap-4 mt-2 text-xs text-gray-500">
        <span>Steps: {metrics.total_steps}</span>
        <span>•</span>
        <span>Handoffs: {metrics.handoffs}</span>
        <span>•</span>
        <span>Artifacts: {metrics.artifacts_produced}</span>
        {metrics.duration_seconds > 0 && (
          <>
            <span>•</span>
            <span>Duration: {metrics.duration_seconds.toFixed(1)}s</span>
          </>
        )}
      </div>
    </div>
  );
}

export default TaskProgress;
