/**
 * UnfurlingPanel
 *
 * Leaf-like expansion for panels and modals.
 * Implements "Unfurling" from Crown Jewels Genesis Moodboard.
 *
 * @see plans/crown-jewels-genesis.md - Phase 1: Foundation
 * @see hooks/useUnfurling.ts
 */

import React, { useEffect } from 'react';
import { useUnfurling, type UnfurlingOptions, type UnfurlDirection } from '@/hooks/useUnfurling';

// =============================================================================
// Types
// =============================================================================

export interface UnfurlingPanelProps {
  /**
   * Panel is open/visible.
   * When true, panel unfurls. When false, panel folds.
   */
  isOpen: boolean;

  /**
   * Direction of unfurl.
   * - down: Unfurl downward from top (dropdown menus, accordions)
   * - up: Unfurl upward from bottom (bottom sheets)
   * - left: Unfurl leftward from right (side panels from right)
   * - right: Unfurl rightward from left (side panels from left)
   * - radial: Expand from center (modals, overlays)
   *
   * Default: 'down'
   */
  direction?: UnfurlDirection;

  /**
   * Duration of transition in ms.
   * Default: 300
   */
  duration?: number;

  /**
   * Delay before content fades in (0-1).
   * 0 = content visible immediately.
   * 0.3 = content fades in at 30% unfurl progress.
   * 1 = content fades in only when fully unfurled.
   *
   * Default: 0.3
   */
  contentFadeDelay?: number;

  /**
   * Callback when panel is fully unfurled.
   */
  onUnfurled?: () => void;

  /**
   * Callback when panel is fully folded.
   */
  onFolded?: () => void;

  /**
   * Additional className for the container.
   */
  className?: string;

  /**
   * Additional inline styles for the container.
   */
  style?: React.CSSProperties;

  /**
   * Additional className for the content wrapper.
   */
  contentClassName?: string;

  /**
   * Panel content.
   */
  children: React.ReactNode;
}

// =============================================================================
// Component
// =============================================================================

/**
 * UnfurlingPanel
 *
 * Panel that unfurls like a leaf with clip-path animation.
 *
 * @example Dropdown panel:
 * ```tsx
 * function Dropdown({ isVisible, children }) {
 *   return (
 *     <UnfurlingPanel isOpen={isVisible} direction="down">
 *       {children}
 *     </UnfurlingPanel>
 *   );
 * }
 * ```
 *
 * @example Radial modal:
 * ```tsx
 * <UnfurlingPanel
 *   isOpen={showModal}
 *   direction="radial"
 *   duration={400}
 *   onFolded={() => setShowModal(false)}
 * >
 *   <ModalContent />
 * </UnfurlingPanel>
 * ```
 *
 * @example Side panel from right:
 * ```tsx
 * <UnfurlingPanel
 *   isOpen={showDetails}
 *   direction="left"
 *   contentFadeDelay={0.2}
 * >
 *   <DetailsSidebar />
 * </UnfurlingPanel>
 * ```
 */
export function UnfurlingPanel({
  isOpen,
  direction = 'down',
  duration,
  contentFadeDelay = 0.3,
  onUnfurled,
  onFolded,
  className,
  style: customStyle,
  contentClassName,
  children,
}: UnfurlingPanelProps) {
  // Get unfurling animation state
  const unfurlingOptions: UnfurlingOptions = {
    direction,
    duration,
    contentFadeDelay,
    onUnfurled,
    onFolded,
  };

  const {
    unfurl,
    fold,
    style: unfurlingStyle,
    contentStyle,
  } = useUnfurling(unfurlingOptions);

  // Sync isOpen prop with unfurl/fold actions
  useEffect(() => {
    if (isOpen) {
      unfurl();
    } else {
      fold();
    }
  }, [isOpen, unfurl, fold]);

  // Merge custom styles with unfurling styles
  const mergedStyle: React.CSSProperties = {
    ...unfurlingStyle,
    ...customStyle,
  };

  return (
    <div className={className} style={mergedStyle}>
      <div className={contentClassName} style={contentStyle}>
        {children}
      </div>
    </div>
  );
}

// =============================================================================
// Display Name
// =============================================================================

UnfurlingPanel.displayName = 'UnfurlingPanel';

// =============================================================================
// Default Export
// =============================================================================

export default UnfurlingPanel;
