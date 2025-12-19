/**
 * ForgeVisualization - The Metaphysical Forge visualization canvas
 *
 * PHASE 1: Stripped of spectator economy, renamed from Atelier to Forge.
 * PHASE 2: K-gent Integration - SoulPresence in header, governance gate in backend.
 *
 * This component handles:
 * - Multi-view navigation (Overview, Workshops, Artisans, Contributions)
 * - Artisan selection and workshop browsing
 * - Contribution viewing
 * - Mobile/tablet/desktop layouts
 * - K-gent soul presence indicator (Phase 2)
 *
 * "The Forge is where Kent builds with Kent."
 *
 * @see spec/protocols/metaphysical-forge.md
 * @see docs/skills/crown-jewel-patterns.md
 */

import { useState, useCallback } from 'react';
import { Hammer, Users, Brush, Image } from 'lucide-react';
import {
  useForgeManifest,
  useWorkshops,
  useArtisans,
  useContributions,
  type WorldForgeWorkshopListResponse,
  type WorldForgeArtisanListResponse,
  type WorldForgeContributionListResponse,
} from '@/hooks/useForgeQuery';
import { ErrorPanel, LoadingPanel, SoulPresence } from '@/components/forge';
import { cn } from '@/lib/utils';
import type { Density } from '@/shell/types';

// =============================================================================
// Types
// =============================================================================

export interface ForgeVisualizationProps {
  /** Initial status data from PathProjection */
  status: ForgeStatusData | null;
  /** Current layout density */
  density: Density;
  /** Layout helpers */
  isMobile: boolean;
  isTablet: boolean;
  isDesktop: boolean;
  /** Refetch function from PathProjection */
  refetch: () => void;
}

/** Status data from world.forge.manifest */
export interface ForgeStatusData {
  total_workshops?: number;
  active_workshops?: number;
  total_artisans?: number;
  total_contributions?: number;
  total_exhibitions?: number;
  open_exhibitions?: number;
  status?: string;
}

type View = 'overview' | 'workshops' | 'artisans' | 'contributions';

// =============================================================================
// Component
// =============================================================================

