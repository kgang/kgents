/**
 * MetricsTab: Charts for activity history and eigenvector drift.
 *
 * Visualizes temporal patterns in citizen behavior.
 */

import { useState } from 'react';
import { cn } from '@/lib/utils';
import type { CitizenCardJSON, CitizenEigenvectors } from '@/reactive/types';
import type { CitizenManifest, Eigenvectors } from '@/api/types';

type EigenvectorKey = keyof Eigenvectors;
type CitizenEigenvectorKey = keyof CitizenEigenvectors;

export interface MetricsTabProps {
  citizen: CitizenCardJSON;
  manifest: CitizenManifest | null;
  expanded?: boolean;
}

type TimeRange = '1h' | '6h' | '24h' | '7d';
type MetricView = 'eigenvector' | 'activity' | 'entropy';

export function MetricsTab({ citizen, manifest, expanded = false }: MetricsTabProps) {
  const [timeRange, setTimeRange] = useState<TimeRange>('24h');
  const [metricView, setMetricView] = useState<MetricView>('eigenvector');

  return (
    <div className="space-y-6">
      {/* Controls */}
      <div className="flex items-center justify-between">
        <TimeRangeSelector value={timeRange} onChange={setTimeRange} />
        <MetricViewSelector value={metricView} onChange={setMetricView} />
      </div>

      {/* Main Chart */}
      <div className={cn('bg-town-surface/30 rounded-lg p-4', expanded ? 'h-64' : 'h-48')}>
        {metricView === 'eigenvector' && (
          <EigenvectorDriftChart
            citizen={citizen}
            manifest={manifest}
            timeRange={timeRange}
            height={expanded ? 200 : 140}
          />
        )}
        {metricView === 'activity' && (
          <ActivityChart citizen={citizen} timeRange={timeRange} height={expanded ? 200 : 140} />
        )}
        {metricView === 'entropy' && (
          <EntropyChart citizen={citizen} timeRange={timeRange} height={expanded ? 200 : 140} />
        )}
      </div>

      {/* Summary Stats */}
      <div className={cn('grid gap-4', expanded ? 'grid-cols-4' : 'grid-cols-2')}>
        <MetricCard
          label="Peak Activity"
          value={formatTime(getPeakActivityTime(timeRange))}
          trend="+12%"
          positive
        />
        <MetricCard
          label="Avg Entropy"
          value={citizen.entropy.toFixed(3)}
          trend="-0.5%"
          positive
        />
        <MetricCard
          label="Drift Rate"
          value={getDriftRate(citizen).toFixed(3)}
          trend="+2%"
          positive={false}
        />
        <MetricCard label="Active Time" value={getActiveTime(timeRange)} trend="+8%" positive />
      </div>

      {/* Eigenvector Radar (expanded only) */}
      {expanded && manifest?.eigenvectors && (
        <div className="mt-6">
          <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wide mb-3">
            Eigenvector Profile
          </h3>
          <div className="flex items-center justify-center">
            <EigenvectorRadar eigenvectors={manifest.eigenvectors} size={200} />
          </div>
        </div>
      )}
    </div>
  );
}

// =============================================================================
// Controls
// =============================================================================

function TimeRangeSelector({
  value,
  onChange,
}: {
  value: TimeRange;
  onChange: (v: TimeRange) => void;
}) {
  const options: TimeRange[] = ['1h', '6h', '24h', '7d'];

  return (
    <div className="flex gap-1 bg-town-surface/30 rounded-lg p-1">
      {options.map((opt) => (
        <button
          key={opt}
          onClick={() => onChange(opt)}
          className={cn(
            'px-3 py-1 text-xs font-medium rounded transition-colors',
            value === opt ? 'bg-town-highlight text-white' : 'text-gray-400 hover:text-white'
          )}
        >
          {opt}
        </button>
      ))}
    </div>
  );
}

function MetricViewSelector({
  value,
  onChange,
}: {
  value: MetricView;
  onChange: (v: MetricView) => void;
}) {
  const options: { id: MetricView; label: string; icon: string }[] = [
    { id: 'eigenvector', label: 'Eigenvectors', icon: '📊' },
    { id: 'activity', label: 'Activity', icon: '📈' },
    { id: 'entropy', label: 'Entropy', icon: '🎲' },
  ];

  return (
    <div className="flex gap-1">
      {options.map((opt) => (
        <button
          key={opt.id}
          onClick={() => onChange(opt.id)}
          className={cn(
            'px-2 py-1 text-xs rounded transition-colors',
            value === opt.id
              ? 'bg-town-accent/50 text-white'
              : 'text-gray-400 hover:bg-town-accent/20'
          )}
          title={opt.label}
        >
          {opt.icon}
        </button>
      ))}
    </div>
  );
}

// =============================================================================
// Charts
// =============================================================================

interface ChartProps {
  citizen: CitizenCardJSON;
  manifest?: CitizenManifest | null;
  timeRange: TimeRange;
  height: number;
}

