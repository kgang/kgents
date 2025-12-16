/**
 * ParkScenario: Crisis practice scenario page.
 *
 * Wave 3: Punchdrunk Park web UI.
 *
 * Features:
 * - Scenario start/complete controls
 * - Real-time timer display
 * - Crisis phase state machine
 * - Dialogue mask selection
 * - Consent mechanics
 */

import { useState, useEffect, useCallback } from 'react';
import { parkApi } from '../api/client';
import type {
  ParkScenarioState,
  ParkMaskInfo,
  ParkScenarioSummary,
  ParkCrisisPhase,
} from '../api/types';
import { TimerGrid } from '../components/park/TimerDisplay';
import { PhaseTransition, PhaseIndicator } from '../components/park/PhaseTransition';
import { MaskSelector, CurrentMaskBadge } from '../components/park/MaskSelector';
import { ConsentMeter } from '../components/park/ConsentMeter';
import {
  PersonalityLoading,
  InlineError,
  Shake,
  PopOnMount,
  celebrate,
} from '../components/joy';
import { useSynergyToast } from '../components/synergy';

type ViewState = 'idle' | 'running' | 'summary';
type Template = 'data-breach' | 'service-outage' | 'custom';
type TimerType = 'gdpr' | 'sec' | 'hipaa' | 'sla';

