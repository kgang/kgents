/**
 * Gardener Page - The Meta-Jewel for Development Sessions
 *
 * Visualizes and manages GardenerSession polynomial state machines.
 *
 * Wave 1: Hero Path Polish
 * Foundation 3: Visible Polynomial State
 *
 * Key Features:
 * - Polynomial state machine visualization (SENSE → ACT → REFLECT)
 * - Session management (create, resume, view)
 * - Context integration with Brain + Gestalt
 * - Observer-dependent session views
 *
 * @see plans/core-apps/the-gardener.md
 * @see plans/crown-jewels-enlightened.md
 */

import { useState, useCallback, useMemo } from 'react';
import type {
  PolynomialVisualization,
  GardenerSessionState,
} from '../api/types';
import { useWindowLayout } from '../hooks/useLayoutContext';
import { PolynomialDiagram } from '../components/polynomial';
import { useObserverState, ObserverSwitcher, DEFAULT_OBSERVERS, PathTrace } from '../components/path';
import { Breathe, celebrate } from '../components/joy';
import { JEWEL_COLORS } from '../constants';

// =============================================================================
// Mock Data (until API is ready)
// =============================================================================

/**
 * Create a mock session for demonstration.
 * This will be replaced with actual API data in Wave 2.
 */
function createMockSession(phase: 'SENSE' | 'ACT' | 'REFLECT'): GardenerSessionState {
  return {
    session_id: 'mock-session-001',
    name: 'Wave 1 Hero Path Implementation',
    phase,
    plan_path: 'plans/crown-jewels-enlightened.md',
    intent: {
      description: 'Implement the Hero Path jewels with full foundation support',
      priority: 'high',
    },
    artifacts_count: phase === 'SENSE' ? 0 : phase === 'ACT' ? 3 : 5,
    learnings_count: phase === 'REFLECT' ? 2 : 0,
    sense_count: 1,
    act_count: phase === 'SENSE' ? 0 : 1,
    reflect_count: phase === 'REFLECT' ? 1 : 0,
  };
}

/**
 * Create polynomial visualization from session state.
 */
