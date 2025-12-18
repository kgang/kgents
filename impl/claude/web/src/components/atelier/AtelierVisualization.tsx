/**
 * AtelierVisualization - The complete Atelier visualization canvas
 *
 * PROJECTION-FIRST REFACTOR (OS Shell Phase: refactor-atelier)
 *
 * This component contains ALL the visualization and control logic
 * extracted from the original Atelier.tsx page. It receives status
 * data from PathProjection and handles:
 *
 * - Multi-view navigation (Gallery, Commission, Collaborate)
 * - Artisan selection and commissioning
 * - Piece detail with provenance
 * - Lineage tree visualization
 * - Streaming commission progress
 * - Mobile/tablet/desktop layouts
 *
 * Design: This component is the "heavy lifting" that enables the
 * Atelier page itself to be projection-first (<50 LOC).
 *
 * @see spec/protocols/os-shell.md - Part III: Projection-First Rendering
 * @see docs/skills/crown-jewel-patterns.md
 */

import { useState, useCallback, useEffect } from 'react';
import { Palette, Users, Brush, Image, Radio, Eye, EyeOff, Zap } from 'lucide-react';
import {
  useAtelierManifest,
  useWorkshops,
  useArtisans,
  useContributions,
  type WorldAtelierWorkshopListResponse,
  type WorldAtelierArtisanListResponse,
  type WorldAtelierContributionListResponse,
} from '@/hooks/useAtelierQuery';
import {
  ErrorPanel,
  LoadingPanel,
  FishbowlCanvas,
  SpectatorOverlay,
  TokenBalanceWidget,
  TokenFlowIndicator,
  SpendHistoryPanel,
  BidQueuePanel,
  BidSubmitModal,
  type Bid,
  type TokenFlowEvent,
} from '@/components/atelier';
import { useAtelierStream } from '@/hooks/useAtelierStream';
import { useTokenBalance } from '@/hooks/useTokenBalance';
import { cn } from '@/lib/utils';
import type { Density } from '@/shell/types';

// =============================================================================
// Types
// =============================================================================

export interface AtelierVisualizationProps {
  /** Initial status data from PathProjection */
  status: AtelierStatusData | null;
  /** Current layout density */
  density: Density;
  /** Layout helpers */
  isMobile: boolean;
  isTablet: boolean;
  isDesktop: boolean;
  /** Refetch function from PathProjection */
  refetch: () => void;
}

/** Status data from world.atelier.manifest */
export interface AtelierStatusData {
  total_workshops?: number;
  active_workshops?: number;
  total_artisans?: number;
  total_contributions?: number;
  total_exhibitions?: number;
  open_exhibitions?: number;
  status?: string;
}

type View = 'overview' | 'workshops' | 'artisans' | 'contributions' | 'fishbowl';

/** Live session summary for session selector */
interface LiveSession {
  id: string;
  artisanId?: string;
  artisanName?: string;
  isLive: boolean;
  spectatorCount: number;
}

// =============================================================================
// Component
// =============================================================================

