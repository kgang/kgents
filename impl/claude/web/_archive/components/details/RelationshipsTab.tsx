/**
 * RelationshipsTab: Relationship graph with other citizens.
 *
 * Shows connections, affinities, and coalition membership.
 */

import { useState, useMemo } from 'react';
import { cn } from '@/lib/utils';
import type { CitizenCardJSON } from '@/reactive/types';
import type { CitizenManifest } from '@/api/types';

export interface RelationshipsTabProps {
  citizen: CitizenCardJSON;
  manifest: CitizenManifest | null;
  expanded?: boolean;
}

type ViewMode = 'list' | 'graph';
type FilterType = 'all' | 'positive' | 'negative' | 'neutral';

export function RelationshipsTab({ citizen, manifest, expanded = false }: RelationshipsTabProps) {
  const [viewMode, setViewMode] = useState<ViewMode>('list');
  const [filter, setFilter] = useState<FilterType>('all');

  const relationships = manifest?.relationships ?? {};
  const entries = Object.entries(relationships);

  const filteredEntries = useMemo(() => {
    return entries.filter(([_, value]) => {
      if (filter === 'all') return true;
      if (filter === 'positive') return value > 0.1;
      if (filter === 'negative') return value < -0.1;
      return value >= -0.1 && value <= 0.1;
    });
  }, [entries, filter]);

  const stats = useMemo(() => {
    const positive = entries.filter(([_, v]) => v > 0.1).length;
    const negative = entries.filter(([_, v]) => v < -0.1).length;
    const neutral = entries.length - positive - negative;
    const avgStrength = entries.length > 0
      ? entries.reduce((sum, [_, v]) => sum + Math.abs(v), 0) / entries.length
      : 0;
    return { total: entries.length, positive, negative, neutral, avgStrength };
  }, [entries]);

  if (entries.length === 0) {
    return (
      <div className="text-center py-12 text-gray-500">
        <span className="text-4xl block mb-4">🤝</span>
        <p>No relationships recorded yet.</p>
        <p className="text-sm mt-2">Relationships form through interactions in town.</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Stats Summary */}
      <div className="grid grid-cols-4 gap-3">
        <StatBadge label="Total" value={stats.total} />
        <StatBadge label="Positive" value={stats.positive} color="text-green-400" />
        <StatBadge label="Negative" value={stats.negative} color="text-red-400" />
        <StatBadge label="Avg" value={stats.avgStrength.toFixed(2)} />
      </div>

      {/* Controls */}
      <div className="flex items-center justify-between">
        <FilterSelector value={filter} onChange={setFilter} />
        <ViewToggle value={viewMode} onChange={setViewMode} />
      </div>

      {/* Content */}
      {viewMode === 'list' ? (
        <RelationshipList
          relationships={filteredEntries}
          citizenName={citizen.name}
          expanded={expanded}
        />
      ) : (
        <RelationshipGraph
          relationships={filteredEntries}
          citizenName={citizen.name}
          expanded={expanded}
        />
      )}
    </div>
  );
}

// =============================================================================
// Controls
// =============================================================================

function FilterSelector({
  value,
  onChange,
}: {
  value: FilterType;
  onChange: (v: FilterType) => void;
}) {
  const options: { id: FilterType; label: string }[] = [
    { id: 'all', label: 'All' },
    { id: 'positive', label: '+' },
    { id: 'negative', label: '-' },
    { id: 'neutral', label: '~' },
  ];

  return (
    <div className="flex gap-1 bg-town-surface/30 rounded-lg p-1">
      {options.map((opt) => (
        <button
          key={opt.id}
          onClick={() => onChange(opt.id)}
          className={cn(
            'px-3 py-1 text-xs font-medium rounded transition-colors',
            value === opt.id ? 'bg-town-accent text-white' : 'text-gray-400 hover:text-white'
          )}
        >
          {opt.label}
        </button>
      ))}
    </div>
  );
}

function ViewToggle({
  value,
  onChange,
}: {
  value: ViewMode;
  onChange: (v: ViewMode) => void;
}) {
  return (
    <div className="flex gap-1">
      <button
        onClick={() => onChange('list')}
        className={cn(
          'p-2 rounded transition-colors',
          value === 'list' ? 'bg-town-accent/50 text-white' : 'text-gray-400 hover:text-white'
        )}
        title="List view"
      >
        ☰
      </button>
      <button
        onClick={() => onChange('graph')}
        className={cn(
          'p-2 rounded transition-colors',
          value === 'graph' ? 'bg-town-accent/50 text-white' : 'text-gray-400 hover:text-white'
        )}
        title="Graph view"
      >
        ⚛
      </button>
    </div>
  );
}

function StatBadge({
  label,
  value,
  color,
}: {
  label: string;
  value: string | number;
  color?: string;
}) {
  return (
    <div className="bg-town-surface/30 rounded-lg p-2 text-center">
      <div className={cn('text-lg font-semibold', color)}>{value}</div>
      <div className="text-xs text-gray-500">{label}</div>
    </div>
  );
}

// =============================================================================
// List View
// =============================================================================

interface RelationshipListProps {
  relationships: [string, number][];
  citizenName: string;
  expanded?: boolean;
}

