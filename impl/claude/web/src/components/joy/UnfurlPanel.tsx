/**
 * UnfurlPanel - Leaf-like expanding panel component
 *
 * Implements "Unfurling" from Crown Jewels Genesis Moodboard.
 * Panels unfurl like leaves, not slide mechanically.
 *
 * @see plans/crown-jewels-genesis.md - Phase 1: Foundation
 * @see hooks/useUnfurling.ts - Animation hook
 */

import {
  type ReactNode,
  type CSSProperties,
  forwardRef,
  useEffect,
  useImperativeHandle,
} from 'react';
import {
  useUnfurling,
  type UnfurlDirection,
} from '@/hooks';
import { LIVING_EARTH, UNFURLING_ANIMATION } from '@/constants';
import { useMotionPreferences } from './useMotionPreferences';

// =============================================================================
// Types
// =============================================================================

export interface UnfurlPanelProps {
  /** Panel content */
  children: ReactNode;

  /** Whether panel is open */
  isOpen: boolean;

  /**
   * Unfurl direction.
   * Default: 'down'
   */
  direction?: UnfurlDirection;

  /**
   * Animation duration in ms.
   * Default: 300
   */
  duration?: number;

  /**
   * Delay before content fades in (0-1 of unfurl progress).
   * Default: 0.3
   */
  contentFadeDelay?: number;

  /**
   * Show organic border with gradient.
   * Default: false
   */
  organicBorder?: boolean;

  /**
   * Border/accent color.
   * Default: LIVING_EARTH.sage
   */
  accentColor?: string;

  /**
   * Callback when unfurl animation completes.
   */
  onUnfurled?: () => void;

  /**
   * Callback when fold animation completes.
   */
  onFolded?: () => void;

  /** Additional CSS class for outer container */
  className?: string;

  /** Additional CSS class for inner content */
  contentClassName?: string;

  /** Additional styles for outer container */
  style?: CSSProperties;

  /** Additional styles for inner content */
  contentStyle?: CSSProperties;

  /** ARIA label for accessibility */
  'aria-label'?: string;
}

export interface UnfurlPanelRef {
  /** Manually trigger unfurl */
  unfurl: () => void;
  /** Manually trigger fold */
  fold: () => void;
  /** Toggle state */
  toggle: () => void;
  /** Current open state */
  isOpen: boolean;
  /** Current animation progress (0-1) */
  progress: number;
}

// =============================================================================
// Component
// =============================================================================

/**
 * UnfurlPanel
 *
 * An expanding panel with organic leaf-like animation.
 * Use for collapsible sections, drawers, and revealed content.
 *
 * @example Basic collapsible:
 * ```tsx
 * function CollapsibleSection({ title, children }) {
 *   const [isOpen, setIsOpen] = useState(false);
 *
 *   return (
 *     <div>
 *       <button onClick={() => setIsOpen(!isOpen)}>
 *         {title}
 *       </button>
 *       <UnfurlPanel isOpen={isOpen}>
 *         {children}
 *       </UnfurlPanel>
 *     </div>
 *   );
 * }
 * ```
 *
 * @example Radial reveal:
 * ```tsx
 * <UnfurlPanel
 *   isOpen={showModal}
 *   direction="radial"
 *   duration={400}
 *   organicBorder
 *   accentColor="#D4A574"
 * >
 *   <ModalContent />
 * </UnfurlPanel>
 * ```
 *
 * @example With ref control:
 * ```tsx
 * const panelRef = useRef<UnfurlPanelRef>(null);
 *
 * <UnfurlPanel ref={panelRef} isOpen={false}>
 *   Content
 * </UnfurlPanel>
 *
 * // Later: panelRef.current?.unfurl();
 * ```
 */
export const UnfurlPanel = forwardRef<UnfurlPanelRef, UnfurlPanelProps>(
  function UnfurlPanel(
    {
      children,
      isOpen,
      direction = 'down',
      duration = UNFURLING_ANIMATION.duration,
      contentFadeDelay = 0.3,
      organicBorder = false,
      accentColor = LIVING_EARTH.sage,
      onUnfurled,
      onFolded,
      className = '',
      contentClassName = '',
      style,
      contentStyle,
      'aria-label': ariaLabel,
    },
    ref
  ) {
    const { shouldAnimate } = useMotionPreferences();

    const {
      progress,
      isAnimating,
      isOpen: hookIsOpen,
      unfurl,
      fold,
      toggle,
      style: unfurlStyle,
      contentStyle: unfurlContentStyle,
    } = useUnfurling({
      enabled: shouldAnimate,
      duration,
      direction,
      contentFadeDelay,
      initialOpen: isOpen,
      respectReducedMotion: true,
      onUnfurled,
      onFolded,
    });

    // Sync with controlled isOpen prop
    useEffect(() => {
      if (isOpen && !hookIsOpen) {
        unfurl();
      } else if (!isOpen && hookIsOpen) {
        fold();
      }
    }, [isOpen, hookIsOpen, unfurl, fold]);

    // Expose ref methods
    useImperativeHandle(
      ref,
      () => ({
        unfurl,
        fold,
        toggle,
        isOpen: hookIsOpen,
        progress,
      }),
      [unfurl, fold, toggle, hookIsOpen, progress]
    );

    // If reduced motion, show/hide immediately
    if (!shouldAnimate) {
      if (!isOpen) {
        return null;
      }
      return (
        <div
          className={`${className}`}
          style={style}
          role="region"
          aria-label={ariaLabel}
          aria-expanded={isOpen}
        >
          <div className={contentClassName} style={contentStyle}>
            {children}
          </div>
        </div>
      );
    }

    // Don't render if fully closed and not animating
    if (progress === 0 && !isAnimating && !isOpen) {
      return null;
    }

    return (
      <div
        className={`overflow-hidden ${className}`}
        style={{
          ...unfurlStyle,
          ...style,
        }}
        role="region"
        aria-label={ariaLabel}
        aria-expanded={hookIsOpen}
        data-unfurl-direction={direction}
        data-unfurl-progress={progress.toFixed(2)}
      >
        {/* Organic border (decorative) */}
        {organicBorder && (
          <div
            className="absolute inset-0 pointer-events-none rounded-inherit"
            style={{
              borderRadius: 'inherit',
              border: `1px solid ${accentColor}`,
              opacity: progress * 0.6,
              transition: 'opacity 0.15s ease-out',
            }}
          />
        )}

        {/* Content with fade delay */}
        <div
          className={contentClassName}
          style={{
            ...unfurlContentStyle,
            ...contentStyle,
          }}
        >
          {children}
        </div>

        {/* Leaf vein decoration for organic feel */}
        {organicBorder && direction !== 'radial' && (
          <LeafVeinDecoration
            direction={direction}
            progress={progress}
            color={accentColor}
          />
        )}
      </div>
    );
  }
);

