/**
 * EvidenceStream - Live playthrough data and quality crystals
 *
 * "Evidence is not data. It's data that has passed through the fire of evaluation."
 *
 * Right panel in Create Mode. Shows:
 * - Live stream of playthrough events
 * - Quality crystals from completed runs
 * - Galois loss visualization over time
 * - Axiom-by-axiom score breakdown
 *
 * STARK BIOME aesthetic: 90% steel, 10% earned glow.
 */

import { memo, useState, useEffect, useMemo } from 'react';
import { Activity, Gem, TrendingDown, Filter, Play, Pause, RefreshCw } from 'lucide-react';
import type { EvidenceFilter, EvidenceStreamData, QualityCrystal, GaloisLossPoint } from './types';

// =============================================================================
// Types
// =============================================================================

export interface EvidenceStreamProps {
  /** Game ID to stream evidence for */
  gameId: string;
  /** Optional filter configuration */
  evidenceFilter?: EvidenceFilter;
  /** Called when filter changes */
  onFilterChange?: (filter: EvidenceFilter) => void;
  /** Called when a crystal is selected for detail view */
  onCrystalSelect?: (crystalId: string) => void;
}

// =============================================================================
// Mock Data (would be replaced with real API)
// =============================================================================

function generateMockStreamData(gameId: string): EvidenceStreamData {
  const now = new Date();
  const crystals: QualityCrystal[] = [
    {
      id: 'crystal-1',
      compositionId: 'comp-1',
      timestamp: new Date(now.getTime() - 60000),
      axiomScores: { A1: 0.92, A2: 0.85, A3: 0.78, A4: 0.88 },
      overallQuality: 0.86,
      playerActions: ['jump', 'dash', 'attack'],
      duration: 45,
    },
    {
      id: 'crystal-2',
      compositionId: 'comp-1',
      timestamp: new Date(now.getTime() - 120000),
      axiomScores: { A1: 0.88, A2: 0.9, A3: 0.72, A4: 0.85 },
      overallQuality: 0.84,
      playerActions: ['block', 'attack', 'collect'],
      duration: 62,
    },
    {
      id: 'crystal-3',
      compositionId: 'comp-2',
      timestamp: new Date(now.getTime() - 180000),
      axiomScores: { A1: 0.95, A2: 0.82, A3: 0.88, A4: 0.9 },
      overallQuality: 0.89,
      playerActions: ['dash', 'jump', 'attack', 'attack'],
      duration: 38,
    },
  ];

  const lossHistory: GaloisLossPoint[] = Array.from({ length: 20 }, (_, i) => ({
    timestamp: new Date(now.getTime() - i * 10000),
    loss: 0.15 + Math.random() * 0.1 - 0.05,
    contributors: ['composition complexity', 'mechanic count'],
  })).reverse();

  return {
    sessionId: `session-${gameId}-${Date.now()}`,
    crystals,
    lossHistory,
    currentLoss: lossHistory[lossHistory.length - 1]?.loss || 0.15,
    isLive: true,
  };
}

// =============================================================================
// Subcomponents
// =============================================================================

interface CrystalCardProps {
  crystal: QualityCrystal;
  isSelected: boolean;
  onSelect: () => void;
}

