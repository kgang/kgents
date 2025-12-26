/**
 * CoherenceTimeline — Coherence Journey Visualization
 *
 * Journey 5: Meta — Watching Yourself Grow
 *
 * Features:
 * - Line graph showing coherence score over time
 * - Hover tooltips with commit details
 * - Breakthrough badges (🏆) at significant jumps
 * - Layer distribution pie chart tab
 * - Export to markdown + SVG
 *
 * STARK BIOME aesthetic: 90% steel, 10% earned glow
 */

import { memo, useMemo, useState, useRef } from 'react';
import './CoherenceTimeline.css';

// =============================================================================
// Types
// =============================================================================

export interface CoherencePoint {
  timestamp: Date;
  score: number;
  commitId?: string;
  breakthrough?: boolean;
  layerDistribution: Record<number, number>;
}

export interface CoherenceTimelineProps {
  points: CoherencePoint[];
  width?: number;
  height?: number;
  className?: string;
}

type ViewMode = 'timeline' | 'distribution';

// =============================================================================
// Helpers
// =============================================================================

function formatDate(date: Date): string {
  return date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

function formatScore(score: number): string {
  return (score * 100).toFixed(1);
}

function calculateBreakthroughThreshold(points: CoherencePoint[]): number {
  if (points.length < 2) return 0;
  const deltas = points.slice(1).map((p, i) => p.score - points[i].score);
  const avgDelta = deltas.reduce((sum, d) => sum + Math.abs(d), 0) / deltas.length;
  return avgDelta * 2; // 2x average change = breakthrough
}

// =============================================================================
// Subcomponents
// =============================================================================

interface TooltipProps {
  point: CoherencePoint;
  x: number;
  y: number;
}

const Tooltip = memo(function Tooltip({ point, x, y }: TooltipProps) {
  return (
    <div
      className="coherence-timeline__tooltip"
      style={{
        left: `${x}px`,
        top: `${y - 80}px`,
      }}
    >
      <div className="coherence-timeline__tooltip-score">
        {formatScore(point.score)}%
      </div>
      <div className="coherence-timeline__tooltip-date">
        {formatDate(point.timestamp)}
      </div>
      {point.commitId && (
        <div className="coherence-timeline__tooltip-commit">
          {point.commitId.substring(0, 7)}
        </div>
      )}
      {point.breakthrough && (
        <div className="coherence-timeline__tooltip-breakthrough">
          🏆 Breakthrough
        </div>
      )}
    </div>
  );
});

interface LayerDistributionProps {
  distribution: Record<number, number>;
}

const LayerDistribution = memo(function LayerDistribution({
  distribution,
}: LayerDistributionProps) {
  const total = Object.values(distribution).reduce((sum, count) => sum + count, 0);
  const layers = Object.entries(distribution)
    .map(([layer, count]) => ({
      layer: parseInt(layer, 10),
      count,
      percentage: (count / total) * 100,
    }))
    .sort((a, b) => a.layer - b.layer);

  // Simple arc calculation for pie chart
  let currentAngle = -90; // Start at top
  const arcs = layers.map(({ layer, count, percentage }) => {
    const sweepAngle = (percentage / 100) * 360;
    const arc = {
      layer,
      count,
      percentage,
      startAngle: currentAngle,
      endAngle: currentAngle + sweepAngle,
    };
    currentAngle += sweepAngle;
    return arc;
  });

  const getLayerColor = (layer: number): string => {
    const colors = [
      'var(--color-steel-300)', // Layer 0
      'var(--color-life-sage)', // Layer 1
      'var(--color-glow-lichen)', // Layer 2
      'var(--color-glow-spore)', // Layer 3
      'var(--color-glow-amber)', // Layer 4+
    ];
    return colors[Math.min(layer, colors.length - 1)];
  };

  const polarToCartesian = (
    centerX: number,
    centerY: number,
    radius: number,
    angleInDegrees: number
  ) => {
    const angleInRadians = (angleInDegrees * Math.PI) / 180.0;
    return {
      x: centerX + radius * Math.cos(angleInRadians),
      y: centerY + radius * Math.sin(angleInRadians),
    };
  };

  const describeArc = (
    x: number,
    y: number,
    radius: number,
    startAngle: number,
    endAngle: number
  ) => {
    const start = polarToCartesian(x, y, radius, endAngle);
    const end = polarToCartesian(x, y, radius, startAngle);
    const largeArcFlag = endAngle - startAngle <= 180 ? '0' : '1';
    return [
      'M',
      x,
      y,
      'L',
      start.x,
      start.y,
      'A',
      radius,
      radius,
      0,
      largeArcFlag,
      0,
      end.x,
      end.y,
      'Z',
    ].join(' ');
  };

  const centerX = 120;
  const centerY = 120;
  const radius = 100;

  return (
    <div className="coherence-timeline__distribution">
      <svg width="240" height="240" viewBox="0 0 240 240">
        {arcs.map((arc) => (
          <path
            key={arc.layer}
            d={describeArc(centerX, centerY, radius, arc.startAngle, arc.endAngle)}
            fill={getLayerColor(arc.layer)}
            stroke="var(--surface-0)"
            strokeWidth="2"
            className="coherence-timeline__distribution-arc"
          />
        ))}
      </svg>
      <div className="coherence-timeline__distribution-legend">
        {layers.map(({ layer, count, percentage }) => (
          <div key={layer} className="coherence-timeline__distribution-legend-item">
            <div
              className="coherence-timeline__distribution-legend-color"
              style={{ background: getLayerColor(layer) }}
            />
            <span className="coherence-timeline__distribution-legend-label">
              Layer {layer}
            </span>
            <span className="coherence-timeline__distribution-legend-value">
              {count} ({percentage.toFixed(1)}%)
            </span>
          </div>
        ))}
      </div>
    </div>
  );
});

// =============================================================================
// Main Component
// =============================================================================

export const CoherenceTimeline = memo(function CoherenceTimeline({
  points,
  width = 800,
  height = 400,
  className = '',
}: CoherenceTimelineProps) {
  const [viewMode, setViewMode] = useState<ViewMode>('timeline');
  const [hoveredIndex, setHoveredIndex] = useState<number | null>(null);
  const svgRef = useRef<SVGSVGElement>(null);

  const padding = { top: 40, right: 40, bottom: 60, left: 60 };
  const chartWidth = width - padding.left - padding.right;
  const chartHeight = height - padding.top - padding.bottom;

  // Sort points by timestamp
  const sortedPoints = useMemo(() => {
    return [...points].sort((a, b) => a.timestamp.getTime() - b.timestamp.getTime());
  }, [points]);

  // Calculate breakthrough threshold
  const breakthroughThreshold = useMemo(() => {
    return calculateBreakthroughThreshold(sortedPoints);
  }, [sortedPoints]);

  // Mark breakthroughs
  const enrichedPoints = useMemo(() => {
    return sortedPoints.map((point, i) => {
      if (i === 0) return { ...point, breakthrough: false };
      const delta = point.score - sortedPoints[i - 1].score;
      return {
        ...point,
        breakthrough: delta > breakthroughThreshold,
      };
    });
  }, [sortedPoints, breakthroughThreshold]);

  // Calculate scales
  const { xScale, yScale } = useMemo(() => {
    if (enrichedPoints.length === 0) {
      return { xScale: () => 0, yScale: () => 0 };
    }

    const minTime = enrichedPoints[0].timestamp.getTime();
    const maxTime = enrichedPoints[enrichedPoints.length - 1].timestamp.getTime();
    const minScore = Math.min(...enrichedPoints.map((p) => p.score));
    const maxScore = Math.max(...enrichedPoints.map((p) => p.score));

    const xScale = (time: number) => {
      if (maxTime === minTime) return chartWidth / 2;
      return ((time - minTime) / (maxTime - minTime)) * chartWidth;
    };

    const yScale = (score: number) => {
      const range = maxScore - minScore || 0.1; // Avoid division by zero
      return chartHeight - ((score - minScore) / range) * chartHeight;
    };

    return { xScale, yScale };
  }, [enrichedPoints, chartWidth, chartHeight]);

  // Generate SVG path
  const linePath = useMemo(() => {
    if (enrichedPoints.length === 0) return '';

    const pathParts = enrichedPoints.map((point, i) => {
      const x = xScale(point.timestamp.getTime());
      const y = yScale(point.score);
      return i === 0 ? `M ${x} ${y}` : `L ${x} ${y}`;
    });

    return pathParts.join(' ');
  }, [enrichedPoints, xScale, yScale]);

  // Aggregate layer distribution across all points
  const totalDistribution = useMemo(() => {
    const dist: Record<number, number> = {};
    enrichedPoints.forEach((point) => {
      Object.entries(point.layerDistribution).forEach(([layer, count]) => {
        const layerNum = parseInt(layer, 10);
        dist[layerNum] = (dist[layerNum] || 0) + count;
      });
    });
    return dist;
  }, [enrichedPoints]);

  // Export handlers
  const handleExportSVG = () => {
    if (!svgRef.current) return;
    const svgData = new XMLSerializer().serializeToString(svgRef.current);
    const blob = new Blob([svgData], { type: 'image/svg+xml;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'coherence-timeline.svg';
    link.click();
    URL.revokeObjectURL(url);
  };

  const handleExportMarkdown = () => {
    const md = [
      '# Coherence Timeline',
      '',
      '## Summary',
      `- Total Points: ${enrichedPoints.length}`,
      `- Current Score: ${formatScore(enrichedPoints[enrichedPoints.length - 1]?.score || 0)}%`,
      `- Breakthroughs: ${enrichedPoints.filter((p) => p.breakthrough).length}`,
      '',
      '## Timeline',
      '',
      ...enrichedPoints.map((point) => {
        const icon = point.breakthrough ? '🏆 ' : '';
        return `- ${icon}${formatDate(point.timestamp)}: ${formatScore(point.score)}% ${
          point.commitId ? `(${point.commitId.substring(0, 7)})` : ''
        }`;
      }),
      '',
      '## Layer Distribution',
      '',
      ...Object.entries(totalDistribution)
        .sort(([a], [b]) => parseInt(a, 10) - parseInt(b, 10))
        .map(([layer, count]) => `- Layer ${layer}: ${count}`),
    ].join('\n');

    const blob = new Blob([md], { type: 'text/markdown;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'coherence-timeline.md';
    link.click();
    URL.revokeObjectURL(url);
  };

  if (enrichedPoints.length === 0) {
    return (
      <div className={`coherence-timeline coherence-timeline--empty ${className}`}>
        <div className="coherence-timeline__empty-state">
          No coherence data available
        </div>
      </div>
    );
  }

  return (
    <div className={`coherence-timeline ${className}`}>
      {/* Header */}
      <div className="coherence-timeline__header">
        <div className="coherence-timeline__tabs">
          <button
            className={`coherence-timeline__tab ${
              viewMode === 'timeline' ? 'coherence-timeline__tab--active' : ''
            }`}
            onClick={() => setViewMode('timeline')}
          >
            Timeline
          </button>
          <button
            className={`coherence-timeline__tab ${
              viewMode === 'distribution' ? 'coherence-timeline__tab--active' : ''
            }`}
            onClick={() => setViewMode('distribution')}
          >
            Distribution
          </button>
        </div>

        <div className="coherence-timeline__actions">
          <button className="coherence-timeline__action" onClick={handleExportMarkdown}>
            Export MD
          </button>
          <button className="coherence-timeline__action" onClick={handleExportSVG}>
            Export SVG
          </button>
        </div>
      </div>

      {/* Content */}
      {viewMode === 'timeline' ? (
        <div className="coherence-timeline__chart">
          <svg
            ref={svgRef}
            width={width}
            height={height}
            className="coherence-timeline__svg"
            onMouseLeave={() => setHoveredIndex(null)}
          >
            {/* Background grid */}
            <g className="coherence-timeline__grid">
              {[0, 0.25, 0.5, 0.75, 1].map((score) => (
                <line
                  key={score}
                  x1={padding.left}
                  y1={padding.top + yScale(score)}
                  x2={width - padding.right}
                  y2={padding.top + yScale(score)}
                  stroke="var(--surface-3)"
                  strokeWidth="1"
                  strokeDasharray="4 4"
                />
              ))}
            </g>

            {/* Line path */}
            <g transform={`translate(${padding.left}, ${padding.top})`}>
              <path
                d={linePath}
                fill="none"
                stroke="var(--color-life-sage)"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
                className="coherence-timeline__line"
              />

              {/* Data points */}
              {enrichedPoints.map((point, i) => {
                const x = xScale(point.timestamp.getTime());
                const y = yScale(point.score);
                const isHovered = hoveredIndex === i;

                return (
                  <g key={i}>
                    {/* Point circle */}
                    <circle
                      cx={x}
                      cy={y}
                      r={point.breakthrough ? 8 : 5}
                      fill={
                        point.breakthrough
                          ? 'var(--color-glow-amber)'
                          : 'var(--color-life-sage)'
                      }
                      stroke="var(--surface-0)"
                      strokeWidth="2"
                      className={`coherence-timeline__point ${
                        isHovered ? 'coherence-timeline__point--hovered' : ''
                      }`}
                      onMouseEnter={() => setHoveredIndex(i)}
                    />

                    {/* Breakthrough badge */}
                    {point.breakthrough && (
                      <text
                        x={x}
                        y={y - 20}
                        textAnchor="middle"
                        fontSize="16"
                        className="coherence-timeline__breakthrough-badge"
                      >
                        🏆
                      </text>
                    )}
                  </g>
                );
              })}
            </g>

            {/* Y-axis labels */}
            <g>
              {[0, 0.25, 0.5, 0.75, 1].map((score) => (
                <text
                  key={score}
                  x={padding.left - 10}
                  y={padding.top + yScale(score)}
                  textAnchor="end"
                  alignmentBaseline="middle"
                  fontSize="12"
                  fill="var(--text-muted)"
                  fontFamily="var(--font-mono)"
                >
                  {formatScore(score)}%
                </text>
              ))}
            </g>

            {/* X-axis labels (first and last) */}
            <g>
              <text
                x={padding.left}
                y={height - padding.bottom + 20}
                textAnchor="start"
                fontSize="12"
                fill="var(--text-muted)"
                fontFamily="var(--font-mono)"
              >
                {formatDate(enrichedPoints[0].timestamp)}
              </text>
              <text
                x={width - padding.right}
                y={height - padding.bottom + 20}
                textAnchor="end"
                fontSize="12"
                fill="var(--text-muted)"
                fontFamily="var(--font-mono)"
              >
                {formatDate(enrichedPoints[enrichedPoints.length - 1].timestamp)}
              </text>
            </g>
          </svg>

          {/* Tooltip */}
          {hoveredIndex !== null && (
            <Tooltip
              point={enrichedPoints[hoveredIndex]}
              x={padding.left + xScale(enrichedPoints[hoveredIndex].timestamp.getTime())}
              y={padding.top + yScale(enrichedPoints[hoveredIndex].score)}
            />
          )}
        </div>
      ) : (
        <LayerDistribution distribution={totalDistribution} />
      )}
    </div>
  );
});

export default CoherenceTimeline;
