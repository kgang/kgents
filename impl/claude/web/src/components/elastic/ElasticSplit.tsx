/**
 * ElasticSplit: Two-pane responsive layout with draggable divider.
 *
 * Features:
 * - Horizontal or vertical split
 * - Draggable divider for ratio adjustment
 * - Responsive collapse based on DESIGN_POLYNOMIAL density
 * - Priority-based collapse (primary or secondary first)
 *
 * Uses useDesignPolynomial for density-aware collapse behavior.
 * At 'compact' density, the split collapses to a stacked layout.
 *
 * @see plans/web-refactor/elastic-primitives.md
 * @see plans/design-language-consolidation.md
 */

import {
  useState,
  useRef,
  useCallback,
  useEffect,
  type ReactNode,
  type CSSProperties,
  type MouseEvent as ReactMouseEvent,
} from 'react';
import { useDesignPolynomial, type Density } from '@/hooks/useDesignPolynomial';

export interface ElasticSplitProps {
  /** Split direction */
  direction?: 'horizontal' | 'vertical';

  /** Initial split ratio (0-1, where 0.5 = 50/50) */
  defaultRatio?: number;

  /**
   * Density at which to collapse to stacked layout.
   * - 'compact': Collapse only at mobile widths (default)
   * - 'comfortable': Collapse at tablet and mobile
   * - 'spacious': Never collapse (always split)
   * @default 'compact'
   */
  collapseAtDensity?: Density;

  /**
   * @deprecated Use collapseAtDensity instead. Kept for backward compatibility.
   * Below this width (px), stack instead of split.
   */
  collapseAt?: number;

  /** Which pane collapses first */
  collapsePriority?: 'primary' | 'secondary';

  /** Primary pane content */
  primary: ReactNode;

  /** Secondary pane content */
  secondary: ReactNode;

  /** Whether the divider is draggable */
  resizable?: boolean;

  /** Minimum pane size in pixels */
  minPaneSize?: number;

  /** Custom class name */
  className?: string;

  /** Custom styles */
  style?: CSSProperties;

  /** Callback when ratio changes */
  onRatioChange?: (ratio: number) => void;
}

export function ElasticSplit({
  direction = 'horizontal',
  defaultRatio = 0.5,
  collapseAtDensity = 'compact',
  collapseAt: _collapseAt, // Deprecated, kept for backward compatibility
  collapsePriority = 'secondary',
  primary,
  secondary,
  resizable = true,
  minPaneSize = 100,
  className = '',
  style,
  onRatioChange,
}: ElasticSplitProps) {
  // Use the design polynomial for density-aware behavior
  const { state: designState } = useDesignPolynomial();
  const containerRef = useRef<HTMLDivElement>(null);
  const [ratio, setRatio] = useState(defaultRatio);
  const [isDragging, setIsDragging] = useState(false);

  // Determine if we should collapse based on density
  // Density order: compact < comfortable < spacious
  const densityOrder: Density[] = ['compact', 'comfortable', 'spacious'];
  const currentDensityIndex = densityOrder.indexOf(designState.density);
  const collapseDensityIndex = densityOrder.indexOf(collapseAtDensity);

  // Collapse if current density is at or below the collapse threshold
  // E.g., collapseAtDensity='compact' means only collapse at compact
  //       collapseAtDensity='comfortable' means collapse at compact AND comfortable
  const isCollapsed = currentDensityIndex <= collapseDensityIndex;

  // Handle drag start
  const handleDragStart = useCallback((e: ReactMouseEvent) => {
    if (!resizable) return;
    e.preventDefault();
    setIsDragging(true);
  }, [resizable]);

  // Handle drag
  useEffect(() => {
    if (!isDragging) return;

    const handleMouseMove = (e: MouseEvent) => {
      if (!containerRef.current) return;

      const rect = containerRef.current.getBoundingClientRect();
      let newRatio: number;

      if (direction === 'horizontal') {
        const x = e.clientX - rect.left;
        newRatio = x / rect.width;
      } else {
        const y = e.clientY - rect.top;
        newRatio = y / rect.height;
      }

      // Clamp ratio to ensure minimum pane sizes
      const minRatio = minPaneSize / (direction === 'horizontal' ? rect.width : rect.height);
      const maxRatio = 1 - minRatio;
      newRatio = Math.max(minRatio, Math.min(maxRatio, newRatio));

      setRatio(newRatio);
      onRatioChange?.(newRatio);
    };

    const handleMouseUp = () => {
      setIsDragging(false);
    };

    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseup', handleMouseUp);

    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };
  }, [isDragging, direction, minPaneSize, onRatioChange]);

  // Collapsed layout: stack panes
  if (isCollapsed) {
    const first = collapsePriority === 'secondary' ? primary : secondary;
    const second = collapsePriority === 'secondary' ? secondary : primary;

    return (
      <div
        ref={containerRef}
        className={`flex flex-col gap-4 ${className}`}
        style={style}
        data-collapsed="true"
        data-density={designState.density}
        data-collapse-reason={`density=${designState.density} <= ${collapseAtDensity}`}
      >
        <div className="flex-1">{first}</div>
        <div className="flex-1">{second}</div>
      </div>
    );
  }

  // Split layout
  const isHorizontal = direction === 'horizontal';
  const primarySize = `${ratio * 100}%`;
  const secondarySize = `${(1 - ratio) * 100}%`;

  const containerStyles: CSSProperties = {
    display: 'flex',
    flexDirection: isHorizontal ? 'row' : 'column',
    height: '100%',
    width: '100%',
    userSelect: isDragging ? 'none' : undefined,
    ...style,
  };

  const dividerStyles: CSSProperties = {
    flexShrink: 0,
    width: isHorizontal ? '4px' : '100%',
    height: isHorizontal ? '100%' : '4px',
    backgroundColor: 'rgba(100, 100, 120, 0.3)',
    cursor: resizable ? (isHorizontal ? 'col-resize' : 'row-resize') : 'default',
    transition: isDragging ? 'none' : 'background-color var(--elastic-transition-fast)',
  };

  const dividerActiveStyles: CSSProperties = isDragging
    ? {
        backgroundColor: 'rgba(233, 69, 96, 0.5)',
      }
    : {};

  return (
    <div
      ref={containerRef}
      className={className}
      style={containerStyles}
      data-direction={direction}
      data-dragging={isDragging}
      data-density={designState.density}
      data-collapsed="false"
    >
      {/* Primary pane */}
      <div
        className="overflow-auto"
        style={{
          [isHorizontal ? 'width' : 'height']: primarySize,
          minWidth: isHorizontal ? minPaneSize : undefined,
          minHeight: !isHorizontal ? minPaneSize : undefined,
        }}
      >
        {primary}
      </div>

      {/* Divider */}
      <div
        className={`hover:bg-town-accent/50 ${resizable ? 'active:bg-town-highlight/50' : ''}`}
        style={{ ...dividerStyles, ...dividerActiveStyles }}
        onMouseDown={handleDragStart}
        role={resizable ? 'separator' : undefined}
        aria-orientation={isHorizontal ? 'vertical' : 'horizontal'}
        aria-valuenow={Math.round(ratio * 100)}
        aria-valuemin={0}
        aria-valuemax={100}
      />

      {/* Secondary pane */}
      <div
        className="overflow-auto"
        style={{
          [isHorizontal ? 'width' : 'height']: secondarySize,
          minWidth: isHorizontal ? minPaneSize : undefined,
          minHeight: !isHorizontal ? minPaneSize : undefined,
        }}
      >
        {secondary}
      </div>
    </div>
  );
}

export default ElasticSplit;
