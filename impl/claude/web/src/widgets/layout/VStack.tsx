/**
 * VStack: Vertical composition container.
 *
 * Renders children in a vertical column with configurable:
 * - gap between items
 * - optional separator between items
 *
 * When used within WidgetRenderer, uses context for recursive rendering.
 * When used directly (e.g., in tests), renders without nested widgets.
 */

import { Fragment, memo } from 'react';
import type { VStackJSON } from '@/reactive/types';
import { useWidgetRenderOptional } from '../context';

export interface VStackProps extends Omit<VStackJSON, 'type'> {
  onSelect?: (id: string) => void;
  selectedId?: string | null;
  className?: string;
}

export const VStack = memo(function VStack({
  gap,
  separator,
  children,
  onSelect,
  selectedId,
  className,
}: VStackProps) {
  const renderWidget = useWidgetRenderOptional();

  return (
    <div
      className={`kgents-vstack flex flex-col ${className || ''}`}
      style={{ gap: `${gap * 16}px` }}
    >
      {children.map((child, i) => (
        <Fragment key={i}>
          {i > 0 && separator && <div className="text-gray-400 text-center">{separator}</div>}
          {renderWidget
            ? renderWidget({ widget: child, onSelect, selectedId })
            : <span data-widget-type={child.type}>[Widget: {child.type}]</span>}
        </Fragment>
      ))}
    </div>
  );
});

export default VStack;
