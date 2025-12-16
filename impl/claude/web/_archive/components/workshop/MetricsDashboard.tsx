/**
 * MetricsDashboard: Workshop-wide metrics visualization (Chunk 9).
 *
 * Shows aggregate metrics with sparklines, builder performance bars,
 * and handoff flow visualization.
 */

import { useEffect, useState } from 'react';
import { useWorkshopStore } from '@/stores/workshopStore';
import { workshopApi } from '@/api/client';
import { BUILDER_COLORS, BUILDER_ICONS, type BuilderArchetype } from '@/api/types';

interface MetricsDashboardProps {
  onClose?: () => void;
}

type Period = '24h' | '7d' | '30d' | 'all';

const PERIODS: { value: Period; label: string }[] = [
  { value: '24h', label: '24h' },
  { value: '7d', label: '7d' },
  { value: '30d', label: '30d' },
  { value: 'all', label: 'All' },
];

export function MetricsDashboard({ onClose }: MetricsDashboardProps) {
  const {
    aggregateMetrics,
    builderMetrics,
    flowMetrics,
    metricsPeriod,
    setAggregateMetrics,
    setBuilderMetrics,
    setFlowMetrics,
    setMetricsPeriod,
  } = useWorkshopStore();

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Load metrics on mount and period change
  useEffect(() => {
    const loadMetrics = async () => {
      setLoading(true);
      setError(null);
      try {
        const [aggResponse, flowResponse] = await Promise.all([
          workshopApi.getAggregateMetrics(metricsPeriod),
          workshopApi.getFlowMetrics(),
        ]);

        setAggregateMetrics(aggResponse.data);
        setFlowMetrics(flowResponse.data);

        // Load builder metrics for all archetypes
        const archetypes: BuilderArchetype[] = ['Scout', 'Sage', 'Spark', 'Steady', 'Sync'];
        await Promise.all(
          archetypes.map(async (archetype) => {
            const response = await workshopApi.getBuilderMetrics(archetype, metricsPeriod);
            setBuilderMetrics(archetype, response.data);
          })
        );
      } catch (err: unknown) {
        const axiosErr = err as { response?: { data?: { detail?: string } } };
        setError(axiosErr.response?.data?.detail || 'Failed to load metrics');
      } finally {
        setLoading(false);
      }
    };

    loadMetrics();
  }, [metricsPeriod, setAggregateMetrics, setFlowMetrics, setBuilderMetrics]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-pulse text-4xl mb-2">📊</div>
          <p className="text-gray-400">Loading metrics...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="text-4xl mb-2">⚠️</div>
          <p className="text-red-400">{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-4 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold">Workshop Metrics</h2>
        <div className="flex items-center gap-2">
          {/* Period Selector */}
          <div className="flex bg-town-surface rounded-lg p-1">
            {PERIODS.map(({ value, label }) => (
              <button
                key={value}
                onClick={() => setMetricsPeriod(value)}
                className={`px-3 py-1 text-sm rounded transition-colors ${
                  metricsPeriod === value
                    ? 'bg-town-highlight text-white'
                    : 'text-gray-400 hover:text-white'
                }`}
              >
                {label}
              </button>
            ))}
          </div>
          {onClose && (
            <button
              onClick={onClose}
              className="p-1 text-gray-400 hover:text-white transition-colors"
            >
              ✕
            </button>
          )}
        </div>
      </div>

      {/* Summary Cards */}
      {aggregateMetrics && (
        <div className="grid grid-cols-3 gap-4">
          <MetricCard
            label="Tasks"
            value={aggregateMetrics.total_tasks}
            subtext={`${aggregateMetrics.completed_tasks} completed`}
            sparkline={aggregateMetrics.tasks_by_day.map((d) => d.value)}
          />
          <MetricCard
            label="Artifacts"
            value={aggregateMetrics.total_artifacts}
            subtext={`${aggregateMetrics.total_handoffs} handoffs`}
            sparkline={aggregateMetrics.artifacts_by_day.map((d) => d.value)}
          />
          <MetricCard
            label="Tokens"
            value={formatNumber(aggregateMetrics.total_tokens)}
            subtext={`${aggregateMetrics.avg_duration_seconds.toFixed(1)}s avg`}
            sparkline={aggregateMetrics.tokens_by_day.map((d) => d.value)}
          />
        </div>
      )}

      {/* Builder Performance */}
      <div className="bg-town-surface/30 rounded-lg p-4">
        <h3 className="font-semibold mb-4">Builder Performance</h3>
        <div className="space-y-3">
          {(['Scout', 'Sage', 'Spark', 'Steady', 'Sync'] as BuilderArchetype[]).map(
            (archetype) => {
              const metrics = builderMetrics[archetype];
              if (!metrics) return null;

              const efficiency = metrics.specialty_efficiency * 100;
              const color = BUILDER_COLORS[archetype];
              const icon = BUILDER_ICONS[archetype];

              return (
                <div key={archetype} className="flex items-center gap-3">
                  <div className="w-20 flex items-center gap-1">
                    <span>{icon}</span>
                    <span className="text-sm">{archetype}</span>
                  </div>
                  <div className="flex-1">
                    <div className="h-4 bg-town-surface rounded-full overflow-hidden">
                      <div
                        className="h-full transition-all duration-500"
                        style={{
                          width: `${efficiency}%`,
                          backgroundColor: color,
                        }}
                      />
                    </div>
                  </div>
                  <div className="w-12 text-right text-sm text-gray-400">
                    {efficiency.toFixed(0)}%
                  </div>
                  <div className="w-20 text-right text-sm text-gray-400">
                    {metrics.tasks_participated} tasks
                  </div>
                  <div className="w-16 text-right text-sm text-gray-400">
                    {metrics.avg_duration_seconds.toFixed(1)}s
                  </div>
                </div>
              );
            }
          )}
        </div>
      </div>

      {/* Handoff Flow */}
      {flowMetrics && flowMetrics.flows.length > 0 && (
        <div className="bg-town-surface/30 rounded-lg p-4">
          <h3 className="font-semibold mb-4">Handoff Flow</h3>
          <HandoffFlowViz flows={flowMetrics.flows} />
        </div>
      )}
    </div>
  );
}

// =============================================================================
// Sub-Components
// =============================================================================

interface MetricCardProps {
  label: string;
  value: number | string;
  subtext: string;
  sparkline?: number[];
}

function MetricCard({ label, value, subtext, sparkline }: MetricCardProps) {
  return (
    <div className="bg-town-surface/30 rounded-lg p-4">
      <div className="text-sm text-gray-400">{label}</div>
      <div className="text-3xl font-bold mt-1">{value}</div>
      <div className="text-xs text-gray-500 mt-1">{subtext}</div>
      {sparkline && sparkline.length > 0 && (
        <div className="mt-2">
          <Sparkline values={sparkline} />
        </div>
      )}
    </div>
  );
}

interface SparklineProps {
  values: number[];
  height?: number;
}

function Sparkline({ values, height = 24 }: SparklineProps) {
  if (values.length === 0) return null;

  const max = Math.max(...values, 1);
  const width = values.length * 6;

  return (
    <svg width="100%" height={height} viewBox={`0 0 ${width} ${height}`} className="text-town-highlight">
      <path
        d={values
          .map((v, i) => {
            const x = i * 6;
            const y = height - (v / max) * height * 0.9;
            return `${i === 0 ? 'M' : 'L'} ${x} ${y}`;
          })
          .join(' ')}
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
      />
    </svg>
  );
}

interface HandoffFlowVizProps {
  flows: { from_builder: string; to_builder: string; count: number }[];
}

function HandoffFlowViz({ flows }: HandoffFlowVizProps) {
  const archetypes: BuilderArchetype[] = ['Scout', 'Sage', 'Spark', 'Steady', 'Sync'];
  const maxCount = Math.max(...flows.map((f) => f.count), 1);

  return (
    <div className="flex items-center justify-between">
      {archetypes.map((archetype, idx) => {
        const icon = BUILDER_ICONS[archetype];
        const color = BUILDER_COLORS[archetype];

        // Find flows from this archetype
        const outFlow = flows.find(
          (f) =>
            f.from_builder === archetype &&
            archetypes.indexOf(f.to_builder as BuilderArchetype) === idx + 1
        );

        return (
          <div key={archetype} className="flex items-center">
            <div
              className="w-10 h-10 rounded-full flex items-center justify-center text-lg"
              style={{ backgroundColor: color + '30', border: `2px solid ${color}` }}
            >
              {icon}
            </div>
            {idx < archetypes.length - 1 && (
              <div className="flex items-center mx-2">
                <div
                  className="h-1 bg-town-accent/50 transition-all"
                  style={{
                    width: `${Math.max(20, (outFlow?.count || 0) / maxCount * 60)}px`,
                  }}
                />
                {outFlow && outFlow.count > 0 && (
                  <span className="text-xs text-gray-400 mx-1">({outFlow.count})</span>
                )}
                <div className="text-gray-400">▶</div>
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}

// =============================================================================
// Helpers
// =============================================================================

function formatNumber(num: number): string {
  if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`;
  if (num >= 1000) return `${(num / 1000).toFixed(1)}k`;
  return num.toString();
}

export default MetricsDashboard;
