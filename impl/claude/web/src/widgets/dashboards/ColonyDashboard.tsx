/**
 * ColonyDashboard: Agent Town colony overview dashboard.
 *
 * Displays:
 * - Header with phase and day
 * - Status bar with colony metrics
 * - Citizen grid (using ElasticContainer)
 * - Footer with entropy and token counts
 *
 * Now with elastic layout - citizens auto-arrange based on viewport.
 * @see plans/web-refactor/elastic-primitives.md
 */

import { memo } from 'react';
import type { ColonyDashboardJSON } from '@/reactive/types';
import { ElasticContainer, ElasticPlaceholder } from '@/components/elastic';
import { CitizenCard } from '../cards';

export interface ColonyDashboardProps extends Omit<ColonyDashboardJSON, 'type'> {
  onSelectCitizen?: (id: string) => void;
  className?: string;
}

export const ColonyDashboard = memo(function ColonyDashboard({
  colony_id,
  phase,
  day,
  metrics,
  citizens,
  selected_citizen_id,
  onSelectCitizen,
  className,
}: ColonyDashboardProps) {
  // Defensive defaults for metrics (SSE stream may not include all fields)
  const safeMetrics = {
    total_events: metrics?.total_events ?? 0,
    entropy_budget: metrics?.entropy_budget ?? 0,
    total_tokens: metrics?.total_tokens ?? 0,
  };

  return (
    <div
      className={`kgents-colony-dashboard border rounded-lg overflow-hidden ${className || ''}`}
      data-colony-id={colony_id}
    >
      {/* Header */}
      <div className="flex justify-between items-center px-4 py-3 bg-gray-900 text-white">
        <span className="font-bold">AGENT TOWN DASHBOARD</span>
        <span className="text-gray-400">
          {phase} · Day {day}
        </span>
      </div>

      {/* Status bar */}
      <div className="flex flex-wrap gap-x-4 gap-y-1 px-4 py-2 bg-gray-100 text-sm border-b">
        <span>
          <strong>Colony:</strong> {colony_id?.slice(0, 12) ?? 'unknown'}
        </span>
        <span>
          <strong>Citizens:</strong> {citizens?.length ?? 0}
        </span>
        <span>
          <strong>Events:</strong> {safeMetrics.total_events}
        </span>
      </div>

      {/* Citizen grid using ElasticContainer */}
      <ElasticContainer
        layout="grid"
        gap={{ sm: 'var(--elastic-gap-sm)', md: 'var(--elastic-gap-md)', lg: 'var(--elastic-gap-lg)' }}
        padding={{ sm: 'var(--elastic-gap-sm)', md: 'var(--elastic-gap-md)' }}
        transition="smooth"
        minItemWidth={200}
        emptyState={
          <ElasticPlaceholder
            for="agent"
            state="empty"
            emptyMessage="No citizens in this colony yet"
          />
        }
        className="min-h-[200px]"
      >
        {(citizens ?? []).map((citizen) => (
          <CitizenCard
            key={citizen.citizen_id}
            {...citizen}
            onSelect={onSelectCitizen}
            isSelected={citizen.citizen_id === selected_citizen_id}
          />
        ))}
      </ElasticContainer>

      {/* Footer */}
      <div className="flex justify-between flex-wrap gap-x-4 px-4 py-2 bg-gray-100 text-sm border-t">
        <span>Entropy: {safeMetrics.entropy_budget.toFixed(2)}</span>
        <span>Tokens: {safeMetrics.total_tokens}</span>
      </div>
    </div>
  );
});

export default ColonyDashboard;
