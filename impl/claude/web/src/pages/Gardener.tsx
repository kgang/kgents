/**
 * Gardener Page - 2D Renaissance Implementation
 *
 * The Gardener is the meta-jewel for development sessions, combining:
 * - Garden state (plots, seasons, gestures) from self.garden.*
 * - Session state machine (SENSE -> ACT -> REFLECT) from concept.gardener.*
 *
 * This page uses BOTH AGENTESE node families:
 * - self.garden.* → useGardenManifest() → GardenJSON (plots, seasons)
 * - concept.gardener.* → useGardenerSession() → session state (phase, intent)
 *
 * @see spec/protocols/2d-renaissance.md - Phase 2
 * @see docs/creative/visual-system.md - NO EMOJIS policy
 */

import { useMemo, useCallback } from 'react';
import { Gardener2D } from '@/components/gardener';
import type { GardenerSessionState } from '@/api/types';
import type { GardenJSON, TransitionSuggestionJSON } from '@/reactive/types';
import {
  useGardenManifest,
  useGardenSuggest,
  useGardenAccept,
  useGardenDismiss,
  toTransitionSuggestion,
} from '@/hooks';
import { useGardenerSession } from '@/hooks/useGardenerQuery';

// Gardener polynomial phase - local definition for type safety
type GardenerPhase = 'SENSE' | 'ACT' | 'REFLECT';

// =============================================================================
// Default/Fallback Data (shows when API unavailable)
// =============================================================================

const DEFAULT_GARDEN: GardenJSON = {
  type: 'garden',
  garden_id: 'default',
  name: 'Loading...',
  created_at: new Date().toISOString(),
  season: 'DORMANT',
  season_since: new Date().toISOString(),
  plots: {},
  active_plot: null,
  session_id: null,
  memory_crystals: [],
  prompt_count: 0,
  prompt_types: {},
  recent_gestures: [],
  last_tended: new Date().toISOString(),
  metrics: {
    health_score: 0,
    total_prompts: 0,
    active_plots: 0,
    entropy_spent: 0,
    entropy_budget: 5.0,
  },
  computed: {
    health_score: 0,
    entropy_remaining: 5.0,
    entropy_percentage: 1.0,
    active_plot_count: 0,
    total_plot_count: 0,
    season_plasticity: 0.5,
    season_entropy_multiplier: 1.0,
  },
};

const DEFAULT_SESSION: GardenerSessionState = {
  session_id: 'default',
  name: 'No Active Session',
  phase: 'SENSE',
  artifacts_count: 0,
  learnings_count: 0,
  sense_count: 0,
  act_count: 0,
  reflect_count: 0,
};

// =============================================================================
// Transform API Response to GardenerSessionState
// =============================================================================

function toSessionState(
  apiResponse: {
    status: string;
    session_id?: string | null;
    name?: string | null;
    phase?: unknown;
    sense_count?: number;
    act_count?: number;
    reflect_count?: number;
    intent?: string | null;
    plan_path?: string | null;
  } | null
): GardenerSessionState | null {
  if (!apiResponse || apiResponse.status === 'no_session') {
    return null;
  }

  const phase = (apiResponse.phase as GardenerPhase) ?? 'SENSE';

  return {
    session_id: apiResponse.session_id ?? 'unknown',
    name: apiResponse.name ?? 'Unnamed Session',
    phase,
    plan_path: apiResponse.plan_path ?? undefined,
    intent: apiResponse.intent
      ? { description: apiResponse.intent, priority: 'medium' }
      : undefined,
    artifacts_count: phase === 'SENSE' ? 0 : phase === 'ACT' ? 6 : 8,
    learnings_count: phase === 'REFLECT' ? 3 : 0,
    sense_count: apiResponse.sense_count ?? 0,
    act_count: apiResponse.act_count ?? 0,
    reflect_count: apiResponse.reflect_count ?? 0,
  };
}

// =============================================================================
// Loading State Component
// =============================================================================

function LoadingState() {
  return (
    <div className="h-screen flex items-center justify-center bg-gradient-to-br from-emerald-50 to-green-100 dark:from-gray-900 dark:to-gray-800">
      <div className="text-center space-y-4">
        <div className="w-16 h-16 mx-auto border-4 border-emerald-500 border-t-transparent rounded-full animate-spin" />
        <p className="text-lg text-emerald-700 dark:text-emerald-400">
          Growing the garden...
        </p>
      </div>
    </div>
  );
}

// =============================================================================
// Error State Component
// =============================================================================

