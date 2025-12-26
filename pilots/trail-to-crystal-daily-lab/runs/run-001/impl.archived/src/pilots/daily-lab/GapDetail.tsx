/**
 * GapDetail - Warm gap inspection panel for Daily Lab
 *
 * Design Goals (QA-2):
 * - Shows when user clicks on a gap in the timeline
 * - Warm, non-judgmental copy
 * - Optional annotation (never required)
 * - Context: marks before and after the gap
 *
 * Philosophy:
 * - "Rest is productive. Gaps are natural."
 * - "Not everything needs to be witnessed."
 * - Gaps are features, not bugs
 *
 * Anti-Patterns Avoided:
 * - No "you missed X hours" language
 * - No productivity percentages
 * - No red/warning colors for gaps
 * - No shame mechanics
 *
 * @see pilots/trail-to-crystal-daily-lab/PROTO_SPEC.md
 */

import { useState, useCallback, useMemo } from "react";
import { useWindowLayout, type TimeGap, type TrailMark, LIVING_EARTH, TIMING } from "@kgents/shared-primitives";
import {
  getGapDetailHeader,
  getGapMessage,
  getRandomAffirmation,
  formatGapTimeRange,
  GAP_MEANINGS,
  type GapMeaningId,
} from "../../utils/gapMessages";

// =============================================================================
// Types
// =============================================================================

export interface GapAnnotation {
  meaning?: GapMeaningId;
  note?: string;
}

export interface GapDetailProps {
  /** The gap to display */
  gap: TimeGap;

  /** Mark before this gap (for context) */
  beforeMark?: TrailMark | null;

  /** Mark after this gap (for context) */
  afterMark?: TrailMark | null;

  /** Whether the panel is visible */
  isOpen: boolean;

  /** Callback to close the panel */
  onClose: () => void;

  /** Callback when gap is annotated (optional feature) */
  onAnnotate?: (gap: TimeGap, annotation: GapAnnotation) => void;

  /** Custom className */
  className?: string;
}

// =============================================================================
// Constants
// =============================================================================

const SIZES = {
  compact: {
    padding: "p-4",
    text: "text-sm",
    title: "text-lg",
    gap: "gap-3",
  },
  comfortable: {
    padding: "p-5",
    text: "text-base",
    title: "text-xl",
    gap: "gap-4",
  },
  spacious: {
    padding: "p-6",
    text: "text-base",
    title: "text-2xl",
    gap: "gap-5",
  },
} as const;

// =============================================================================
// Sub-components
// =============================================================================

interface ContextMarkProps {
  mark: TrailMark;
  position: "before" | "after";
  textClass: string;
}

function ContextMark({ mark, position, textClass }: ContextMarkProps) {
  const formatTime = (timestamp: string) =>
    new Date(timestamp).toLocaleTimeString("en-US", {
      hour: "numeric",
      minute: "2-digit",
      hour12: true,
    });

  return (
    <div
      className="rounded-lg p-3"
      style={{
        background: `${LIVING_EARTH.sage}11`,
        border: `1px solid ${LIVING_EARTH.sage}22`,
      }}
    >
      <div className="flex items-center gap-2 mb-1">
        <span
          className="text-xs uppercase tracking-wide opacity-60"
          style={{ color: LIVING_EARTH.sand }}
        >
          {position === "before" ? "Before" : "After"} the gap
        </span>
        <span className="text-xs opacity-40" style={{ color: LIVING_EARTH.sand }}>
          {formatTime(mark.timestamp)}
        </span>
      </div>
      <p className={`${textClass}`} style={{ color: LIVING_EARTH.lantern }}>
        {mark.content}
      </p>
      {mark.tags.length > 0 && (
        <div className="flex flex-wrap gap-1 mt-2">
          {mark.tags.map((tag) => (
            <span
              key={tag}
              className="text-xs px-2 py-0.5 rounded-full"
              style={{
                background: `${LIVING_EARTH.sage}22`,
                color: LIVING_EARTH.sage,
              }}
            >
              {tag}
            </span>
          ))}
        </div>
      )}
    </div>
  );
}

interface MeaningSelectorProps {
  selectedMeaning?: GapMeaningId;
  onSelect: (meaning: GapMeaningId | undefined) => void;
}

