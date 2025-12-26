/**
 * GapSummaryCard - Warm, non-judgmental gap summary for Crystal page
 *
 * Design Goals (QA-2):
 * - Shows total gap time for the day
 * - Warm framing: "Your day included X hours of quiet time"
 * - Visual showing marked vs resting (no judgment)
 * - Link to view pauses in trail
 *
 * Philosophy:
 * - Gaps are honored, not hidden
 * - Resting time is part of the honest record
 * - No productivity percentages or shame mechanics
 * - Use warm language: "resting", "reflecting", "quiet time", "pauses"
 *
 * Anti-Patterns Avoided:
 * - No comparison to "ideal" tracked time
 * - No red/warning colors
 * - No "you missed" or "untracked" language
 *
 * @see pilots/trail-to-crystal-daily-lab/PROTO_SPEC.md
 */

import { useMemo } from "react";
import { useWindowLayout, type TimeGap, LIVING_EARTH } from "@kgents/shared-primitives";
import { formatGapDuration, getRandomAffirmation } from "../../utils/gapMessages";

// =============================================================================
// Types
// =============================================================================

export interface GapSummaryCardProps {
  /** All gaps for the day */
  gaps: TimeGap[];

  /** Total tracked time in minutes (from marks) */
  trackedMinutes?: number;

  /** Callback to view gaps in trail */
  onViewTrail?: () => void;

  /** Custom className */
  className?: string;
}

// =============================================================================
// Constants
// =============================================================================

const SIZES = {
  compact: {
    padding: "p-3",
    text: "text-sm",
    title: "text-base",
  },
  comfortable: {
    padding: "p-4",
    text: "text-base",
    title: "text-lg",
  },
  spacious: {
    padding: "p-5",
    text: "text-base",
    title: "text-xl",
  },
} as const;

// =============================================================================
// Sub-components
// =============================================================================

interface TimeDistributionProps {
  trackedMinutes: number;
  gapMinutes: number;
}

/**
 * Simple visual showing marked vs resting time
 * Uses calming sage green for resting time (not warning colors)
 */
function TimeDistribution({ trackedMinutes, gapMinutes }: TimeDistributionProps) {
  const total = trackedMinutes + gapMinutes;
  if (total === 0) return null;

  const trackedPercent = Math.round((trackedMinutes / total) * 100);
  const gapPercent = 100 - trackedPercent;

  return (
    <div className="space-y-2">
      {/* Bar visualization */}
      <div
        className="h-3 rounded-full overflow-hidden flex"
        style={{ background: `${LIVING_EARTH.sage}22` }}
      >
        {/* Tracked portion - amber/warm */}
        <div
          className="h-full transition-all duration-500"
          style={{
            width: `${trackedPercent}%`,
            background: `${LIVING_EARTH.amber}88`,
          }}
        />
        {/* Resting portion - calming sage green */}
        <div
          className="h-full transition-all duration-500"
          style={{
            width: `${gapPercent}%`,
            background: `${LIVING_EARTH.sage}44`,
          }}
        />
      </div>

      {/* Legend - no percentages, just facts */}
      <div className="flex items-center justify-between text-xs opacity-60">
        <div className="flex items-center gap-2">
          <span
            className="w-2 h-2 rounded-full"
            style={{ background: `${LIVING_EARTH.amber}88` }}
          />
          <span style={{ color: LIVING_EARTH.sand }}>
            {formatGapDuration(trackedMinutes)} marked
          </span>
        </div>
        <div className="flex items-center gap-2">
          <span
            className="w-2 h-2 rounded-full"
            style={{ background: `${LIVING_EARTH.sage}44` }}
          />
          <span style={{ color: LIVING_EARTH.sand }}>
            {formatGapDuration(gapMinutes)} resting
          </span>
        </div>
      </div>
    </div>
  );
}

interface GapListPreviewProps {
  gaps: TimeGap[];
  textClass: string;
}

function GapListPreview({ gaps, textClass }: GapListPreviewProps) {
  const formatTime = (timestamp: string) =>
    new Date(timestamp).toLocaleTimeString("en-US", {
      hour: "numeric",
      minute: "2-digit",
      hour12: true,
    });

  // Show up to 3 gaps
  const previewGaps = gaps.slice(0, 3);
  const remaining = gaps.length - 3;

  return (
    <div className="space-y-2">
      {previewGaps.map((gap, index) => (
        <div
          key={`${gap.start}-${index}`}
          className="flex items-center justify-between py-1"
        >
          <span className={`${textClass} opacity-60`} style={{ color: LIVING_EARTH.sand }}>
            {formatTime(gap.start)} - {formatTime(gap.end)}
          </span>
          <span className={`${textClass}`} style={{ color: LIVING_EARTH.sage }}>
            {formatGapDuration(gap.duration_minutes)}
          </span>
        </div>
      ))}
      {remaining > 0 && (
        <p className="text-sm opacity-40" style={{ color: LIVING_EARTH.clay }}>
          + {remaining} more gap{remaining !== 1 ? "s" : ""}
        </p>
      )}
    </div>
  );
}

