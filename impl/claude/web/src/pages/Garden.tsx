/**
 * Garden: Gardener-Logos visualization page.
 *
 * Displays the garden state with:
 * - Season indicator
 * - Plot grid
 * - Gesture history
 * - Tending actions
 * - Auto-Inducer transition suggestions (Phase 8)
 *
 * @see plans/gardener-logos-enactment.md Phase 7, Phase 8
 */

import { useState, useEffect, useCallback } from 'react';
import { gardenerApi, GardenStateResponse, TransitionSuggestion } from '@/api/client';
import { GardenVisualization } from '@/components/garden';
import type { GardenJSON, TendingVerb, TransitionSuggestionJSON } from '@/reactive/types';
import { PersonalityLoading, EmpathyError, Breathe, PopOnMount, celebrate } from '@/components/joy';

type LoadingState = 'loading' | 'loaded' | 'error';

export default function Garden() {
  const [garden, setGarden] = useState<GardenStateResponse | null>(null);
  const [loadingState, setLoadingState] = useState<LoadingState>('loading');
  const [error, setError] = useState<string | null>(null);
  const [tending, setTending] = useState<string | null>(null); // Tracks active tending operation

  // Phase 8: Auto-Inducer state
  const [transitionSuggestion, setTransitionSuggestion] = useState<TransitionSuggestion | null>(
    null
  );
  const [isTransitionLoading, setIsTransitionLoading] = useState(false);

  // Load garden state
  const loadGarden = useCallback(async () => {
    try {
      const response = await gardenerApi.getGarden();
      setGarden(response);
      setLoadingState('loaded');
    } catch (err) {
      console.error('[Garden] Failed to load:', err);
      setError('Failed to load garden state');
      setLoadingState('error');
    }
  }, []);

  useEffect(() => {
    loadGarden();
  }, [loadGarden]);

  // Handle tending gesture
  const handleTend = useCallback(
    async (verb: TendingVerb, target: string, reasoning?: string) => {
      if (tending) return; // Prevent concurrent tending

      setTending(`${verb} ${target}`);
      try {
        const response = await gardenerApi.tend(verb, target, {
          reasoning: reasoning || `Tending ${target} with ${verb.toLowerCase()}`,
        });

        if (response.accepted) {
          // Reload garden to get updated state
          await loadGarden();

          // Foundation 5: Celebrate successful tending!
          celebrate({ intensity: 'subtle' });

          // Phase 8: Check for transition suggestion
          if (response.suggested_transition) {
            setTransitionSuggestion(response.suggested_transition);
          }
        } else {
          console.warn('[Garden] Tending not accepted:', response.error);
        }
      } catch (err) {
        console.error('[Garden] Tending failed:', err);
      } finally {
        setTending(null);
      }
    },
    [tending, loadGarden]
  );

  // Phase 8: Accept transition suggestion
  // gardenerApi now returns unwrapped data (AGENTESE pattern)
  const handleAcceptTransition = useCallback(async () => {
    if (!transitionSuggestion || isTransitionLoading) return;

    setIsTransitionLoading(true);
    try {
      const result = await gardenerApi.acceptTransition(
        transitionSuggestion.from_season,
        transitionSuggestion.to_season
      );

      if (result.status === 'accepted') {
        // Clear suggestion and reload garden
        setTransitionSuggestion(null);
        await loadGarden();
      } else {
        console.warn('[Garden] Transition not accepted:', result.message);
      }
    } catch (err) {
      console.error('[Garden] Failed to accept transition:', err);
    } finally {
      setIsTransitionLoading(false);
    }
  }, [transitionSuggestion, isTransitionLoading, loadGarden]);

  // Phase 8: Dismiss transition suggestion
  const handleDismissTransition = useCallback(async () => {
    if (!transitionSuggestion || isTransitionLoading) return;

    setIsTransitionLoading(true);
    try {
      await gardenerApi.dismissTransition(
        transitionSuggestion.from_season,
        transitionSuggestion.to_season
      );

      // Clear suggestion (don't need to reload garden)
      setTransitionSuggestion(null);
    } catch (err) {
      console.error('[Garden] Failed to dismiss transition:', err);
    } finally {
      setIsTransitionLoading(false);
    }
  }, [transitionSuggestion, isTransitionLoading]);

  // Handle plot selection
  const handlePlotSelect = useCallback(
    async (plotName: string) => {
      try {
        await gardenerApi.focusPlot(plotName);
        await loadGarden();
      } catch (err) {
        console.error('[Garden] Failed to focus plot:', err);
      }
    },
    [loadGarden]
  );

  // Loading state - Foundation 5: PersonalityLoading for gardener
  if (loadingState === 'loading') {
    return (
      <div className="h-[calc(100vh-64px)] flex items-center justify-center bg-gray-900">
        <PersonalityLoading jewel="gardener" size="lg" action="seed" />
      </div>
    );
  }

  // Error state - Foundation 5: EmpathyError with gardener personality
  if (loadingState === 'error' || !garden) {
    return (
      <div className="h-[calc(100vh-64px)] flex items-center justify-center bg-gray-900">
        <EmpathyError
          type="network"
          title="Garden Unavailable"
          subtitle={error || 'Could not load garden state'}
          details="Check that the backend server is running"
          action="Retry"
          onAction={loadGarden}
          secondaryAction="Go Home"
          onSecondaryAction={() => {
            window.location.href = '/';
          }}
          size="lg"
        />
      </div>
    );
  }

  // Convert API response to GardenJSON format for visualization
  const gardenJSON: GardenJSON = {
    type: 'garden',
    garden_id: garden.garden_id,
    name: garden.name,
    created_at: garden.created_at,
    season: garden.season,
    season_since: garden.season_since,
    plots: Object.fromEntries(
      Object.entries(garden.plots).map(([key, plot]) => [
        key,
        {
          ...plot,
          metadata: plot.metadata as Record<string, unknown>,
        },
      ])
    ),
    active_plot: garden.active_plot,
    session_id: garden.session_id,
    memory_crystals: garden.memory_crystals,
    prompt_count: garden.prompt_count,
    prompt_types: garden.prompt_types,
    recent_gestures: garden.recent_gestures,
    last_tended: garden.last_tended,
    metrics: garden.metrics,
    computed: garden.computed,
  };

  return (
    <div className="h-[calc(100vh-64px)] flex flex-col bg-gray-900">
      {/* Tending indicator - Foundation 5: Breathe animation */}
      {tending && (
        <div className="absolute top-20 left-1/2 transform -translate-x-1/2 z-50">
          <PopOnMount scale={1.05} duration={200}>
            <Breathe intensity={0.4} speed="fast">
              <div className="bg-jewel-gardener-bg/90 text-jewel-gardener px-4 py-2 rounded-lg shadow-lg flex items-center gap-2 backdrop-blur-sm">
                <span className="animate-pulse">💧</span>
                <span>Tending: {tending}</span>
              </div>
            </Breathe>
          </PopOnMount>
        </div>
      )}

      {/* Main visualization */}
      <GardenVisualization
        garden={gardenJSON}
        onTend={handleTend}
        onPlotSelect={handlePlotSelect}
        className="flex-1"
        // Phase 8: Auto-Inducer props
        transitionSuggestion={transitionSuggestion as TransitionSuggestionJSON | null}
        onAcceptTransition={handleAcceptTransition}
        onDismissTransition={handleDismissTransition}
        isTransitionLoading={isTransitionLoading}
      />
    </div>
  );
}
