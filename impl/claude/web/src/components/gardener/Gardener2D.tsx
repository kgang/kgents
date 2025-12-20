/**
 * Gardener2D - Unified Garden + Session Visualization
 *
 * The 2D Renaissance implementation that unifies:
 * - GardenVisualization (plot grid, seasons, gestures)
 * - GardenerVisualization (session state machine)
 *
 * Into a single organic experience with Living Earth aesthetic.
 *
 * @see spec/protocols/2d-renaissance.md - Phase 2: Gardener2D
 * @see docs/creative/visual-system.md - NO EMOJIS policy
 */

import { useState, useCallback } from 'react';
import { Leaf } from 'lucide-react';
import { useShell } from '@/shell';
import { ElasticSplit } from '@/components/elastic/ElasticSplit';
import { BottomDrawer } from '@/components/elastic/BottomDrawer';
import { Breathe } from '@/components/joy';
import type {
  GardenJSON,
  TendingVerb,
  TransitionSuggestionJSON,
  ConceptSeedJSON,
} from '@/reactive/types';
import type { GardenerSessionState, GardenerPhase } from '@/api/types';

// Sub-components
import { SeasonOrb } from './SeasonOrb';
import { PlotTile } from './PlotTile';
import { GestureStream } from './GestureStream';
import { SessionPolynomial } from './SessionPolynomial';
import { TendingPalette } from './TendingPalette';
import { TransitionSuggester } from './TransitionSuggester';
import { NurseryBed } from './NurseryBed';

// =============================================================================
// Types
// =============================================================================

export interface Gardener2DProps {
  /** Garden state from AGENTESE */
  garden: GardenJSON;
  /** Session state from AGENTESE */
  session: GardenerSessionState;
  /** Callback when tending action is submitted */
  onTend?: (verb: TendingVerb, target: string, reasoning?: string) => void;
  /** Callback when phase changes */
  onPhaseChange?: (phase: GardenerPhase) => void;
  /** Callback when plot is selected */
  onPlotSelect?: (plotName: string) => void;
  /** Auto-Inducer transition suggestion */
  transitionSuggestion?: TransitionSuggestionJSON | null;
  /** Accept transition callback */
  onAcceptTransition?: () => void;
  /** Dismiss transition callback */
  onDismissTransition?: () => void;
  /** Transition loading state */
  isTransitionLoading?: boolean;
  /** Concept seeds from nursery */
  nurserySeeds?: ConceptSeedJSON[];
  /** Callback when user promotes a concept */
  onPromoteConcept?: (handle: string) => void;
  /** Callback when user dismisses a concept */
  onDismissConcept?: (handle: string) => void;
  /** Custom class name */
  className?: string;
}

// =============================================================================
// Main Component
// =============================================================================

