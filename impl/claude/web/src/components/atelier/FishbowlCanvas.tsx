/**
 * FishbowlCanvas - Live creation stream with organic breathing border
 *
 * The centerpiece of the Atelier spectator experience.
 * Spectators gather around the fishbowl to watch creation unfold in real-time.
 *
 * Features:
 * - Breathing border animation (3-4s cycle) using LIVING_EARTH.amber
 * - Content fade-in using useGrowing hook
 * - Spectator count badge
 * - Optional spectator cursor overlay
 * - SSE subscription for live updates
 *
 * @see plans/crown-jewels-genesis-phase2.md - Week 3: FishbowlCanvas Core
 * @see docs/skills/crown-jewel-patterns.md - Pattern 1: Container Owns Workflow
 */

import React, { useEffect, useCallback, useMemo } from 'react';
import { Eye } from 'lucide-react';
import { useBreathing } from '@/hooks/useBreathing';
import { useGrowing } from '@/hooks/useGrowing';
import { LIVING_EARTH } from '@/constants/colors';
import { cn } from '@/lib/utils';

// =============================================================================
// Types
// =============================================================================

export interface ArtisanSummary {
  id: string;
  name: string;
  specialty: string;
  style?: string;
  is_active: boolean;
}

export interface SpectatorCursor {
  id: string;
  position: { x: number; y: number };
  citizenId?: string;
  eigenvector?: number[];
  lastUpdate: number;
}

export interface FishbowlCanvasProps {
  /** Session ID for SSE subscription */
  sessionId: string;
  /** Current artisan (creator) */
  artisan: ArtisanSummary | null;
  /** Whether the stream is live */
  isLive: boolean;
  /** Content to display */
  content: string;
  /** Content type for rendering */
  contentType: 'image' | 'text' | 'code';
  /** Number of spectators watching */
  spectatorCount: number;
  /** Optional spectator cursors for overlay */
  spectatorCursors?: SpectatorCursor[];
  /** Show spectator cursor overlay */
  showCursors?: boolean;
  /** Click handler for canvas interactions */
  onCanvasClick?: (position: { x: number; y: number }) => void;
  /** Optional class name for styling */
  className?: string;
}

// =============================================================================
// Breathing Border Configuration
// =============================================================================

const BREATHING_CONFIG = {
  duration: 4000,    // 4s full cycle (Ghibli-inspired)
  baseIntensity: 0.3,
  maxIntensity: 0.6,
  glowRadius: 20,
  insetGlowRadius: 10,
} as const;

// =============================================================================
// Component: SpectatorBadge
// =============================================================================

interface SpectatorBadgeProps {
  count: number;
  isLive: boolean;
}

function SpectatorBadge({ count, isLive }: SpectatorBadgeProps) {
  const { style: breatheStyle } = useBreathing({
    enabled: isLive,
    period: 3000,
    amplitude: 0.02,
  });

  return (
    <div
      className={cn(
        'absolute bottom-4 right-4 z-10',
        'flex items-center gap-1.5 px-2.5 py-1.5 rounded-full',
        'text-sm font-medium',
        'backdrop-blur-sm transition-colors duration-300',
        isLive
          ? 'bg-green-500/20 text-green-300 border border-green-500/30'
          : 'bg-stone-500/20 text-stone-400 border border-stone-500/30'
      )}
      style={isLive ? breatheStyle : undefined}
    >
      {isLive && (
        <span
          className="w-2 h-2 rounded-full bg-green-400 animate-pulse"
          aria-hidden="true"
        />
      )}
      <Eye className="w-3.5 h-3.5" aria-hidden="true" />
      <span>{count}</span>
      <span className="sr-only">spectators watching</span>
    </div>
  );
}

// =============================================================================
// Component: ContentRenderer
// =============================================================================

interface ContentRendererProps {
  content: string;
  contentType: 'image' | 'text' | 'code';
  isVisible: boolean;
}

function ContentRenderer({ content, contentType, isVisible }: ContentRendererProps) {
  const { style, trigger } = useGrowing({
    enabled: true,
    duration: 400,
  });

  // Trigger growth animation when content appears
  useEffect(() => {
    if (isVisible && content) {
      trigger();
    }
  }, [isVisible, content, trigger]);

  if (!content) {
    return (
      <div className="flex items-center justify-center h-full text-stone-500 italic">
        Awaiting creation...
      </div>
    );
  }

  return (
    <div style={style} className="h-full overflow-auto">
      {contentType === 'image' && (
        <img
          src={content}
          alt="Created artwork"
          className="max-w-full max-h-full object-contain mx-auto"
        />
      )}

      {contentType === 'text' && (
        <div className="p-6 text-stone-200 whitespace-pre-wrap leading-relaxed font-serif">
          {content}
        </div>
      )}

      {contentType === 'code' && (
        <pre className="p-6 text-sm text-stone-300 font-mono overflow-x-auto">
          <code>{content}</code>
        </pre>
      )}
    </div>
  );
}

