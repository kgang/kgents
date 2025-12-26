/**
 * DayView - Main layout for daily lab experience
 *
 * Design Philosophy (from PROTO_SPEC):
 * - QA-1: Lighter than a to-do list
 * - QA-2: Reward honest gaps (use "resting", not "untracked")
 * - QA-3: Witnessed, not surveilled (warm companion language)
 * - QA-4: Crystal = memory artifact (warmth, texture, not bullets)
 *
 * Layout:
 * - Top: Quick capture (< 5 seconds to mark)
 * - Middle: Trail timeline with neutral gap indicators
 * - Bottom: Crystal when available
 *
 * @see pilots/trail-to-crystal-daily-lab/PROTO_SPEC.md
 */

import { useCallback, useState } from 'react';
import {
  MarkCaptureInput,
  TrailTimeline,
  CrystalCard,
  GapSummary,
  LIVING_EARTH,
  useWindowLayout,
  type CaptureRequest,
  type CaptureResponse,
  type TrailMark,
  type TimeGap,
  type Crystal,
  type CompressionHonesty,
} from '@kgents/shared-primitives';

// =============================================================================
// Types
// =============================================================================

export interface DayViewProps {
  /** Current date being viewed */
  date: Date;

  /** Trail marks for the day */
  marks: TrailMark[];

  /** Gaps between marks */
  gaps: TimeGap[];

  /** Crystal for the day (if crystallized) */
  crystal?: Crystal;

  /** Compression honesty for the crystal */
  crystalHonesty?: CompressionHonesty;

  /** Whether the day is loading */
  isLoading?: boolean;

  /** Error message if any */
  error?: string;

  /** Handler for capturing a new mark */
  onCapture: (request: CaptureRequest) => Promise<CaptureResponse | void>;

  /** Handler for crystallizing the day */
  onCrystallize?: () => Promise<void>;

  /** Handler for exporting the day */
  onExport?: (format: 'markdown' | 'json') => Promise<void>;

  /** Handler for sharing the crystal */
  onShareCrystal?: (crystal: Crystal) => void;

  /** Review prompt from backend */
  reviewPrompt?: string;
}

// =============================================================================
// Density-aware Sizing
// =============================================================================

const SIZES = {
  compact: {
    gap: 'gap-3',
    padding: 'p-3',
    maxWidth: 'max-w-lg',
    headerText: 'text-lg',
  },
  comfortable: {
    gap: 'gap-4',
    padding: 'p-4',
    maxWidth: 'max-w-xl',
    headerText: 'text-xl',
  },
  spacious: {
    gap: 'gap-6',
    padding: 'p-6',
    maxWidth: 'max-w-2xl',
    headerText: 'text-2xl',
  },
} as const;

// =============================================================================
// Component
// =============================================================================

/**
 * DayView
 *
 * The main daily lab experience. Shows:
 * 1. Quick capture input at top
 * 2. Trail timeline with gaps honored (not shamed)
 * 3. Crystal when the day is crystallized
 *
 * @example
 * <DayView
 *   date={new Date()}
 *   marks={trail.marks}
 *   gaps={trail.gaps}
 *   onCapture={handleCapture}
 * />
 */