export function ForgeVisualization({
  status: _status,
  density: _density,
  isMobile,
  isTablet: _isTablet,
  isDesktop: _isDesktop,
  refetch: _refetch,
}: ForgeVisualizationProps) {
  // Navigation state
  const [view, setView] = useState<View>('overview');
  const [selectedWorkshopId, setSelectedWorkshopId] = useState<string | null>(null);

  // AGENTESE hooks - contract-driven data fetching
  const manifest = useForgeManifest();
  const workshops = useWorkshops();
  const artisans = useArtisans(selectedWorkshopId || '', { enabled: !!selectedWorkshopId });
  const contributions = useContributions({ workshopId: selectedWorkshopId ?? undefined });

  // Combined loading/error state
  const isLoading = manifest.isLoading || workshops.isLoading;
  const error = manifest.error?.message || workshops.error?.message || null;

  // Retry handler for error state
  const handleRetry = useCallback(() => {
    manifest.refetch();
    workshops.refetch();
    if (selectedWorkshopId) {
      artisans.refetch();
      contributions.refetch();
    }
  }, [manifest, workshops, artisans, contributions, selectedWorkshopId]);

  // Select a workshop to view its artisans
  const selectWorkshop = useCallback((workshopId: string) => {
    setSelectedWorkshopId(workshopId);
    setView('artisans');
  }, []);

  // Navigation tabs
  const tabs: Array<{ key: View; label: string; icon: typeof Hammer }> = [
    { key: 'overview', label: 'Overview', icon: Hammer },
    { key: 'workshops', label: 'Workshops', icon: Users },
    { key: 'artisans', label: 'Artisans', icon: Brush },
    { key: 'contributions', label: 'Works', icon: Image },
  ];

  // Density-adaptive styles
  const containerPadding = isMobile ? 'px-4 py-4' : 'px-6 py-8';
  const maxWidth = isMobile ? 'max-w-full' : 'max-w-6xl';
  const titleSize = isMobile ? 'text-xl' : 'text-2xl';

  return (
    <div className="min-h-screen bg-stone-50">
      {/* Header */}
      <header className="bg-white border-b border-stone-100">
        <div className={`${maxWidth} mx-auto ${containerPadding}`}>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              {/* K-gent Soul Presence (Phase 2) */}
              <SoulPresence compact={isMobile} showEigenvectors={!isMobile} />
              <div>
                <h1 className={`${titleSize} font-serif text-stone-800 flex items-center gap-2`}>
                  <Hammer className="w-5 h-5 text-amber-500" />
                  Forge
                </h1>
                <p className="mt-1 text-sm text-stone-400">Where agents are built</p>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Navigation */}
      <nav className="bg-white border-b border-stone-100 sticky top-0 z-10">
        <div className={`${maxWidth} mx-auto ${isMobile ? 'px-4' : 'px-6'}`}>
          <div className="flex items-center gap-1 overflow-x-auto">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.key}
                  onClick={() => setView(tab.key)}
                  className={cn(
                    'px-4 py-3 text-sm font-medium transition-colors whitespace-nowrap',
                    'border-b-2 -mb-px flex items-center gap-2',
                    view === tab.key
                      ? 'border-amber-400 text-amber-700'
                      : 'border-transparent text-stone-500 hover:text-stone-700'
                  )}
                >
                  <Icon className="w-4 h-4" />
                  {tab.label}
                </button>
              );
            })}
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className={`${maxWidth} mx-auto ${containerPadding}`}>
        {/* Global Error State */}
        {error && <ErrorPanel title="Unable to load forge" message={error} onRetry={handleRetry} />}

        {/* Global Loading State */}
        {isLoading && !error && <LoadingPanel message="Preparing the forge..." />}

        {/* Overview View - Manifest Stats */}
        {!isLoading && !error && view === 'overview' && manifest.data && (
          <div className="space-y-6">
            <h2 className="text-lg font-medium text-stone-700">Forge Overview</h2>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
              <StatCard
                label="Workshops"
                value={manifest.data.total_workshops}
                subValue={`${manifest.data.active_workshops} active`}
              />
              <StatCard label="Artisans" value={manifest.data.total_artisans} />
              <StatCard label="Contributions" value={manifest.data.total_contributions} />
              <StatCard
                label="Exhibitions"
                value={manifest.data.total_exhibitions}
                subValue={`${manifest.data.open_exhibitions} open`}
              />
              <StatCard label="Storage" value={manifest.data.storage_backend} isText />
            </div>
          </div>
        )}

        {/* Workshops View */}
        {!isLoading && !error && view === 'workshops' && (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-medium text-stone-700">Workshops</h2>
              <span className="text-sm text-stone-400">{workshops.data?.count ?? 0} total</span>
            </div>
            {workshops.data?.workshops.length === 0 && (
              <EmptyState message="No workshops yet. Create one to get started." />
            )}
            <div className="grid gap-4 md:grid-cols-2">
              {workshops.data?.workshops.map((workshop) => (
                <WorkshopCard
                  key={workshop.id}
                  workshop={workshop}
                  onClick={() => selectWorkshop(workshop.id)}
                />
              ))}
            </div>
          </div>
        )}

        {/* Artisans View */}
        {!isLoading && !error && view === 'artisans' && (
          <div className="space-y-6">
            {selectedWorkshopId ? (
              <>
                <div className="flex items-center justify-between">
                  <div>
                    <button
                      onClick={() => {
                        setSelectedWorkshopId(null);
                        setView('workshops');
                      }}
                      className="text-sm text-stone-400 hover:text-stone-600 flex items-center gap-1 mb-2"
                    >
                      <span>&larr;</span> Back to workshops
                    </button>
                    <h2 className="text-lg font-medium text-stone-700">Artisans</h2>
                  </div>
                  <span className="text-sm text-stone-400">
                    {artisans.data?.count ?? 0} in workshop
                  </span>
                </div>
                {artisans.isLoading && <LoadingPanel message="Loading artisans..." />}
                {!artisans.isLoading && artisans.data?.artisans.length === 0 && (
                  <EmptyState message="No artisans in this workshop yet." />
                )}
                <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                  {artisans.data?.artisans.map((artisan) => (
                    <ArtisanCard key={artisan.id} artisan={artisan} />
                  ))}
                </div>
              </>
            ) : (
              <EmptyState message="Select a workshop first to view its artisans." />
            )}
          </div>
        )}

        {/* Contributions View */}
        {!isLoading && !error && view === 'contributions' && (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-medium text-stone-700">Recent Works</h2>
              <span className="text-sm text-stone-400">
                {contributions.data?.count ?? 0} contributions
              </span>
            </div>
            {contributions.isLoading && <LoadingPanel message="Loading works..." />}
            {!contributions.isLoading && contributions.data?.contributions.length === 0 && (
              <EmptyState message="No contributions yet. Artisans are waiting for commissions." />
            )}
            <div className="grid gap-4">
              {contributions.data?.contributions.map((contribution) => (
                <ContributionCard key={contribution.id} contribution={contribution} />
              ))}
            </div>
          </div>
        )}
      </main>

      {/* Footer - minimal */}
      <footer className="border-t border-stone-100 bg-white mt-16">
        <div className={`${maxWidth} mx-auto ${containerPadding} text-center`}>
          <p className="text-xs text-stone-300">Metaphysical Forge</p>
        </div>
      </footer>
    </div>
  );
}

