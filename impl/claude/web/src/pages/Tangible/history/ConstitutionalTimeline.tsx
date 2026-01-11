/**
 * ConstitutionalTimeline - Main Timeline Visualization
 *
 * Horizontal or vertical timeline showing constitutional moments.
 * Moments are color-coded by impact level with hover preview and click to expand.
 *
 * STARK BIOME: 90% steel, 10% earned amber glow for significant moments.
 */

import { memo, useMemo } from 'react';
import { GitBranch, GitCommit, RefreshCw, Sparkles, AlertTriangle } from 'lucide-react';

import type { ConstitutionalMoment, TimeZoom } from './types';
import { HISTORY_LAYER_COLORS, IMPACT_COLORS, MOMENT_TYPE_LABELS } from './types';

// =============================================================================
// Types
// =============================================================================

interface ConstitutionalTimelineProps {
  moments: ConstitutionalMoment[];
  selectedMoment: string | null;
  onMomentSelect: (id: string) => void;
  zoom: TimeZoom;
}

// =============================================================================
// Helpers
// =============================================================================

function formatDate(timestamp: string): string {
  const date = new Date(timestamp);
  return date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  });
}

// formatTime is available for future use in expanded timeline views
function _formatTime(timestamp: string): string {
  const date = new Date(timestamp);
  return date.toLocaleTimeString('en-US', {
    hour: '2-digit',
    minute: '2-digit',
  });
}

function getTypeIcon(type: ConstitutionalMoment['type']) {
  switch (type) {
    case 'genesis':
      return Sparkles;
    case 'amendment':
      return GitCommit;
    case 'derivation_added':
      return GitBranch;
    case 'drift_correction':
      return RefreshCw;
    default:
      return GitCommit;
  }
}

// =============================================================================
// Timeline Node Component
// =============================================================================

interface TimelineNodeProps {
  moment: ConstitutionalMoment;
  isSelected: boolean;
  onClick: () => void;
}

const TimelineNode = memo(function TimelineNode({
  moment,
  isSelected,
  onClick,
}: TimelineNodeProps) {
  const Icon = getTypeIcon(moment.type);
  const layerColor =
    HISTORY_LAYER_COLORS[moment.layer as keyof typeof HISTORY_LAYER_COLORS] ||
    HISTORY_LAYER_COLORS[4];
  const impactColor = IMPACT_COLORS[moment.impact];

  return (
    <button
      className={`timeline-node ${isSelected ? 'timeline-node--selected' : ''}`}
      onClick={onClick}
      data-type={moment.type}
      data-impact={moment.impact}
      style={
        {
          '--layer-color': layerColor,
          '--impact-color': impactColor,
        } as React.CSSProperties
      }
    >
      <div className="timeline-node__dot">
        <Icon size={12} className="timeline-node__icon" />
      </div>
      <div className="timeline-node__content">
        <div className="timeline-node__header">
          <span className="timeline-node__layer">L{moment.layer}</span>
          <span className="timeline-node__type">{MOMENT_TYPE_LABELS[moment.type]}</span>
          <span className="timeline-node__date">{formatDate(moment.timestamp)}</span>
        </div>
        <div className="timeline-node__title">{moment.title}</div>
        <div className="timeline-node__description">{moment.description}</div>
        <div className="timeline-node__meta">
          {moment.commitSha && (
            <span className="timeline-node__commit">
              <GitCommit size={10} />
              {moment.commitSha.slice(0, 7)}
            </span>
          )}
          {moment.author && <span className="timeline-node__author">{moment.author}</span>}
          {moment.impact === 'constitutional' && (
            <span className="timeline-node__badge timeline-node__badge--constitutional">
              <AlertTriangle size={10} />
              Constitutional
            </span>
          )}
        </div>
      </div>
    </button>
  );
});

// =============================================================================
// Timeline Group (by date)
// =============================================================================

interface TimelineGroupProps {
  date: string;
  moments: ConstitutionalMoment[];
  selectedMoment: string | null;
  onMomentSelect: (id: string) => void;
}

const TimelineGroup = memo(function TimelineGroup({
  date,
  moments,
  selectedMoment,
  onMomentSelect,
}: TimelineGroupProps) {
  return (
    <div className="timeline-group">
      <div className="timeline-group__header">
        <span className="timeline-group__date">{date}</span>
        <span className="timeline-group__count">{moments.length} changes</span>
      </div>
      <div className="timeline-group__nodes">
        {moments.map((moment) => (
          <TimelineNode
            key={moment.id}
            moment={moment}
            isSelected={selectedMoment === moment.id}
            onClick={() => onMomentSelect(moment.id)}
          />
        ))}
      </div>
    </div>
  );
});

// =============================================================================
// Main Component
// =============================================================================

export const ConstitutionalTimeline = memo(function ConstitutionalTimeline({
  moments,
  selectedMoment,
  onMomentSelect,
  zoom,
}: ConstitutionalTimelineProps) {
  // Group moments by date
  const groupedMoments = useMemo(() => {
    const groups: Record<string, ConstitutionalMoment[]> = {};

    moments.forEach((moment) => {
      const date = formatDate(moment.timestamp);
      if (!groups[date]) {
        groups[date] = [];
      }
      groups[date].push(moment);
    });

    // Sort groups by date descending
    return Object.entries(groups).sort((a, b) => {
      const dateA = new Date(a[1][0].timestamp);
      const dateB = new Date(b[1][0].timestamp);
      return dateB.getTime() - dateA.getTime();
    });
  }, [moments]);

  // Filter by zoom level
  const filteredGroups = useMemo(() => {
    const now = new Date();
    const cutoff = new Date();

    switch (zoom) {
      case '1D':
        cutoff.setDate(now.getDate() - 1);
        break;
      case '1W':
        cutoff.setDate(now.getDate() - 7);
        break;
      case '1M':
        cutoff.setMonth(now.getMonth() - 1);
        break;
      case 'ALL':
      default:
        return groupedMoments;
    }

    return groupedMoments.filter(([, moments]) => {
      const groupDate = new Date(moments[0].timestamp);
      return groupDate >= cutoff;
    });
  }, [groupedMoments, zoom]);

  if (filteredGroups.length === 0) {
    return (
      <div className="timeline-empty">
        <GitBranch size={32} className="timeline-empty__icon" />
        <p className="timeline-empty__text">No constitutional changes in this time range</p>
        <p className="timeline-empty__hint">Try adjusting the filters or zoom level</p>
      </div>
    );
  }

  return (
    <div className="constitutional-timeline">
      {/* Timeline Track */}
      <div className="constitutional-timeline__track" />

      {/* Timeline Nodes */}
      <div className="constitutional-timeline__nodes">
        {filteredGroups.map(([date, moments]) => (
          <TimelineGroup
            key={date}
            date={date}
            moments={moments}
            selectedMoment={selectedMoment}
            onMomentSelect={onMomentSelect}
          />
        ))}
      </div>

      {/* Timeline Legend */}
      <div className="constitutional-timeline__legend">
        <div className="timeline-legend__title">Impact Level</div>
        <div className="timeline-legend__items">
          {(['constitutional', 'significant', 'moderate', 'minor'] as const).map((impact) => (
            <div key={impact} className="timeline-legend__item">
              <span
                className="timeline-legend__dot"
                style={{ background: IMPACT_COLORS[impact] }}
              />
              <span className="timeline-legend__label">{impact}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
});
