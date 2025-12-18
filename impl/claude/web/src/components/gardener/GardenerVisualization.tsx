/**
 * GardenerVisualization - Session State Machine Visualization
 *
 * Renders the Gardener session state machine with:
 * - Polynomial diagram (SENSE → ACT → REFLECT cycle)
 * - Session panel (intent, stats, actions)
 * - Observer-dependent views
 *
 * This is a Gallery-sourced visualization for the Gardener Crown Jewel.
 *
 * @see spec/protocols/os-shell.md - Gallery Primitive Reliance
 * @see docs/creative/visual-system.md - No Emoji Policy
 */

import { useCallback, useMemo } from 'react';
import { Eye, Zap, MessageSquare } from 'lucide-react';
import type { Density } from '@/shell/types';
import type {
  GardenerSessionState,
  GardenerPhase,
  PolynomialVisualization,
} from '@/api/types';
import { PolynomialDiagram } from '@/components/polynomial';
import { Breathe, celebrate } from '@/components/joy';
import { JEWEL_COLORS } from '@/constants';

// =============================================================================
// Types
// =============================================================================

export interface GardenerVisualizationProps {
  /** Session state data from API */
  session: GardenerSessionState;
  /** Layout density */
  density: Density;
  /** Callback when phase changes */
  onPhaseChange?: (phase: GardenerPhase) => void;
}

// =============================================================================
// Phase Config (Icon-based, no emojis)
// =============================================================================

const PHASE_CONFIG: Record<GardenerPhase, {
  Icon: typeof Eye;
  label: string;
  description: string;
  color: string;
  bgClass: string;
}> = {
  SENSE: {
    Icon: Eye,
    label: 'Sensing',
    description: 'Gather context from forest, codebase, memory',
    color: 'text-cyan-400',
    bgClass: 'bg-cyan-900/30',
  },
  ACT: {
    Icon: Zap,
    label: 'Acting',
    description: 'Execute intent: write code, create docs',
    color: 'text-yellow-400',
    bgClass: 'bg-yellow-900/30',
  },
  REFLECT: {
    Icon: MessageSquare,
    label: 'Reflecting',
    description: 'Consolidate learnings, update meta.md',
    color: 'text-purple-400',
    bgClass: 'bg-purple-900/30',
  },
};

// =============================================================================
// Helpers
// =============================================================================

/**
 * Create polynomial visualization from session state.
 */
function createVisualization(session: GardenerSessionState): PolynomialVisualization {
  return {
    id: session.session_id,
    name: session.name,
    positions: (['SENSE', 'ACT', 'REFLECT'] as GardenerPhase[]).map((id) => {
      const config = PHASE_CONFIG[id];
      return {
        id,
        label: config.label,
        description: config.description,
        is_current: session.phase === id,
        is_terminal: false, // Gardener phases are cyclic
        color: session.phase === id ? JEWEL_COLORS.gardener.primary : undefined,
      };
    }),
    edges: [
      { source: 'SENSE', target: 'ACT', label: 'advance', is_valid: session.phase === 'SENSE' },
      { source: 'ACT', target: 'REFLECT', label: 'advance', is_valid: session.phase === 'ACT' },
      { source: 'REFLECT', target: 'SENSE', label: 'cycle', is_valid: session.phase === 'REFLECT' },
      { source: 'ACT', target: 'SENSE', label: 'rollback', is_valid: session.phase === 'ACT' },
    ],
    current: session.phase,
    valid_directions: session.phase === 'SENSE' ? ['ACT'] :
                      session.phase === 'ACT' ? ['REFLECT', 'SENSE'] :
                      ['SENSE'],
    history: [
      ...(session.sense_count > 0 ? [{ from_position: 'INIT', to_position: 'SENSE', timestamp: new Date().toISOString() }] : []),
      ...(session.act_count > 0 ? [{ from_position: 'SENSE', to_position: 'ACT', timestamp: new Date().toISOString() }] : []),
      ...(session.reflect_count > 0 ? [{ from_position: 'ACT', to_position: 'REFLECT', timestamp: new Date().toISOString() }] : []),
    ],
    metadata: {
      phase_times: {
        SENSE: session.sense_count,
        ACT: session.act_count,
        REFLECT: session.reflect_count,
      },
    },
  };
}

