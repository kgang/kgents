/**
 * CrystalCard - Memory artifact display for Daily Lab
 *
 * Design Goals (QA-3, QA-4):
 * - Warmth, not clinical (witnessed, not surveilled)
 * - Crystal feels like a memory artifact, not a summary
 * - Shows compression ratio and dropped marks honestly
 * - Shareable/exportable
 *
 * WARMTH Calibration:
 * - "I noticed some patterns worth keeping."
 * - "To keep this clear, I'm setting aside: {dropped}"
 *
 * @see pilots/trail-to-crystal-daily-lab/PROTO_SPEC.md
 * @see impl/claude/services/witness/daily_lab.py
 */

import { useMemo, useCallback, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useWindowLayout } from '@/hooks/useLayoutContext';
import { GrowingContainer } from '@/components/joy';
import { LIVING_EARTH, TIMING } from '@/constants';

// =============================================================================
// Types
// =============================================================================

/** Crystal data from backend DailyCrystal */
export interface Crystal {
  crystal_id: string;
  insight: string;
  significance: string;
  disclosure: string;
  level: 'session' | 'day' | 'week' | 'epoch';
  timestamp: string;
  confidence: number;
  topics?: string[];
  principles?: string[];
}

/** Compression honesty details */
export interface CompressionHonesty {
  dropped_count: number;
  dropped_tags: string[];
  dropped_summaries: string[];
  galois_loss: number;
}

export interface CrystalCardProps {
  /** The crystal to display */
  crystal: Crystal;

  /** Compression honesty details (optional) */
  honesty?: CompressionHonesty;

  /** Callback when share is clicked */
  onShare?: (crystal: Crystal) => void;

  /** Callback when export is clicked */
  onExport?: (crystal: Crystal, format: 'markdown' | 'json') => void;

  /** Expanded state (controlled) */
  isExpanded?: boolean;

  /** Callback when expanded state changes */
  onExpandedChange?: (expanded: boolean) => void;

  /** Custom className */
  className?: string;

  /** Display variant */
  variant?: 'card' | 'compact' | 'full';
}

// =============================================================================
// Constants
// =============================================================================

/** Level display names */
const LEVEL_LABELS: Record<Crystal['level'], string> = {
  session: 'Session Crystal',
  day: 'Daily Crystal',
  week: 'Weekly Crystal',
  epoch: 'Epoch Crystal',
};

/** Level icons (SVG paths) */
const LEVEL_ICONS: Record<Crystal['level'], string> = {
  session: 'M12 2 2 7l10 5 10-5-10-5Z M2 17l10 5 10-5 M2 12l10 5 10-5',
  day: 'M12 2v10M12 22v-4M4.93 4.93l7.07 7.07M19.07 19.07l-2.83-2.83M2 12h4M22 12h-4M4.93 19.07l2.83-2.83M19.07 4.93l-7.07 7.07',
  week: 'M4 8h16M4 14h16M12 4v16',
  epoch: 'M12 2l-2 8h4l-2 8M8 12a4 4 0 1 0 8 0 4 4 0 1 0-8 0',
};

/** Density-aware sizing */
const SIZES = {
  compact: {
    padding: 'p-3',
    text: 'text-sm',
    title: 'text-base',
    iconSize: 16,
  },
  comfortable: {
    padding: 'p-4',
    text: 'text-base',
    title: 'text-lg',
    iconSize: 20,
  },
  spacious: {
    padding: 'p-6',
    text: 'text-base',
    title: 'text-xl',
    iconSize: 24,
  },
} as const;

// =============================================================================
// Sub-components
// =============================================================================

interface CrystalIconProps {
  level: Crystal['level'];
  size: number;
}

function CrystalIcon({ level, size }: CrystalIconProps) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke={LIVING_EARTH.amber}
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d={LEVEL_ICONS[level]} />
    </svg>
  );
}

interface ConfidenceMeterProps {
  confidence: number;
  size?: 'sm' | 'md';
}

function ConfidenceMeter({ confidence, size = 'md' }: ConfidenceMeterProps) {
  const percent = Math.round(confidence * 100);
  const barHeight = size === 'sm' ? 4 : 6;

  return (
    <div className="flex items-center gap-2">
      <div
        className="flex-1 rounded-full overflow-hidden"
        style={{
          height: barHeight,
          background: `${LIVING_EARTH.sage}33`,
        }}
      >
        <div
          className="h-full rounded-full transition-all duration-500"
          style={{
            width: `${percent}%`,
            background:
              confidence > 0.8
                ? LIVING_EARTH.sage
                : confidence > 0.5
                  ? LIVING_EARTH.amber
                  : LIVING_EARTH.clay,
          }}
        />
      </div>
      <span
        className="text-xs opacity-60"
        style={{ color: LIVING_EARTH.sand }}
      >
        {percent}%
      </span>
    </div>
  );
}

interface DisclosureBlockProps {
  honesty: CompressionHonesty;
  sizes: (typeof SIZES)[keyof typeof SIZES];
}