export function Gardener2D({
  garden,
  session,
  onTend,
  onPhaseChange,
  onPlotSelect,
  transitionSuggestion,
  onAcceptTransition,
  onDismissTransition,
  isTransitionLoading = false,
  nurserySeeds = [],
  onPromoteConcept,
  onDismissConcept,
  className = '',
}: Gardener2DProps) {
  const { density, isMobile } = useShell();
  const [selectedPlot, setSelectedPlot] = useState<string | null>(garden.active_plot);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [drawerContent, setDrawerContent] = useState<'gestures' | 'tending' | 'detail'>('gestures');

  // Handle plot selection
  const handlePlotSelect = useCallback(
    (plotName: string) => {
      setSelectedPlot(plotName === selectedPlot ? null : plotName);
      onPlotSelect?.(plotName);
      if (isMobile) {
        setDrawerContent('detail');
        setDrawerOpen(true);
      }
    },
    [selectedPlot, onPlotSelect, isMobile]
  );

  // Handle tending action
  const handleTend = useCallback(
    (verb: TendingVerb, target: string, reasoning?: string) => {
      onTend?.(verb, target, reasoning);
      if (isMobile) {
        setDrawerOpen(false);
      }
    },
    [onTend, isMobile]
  );

  // Open drawer for specific content
  const openDrawer = useCallback((content: 'gestures' | 'tending' | 'detail') => {
    setDrawerContent(content);
    setDrawerOpen(true);
  }, []);

  const plots = Object.values(garden.plots);
  const selectedPlotData = selectedPlot ? garden.plots[selectedPlot] : null;

  // ==========================================================================
  // Mobile Layout
  // ==========================================================================
  if (isMobile) {
    return (
      <div className={`flex flex-col h-full bg-[#2D1B14] ${className}`}>
        {/* Header */}
        <Gardener2DHeader garden={garden} session={session} density={density} />

        {/* Auto-Inducer Banner */}
        {transitionSuggestion && onAcceptTransition && onDismissTransition && (
          <div className="px-3 pt-3">
            <TransitionSuggester
              suggestion={transitionSuggestion}
              onAccept={onAcceptTransition}
              onDismiss={onDismissTransition}
              isLoading={isTransitionLoading}
              compact
            />
          </div>
        )}

        {/* Main Content - Scrollable */}
        <div className="flex-1 overflow-y-auto p-3 space-y-4">
          {/* Season Orb */}
          <SeasonOrb
            season={garden.season}
            plasticity={garden.computed.season_plasticity}
            entropyMultiplier={garden.computed.season_entropy_multiplier}
            seasonSince={garden.season_since}
            compact
          />

          {/* Session State Machine (inline) */}
          <SessionPolynomial session={session} onPhaseChange={onPhaseChange} compact />

          {/* Concept Nursery (compact, if seeds exist) */}
          <NurseryBed
            seeds={nurserySeeds}
            onPromote={onPromoteConcept}
            onDismiss={onDismissConcept}
            compact
          />

          {/* Plot Tiles */}
          <div>
            <h3 className="text-xs font-semibold text-[#AB9080] uppercase tracking-wide mb-2">
              Plots ({garden.computed.active_plot_count}/{garden.computed.total_plot_count})
            </h3>
            <div className="space-y-2">
              {plots.map((plot) => (
                <PlotTile
                  key={plot.name}
                  plot={plot}
                  isActive={plot.name === garden.active_plot}
                  isSelected={plot.name === selectedPlot}
                  gardenSeason={garden.season}
                  onSelect={handlePlotSelect}
                  compact
                />
              ))}
            </div>
          </div>
        </div>

        {/* Floating Actions */}
        <TendingPalette
          target={selectedPlot || 'concept.gardener'}
          onTend={handleTend}
          onOpenGestures={() => openDrawer('gestures')}
          floating
        />

        {/* Bottom Drawer */}
        <BottomDrawer
          isOpen={drawerOpen}
          onClose={() => setDrawerOpen(false)}
          title={
            drawerContent === 'gestures'
              ? 'Gesture Stream'
              : drawerContent === 'tending'
                ? 'Tend Plot'
                : selectedPlotData?.name || 'Plot Detail'
          }
        >
          {drawerContent === 'gestures' && (
            <div className="p-4">
              <GestureStream gestures={garden.recent_gestures} maxDisplay={15} />
            </div>
          )}
          {drawerContent === 'detail' && selectedPlotData && (
            <PlotDetailPanel
              plot={selectedPlotData}
              gardenSeason={garden.season}
              onTend={handleTend}
            />
          )}
        </BottomDrawer>
      </div>
    );
  }

  // ==========================================================================
  // Desktop/Tablet Layout (ElasticSplit)
  // ==========================================================================
  return (
    <div className={`h-full bg-[#2D1B14] ${className}`}>
      {/* Header */}
      <Gardener2DHeader garden={garden} session={session} density={density} />

      {/* Auto-Inducer Banner */}
      {transitionSuggestion && onAcceptTransition && onDismissTransition && (
        <div className="px-4 pt-3">
          <TransitionSuggester
            suggestion={transitionSuggestion}
            onAccept={onAcceptTransition}
            onDismiss={onDismissTransition}
            isLoading={isTransitionLoading}
          />
        </div>
      )}

      {/* Main Split View */}
      <ElasticSplit
        defaultRatio={0.65}
        collapseAtDensity="compact"
        collapsePriority="secondary"
        className="flex-1"
        primary={
          <div className="h-full overflow-y-auto p-4 space-y-4">
            {/* Season Orb */}
            <SeasonOrb
              season={garden.season}
              plasticity={garden.computed.season_plasticity}
              entropyMultiplier={garden.computed.season_entropy_multiplier}
              seasonSince={garden.season_since}
            />

            {/* Plot Grid */}
            <div>
              <h3 className="text-xs font-semibold text-[#AB9080] uppercase tracking-wide mb-3">
                Plots ({garden.computed.active_plot_count}/{garden.computed.total_plot_count}{' '}
                active)
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {plots.map((plot) => (
                  <PlotTile
                    key={plot.name}
                    plot={plot}
                    isActive={plot.name === garden.active_plot}
                    isSelected={plot.name === selectedPlot}
                    gardenSeason={garden.season}
                    onSelect={handlePlotSelect}
                  />
                ))}
              </div>
            </div>

            {/* Gesture Stream */}
            <div>
              <h3 className="text-xs font-semibold text-[#AB9080] uppercase tracking-wide mb-3">
                Gesture Stream
              </h3>
              <GestureStream gestures={garden.recent_gestures} maxDisplay={8} />
            </div>
          </div>
        }
        secondary={
          <div className="h-full overflow-y-auto p-4 space-y-4 border-l border-[#4A3728]">
            {/* Session Polynomial */}
            <SessionPolynomial session={session} onPhaseChange={onPhaseChange} />

            {/* Concept Nursery (if seeds exist) */}
            <NurseryBed
              seeds={nurserySeeds}
              onPromote={onPromoteConcept}
              onDismiss={onDismissConcept}
            />

            {/* Selected Plot Detail or Tending Palette */}
            {selectedPlotData ? (
              <PlotDetailPanel
                plot={selectedPlotData}
                gardenSeason={garden.season}
                onTend={handleTend}
                onClose={() => setSelectedPlot(null)}
              />
            ) : (
              <TendingPalette target="concept.gardener" onTend={handleTend} />
            )}
          </div>
        }
      />
    </div>
  );
}

