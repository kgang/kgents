/**
 * MarkCaptureInput - Quick mark entry for Daily Lab
 *
 * Design Goals (QA-1):
 * - Less than 5 seconds to capture a mark
 * - Lighter than a to-do list
 * - No friction; instant capture
 *
 * WARMTH Calibration:
 * - Primary joy: FLOW (quick capture)
 * - Prompt: "What's on your mind?"
 *
 * @see pilots/trail-to-crystal-daily-lab/PROTO_SPEC.md
 * @see impl/claude/services/witness/daily_lab.py
 */

import { useState, useCallback, useRef, useEffect, type KeyboardEvent } from 'react';
import { useWindowLayout } from '../hooks/useLayoutContext';
import { GrowingContainer } from '../joy/GrowingContainer';
import { LIVING_EARTH } from '../constants';

// =============================================================================
// Types
// =============================================================================

/** Daily Lab intent tags from backend */
export type DailyTag = 'eureka' | 'gotcha' | 'taste' | 'friction' | 'joy' | 'veto';

/** Mark capture request - matches backend CaptureRequest */
export interface CaptureRequest {
  content: string;
  tag?: DailyTag;
  reasoning?: string;
}

/** Mark capture response - matches backend CaptureResponse */
export interface CaptureResponse {
  mark_id: string;
  content: string;
  tag: string | null;
  timestamp: string;
  warmth_response: string;
}

export interface MarkCaptureInputProps {
  /** Callback when mark is submitted */
  onCapture: (request: CaptureRequest) => Promise<CaptureResponse | void>;

  /** Optional placeholder override */
  placeholder?: string;

  /** Show tag selector by default */
  showTags?: boolean;

  /** Disabled state */
  disabled?: boolean;

  /** Custom className */
  className?: string;

  /** Auto-focus on mount */
  autoFocus?: boolean;
}

// =============================================================================
// Constants
// =============================================================================

/** Tag metadata for display */
const TAG_META: Record<DailyTag, { label: string; description: string }> = {
  eureka: { label: 'Eureka', description: 'A breakthrough or insight' },
  gotcha: { label: 'Gotcha', description: 'Something that tripped you up' },
  taste: { label: 'Taste', description: 'A design or aesthetic decision' },
  friction: { label: 'Friction', description: 'Resistance encountered' },
  joy: { label: 'Joy', description: 'A moment of delight' },
  veto: { label: 'Veto', description: 'Something that felt wrong' },
};

/** Density-aware sizing */
const SIZES = {
  compact: { padding: 'p-2', text: 'text-sm', tagSize: 'text-xs px-2 py-1' },
  comfortable: { padding: 'p-3', text: 'text-base', tagSize: 'text-sm px-3 py-1.5' },
  spacious: { padding: 'p-4', text: 'text-base', tagSize: 'text-sm px-3 py-2' },
} as const;

// =============================================================================
// Component
// =============================================================================

/**
 * MarkCaptureInput
 *
 * Quick mark capture with < 5 second flow.
 * Supports optional tag and reasoning for deeper reflection.
 *
 * @example Quick capture:
 * ```tsx
 * <MarkCaptureInput
 *   onCapture={async (req) => {
 *     const response = await api.capture(req);
 *     console.log(response.warmth_response);
 *   }}
 * />
 * ```
 *
 * @example With tags visible:
 * ```tsx
 * <MarkCaptureInput onCapture={handleCapture} showTags />
 * ```
 */
