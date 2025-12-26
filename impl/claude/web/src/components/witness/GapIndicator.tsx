/**
 * GapIndicator - Neutral gap display for Daily Lab
 *
 * Design Goals (QA-2):
 * - Display gaps neutrally (gaps are data, not shame)
 * - "Untracked time: 2h. Noted, not judged."
 * - NO shame mechanics
 *
 * Philosophy:
 * - Gaps are honored, not hidden
 * - Untracked time is signal, not failure
 * - The system is descriptive, not punitive
 *
 * @see pilots/trail-to-crystal-daily-lab/PROTO_SPEC.md
 * @see impl/claude/services/witness/daily_lab.py
 */

import { useMemo } from 'react';
import { useWindowLayout } from '@/hooks/useLayoutContext';
import { GrowingContainer } from '@/components/joy';
import { LIVING_EARTH } from '@/constants';

// =============================================================================
// Types
// =============================================================================

/** Time gap data */
export interface TimeGap {
  start: string;
  end: string;
  duration_minutes: number;
}

export interface GapIndicatorProps {
  /** The gap to display */
  gap: TimeGap;

  /** Display variant */
  variant?: 'inline' | 'card' | 'minimal';

  /** Show time range */
  showTimeRange?: boolean;

  /** Callback when gap is clicked */
  onClick?: (gap: TimeGap) => void;

  /** Custom className */
  className?: string;

  /** Custom message override */
  message?: string;
}

// =============================================================================
// Constants
// =============================================================================

/** Neutral gap messages - NO judgment, just observation */
const GAP_MESSAGES = {
  short: [
    'A brief pause.',
    'Short break noted.',
    'A moment away.',
  ],
  medium: [
    'Untracked time. That happens.',
    'Time passed. Noted.',
    'Some time went unrecorded.',
  ],
  long: [
    'Extended time away. That\'s okay.',
    'A longer gap. Rest is valid.',
    'Untracked hours. This is data, not judgment.',
  ],
};

/** Density-aware sizing */
const SIZES = {
  compact: {
    padding: 'p-2',
    text: 'text-xs',
    iconSize: 14,
  },
  comfortable: {
    padding: 'p-3',
    text: 'text-sm',
    iconSize: 16,
  },
  spacious: {
    padding: 'p-4',
    text: 'text-base',
    iconSize: 18,
  },
} as const;

// =============================================================================
// Helpers
// =============================================================================

/** Format duration for display */
function formatDuration(minutes: number): string {
  if (minutes < 60) {
    return `${minutes} minute${minutes !== 1 ? 's' : ''}`;
  }
  const hours = Math.floor(minutes / 60);
  const remainingMins = minutes % 60;
  if (remainingMins === 0) {
    return `${hours} hour${hours !== 1 ? 's' : ''}`;
  }
  return `${hours}h ${remainingMins}m`;
}

/** Format time for display */
function formatTime(timestamp: string): string {
  const date = new Date(timestamp);
  return date.toLocaleTimeString('en-US', {
    hour: 'numeric',
    minute: '2-digit',
    hour12: true,
  });
}

/** Get a neutral message based on gap duration */
function getNeutralMessage(minutes: number): string {
  let messages: string[];
  if (minutes < 30) {
    messages = GAP_MESSAGES.short;
  } else if (minutes < 120) {
    messages = GAP_MESSAGES.medium;
  } else {
    messages = GAP_MESSAGES.long;
  }
  // Deterministic selection based on minutes for consistency
  return messages[minutes % messages.length];
}

/** Get the gap category */
function getGapCategory(minutes: number): 'short' | 'medium' | 'long' {
  if (minutes < 30) return 'short';
  if (minutes < 120) return 'medium';
  return 'long';
}

// =============================================================================
// Sub-components
// =============================================================================

interface GapIconProps {
  size: number;
  category: 'short' | 'medium' | 'long';
}

function GapIcon({ size, category }: GapIconProps) {
  // Different icons for different gap lengths - all neutral
  const paths: Record<typeof category, string> = {
    short: 'M5 12h14', // Simple dash
    medium: 'M5 12h14 M12 5v14', // Cross/plus
    long: 'M5 12h14 M9 5v14 M15 5v14', // Triple lines
  };

  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke={LIVING_EARTH.sage}
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      opacity={0.6}
    >
      <path d={paths[category]} />
    </svg>
  );
}

// =============================================================================
// Main Component
// =============================================================================

/**
 * GapIndicator
 *
 * Neutral display of untracked time periods.
 * NO shame mechanics - gaps are data, not failure.
 *
 * @example Inline usage (within timeline):
 * ```tsx
 * <GapIndicator gap={timeGap} variant="inline" />
 * ```
 *
 * @example Card usage (standalone):
 * ```tsx
 * <GapIndicator
 *   gap={timeGap}
 *   variant="card"
 *   showTimeRange
 *   onClick={(gap) => console.log('Gap:', gap)}
 * />
 * ```
 *
 * @example Minimal usage (summary):
 * ```tsx
 * <GapIndicator
 *   gap={timeGap}
 *   variant="minimal"
 *   message="2 hours untracked today"
 * />
 * ```
 */
