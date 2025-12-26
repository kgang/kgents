/**
 * DayClosurePrompt - Day Closure Ritual for Daily Lab
 *
 * Enforces Law L1: "A day is complete only when a crystal is produced."
 *
 * Design Goals:
 * - QA-1: The daily ritual must feel lighter than a to-do list
 * - Closure should feel like a gift, not homework
 * - Gentle, warm messaging with no urgency or guilt
 *
 * Anti-Patterns Avoided:
 * - No countdown timers or urgency messaging
 * - No "you haven't done this yet" guilt language
 * - No forced closure - always allow dismissal
 *
 * @see PROTO_SPEC.md - L1 Day Closure Law
 */

import { useState, useEffect, useCallback, useMemo } from 'react';
import { LIVING_EARTH, GrowingContainer } from '@kgents/shared-primitives';
// Note: TIMING is also exported from shared-primitives but not used here
import type { TrailMark, Crystal, CompressionHonesty } from '@kgents/shared-primitives';

// =============================================================================
// Types
// =============================================================================

export interface DayClosurePromptProps {
  /** Number of marks captured today */
  markCount: number;

  /** Preview of marks to be crystallized */
  marks?: TrailMark[];

  /** Whether a crystal already exists for today */
  hasCrystal: boolean;

  /** Callback when user confirms crystallization */
  onCrystallize: () => Promise<{ crystal: Crystal; honesty: CompressionHonesty } | null>;

  /** Callback when prompt is dismissed */
  onDismiss?: () => void;

  /** Force show the prompt (ignores time check) */
  forceShow?: boolean;
}

// =============================================================================
// Constants
// =============================================================================

const SNOOZE_DURATION_MS = 2 * 60 * 60 * 1000; // 2 hours
const STORAGE_KEY = 'dailylab_closure_dismissed';
const CLOSURE_HOUR = 18; // 6 PM

// =============================================================================
// Hooks
// =============================================================================

/**
 * Hook to manage closure prompt visibility
 */
function useClosureVisibility(hasCrystal: boolean, forceShow?: boolean) {
  const [dismissed, setDismissed] = useState(false);

  // Check if it's past closure time
  const isPastClosureTime = useMemo(() => {
    const now = new Date();
    return now.getHours() >= CLOSURE_HOUR;
  }, []);

  // Check localStorage for snooze status
  useEffect(() => {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (!stored) return;

    try {
      const { timestamp, date } = JSON.parse(stored);
      const today = new Date().toDateString();

      // Reset if it's a new day
      if (date !== today) {
        localStorage.removeItem(STORAGE_KEY);
        setDismissed(false);
        return;
      }

      // Check if snooze has expired
      const elapsed = Date.now() - timestamp;
      if (elapsed < SNOOZE_DURATION_MS) {
        setDismissed(true);
      } else {
        localStorage.removeItem(STORAGE_KEY);
        setDismissed(false);
      }
    } catch {
      localStorage.removeItem(STORAGE_KEY);
    }
  }, []);

  // Save snooze to localStorage
  const snooze = useCallback(() => {
    const today = new Date().toDateString();
    localStorage.setItem(
      STORAGE_KEY,
      JSON.stringify({ timestamp: Date.now(), date: today })
    );
    setDismissed(true);
  }, []);

  // Determine if prompt should show
  const shouldShow = useMemo(() => {
    if (forceShow) return true;
    if (hasCrystal) return false;
    if (dismissed) return false;
    return isPastClosureTime;
  }, [forceShow, hasCrystal, dismissed, isPastClosureTime]);

  return { shouldShow, snooze };
}

// =============================================================================
// Confetti Animation Component
// =============================================================================

interface ConfettiProps {
  active: boolean;
}

function Confetti({ active }: ConfettiProps) {
  const [particles, setParticles] = useState<
    Array<{ id: number; x: number; delay: number; color: string }>
  >([]);

  useEffect(() => {
    if (!active) {
      setParticles([]);
      return;
    }

    const colors = [LIVING_EARTH.amber, LIVING_EARTH.sage, LIVING_EARTH.lantern];
    const newParticles = Array.from({ length: 30 }, (_, i) => ({
      id: i,
      x: Math.random() * 100,
      delay: Math.random() * 500,
      color: colors[i % colors.length],
    }));
    setParticles(newParticles);

    // Clear after animation
    const timer = setTimeout(() => setParticles([]), 2500);
    return () => clearTimeout(timer);
  }, [active]);

  if (!active || particles.length === 0) return null;

  return (
    <div className="absolute inset-0 overflow-hidden pointer-events-none">
      {particles.map((p) => (
        <div
          key={p.id}
          className="absolute w-2 h-2 rounded-full animate-confetti"
          style={{
            left: `${p.x}%`,
            top: '-10px',
            backgroundColor: p.color,
            animationDelay: `${p.delay}ms`,
          }}
        />
      ))}
      <style>{`
        @keyframes confetti {
          0% {
            transform: translateY(0) rotate(0deg);
            opacity: 1;
          }
          100% {
            transform: translateY(400px) rotate(720deg);
            opacity: 0;
          }
        }
        .animate-confetti {
          animation: confetti 2s ease-out forwards;
        }
      `}</style>
    </div>
  );
}