// =============================================================================
// Main Component
// =============================================================================

/**
 * GapSummaryCard
 *
 * A warm, non-judgmental summary of pauses for the Crystal page.
 * Frames resting time as part of your day's rhythm.
 *
 * @example
 * ```tsx
 * <GapSummaryCard
 *   gaps={todayGaps}
 *   trackedMinutes={320}
 *   onViewTrail={() => navigate('/daily-lab/trail')}
 * />
 * ```
 */
export function GapSummaryCard({
  gaps,
  trackedMinutes = 0,
  onViewTrail,
  className = "",
}: GapSummaryCardProps) {
  const { density } = useWindowLayout();
  const sizes = SIZES[density];

  // Calculate totals
  const totalGapMinutes = useMemo(
    () => gaps.reduce((sum, g) => sum + g.duration_minutes, 0),
    [gaps]
  );

  // Get an affirmation
  const affirmation = useMemo(() => getRandomAffirmation(), []);

  // If no gaps, show positive message
  if (gaps.length === 0) {
    return (
      <div
        className={`rounded-xl ${sizes.padding} ${className}`}
        style={{
          background: `${LIVING_EARTH.sage}11`,
          border: `1px solid ${LIVING_EARTH.sage}22`,
        }}
      >
        <p className={`${sizes.text} opacity-60`} style={{ color: LIVING_EARTH.sage }}>
          Your trail has no significant gaps today.
        </p>
      </div>
    );
  }

  return (
    <div
      className={`rounded-xl ${className}`}
      style={{
        background: LIVING_EARTH.bark,
        border: `1px solid ${LIVING_EARTH.sage}22`,
      }}
    >
      {/* Header */}
      <div
        className={`${sizes.padding} border-b`}
        style={{ borderColor: `${LIVING_EARTH.sage}22` }}
      >
        <h3
          className={`${sizes.title} font-medium mb-1`}
          style={{ color: LIVING_EARTH.sage }}
        >
          Your Day's Rhythm
        </h3>
        <p className={`${sizes.text} opacity-70`} style={{ color: LIVING_EARTH.sand }}>
          Your day included {formatGapDuration(totalGapMinutes)} of quiet time across{" "}
          {gaps.length} pause{gaps.length !== 1 ? "s" : ""}.
        </p>
      </div>

      {/* Time Distribution (if we have tracked time data) */}
      {trackedMinutes > 0 && (
        <div className={sizes.padding}>
          <TimeDistribution
            trackedMinutes={trackedMinutes}
            gapMinutes={totalGapMinutes}
          />
        </div>
      )}

      {/* Gap List Preview */}
      <div
        className={`${sizes.padding} border-t`}
        style={{ borderColor: `${LIVING_EARTH.sage}22` }}
      >
        <p
          className="text-xs uppercase tracking-wide opacity-60 mb-2"
          style={{ color: LIVING_EARTH.sand }}
        >
          Pauses in your trail
        </p>
        <GapListPreview gaps={gaps} textClass={sizes.text} />
      </div>

      {/* Affirmation */}
      <div
        className={`${sizes.padding} border-t text-center`}
        style={{ borderColor: `${LIVING_EARTH.sage}22` }}
      >
        <p
          className="text-sm italic opacity-50"
          style={{ color: LIVING_EARTH.sage }}
        >
          "{affirmation}"
        </p>
      </div>

      {/* Action to view trail */}
      {onViewTrail && (
        <div
          className={`${sizes.padding} border-t`}
          style={{ borderColor: `${LIVING_EARTH.sage}22` }}
        >
          <button
            onClick={onViewTrail}
            className={`w-full ${sizes.text} py-2 rounded-lg opacity-70 hover:opacity-100 transition-opacity flex items-center justify-center gap-2`}
            style={{
              background: `${LIVING_EARTH.sage}11`,
              color: LIVING_EARTH.sage,
            }}
          >
            View pauses in trail
            <svg
              width="16"
              height="16"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
            >
              <path d="M5 12h14M12 5l7 7-7 7" />
            </svg>
          </button>
        </div>
      )}
    </div>
  );
}

export default GapSummaryCard;
