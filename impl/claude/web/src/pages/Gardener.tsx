/**
 * Gardener Page - 2D Renaissance Implementation
 *
 * The Gardener is the meta-jewel for development sessions, combining:
 * - Garden state (plots, seasons, gestures)
 * - Session state machine (SENSE -> ACT -> REFLECT)
 *
 * This is the Phase 2 implementation of the 2D Renaissance spec.
 * Uses Gardener2D for unified visualization with Living Earth aesthetic.
 *
 * @see spec/protocols/2d-renaissance.md - Phase 2
 * @see docs/creative/visual-system.md - NO EMOJIS policy
 */

import { useState, useCallback, useMemo } from 'react';
import { Gardener2D } from '@/components/gardener';
import type { GardenerPhase } from '@/api/types/_generated/concept-gardener';
import type { GardenerSessionState } from '@/api/types';
import type { GardenJSON, TransitionSuggestionJSON } from '@/reactive/types';

// =============================================================================
// Mock Data (REMOVE when AGENTESE API is ready)
// =============================================================================

const createMockGarden = (): GardenJSON => ({
  type: 'garden',
  garden_id: 'garden-001',
  name: 'Wave 1 Hero Path',
  created_at: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString(),
  season: 'SPROUTING',
  season_since: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
  plots: {
    'hero-path': {
      name: 'hero-path',
      path: 'concept.gardener.plots.hero-path',
      description: 'Wave 1 Hero Path Implementation - Brain, Gardener, Gestalt',
      plan_path: 'plans/crown-jewels-enlightened.md',
      crown_jewel: 'Gardener',
      prompts: ['Implement Gardener2D', 'Add Living Earth palette'],
      season_override: null,
      rigidity: 0.3,
      progress: 0.65,
      created_at: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toISOString(),
      last_tended: new Date(Date.now() - 15 * 60 * 1000).toISOString(),
      tags: ['wave-1', 'hero-path', 'crown-jewels'],
      metadata: {},
    },
    foundation: {
      name: 'foundation',
      path: 'concept.gardener.plots.foundation',
      description: 'Categorical foundation - PolyAgent, Operad, Sheaf',
      plan_path: null,
      crown_jewel: 'Brain',
      prompts: [],
      season_override: null,
      rigidity: 0.7,
      progress: 1.0,
      created_at: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString(),
      last_tended: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(),
      tags: ['foundation', 'categorical'],
      metadata: {},
    },
    'atelier-rebuild': {
      name: 'atelier-rebuild',
      path: 'concept.gardener.plots.atelier-rebuild',
      description: 'Atelier Crown Jewel rebuild with token economy',
      plan_path: 'plans/crown-jewels-genesis-phase2-chunks3-5.md',
      crown_jewel: 'Atelier',
      prompts: ['Add BidQueue', 'Token visualization'],
      season_override: 'BLOOMING',
      rigidity: 0.4,
      progress: 0.92,
      created_at: new Date(Date.now() - 10 * 24 * 60 * 60 * 1000).toISOString(),
      last_tended: new Date(Date.now() - 1 * 60 * 60 * 1000).toISOString(),
      tags: ['atelier', 'token-economy'],
      metadata: {},
    },
    'town-frontend': {
      name: 'town-frontend',
      path: 'concept.gardener.plots.town-frontend',
      description: 'Town/Coalition frontend visualization',
      plan_path: null,
      crown_jewel: 'Coalition',
      prompts: [],
      season_override: null,
      rigidity: 0.5,
      progress: 0.55,
      created_at: new Date(Date.now() - 14 * 24 * 60 * 60 * 1000).toISOString(),
      last_tended: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000).toISOString(),
      tags: ['town', 'coalition', 'waiting'],
      metadata: {},
    },
  },
  active_plot: 'hero-path',
  session_id: 'session-001',
  memory_crystals: ['categorical-theory', 'agent-town', 'k-gent-soul'],
  prompt_count: 42,
  prompt_types: { implementation: 28, research: 10, refactor: 4 },
  recent_gestures: [
    {
      verb: 'OBSERVE',
      target: 'concept.gardener',
      tone: 0.6,
      reasoning: 'Checking garden state before 2D Renaissance work',
      entropy_cost: 0.1,
      timestamp: new Date(Date.now() - 2 * 60 * 1000).toISOString(),
      observer: 'kent',
      session_id: 'session-001',
      result_summary: 'success',
    },
    {
      verb: 'WATER',
      target: 'concept.gardener.plots.hero-path',
      tone: 0.8,
      reasoning: 'Hydrating hero path with Gardener2D implementation',
      entropy_cost: 0.25,
      timestamp: new Date(Date.now() - 15 * 60 * 1000).toISOString(),
      observer: 'kent',
      session_id: 'session-001',
      result_summary: 'success',
    },
    {
      verb: 'GRAFT',
      target: 'concept.gardener.plots.atelier-rebuild',
      tone: 0.7,
      reasoning: 'Connecting BidQueue component to Atelier',
      entropy_cost: 0.35,
      timestamp: new Date(Date.now() - 1 * 60 * 60 * 1000).toISOString(),
      observer: 'kent',
      session_id: 'session-001',
      result_summary: 'success',
    },
  ],
  last_tended: new Date(Date.now() - 2 * 60 * 1000).toISOString(),
  metrics: {
    health_score: 0.82,
    total_prompts: 42,
    active_plots: 3,
    entropy_spent: 1.7,
    entropy_budget: 5.0,
  },
  computed: {
    health_score: 0.82,
    entropy_remaining: 3.3,
    entropy_percentage: 0.66,
    active_plot_count: 3,
    total_plot_count: 4,
    season_plasticity: 0.78,
    season_entropy_multiplier: 1.5,
  },
});