// =============================================================================
// Sub-Components
// =============================================================================

interface HeaderProps {
  garden: GardenJSON;
  session: GardenerSessionState;
  density: string;
}

function Gardener2DHeader({ garden, session, density }: HeaderProps) {
  const isCompact = density === 'compact';

  return (
    <header className="flex-shrink-0 bg-[#4A3728]/50 border-b border-[#6B4E3D] px-4 py-3">
      <div className="flex items-center justify-between">
        {/* Left: Garden info */}
        <div className="flex items-center gap-3">
          <Breathe intensity={0.3} speed="slow">
            <Leaf className="w-6 h-6 text-[#4A6B4A]" />
          </Breathe>
          <div>
            <h1 className={`font-semibold text-[#F5E6D3] ${isCompact ? 'text-base' : 'text-lg'}`}>
              The Gardener
            </h1>
            <p className={`text-[#AB9080] ${isCompact ? 'text-[10px]' : 'text-xs'}`}>
              {session.name || garden.name}
            </p>
          </div>
        </div>

        {/* Right: Session indicator */}
        <div className="flex items-center gap-3">
          <div className="text-right">
            <div className={`text-[#AB9080] ${isCompact ? 'text-[10px]' : 'text-xs'}`}>Session</div>
            <div className={`font-medium text-[#D4A574] ${isCompact ? 'text-xs' : 'text-sm'}`}>
              {formatDuration(session.sense_count + session.act_count + session.reflect_count)}
            </div>
          </div>
          <div
            className={`px-2 py-1 rounded-full text-xs font-medium bg-[#4A6B4A]/30 text-[#8BAB8B]`}
          >
            {session.phase}
          </div>
        </div>
      </div>
    </header>
  );
}

interface PlotDetailPanelProps {
  plot: NonNullable<GardenJSON['plots'][string]>;
  gardenSeason: GardenJSON['season'];
  onTend?: (verb: TendingVerb, target: string, reasoning?: string) => void;
  onClose?: () => void;
}

function PlotDetailPanel({
  plot,
  gardenSeason: _gardenSeason,
  onTend,
  onClose,
}: PlotDetailPanelProps) {
  return (
    <div className="p-4 bg-[#4A3728]/30 rounded-lg">
      {/* Header */}
      <div className="flex items-center justify-between mb-3">
        <h3 className="font-semibold text-[#F5E6D3]">{formatPlotName(plot.name)}</h3>
        {onClose && (
          <button
            onClick={onClose}
            className="text-[#AB9080] hover:text-[#F5E6D3] text-lg transition-colors"
            aria-label="Close"
          >
            x
          </button>
        )}
      </div>

      {/* Description */}
      {plot.description && <p className="text-sm text-[#AB9080] mb-3">{plot.description}</p>}

      {/* AGENTESE path */}
      <div className="mb-3">
        <span className="text-xs text-[#6B4E3D]">Path: </span>
        <code className="text-xs text-[#8BAB8B] bg-[#1A2E1A] px-1.5 py-0.5 rounded">
          {plot.path}
        </code>
      </div>

      {/* Progress */}
      <div className="mb-3">
        <div className="flex justify-between text-xs mb-1">
          <span className="text-[#6B4E3D]">Progress</span>
          <span className="text-[#8BAB8B]">{(plot.progress * 100).toFixed(0)}%</span>
        </div>
        <div className="h-2 bg-[#1A2E1A] rounded-full overflow-hidden">
          <div
            className="h-full bg-[#4A6B4A] transition-all duration-500"
            style={{ width: `${plot.progress * 100}%` }}
          />
        </div>
      </div>

      {/* Tending Actions */}
      {onTend && (
        <div className="pt-3 border-t border-[#6B4E3D]">
          <TendingPalette target={plot.path} onTend={onTend} inline />
        </div>
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

function formatDuration(cycles: number): string {
  if (cycles === 0) return 'Starting';
  if (cycles === 1) return '1 cycle';
  return `${cycles} cycles`;
}

export default Gardener2D;