function DisclosureBlock({ honesty, sizes }: DisclosureBlockProps) {
  const [showDetails, setShowDetails] = useState(false);

  if (honesty.dropped_count === 0) {
    return (
      <div
        className={`${sizes.text} opacity-60`}
        style={{ color: LIVING_EARTH.sage }}
      >
        Everything was preserved.
      </div>
    );
  }

  const lossPercent = Math.round(honesty.galois_loss * 100);

  return (
    <div>
      <button
        onClick={() => setShowDetails(!showDetails)}
        className="flex items-center gap-2 opacity-70 hover:opacity-100 transition-opacity"
        style={{ color: LIVING_EARTH.sand }}
        aria-expanded={showDetails}
      >
        <span className={sizes.text}>
          Set aside {honesty.dropped_count} note
          {honesty.dropped_count !== 1 ? 's' : ''} to keep this focused
          {lossPercent > 0 && ` (drift: ${lossPercent}%)`}
        </span>
        <svg
          width="12"
          height="12"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          style={{
            transform: showDetails ? 'rotate(180deg)' : 'rotate(0deg)',
            transition: `transform ${TIMING.standard}ms`,
          }}
        >
          <path d="m6 9 6 6 6-6" />
        </svg>
      </button>

      <AnimatePresence>
        {showDetails && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: TIMING.standard / 1000 }}
            className="overflow-hidden"
          >
            <div
              className={`mt-2 ${sizes.padding} rounded-lg`}
              style={{ background: `${LIVING_EARTH.sage}11` }}
            >
              {/* Dropped tags */}
              {honesty.dropped_tags.length > 0 && (
                <div className="mb-2">
                  <span
                    className="text-xs opacity-60"
                    style={{ color: LIVING_EARTH.sand }}
                  >
                    Mostly:
                  </span>
                  <div className="flex flex-wrap gap-1 mt-1">
                    {honesty.dropped_tags.map((tag) => (
                      <span
                        key={tag}
                        className="text-xs px-2 py-0.5 rounded-full"
                        style={{
                          background: `${LIVING_EARTH.sage}22`,
                          color: LIVING_EARTH.clay,
                        }}
                      >
                        {tag}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Dropped summaries preview */}
              {honesty.dropped_summaries.length > 0 && (
                <div>
                  <span
                    className="text-xs opacity-60"
                    style={{ color: LIVING_EARTH.sand }}
                  >
                    Preview:
                  </span>
                  <ul className="mt-1 space-y-1">
                    {honesty.dropped_summaries.slice(0, 3).map((summary, i) => (
                      <li
                        key={i}
                        className="text-xs opacity-60"
                        style={{ color: LIVING_EARTH.clay }}
                      >
                        {summary}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

// =============================================================================
// Main Component
// =============================================================================

/**
 * CrystalCard
 *
 * Displays a compressed crystal with warmth and honesty.
 * Shows insight, significance, and compression disclosure.
 *
 * @example Basic usage:
 * ```tsx
 * <CrystalCard
 *   crystal={dailyCrystal.crystal}
 *   honesty={dailyCrystal.honesty}
 * />
 * ```
 *
 * @example With actions:
 * ```tsx
 * <CrystalCard
 *   crystal={crystal}
 *   onShare={(c) => shareToClipboard(c)}
 *   onExport={(c, fmt) => downloadAs(c, fmt)}
 * />
 * ```
 */
export function CrystalCard({
  crystal,
  honesty,
  onShare,
  onExport,
  isExpanded: controlledExpanded,
  onExpandedChange,
  className = '',
  variant = 'card',
}: CrystalCardProps) {
  const { density } = useWindowLayout();
  const sizes = SIZES[density];

  // Internal expanded state
  const [internalExpanded, setInternalExpanded] = useState(false);
  const isExpanded = controlledExpanded ?? internalExpanded;
  const setIsExpanded = onExpandedChange ?? setInternalExpanded;

  // Format timestamp
  const formattedDate = useMemo(() => {
    const date = new Date(crystal.timestamp);
    return date.toLocaleDateString('en-US', {
      weekday: 'short',
      month: 'short',
      day: 'numeric',
      year: date.getFullYear() !== new Date().getFullYear() ? 'numeric' : undefined,
    });
  }, [crystal.timestamp]);

  // Handle share
  const handleShare = useCallback(() => {
    onShare?.(crystal);
  }, [crystal, onShare]);

  // Handle export
  const handleExport = useCallback(
    (format: 'markdown' | 'json') => {
      onExport?.(crystal, format);
    },
    [crystal, onExport]
  );

  // Compact variant
  if (variant === 'compact') {
    return (
      <div
        className={`flex items-start gap-3 ${sizes.padding} ${className}`}
        style={{
          background: LIVING_EARTH.bark,
          borderRadius: 8,
          border: `1px solid ${LIVING_EARTH.sage}22`,
        }}
      >
        <CrystalIcon level={crystal.level} size={sizes.iconSize} />
        <div className="flex-1 min-w-0">
          <p
            className={`${sizes.text} line-clamp-2`}
            style={{ color: LIVING_EARTH.lantern }}
          >
            {crystal.insight}
          </p>
          <span
            className="text-xs opacity-60"
            style={{ color: LIVING_EARTH.sand }}
          >
            {formattedDate}
          </span>
        </div>
      </div>
    );
  }

  return (
    <GrowingContainer autoTrigger duration="normal">
      <div
        className={`crystal-card ${className}`}
        style={{
          background: LIVING_EARTH.bark,
          borderRadius: 16,
          border: `1px solid ${LIVING_EARTH.amber}33`,
          boxShadow: `0 4px 24px ${LIVING_EARTH.bark}80`,
        }}
      >
        {/* Header */}
        <div
          className={`flex items-start justify-between ${sizes.padding} border-b`}
          style={{ borderColor: `${LIVING_EARTH.amber}22` }}
        >
          <div className="flex items-center gap-3">
            <CrystalIcon level={crystal.level} size={sizes.iconSize} />
            <div>
              <h3
                className={`${sizes.title} font-medium`}
                style={{ color: LIVING_EARTH.lantern }}
              >
                {LEVEL_LABELS[crystal.level]}
              </h3>
              <span
                className="text-xs opacity-60"
                style={{ color: LIVING_EARTH.sand }}
              >
                {formattedDate}
              </span>
            </div>
          </div>

          {/* Confidence */}
          <div className="w-24">
            <ConfidenceMeter confidence={crystal.confidence} size="sm" />
          </div>
        </div>

        {/* Content */}
        <div className={sizes.padding}>
          {/* Insight - The Core */}
          <div className="mb-4">
            <p
              className={`${sizes.text} leading-relaxed`}
              style={{ color: LIVING_EARTH.clay }}
            >
              {crystal.insight}
            </p>
          </div>

          {/* Significance */}
          <div className="mb-4">
            <span
              className="text-xs font-medium uppercase tracking-wide opacity-60"
              style={{ color: LIVING_EARTH.sand }}
            >
              Why this matters
            </span>
            <p
              className={`${sizes.text} mt-1`}
              style={{ color: LIVING_EARTH.sand }}
            >
              {crystal.significance}
            </p>
          </div>

          {/* Topics */}
          {crystal.topics && crystal.topics.length > 0 && (
            <div className="flex flex-wrap gap-2 mb-4">
              {crystal.topics.map((topic) => (
                <span
                  key={topic}
                  className="text-xs px-2 py-1 rounded-full"
                  style={{
                    background: `${LIVING_EARTH.sage}22`,
                    color: LIVING_EARTH.sage,
                  }}
                >
                  {topic}
                </span>
              ))}
            </div>
          )}

          {/* Compression Disclosure (Amendment G) */}
          {honesty && (
            <div
              className="pt-4 border-t"
              style={{ borderColor: `${LIVING_EARTH.sage}22` }}
            >
              <DisclosureBlock honesty={honesty} sizes={sizes} />
            </div>
          )}

          {/* Fallback disclosure from crystal */}
          {!honesty && crystal.disclosure && (
            <div
              className={`pt-4 border-t ${sizes.text} opacity-60`}
              style={{
                borderColor: `${LIVING_EARTH.sage}22`,
                color: LIVING_EARTH.sage,
              }}
            >
              {crystal.disclosure}
            </div>
          )}
        </div>

        {/* Actions */}
        {(onShare || onExport) && (
          <div
            className={`flex items-center justify-end gap-2 ${sizes.padding} border-t`}
            style={{ borderColor: `${LIVING_EARTH.sage}22` }}
          >
            {onShare && (
              <button
                onClick={handleShare}
                className="flex items-center gap-1 px-3 py-1.5 rounded-lg text-sm opacity-70 hover:opacity-100 transition-opacity"
                style={{ color: LIVING_EARTH.sand }}
              >
                <svg
                  width="14"
                  height="14"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                >
                  <path d="M4 12v8a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-8M16 6l-4-4-4 4M12 2v13" />
                </svg>
                Share
              </button>
            )}
            {onExport && (
              <div className="relative group">
                <button
                  className="flex items-center gap-1 px-3 py-1.5 rounded-lg text-sm opacity-70 hover:opacity-100 transition-opacity"
                  style={{ color: LIVING_EARTH.sand }}
                >
                  <svg
                    width="14"
                    height="14"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2"
                  >
                    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M7 10l5 5 5-5M12 15V3" />
                  </svg>
                  Export
                </button>
                <div
                  className="absolute right-0 top-full mt-1 py-1 rounded-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all"
                  style={{
                    background: LIVING_EARTH.bark,
                    border: `1px solid ${LIVING_EARTH.sage}33`,
                  }}
                >
                  <button
                    onClick={() => handleExport('markdown')}
                    className="block w-full px-4 py-1.5 text-sm text-left hover:bg-white/5"
                    style={{ color: LIVING_EARTH.sand }}
                  >
                    Markdown
                  </button>
                  <button
                    onClick={() => handleExport('json')}
                    className="block w-full px-4 py-1.5 text-sm text-left hover:bg-white/5"
                    style={{ color: LIVING_EARTH.sand }}
                  >
                    JSON
                  </button>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </GrowingContainer>
  );
}

// =============================================================================
// Exports
// =============================================================================

export default CrystalCard;