const CrystalCard = memo(function CrystalCard({ crystal, isSelected, onSelect }: CrystalCardProps) {
  const formatTime = (date: Date) => {
    return date.toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const qualityColor =
    crystal.overallQuality >= 0.85
      ? 'var(--glow-amber)'
      : crystal.overallQuality >= 0.7
        ? 'var(--layer-1)'
        : 'var(--steel-500)';

  return (
    <button
      className={`evidence-crystal ${isSelected ? 'evidence-crystal--selected' : ''}`}
      onClick={onSelect}
    >
      <div className="evidence-crystal__header">
        <Gem size={12} style={{ color: qualityColor }} />
        <span className="evidence-crystal__time">{formatTime(crystal.timestamp)}</span>
        <span className="evidence-crystal__quality" style={{ color: qualityColor }}>
          {Math.round(crystal.overallQuality * 100)}%
        </span>
      </div>

      <div className="evidence-crystal__axioms">
        {Object.entries(crystal.axiomScores).map(([axiomId, score]) => (
          <div key={axiomId} className="evidence-crystal__axiom">
            <span className="evidence-crystal__axiom-id">{axiomId}</span>
            <div className="evidence-crystal__axiom-bar">
              <div className="evidence-crystal__axiom-fill" style={{ width: `${score * 100}%` }} />
            </div>
            <span className="evidence-crystal__axiom-value">{Math.round(score * 100)}</span>
          </div>
        ))}
      </div>

      <div className="evidence-crystal__actions">
        {crystal.playerActions.slice(0, 3).map((action, i) => (
          <span key={i} className="evidence-crystal__action">
            {action}
          </span>
        ))}
        {crystal.playerActions.length > 3 && (
          <span className="evidence-crystal__action-more">+{crystal.playerActions.length - 3}</span>
        )}
      </div>

      <div className="evidence-crystal__footer">
        <span className="evidence-crystal__duration">{crystal.duration}s</span>
      </div>
    </button>
  );
});

interface LossChartProps {
  history: GaloisLossPoint[];
  currentLoss: number;
}

const LossChart = memo(function LossChart({ history, currentLoss }: LossChartProps) {
  // Simple sparkline visualization
  const maxLoss = Math.max(...history.map((p) => p.loss), 0.3);
  const minLoss = Math.min(...history.map((p) => p.loss), 0);
  const range = maxLoss - minLoss || 0.1;

  const points = history
    .map((point, i) => {
      const x = (i / (history.length - 1)) * 100;
      const y = 100 - ((point.loss - minLoss) / range) * 100;
      return `${x},${y}`;
    })
    .join(' ');

  const lossColor =
    currentLoss <= 0.1
      ? 'var(--glow-amber)'
      : currentLoss <= 0.2
        ? 'var(--layer-1)'
        : 'var(--layer-2)';

  return (
    <div className="evidence-loss-chart">
      <div className="evidence-loss-chart__header">
        <TrendingDown size={12} />
        <span>Galois Loss</span>
        <span className="evidence-loss-chart__current" style={{ color: lossColor }}>
          {(currentLoss * 100).toFixed(1)}%
        </span>
      </div>
      <svg className="evidence-loss-chart__svg" viewBox="0 0 100 40" preserveAspectRatio="none">
        <polyline
          points={points}
          fill="none"
          stroke={lossColor}
          strokeWidth="1.5"
          vectorEffect="non-scaling-stroke"
        />
        {/* Current point */}
        {history.length > 0 && (
          <circle
            cx="100"
            cy={100 - ((currentLoss - minLoss) / range) * 100}
            r="2"
            fill={lossColor}
          />
        )}
      </svg>
      <div className="evidence-loss-chart__labels">
        <span>{(minLoss * 100).toFixed(0)}%</span>
        <span>{(maxLoss * 100).toFixed(0)}%</span>
      </div>
    </div>
  );
});

interface StreamControlsProps {
  isLive: boolean;
  onToggleLive: () => void;
  onRefresh: () => void;
}

const StreamControls = memo(function StreamControls({
  isLive,
  onToggleLive,
  onRefresh,
}: StreamControlsProps) {
  return (
    <div className="evidence-controls">
      <button
        className={`evidence-controls__btn ${isLive ? 'evidence-controls__btn--active' : ''}`}
        onClick={onToggleLive}
        title={isLive ? 'Pause stream' : 'Resume stream'}
      >
        {isLive ? <Pause size={12} /> : <Play size={12} />}
        <span>{isLive ? 'Live' : 'Paused'}</span>
      </button>
      <button className="evidence-controls__btn" onClick={onRefresh} title="Refresh data">
        <RefreshCw size={12} />
      </button>
    </div>
  );
});

interface FilterPanelProps {
  filter: EvidenceFilter;
  onFilterChange: (filter: EvidenceFilter) => void;
}

const FilterPanel = memo(function FilterPanel({ filter, onFilterChange }: FilterPanelProps) {
  const [isOpen, setIsOpen] = useState(false);

  const activeFilterCount = useMemo(() => {
    let count = 0;
    if (filter.mechanicIds?.length) count++;
    if (filter.axiomIds?.length) count++;
    if (filter.timeRange) count++;
    if (filter.minQuality !== undefined) count++;
    return count;
  }, [filter]);

  return (
    <div className="evidence-filter">
      <button
        className={`evidence-filter__toggle ${activeFilterCount > 0 ? 'evidence-filter__toggle--active' : ''}`}
        onClick={() => setIsOpen(!isOpen)}
      >
        <Filter size={12} />
        <span>Filter</span>
        {activeFilterCount > 0 && (
          <span className="evidence-filter__count">{activeFilterCount}</span>
        )}
      </button>

      {isOpen && (
        <div className="evidence-filter__panel">
          <div className="evidence-filter__group">
            <label>Min Quality</label>
            <input
              type="range"
              min="0"
              max="100"
              value={(filter.minQuality || 0) * 100}
              onChange={(e) =>
                onFilterChange({
                  ...filter,
                  minQuality: parseInt(e.target.value, 10) / 100,
                })
              }
            />
            <span>{((filter.minQuality || 0) * 100).toFixed(0)}%</span>
          </div>

          <div className="evidence-filter__group">
            <label>Axioms</label>
            <div className="evidence-filter__axioms">
              {['A1', 'A2', 'A3', 'A4'].map((axiomId) => (
                <button
                  key={axiomId}
                  className={`evidence-filter__axiom ${filter.axiomIds?.includes(axiomId) ? 'evidence-filter__axiom--active' : ''}`}
                  onClick={() => {
                    const current = filter.axiomIds || [];
                    const next = current.includes(axiomId)
                      ? current.filter((id) => id !== axiomId)
                      : [...current, axiomId];
                    onFilterChange({ ...filter, axiomIds: next.length ? next : undefined });
                  }}
                >
                  {axiomId}
                </button>
              ))}
            </div>
          </div>

          <button className="evidence-filter__clear" onClick={() => onFilterChange({})}>
            Clear all
          </button>
        </div>
      )}
    </div>
  );
});

// =============================================================================
// Main Component
// =============================================================================

export const EvidenceStream = memo(function EvidenceStream({
  gameId,
  evidenceFilter = {},
  onFilterChange,
  onCrystalSelect,
}: EvidenceStreamProps) {
  const [streamData, setStreamData] = useState<EvidenceStreamData | null>(null);
  const [isLive, setIsLive] = useState(true);
  const [selectedCrystalId, setSelectedCrystalId] = useState<string | null>(null);
  const [localFilter, setLocalFilter] = useState<EvidenceFilter>(evidenceFilter);

  // Load initial data
  useEffect(() => {
    setStreamData(generateMockStreamData(gameId));
  }, [gameId]);

  // Simulate live updates
  useEffect(() => {
    if (!isLive || !streamData) return;

    const interval = setInterval(() => {
      setStreamData((prev) => {
        if (!prev) return prev;
        const newLoss = Math.max(0, Math.min(1, prev.currentLoss + (Math.random() - 0.5) * 0.02));
        return {
          ...prev,
          currentLoss: newLoss,
          lossHistory: [
            ...prev.lossHistory.slice(1),
            {
              timestamp: new Date(),
              loss: newLoss,
              contributors: prev.lossHistory[prev.lossHistory.length - 1]?.contributors || [],
            },
          ],
        };
      });
    }, 2000);

    return () => clearInterval(interval);
  }, [isLive, streamData]);

  // Filter crystals
  const filteredCrystals = useMemo(() => {
    if (!streamData) return [];
    let crystals = streamData.crystals;

    if (localFilter.minQuality !== undefined) {
      crystals = crystals.filter((c) => c.overallQuality >= (localFilter.minQuality || 0));
    }

    if (localFilter.axiomIds && localFilter.axiomIds.length > 0) {
      const axiomIds = localFilter.axiomIds;
      crystals = crystals.filter((c) =>
        axiomIds.some((axiomId) => (c.axiomScores[axiomId] || 0) >= 0.8)
      );
    }

    return crystals;
  }, [streamData, localFilter]);

  const handleFilterChange = (filter: EvidenceFilter) => {
    setLocalFilter(filter);
    onFilterChange?.(filter);
  };

  const handleCrystalSelect = (crystalId: string) => {
    setSelectedCrystalId(crystalId);
    onCrystalSelect?.(crystalId);
  };

  const handleRefresh = () => {
    setStreamData(generateMockStreamData(gameId));
  };

  if (!streamData) {
    return (
      <div className="evidence-stream evidence-stream--loading">
        <Activity size={24} className="evidence-stream__loading-icon" />
        <span>Loading evidence stream...</span>
      </div>
    );
  }

  return (
    <div className="evidence-stream">
      {/* Header */}
      <div className="evidence-stream__header">
        <Activity size={14} className="evidence-stream__icon" />
        <span className="evidence-stream__title">Evidence</span>
        <span
          className={`evidence-stream__status ${streamData.isLive && isLive ? 'evidence-stream__status--live' : ''}`}
        >
          {streamData.isLive && isLive ? 'LIVE' : 'PAUSED'}
        </span>
      </div>

      {/* Controls */}
      <div className="evidence-stream__controls">
        <StreamControls
          isLive={isLive}
          onToggleLive={() => setIsLive(!isLive)}
          onRefresh={handleRefresh}
        />
        <FilterPanel filter={localFilter} onFilterChange={handleFilterChange} />
      </div>

      {/* Loss Chart */}
      <LossChart history={streamData.lossHistory} currentLoss={streamData.currentLoss} />

      {/* Crystals */}
      <div className="evidence-stream__section">
        <div className="evidence-stream__section-header">
          <Gem size={12} />
          <span>Quality Crystals</span>
          <span className="evidence-stream__section-count">{filteredCrystals.length}</span>
        </div>

        <div className="evidence-stream__crystals">
          {filteredCrystals.length > 0 ? (
            filteredCrystals.map((crystal) => (
              <CrystalCard
                key={crystal.id}
                crystal={crystal}
                isSelected={selectedCrystalId === crystal.id}
                onSelect={() => handleCrystalSelect(crystal.id)}
              />
            ))
          ) : (
            <div className="evidence-stream__empty">
              <p>No crystals match filters</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
});

export default EvidenceStream;