// =============================================================================
// Main Component
// =============================================================================

/**
 * DayClosurePrompt
 *
 * Gentle reminder to crystallize the day's marks.
 * Appears after 6 PM if no crystal exists.
 *
 * @example Basic usage:
 * ```tsx
 * <DayClosurePrompt
 *   markCount={12}
 *   hasCrystal={false}
 *   onCrystallize={handleCrystallize}
 * />
 * ```
 */
export function DayClosurePrompt({
  markCount,
  marks,
  hasCrystal,
  onCrystallize,
  onDismiss,
  forceShow,
}: DayClosurePromptProps) {
  const { shouldShow, snooze } = useClosureVisibility(hasCrystal, forceShow);
  const [isLoading, setIsLoading] = useState(false);
  const [showConfetti, setShowConfetti] = useState(false);
  const [result, setResult] = useState<{
    crystal: Crystal;
    honesty: CompressionHonesty;
  } | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Handle crystallization
  const handleCrystallize = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      const crystalResult = await onCrystallize();
      if (crystalResult) {
        setResult(crystalResult);
        setShowConfetti(true);
      } else {
        setError('Not enough marks to create a crystal. A few more and you can seal the day.');
      }
    } catch {
      setError('Something went wrong. You can try again when you are ready.');
    } finally {
      setIsLoading(false);
    }
  }, [onCrystallize]);

  // Handle dismiss
  const handleDismiss = useCallback(() => {
    snooze();
    onDismiss?.();
  }, [snooze, onDismiss]);

  // Don't render if shouldn't show and no result
  if (!shouldShow && !result) {
    return null;
  }

  // Success state - show the sealed crystal
  if (result) {
    return (
      <div className="fixed inset-0 z-50 flex items-center justify-center">
        {/* Backdrop */}
        <div
          className="absolute inset-0 backdrop-blur-sm"
          style={{ background: `${LIVING_EARTH.bark}CC` }}
        />

        {/* Confetti */}
        <Confetti active={showConfetti} />

        {/* Content */}
        <GrowingContainer autoTrigger duration="deliberate">
          <div
            className="relative z-10 max-w-md mx-4 p-6 rounded-2xl"
            style={{
              background: LIVING_EARTH.bark,
              border: `1px solid ${LIVING_EARTH.amber}44`,
              boxShadow: `0 8px 32px ${LIVING_EARTH.bark}`,
            }}
          >
            {/* Success header */}
            <div className="text-center mb-6">
              <div
                className="inline-flex items-center justify-center w-16 h-16 rounded-full mb-4"
                style={{ background: `${LIVING_EARTH.amber}22` }}
              >
                <svg
                  width="32"
                  height="32"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke={LIVING_EARTH.amber}
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                >
                  <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2" />
                </svg>
              </div>
              <h2
                className="text-xl font-medium mb-2"
                style={{ color: LIVING_EARTH.lantern }}
              >
                Day sealed.
              </h2>
              <p style={{ color: LIVING_EARTH.sand }}>
                Your story is preserved.
              </p>
            </div>

            {/* Crystal preview */}
            <div
              className="p-4 rounded-xl mb-4"
              style={{ background: `${LIVING_EARTH.sage}11` }}
            >
              <p
                className="text-sm leading-relaxed mb-3"
                style={{ color: LIVING_EARTH.lantern }}
              >
                {result.crystal.insight}
              </p>
              <p
                className="text-xs italic"
                style={{ color: LIVING_EARTH.sage }}
              >
                {result.crystal.significance}
              </p>
            </div>

            {/* Warm closing message */}
            <p
              className="text-sm text-center mb-4 italic"
              style={{ color: LIVING_EARTH.sand }}
            >
              The day ends with warmth, not exhaustion.
            </p>

            {/* Close button */}
            <button
              onClick={() => setResult(null)}
              className="w-full py-3 rounded-xl transition-all"
              style={{
                background: `${LIVING_EARTH.sage}22`,
                color: LIVING_EARTH.sage,
              }}
            >
              Continue
            </button>
          </div>
        </GrowingContainer>
      </div>
    );
  }

  // Main prompt state
  return (
    <div className="fixed inset-0 z-50 flex items-end sm:items-center justify-center">
      {/* Backdrop - clickable to dismiss */}
      <div
        className="absolute inset-0 backdrop-blur-sm cursor-pointer"
        style={{ background: `${LIVING_EARTH.bark}99` }}
        onClick={handleDismiss}
      />

      {/* Prompt panel - slides up from bottom on mobile */}
      <GrowingContainer autoTrigger duration="normal">
        <div
          className="relative z-10 w-full max-w-md mx-4 mb-4 sm:mb-0 p-6 rounded-2xl"
          style={{
            background: LIVING_EARTH.bark,
            border: `1px solid ${LIVING_EARTH.amber}33`,
            boxShadow: `0 -4px 24px ${LIVING_EARTH.bark}80`,
          }}
        >
          {/* Header */}
          <div className="flex items-start justify-between mb-4">
            <div>
              <h2
                className="text-lg font-medium mb-1"
                style={{ color: LIVING_EARTH.lantern }}
              >
                Ready to crystallize?
              </h2>
              <p style={{ color: LIVING_EARTH.sand }}>
                Your trail has {markCount} mark{markCount !== 1 ? 's' : ''} today.
              </p>
            </div>
            <button
              onClick={handleDismiss}
              className="p-2 rounded-lg transition-opacity opacity-60 hover:opacity-100"
              aria-label="Dismiss"
            >
              <svg
                width="20"
                height="20"
                viewBox="0 0 24 24"
                fill="none"
                stroke={LIVING_EARTH.sand}
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              >
                <path d="M18 6L6 18M6 6l12 12" />
              </svg>
            </button>
          </div>

          {/* Marks preview */}
          {marks && marks.length > 0 && (
            <div
              className="mb-4 p-3 rounded-xl max-h-32 overflow-y-auto"
              style={{ background: `${LIVING_EARTH.sage}08` }}
            >
              <p
                className="text-xs uppercase tracking-wide mb-2 opacity-60"
                style={{ color: LIVING_EARTH.sand }}
              >
                Preview
              </p>
              <div className="space-y-1">
                {marks.slice(-5).map((mark) => (
                  <p
                    key={mark.mark_id}
                    className="text-sm truncate"
                    style={{ color: LIVING_EARTH.clay }}
                  >
                    {mark.content}
                  </p>
                ))}
                {marks.length > 5 && (
                  <p
                    className="text-xs opacity-60"
                    style={{ color: LIVING_EARTH.sand }}
                  >
                    and {marks.length - 5} more...
                  </p>
                )}
              </div>
            </div>
          )}

          {/* Error message */}
          {error && (
            <div
              className="mb-4 p-3 rounded-xl text-sm"
              style={{
                background: `${LIVING_EARTH.rust}11`,
                color: LIVING_EARTH.rust,
              }}
            >
              {error}
            </div>
          )}

          {/* Actions */}
          <div className="flex gap-3">
            <button
              onClick={handleDismiss}
              className="flex-1 py-3 rounded-xl transition-all"
              style={{
                background: `${LIVING_EARTH.sage}11`,
                color: LIVING_EARTH.sand,
              }}
            >
              Not yet
            </button>
            <button
              onClick={handleCrystallize}
              disabled={isLoading || markCount < 1}
              className="flex-1 py-3 rounded-xl font-medium transition-all disabled:opacity-50"
              style={{
                background: LIVING_EARTH.amber,
                color: LIVING_EARTH.bark,
              }}
            >
              {isLoading ? (
                <span className="flex items-center justify-center gap-2">
                  <svg
                    className="animate-spin"
                    width="16"
                    height="16"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2"
                  >
                    <path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83" />
                  </svg>
                  Crystallizing...
                </span>
              ) : (
                'Crystallize'
              )}
            </button>
          </div>

          {/* Reassurance */}
          <p
            className="text-xs text-center mt-4 opacity-50"
            style={{ color: LIVING_EARTH.sand }}
          >
            You can always come back later. No rush.
          </p>
        </div>
      </GrowingContainer>
    </div>
  );
}

// =============================================================================
// Exports
// =============================================================================

export default DayClosurePrompt;