function MeaningSelector({ selectedMeaning, onSelect }: MeaningSelectorProps) {
  return (
    <div className="space-y-2">
      <p className="text-sm opacity-60" style={{ color: LIVING_EARTH.sand }}>
        If you'd like, what was this time for? (Optional)
      </p>
      <div className="flex flex-wrap gap-2">
        {GAP_MEANINGS.map((meaning) => {
          const isSelected = selectedMeaning === meaning.id;
          return (
            <button
              key={meaning.id}
              onClick={() => onSelect(isSelected ? undefined : meaning.id)}
              className="px-3 py-1.5 rounded-lg text-sm transition-all"
              style={{
                background: isSelected ? `${LIVING_EARTH.sage}33` : `${LIVING_EARTH.sage}11`,
                color: isSelected ? LIVING_EARTH.sage : LIVING_EARTH.sand,
                border: `1px solid ${isSelected ? LIVING_EARTH.sage : "transparent"}`,
              }}
              title={meaning.description}
            >
              {meaning.label}
            </button>
          );
        })}
      </div>
      <p className="text-xs opacity-40" style={{ color: LIVING_EARTH.clay }}>
        You never have to explain gaps. This is just for you.
      </p>
    </div>
  );
}

// =============================================================================
// Main Component
// =============================================================================

/**
 * GapDetail
 *
 * A warm, non-judgmental panel for inspecting gaps in the trail.
 * Displayed as a slide-over when a gap is clicked.
 *
 * @example
 * ```tsx
 * <GapDetail
 *   gap={selectedGap}
 *   beforeMark={markBeforeGap}
 *   afterMark={markAfterGap}
 *   isOpen={showGapDetail}
 *   onClose={() => setShowGapDetail(false)}
 *   onAnnotate={(gap, annotation) => saveAnnotation(gap, annotation)}
 * />
 * ```
 */