const createMockSession = (phase: GardenerPhase): GardenerSessionState => ({
  session_id: 'session-001',
  name: 'Wave 1 Hero Path Implementation',
  phase,
  plan_path: 'plans/crown-jewels-enlightened.md',
  intent: {
    description: 'Implement Gardener2D with Living Earth aesthetic',
    priority: 'high',
  },
  artifacts_count: phase === 'SENSE' ? 0 : phase === 'ACT' ? 6 : 8,
  learnings_count: phase === 'REFLECT' ? 3 : 0,
  sense_count: 2,
  act_count: phase === 'SENSE' ? 0 : 1,
  reflect_count: phase === 'REFLECT' ? 1 : 0,
});

// Mock transition suggestion (shows occasionally)
const createMockSuggestion = (): TransitionSuggestionJSON | null => {
  // 30% chance of showing suggestion for demo
  if (Math.random() > 0.3) return null;

  return {
    from_season: 'SPROUTING',
    to_season: 'BLOOMING',
    confidence: 0.73,
    reason: 'High activity and artifact creation suggest readiness for crystallization phase',
    signals: {
      gesture_frequency: 4.2,
      gesture_diversity: 0.67,
      plot_progress_delta: 0.15,
      artifacts_created: 6,
      time_in_season_hours: 2.5,
      entropy_spent_ratio: 0.34,
      reflect_count: 1,
      session_active: true,
    },
    triggered_at: new Date().toISOString(),
  };
};

// =============================================================================
// Page Component
// =============================================================================

export default function GardenerPage() {
  const [phase, setPhase] = useState<GardenerPhase>('ACT');
  const [suggestion, setSuggestion] = useState<TransitionSuggestionJSON | null>(() =>
    createMockSuggestion()
  );

  // Memoize mock data
  const garden = useMemo(() => createMockGarden(), []);
  const session = useMemo(() => createMockSession(phase), [phase]);

  // Handlers
  const handlePhaseChange = useCallback((p: GardenerPhase) => setPhase(p), []);

  const handleTend = useCallback((verb: string, target: string, reasoning?: string) => {
    console.info('[Gardener] Tending:', { verb, target, reasoning });
    // TODO: Call AGENTESE logos.invoke("concept.gardener.tend", ...)
  }, []);

  const handlePlotSelect = useCallback((plotName: string) => {
    console.info('[Gardener] Plot selected:', plotName);
  }, []);

  const handleAcceptTransition = useCallback(() => {
    console.info('[Gardener] Transition accepted');
    setSuggestion(null);
    // TODO: Call AGENTESE logos.invoke("concept.gardener.transition.accept", ...)
  }, []);

  const handleDismissTransition = useCallback(() => {
    console.info('[Gardener] Transition dismissed (4h cooldown)');
    setSuggestion(null);
    // TODO: Call AGENTESE logos.invoke("concept.gardener.transition.dismiss", ...)
  }, []);

  return (
    <div className="h-screen overflow-hidden">
      <Gardener2D
        garden={garden}
        session={session}
        onTend={handleTend}
        onPhaseChange={handlePhaseChange}
        onPlotSelect={handlePlotSelect}
        transitionSuggestion={suggestion}
        onAcceptTransition={handleAcceptTransition}
        onDismissTransition={handleDismissTransition}
      />
    </div>
  );
}