export function GapIndicator({
  gap,
  variant = 'card',
  showTimeRange = false,
  onClick,
  className = '',
  message,
}: GapIndicatorProps) {
  const { density } = useWindowLayout();
  const sizes = SIZES[density];

  // Calculate gap properties
  const durationText = useMemo(
    () => formatDuration(gap.duration_minutes),
    [gap.duration_minutes]
  );

  const timeRange = useMemo(
    () => `${formatTime(gap.start)} - ${formatTime(gap.end)}`,
    [gap.start, gap.end]
  );

  const neutralMessage = useMemo(
    () => message || getNeutralMessage(gap.duration_minutes),
    [message, gap.duration_minutes]
  );

  const category = useMemo(
    () => getGapCategory(gap.duration_minutes),
    [gap.duration_minutes]
  );

  // Handle click
  const handleClick = () => {
    onClick?.(gap);
  };

  // Minimal variant
  if (variant === 'minimal') {
    return (
      <span
        className={`${sizes.text} ${className}`}
        style={{ color: LIVING_EARTH.sage }}
      >
        {durationText} untracked
      </span>
    );
  }

  // Inline variant (for timeline)
  if (variant === 'inline') {
    return (
      <div
        className={`
          flex items-center gap-2
          ${onClick ? 'cursor-pointer hover:opacity-100' : ''}
          opacity-60
          transition-opacity
          ${className}
        `}
        onClick={onClick ? handleClick : undefined}
        role={onClick ? 'button' : undefined}
        tabIndex={onClick ? 0 : undefined}
        onKeyDown={
          onClick
            ? (e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                  e.preventDefault();
                  handleClick();
                }
              }
            : undefined
        }
        aria-label={`${durationText} gap`}
      >
        {/* Dashed line */}
        <div
          className="flex-1 border-t-2 border-dashed"
          style={{ borderColor: `${LIVING_EARTH.sage}44` }}
        />

        {/* Duration badge */}
        <span
          className={`${sizes.text} px-2`}
          style={{ color: LIVING_EARTH.sage }}
        >
          {durationText}
        </span>

        {/* Dashed line */}
        <div
          className="flex-1 border-t-2 border-dashed"
          style={{ borderColor: `${LIVING_EARTH.sage}44` }}
        />
      </div>
    );
  }

  // Card variant (default)
  return (
    <GrowingContainer autoTrigger duration="quick">
      <div
        className={`
          gap-indicator
          ${sizes.padding}
          rounded-lg
          ${onClick ? 'cursor-pointer' : ''}
          transition-all duration-150
          ${className}
        `}
        style={{
          background: `${LIVING_EARTH.sage}11`,
          border: `1px dashed ${LIVING_EARTH.sage}33`,
        }}
        onClick={onClick ? handleClick : undefined}
        role={onClick ? 'button' : undefined}
        tabIndex={onClick ? 0 : undefined}
        onKeyDown={
          onClick
            ? (e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                  e.preventDefault();
                  handleClick();
                }
              }
            : undefined
        }
      >
        <div className="flex items-start gap-3">
          {/* Icon */}
          <GapIcon size={sizes.iconSize} category={category} />

          {/* Content */}
          <div className="flex-1">
            {/* Duration */}
            <div
              className={`${sizes.text} font-medium`}
              style={{ color: LIVING_EARTH.sand }}
            >
              {durationText}
            </div>

            {/* Time range */}
            {showTimeRange && (
              <div
                className="text-xs opacity-60 mt-0.5"
                style={{ color: LIVING_EARTH.sage }}
              >
                {timeRange}
              </div>
            )}

            {/* Neutral message */}
            <div
              className={`${sizes.text} mt-2 opacity-60`}
              style={{ color: LIVING_EARTH.sand }}
            >
              {neutralMessage}
            </div>
          </div>
        </div>

        {/* Reminder: No judgment */}
        {gap.duration_minutes >= 60 && (
          <div
            className="text-xs mt-3 pt-2 border-t opacity-40"
            style={{
              borderColor: `${LIVING_EARTH.sage}22`,
              color: LIVING_EARTH.sage,
            }}
          >
            Untracked time is data, not failure.
          </div>
        )}
      </div>
    </GrowingContainer>
  );
}

// =============================================================================
// Summary Component
// =============================================================================

export interface GapSummaryProps {
  /** All gaps for the period */
  gaps: TimeGap[];

  /** Custom className */
  className?: string;
}

/**
 * GapSummary
 *
 * Summary of all gaps for a period.
 * Shows total untracked time neutrally.
 *
 * @example
 * ```tsx
 * <GapSummary gaps={todayGaps} />
 * ```
 */
export function GapSummary({ gaps, className = '' }: GapSummaryProps) {
  const { density } = useWindowLayout();
  const sizes = SIZES[density];

  // Calculate total
  const totalMinutes = useMemo(
    () => gaps.reduce((sum, g) => sum + g.duration_minutes, 0),
    [gaps]
  );

  const totalText = useMemo(
    () => formatDuration(totalMinutes),
    [totalMinutes]
  );

  if (gaps.length === 0) {
    return null;
  }

  return (
    <div
      className={`flex items-center gap-2 ${sizes.padding} ${className}`}
      style={{
        background: `${LIVING_EARTH.sage}08`,
        borderRadius: 8,
      }}
    >
      <GapIcon size={sizes.iconSize} category={getGapCategory(totalMinutes)} />
      <span
        className={`${sizes.text} opacity-60`}
        style={{ color: LIVING_EARTH.sand }}
      >
        {totalText} untracked across {gaps.length} gap
        {gaps.length !== 1 ? 's' : ''}. Noted, not judged.
      </span>
    </div>
  );
}

// =============================================================================
// Exports
// =============================================================================

export default GapIndicator;