// =============================================================================
// Component: ArtisanHeader
// =============================================================================

interface ArtisanHeaderProps {
  artisan: ArtisanSummary | null;
  isLive: boolean;
}

function ArtisanHeader({ artisan, isLive }: ArtisanHeaderProps) {
  if (!artisan) return null;

  return (
    <div className="absolute top-4 left-4 z-10">
      <div
        className={cn(
          'flex items-center gap-2 px-3 py-2 rounded-lg',
          'backdrop-blur-sm',
          'bg-stone-800/60 border border-stone-700/50'
        )}
      >
        <div className="flex flex-col">
          <span className="text-sm font-medium text-stone-200">
            {artisan.name}
          </span>
          <span className="text-xs text-stone-400">
            {artisan.specialty}
          </span>
        </div>
        {isLive && (
          <span className="px-2 py-0.5 text-xs font-medium bg-green-500/20 text-green-300 rounded">
            LIVE
          </span>
        )}
      </div>
    </div>
  );
}

// =============================================================================
// Component: FishbowlCanvas
// =============================================================================

export function FishbowlCanvas({
  sessionId,
  artisan,
  isLive,
  content,
  contentType,
  spectatorCount,
  spectatorCursors = [],
  showCursors = false,
  onCanvasClick,
  className,
}: FishbowlCanvasProps) {
  // Breathing animation for border
  const { scale, isBreathing } = useBreathing({
    enabled: isLive,
    period: BREATHING_CONFIG.duration,
    amplitude: 0.01, // Subtle scale
  });

  // Calculate breathing intensity for glow
  const breathIntensity = useMemo(() => {
    if (!isBreathing) return BREATHING_CONFIG.baseIntensity;
    // Map scale (0.99 - 1.01) to intensity (0.3 - 0.6)
    const normalized = (scale - 0.99) / 0.02;
    return BREATHING_CONFIG.baseIntensity +
      normalized * (BREATHING_CONFIG.maxIntensity - BREATHING_CONFIG.baseIntensity);
  }, [scale, isBreathing]);

  // Dynamic border style with Living Earth amber glow
  const borderStyle = useMemo((): React.CSSProperties => {
    const glowIntensity = breathIntensity;
    const outerGlow = BREATHING_CONFIG.glowRadius * glowIntensity;
    const innerGlow = BREATHING_CONFIG.insetGlowRadius * glowIntensity;

    return {
      boxShadow: isLive
        ? `
          0 0 ${outerGlow}px ${LIVING_EARTH.amber}40,
          inset 0 0 ${innerGlow}px ${LIVING_EARTH.honey}20
        `
        : 'none',
      borderColor: isLive
        ? `rgba(212, 165, 116, ${0.3 + glowIntensity * 0.4})`
        : LIVING_EARTH.clay,
      transition: 'box-shadow 100ms ease-out, border-color 100ms ease-out',
    };
  }, [isLive, breathIntensity]);

  // Handle canvas click
  const handleClick = useCallback(
    (e: React.MouseEvent<HTMLDivElement>) => {
      if (!onCanvasClick) return;

      const rect = e.currentTarget.getBoundingClientRect();
      const x = (e.clientX - rect.left) / rect.width;
      const y = (e.clientY - rect.top) / rect.height;
      onCanvasClick({ x, y });
    },
    [onCanvasClick]
  );

  return (
    <div
      className={cn(
        'relative rounded-xl overflow-hidden',
        'bg-stone-900 border-2',
        'min-h-[300px]',
        onCanvasClick && 'cursor-pointer',
        className
      )}
      style={borderStyle}
      onClick={handleClick}
      role="region"
      aria-label={`Live creation canvas${isLive ? ' - streaming' : ''}`}
      data-session-id={sessionId}
    >
      {/* Artisan header */}
      <ArtisanHeader artisan={artisan} isLive={isLive} />

      {/* Main content area */}
      <div className="relative w-full h-full min-h-[300px]">
        <ContentRenderer
          content={content}
          contentType={contentType}
          isVisible={isLive || !!content}
        />

        {/* Spectator cursor overlay */}
        {showCursors && spectatorCursors.length > 0 && (
          <div className="absolute inset-0 pointer-events-none">
            {spectatorCursors.map((cursor) => (
              <div
                key={cursor.id}
                className="absolute w-3 h-3 rounded-full bg-amber-400/60 border border-amber-300/80"
                style={{
                  left: `${cursor.position.x * 100}%`,
                  top: `${cursor.position.y * 100}%`,
                  transform: 'translate(-50%, -50%)',
                  transition: 'left 100ms, top 100ms',
                }}
                aria-hidden="true"
              />
            ))}
          </div>
        )}
      </div>

      {/* Spectator count badge */}
      <SpectatorBadge count={spectatorCount} isLive={isLive} />
    </div>
  );
}

// =============================================================================
// Exports
// =============================================================================

export default FishbowlCanvas;
