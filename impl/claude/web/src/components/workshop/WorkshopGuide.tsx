import { useState } from 'react';
import { BUILDER_COLORS, BUILDER_ICONS } from '@/api/types';
import type { BuilderArchetype, WorkshopPhase } from '@/api/types';
import { cn } from '@/lib/utils';

/**
 * WorkshopGuide - Explains what's happening in the workshop demo.
 *
 * Shows a collapsible guide explaining:
 * - The 5 builders and their specialties
 * - The 5 phases of work
 * - The flow of handoffs
 */

interface WorkshopGuideProps {
  currentPhase: WorkshopPhase;
  activeBuilder: string | null;
  className?: string;
}

export function WorkshopGuide({ currentPhase, activeBuilder, className }: WorkshopGuideProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  return (
    <div className={cn('bg-town-surface/30 border-b border-town-accent/30', className)}>
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full px-4 py-2 flex items-center justify-between text-sm hover:bg-town-surface/50 transition-colors"
      >
        <span className="flex items-center gap-2">
          <span>📖</span>
          <span className="text-gray-400">What's happening?</span>
          {activeBuilder && (
            <span className="text-xs">
              <span className="text-gray-500">•</span>
              <span
                className="ml-2"
                style={{ color: BUILDER_COLORS[activeBuilder as BuilderArchetype] }}
              >
                {BUILDER_ICONS[activeBuilder as BuilderArchetype]} {activeBuilder}
              </span>
              <span className="text-gray-500 ml-2">is</span>
              <span className={cn('ml-1', getPhaseTextColor(currentPhase))}>
                {getPhaseVerb(currentPhase)}
              </span>
            </span>
          )}
        </span>
        <span className="text-gray-500">{isExpanded ? '▼' : '▶'}</span>
      </button>

      {isExpanded && (
        <div className="px-4 pb-4 space-y-4 text-sm">
          {/* Current Status */}
          <div className="bg-town-bg/50 rounded-lg p-3">
            <h3 className="font-semibold text-white mb-2">Current Status</h3>
            <p className="text-gray-400">
              {getPhaseDescription(currentPhase, activeBuilder)}
            </p>
          </div>

          {/* The Flow */}
          <div>
            <h3 className="font-semibold text-white mb-2">The Development Flow</h3>
            <div className="flex flex-wrap items-center gap-2 text-xs">
              {PHASE_FLOW.map((phase, i) => (
                <div key={phase.phase} className="flex items-center gap-1">
                  <span
                    className={cn(
                      'px-2 py-1 rounded',
                      currentPhase === phase.phase
                        ? 'bg-town-highlight/30 ring-1 ring-town-highlight'
                        : 'bg-town-surface/50'
                    )}
                  >
                    <span>{phase.icon}</span>
                    <span
                      className="ml-1"
                      style={{ color: BUILDER_COLORS[phase.builder as BuilderArchetype] }}
                    >
                      {phase.builder}
                    </span>
                  </span>
                  {i < PHASE_FLOW.length - 1 && <span className="text-gray-500">→</span>}
                </div>
              ))}
            </div>
          </div>

          {/* The Builders */}
          <div>
            <h3 className="font-semibold text-white mb-2">The Builders</h3>
            <div className="grid grid-cols-1 gap-2 text-xs">
              {BUILDERS.map((builder) => (
                <div
                  key={builder.archetype}
                  className={cn(
                    'flex items-start gap-2 p-2 rounded',
                    activeBuilder === builder.archetype
                      ? 'bg-town-highlight/20 ring-1 ring-town-highlight/50'
                      : 'bg-town-surface/30'
                  )}
                >
                  <span className="text-lg">{builder.icon}</span>
                  <div>
                    <span style={{ color: builder.color }} className="font-medium">
                      {builder.archetype}
                    </span>
                    <span className="text-gray-500"> — {builder.role}</span>
                    <p className="text-gray-400 mt-0.5">{builder.description}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

const PHASE_FLOW = [
  { phase: 'EXPLORING', builder: 'Scout', icon: '🔍' },
  { phase: 'DESIGNING', builder: 'Sage', icon: '📐' },
  { phase: 'PROTOTYPING', builder: 'Spark', icon: '⚡' },
  { phase: 'REFINING', builder: 'Steady', icon: '🔧' },
  { phase: 'INTEGRATING', builder: 'Sync', icon: '🔗' },
] as const;

const BUILDERS = [
  {
    archetype: 'Scout',
    icon: BUILDER_ICONS.Scout,
    color: BUILDER_COLORS.Scout,
    role: 'The Explorer',
    description: 'Scouts the codebase, finds patterns, gathers context before work begins.',
  },
  {
    archetype: 'Sage',
    icon: BUILDER_ICONS.Sage,
    color: BUILDER_COLORS.Sage,
    role: 'The Architect',
    description: 'Designs the approach, considers trade-offs, creates the blueprint.',
  },
  {
    archetype: 'Spark',
    icon: BUILDER_ICONS.Spark,
    color: BUILDER_COLORS.Spark,
    role: 'The Prototyper',
    description: 'Rapidly builds initial implementations, experiments with ideas.',
  },
  {
    archetype: 'Steady',
    icon: BUILDER_ICONS.Steady,
    color: BUILDER_COLORS.Steady,
    role: 'The Craftsperson',
    description: 'Refines code quality, adds tests, handles edge cases.',
  },
  {
    archetype: 'Sync',
    icon: BUILDER_ICONS.Sync,
    color: BUILDER_COLORS.Sync,
    role: 'The Integrator',
    description: 'Ensures everything works together, handles final polish and deployment.',
  },
];

function getPhaseVerb(phase: WorkshopPhase): string {
  switch (phase) {
    case 'EXPLORING':
      return 'exploring';
    case 'DESIGNING':
      return 'designing';
    case 'PROTOTYPING':
      return 'prototyping';
    case 'REFINING':
      return 'refining';
    case 'INTEGRATING':
      return 'integrating';
    case 'COMPLETE':
      return 'done!';
    default:
      return 'idle';
  }
}

function getPhaseDescription(phase: WorkshopPhase, builder: string | null): string {
  if (phase === 'IDLE') {
    return 'The workshop is idle. Assign a task to start the development flow.';
  }

  if (phase === 'COMPLETE') {
    return 'The task is complete! All builders have contributed. Review the artifacts produced.';
  }

  const descriptions: Record<string, string> = {
    EXPLORING:
      'Scout is exploring the problem space, gathering context, and identifying relevant patterns in the codebase.',
    DESIGNING:
      'Sage is designing the solution architecture, considering trade-offs, and creating a plan for implementation.',
    PROTOTYPING:
      'Spark is rapidly building the initial implementation, experimenting with approaches to bring the design to life.',
    REFINING:
      'Steady is refining the implementation, improving code quality, adding tests, and handling edge cases.',
    INTEGRATING:
      'Sync is integrating all the pieces, ensuring everything works together, and preparing for delivery.',
  };

  return descriptions[phase] || `${builder || 'A builder'} is working on the task.`;
}

function getPhaseTextColor(phase: WorkshopPhase): string {
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
    case 'COMPLETE':
      return 'text-emerald-400';
    default:
      return 'text-gray-400';
  }
}

export default WorkshopGuide;
