/**
 * ParkVisualization - Main visualization component for Punchdrunk Park.
 *
 * Extracted from ParkScenario.tsx for projection-first architecture.
 * This component handles all business logic and visualization while
 * the page component delegates to PathProjection.
 *
 * Phase 3 Enhancement: Integrates categorical polynomial visualizations
 * for crisis phases, timers, consent debt, and masks. Adds trace panel
 * for N-gent witness pattern and mobile optimization.
 *
 * @see spec/protocols/os-shell.md - Part III: Projection-First Rendering
 * @see docs/creative/visual-system.md - NO EMOJIS policy
 * @see plans/park-town-design-overhaul.md - Phase 3: Park Enhancement
 */

import { useState, useEffect, useCallback } from 'react';
import { Trophy, AlertTriangle, Flag, Lightbulb } from 'lucide-react';
import { parkApi } from '../../api/client';
import type {
  ParkScenarioState,
  ParkMaskInfo,
  ParkScenarioSummary,
  ParkCrisisPhase,
  ParkStatusResponse,
} from '../../api/types';
// Phase 3: Use enhanced components instead of legacy ones
import { TimerMachineGrid } from './TimerMachine';
import { PhaseVisualization } from './PhaseVisualization';
import { PhaseIndicator } from './PhaseTransition';
import { MaskGridEnhanced } from './MaskCardEnhanced';
import { CurrentMaskBadge } from './MaskSelector';
import { ConsentDebtMachine } from './ConsentDebtMachine';
import { ParkTracePanel } from './ParkTracePanel';
import { DirectorOperadExplorer } from './DirectorOperadExplorer';
import { InlineError, Shake, PopOnMount, celebrate } from '../joy';
import { useSynergyToast } from '../synergy';
import { useTeachingModeSafe } from '../../hooks';
import { JEWEL_ICONS, JEWEL_COLORS } from '../../constants/jewels';
import { BottomDrawer } from '../elastic';
import type { Density } from '../../shell/types';

// =============================================================================
// Types
// =============================================================================

type ViewState = 'idle' | 'running' | 'summary';
type Template = 'data-breach' | 'service-outage' | 'custom';
type TimerType = 'gdpr' | 'sec' | 'hipaa' | 'sla';

export interface ParkVisualizationProps {
  /** Initial data from PathProjection (park status) */
  data: ParkStatusResponse;
  /** Current layout density */
  density: Density;
  /** Refetch callback from PathProjection */
  refetch?: () => void;
}

// =============================================================================
// Sub-components (extracted for clarity)
// =============================================================================

interface StartScreenProps {
  masks: ParkMaskInfo[];
  onStart: (template: Template, timerType: TimerType, accelerated: boolean) => void;
  loading: boolean;
}