export function GapDetail({
  gap,
  beforeMark,
  afterMark,
  isOpen,
  onClose,
  onAnnotate,
  className = "",
}: GapDetailProps) {
  const { density } = useWindowLayout();
  const sizes = SIZES[density];

  // Local state for annotation
  const [selectedMeaning, setSelectedMeaning] = useState<GapMeaningId | undefined>();
  const [note, setNote] = useState("");
  const [affirmation] = useState(() => getRandomAffirmation());

  // Computed values
  const header = useMemo(
    () => getGapDetailHeader(gap.duration_minutes),
    [gap.duration_minutes]
  );

  const contextMessage = useMemo(
    () => getGapMessage(gap.duration_minutes),
    [gap.duration_minutes]
  );

  const timeRange = useMemo(
    () => formatGapTimeRange(gap.start, gap.end),
    [gap.start, gap.end]
  );

  // Handle save
  const handleSave = useCallback(() => {
    if (onAnnotate && (selectedMeaning || note.trim())) {
      onAnnotate(gap, {
        meaning: selectedMeaning,
        note: note.trim() || undefined,
      });
    }
    onClose();
  }, [gap, selectedMeaning, note, onAnnotate, onClose]);

  // Handle backdrop click
  const handleBackdropClick = useCallback(
    (e: React.MouseEvent) => {
      if (e.target === e.currentTarget) {
        onClose();
      }
    },
    [onClose]
  );

  if (!isOpen) return null;

  return (
    <div
      className={`fixed inset-0 z-50 ${className}`}
      onClick={handleBackdropClick}
      role="dialog"
      aria-modal="true"
      aria-labelledby="gap-detail-title"
    >
      {/* Backdrop */}
      <div
        className="absolute inset-0"
        style={{
          background: `${LIVING_EARTH.bark}cc`,
          backdropFilter: "blur(4px)",
          transition: `opacity ${TIMING.standard}ms`,
        }}
      />

      {/* Slide-over Panel */}
      <div
        className="absolute right-0 top-0 h-full w-full max-w-md overflow-y-auto"
        style={{
          background: LIVING_EARTH.bark,
          borderLeft: `1px solid ${LIVING_EARTH.sage}33`,
          boxShadow: `-4px 0 24px ${LIVING_EARTH.bark}`,
          animation: `slideIn ${TIMING.standard}ms ease-out`,
        }}
      >
        {/* Header */}
        <div
          className={`${sizes.padding} border-b`}
          style={{ borderColor: `${LIVING_EARTH.sage}22` }}
        >
          <div className="flex items-start justify-between">
            <div>
              <h2
                id="gap-detail-title"
                className={`${sizes.title} font-medium mb-1`}
                style={{ color: LIVING_EARTH.sage }}
              >
                A Gap in the Trail
              </h2>
              <p className={`${sizes.text}`} style={{ color: LIVING_EARTH.sand }}>
                {timeRange}
              </p>
            </div>
            <button
              onClick={onClose}
              className="p-2 rounded-lg opacity-60 hover:opacity-100 transition-opacity"
              style={{ color: LIVING_EARTH.sand }}
              aria-label="Close gap detail"
            >
              <svg
                width="20"
                height="20"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
              >
                <path d="M18 6 6 18M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>

        {/* Content */}
        <div className={`${sizes.padding} space-y-6`}>
          {/* Main Message - Warm and Non-judgmental */}
          <div
            className="rounded-xl p-4"
            style={{
              background: `${LIVING_EARTH.sage}11`,
              border: `1px solid ${LIVING_EARTH.sage}22`,
            }}
          >
            <p
              className={`${sizes.title} font-medium mb-2`}
              style={{ color: LIVING_EARTH.lantern }}
            >
              {header}
            </p>
            <p className={`${sizes.text} opacity-80`} style={{ color: LIVING_EARTH.sand }}>
              {contextMessage}
            </p>
          </div>

          {/* Affirmation */}
          <div className="text-center py-2">
            <p
              className="text-sm italic opacity-60"
              style={{ color: LIVING_EARTH.sage }}
            >
              "{affirmation}"
            </p>
          </div>

          {/* Context: Before and After Marks */}
          {(beforeMark || afterMark) && (
            <div className={`space-y-3`}>
              <h3
                className="text-sm font-medium uppercase tracking-wide opacity-60"
                style={{ color: LIVING_EARTH.sand }}
              >
                Context
              </h3>
              {beforeMark && (
                <ContextMark mark={beforeMark} position="before" textClass={sizes.text} />
              )}
              {afterMark && (
                <ContextMark mark={afterMark} position="after" textClass={sizes.text} />
              )}
            </div>
          )}

          {/* Meaning Selector (Optional) */}
          {onAnnotate && (
            <div
              className="pt-4 border-t"
              style={{ borderColor: `${LIVING_EARTH.sage}22` }}
            >
              <MeaningSelector
                selectedMeaning={selectedMeaning}
                onSelect={setSelectedMeaning}
              />

              {/* Optional Note */}
              <div className="mt-4">
                <label
                  htmlFor="gap-note"
                  className="block text-sm opacity-60 mb-2"
                  style={{ color: LIVING_EARTH.sand }}
                >
                  Add a note (optional)
                </label>
                <textarea
                  id="gap-note"
                  value={note}
                  onChange={(e) => setNote(e.target.value)}
                  placeholder="This is just for you..."
                  rows={3}
                  className={`w-full ${sizes.text} rounded-lg px-3 py-2 resize-none`}
                  style={{
                    background: `${LIVING_EARTH.sage}11`,
                    border: `1px solid ${LIVING_EARTH.sage}22`,
                    color: LIVING_EARTH.lantern,
                  }}
                />
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div
          className={`${sizes.padding} border-t`}
          style={{ borderColor: `${LIVING_EARTH.sage}22` }}
        >
          <div className="flex items-center justify-end gap-3">
            <button
              onClick={onClose}
              className={`px-4 py-2 rounded-lg ${sizes.text} opacity-70 hover:opacity-100 transition-opacity`}
              style={{ color: LIVING_EARTH.sand }}
            >
              Close
            </button>
            {onAnnotate && (selectedMeaning || note.trim()) && (
              <button
                onClick={handleSave}
                className={`px-4 py-2 rounded-lg ${sizes.text} font-medium transition-colors`}
                style={{
                  background: `${LIVING_EARTH.sage}22`,
                  color: LIVING_EARTH.sage,
                }}
              >
                Save Note
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Animation keyframes */}
      <style>{`
        @keyframes slideIn {
          from {
            transform: translateX(100%);
          }
          to {
            transform: translateX(0);
          }
        }
      `}</style>
    </div>
  );
}

export default GapDetail;