function EigenvectorDriftChart({ citizen, timeRange, height }: ChartProps) {
  // Generate drift data for each eigenvector (using only those in CitizenEigenvectors)
  const vectors: { key: CitizenEigenvectorKey; color: string }[] = [
    { key: 'warmth', color: '#ef4444' },
    { key: 'curiosity', color: '#eab308' },
    { key: 'trust', color: '#22c55e' },
  ];

  const numPoints = getTimePoints(timeRange);

  return (
    <svg width="100%" height={height}>
      {/* Grid */}
      {[0, 0.25, 0.5, 0.75, 1].map((y) => (
        <line
          key={y}
          x1="0"
          y1={height * (1 - y)}
          x2="100%"
          y2={height * (1 - y)}
          stroke="currentColor"
          strokeOpacity="0.1"
        />
      ))}

      {/* Lines */}
      {vectors.map(({ key, color }) => {
        const baseValue = citizen.eigenvectors?.[key] ?? 0.5;
        const linePoints = Array.from({ length: numPoints }, (_, i) => {
          const x = (i / (numPoints - 1)) * 100;
          const drift = Math.sin(i * 0.3) * 0.1 + Math.cos(i * 0.2) * 0.05;
          const y = (1 - Math.max(0, Math.min(1, baseValue + drift))) * height;
          return `${x}%,${y}`;
        }).join(' ');

        return (
          <polyline
            key={key}
            points={linePoints}
            fill="none"
            stroke={color}
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
            opacity="0.8"
          />
        );
      })}

      {/* Legend */}
      <g transform={`translate(10, ${height - 20})`}>
        {vectors.slice(0, 4).map(({ key, color }, i) => (
          <g key={key} transform={`translate(${i * 70}, 0)`}>
            <rect width="12" height="3" fill={color} />
            <text x="16" y="3" fontSize="10" fill="#9ca3af">
              {key.slice(0, 4)}
            </text>
          </g>
        ))}
      </g>
    </svg>
  );
}

function ActivityChart({ citizen, timeRange, height }: Omit<ChartProps, 'manifest'>) {
  const points = getTimePoints(timeRange);
  const baseActivity = citizen.capability;

  const data = Array.from({ length: points }, (_, i) => {
    const cyclePos = (i / points) * Math.PI * 2;
    const value = baseActivity + Math.sin(cyclePos) * 0.2 + Math.random() * 0.1 - 0.05;
    return Math.max(0, Math.min(1, value));
  });

  const path = data
    .map((v, i) => {
      const x = (i / (data.length - 1)) * 100;
      const y = (1 - v) * height;
      return `${x}%,${y}`;
    })
    .join(' ');

  const area = `M 0,${height} L ${path.replace(/,/g, ' L ')} L 100%,${height} Z`;

  return (
    <svg width="100%" height={height}>
      {/* Grid */}
      {[0, 0.5, 1].map((y) => (
        <line
          key={y}
          x1="0"
          y1={height * (1 - y)}
          x2="100%"
          y2={height * (1 - y)}
          stroke="currentColor"
          strokeOpacity="0.1"
        />
      ))}

      {/* Area */}
      <path d={area} fill="url(#activityFill)" />

      {/* Line */}
      <polyline
        points={path}
        fill="none"
        stroke="var(--town-highlight, #60a5fa)"
        strokeWidth="2"
        strokeLinecap="round"
      />

      <defs>
        <linearGradient id="activityFill" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="var(--town-highlight)" stopOpacity="0.3" />
          <stop offset="100%" stopColor="var(--town-highlight)" stopOpacity="0" />
        </linearGradient>
      </defs>
    </svg>
  );
}

function EntropyChart({ citizen, timeRange, height }: Omit<ChartProps, 'manifest'>) {
  const points = getTimePoints(timeRange);
  const baseEntropy = citizen.entropy;

  const data = Array.from({ length: points }, (_, i) => {
    // Entropy tends to increase over time with occasional resets
    const trend = (i / points) * 0.05;
    const reset = i % 10 === 0 ? -0.1 : 0;
    const noise = (Math.random() - 0.5) * 0.02;
    return Math.max(0, Math.min(1, baseEntropy + trend + reset + noise));
  });

  return (
    <svg width="100%" height={height}>
      {/* Warning threshold */}
      <rect x="0" y="0" width="100%" height={height * 0.3} fill="#ef444420" />
      <line x1="0" y1={height * 0.3} x2="100%" y2={height * 0.3} stroke="#ef4444" strokeDasharray="4" opacity="0.5" />

      {/* Grid */}
      {[0, 0.5, 1].map((y) => (
        <line
          key={y}
          x1="0"
          y1={height * (1 - y)}
          x2="100%"
          y2={height * (1 - y)}
          stroke="currentColor"
          strokeOpacity="0.1"
        />
      ))}

      {/* Bars */}
      {data.map((v, i) => {
        const x = (i / data.length) * 100;
        const w = 90 / data.length;
        const h = v * height;
        const isHigh = v > 0.7;
        return (
          <rect
            key={i}
            x={`${x}%`}
            y={height - h}
            width={`${w}%`}
            height={h}
            fill={isHigh ? '#ef4444' : '#60a5fa'}
            opacity={0.6}
            rx="1"
          />
        );
      })}
    </svg>
  );
}

