/**
 * PilotSelector
 *
 * Displays available pilots as cards with status, description, and launch action.
 * Uses GrowingContainer for entrance animations.
 */

import { Link } from 'react-router-dom';
import { GrowingContainer } from '@kgents/shared-primitives';
import { usePilots } from '../hooks';
import { useLayout } from './LayoutProvider';
import type { PilotManifest } from '../api/pilots';

// =============================================================================
// Joy Dimension Styles
// =============================================================================

const JOY_BADGE_STYLES: Record<string, string> = {
  FLOW: 'bg-blue-500/20 text-blue-400',
  WARMTH: 'bg-orange-500/20 text-orange-400',
  SURPRISE: 'bg-purple-500/20 text-purple-400',
};

// =============================================================================
// Icons
// =============================================================================

function ActiveIcon({ className }: { className?: string }) {
  return (
    <svg
      className={className}
      fill="none"
      viewBox="0 0 24 24"
      stroke="currentColor"
      strokeWidth={2}
    >
      <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
    </svg>
  );
}

function ClockIcon({ className }: { className?: string }) {
  return (
    <svg
      className={className}
      fill="none"
      viewBox="0 0 24 24"
      stroke="currentColor"
      strokeWidth={2}
    >
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
      />
    </svg>
  );
}

function FlaskIcon({ className }: { className?: string }) {
  return (
    <svg
      className={className}
      fill="none"
      viewBox="0 0 24 24"
      stroke="currentColor"
      strokeWidth={2}
    >
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z"
      />
    </svg>
  );
}

function ArrowIcon({ className }: { className?: string }) {
  return (
    <svg
      className={className}
      fill="none"
      viewBox="0 0 24 24"
      stroke="currentColor"
      strokeWidth={2}
    >
      <path strokeLinecap="round" strokeLinejoin="round" d="M13 7l5 5m0 0l-5 5m5-5H6" />
    </svg>
  );
}

// =============================================================================
// Loading Skeleton
// =============================================================================

function PilotCardSkeleton() {
  return (
    <div className="rounded-xl border border-clay/20 p-5 md:p-6 animate-pulse">
      <div className="flex items-start justify-between mb-4">
        <div className="h-6 w-32 bg-clay/20 rounded" />
        <div className="h-5 w-20 bg-clay/20 rounded-full" />
      </div>
      <div className="space-y-2 mb-4">
        <div className="h-4 w-full bg-clay/20 rounded" />
        <div className="h-4 w-3/4 bg-clay/20 rounded" />
      </div>
      <div className="flex items-center justify-between">
        <div className="h-5 w-16 bg-clay/20 rounded-full" />
        <div className="h-4 w-16 bg-clay/20 rounded" />
      </div>
    </div>
  );
}

// =============================================================================
// Error State
// =============================================================================

function ErrorState({ error, onRetry }: { error: string; onRetry: () => void }) {
  return (
    <div className="flex flex-col items-center justify-center py-12 space-y-4">
      <div className="text-rust text-lg font-medium">Failed to load pilots</div>
      <p className="text-sand/70 text-sm max-w-md text-center">{error}</p>
      <button
        onClick={onRetry}
        className="px-4 py-2 bg-sage/20 text-sage rounded-lg hover:bg-sage/30 transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-sage/40"
      >
        Try Again
      </button>
    </div>
  );
}

// =============================================================================
// Section Header
// =============================================================================

function SectionHeader({ title, count, delay = 0 }: { title: string; count: number; delay?: number }) {
  return (
    <GrowingContainer autoTrigger duration="quick" delay={delay}>
      <div className="flex items-center gap-3 mb-4">
        <h2 className="text-lg font-medium text-lantern">{title}</h2>
        <span className="text-xs bg-clay/20 text-clay px-2 py-0.5 rounded-full">
          {count}
        </span>
      </div>
    </GrowingContainer>
  );
}

// =============================================================================
// Pilot Card
// =============================================================================

interface PilotCardProps {
  pilot: PilotManifest;
}

function PilotCard({ pilot }: PilotCardProps) {
  const isActive = pilot.status === 'active';
  const isExperimental = pilot.status === 'experimental';
  const joyBadgeStyle = JOY_BADGE_STYLES[pilot.joy_dimension] || 'bg-clay/20 text-clay';

  // Get status icon and label
  const getStatusInfo = () => {
    if (isActive) {
      return { icon: <ActiveIcon className="w-3 h-3" />, label: 'Active', style: 'bg-sage/20 text-sage' };
    }
    if (isExperimental) {
      return { icon: <FlaskIcon className="w-3 h-3" />, label: 'Experimental', style: 'bg-amber/20 text-amber' };
    }
    return { icon: <ClockIcon className="w-3 h-3" />, label: 'Coming Soon', style: 'bg-clay/20 text-clay' };
  };

  const statusInfo = getStatusInfo();

  return (
    <div
      className={`
        group relative rounded-xl border p-5 md:p-6
        transition-all duration-200 ease-out
        ${isActive
          ? 'border-sage/30 hover:border-amber hover:shadow-lg hover:shadow-amber/10 hover:-translate-y-1 cursor-pointer'
          : isExperimental
          ? 'border-amber/30 opacity-80'
          : 'border-clay/20 opacity-60'
        }
      `}
    >
      {/* Hover glow effect for active pilots */}
      {isActive && (
        <div className="absolute inset-0 rounded-xl bg-gradient-to-br from-amber/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none" />
      )}

      {/* Header */}
      <div className="flex items-start justify-between mb-3 md:mb-4 relative">
        <h3 className={`text-lg md:text-xl font-semibold text-lantern transition-colors duration-200 ${isActive ? 'group-hover:text-amber' : ''}`}>
          {pilot.name}
        </h3>
        <span
          className={`inline-flex items-center gap-1 text-xs px-2.5 py-1 rounded-full font-medium ${statusInfo.style}`}
        >
          {statusInfo.icon}
          {statusInfo.label}
        </span>
      </div>

      {/* Description */}
      <p className="text-sand text-sm md:text-base mb-4 relative">
        {pilot.description}
      </p>

      {/* Footer */}
      <div className="flex items-center justify-between relative">
        <span className={`text-xs px-2 py-1 rounded-full ${joyBadgeStyle}`}>
          {pilot.joy_dimension}
        </span>
        {isActive && (
          <Link
            to={pilot.route}
            className="inline-flex items-center gap-1.5 text-amber font-medium text-sm hover:text-amber/80 transition-all duration-200 group/link"
          >
            Launch
            <ArrowIcon className="w-4 h-4 transform group-hover/link:translate-x-1 transition-transform duration-200" />
          </Link>
        )}
      </div>
    </div>
  );
}

