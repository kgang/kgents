/**
 * HStack: Horizontal composition container.
 *
 * Renders children in a horizontal row with configurable:
 * - gap between items
 * - optional separator between items
 *
 * When used within WidgetRenderer, uses context for recursive rendering.
 * When used directly (e.g., in tests), renders without nested widgets.
 */

import { Fragment, memo } from 'react';
import type { HStackJSON } from '@/reactive/types';
import { useWidgetRenderOptional } from '../context';

export interface HStackProps extends Omit<HStackJSON, 'type'> {
  onSelect?: (id: string) => void;
  selectedId?: string | null;
  className?: string;
}

export const HStack = memo(function HStack({
  gap,
  separator,
  children,
  onSelect,
  selectedId,
  className,
}: HStackProps) {
  const renderWidget = useWidgetRenderOptional();

  return (
    <div
      className={`kgents-hstack flex items-center ${className || ''}`}
      style={{ gap: `${gap * 8}px` }}
    >
      {children.map((child, i) => (
        <Fragment key={i}>
          {i > 0 && separator && <span className="text-gray-400">{separator}</span>}
          {renderWidget
            ? renderWidget({ widget: child, onSelect, selectedId })
            : <span data-widget-type={child.type}>[Widget: {child.type}]</span>}
        </Fragment>
      ))}
    </div>
  );
});

export default HStack;
