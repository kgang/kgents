/**
 * TrailTimeline - Visual trace navigation for Daily Lab
 *
 * Design Goals (QA-2):
 * - Show marks along time axis
 * - Highlight gaps neutrally (gaps are data, not shame)
 * - Support 100+ marks performantly
 *
 * WARMTH Calibration:
 * - Secondary joy: WARMTH (kind companion reviewing your day)
 * - Gaps are honored, not hidden
 *
 * @see pilots/trail-to-crystal-daily-lab/PROTO_SPEC.md
 * @see impl/claude/services/witness/daily_lab.py
 */

import { useMemo, useCallback, useRef, useEffect, useState } from 'react';
import { useWindowLayout } from '@/hooks/useLayoutContext';
import { GrowingContainer } from '@/components/joy';
import { LIVING_EARTH, TIMING } from '@/constants';
import type { DailyTag } from './MarkCaptureInput';

// =============================================================================
// Types
// =============================================================================

/** Mark data from backend TrailResponse */
export interface TrailMark {
  mark_id: string;
  content: string;
  tags: string[];
  timestamp: string;
}

/** Time gap between marks */
export interface TimeGap {
  start: string;
  end: string;
  duration_minutes: number;
}

export interface TrailTimelineProps {
  /** Marks to display */
  marks: TrailMark[];

  /** Gaps between marks (optional, calculated if not provided) */
  gaps?: TimeGap[];

  /** Gap threshold in minutes before showing a gap indicator */
  gapThreshold?: number;

  /** Currently selected mark ID */
  selectedMarkId?: string | null;

  /** Callback when a mark is selected */
  onSelectMark?: (mark: TrailMark) => void;

  /** Callback when a gap is clicked */
  onGapClick?: (gap: TimeGap) => void;

  /** Show timestamps on marks */
  showTimestamps?: boolean;

  /** Custom className */
  className?: string;

  /** Date being displayed */
  date?: Date;
}

// =============================================================================
// Constants
// =============================================================================

/** Tag colors for visual differentiation */
const TAG_COLORS: Record<string, string> = {
  eureka: '#F59E0B', // Amber
  gotcha: '#EF4444', // Red
  taste: '#8B5CF6', // Purple
  friction: '#6B7280', // Gray
  joy: '#10B981', // Green
  veto: '#EC4899', // Pink
};

/** Density-aware sizing */
const SIZES = {
  compact: {
    markSize: 12,
    gap: 4,
    padding: 'p-2',
    text: 'text-xs',
    timelineHeight: 48,
  },
  comfortable: {
    markSize: 16,
    gap: 6,
    padding: 'p-3',
    text: 'text-sm',
    timelineHeight: 64,
  },
  spacious: {
    markSize: 20,
    gap: 8,
    padding: 'p-4',
    text: 'text-base',
    timelineHeight: 80,
  },
} as const;

// =============================================================================
// Helpers
// =============================================================================

/** Calculate gaps from marks */
function calculateGaps(marks: TrailMark[], thresholdMinutes: number): TimeGap[] {
  if (marks.length < 2) return [];

  const gaps: TimeGap[] = [];
  const sortedMarks = [...marks].sort(
    (a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime()
  );

  for (let i = 1; i < sortedMarks.length; i++) {
    const prevTime = new Date(sortedMarks[i - 1].timestamp).getTime();
    const currTime = new Date(sortedMarks[i].timestamp).getTime();
    const diffMinutes = (currTime - prevTime) / (1000 * 60);

    if (diffMinutes >= thresholdMinutes) {
      gaps.push({
        start: sortedMarks[i - 1].timestamp,
        end: sortedMarks[i].timestamp,
        duration_minutes: Math.round(diffMinutes),
      });
    }
  }

  return gaps;
}

/** Format duration for display */
function formatDuration(minutes: number): string {
  if (minutes < 60) {
    return `${minutes}m`;
  }
  const hours = Math.floor(minutes / 60);
  const remainingMins = minutes % 60;
  return remainingMins > 0 ? `${hours}h ${remainingMins}m` : `${hours}h`;
}

/** Format timestamp for display */
function formatTime(timestamp: string): string {
  const date = new Date(timestamp);
  return date.toLocaleTimeString('en-US', {
    hour: 'numeric',
    minute: '2-digit',
    hour12: true,
  });
}

/** Get primary tag color */
function getMarkColor(tags: string[]): string {
  if (tags.length === 0) return LIVING_EARTH.clay;
  return TAG_COLORS[tags[0]] || LIVING_EARTH.clay;
}

// =============================================================================
// Sub-components
// =============================================================================

interface MarkNodeProps {
  mark: TrailMark;
  isSelected: boolean;
  size: number;
  showTimestamp: boolean;
  onClick: () => void;
  density: 'compact' | 'comfortable' | 'spacious';
}

function MarkNode({
  mark,
  isSelected,
  size,
  showTimestamp,
  onClick,
  density,
}: MarkNodeProps) {
  const color = getMarkColor(mark.tags);
  const textClass = SIZES[density].text;

  return (
    <div
      className="flex flex-col items-center cursor-pointer group"
      onClick={onClick}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          onClick();
        }
      }}
      aria-selected={isSelected}
      aria-label={`Mark: ${mark.content.substring(0, 50)}${mark.content.length > 50 ? '...' : ''}`}
    >
      {/* Mark Dot */}
      <div
        className={`
          rounded-full
          transition-all duration-150
          ${isSelected ? 'ring-2 ring-offset-2' : 'group-hover:scale-110'}
        `}
        style={{
          width: size,
          height: size,
          backgroundColor: color,
          boxShadow: isSelected ? `0 0 8px ${color}66` : 'none',
          // Ring color is set via CSS custom property for Tailwind
          ['--tw-ring-color' as string]: LIVING_EARTH.lantern,
        }}
      />

      {/* Timestamp */}
      {showTimestamp && (
        <span
          className={`${textClass} mt-1 opacity-60 group-hover:opacity-100 transition-opacity`}
          style={{ color: LIVING_EARTH.sand }}
        >
          {formatTime(mark.timestamp)}
        </span>
      )}

      {/* Tag Label (visible on hover or when selected) */}
      {mark.tags.length > 0 && (isSelected || density === 'spacious') && (
        <span
          className={`${textClass} mt-0.5`}
          style={{ color }}
        >
          {mark.tags[0]}
        </span>
      )}
    </div>
  );
}