// =============================================================================
// Main Component
// =============================================================================

export function PilotSelector() {
  const { pilots, loading, error, refresh, usingFallback } = usePilots();
  const { density } = useLayout();

  // Group pilots by status
  const activePilots = pilots.filter((p) => p.status === 'active');
  const comingSoonPilots = pilots.filter((p) => p.status === 'coming_soon');
  const experimentalPilots = pilots.filter((p) => p.status === 'experimental');

  // Responsive grid columns
  const gridCols =
    density === 'compact'
      ? 'grid-cols-1'
      : density === 'comfortable'
      ? 'grid-cols-1 md:grid-cols-2'
      : 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3';

  // Loading state
  if (loading && pilots.length === 0) {
    return (
      <div className="space-y-6 md:space-y-8">
        <div className="text-center">
          <h1 className="text-2xl md:text-3xl font-bold text-lantern mb-2">
            Choose Your Pilot
          </h1>
          <p className="text-sand">Loading available pilots...</p>
        </div>
        <div className={`grid gap-4 md:gap-6 ${gridCols}`}>
          {[1, 2, 3].map((i) => (
            <PilotCardSkeleton key={i} />
          ))}
        </div>
      </div>
    );
  }

  // Error state (only if no pilots at all)
  if (error && pilots.length === 0) {
    return (
      <div className="space-y-6 md:space-y-8">
        <div className="text-center">
          <h1 className="text-2xl md:text-3xl font-bold text-lantern mb-2">
            Choose Your Pilot
          </h1>
        </div>
        <ErrorState error={error} onRetry={refresh} />
      </div>
    );
  }

  // Calculate stagger delays for each section
  let cardIndex = 0;
  const getCardDelay = () => {
    const delay = 150 + cardIndex * 60;
    cardIndex++;
    return delay;
  };

  return (
    <div className="space-y-6 md:space-y-8">
      {/* Header */}
      <div className="text-center">
        <GrowingContainer autoTrigger duration="normal">
          <h1 className="text-2xl md:text-3xl font-bold text-lantern mb-2">
            Choose Your Pilot
          </h1>
        </GrowingContainer>
        <GrowingContainer autoTrigger duration="normal" delay={50}>
          <p className="text-sand">
            Each pilot is a unique experience built on kgents primitives.
          </p>
        </GrowingContainer>
        {usingFallback && (
          <GrowingContainer autoTrigger duration="quick" delay={100}>
            <p className="text-amber/70 text-sm mt-2">
              Using cached pilot data.{' '}
              <button
                onClick={refresh}
                className="underline hover:no-underline focus:outline-none focus:ring-1 focus:ring-amber/40 rounded"
              >
                Refresh
              </button>
            </p>
          </GrowingContainer>
        )}
      </div>

      {/* Active Pilots */}
      {activePilots.length > 0 && (
        <section>
          <SectionHeader title="Ready to Launch" count={activePilots.length} delay={100} />
          <div className={`grid gap-4 md:gap-6 ${gridCols}`}>
            {activePilots.map((pilot) => (
              <GrowingContainer key={pilot.id} autoTrigger duration="normal" delay={getCardDelay()}>
                <PilotCard pilot={pilot} />
              </GrowingContainer>
            ))}
          </div>
        </section>
      )}

      {/* Coming Soon Pilots */}
      {comingSoonPilots.length > 0 && (
        <section>
          <SectionHeader title="Coming Soon" count={comingSoonPilots.length} delay={100 + activePilots.length * 60} />
          <div className={`grid gap-4 md:gap-6 ${gridCols}`}>
            {comingSoonPilots.map((pilot) => (
              <GrowingContainer key={pilot.id} autoTrigger duration="normal" delay={getCardDelay()}>
                <PilotCard pilot={pilot} />
              </GrowingContainer>
            ))}
          </div>
        </section>
      )}

      {/* Experimental Pilots */}
      {experimentalPilots.length > 0 && (
        <section>
          <SectionHeader
            title="Experimental"
            count={experimentalPilots.length}
            delay={100 + (activePilots.length + comingSoonPilots.length) * 60}
          />
          <div className={`grid gap-4 md:gap-6 ${gridCols}`}>
            {experimentalPilots.map((pilot) => (
              <GrowingContainer key={pilot.id} autoTrigger duration="normal" delay={getCardDelay()}>
                <PilotCard pilot={pilot} />
              </GrowingContainer>
            ))}
          </div>
        </section>
      )}
    </div>
  );
}

export default PilotSelector;