export function AtelierVisualization({
  status: _status, // Workshop status from manifest (available for future use)
  density: _density, // Layout density (available for future density-adaptive features)
  isMobile,
  isTablet: _isTablet, // Available for future tablet-specific layouts
  isDesktop: _isDesktop, // Available for future desktop-specific layouts
  refetch: _refetch, // Available for manual refresh
}: AtelierVisualizationProps) {
  // Navigation state
  const [view, setView] = useState<View>('overview');
  const [selectedWorkshopId, setSelectedWorkshopId] = useState<string | null>(null);

  // Fishbowl state (Phase 2: Live sessions)
  const [showSpectatorCursors, setShowSpectatorCursors] = useState(true);
  const [activeSessionId, setActiveSessionId] = useState<string | null>(null);
  const [showBidModal, setShowBidModal] = useState(false);
  const [showSpendHistory, setShowSpendHistory] = useState(false);

  // Token economy state (Phase 2: Chunk 3)
  const tokenBalance = useTokenBalance('demo-spectator-1');
  const [tokenFlowEvents, setTokenFlowEvents] = useState<TokenFlowEvent[]>([]);
  const [bids, setBids] = useState<Bid[]>([]);
  const [recentTokenChange, setRecentTokenChange] = useState<{
    amount: number;
    direction: 'in' | 'out';
  } | undefined>();

  // Live session streaming hook
  const stream = useAtelierStream();

  // Demo live sessions (in production, these would come from an API)
  const [liveSessions] = useState<LiveSession[]>([
    { id: 'demo-session-1', artisanName: 'Calligrapher', isLive: true, spectatorCount: 3 },
    { id: 'demo-session-2', artisanName: 'Poet', isLive: false, spectatorCount: 0 },
  ]);

  // Subscribe to active session when selected
  useEffect(() => {
    if (activeSessionId && view === 'fishbowl') {
      stream.subscribeToSession(activeSessionId);
    }
    return () => {
      stream.unsubscribeFromSession();
    };
  }, [activeSessionId, view]);

  // AGENTESE hooks - contract-driven data fetching
  const manifest = useAtelierManifest();
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

  // Handle bid submission
  const handleBidSubmit = useCallback(async (bid: { bidType: string; content: string; tokenCost: number }) => {
    // Optimistic spend
    const result = await tokenBalance.spend(bid.tokenCost, `Bid: ${bid.bidType}`);

    if (result !== null) {
      // Create new bid
      const newBid: Bid = {
        id: `bid-${Date.now()}`,
        spectatorId: 'demo-spectator-1',
        spectatorName: 'You',
        bidType: bid.bidType as Bid['bidType'],
        content: bid.content,
        tokenCost: bid.tokenCost,
        submittedAt: new Date().toISOString(),
        status: 'pending',
      };

      setBids((prev) => [newBid, ...prev]);
      setShowBidModal(false);

      // Track token flow
      setTokenFlowEvents((prev) => [
        ...prev,
        {
          id: `flow-${Date.now()}`,
          amount: bid.tokenCost,
          direction: 'out',
          timestamp: new Date().toISOString(),
        },
      ]);

      // Update recent change indicator
      setRecentTokenChange({ amount: bid.tokenCost, direction: 'out' });
      setTimeout(() => setRecentTokenChange(undefined), 3000);
    }
  }, [tokenBalance]);

  // Handle bid acceptance (demo: auto-accept after delay)
  const handleBidAccept = useCallback((bidId: string) => {
    setBids((prev) =>
      prev.map((bid) =>
        bid.id === bidId ? { ...bid, status: 'accepted' as const } : bid
      )
    );
  }, []);

  // Handle bid rejection
  const handleBidReject = useCallback((bidId: string) => {
    const bid = bids.find((b) => b.id === bidId);

    if (bid) {
      // Refund tokens
      tokenBalance.earn(bid.tokenCost, 'Bid refund');

      setBids((prev) =>
        prev.map((b) =>
          b.id === bidId ? { ...b, status: 'rejected' as const } : b
        )
      );

      // Track refund flow
      setTokenFlowEvents((prev) => [
        ...prev,
        {
          id: `flow-refund-${Date.now()}`,
          amount: bid.tokenCost,
          direction: 'in',
          timestamp: new Date().toISOString(),
        },
      ]);

      setRecentTokenChange({ amount: bid.tokenCost, direction: 'in' });
      setTimeout(() => setRecentTokenChange(undefined), 3000);
    }
  }, [bids, tokenBalance]);

  // Navigation tabs
  const tabs: Array<{ key: View; label: string; icon: typeof Palette }> = [
    { key: 'overview', label: 'Overview', icon: Palette },
    { key: 'fishbowl', label: 'Live', icon: Radio },
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
            <div>
              <h1 className={`${titleSize} font-serif text-stone-800 flex items-center gap-2`}>
                <Palette className="w-5 h-5 text-amber-500" />
                Tiny Atelier
              </h1>
              <p className="mt-1 text-sm text-stone-400">A workshop of creative artisans</p>
            </div>

            {/* Token Balance Widget */}
            <TokenBalanceWidget
              balance={tokenBalance.balance}
              recentChange={recentTokenChange}
              variant="compact"
              isConnected={tokenBalance.isConnected}
              onClick={() => setShowSpendHistory(!showSpendHistory)}
            />
          </div>

          {/* Spend History Panel (collapsible) */}
          {showSpendHistory && (
            <div className="mt-4">
              <SpendHistoryPanel
                transactions={tokenBalance.recentTransactions}
                currentBalance={tokenBalance.balance}
                initialCollapsed={false}
              />
            </div>
          )}
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
                  className={`
                    px-4 py-3 text-sm font-medium transition-colors whitespace-nowrap
                    border-b-2 -mb-px flex items-center gap-2
                    ${
                      view === tab.key
                        ? 'border-amber-400 text-amber-700'
                        : 'border-transparent text-stone-500 hover:text-stone-700'
                    }
                  `}
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
        {error && (
          <ErrorPanel
            title="Unable to load workshop"
            message={error}
            onRetry={handleRetry}
          />
        )}

        {/* Global Loading State */}
        {isLoading && !error && <LoadingPanel message="Preparing the workshop..." />}

        {/* Overview View - Manifest Stats */}
        {!isLoading && !error && view === 'overview' && manifest.data && (
          <div className="space-y-6">
            <h2 className="text-lg font-medium text-stone-700">Workshop Overview</h2>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
              <StatCard
                label="Workshops"
                value={manifest.data.total_workshops}
                subValue={`${manifest.data.active_workshops} active`}
              />
              <StatCard
                label="Artisans"
                value={manifest.data.total_artisans}
              />
              <StatCard
                label="Contributions"
                value={manifest.data.total_contributions}
              />
              <StatCard
                label="Exhibitions"
                value={manifest.data.total_exhibitions}
                subValue={`${manifest.data.open_exhibitions} open`}
              />
              <StatCard
                label="Storage"
                value={manifest.data.storage_backend}
                isText
              />
            </div>
          </div>
        )}

        {/* Fishbowl View - Live Creation Stream */}
        {view === 'fishbowl' && (
          <div className="space-y-6">
            {/* Header with session selector and cursor toggle */}
            <div className="flex items-center justify-between flex-wrap gap-4">
              <div>
                <h2 className="text-lg font-medium text-stone-700">Live Creation</h2>
                <p className="text-sm text-stone-400">Watch artisans create in real-time</p>
              </div>

              <div className="flex items-center gap-3">
                {/* Submit Bid button */}
                {activeSessionId && (
                  <button
                    onClick={() => setShowBidModal(true)}
                    className={cn(
                      'flex items-center gap-2 px-3 py-1.5 rounded-full text-sm',
                      'bg-amber-500 text-white hover:bg-amber-600 transition-colors'
                    )}
                  >
                    <Zap className="w-4 h-4" />
                    Place Bid
                  </button>
                )}

                {/* Cursor toggle */}
                <button
                  onClick={() => setShowSpectatorCursors(!showSpectatorCursors)}
                  className={cn(
                    'flex items-center gap-2 px-3 py-1.5 rounded-full text-sm',
                    'transition-colors border',
                    showSpectatorCursors
                      ? 'bg-amber-100 text-amber-700 border-amber-200'
                      : 'bg-stone-100 text-stone-500 border-stone-200'
                  )}
                  aria-pressed={showSpectatorCursors}
                >
                  {showSpectatorCursors ? (
                    <>
                      <Eye className="w-4 h-4" />
                      Cursors On
                    </>
                  ) : (
                    <>
                      <EyeOff className="w-4 h-4" />
                      Cursors Off
                    </>
                  )}
                </button>
              </div>
            </div>

            {/* Session Selector */}
            <SessionSelector
              sessions={liveSessions}
              activeSessionId={activeSessionId}
              onSelect={(id) => setActiveSessionId(id)}
            />

            {/* Main Fishbowl Layout: Canvas + Sidebar */}
            <div className={cn('grid gap-6', isMobile ? 'grid-cols-1' : 'grid-cols-[1fr,300px]')}>
              {/* FishbowlCanvas with TokenFlowIndicator */}
              <div className="relative">
                {activeSessionId ? (
                  <>
                    <FishbowlCanvas
                      sessionId={activeSessionId}
                      artisan={
                        liveSessions.find((s) => s.id === activeSessionId)
                          ? {
                              id: activeSessionId,
                              name: liveSessions.find((s) => s.id === activeSessionId)?.artisanName || 'Artisan',
                              specialty: 'Creating',
                              is_active: true,
                            }
                          : null
                      }
                      isLive={stream.isSessionLive}
                      content={stream.sessionState?.content || ''}
                      contentType={stream.sessionState?.contentType || 'text'}
                      spectatorCount={stream.sessionState?.spectatorCount || 0}
                      spectatorCursors={stream.spectatorCursors}
                      showCursors={showSpectatorCursors}
                      onCanvasClick={(pos) => stream.updateCursor(pos)}
                      className="min-h-[400px]"
                    />

                    {/* Token Flow Indicator (overlay on canvas) */}
                    <TokenFlowIndicator
                      events={tokenFlowEvents}
                      position="bottom"
                      canvasWidth={600}
                      canvasHeight={400}
                      enabled={true}
                    />
                  </>
                ) : (
                  <div className="bg-stone-100 rounded-xl border border-stone-200 p-12 text-center">
                    <Radio className="w-8 h-8 text-stone-300 mx-auto mb-4" />
                    <p className="text-stone-500">Select a session above to watch live creation</p>
                  </div>
                )}

                {/* Spectator Overlay (separate from canvas for flexibility) */}
                {activeSessionId && showSpectatorCursors && (
                  <div className="relative">
                    <SpectatorOverlay
                      spectators={stream.spectatorCursors}
                      showCursors={showSpectatorCursors}
                      eigenvectorColors={true}
                      showNames={true}
                    />
                  </div>
                )}
              </div>

              {/* Bid Queue Sidebar */}
              {activeSessionId && !isMobile && (
                <BidQueuePanel
                  bids={bids}
                  isCreator={false} // Spectator view
                  onAccept={handleBidAccept}
                  onReject={handleBidReject}
                  tokenBalance={tokenBalance.balance}
                />
              )}
            </div>

            {/* Mobile: Bid Queue below canvas */}
            {activeSessionId && isMobile && (
              <BidQueuePanel
                bids={bids}
                isCreator={false}
                onAccept={handleBidAccept}
                onReject={handleBidReject}
                tokenBalance={tokenBalance.balance}
              />
            )}
          </div>
        )}

        {/* Bid Submit Modal */}
        <BidSubmitModal
          isOpen={showBidModal}
          onClose={() => setShowBidModal(false)}
          onSubmit={handleBidSubmit}
          tokenBalance={tokenBalance.balance}
        />

        {/* Workshops View */}
        {!isLoading && !error && view === 'workshops' && (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-medium text-stone-700">Workshops</h2>
              <span className="text-sm text-stone-400">
                {workshops.data?.count ?? 0} total
              </span>
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
              <EmptyState message="No contributions yet. Artisans are waiting for inspiration." />
            )}
            <div className="grid gap-4">
              {contributions.data?.contributions.map((contribution) => (
                <ContributionCard key={contribution.id} contribution={contribution} />
              ))}
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-stone-100 bg-white mt-16">
        <div className={`${maxWidth} mx-auto ${containerPadding} text-center`}>
          <p className="text-xs text-stone-300">Tiny Atelier - A kgents demo</p>
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

// Session Selector for Fishbowl view
interface SessionSelectorProps {
  sessions: LiveSession[];
  activeSessionId: string | null;
  onSelect: (sessionId: string) => void;
}

function SessionSelector({ sessions, activeSessionId, onSelect }: SessionSelectorProps) {
  if (sessions.length === 0) {
    return (
      <div className="text-sm text-stone-400 italic">
        No active sessions at the moment
      </div>
    );
  }

  return (
    <div className="flex gap-2 overflow-x-auto pb-2 -mx-1 px-1">
      {sessions.map((session) => (
        <button
          key={session.id}
          onClick={() => onSelect(session.id)}
          className={cn(
            'px-4 py-2 rounded-full text-sm whitespace-nowrap transition-all',
            'border flex items-center gap-2',
            activeSessionId === session.id
              ? 'bg-amber-100 text-amber-800 border-amber-300'
              : session.isLive
                ? 'bg-green-50 text-green-700 border-green-200 hover:bg-green-100'
                : 'bg-stone-50 text-stone-500 border-stone-200 hover:bg-stone-100'
          )}
        >
          {session.isLive && (
            <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
          )}
          <span className="font-medium">{session.artisanName || 'Unknown'}</span>
          {session.isLive && (
            <span className="text-xs opacity-75">
              {session.spectatorCount} watching
            </span>
          )}
        </button>
      ))}
    </div>
  );
}

interface WorkshopCardProps {
  workshop: WorldAtelierWorkshopListResponse['workshops'][0];
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
  artisan: WorldAtelierArtisanListResponse['artisans'][0];
}

function ArtisanCard({ artisan }: ArtisanCardProps) {
  return (
    <div className="bg-white rounded-lg border border-stone-200 p-4">
      <div className="flex items-center justify-between">
        <h3 className="font-medium text-stone-800">{artisan.name}</h3>
        {artisan.is_active && (
          <span className="w-2 h-2 bg-green-400 rounded-full" title="Active" />
        )}
      </div>
      <p className="mt-1 text-sm text-amber-600">{artisan.specialty}</p>
      {artisan.style && (
        <p className="mt-1 text-xs text-stone-400">{artisan.style}</p>
      )}
      <div className="mt-3 text-xs text-stone-400">
        {artisan.contribution_count} contributions
      </div>
    </div>
  );
}

interface ContributionCardProps {
  contribution: WorldAtelierContributionListResponse['contributions'][0];
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
        <p className="mt-2 text-xs text-stone-400 italic">
          Prompt: {contribution.prompt}
        </p>
      )}
    </div>
  );
}

export default AtelierVisualization;