// =============================================================================
// Helper Components
// =============================================================================

interface StatCardProps {
  label: string;
  value: number | string;
  subValue?: string;
  isText?: boolean;
}

function StatCard({ label, value, subValue, isText }: StatCardProps) {
  return (
    <div className="bg-white rounded-lg border border-stone-200 p-4">
      <div className="text-sm text-stone-500">{label}</div>
      <div className={`mt-1 ${isText ? 'text-lg' : 'text-2xl'} font-medium text-stone-800`}>
        {value}
      </div>
      {subValue && <div className="text-xs text-stone-400 mt-1">{subValue}</div>}
    </div>
  );
}

interface EmptyStateProps {
  message: string;
}

function EmptyState({ message }: EmptyStateProps) {
  return (
    <div className="text-center py-12">
      <p className="text-stone-400">{message}</p>
    </div>
  );
}

interface WorkshopCardProps {
  workshop: WorldForgeWorkshopListResponse['workshops'][0];
  onClick: () => void;
}

function WorkshopCard({ workshop, onClick }: WorkshopCardProps) {
  return (
    <button
      onClick={onClick}
      className="text-left bg-white rounded-lg border border-stone-200 p-4 hover:border-amber-300 transition-colors"
    >
      <div className="flex items-center justify-between">
        <h3 className="font-medium text-stone-800">{workshop.name}</h3>
        {workshop.is_active && (
          <span className="px-2 py-0.5 text-xs bg-green-100 text-green-700 rounded-full">
            Active
          </span>
        )}
      </div>
      {workshop.description && (
        <p className="mt-1 text-sm text-stone-500 line-clamp-2">{workshop.description}</p>
      )}
      <div className="mt-3 flex items-center gap-4 text-xs text-stone-400">
        <span>{workshop.artisan_count} artisans</span>
        <span>{workshop.contribution_count} works</span>
      </div>
    </button>
  );
}

interface ArtisanCardProps {
  artisan: WorldForgeArtisanListResponse['artisans'][0];
}

function ArtisanCard({ artisan }: ArtisanCardProps) {
  return (
    <div className="bg-white rounded-lg border border-stone-200 p-4">
      <div className="flex items-center justify-between">
        <h3 className="font-medium text-stone-800">{artisan.name}</h3>
        {artisan.is_active && <span className="w-2 h-2 bg-green-400 rounded-full" title="Active" />}
      </div>
      <p className="mt-1 text-sm text-amber-600">{artisan.specialty}</p>
      {artisan.style && <p className="mt-1 text-xs text-stone-400">{artisan.style}</p>}
      <div className="mt-3 text-xs text-stone-400">{artisan.contribution_count} contributions</div>
    </div>
  );
}

interface ContributionCardProps {
  contribution: WorldForgeContributionListResponse['contributions'][0];
}

function ContributionCard({ contribution }: ContributionCardProps) {
  return (
    <div className="bg-white rounded-lg border border-stone-200 p-4">
      <div className="flex items-center justify-between mb-2">
        <span className="text-sm font-medium text-stone-700">{contribution.artisan_name}</span>
        <span className="text-xs text-stone-400">{contribution.contribution_type}</span>
      </div>
      <p className="text-stone-600 text-sm line-clamp-3">{contribution.content}</p>
      {contribution.prompt && (
        <p className="mt-2 text-xs text-stone-400 italic">Prompt: {contribution.prompt}</p>
      )}
    </div>
  );
}

export default ForgeVisualization;