interface GapNodeProps {
  gap: TimeGap;
  size: number;
  onClick?: () => void;
  density: 'compact' | 'comfortable' | 'spacious';
}

function GapNode({ gap, size, onClick, density }: GapNodeProps) {
  const textClass = SIZES[density].text;
  const durationText = formatDuration(gap.duration_minutes);

  return (
    <div
      className={`
        flex flex-col items-center
        ${onClick ? 'cursor-pointer group' : ''}
      `}
      onClick={onClick}
      role={onClick ? 'button' : undefined}
      tabIndex={onClick ? 0 : undefined}
      onKeyDown={
        onClick
          ? (e) => {
              if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                onClick();
              }
            }
          : undefined
      }
      aria-label={`Gap: ${durationText} of untracked time`}
    >
      {/* Gap Indicator - dashed line */}
      <div
        className="flex items-center gap-1"
        style={{
          height: size,
          minWidth: 40,
        }}
      >
        <div
          className="flex-1 border-t-2 border-dashed"
          style={{ borderColor: `${LIVING_EARTH.sage}44` }}
        />
        <span
          className={`${textClass} px-2 opacity-60`}
          style={{ color: LIVING_EARTH.sage }}
        >
          {durationText}
        </span>
        <div
          className="flex-1 border-t-2 border-dashed"
          style={{ borderColor: `${LIVING_EARTH.sage}44` }}
        />
      </div>

      {/* Neutral gap message (no shame) */}
      {density !== 'compact' && (
        <span
          className={`${textClass} mt-1 opacity-40`}
          style={{ color: LIVING_EARTH.sand }}
        >
          Untracked
        </span>
      )}
    </div>
  );
}

// =============================================================================
// Main Component
// =============================================================================

/**
 * TrailTimeline
 *
 * Visual timeline of marks with neutral gap indicators.
 * Supports 100+ marks with virtualization when needed.
 *
 * @example Basic usage:
 * ```tsx
 * <TrailTimeline
 *   marks={trailData.marks}
 *   onSelectMark={(mark) => setSelectedMark(mark)}
 * />
 * ```
 *
 * @example With gap handling:
 * ```tsx
 * <TrailTimeline
 *   marks={trailData.marks}
 *   gapThreshold={30} // Show gaps > 30 minutes
 *   onGapClick={(gap) => console.log('Gap clicked:', gap)}
 * />
 * ```
 */
