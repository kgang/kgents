/**
 * ElasticContainer: Self-arranging container with layout strategies.
 *
 * The fundamental building block for elastic layouts. Replaces raw div wrappers
 * with a container that provides layout context to its children.
 *
 * @see plans/web-refactor/elastic-primitives.md
 */

import React, { useMemo, type ReactNode, type CSSProperties } from 'react';
import {
  useLayoutMeasure,
  LayoutContextProvider as LayoutContextReact,
} from '@/hooks/useLayoutContext';
import type { LayoutContext } from '@/reactive/types';

export type LayoutStrategy = 'flow' | 'grid' | 'masonry' | 'stack';
export type OverflowBehavior = 'scroll' | 'wrap' | 'collapse' | 'truncate';
export type TransitionStyle = 'none' | 'fast' | 'smooth' | 'spring';

export interface ResponsiveValue<T> {
  sm?: T;
  md?: T;
  lg?: T;
}

export interface ElasticContainerProps {
  /** Layout strategy */
  layout?: LayoutStrategy;

  /** How to handle overflow */
  overflow?: OverflowBehavior;

  /** Gap between children (CSS value or responsive object) */
  gap?: string | ResponsiveValue<string>;

  /** Padding (CSS value or responsive object) */
  padding?: string | ResponsiveValue<string>;

  /** What to show when empty */
  emptyState?: ReactNode;

  /** Animation config */
  transition?: TransitionStyle;

  /** Stack direction when layout='stack' */
  direction?: 'horizontal' | 'vertical';

  /** Minimum item width for grid layout */
  minItemWidth?: number;

  /** Custom class name */
  className?: string;

  /** Custom styles */
  style?: CSSProperties;

  /** Accessibility role */
  role?: string;

  /** Children */
  children: ReactNode;
}

/**
 * Get CSS class for layout strategy
 */
function getLayoutClass(layout: LayoutStrategy, direction: 'horizontal' | 'vertical'): string {
  switch (layout) {
    case 'flow':
      return 'elastic-flow';
    case 'grid':
      return 'elastic-grid';
    case 'masonry':
      return 'elastic-masonry';
    case 'stack':
      return direction === 'horizontal' ? 'elastic-stack-h' : 'elastic-stack-v';
    default:
      return '';
  }
}

/**
 * Get transition CSS variable
 */
function getTransitionVar(transition: TransitionStyle): string {
  switch (transition) {
    case 'fast':
      return 'var(--elastic-transition-fast)';
    case 'smooth':
      return 'var(--elastic-transition-smooth)';
    case 'spring':
      return 'var(--elastic-transition-spring)';
    default:
      return 'none';
  }
}

/**
 * Resolve responsive value based on width
 */
function resolveResponsive<T>(
  value: T | ResponsiveValue<T> | undefined,
  width: number,
  defaultValue: T
): T {
  if (value === undefined) return defaultValue;
  if (typeof value !== 'object' || value === null) return value as T;

  const responsive = value as ResponsiveValue<T>;

  // Apply based on breakpoints (mobile-first)
  if (width >= 1024 && responsive.lg !== undefined) return responsive.lg;
  if (width >= 768 && responsive.md !== undefined) return responsive.md;
  if (responsive.sm !== undefined) return responsive.sm;

  return defaultValue;
}

/**
 * Count valid React children
 */
function countChildren(children: ReactNode): number {
  let count = 0;
  React.Children.forEach(children, (child) => {
    if (React.isValidElement(child)) count++;
  });
  return count;
}

export function ElasticContainer({
  layout = 'stack',
  overflow = 'wrap',
  gap,
  padding,
  emptyState,
  transition = 'smooth',
  direction = 'vertical',
  minItemWidth = 200,
  className = '',
  style,
  role,
  children,
}: ElasticContainerProps) {
  const [containerRef, context] = useLayoutMeasure({
    parentLayout: layout,
  });

  // Resolve responsive values
  const resolvedGap = resolveResponsive(gap, context.availableWidth, 'var(--elastic-gap-md)');
  const resolvedPadding = resolveResponsive(
    padding,
    context.availableWidth,
    'var(--elastic-gap-md)'
  );

  // Build inline styles
  const containerStyle = useMemo((): CSSProperties => {
    const baseStyles: CSSProperties = {
      gap: resolvedGap,
      padding: resolvedPadding,
      transition: getTransitionVar(transition),
      ...style,
    };

    // Grid-specific: set column template
    if (layout === 'grid') {
      baseStyles.gridTemplateColumns = `repeat(auto-fit, minmax(${minItemWidth}px, 1fr))`;
    }

    // Overflow handling
    if (overflow === 'scroll') {
      baseStyles.overflowX = 'auto';
      baseStyles.overflowY = 'auto';
    } else if (overflow === 'truncate') {
      baseStyles.overflow = 'hidden';
    }

    return baseStyles;
  }, [resolvedGap, resolvedPadding, transition, style, layout, minItemWidth, overflow]);

  const layoutClass = getLayoutClass(layout, direction);
  const childCount = countChildren(children);

  // Show empty state if no children
  if (childCount === 0 && emptyState) {
    return (
      <div
        ref={containerRef as React.RefObject<HTMLDivElement>}
        className={`${layoutClass} ${className}`.trim()}
        style={style}
      >
        <div className="empty-state">{emptyState}</div>
      </div>
    );
  }

  return (
    <LayoutContextReact.Provider value={context}>
      <div
        ref={containerRef as React.RefObject<HTMLDivElement>}
        className={`${layoutClass} ${className}`.trim()}
        style={containerStyle}
        role={role}
      >
        {children}
      </div>
    </LayoutContextReact.Provider>
  );
}

/**
 * Export context provider for custom layouts
 */
export const LayoutContextProvider = LayoutContextReact.Provider;
export type { LayoutContext };

export default ElasticContainer;
