/**
 * FloatingSidebar: Floating overlay sidebar with collapsible behavior.
 *
 * Key Principles:
 * - **Overlay > Push**: Floats over content, preserving full content width
 * - **Transform > Reflow**: Uses translate-x for smooth animation
 * - **Toggle Follows Panel**: Expand button slides with sidebar
 * - **Sheaf Condition**: Bottom offset respects sibling panels via context
 *
 * Physical constraints enforced:
 * - Toggle button touch target: 48px minimum
 * - Glass effect: 82.5% opacity with backdrop blur
 *
 * @see docs/skills/elastic-ui-patterns.md (Floating Overlay Pattern)
 */

import { type ReactNode, type CSSProperties } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronRight, X } from 'lucide-react';
import {
  GLASS_EFFECT,
  Z_INDEX_LAYERS,
  SIDEBAR_WIDTHS,
  PHYSICAL_CONSTRAINTS,
  type GlassVariant,
  type Density,
} from './types';

export interface FloatingSidebarProps {
  /** Whether the sidebar is expanded */
  isExpanded: boolean;

  /** Callback to toggle expansion */
  onToggle: () => void;

  /** Sidebar content */
  children: ReactNode;

  /** Sidebar width in pixels */
  width?: number;

  /** Bottom offset to respect sibling panels (sheaf condition) */
  bottomOffset?: string | number;

  /** Top offset (e.g., for header) */
  topOffset?: string | number;

  /** Glass effect variant */
  glass?: GlassVariant;

  /** Current density for responsive behavior */
  density?: Density;

  /** Whether to animate transitions */
  animate?: boolean;

  /** Custom class name */
  className?: string;

  /** Accessible label */
  ariaLabel?: string;

  /** Header content (optional) */
  header?: ReactNode;

  /** Show close button in header */
  showCloseButton?: boolean;
}

/**
 * FloatingSidebar component for overlay navigation panels.
 *
 * Usage:
 * ```tsx
 * const { terminalExpanded } = useShell();
 * const bottomOffset = terminalExpanded ? '200px' : '48px';
 *
 * <FloatingSidebar
 *   isExpanded={navExpanded}
 *   onToggle={() => setNavExpanded(!navExpanded)}
 *   bottomOffset={bottomOffset}
 *   header={<h2>Navigation</h2>}
 * >
 *   <NavTree />
 * </FloatingSidebar>
 * ```
 */
export function FloatingSidebar({
  isExpanded,
  onToggle,
  children,
  width,
  bottomOffset = 0,
  topOffset = 0,
  glass = 'standard',
  density = 'spacious',
  animate = true,
  className = '',
  ariaLabel = 'Sidebar',
  header,
  showCloseButton = true,
}: FloatingSidebarProps) {
  // Get effective width based on density
  const effectiveWidth = width ?? (density === 'spacious' ? SIDEBAR_WIDTHS.full : SIDEBAR_WIDTHS.compact);

  // Get glass effect styles
  const glassStyles = GLASS_EFFECT[glass];

  // Animation duration
  const duration = animate ? 0.25 : 0;

  // Convert offsets to CSS values
  const topCss = typeof topOffset === 'number' ? `${topOffset}px` : topOffset;
  const bottomCss = typeof bottomOffset === 'number' ? `${bottomOffset}px` : bottomOffset;

  const sidebarStyle: CSSProperties = {
    width: effectiveWidth,
    top: topCss,
    bottom: bottomCss,
  };

  const toggleStyle: CSSProperties = {
    minWidth: PHYSICAL_CONSTRAINTS.minTouchTarget,
    minHeight: PHYSICAL_CONSTRAINTS.minTouchTarget,
  };

  return (
    <>
      {/* Toggle button - always visible, slides with sidebar */}
      <button
        onClick={onToggle}
        className={`
          fixed left-0 top-1/2 -translate-y-1/2
          p-2 ${glassStyles.background} ${glassStyles.blur}
          rounded-r-lg border border-l-0 border-gray-700/50
          hover:bg-gray-700 transition-all duration-200
        `}
        style={{
          ...toggleStyle,
          zIndex: Z_INDEX_LAYERS.toggle,
          transform: `translateY(-50%) translateX(${isExpanded ? effectiveWidth : 0}px)`,
          transition: animate ? 'transform 0.25s ease' : 'none',
        }}
        aria-label={isExpanded ? `Close ${ariaLabel}` : `Open ${ariaLabel}`}
        aria-expanded={isExpanded}
      >
        <motion.span
          animate={{ rotate: isExpanded ? 180 : 0 }}
          transition={{ duration }}
          className="block"
        >
          <ChevronRight className="w-4 h-4 text-gray-400" />
        </motion.span>
      </button>

      {/* Floating sidebar panel */}
      <AnimatePresence>
        {isExpanded && (
          <motion.aside
            initial={{ x: -effectiveWidth, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            exit={{ x: -effectiveWidth, opacity: 0 }}
            transition={{ duration, ease: [0.4, 0, 0.2, 1] }}
            style={{ ...sidebarStyle, zIndex: Z_INDEX_LAYERS.panel }}
            className={`
              fixed left-0
              ${glassStyles.background} ${glassStyles.blur}
              border-r border-gray-700/50
              overflow-y-auto shadow-xl
              ${className}
            `}
            role="complementary"
            aria-label={ariaLabel}
          >
            {/* Header with optional close button */}
            {(header || showCloseButton) && (
              <div className={`
                sticky top-0 ${glassStyles.background} ${glassStyles.blur}
                border-b border-gray-700/50 px-3 py-2
                flex items-center justify-between
              `}>
                {header && <div className="flex-1">{header}</div>}
                {showCloseButton && (
                  <button
                    onClick={onToggle}
                    className="p-1 hover:bg-gray-700 rounded transition-colors"
                    style={toggleStyle}
                    aria-label={`Close ${ariaLabel}`}
                  >
                    <X className="w-4 h-4 text-gray-400" />
                  </button>
                )}
              </div>
            )}

            {/* Content */}
            <div className="p-3">
              {children}
            </div>
          </motion.aside>
        )}
      </AnimatePresence>
    </>
  );
}

export default FloatingSidebar;