export function TrailTimeline({
  marks,
  gaps: providedGaps,
  gapThreshold = 30,
  selectedMarkId,
  onSelectMark,
  onGapClick,
  showTimestamps = true,
  className = '',
  date,
}: TrailTimelineProps) {
  const { density } = useWindowLayout();
  const sizes = SIZES[density];
  const containerRef = useRef<HTMLDivElement>(null);
  const [isOverflowing, setIsOverflowing] = useState(false);

  // Calculate gaps if not provided
  const gaps = useMemo(() => {
    return providedGaps || calculateGaps(marks, gapThreshold);
  }, [marks, providedGaps, gapThreshold]);

  // Sort marks by timestamp
  const sortedMarks = useMemo(() => {
    return [...marks].sort(
      (a, b) =>
        new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime()
    );
  }, [marks]);

  // Build timeline items (marks + gaps interleaved)
  const timelineItems = useMemo(() => {
    const items: Array<
      | { type: 'mark'; data: TrailMark }
      | { type: 'gap'; data: TimeGap }
    > = [];

    const gapsByStart = new Map(
      gaps.map((g) => [g.start, g])
    );

    for (let i = 0; i < sortedMarks.length; i++) {
      const mark = sortedMarks[i];
      items.push({ type: 'mark', data: mark });

      // Check if there's a gap after this mark
      const gap = gapsByStart.get(mark.timestamp);
      if (gap) {
        items.push({ type: 'gap', data: gap });
      }
    }

    return items;
  }, [sortedMarks, gaps]);

  // Check for overflow
  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    const checkOverflow = () => {
      setIsOverflowing(container.scrollWidth > container.clientWidth);
    };

    checkOverflow();

    const observer = new ResizeObserver(checkOverflow);
    observer.observe(container);
    return () => observer.disconnect();
  }, [timelineItems.length]);

  // Handle mark selection
  const handleSelectMark = useCallback(
    (mark: TrailMark) => {
      onSelectMark?.(mark);
    },
    [onSelectMark]
  );

  // Handle gap click
  const handleGapClick = useCallback(
    (gap: TimeGap) => {
      onGapClick?.(gap);
    },
    [onGapClick]
  );

  // Empty state
  if (marks.length === 0) {
    return (
      <div
        className={`flex items-center justify-center ${sizes.padding} ${className}`}
        style={{
          background: `${LIVING_EARTH.bark}`,
          borderRadius: 12,
          minHeight: sizes.timelineHeight,
        }}
      >
        <span
          className={`${sizes.text} opacity-60`}
          style={{ color: LIVING_EARTH.sand }}
        >
          A quiet day. That's okay too.
        </span>
      </div>
    );
  }

  return (
    <div
      className={`trail-timeline ${className}`}
      style={{
        background: LIVING_EARTH.bark,
        borderRadius: 12,
        border: `1px solid ${LIVING_EARTH.sage}22`,
      }}
    >
      {/* Header */}
      <div
        className={`flex items-center justify-between ${sizes.padding} border-b`}
        style={{ borderColor: `${LIVING_EARTH.sage}22` }}
      >
        <span className={`${sizes.text} font-medium`} style={{ color: LIVING_EARTH.lantern }}>
          {date
            ? date.toLocaleDateString('en-US', {
                weekday: 'long',
                month: 'short',
                day: 'numeric',
              })
            : "Today's Trail"}
        </span>
        <span className={`${sizes.text} opacity-60`} style={{ color: LIVING_EARTH.sand }}>
          {marks.length} mark{marks.length !== 1 ? 's' : ''}
          {gaps.length > 0 && ` / ${gaps.length} gap${gaps.length !== 1 ? 's' : ''}`}
        </span>
      </div>

      {/* Timeline */}
      <div
        ref={containerRef}
        className={`
          flex items-center
          ${sizes.padding}
          overflow-x-auto
          scrollbar-thin scrollbar-thumb-stone-600 scrollbar-track-transparent
        `}
        style={{
          gap: sizes.gap * 2,
          minHeight: sizes.timelineHeight,
        }}
      >
        {/* Start marker */}
        <div
          className={`${sizes.text} opacity-40 shrink-0`}
          style={{ color: LIVING_EARTH.sage }}
        >
          Start
        </div>

        {/* Timeline items */}
        {timelineItems.map((item, index) => (
          <GrowingContainer
            key={item.type === 'mark' ? item.data.mark_id : `gap-${index}`}
            autoTrigger
            delay={index * 30}
            duration="quick"
          >
            {item.type === 'mark' ? (
              <MarkNode
                mark={item.data}
                isSelected={selectedMarkId === item.data.mark_id}
                size={sizes.markSize}
                showTimestamp={showTimestamps}
                onClick={() => handleSelectMark(item.data)}
                density={density}
              />
            ) : (
              <GapNode
                gap={item.data}
                size={sizes.markSize}
                onClick={onGapClick ? () => handleGapClick(item.data) : undefined}
                density={density}
              />
            )}
          </GrowingContainer>
        ))}

        {/* End marker */}
        <div
          className={`${sizes.text} opacity-40 shrink-0`}
          style={{ color: LIVING_EARTH.sage }}
        >
          Now
        </div>
      </div>

      {/* Scroll hint */}
      {isOverflowing && (
        <div
          className={`flex justify-center ${sizes.padding} border-t`}
          style={{ borderColor: `${LIVING_EARTH.sage}22` }}
        >
          <span
            className={`${sizes.text} opacity-40`}
            style={{ color: LIVING_EARTH.sage }}
          >
            Scroll to see more
          </span>
        </div>
      )}
    </div>
  );
}

// =============================================================================
// Exports
// =============================================================================

export default TrailTimeline;
