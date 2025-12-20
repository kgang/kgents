/**
 * Garden: Gardener-Logos visualization page.
 *
 * Displays the garden state with:
 * - Season indicator
 * - Plot grid
 * - Gesture history
 * - Tending actions
 * - Auto-Inducer transition suggestions (Phase 8)
 * - Live Witness thoughts + Muse whispers (Phase 2-3)
 *
 * ELASTIC UI (Phase 4):
 * - Compact (mobile): Single-column, bottom drawer, floating quick-tend
 * - Comfortable (tablet): Two-column with collapsible details
 * - Spacious (desktop): Full layout with persistent overlays
 *
 * @see plans/melodic-toasting-octopus.md Phase 4
 * @see docs/skills/elastic-ui-patterns.md
 */

import { useState, useEffect, useCallback } from 'react';
import { gardenerApi, GardenStateResponse, TransitionSuggestion } from '@/api/client';
import { GardenVisualization } from '@/components/garden';
import type { GardenJSON, TendingVerb, TransitionSuggestionJSON } from '@/reactive/types';
import { PersonalityLoading, EmpathyError, Breathe, PopOnMount, celebrate } from '@/components/joy';
import {
  useWindowLayout,
  BottomDrawer,
  FloatingActions,
  type FloatingAction,
} from '@/components/elastic';
import { WitnessOverlay } from '@/components/witness/WitnessOverlay';
import { MuseWhisper } from '@/components/muse/MuseWhisper';
import { useWitnessStream } from '@/hooks/useWitnessStream';
import { useMuseStream } from '@/hooks/useMuseStream';

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

  // Phase 4: Elastic UI - layout awareness
  const { density, isMobile } = useWindowLayout();

  // Phase 4: Mobile drawer state for details panel
  const [detailsDrawerOpen, setDetailsDrawerOpen] = useState(false);
  const [selectedPlotForDrawer, setSelectedPlotForDrawer] = useState<string | null>(null);

  // Phase 2-3: Witness and Muse streams
  const witnessStream = useWitnessStream({
    sources: ['gardener', 'git', 'system'],
    enabled: loadingState === 'loaded',
  });

  const museStream = useMuseStream({
    enabled: loadingState === 'loaded',
  });

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

  // Handle plot selection - adapts to density
  const handlePlotSelect = useCallback(
    async (plotName: string) => {
      try {
        await gardenerApi.focusPlot(plotName);
        await loadGarden();

        // On mobile, open the details drawer
        if (isMobile) {
          setSelectedPlotForDrawer(plotName);
          setDetailsDrawerOpen(true);
        }
      } catch (err) {
        console.error('[Garden] Failed to focus plot:', err);
      }
    },
    [loadGarden, isMobile]
  );

  // Phase 4: Floating action handlers for mobile quick-tending
  const quickTendActions: FloatingAction[] = [
    {
      id: 'observe',
      icon: '👁️',
      label: 'Observe',
      onClick: () => handleTend('OBSERVE', 'concept.gardener'),
      variant: 'default',
    },
    {
      id: 'water',
      icon: '💧',
      label: 'Water',
      onClick: () => handleTend('WATER', 'concept.gardener'),
      variant: 'primary',
    },
    {
      id: 'prune',
      icon: '✂️',
      label: 'Prune',
      onClick: () => handleTend('PRUNE', 'concept.gardener'),
      variant: 'default',
    },
  ];

  // Phase 3: Muse whisper handlers
  const handleMuseDismiss = useCallback(() => {
    if (museStream.currentWhisper) {
      museStream.dismiss(museStream.currentWhisper.whisper_id, 'user_dismissed');
    }
  }, [museStream]);

  const handleMuseAccept = useCallback(() => {
    if (museStream.currentWhisper) {
      museStream.accept(museStream.currentWhisper.whisper_id, 'acknowledged');
    }
  }, [museStream]);

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

  // Get selected plot data for mobile drawer
  const selectedDrawerPlotData = selectedPlotForDrawer ? garden.plots[selectedPlotForDrawer] : null;

  return (
    <div className="h-[calc(100vh-64px)] flex flex-col bg-gray-900 relative">
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

      {/* Main visualization with density awareness */}
      <GardenVisualization
        garden={gardenJSON}
        onTend={handleTend}
        onPlotSelect={handlePlotSelect}
        className="flex-1"
        density={density}
        // Phase 8: Auto-Inducer props
        transitionSuggestion={transitionSuggestion as TransitionSuggestionJSON | null}
        onAcceptTransition={handleAcceptTransition}
        onDismissTransition={handleDismissTransition}
        isTransitionLoading={isTransitionLoading}
      />

      {/* Phase 4: Mobile floating actions for quick tending */}
      {isMobile && (
        <FloatingActions
          actions={quickTendActions}
          position="bottom-right"
          direction="vertical"
          className="z-30"
        />
      )}

      {/* Phase 4: Mobile bottom drawer for plot details */}
      <BottomDrawer
        isOpen={detailsDrawerOpen && isMobile}
        onClose={() => setDetailsDrawerOpen(false)}
        title={
          selectedDrawerPlotData ? formatPlotName(selectedDrawerPlotData.name) : 'Plot Details'
        }
        maxHeightPercent={60}
      >
        {selectedDrawerPlotData && (
          <div className="p-4 space-y-4">
            {/* Description */}
            {selectedDrawerPlotData.description && (
              <p className="text-sm text-gray-400">{selectedDrawerPlotData.description}</p>
            )}

            {/* Progress */}
            <div>
              <div className="flex justify-between text-xs mb-1">
                <span className="text-gray-500">Progress</span>
                <span className="text-gray-400">
                  {(selectedDrawerPlotData.progress * 100).toFixed(0)}%
                </span>
              </div>
              <div className="h-2 bg-gray-700 rounded-full overflow-hidden">
                <div
                  className="h-full bg-green-500 transition-all"
                  style={{ width: `${selectedDrawerPlotData.progress * 100}%` }}
                />
              </div>
            </div>

            {/* Quick tending actions */}
            <div>
              <h4 className="text-xs font-semibold text-gray-500 mb-2">Tend this plot</h4>
              <div className="grid grid-cols-3 gap-2">
                {(['OBSERVE', 'WATER', 'PRUNE'] as const).map((verb) => (
                  <button
                    key={verb}
                    onClick={() => {
                      handleTend(verb, selectedDrawerPlotData.path);
                      setDetailsDrawerOpen(false);
                    }}
                    className="flex flex-col items-center gap-1 p-3 rounded bg-gray-800 hover:bg-gray-700 transition-colors"
                  >
                    <span className="text-xl">
                      {verb === 'OBSERVE' ? '👁️' : verb === 'WATER' ? '💧' : '✂️'}
                    </span>
                    <span className="text-[10px] text-gray-400">{verb}</span>
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}
      </BottomDrawer>

      {/* Phase 2: Witness Overlay - adapts to density */}
      {!isMobile && (
        <WitnessOverlay
          thoughts={witnessStream.thoughts}
          isWitnessing={witnessStream.isWitnessing}
          status={witnessStream.status}
          density={density}
          onMarkMoment={() => console.log('[Garden] Mark moment')}
          onCrystallize={() => console.log('[Garden] Crystallize')}
        />
      )}

      {/* Phase 3: Muse Whisper - hide on mobile, show on tablet/desktop */}
      {!isMobile && museStream.currentWhisper && (
        <MuseWhisper
          whisper={museStream.currentWhisper}
          onDismiss={handleMuseDismiss}
          onAccept={handleMuseAccept}
          autoHideTimeout={30000}
        />
      )}
    </div>
  );
}

// =============================================================================
// Helpers
// =============================================================================

function formatPlotName(name: string): string {
  return name
    .split('-')
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
}
