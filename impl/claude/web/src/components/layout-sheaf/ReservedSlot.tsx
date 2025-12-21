/**
 * ReservedSlot - A layout region with reserved space managed by Layout Sheaf.
 *
 * Children can appear/disappear without causing layout shift because the
 * slot height is pre-reserved via claims.
 *
 * @example
 * <ReservedSlot id="description" className="text-gray-400">
 *   {isHovered && <Description text={desc} />}
 * </ReservedSlot>
 *
 * @see spec/ui/layout-sheaf.md
 */

import { useEffect, type ReactNode, type CSSProperties } from 'react';
import { useLayoutSheafOptional } from './LayoutSheafContext';
import type { LayoutSlot } from './types';

export interface ReservedSlotProps {
  /** Unique slot identifier */
  id: string;
  /** Optional constraints for the slot */
  constraints?: LayoutSlot['constraints'];
  /** Additional CSS classes */
  className?: string;
  /** Inline styles (merged with sheaf styles) */
  style?: React.CSSProperties;
  /** Content to render */
  children?: ReactNode;
  /** Fallback when no children */
  fallback?: ReactNode;
  /** data-testid for testing */
  testId?: string;
}

/**
 * A layout region with reserved space managed by LayoutSheaf.
 *
 * The slot renders with stable dimensions regardless of whether
 * children are present or absent. Use with FadeTransition for
 * smooth content appearance.
 */
export function ReservedSlot({
  id,
  constraints,
  className = '',
  style,
  children,
  fallback,
  testId,
}: ReservedSlotProps) {
  const sheaf = useLayoutSheafOptional();

  // Register slot with constraints on mount
  useEffect(() => {
    if (sheaf && constraints) {
      sheaf.registerSlot({ id, constraints, priority: 0 });
      return () => sheaf.unregisterSlot(id);
    }
  }, [sheaf, id, constraints]);

  // Get resolved style from sheaf (or empty if no provider)
  const slotStyle = sheaf?.getSlotStyle(id) ?? {};

  const combinedStyle: CSSProperties = {
    ...slotStyle,
    ...style,
    overflow: 'hidden',
  };

  return (
    <div
      className={className}
      style={combinedStyle}
      data-testid={testId ?? `slot-${id}`}
      data-slot-id={id}
    >
      {children ?? fallback}
    </div>
  );
}