function ErrorState({ error, onRetry }: { error: Error; onRetry: () => void }) {
  return (
    <div className="h-screen flex items-center justify-center bg-gradient-to-br from-red-50 to-amber-50 dark:from-gray-900 dark:to-gray-800">
      <div className="text-center space-y-4 max-w-md px-6">
        <div className="text-4xl mb-4">🥀</div>
        <h2 className="text-xl font-semibold text-red-700 dark:text-red-400">
          Garden Dormant
        </h2>
        <p className="text-gray-600 dark:text-gray-400">
          Could not connect to the garden backend. The soil needs tending.
        </p>
        <p className="text-sm text-gray-500 dark:text-gray-500 font-mono">
          {error.message}
        </p>
        <button
          onClick={onRetry}
          className="mt-4 px-6 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg transition-colors"
        >
          Retry Connection
        </button>
      </div>
    </div>
  );
}

// =============================================================================
// Page Component
// =============================================================================

export default function GardenerPage() {
  // ─────────────────────────────────────────────────────────────────────────────
  // Data Fetching: self.garden.* for state, concept.gardener.* for session
  // ─────────────────────────────────────────────────────────────────────────────

  const {
    data: gardenData,
    isLoading: gardenLoading,
    error: gardenError,
    refetch: refetchGarden,
  } = useGardenManifest();

  const {
    data: sessionData,
    isLoading: sessionLoading,
    error: sessionError,
    refetch: refetchSession,
  } = useGardenerSession();

  const {
    data: suggestData,
    refetch: refetchSuggest,
  } = useGardenSuggest({ enabled: !gardenLoading && !gardenError });

  // Mutation hooks for transition actions
  const { mutateAsync: acceptTransition } = useGardenAccept();
  const { mutateAsync: dismissTransition } = useGardenDismiss();

  // ─────────────────────────────────────────────────────────────────────────────
  // Derived State with Graceful Fallbacks
  // ─────────────────────────────────────────────────────────────────────────────

  // Garden state: use API data or default
  const garden = useMemo<GardenJSON>(() => {
    if (gardenData && gardenData.type === 'garden') {
      return gardenData;
    }
    return DEFAULT_GARDEN;
  }, [gardenData]);

  // Session state: transform API response
  const session = useMemo<GardenerSessionState>(() => {
    const transformed = toSessionState(sessionData);
    return transformed ?? DEFAULT_SESSION;
  }, [sessionData]);

  // Transition suggestion: convert backend response to frontend type
  const suggestion = useMemo<TransitionSuggestionJSON | null>(() => {
    return toTransitionSuggestion(suggestData ?? null);
  }, [suggestData]);

  // ─────────────────────────────────────────────────────────────────────────────
  // Handlers
  // ─────────────────────────────────────────────────────────────────────────────

  const handleTend = useCallback((verb: string, target: string, reasoning?: string) => {
    console.info('[Gardener] Tending:', { verb, target, reasoning });
    // TODO: Call AGENTESE logos.invoke("self.garden.tend", ...)
    // After tending, refetch garden state
    refetchGarden();
  }, [refetchGarden]);

  const handlePhaseChange = useCallback((_p: GardenerPhase) => {
    // Session phase is managed by concept.gardener.session.advance
    // This handler is for local UI state if needed
    refetchSession();
  }, [refetchSession]);

  const handlePlotSelect = useCallback((plotName: string) => {
    console.info('[Gardener] Plot selected:', plotName);
    // TODO: Could call self.garden.active to set active plot
  }, []);

  const handleAcceptTransition = useCallback(async () => {
    console.info('[Gardener] Transition accepted');
    try {
      await acceptTransition();
      // Refetch to get updated state
      refetchGarden();
      refetchSuggest();
    } catch (err) {
      console.error('[Gardener] Failed to accept transition:', err);
    }
  }, [acceptTransition, refetchGarden, refetchSuggest]);

  const handleDismissTransition = useCallback(async () => {
    console.info('[Gardener] Transition dismissed (4h cooldown)');
    try {
      await dismissTransition();
      // Refetch to clear suggestion
      refetchSuggest();
    } catch (err) {
      console.error('[Gardener] Failed to dismiss transition:', err);
    }
  }, [dismissTransition, refetchSuggest]);

  const handleRetry = useCallback(() => {
    refetchGarden();
    refetchSession();
    refetchSuggest();
  }, [refetchGarden, refetchSession, refetchSuggest]);

  // ─────────────────────────────────────────────────────────────────────────────
  // Loading & Error States
  // ─────────────────────────────────────────────────────────────────────────────

  const isLoading = gardenLoading || sessionLoading;
  const error = gardenError ?? sessionError;

  if (isLoading) {
    return <LoadingState />;
  }

  if (error) {
    return <ErrorState error={error} onRetry={handleRetry} />;
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Render
  // ─────────────────────────────────────────────────────────────────────────────

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
