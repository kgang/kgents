/**
 * Gap-Positive Messaging Utilities
 *
 * Philosophy (QA-2):
 * - Untracked time is data, not shame
 * - Gaps are honored, not hidden
 * - Rest is productive. Silence is meaningful.
 *
 * Anti-Patterns Avoided:
 * - No "you missed X hours" language
 * - No productivity percentages
 * - No comparison to "ideal" tracked time
 * - No streaks or tracking goals
 *
 * @see pilots/trail-to-crystal-daily-lab/PROTO_SPEC.md
 */

// =============================================================================
// Core Messages
// =============================================================================

/** Warm, affirming messages for gaps - rotated randomly */
export const GAP_AFFIRMATIONS = [
  "Resting time is still your time.",
  "Gaps are breathing room.",
  "Not everything needs a mark.",
  "Rest is part of the rhythm.",
  "Some moments are just for living.",
  "Space between the notes makes the music.",
  "Silence is also meaningful.",
  "Your day includes what you didn't record too.",
  "The quiet hours matter just as much.",
  "Living doesn't always need witnesses.",
  "Time to reflect is time well spent.",
  "Some of the best thinking happens in stillness.",
] as const;

/** Context-aware messages based on gap duration */
export const GAP_MESSAGES_BY_DURATION = {
  /** Under 30 minutes */
  brief: [
    "A brief pause. That's part of the rhythm.",
    "A small gap. These add up to a richer day.",
    "A moment between moments.",
    "Short gaps are transitions. They count.",
    "A little breathing room.",
  ],
  /** 30-120 minutes */
  moderate: [
    "Some time for resting or reflecting. That's okay.",
    "A gap in the trail. Life doesn't pause for logs.",
    "A pause for thought, perhaps, or something private.",
    "An hour or so off the trail. That happens.",
    "Time for your own thoughts.",
  ],
  /** Over 2 hours */
  extended: [
    "Extended time for rest or reflection. That's valid.",
    "A longer gap. Rest is productive too.",
    "Several hours of quiet time. That's part of your day too.",
    "A significant pause. Not everything needs to be witnessed.",
    "Time spent in your own space.",
  ],
  /** Overnight or very long gaps */
  major: [
    "A substantial portion of your day was lived, not logged.",
    "Many hours away. Life happens between the marks.",
    "Most of this time was for living, not recording.",
    "A large gap. Your story includes the spaces too.",
    "Time to rest and renew.",
  ],
} as const;

/** Possible meanings for gaps - user can optionally select */
export const GAP_MEANINGS = [
  { id: "rest", label: "Rest", description: "Sleep, relaxation, recovery" },
  { id: "deep_work", label: "Deep work", description: "Focused activity without pauses" },
  { id: "transition", label: "Transition", description: "Moving between contexts" },
  { id: "life", label: "Life happened", description: "Personal time, interruptions, the unexpected" },
  { id: "offline", label: "Offline time", description: "Away from devices" },
  { id: "social", label: "Social time", description: "Time with others" },
  { id: "unmarked", label: "Prefer not to label", description: "Some things don't need categories" },
] as const;

export type GapMeaningId = (typeof GAP_MEANINGS)[number]["id"];

// =============================================================================
// Helper Functions
// =============================================================================

/**
 * Get duration category for a gap
 */
export function getGapDurationCategory(
  durationMinutes: number
): "brief" | "moderate" | "extended" | "major" {
  if (durationMinutes < 30) return "brief";
  if (durationMinutes < 120) return "moderate";
  if (durationMinutes < 360) return "extended";
  return "major";
}

/**
 * Get a context-aware gap message based on duration
 *
 * @param durationMinutes - Gap duration in minutes
 * @returns A warm, non-judgmental message about the gap
 */
export function getGapMessage(durationMinutes: number): string {
  const category = getGapDurationCategory(durationMinutes);
  const messages = GAP_MESSAGES_BY_DURATION[category];
  // Deterministic selection based on duration for consistency
  const index = durationMinutes % messages.length;
  return messages[index];
}

/**
 * Get a random gap affirmation
 *
 * @returns A warm, affirming message about gaps in general
 */
export function getRandomAffirmation(): string {
  const index = Math.floor(Math.random() * GAP_AFFIRMATIONS.length);
  return GAP_AFFIRMATIONS[index];
}

/**
 * Format gap duration in a warm, human way
 *
 * @param minutes - Duration in minutes
 * @returns Human-readable duration string
 */
export function formatGapDuration(minutes: number): string {
  if (minutes < 60) {
    return `${minutes} minute${minutes !== 1 ? "s" : ""}`;
  }

  const hours = Math.floor(minutes / 60);
  const remainingMins = minutes % 60;

  if (remainingMins === 0) {
    return `${hours} hour${hours !== 1 ? "s" : ""}`;
  }

  if (hours === 1 && remainingMins < 30) {
    return `about an hour`;
  }

  if (hours >= 1 && remainingMins >= 30) {
    return `about ${hours + 1} hours`;
  }

  return `${hours}h ${remainingMins}m`;
}

/**
 * Get a warm header for gap detail view
 *
 * @param durationMinutes - Gap duration
 * @returns A header message for the gap detail panel
 */
export function getGapDetailHeader(durationMinutes: number): string {
  const duration = formatGapDuration(durationMinutes);
  const category = getGapDurationCategory(durationMinutes);

  switch (category) {
    case "brief":
      return `${duration} of quiet time`;
    case "moderate":
      return `${duration} of resting or reflecting. That's part of your day too.`;
    case "extended":
      return `${duration} of time for yourself. Rest is productive.`;
    case "major":
      return `${duration} of space. Not everything needs to be witnessed.`;
  }
}

/**
 * Get the time range formatted warmly
 */
export function formatGapTimeRange(start: string, end: string): string {
  const startDate = new Date(start);
  const endDate = new Date(end);

  const formatTime = (date: Date) =>
    date.toLocaleTimeString("en-US", {
      hour: "numeric",
      minute: "2-digit",
      hour12: true,
    });

  return `Between ${formatTime(startDate)} and ${formatTime(endDate)}`;
}

// =============================================================================
// Compression Honesty Messages
// =============================================================================

/**
 * Get positive framing for compression/dropped items
 *
 * @param droppedCount - Number of items that were compressed away
 * @returns Warm message about compression
 */
export function getCompressionMessage(droppedCount: number): string {
  if (droppedCount === 0) {
    return "Everything was preserved in this crystal.";
  }

  if (droppedCount === 1) {
    return "1 moment was composted to nourish this crystal.";
  }

  if (droppedCount <= 3) {
    return `${droppedCount} moments were composted to nourish this crystal.`;
  }

  if (droppedCount <= 10) {
    return `${droppedCount} moments found their way into the soil. The crystal holds what grew.`;
  }

  return `${droppedCount} moments were released. The crystal carries their essence.`;
}

/**
 * Get secondary message explaining compression positively
 */
export function getCompressionExplanation(galoisLoss: number): string {
  const lossPercent = Math.round(galoisLoss * 100);

  if (lossPercent === 0) {
    return "Full fidelity was preserved.";
  }

  if (lossPercent < 10) {
    return "Almost everything made it through.";
  }

  if (lossPercent < 30) {
    return "The essential patterns were preserved.";
  }

  return "The crystal captures the meaningful core.";
}