// =============================================================================
// Decorative Elements
// =============================================================================

interface LeafVeinDecorationProps {
  direction: UnfurlDirection;
  progress: number;
  color: string;
}

/**
 * Subtle leaf vein pattern that reveals with unfurl
 */
function LeafVeinDecoration({ direction, progress, color }: LeafVeinDecorationProps) {
  const isVertical = direction === 'down' || direction === 'up';

  return (
    <svg
      className="absolute pointer-events-none"
      style={{
        [direction === 'down' ? 'top' : direction === 'up' ? 'bottom' : 'left']: 0,
        [isVertical ? 'left' : 'top']: '50%',
        transform: isVertical ? 'translateX(-50%)' : 'translateY(-50%)',
        width: isVertical ? 40 : 'auto',
        height: isVertical ? 'auto' : 40,
        opacity: progress * 0.15,
      }}
      viewBox="0 0 40 60"
      fill="none"
    >
      {/* Central vein */}
      <path
        d="M20 0 L20 60"
        stroke={color}
        strokeWidth="1"
        strokeDasharray={`${progress * 60} 60`}
      />
      {/* Side veins */}
      <path
        d="M20 15 L8 25 M20 30 L10 40 M20 45 L12 52"
        stroke={color}
        strokeWidth="0.5"
        strokeDasharray={`${progress * 20} 20`}
        opacity={Math.max(0, progress - 0.3)}
      />
      <path
        d="M20 15 L32 25 M20 30 L30 40 M20 45 L28 52"
        stroke={color}
        strokeWidth="0.5"
        strokeDasharray={`${progress * 20} 20`}
        opacity={Math.max(0, progress - 0.3)}
      />
    </svg>
  );
}

// =============================================================================
// Specialized Variants
// =============================================================================

/**
 * UnfurlDrawer - Side drawer with horizontal unfurl
 */
export function UnfurlDrawer({
  children,
  isOpen,
  side = 'right',
  className = '',
  ...props
}: Omit<UnfurlPanelProps, 'direction'> & { side?: 'left' | 'right' }) {
  return (
    <UnfurlPanel
      isOpen={isOpen}
      direction={side === 'right' ? 'left' : 'right'}
      className={`fixed top-0 bottom-0 ${side}-0 w-80 bg-surface-card shadow-xl ${className}`}
      organicBorder
      duration={350}
      {...props}
    >
      {children}
    </UnfurlPanel>
  );
}

/**
 * UnfurlAccordion - Accordion section with down unfurl
 */
export function UnfurlAccordion({
  title,
  children,
  isOpen,
  onToggle,
  className = '',
  ...props
}: Omit<UnfurlPanelProps, 'direction'> & {
  title: ReactNode;
  onToggle?: () => void;
}) {
  return (
    <div className={className}>
      <button
        className="w-full flex items-center justify-between p-3 text-left hover:bg-white/5 transition-colors"
        onClick={onToggle}
        aria-expanded={isOpen}
      >
        <span style={{ color: LIVING_EARTH.lantern }}>{title}</span>
        <svg
          className="w-4 h-4 transition-transform"
          style={{
            color: LIVING_EARTH.clay,
            transform: isOpen ? 'rotate(180deg)' : 'rotate(0deg)',
          }}
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M19 9l-7 7-7-7"
          />
        </svg>
      </button>
      <UnfurlPanel isOpen={isOpen} direction="down" {...props}>
        <div className="p-3 pt-0">{children}</div>
      </UnfurlPanel>
    </div>
  );
}

/**
 * UnfurlModal - Radial reveal modal
 */
export function UnfurlModal({
  children,
  isOpen,
  onClose,
  className = '',
  ...props
}: Omit<UnfurlPanelProps, 'direction'> & { onClose?: () => void }) {
  return (
    <>
      {/* Backdrop */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-40"
          onClick={onClose}
          style={{
            opacity: isOpen ? 1 : 0,
            transition: 'opacity 0.2s ease-out',
          }}
        />
      )}

      {/* Modal */}
      <div
        className="fixed inset-0 flex items-center justify-center pointer-events-none z-50"
      >
        <UnfurlPanel
          isOpen={isOpen}
          direction="radial"
          duration={400}
          organicBorder
          accentColor={LIVING_EARTH.amber}
          className={`pointer-events-auto rounded-xl p-6 shadow-2xl ${className}`}
          style={{ background: LIVING_EARTH.bark }}
          {...props}
        >
          {children}
        </UnfurlPanel>
      </div>
    </>
  );
}

// =============================================================================
// Default Export
// =============================================================================

export default UnfurlPanel;
