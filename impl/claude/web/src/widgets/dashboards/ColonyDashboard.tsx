/**
 * ColonyDashboard: Agent Town colony overview dashboard.
 *
 * Displays:
 * - Header with phase and day
 * - Status bar with colony metrics
 * - Citizen grid
 * - Footer with entropy and token counts
 */

import { memo, useMemo } from 'react';
import type { ColonyDashboardJSON, CitizenCardJSON } from '@/reactive/types';
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
  grid_cols,
  selected_citizen_id,
  onSelectCitizen,
  className,
}: ColonyDashboardProps) {
  // Build grid rows
  const rows = useMemo(() => {
    const result: CitizenCardJSON[][] = [];
    for (let i = 0; i < citizens.length; i += grid_cols) {
      result.push(citizens.slice(i, i + grid_cols));
    }
    return result;
  }, [citizens, grid_cols]);

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
      <div className="flex gap-4 px-4 py-2 bg-gray-100 text-sm border-b">
        <span>
          <strong>Colony:</strong> {colony_id.slice(0, 12)}
        </span>
        <span>
          <strong>Citizens:</strong> {citizens.length}
        </span>
        <span>
          <strong>Events:</strong> {metrics.total_events}
        </span>
      </div>

      {/* Citizen grid */}
      <div className="p-4">
        <div className="flex flex-col gap-4">
          {rows.map((row, rowIdx) => (
            <div key={rowIdx} className="flex gap-4">
              {row.map((citizen) => (
                <CitizenCard
                  key={citizen.citizen_id}
                  {...citizen}
                  onSelect={onSelectCitizen}
                  isSelected={citizen.citizen_id === selected_citizen_id}
                />
              ))}
            </div>
          ))}
        </div>
      </div>

      {/* Footer */}
      <div className="flex justify-between px-4 py-2 bg-gray-100 text-sm border-t">
        <span>Entropy: {metrics.entropy_budget.toFixed(2)}</span>
        <span>Tokens: {metrics.total_tokens}</span>
      </div>
    </div>
  );
});

export default ColonyDashboard;