function StartScreen({ masks, onStart, loading }: StartScreenProps) {
  const [selectedTemplate, setSelectedTemplate] = useState<Template>('data-breach');
  const [selectedTimer, setSelectedTimer] = useState<TimerType>('sla');
  const [accelerated, setAccelerated] = useState(true);

  const ParkIcon = JEWEL_ICONS.park;

  return (
    <div className="grid md:grid-cols-2 gap-8">
      {/* Start Config */}
      <div className="bg-gray-800/50 rounded-xl p-6">
        <h2 className="text-lg font-semibold mb-4">Start Scenario</h2>

        {/* Template Selection */}
        <div className="mb-4">
          <label className="block text-sm text-gray-400 mb-2">Template</label>
          <div className="grid grid-cols-3 gap-2">
            {(['data-breach', 'service-outage', 'custom'] as Template[]).map((t) => (
              <button
                key={t}
                onClick={() => setSelectedTemplate(t)}
                className={`
                  px-3 py-2 text-sm rounded transition-colors
                  ${
                    selectedTemplate === t
                      ? 'bg-amber-600 text-white'
                      : 'bg-gray-700 hover:bg-gray-600 text-gray-300'
                  }
                `}
              >
                {t.replace('-', ' ').replace(/\b\w/g, (c) => c.toUpperCase())}
              </button>
            ))}
          </div>
        </div>

        {/* Timer Selection (for custom) */}
        {selectedTemplate === 'custom' && (
          <div className="mb-4">
            <label className="block text-sm text-gray-400 mb-2">Timer Type</label>
            <div className="grid grid-cols-4 gap-2">
              {(['gdpr', 'sec', 'hipaa', 'sla'] as TimerType[]).map((t) => (
                <button
                  key={t}
                  onClick={() => setSelectedTimer(t)}
                  className={`
                    px-3 py-2 text-xs rounded transition-colors uppercase
                    ${
                      selectedTimer === t
                        ? 'bg-blue-600 text-white'
                        : 'bg-gray-700 hover:bg-gray-600 text-gray-300'
                    }
                  `}
                >
                  {t}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Accelerated toggle */}
        <div className="mb-6">
          <label className="flex items-center gap-3 cursor-pointer">
            <input
              type="checkbox"
              checked={accelerated}
              onChange={(e) => setAccelerated(e.target.checked)}
              className="w-4 h-4 rounded border-gray-600"
            />
            <span className="text-sm">Accelerated Mode (60x speed)</span>
          </label>
        </div>

        {/* Start button */}
        <button
          onClick={() => onStart(selectedTemplate, selectedTimer, accelerated)}
          disabled={loading}
          className="w-full py-3 bg-green-600 hover:bg-green-700 disabled:bg-gray-700 disabled:text-gray-500 text-white font-medium rounded-lg transition-colors"
        >
          {loading ? 'Starting...' : 'Start Crisis Practice'}
        </button>
      </div>

      {/* Mask Preview */}
      <div className="bg-gray-800/50 rounded-xl p-6">
        <h2 className="text-lg font-semibold mb-4">Available Masks</h2>
        <div className="space-y-3 max-h-96 overflow-y-auto">
          {masks.map((mask) => (
            <div key={mask.name} className="flex items-center gap-3 p-3 bg-gray-700/50 rounded-lg">
              <ParkIcon className="w-6 h-6" style={{ color: JEWEL_COLORS.park.primary }} />
              <div>
                <p className="text-sm font-medium">{mask.name}</p>
                <p className="text-xs text-gray-400">{mask.description}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

interface SummaryScreenProps {
  summary: ParkScenarioSummary;
  onReset: () => void;
}

// =============================================================================
// Running Scenario Component (Phase 3 Enhanced)
// =============================================================================

interface RunningScenarioProps {
  scenario: ParkScenarioState;
  masks: ParkMaskInfo[];
  autoTick: boolean;
  setAutoTick: (v: boolean) => void;
  onTick: (count?: number) => void;
  onTransition: (phase: ParkCrisisPhase) => void;
  onDonMask: (name: string) => void;
  onDoffMask: () => void;
  onUseForce: () => void;
  onComplete: (outcome: 'success' | 'failure' | 'abandon') => void;
  isMobile: boolean;
  /** Whether teaching mode is enabled (Phase 4) */
  teachingEnabled: boolean;
  /** Toggle teaching mode */
  onToggleTeaching: () => void;
}

function RunningScenario({
  scenario,
  masks,
  autoTick,
  setAutoTick,
  onTick,
  onTransition,
  onDonMask,
  onDoffMask,
  onUseForce,
  onComplete,
  isMobile,
  teachingEnabled,
  onToggleTeaching,
}: RunningScenarioProps) {
  // Mobile drawer states
  const [masksDrawerOpen, setMasksDrawerOpen] = useState(false);
  const [traceDrawerOpen, setTraceDrawerOpen] = useState(false);
  const [showOperadExplorer, setShowOperadExplorer] = useState(false);

  // Desktop layout
  if (!isMobile) {
    return (
      <>
      <div className="grid lg:grid-cols-3 gap-6">
        {/* Left Column - State Machines */}
        <div className="space-y-6">
          {/* Scenario Info */}
          <div className="bg-gray-800/50 rounded-xl p-4">
            <h2 className="text-lg font-semibold mb-2">{scenario.name}</h2>
            <p className="text-xs text-gray-400 mb-4">{scenario.scenario_type}</p>

            {/* Auto-tick toggle */}
            <label className="flex items-center gap-2 text-sm cursor-pointer">
              <input
                type="checkbox"
                checked={autoTick}
                onChange={(e) => setAutoTick(e.target.checked)}
                className="w-4 h-4 rounded border-gray-600"
              />
              <span className="text-gray-400">Auto-advance timers</span>
            </label>

            {/* Manual tick */}
            <div className="flex gap-2 mt-3">
              <button
                onClick={() => onTick(1)}
                className="flex-1 py-2 text-xs bg-gray-700 hover:bg-gray-600 rounded"
              >
                +1 tick
              </button>
              <button
                onClick={() => onTick(10)}
                className="flex-1 py-2 text-xs bg-gray-700 hover:bg-gray-600 rounded"
              >
                +10 ticks
              </button>
            </div>
          </div>

          {/* Timers with State Machine (Phase 3) */}
          <div className="bg-gray-800/50 rounded-xl p-4">
            <h3 className="text-sm font-medium text-gray-300 mb-3">Timer Machines</h3>
            <TimerMachineGrid
              timers={scenario.timers}
              accelerated={scenario.accelerated}
              showStateMachine
              compact
            />
          </div>

          {/* Consent Debt Machine (Phase 3) */}
          <ConsentDebtMachine
            consentDebt={scenario.consent_debt}
            forcesUsed={scenario.forces_used}
            forcesRemaining={scenario.forces_remaining}
            onForce={onUseForce}
            forceDisabled={scenario.forces_remaining === 0}
            showStateMachine
            showTeaching={teachingEnabled}
          />

          {/* Learn Director Operad Button */}
          <button
            onClick={() => setShowOperadExplorer(true)}
            className="w-full py-2 text-sm bg-slate-700 hover:bg-slate-600 rounded-lg flex items-center justify-center gap-2 transition-colors"
          >
            <Lightbulb className="w-4 h-4" />
            Learn Director Operad
          </button>
        </div>

        {/* Center Column - Phase & Actions */}
        <div className="space-y-6">
          {/* Phase Visualization (Phase 3) */}
          <div className="bg-gray-800/50 rounded-xl p-4">
            <PhaseVisualization
              currentPhase={scenario.crisis_phase}
              availableTransitions={scenario.available_transitions}
              phaseTransitions={scenario.phase_transitions}
              consentDebt={scenario.consent_debt}
              onTransition={onTransition}
              showTeaching={teachingEnabled}
            />
          </div>

          {/* Current Mask */}
          <div className="bg-gray-800/50 rounded-xl p-4">
            <h3 className="text-sm font-medium text-gray-300 mb-3">Current Mask</h3>
            <CurrentMaskBadge
              mask={scenario.mask}
              onDoff={scenario.mask ? onDoffMask : undefined}
            />
          </div>

          {/* Trace Panel (Phase 3 - N-gent Witness) */}
          <div className="bg-gray-800/50 rounded-xl p-4">
            <ParkTracePanel
              phaseTransitions={scenario.phase_transitions}
              timers={scenario.timers}
              currentMask={scenario.mask}
              forcesUsed={scenario.forces_used}
              maxEvents={8}
              showTeaching={teachingEnabled}
            />
          </div>

          {/* Complete Controls */}
          <div className="bg-gray-800/50 rounded-xl p-4">
            <h3 className="text-sm font-medium text-gray-300 mb-3">Complete Scenario</h3>
            <div className="grid grid-cols-3 gap-2">
              <button
                onClick={() => onComplete('success')}
                className="py-2 text-xs bg-green-700 hover:bg-green-600 rounded"
              >
                Success
              </button>
              <button
                onClick={() => onComplete('failure')}
                className="py-2 text-xs bg-red-700 hover:bg-red-600 rounded"
              >
                Failure
              </button>
              <button
                onClick={() => onComplete('abandon')}
                className="py-2 text-xs bg-gray-600 hover:bg-gray-500 rounded"
              >
                Abandon
              </button>
            </div>
          </div>
        </div>

        {/* Right Column - Masks (Phase 3 Enhanced) */}
        <div className="bg-gray-800/50 rounded-xl p-4 max-h-[calc(100vh-12rem)] overflow-y-auto">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-sm font-medium text-gray-300">Dialogue Masks</h3>
            {/* Teaching toggle (Phase 4) */}
            <button
              onClick={onToggleTeaching}
              className={`p-1.5 rounded transition-colors ${
                teachingEnabled
                  ? 'bg-blue-500/30 text-blue-400'
                  : 'bg-gray-700/50 text-gray-500 hover:text-gray-300'
              }`}
              title={`Teaching: ${teachingEnabled ? 'ON' : 'OFF'}`}
            >
              <Lightbulb className="w-4 h-4" />
            </button>
          </div>
          <MaskGridEnhanced
            masks={masks}
            currentMask={scenario.mask}
            onDon={onDonMask}
            onDoff={onDoffMask}
            showAffordances
            showTeaching={teachingEnabled}
            compact
          />
        </div>
      </div>

      {/* Director Operad Explorer Modal */}
      {showOperadExplorer && (
        <DirectorOperadExplorer
          variant="modal"
          currentPhase={scenario.crisis_phase as any}
          showTeaching={teachingEnabled}
          onClose={() => setShowOperadExplorer(false)}
        />
      )}
      </>
    );
  }

  // Mobile layout with BottomDrawers
  return (
    <div className="space-y-4">
      {/* Header with phase and consent */}
      <div className="bg-gray-800/50 rounded-xl p-3">
        <div className="flex items-center justify-between mb-3">
          <div>
            <h2 className="text-sm font-semibold">{scenario.name}</h2>
            <p className="text-xs text-gray-500">{scenario.scenario_type}</p>
          </div>
          <PhaseIndicator currentPhase={scenario.crisis_phase} />
        </div>

        {/* Compact consent debt */}
        <ConsentDebtMachine
          consentDebt={scenario.consent_debt}
          forcesUsed={scenario.forces_used}
          forcesRemaining={scenario.forces_remaining}
          onForce={onUseForce}
          forceDisabled={scenario.forces_remaining === 0}
          showStateMachine={false}
          showTeaching={false}
          compact
        />
      </div>

      {/* Timers - compact */}
      <div className="bg-gray-800/50 rounded-xl p-3">
        <TimerMachineGrid
          timers={scenario.timers}
          accelerated={scenario.accelerated}
          showStateMachine={false}
          compact
        />
      </div>

      {/* Phase Visualization - compact */}
      <div className="bg-gray-800/50 rounded-xl p-3">
        <PhaseVisualization
          currentPhase={scenario.crisis_phase}
          availableTransitions={scenario.available_transitions}
          phaseTransitions={scenario.phase_transitions}
          consentDebt={scenario.consent_debt}
          onTransition={onTransition}
          compact
          showTeaching={false}
        />
      </div>

      {/* Current Mask */}
      <div className="bg-gray-800/50 rounded-xl p-3">
        <CurrentMaskBadge mask={scenario.mask} onDoff={scenario.mask ? onDoffMask : undefined} />
      </div>

      {/* Mobile action buttons */}
      <div className="fixed bottom-4 left-4 right-4 flex gap-2 z-40">
        <button
          onClick={() => setMasksDrawerOpen(true)}
          className="flex-1 py-3 bg-amber-600 hover:bg-amber-700 text-white text-sm font-medium rounded-lg"
        >
          Masks
        </button>
        <button
          onClick={() => setTraceDrawerOpen(true)}
          className="flex-1 py-3 bg-gray-700 hover:bg-gray-600 text-white text-sm font-medium rounded-lg"
        >
          Trace
        </button>
        <button
          onClick={() => onComplete('success')}
          className="flex-1 py-3 bg-green-700 hover:bg-green-600 text-white text-sm font-medium rounded-lg"
        >
          Done
        </button>
      </div>

      {/* Masks BottomDrawer */}
      <BottomDrawer
        isOpen={masksDrawerOpen}
        onClose={() => setMasksDrawerOpen(false)}
        title="Dialogue Masks"
        maxHeightPercent={80}
      >
        <div className="p-4">
          <MaskGridEnhanced
            masks={masks}
            currentMask={scenario.mask}
            onDon={onDonMask}
            onDoff={onDoffMask}
            showAffordances
            compact
          />
        </div>
      </BottomDrawer>

      {/* Trace BottomDrawer */}
      <BottomDrawer
        isOpen={traceDrawerOpen}
        onClose={() => setTraceDrawerOpen(false)}
        title="Scenario Trace"
        maxHeightPercent={70}
      >
        <div className="p-4">
          <ParkTracePanel
            phaseTransitions={scenario.phase_transitions}
            timers={scenario.timers}
            currentMask={scenario.mask}
            forcesUsed={scenario.forces_used}
            maxEvents={15}
            showTeaching={teachingEnabled}
          />
        </div>
      </BottomDrawer>

      {/* Director Operad Explorer Modal - also available on mobile */}
      {showOperadExplorer && (
        <DirectorOperadExplorer
          variant="modal"
          currentPhase={scenario.crisis_phase as any}
          showTeaching={teachingEnabled}
          onClose={() => setShowOperadExplorer(false)}
        />
      )}
    </div>
  );
}

function SummaryScreen({ summary, onReset }: SummaryScreenProps) {
  // Get outcome icon
  const OutcomeIcon =
    summary.outcome === 'success' ? Trophy : summary.outcome === 'failure' ? AlertTriangle : Flag;

  const outcomeColor =
    summary.outcome === 'success'
      ? JEWEL_COLORS.gardener.primary
      : summary.outcome === 'failure'
        ? JEWEL_COLORS.domain.primary
        : JEWEL_COLORS.coalition.primary;

  return (
    <PopOnMount scale={1.1} duration={300}>
      <div className="max-w-2xl mx-auto">
        <div className="bg-gray-800/50 rounded-xl p-8">
          {/* Header */}
          <div className="text-center mb-6">
            <OutcomeIcon className="w-16 h-16 mx-auto mb-4" style={{ color: outcomeColor }} />
            <h2 className="text-2xl font-bold mb-2">
              Scenario {summary.outcome.charAt(0).toUpperCase() + summary.outcome.slice(1)}
            </h2>
            <p className="text-gray-400">{summary.name}</p>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-3 gap-4 mb-6">
            <div className="text-center p-4 bg-gray-700/50 rounded-lg">
              <p className="text-2xl font-bold">{Math.round(summary.duration_seconds)}s</p>
              <p className="text-xs text-gray-400">Duration</p>
            </div>
            <div className="text-center p-4 bg-gray-700/50 rounded-lg">
              <p className="text-2xl font-bold">{Math.round(summary.consent_debt_final * 100)}%</p>
              <p className="text-xs text-gray-400">Final Debt</p>
            </div>
            <div className="text-center p-4 bg-gray-700/50 rounded-lg">
              <p className="text-2xl font-bold">{summary.forces_used}/3</p>
              <p className="text-xs text-gray-400">Forces Used</p>
            </div>
          </div>

          {/* Timer Outcomes */}
          <div className="mb-6">
            <h3 className="text-sm font-medium text-gray-300 mb-3">Timer Outcomes</h3>
            <div className="space-y-2">
              {Object.entries(summary.timer_outcomes).map(([name, data]) => (
                <div
                  key={name}
                  className={`flex items-center justify-between p-3 rounded ${
                    data.expired ? 'bg-red-900/20' : 'bg-green-900/20'
                  }`}
                >
                  <span className="text-sm">{name}</span>
                  <span className={`text-xs ${data.expired ? 'text-red-400' : 'text-green-400'}`}>
                    {data.expired ? 'EXPIRED' : data.status}
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* Phase Transitions */}
          {summary.phase_transitions.length > 0 && (
            <div className="mb-6">
              <h3 className="text-sm font-medium text-gray-300 mb-3">
                Phase Transitions ({summary.phase_transitions.length})
              </h3>
              <div className="space-y-1 text-xs text-gray-400">
                {summary.phase_transitions.map((t, i) => (
                  <p key={i}>
                    {t.from} → {t.to} (debt: {Math.round(t.consent_debt * 100)}%)
                  </p>
                ))}
              </div>
            </div>
          )}

          {/* Restart */}
          <button
            onClick={onReset}
            className="w-full py-3 bg-jewel-park hover:bg-jewel-park-accent text-white font-medium rounded-lg transition-colors"
          >
            Start New Scenario
          </button>
        </div>
      </div>
    </PopOnMount>
  );
}

// =============================================================================
// Main Component
// =============================================================================

export function ParkVisualization({ data, density, refetch: _refetch }: ParkVisualizationProps) {
  // Determine initial state from data
  const initialViewState: ViewState = data.running ? 'running' : 'idle';

  // Mobile detection for bottom drawer usage
  const isMobile = density === 'compact';

  // State
  const [viewState, setViewState] = useState<ViewState>(initialViewState);
  const [scenario, setScenario] = useState<ParkScenarioState | null>(
    data.running ? (data as unknown as ParkScenarioState) : null
  );
  const [masks, setMasks] = useState<ParkMaskInfo[]>([]);
  const [summary, setSummary] = useState<ParkScenarioSummary | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [tickInterval, setTickInterval] = useState<ReturnType<typeof setInterval> | null>(null);
  const [autoTick, setAutoTick] = useState(true);

  // Teaching mode (Phase 4)
  const { enabled: teachingEnabled, toggle: toggleTeaching } = useTeachingModeSafe();

  // Synergy toasts
  const { scenarioComplete: showScenarioCompleteToast } = useSynergyToast();

  // Load masks on mount
  useEffect(() => {
    const loadMasks = async () => {
      try {
        const masksRes = await parkApi.getMasks();
        setMasks(masksRes);

        // If running, load full scenario
        if (data.running) {
          const scenarioRes = await parkApi.getScenario();
          setScenario(scenarioRes);
          setViewState('running');
        }
      } catch (err) {
        console.error('Failed to load masks:', err);
        setError('Failed to load masks');
      }
    };
    loadMasks();

    return () => {
      if (tickInterval) clearInterval(tickInterval);
    };
  }, []);

  // Auto-tick when running
  useEffect(() => {
    if (viewState === 'running' && autoTick && scenario?.is_active) {
      const interval = setInterval(async () => {
        try {
          const res = await parkApi.tick({ count: 1 });
          setScenario(res);
        } catch (err) {
          console.error('Tick failed:', err);
        }
      }, 1000);
      setTickInterval(interval);
      return () => clearInterval(interval);
    }
  }, [viewState, autoTick, scenario?.is_active]);

  // Actions
  const startScenario = useCallback(
    async (template: Template, timerType: TimerType, accelerated: boolean) => {
      try {
        setLoading(true);
        setError(null);
        const res = await parkApi.startScenario({
          template: template !== 'custom' ? template : undefined,
          timer_type: template === 'custom' ? timerType : undefined,
          accelerated,
        });
        setScenario(res);
        setViewState('running');
      } catch (err) {
        console.error('Failed to start scenario:', err);
        setError('Failed to start scenario');
      } finally {
        setLoading(false);
      }
    },
    []
  );

  const tickScenario = useCallback(
    async (count: number = 1) => {
      if (!scenario) return;
      try {
        const res = await parkApi.tick({ count });
        setScenario(res);
      } catch (err) {
        console.error('Tick failed:', err);
      }
    },
    [scenario]
  );

  const transitionPhase = useCallback(
    async (phase: ParkCrisisPhase) => {
      if (!scenario) return;
      try {
        const res = await parkApi.transitionPhase({
          phase: phase.toLowerCase() as 'normal' | 'incident' | 'response' | 'recovery',
        });
        setScenario(res);
      } catch (err) {
        console.error('Transition failed:', err);
        setError('Invalid phase transition');
      }
    },
    [scenario]
  );

  const donMask = useCallback(
    async (maskName: string) => {
      if (!scenario) return;
      try {
        const res = await parkApi.maskAction({ action: 'don', mask_name: maskName });
        setScenario(res);
      } catch (err) {
        console.error('Don mask failed:', err);
        setError('Cannot don mask');
      }
    },
    [scenario]
  );

  const doffMask = useCallback(async () => {
    if (!scenario) return;
    try {
      const res = await parkApi.maskAction({ action: 'doff' });
      setScenario(res);
    } catch (err) {
      console.error('Doff mask failed:', err);
    }
  }, [scenario]);

  const useForce = useCallback(async () => {
    if (!scenario) return;
    try {
      const res = await parkApi.useForce();
      setScenario(res);
    } catch (err) {
      console.error('Force failed:', err);
      setError('Cannot use force - limit reached');
    }
  }, [scenario]);

  const completeScenario = useCallback(
    async (outcome: 'success' | 'failure' | 'abandon') => {
      if (!scenario) return;
      try {
        setLoading(true);
        if (tickInterval) {
          clearInterval(tickInterval);
          setTickInterval(null);
        }
        const res = await parkApi.completeScenario({ outcome });
        setSummary(res);
        setScenario(null);
        setViewState('summary');

        if (outcome === 'success') {
          celebrate({ intensity: 'epic' });
        }
        showScenarioCompleteToast(res.name, res.forces_used);
      } catch (err) {
        console.error('Complete failed:', err);
        setError('Failed to complete scenario');
      } finally {
        setLoading(false);
      }
    },
    [scenario, tickInterval, showScenarioCompleteToast]
  );

  const resetToIdle = useCallback(() => {
    setSummary(null);
    setViewState('idle');
    setError(null);
  }, []);

  // Get icons
  const ParkIcon = JEWEL_ICONS.park;

  return (
    <div className="min-h-screen bg-gray-900 text-gray-100 p-6">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <header className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold flex items-center gap-3">
                <ParkIcon className="w-8 h-8" style={{ color: JEWEL_COLORS.park.primary }} />
                Punchdrunk Park
              </h1>
              <p className="text-gray-400 text-sm mt-1">Crisis practice with dialogue masks</p>
            </div>
            {viewState === 'running' && scenario && (
              <PhaseIndicator currentPhase={scenario.crisis_phase} />
            )}
          </div>
        </header>

        {/* Error banner */}
        {error && (
          <Shake trigger={!!error} intensity="normal">
            <div className="mb-6 p-4 bg-red-900/30 border border-red-800 rounded-lg flex items-center justify-between">
              <InlineError message={error} />
              <button onClick={() => setError(null)} className="text-red-400 hover:text-white ml-4">
                ×
              </button>
            </div>
          </Shake>
        )}

        {/* Idle State - Start Screen */}
        {viewState === 'idle' && (
          <StartScreen masks={masks} onStart={startScenario} loading={loading} />
        )}

        {/* Running State - Phase 3 Enhanced */}
        {viewState === 'running' && scenario && (
          <RunningScenario
            scenario={scenario}
            masks={masks}
            autoTick={autoTick}
            setAutoTick={setAutoTick}
            onTick={tickScenario}
            onTransition={transitionPhase}
            onDonMask={donMask}
            onDoffMask={doffMask}
            onUseForce={useForce}
            onComplete={completeScenario}
            isMobile={isMobile}
            teachingEnabled={teachingEnabled}
            onToggleTeaching={toggleTeaching}
          />
        )}

        {/* Summary State */}
        {viewState === 'summary' && summary && (
          <SummaryScreen summary={summary} onReset={resetToIdle} />
        )}
      </div>
    </div>
  );
}

export default ParkVisualization;