export function MarkCaptureInput({
  onCapture,
  placeholder = "What's on your mind?",
  showTags = false,
  disabled = false,
  className = '',
  autoFocus = false,
}: MarkCaptureInputProps) {
  const { density } = useWindowLayout();
  const sizes = SIZES[density];

  // State
  const [content, setContent] = useState('');
  const [selectedTag, setSelectedTag] = useState<DailyTag | null>(null);
  const [isTagSelectorOpen, setIsTagSelectorOpen] = useState(showTags);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [lastResponse, setLastResponse] = useState<string | null>(null);

  // Refs
  const inputRef = useRef<HTMLTextAreaElement>(null);

  // Auto-focus
  useEffect(() => {
    if (autoFocus && inputRef.current) {
      inputRef.current.focus();
    }
  }, [autoFocus]);

  // Clear response after a delay
  useEffect(() => {
    if (lastResponse) {
      const timeout = setTimeout(() => setLastResponse(null), 3000);
      return () => clearTimeout(timeout);
    }
  }, [lastResponse]);

  // Handle submission
  const handleSubmit = useCallback(async () => {
    if (!content.trim() || isSubmitting || disabled) return;

    setIsSubmitting(true);
    try {
      const request: CaptureRequest = {
        content: content.trim(),
        tag: selectedTag ?? undefined,
      };

      const response = await onCapture(request);

      // Clear form on success
      setContent('');
      setSelectedTag(null);
      setIsTagSelectorOpen(showTags);

      // Show warmth response
      if (response?.warmth_response) {
        setLastResponse(response.warmth_response);
      }

      // Refocus input
      inputRef.current?.focus();
    } catch (error) {
      console.error('Failed to capture mark:', error);
    } finally {
      setIsSubmitting(false);
    }
  }, [content, selectedTag, isSubmitting, disabled, onCapture, showTags]);

  // Handle keyboard shortcuts
  const handleKeyDown = useCallback(
    (e: KeyboardEvent<HTMLTextAreaElement>) => {
      // Enter without shift submits
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        handleSubmit();
      }
      // Escape clears
      if (e.key === 'Escape') {
        setContent('');
        setSelectedTag(null);
      }
    },
    [handleSubmit]
  );

  // Toggle tag
  const toggleTag = useCallback((tag: DailyTag) => {
    setSelectedTag((prev) => (prev === tag ? null : tag));
  }, []);

  return (
    <div
      className={`mark-capture-input ${className}`}
      style={{
        background: LIVING_EARTH.bark,
        borderRadius: 12,
        border: `1px solid ${LIVING_EARTH.sage}33`,
      }}
    >
      {/* Input Area */}
      <div className={sizes.padding}>
        <textarea
          ref={inputRef}
          value={content}
          onChange={(e) => setContent(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          disabled={disabled || isSubmitting}
          className={`
            w-full bg-transparent resize-none outline-none
            ${sizes.text}
            placeholder:opacity-50
          `}
          style={{
            color: LIVING_EARTH.lantern,
            minHeight: density === 'compact' ? 40 : 56,
          }}
          rows={1}
          aria-label="Mark capture input"
        />
      </div>

      {/* Tag Selector */}
      {isTagSelectorOpen && (
        <div
          className={`flex flex-wrap gap-2 ${sizes.padding} border-t`}
          style={{ borderColor: `${LIVING_EARTH.sage}22` }}
        >
          {(Object.keys(TAG_META) as DailyTag[]).map((tag) => (
            <button
              key={tag}
              onClick={() => toggleTag(tag)}
              disabled={disabled || isSubmitting}
              className={`
                ${sizes.tagSize}
                rounded-full
                transition-all duration-150
                ${
                  selectedTag === tag
                    ? 'ring-2 ring-offset-1'
                    : 'opacity-70 hover:opacity-100'
                }
              `}
              style={{
                background:
                  selectedTag === tag
                    ? `${LIVING_EARTH.amber}33`
                    : `${LIVING_EARTH.sage}22`,
                color:
                  selectedTag === tag ? LIVING_EARTH.amber : LIVING_EARTH.sand,
                // Ring color is set via Tailwind class (ring-amber-500) or CSS custom property
                ['--tw-ring-color' as string]: LIVING_EARTH.amber,
              }}
              title={TAG_META[tag].description}
              aria-pressed={selectedTag === tag}
            >
              {TAG_META[tag].label}
            </button>
          ))}
        </div>
      )}

      {/* Action Bar */}
      <div
        className={`flex items-center justify-between ${sizes.padding} border-t`}
        style={{ borderColor: `${LIVING_EARTH.sage}22` }}
      >
        {/* Left: Toggle tags */}
        <button
          onClick={() => setIsTagSelectorOpen((prev) => !prev)}
          className="text-sm opacity-60 hover:opacity-100 transition-opacity"
          style={{ color: LIVING_EARTH.clay }}
          aria-expanded={isTagSelectorOpen}
          aria-label={isTagSelectorOpen ? 'Hide tags' : 'Show tags'}
        >
          {isTagSelectorOpen ? 'Hide tags' : 'Add tag'}
        </button>

        {/* Right: Submit button */}
        <button
          onClick={handleSubmit}
          disabled={!content.trim() || isSubmitting || disabled}
          className={`
            ${sizes.tagSize}
            rounded-lg
            font-medium
            transition-all duration-150
            disabled:opacity-40 disabled:cursor-not-allowed
          `}
          style={{
            background: content.trim()
              ? LIVING_EARTH.amber
              : `${LIVING_EARTH.sage}33`,
            color: content.trim() ? LIVING_EARTH.bark : LIVING_EARTH.clay,
          }}
        >
          {isSubmitting ? 'Capturing...' : 'Capture'}
        </button>
      </div>

      {/* Warmth Response */}
      {lastResponse && (
        <GrowingContainer autoTrigger duration="quick">
          <div
            className={`${sizes.padding} text-center`}
            style={{
              color: LIVING_EARTH.sage,
              background: `${LIVING_EARTH.sage}11`,
              borderTop: `1px solid ${LIVING_EARTH.sage}22`,
            }}
          >
            {lastResponse}
          </div>
        </GrowingContainer>
      )}
    </div>
  );
}

// =============================================================================
// Exports
// =============================================================================

export default MarkCaptureInput;