// =============================================================================
// Radar Chart
// =============================================================================

interface EigenvectorRadarProps {
  eigenvectors: Eigenvectors;
  size: number;
}

function EigenvectorRadar({ eigenvectors, size }: EigenvectorRadarProps) {
  const vectors: { key: EigenvectorKey; label: string }[] = [
    { key: 'warmth', label: 'W' },
    { key: 'curiosity', label: 'Cu' },
    { key: 'trust', label: 'T' },
    { key: 'creativity', label: 'Cr' },
    { key: 'patience', label: 'P' },
    { key: 'resilience', label: 'R' },
    { key: 'ambition', label: 'A' },
  ];

  const center = size / 2;
  const radius = size / 2 - 30;
  const angleStep = (Math.PI * 2) / vectors.length;

  // Generate polygon points
  const points = vectors
    .map(({ key }, i) => {
      const value = eigenvectors[key];
      const angle = i * angleStep - Math.PI / 2;
      const r = value * radius;
      const x = center + Math.cos(angle) * r;
      const y = center + Math.sin(angle) * r;
      return `${x},${y}`;
    })
    .join(' ');

  return (
    <svg width={size} height={size}>
      {/* Background rings */}
      {[0.25, 0.5, 0.75, 1].map((r) => (
        <polygon
          key={r}
          points={vectors
            .map((_, i) => {
              const angle = i * angleStep - Math.PI / 2;
              const x = center + Math.cos(angle) * radius * r;
              const y = center + Math.sin(angle) * radius * r;
              return `${x},${y}`;
            })
            .join(' ')}
          fill="none"
          stroke="currentColor"
          strokeOpacity="0.1"
        />
      ))}

      {/* Axis lines */}
      {vectors.map((_, i) => {
        const angle = i * angleStep - Math.PI / 2;
        const x = center + Math.cos(angle) * radius;
        const y = center + Math.sin(angle) * radius;
        return (
          <line
            key={i}
            x1={center}
            y1={center}
            x2={x}
            y2={y}
            stroke="currentColor"
            strokeOpacity="0.1"
          />
        );
      })}

      {/* Data polygon */}
      <polygon
        points={points}
        fill="var(--town-highlight, #60a5fa)"
        fillOpacity="0.3"
        stroke="var(--town-highlight, #60a5fa)"
        strokeWidth="2"
      />

      {/* Labels */}
      {vectors.map(({ label }, i) => {
        const angle = i * angleStep - Math.PI / 2;
        const x = center + Math.cos(angle) * (radius + 20);
        const y = center + Math.sin(angle) * (radius + 20);
        return (
          <text
            key={i}
            x={x}
            y={y}
            fontSize="10"
            fill="#9ca3af"
            textAnchor="middle"
            dominantBaseline="middle"
          >
            {label}
          </text>
        );
      })}
    </svg>
  );
}

// =============================================================================
// Metric Cards
// =============================================================================

interface MetricCardProps {
  label: string;
  value: string;
  trend: string;
  positive: boolean;
}

function MetricCard({ label, value, trend, positive }: MetricCardProps) {
  return (
    <div className="bg-town-surface/30 rounded-lg p-3 border border-town-accent/20">
      <div className="text-xs text-gray-400 mb-1">{label}</div>
      <div className="flex items-end justify-between">
        <span className="text-lg font-semibold">{value}</span>
        <span
          className={cn(
            'text-xs font-medium',
            positive ? 'text-green-400' : 'text-red-400'
          )}
        >
          {trend}
        </span>
      </div>
    </div>
  );
}

// =============================================================================
// Helpers
// =============================================================================

function getTimePoints(range: TimeRange): number {
  switch (range) {
    case '1h':
      return 12;
    case '6h':
      return 24;
    case '24h':
      return 48;
    case '7d':
      return 84;
    default:
      return 24;
  }
}

function formatTime(hours: number): string {
  if (hours === 0) return 'Now';
  if (hours < 24) return `${hours}h ago`;
  return `${Math.floor(hours / 24)}d ago`;
}

function getPeakActivityTime(_range: TimeRange): number {
  // Mock: return hours ago of peak activity
  return Math.floor(Math.random() * 6);
}

function getDriftRate(citizen: CitizenCardJSON): number {
  // Mock: calculate drift from entropy
  return citizen.entropy * 0.1;
}

function getActiveTime(range: TimeRange): string {
  const totalHours = range === '1h' ? 1 : range === '6h' ? 6 : range === '24h' ? 24 : 168;
  const activeHours = Math.floor(totalHours * 0.65);
  return range === '7d' ? `${Math.floor(activeHours / 24)}d ${activeHours % 24}h` : `${activeHours}h`;
}

export default MetricsTab;