export default function ParkScenario() {
  // State
  const [viewState, setViewState] = useState<ViewState>('idle');
  const [scenario, setScenario] = useState<ParkScenarioState | null>(null);
  const [masks, setMasks] = useState<ParkMaskInfo[]>([]);
  const [summary, setSummary] = useState<ParkScenarioSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [tickInterval, setTickInterval] = useState<ReturnType<typeof setInterval> | null>(null);

  // Start config
  const [selectedTemplate, setSelectedTemplate] = useState<Template>('data-breach');
  const [selectedTimer, setSelectedTimer] = useState<TimerType>('sla');
  const [accelerated, setAccelerated] = useState(true);
  const [autoTick, setAutoTick] = useState(true);

  // Synergy toasts (Wave 4: Cross-jewel notifications)
  const { scenarioComplete: showScenarioCompleteToast } = useSynergyToast();

  // Load initial state
  useEffect(() => {
    const loadState = async () => {
      try {
        setLoading(true);
        const [masksRes, statusRes] = await Promise.all([
          parkApi.getMasks(),
          parkApi.getStatus(),
        ]);

        setMasks(masksRes.data);

        if (statusRes.data.running) {
          const scenarioRes = await parkApi.getScenario();
          setScenario(scenarioRes.data);
          setViewState('running');
        }
      } catch (err) {
        console.error('Failed to load Park state:', err);
        setError('Failed to load Park state');
      } finally {
        setLoading(false);
      }
    };

    loadState();

    return () => {
      if (tickInterval) {
        clearInterval(tickInterval);
      }
    };
  }, []);

  // Auto-tick when running
  useEffect(() => {
    if (viewState === 'running' && autoTick && scenario?.is_active) {
      const interval = setInterval(async () => {
        try {
          const res = await parkApi.tick({ count: 1 });
          setScenario(res.data);
        } catch (err) {
          console.error('Tick failed:', err);
        }
      }, 1000);
      setTickInterval(interval);

      return () => clearInterval(interval);
    }
  }, [viewState, autoTick, scenario?.is_active]);

  // Actions
  const startScenario = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      const res = await parkApi.startScenario({
        template: selectedTemplate !== 'custom' ? selectedTemplate : undefined,
        timer_type: selectedTemplate === 'custom' ? selectedTimer : undefined,
        accelerated,
      });

      setScenario(res.data);
      setViewState('running');
    } catch (err) {
      console.error('Failed to start scenario:', err);
      setError('Failed to start scenario');
    } finally {
      setLoading(false);
    }
  }, [selectedTemplate, selectedTimer, accelerated]);

  const tickScenario = useCallback(async (count: number = 1) => {
    if (!scenario) return;
    try {
      const res = await parkApi.tick({ count });
      setScenario(res.data);
    } catch (err) {
      console.error('Tick failed:', err);
    }
  }, [scenario]);

  const transitionPhase = useCallback(async (phase: ParkCrisisPhase) => {
    if (!scenario) return;
    try {
      const res = await parkApi.transitionPhase({
        phase: phase.toLowerCase() as 'normal' | 'incident' | 'response' | 'recovery',
      });
      setScenario(res.data);
    } catch (err) {
      console.error('Transition failed:', err);
      setError('Invalid phase transition');
    }
  }, [scenario]);

  const donMask = useCallback(async (maskName: string) => {
    if (!scenario) return;
    try {
      const res = await parkApi.maskAction({ action: 'don', mask_name: maskName });
      setScenario(res.data);
    } catch (err) {
      console.error('Don mask failed:', err);
      setError('Cannot don mask');
    }
  }, [scenario]);

  const doffMask = useCallback(async () => {
    if (!scenario) return;
    try {
      const res = await parkApi.maskAction({ action: 'doff' });
      setScenario(res.data);
    } catch (err) {
      console.error('Doff mask failed:', err);
    }
  }, [scenario]);

  const useForce = useCallback(async () => {
    if (!scenario) return;
    try {
      const res = await parkApi.useForce();
      setScenario(res.data);
    } catch (err) {
      console.error('Force failed:', err);
      setError('Cannot use force - limit reached');
    }
  }, [scenario]);

  const completeScenario = useCallback(async (outcome: 'success' | 'failure' | 'abandon') => {
    if (!scenario) return;
    try {
      setLoading(true);
      if (tickInterval) {
        clearInterval(tickInterval);
        setTickInterval(null);
      }
      const res = await parkApi.completeScenario({ outcome });
      setSummary(res.data);
      setScenario(null);
      setViewState('summary');

      // Foundation 5: Celebrate success with epic confetti!
      if (outcome === 'success') {
        celebrate({ intensity: 'epic' });
      }

      // Wave 4: Show synergy toast for scenario completion
      showScenarioCompleteToast(res.data.name, res.data.forces_used);
    } catch (err) {
      console.error('Complete failed:', err);
      setError('Failed to complete scenario');
    } finally {
      setLoading(false);
    }
  }, [scenario, tickInterval, showScenarioCompleteToast]);

  const resetToIdle = useCallback(() => {
    setSummary(null);
    setViewState('idle');
    setError(null);
  }, []);

  // Loading state - Foundation 5: PersonalityLoading for Park
  if (loading && viewState === 'idle' && !scenario) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-900">
        <PersonalityLoading jewel="park" size="lg" action="connect" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-900 text-gray-100 p-6">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <header className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold flex items-center gap-3">
                <span className="text-3xl">🎭</span>
                Punchdrunk Park
              </h1>
              <p className="text-gray-400 text-sm mt-1">
                Crisis practice with dialogue masks
              </p>
            </div>
            {viewState === 'running' && scenario && (
              <PhaseIndicator currentPhase={scenario.crisis_phase} />
            )}
          </div>
        </header>

        {/* Error banner - Foundation 5: Shake + InlineError */}
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
                        ${selectedTemplate === t
                          ? 'bg-amber-600 text-white'
                          : 'bg-gray-700 hover:bg-gray-600 text-gray-300'
                        }
                      `}
                    >
                      {t.replace('-', ' ').replace(/\b\w/g, c => c.toUpperCase())}
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
                          ${selectedTimer === t
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
                onClick={startScenario}
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
                  <div
                    key={mask.name}
                    className="flex items-center gap-3 p-3 bg-gray-700/50 rounded-lg"
                  >
                    <span className="text-2xl">
                      {mask.archetype === 'TRICKSTER' ? '🎭' :
                       mask.archetype === 'SAGE' ? '🦉' :
                       mask.archetype === 'DREAMER' ? '💭' :
                       mask.archetype === 'SKEPTIC' ? '🔍' :
                       mask.archetype === 'ARCHITECT' ? '🏗️' :
                       mask.archetype === 'CHILD' ? '🌟' :
                       mask.archetype === 'WARRIOR' ? '⚔️' :
                       mask.archetype === 'HEALER' ? '💚' : '🎭'}
                    </span>
                    <div>
                      <p className="text-sm font-medium">{mask.name}</p>
                      <p className="text-xs text-gray-400">{mask.description}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Running State */}
        {viewState === 'running' && scenario && (
          <div className="grid lg:grid-cols-3 gap-6">
            {/* Left Column - Timers & Controls */}
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
                    onClick={() => tickScenario(1)}
                    className="flex-1 py-2 text-xs bg-gray-700 hover:bg-gray-600 rounded"
                  >
                    +1 tick
                  </button>
                  <button
                    onClick={() => tickScenario(10)}
                    className="flex-1 py-2 text-xs bg-gray-700 hover:bg-gray-600 rounded"
                  >
                    +10 ticks
                  </button>
                </div>
              </div>

              {/* Timers */}
              <div className="bg-gray-800/50 rounded-xl p-4">
                <h3 className="text-sm font-medium text-gray-300 mb-3">Timers</h3>
                <TimerGrid
                  timers={scenario.timers}
                  accelerated={scenario.accelerated}
                />
              </div>

              {/* Consent Meter */}
              <ConsentMeter
                consentDebt={scenario.consent_debt}
                forcesUsed={scenario.forces_used}
                forcesRemaining={scenario.forces_remaining}
                onForce={useForce}
                forceDisabled={scenario.forces_remaining === 0}
              />
            </div>

            {/* Center Column - Phase & Actions */}
            <div className="space-y-6">
              {/* Phase Transition */}
              <div className="bg-gray-800/50 rounded-xl p-4">
                <h3 className="text-sm font-medium text-gray-300 mb-4">Crisis Phase</h3>
                <PhaseTransition
                  currentPhase={scenario.crisis_phase}
                  availableTransitions={scenario.available_transitions}
                  phaseTransitions={scenario.phase_transitions}
                  onTransition={transitionPhase}
                  compact
                />
              </div>

              {/* Current Mask */}
              <div className="bg-gray-800/50 rounded-xl p-4">
                <h3 className="text-sm font-medium text-gray-300 mb-3">Current Mask</h3>
                <CurrentMaskBadge
                  mask={scenario.mask}
                  onDoff={scenario.mask ? doffMask : undefined}
                />
              </div>

              {/* Complete Controls */}
              <div className="bg-gray-800/50 rounded-xl p-4">
                <h3 className="text-sm font-medium text-gray-300 mb-3">Complete Scenario</h3>
                <div className="grid grid-cols-3 gap-2">
                  <button
                    onClick={() => completeScenario('success')}
                    className="py-2 text-xs bg-green-700 hover:bg-green-600 rounded"
                  >
                    Success
                  </button>
                  <button
                    onClick={() => completeScenario('failure')}
                    className="py-2 text-xs bg-red-700 hover:bg-red-600 rounded"
                  >
                    Failure
                  </button>
                  <button
                    onClick={() => completeScenario('abandon')}
                    className="py-2 text-xs bg-gray-600 hover:bg-gray-500 rounded"
                  >
                    Abandon
                  </button>
                </div>
              </div>
            </div>

            {/* Right Column - Masks */}
            <div className="bg-gray-800/50 rounded-xl p-4">
              <h3 className="text-sm font-medium text-gray-300 mb-3">Dialogue Masks</h3>
              <MaskSelector
                masks={masks}
                currentMask={scenario.mask}
                onDon={donMask}
                onDoff={doffMask}
                compact
              />
            </div>
          </div>
        )}

        {/* Summary State - Foundation 5: Pop animation for dramatic reveal */}
        {viewState === 'summary' && summary && (
          <PopOnMount scale={1.1} duration={300}>
            <div className="max-w-2xl mx-auto">
              <div className="bg-gray-800/50 rounded-xl p-8">
                {/* Header */}
                <div className="text-center mb-6">
                  <span className="text-6xl mb-4 block">
                    {summary.outcome === 'success' ? '🏆' :
                     summary.outcome === 'failure' ? '💥' : '🏳️'}
                  </span>
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
                onClick={resetToIdle}
                className="w-full py-3 bg-jewel-park hover:bg-jewel-park-accent text-white font-medium rounded-lg transition-colors"
              >
                Start New Scenario
              </button>
            </div>
          </div>
          </PopOnMount>
        )}
      </div>
    </div>
  );
}