function RelationshipList({ relationships, expanded }: RelationshipListProps) {
  const sorted = [...relationships].sort(([, a], [, b]) => b - a);
  const display = expanded ? sorted : sorted.slice(0, 10);

  return (
    <div className="space-y-2">
      {display.map(([name, value]) => (
        <RelationshipRow key={name} name={name} value={value} />
      ))}
      {!expanded && sorted.length > 10 && (
        <p className="text-xs text-gray-500 text-center mt-3">
          +{sorted.length - 10} more relationships
        </p>
      )}
    </div>
  );
}

function RelationshipRow({ name, value }: { name: string; value: number }) {
  const absValue = Math.abs(value);
  const isPositive = value > 0.1;
  const isNegative = value < -0.1;

  return (
    <div className="flex items-center gap-3 bg-town-surface/20 rounded-lg p-3">
      {/* Avatar */}
      <div
        className={cn(
          'w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium',
          isPositive
            ? 'bg-green-500/20 text-green-400'
            : isNegative
              ? 'bg-red-500/20 text-red-400'
              : 'bg-gray-500/20 text-gray-400'
        )}
      >
        {name.charAt(0).toUpperCase()}
      </div>

      {/* Name */}
      <div className="flex-1 min-w-0">
        <div className="font-medium truncate">{name}</div>
        <div className="text-xs text-gray-500">{getRelationshipLabel(value)}</div>
      </div>

      {/* Strength bar */}
      <div className="w-20">
        <div className="h-2 bg-town-surface rounded-full overflow-hidden flex">
          {value < 0 ? (
            <>
              <div className="flex-1" />
              <div
                className="bg-red-500 transition-all"
                style={{ width: `${absValue * 50}%` }}
              />
            </>
          ) : (
            <>
              <div
                className="bg-green-500 transition-all ml-auto"
                style={{ width: `${absValue * 50}%` }}
              />
            </>
          )}
        </div>
      </div>

      {/* Value */}
      <span
        className={cn(
          'text-sm font-mono w-12 text-right',
          isPositive ? 'text-green-400' : isNegative ? 'text-red-400' : 'text-gray-500'
        )}
      >
        {value > 0 ? '+' : ''}
        {value.toFixed(2)}
      </span>
    </div>
  );
}

// =============================================================================
// Graph View
// =============================================================================

interface RelationshipGraphProps {
  relationships: [string, number][];
  citizenName: string;
  expanded?: boolean;
}

function RelationshipGraph({ relationships, citizenName, expanded }: RelationshipGraphProps) {
  const size = expanded ? 400 : 280;
  const center = size / 2;
  const innerRadius = 30;
  const outerRadius = size / 2 - 40;

  // Sort by strength for layout
  const sorted = [...relationships].sort(([, a], [, b]) => Math.abs(b) - Math.abs(a));
  const displayed = sorted.slice(0, 12);

  return (
    <div className="flex justify-center">
      <svg width={size} height={size} className="overflow-visible">
        {/* Connections */}
        {displayed.map(([name, value], i) => {
          const angle = (i / displayed.length) * Math.PI * 2 - Math.PI / 2;
          const distance = outerRadius * (0.5 + Math.abs(value) * 0.5);
          const x = center + Math.cos(angle) * distance;
          const y = center + Math.sin(angle) * distance;

          const isPositive = value > 0.1;
          const isNegative = value < -0.1;
          const color = isPositive ? '#22c55e' : isNegative ? '#ef4444' : '#6b7280';

          return (
            <g key={name}>
              {/* Connection line */}
              <line
                x1={center}
                y1={center}
                x2={x}
                y2={y}
                stroke={color}
                strokeWidth={Math.abs(value) * 3 + 1}
                strokeOpacity={0.5}
              />

              {/* Node */}
              <circle cx={x} cy={y} r={16} fill={color} fillOpacity={0.2} stroke={color} />

              {/* Label */}
              <text
                x={x}
                y={y + 4}
                fontSize="10"
                fill="white"
                textAnchor="middle"
                fontWeight="bold"
              >
                {name.slice(0, 2).toUpperCase()}
              </text>

              {/* Full name tooltip on hover */}
              <title>
                {name}: {value > 0 ? '+' : ''}
                {value.toFixed(2)}
              </title>
            </g>
          );
        })}

        {/* Center node (current citizen) */}
        <circle
          cx={center}
          cy={center}
          r={innerRadius}
          fill="var(--town-highlight, #60a5fa)"
          fillOpacity={0.3}
          stroke="var(--town-highlight, #60a5fa)"
          strokeWidth={2}
        />
        <text
          x={center}
          y={center + 4}
          fontSize="12"
          fill="white"
          textAnchor="middle"
          fontWeight="bold"
        >
          {citizenName.slice(0, 3)}
        </text>
      </svg>
    </div>
  );
}

// =============================================================================
// Helpers
// =============================================================================

function getRelationshipLabel(value: number): string {
  if (value > 0.7) return 'Close friend';
  if (value > 0.4) return 'Friend';
  if (value > 0.1) return 'Acquaintance';
  if (value > -0.1) return 'Neutral';
  if (value > -0.4) return 'Distant';
  if (value > -0.7) return 'Rival';
  return 'Adversary';
}

export default RelationshipsTab;