export function DayView({
  date,
  marks,
  gaps,
  crystal,
  crystalHonesty,
  isLoading,
  error,
  onCapture,
  onCrystallize,
  onExport,
  onShareCrystal,
  reviewPrompt,
}: DayViewProps) {
  const { density } = useWindowLayout();
  const sizes = SIZES[density];

  const [selectedMark, setSelectedMark] = useState<TrailMark | null>(null);
  const [isCrystallizing, setIsCrystallizing] = useState(false);

  // Format the date header
  const dateHeader = date.toLocaleDateString('en-US', {
    weekday: 'long',
    month: 'long',
    day: 'numeric',
  });

  // Check if this is today
  const isToday =
    date.toDateString() === new Date().toDateString();

  // Handle crystallization
  const handleCrystallize = useCallback(async () => {
    if (!onCrystallize || isCrystallizing) return;

    setIsCrystallizing(true);
    try {
      await onCrystallize();
    } finally {
      setIsCrystallizing(false);
    }
  }, [onCrystallize, isCrystallizing]);

  // Handle mark selection
  const handleSelectMark = useCallback((mark: TrailMark) => {
    setSelectedMark((prev) => (prev?.mark_id === mark.mark_id ? null : mark));
  }, []);

  // Handle crystal share
  const handleShareCrystal = useCallback(
    (c: Crystal) => {
      onShareCrystal?.(c);
    },
    [onShareCrystal]
  );

  // Handle crystal export
  const handleExportCrystal = useCallback(
    (_c: Crystal, format: 'markdown' | 'json') => {
      onExport?.(format);
    },
    [onExport]
  );

  return (
    <div
      className={`day-view mx-auto ${sizes.maxWidth} ${sizes.padding}`}
      style={{ minHeight: '100vh', background: LIVING_EARTH.bark }}
    >
      {/* Header */}
      <header className="mb-6">
        <h1
          className={`${sizes.headerText} font-semibold`}
          style={{ color: LIVING_EARTH.lantern }}
        >
          {isToday ? "Today's Journey" : dateHeader}
        </h1>
        <p
          className="text-sm mt-1 opacity-60"
          style={{ color: LIVING_EARTH.sand }}
        >
          {isToday
            ? "Capture what's on your mind. Gaps are honored, not hidden."
            : `Reviewing ${dateHeader}`}
        </p>
      </header>

      {/* Error state */}
      {error && (
        <div
          className={`${sizes.padding} rounded-lg mb-4`}
          style={{
            background: `${LIVING_EARTH.rust}22`,
            border: `1px solid ${LIVING_EARTH.rust}44`,
          }}
        >
          <p style={{ color: LIVING_EARTH.rust }}>{error}</p>
        </div>
      )}

      {/* Main content */}
      <div className={`flex flex-col ${sizes.gap}`}>
        {/* Quick Capture (only for today) */}
        {isToday && (
          <section aria-label="Capture">
            <MarkCaptureInput
              onCapture={onCapture}
              placeholder="What's on your mind?"
              autoFocus={marks.length === 0}
            />
          </section>
        )}

        {/* Loading state */}
        {isLoading && (
          <div
            className="flex items-center justify-center py-12"
            style={{ color: LIVING_EARTH.sand }}
          >
            <span className="opacity-60">Loading your trail...</span>
          </div>
        )}

        {/* Trail Timeline */}
        {!isLoading && marks.length > 0 && (
          <section aria-label="Trail">
            <TrailTimeline
              marks={marks}
              gaps={gaps}
              date={date}
              selectedMarkId={selectedMark?.mark_id}
              onSelectMark={handleSelectMark}
              showTimestamps
            />
          </section>
        )}

        {/* Empty state (no marks yet) */}
        {!isLoading && marks.length === 0 && isToday && (
          <div
            className={`${sizes.padding} rounded-lg text-center`}
            style={{
              background: `${LIVING_EARTH.sage}11`,
              border: `1px dashed ${LIVING_EARTH.sage}33`,
            }}
          >
            <p style={{ color: LIVING_EARTH.sand }} className="opacity-70">
              A new day awaits. What will you notice?
            </p>
          </div>
        )}

        {/* Gap Summary (neutral, not shaming) */}
        {!isLoading && gaps.length > 0 && (
          <GapSummary gaps={gaps} />
        )}

        {/* Selected Mark Detail */}
        {selectedMark && (
          <section
            aria-label="Selected mark"
            className={`${sizes.padding} rounded-lg`}
            style={{
              background: `${LIVING_EARTH.sage}11`,
              border: `1px solid ${LIVING_EARTH.sage}22`,
            }}
          >
            <p style={{ color: LIVING_EARTH.lantern }}>{selectedMark.content}</p>
            {selectedMark.tags.length > 0 && (
              <div className="flex gap-2 mt-2">
                {selectedMark.tags.map((tag) => (
                  <span
                    key={tag}
                    className="text-xs px-2 py-1 rounded-full"
                    style={{
                      background: `${LIVING_EARTH.amber}22`,
                      color: LIVING_EARTH.amber,
                    }}
                  >
                    {tag}
                  </span>
                ))}
              </div>
            )}
          </section>
        )}

        {/* Review Prompt */}
        {reviewPrompt && !crystal && marks.length >= 3 && (
          <section
            aria-label="Review prompt"
            className={`${sizes.padding} rounded-lg`}
            style={{
              background: `${LIVING_EARTH.amber}11`,
              border: `1px solid ${LIVING_EARTH.amber}22`,
            }}
          >
            <p className="text-sm" style={{ color: LIVING_EARTH.amber }}>
              {reviewPrompt}
            </p>
          </section>
        )}

        {/* Crystal (if day is crystallized) */}
        {crystal && (
          <section aria-label="Daily crystal">
            <CrystalCard
              crystal={crystal}
              honesty={crystalHonesty}
              onShare={onShareCrystal ? handleShareCrystal : undefined}
              onExport={onExport ? handleExportCrystal : undefined}
            />
          </section>
        )}

        {/* Crystallize Action (when ready) */}
        {!crystal && marks.length >= 3 && onCrystallize && (
          <section aria-label="Crystallize">
            <button
              onClick={handleCrystallize}
              disabled={isCrystallizing}
              className={`
                w-full ${sizes.padding} rounded-lg
                font-medium transition-all duration-150
                disabled:opacity-50 disabled:cursor-not-allowed
              `}
              style={{
                background: LIVING_EARTH.amber,
                color: LIVING_EARTH.bark,
              }}
            >
              {isCrystallizing ? 'Crystallizing...' : 'Crystallize Today'}
            </button>
            <p
              className="text-xs mt-2 text-center opacity-50"
              style={{ color: LIVING_EARTH.sand }}
            >
              Compress today into a memory artifact
            </p>
          </section>
        )}

        {/* Not enough marks message */}
        {!crystal && marks.length > 0 && marks.length < 3 && (
          <p
            className="text-xs text-center opacity-40"
            style={{ color: LIVING_EARTH.sage }}
          >
            {3 - marks.length} more mark{3 - marks.length !== 1 ? 's' : ''} until you can crystallize
          </p>
        )}
      </div>

      {/* Footer */}
      <footer className="mt-12 pt-6 border-t" style={{ borderColor: `${LIVING_EARTH.sage}22` }}>
        <p
          className="text-xs text-center opacity-40"
          style={{ color: LIVING_EARTH.sand }}
        >
          Daily Lab - Turn your day into proof of intention
        </p>
      </footer>
    </div>
  );
}

export default DayView;
