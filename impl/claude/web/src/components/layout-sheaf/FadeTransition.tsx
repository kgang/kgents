/**
 * FadeTransition - Fade content in/out without layout shift.
 *
 * Use inside ReservedSlot for transient content (hover descriptions,
 * expandable sections, etc.).
 *
 * Uses simple CSS opacity transitions - tasteful and lightweight.
 *
 * @example
 * <ReservedSlot id="description">
 *   <FadeTransition show={isHovered}>
 *     {description}
 *   </FadeTransition>
 * </ReservedSlot>
 *
 * @see spec/ui/layout-sheaf.md
 */

import type { ReactNode, CSSProperties } from 'react';

export interface FadeTransitionProps {
  /** Whether to show the content */
  show: boolean;
  /** Content to render */
  children: ReactNode;
  /** Transition duration in milliseconds */
  duration?: number;
  /** Additional CSS classes */
  className?: string;
}

/**
 * Fade content in/out using CSS opacity transition.
 *
 * The content is always rendered (for stable layout), but opacity
 * transitions between 0 and 1 based on the `show` prop.
 */
export function FadeTransition({
  show,
  children,
  duration = 150,
  className = '',
}: FadeTransitionProps) {
  const style: CSSProperties = {
    opacity: show ? 1 : 0,
    transition: `opacity ${duration}ms ease-out`,
    // Prevent interaction when hidden
    pointerEvents: show ? 'auto' : 'none',
  };

  return (
    <div className={className} style={style} aria-hidden={!show}>
      {children}
    </div>
  );
}