function createSessionVisualization(session: GardenerSessionState): PolynomialVisualization {
  const positionLabels: Record<string, { label: string; emoji: string; description: string }> = {
    SENSE: { label: 'Sense', emoji: '👁️', description: 'Gather context from forest, codebase, memory' },
    ACT: { label: 'Act', emoji: '⚡', description: 'Execute intent: write code, create docs' },
    REFLECT: { label: 'Reflect', emoji: '💭', description: 'Consolidate learnings, update meta.md' },
  };

  return {
    id: session.session_id,
    name: session.name,
    positions: ['SENSE', 'ACT', 'REFLECT'].map((id) => ({
      id,
      label: positionLabels[id].label,
      description: positionLabels[id].description,
      emoji: positionLabels[id].emoji,
      is_current: session.phase === id,
      is_terminal: false, // Gardener phases are cyclic, never terminal
      color: session.phase === id ? JEWEL_COLORS.gardener.primary : undefined,
    })),
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
      // Mock history
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
// Session Panel
// =============================================================================

interface SessionPanelProps {
  session: GardenerSessionState;
  onPhaseChange: (phase: 'SENSE' | 'ACT' | 'REFLECT') => void;
  density: 'compact' | 'comfortable' | 'spacious';
}

function SessionPanel({ session, onPhaseChange, density }: SessionPanelProps) {
  const isCompact = density === 'compact';

  const phaseConfig = {
    SENSE: { emoji: '👁️', label: 'Sensing', color: 'text-cyan-400 bg-cyan-900/30' },
    ACT: { emoji: '⚡', label: 'Acting', color: 'text-yellow-400 bg-yellow-900/30' },
    REFLECT: { emoji: '💭', label: 'Reflecting', color: 'text-purple-400 bg-purple-900/30' },
  };

  const currentPhaseConfig = phaseConfig[session.phase];

  return (
    <div className={`bg-gray-800/50 rounded-lg ${isCompact ? 'p-3' : 'p-4'} space-y-4`}>
      {/* Current Phase */}
      <div>
        <h3 className={`font-semibold text-gray-400 uppercase tracking-wide ${isCompact ? 'text-[10px]' : 'text-xs'} mb-2`}>
          Current Phase
        </h3>
        <Breathe intensity={0.3} speed="slow">
          <div className={`inline-flex items-center gap-2 px-3 py-2 rounded-lg ${currentPhaseConfig.color}`}>
            <span className="text-xl">{currentPhaseConfig.emoji}</span>
            <span className={`font-semibold ${isCompact ? 'text-sm' : ''}`}>{currentPhaseConfig.label}</span>
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
    </div>
  );
}

// =============================================================================
// Main Component
// =============================================================================

export default function Gardener() {
  const { density, isMobile, isDesktop } = useWindowLayout();

  // Mock session state (until API is ready)
  const [sessionPhase, setSessionPhase] = useState<'SENSE' | 'ACT' | 'REFLECT'>('SENSE');
  const session = useMemo(() => createMockSession(sessionPhase), [sessionPhase]);

  // Observer state
  const [observer, setObserver] = useObserverState('gardener', 'strategic');

  // Polynomial visualization
  const visualization = useMemo(() => createSessionVisualization(session), [session]);

  // Handle phase transitions
  const handlePhaseChange = useCallback((phase: 'SENSE' | 'ACT' | 'REFLECT') => {
    setSessionPhase(phase);

    // Foundation 5: Celebrate cycle completion
    if (phase === 'SENSE' && sessionPhase === 'REFLECT') {
      celebrate({ intensity: 'normal' });
    }
  }, [sessionPhase]);

  // Handle diagram transitions
  const handleDiagramTransition = useCallback((positionId: string) => {
    const phase = positionId as 'SENSE' | 'ACT' | 'REFLECT';
    if (visualization.valid_directions.includes(positionId)) {
      handlePhaseChange(phase);
    }
  }, [visualization.valid_directions, handlePhaseChange]);

  return (
    <div className="h-screen flex flex-col bg-gray-900 text-white overflow-hidden">
      {/* Header */}
      <header className="flex-shrink-0 border-b border-gray-800 px-4 py-3 bg-gray-900">
        <div className="flex justify-between items-center">
          <div>
            <h1 className={`font-bold flex items-center gap-2 ${isMobile ? 'text-lg' : 'text-xl'}`}>
              <span>🌱</span>
              <span>The Gardener</span>
              <Breathe intensity={0.3} speed="slow">
                <span className="text-lime-400">●</span>
              </Breathe>
            </h1>
            <p className={`text-gray-400 mt-0.5 ${isMobile ? 'text-xs' : 'text-sm'}`}>
              {session.name}
            </p>
          </div>

          {/* Observer switcher (desktop only) */}
          {isDesktop && (
            <ObserverSwitcher
              current={observer}
              available={DEFAULT_OBSERVERS.gardener}
              onChange={setObserver}
              variant="pills"
              size="sm"
            />
          )}
        </div>
      </header>

      {/* Main Content */}
      <div className="flex-1 overflow-y-auto p-4">
        <div className={`mx-auto ${isDesktop ? 'max-w-4xl' : ''}`}>
          {/* Path Trace - Shows AGENTESE path */}
          <PathTrace
            path={`concept.gardener.session[${session.session_id}].manifest`}
            observer={observer}
            aspect="manifest"
            effects={['PHASE_DISPLAYED', 'STATE_VISIBLE']}
            className="mb-4"
          />

          {/* Polynomial Diagram - Foundation 3: Visible Polynomial State */}
          <div className="bg-gray-800/50 rounded-lg p-4 mb-4">
            <h2 className={`font-semibold text-gray-400 uppercase tracking-wide mb-4 ${isMobile ? 'text-[10px]' : 'text-xs'}`}>
              Session State Machine
            </h2>
            <div className="flex justify-center">
              <PolynomialDiagram
                visualization={visualization}
                layout={isMobile ? 'linear-vertical' : 'linear'}
                onTransition={handleDiagramTransition}
                showHistory
                compact={isMobile}
                showEdgeLabels={!isMobile}
              />
            </div>
            <p className="text-center text-gray-500 text-xs mt-3">
              Click on a valid state to transition
            </p>
          </div>

          {/* Session Panel */}
          <SessionPanel
            session={session}
            onPhaseChange={handlePhaseChange}
            density={density}
          />

          {/* AGENTESE Hint */}
          <div className="mt-4 p-3 bg-gray-800/30 rounded-lg border border-gray-700 text-xs text-gray-500">
            <span className="text-gray-400 font-medium">CLI Equivalent:</span>
            <code className="ml-2 text-lime-400 font-mono">
              kg grow session --manifest
            </code>
          </div>
        </div>
      </div>
    </div>
  );
}