// =============================================================================
// Session Panel Component
// =============================================================================

interface SessionPanelProps {
  session: GardenerSessionState;
  onPhaseChange?: (phase: GardenerPhase) => void;
  density: Density;
}

function SessionPanel({ session, onPhaseChange, density }: SessionPanelProps) {
  const isCompact = density === 'compact';
  const config = PHASE_CONFIG[session.phase];
  const { Icon } = config;

  return (
    <div className={`bg-gray-800/50 rounded-lg ${isCompact ? 'p-3' : 'p-4'} space-y-4`}>
      {/* Current Phase */}
      <div>
        <h3 className={`font-semibold text-gray-400 uppercase tracking-wide ${isCompact ? 'text-[10px]' : 'text-xs'} mb-2`}>
          Current Phase
        </h3>
        <Breathe intensity={0.3} speed="slow">
          <div className={`inline-flex items-center gap-2 px-3 py-2 rounded-lg ${config.bgClass}`}>
            <Icon className={`${isCompact ? 'w-4 h-4' : 'w-5 h-5'} ${config.color}`} />
            <span className={`font-semibold ${config.color} ${isCompact ? 'text-sm' : ''}`}>
              {config.label}
            </span>
          </div>
        </Breathe>
      </div>

      {/* Intent */}
      {session.intent && (
        <div>
          <h3 className={`font-semibold text-gray-400 uppercase tracking-wide ${isCompact ? 'text-[10px]' : 'text-xs'} mb-2`}>
            Intent
          </h3>
          <p className={`text-gray-300 ${isCompact ? 'text-xs' : 'text-sm'}`}>
            {session.intent.description}
          </p>
          <span className={`inline-block mt-1 px-2 py-0.5 bg-gray-700 rounded text-gray-400 ${isCompact ? 'text-[10px]' : 'text-xs'}`}>
            Priority: {session.intent.priority}
          </span>
        </div>
      )}

      {/* Plan Path */}
      {session.plan_path && (
        <div>
          <h3 className={`font-semibold text-gray-400 uppercase tracking-wide ${isCompact ? 'text-[10px]' : 'text-xs'} mb-1`}>
            Plan
          </h3>
          <p className={`text-lime-400 font-mono ${isCompact ? 'text-[10px]' : 'text-xs'} truncate`}>
            {session.plan_path}
          </p>
        </div>
      )}

      {/* Stats */}
      <div>
        <h3 className={`font-semibold text-gray-400 uppercase tracking-wide ${isCompact ? 'text-[10px]' : 'text-xs'} mb-2`}>
          Stats
        </h3>
        <div className={`grid ${isCompact ? 'grid-cols-4 gap-2' : 'grid-cols-2 gap-3'}`}>
          {[
            { label: 'Artifacts', value: session.artifacts_count, color: 'text-lime-400' },
            { label: 'Learnings', value: session.learnings_count, color: 'text-purple-400' },
            { label: 'Cycles', value: session.reflect_count, color: 'text-cyan-400' },
            { label: 'Sense', value: session.sense_count, color: 'text-gray-400' },
          ].map((stat) => (
            <div key={stat.label} className="text-center">
              <div className={`font-bold ${stat.color} ${isCompact ? 'text-lg' : 'text-2xl'}`}>
                {stat.value}
              </div>
              <div className={`text-gray-500 ${isCompact ? 'text-[10px]' : 'text-xs'}`}>
                {stat.label}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Actions */}
      {onPhaseChange && (
        <div className="pt-3 border-t border-gray-700">
          <h3 className={`font-semibold text-gray-400 uppercase tracking-wide ${isCompact ? 'text-[10px]' : 'text-xs'} mb-2`}>
            Actions
          </h3>
          <div className="flex flex-wrap gap-2">
            <button
              onClick={() => onPhaseChange('ACT')}
              disabled={session.phase !== 'SENSE'}
              className={`px-3 py-1.5 rounded font-medium transition-colors ${isCompact ? 'text-xs' : 'text-sm'} ${
                session.phase === 'SENSE'
                  ? 'bg-lime-600 hover:bg-lime-700 text-white'
                  : 'bg-gray-700 text-gray-500 cursor-not-allowed'
              }`}
            >
              Advance to Act
            </button>
            <button
              onClick={() => onPhaseChange('REFLECT')}
              disabled={session.phase !== 'ACT'}
              className={`px-3 py-1.5 rounded font-medium transition-colors ${isCompact ? 'text-xs' : 'text-sm'} ${
                session.phase === 'ACT'
                  ? 'bg-lime-600 hover:bg-lime-700 text-white'
                  : 'bg-gray-700 text-gray-500 cursor-not-allowed'
              }`}
            >
              Advance to Reflect
            </button>
            <button
              onClick={() => onPhaseChange('SENSE')}
              disabled={session.phase !== 'REFLECT'}
              className={`px-3 py-1.5 rounded font-medium transition-colors ${isCompact ? 'text-xs' : 'text-sm'} ${
                session.phase === 'REFLECT'
                  ? 'bg-purple-600 hover:bg-purple-700 text-white'
                  : 'bg-gray-700 text-gray-500 cursor-not-allowed'
              }`}
            >
              Start New Cycle
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

// =============================================================================
// Main Component
// =============================================================================

/**
 * GardenerVisualization - The main visualization component for Gardener sessions.
 *
 * This is designed to be used with PathProjection for projection-first pages.
 */
export function GardenerVisualization({
  session,
  density,
  onPhaseChange,
}: GardenerVisualizationProps) {
  const isMobile = density === 'compact';
  const isDesktop = density === 'spacious';

  // Create polynomial visualization
  const visualization = useMemo(() => createVisualization(session), [session]);

  // Handle phase transitions with celebration
  const handlePhaseChange = useCallback((phase: GardenerPhase) => {
    // Celebrate cycle completion
    if (phase === 'SENSE' && session.phase === 'REFLECT') {
      celebrate({ intensity: 'normal' });
    }
    onPhaseChange?.(phase);
  }, [session.phase, onPhaseChange]);

  // Handle diagram transitions
  const handleDiagramTransition = useCallback((positionId: string) => {
    const phase = positionId as GardenerPhase;
    if (visualization.valid_directions.includes(positionId)) {
      handlePhaseChange(phase);
    }
  }, [visualization.valid_directions, handlePhaseChange]);

  return (
    <div className={`space-y-4 ${isDesktop ? 'max-w-4xl mx-auto' : ''}`}>
      {/* Polynomial Diagram */}
      <div className="bg-gray-800/50 rounded-lg p-4">
        <h2 className={`font-semibold text-gray-400 uppercase tracking-wide mb-4 ${isMobile ? 'text-[10px]' : 'text-xs'}`}>
          Session State Machine
        </h2>
        <div className="flex justify-center">
          <PolynomialDiagram
            visualization={visualization}
            layout={isMobile ? 'linear-vertical' : 'linear'}
            onTransition={onPhaseChange ? handleDiagramTransition : undefined}
            showHistory
            compact={isMobile}
            showEdgeLabels={!isMobile}
          />
        </div>
        {onPhaseChange && (
          <p className="text-center text-gray-500 text-xs mt-3">
            Click on a valid state to transition
          </p>
        )}
      </div>

      {/* Session Panel */}
      <SessionPanel
        session={session}
        onPhaseChange={onPhaseChange}
        density={density}
      />

      {/* CLI Hint */}
      <div className="p-3 bg-gray-800/30 rounded-lg border border-gray-700 text-xs text-gray-500">
        <span className="text-gray-400 font-medium">CLI Equivalent:</span>
        <code className="ml-2 text-lime-400 font-mono">
          kg grow session --manifest
        </code>
      </div>
    </div>
  );
}

export default GardenerVisualization;
