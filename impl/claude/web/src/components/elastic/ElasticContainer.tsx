/**
 * ElasticContainer: Self-arranging container that adapts to content.
 *
 * The fundamental building block for elastic layouts. Replaces raw div wrappers
 * with layout-aware containers that handle overflow, spacing, and empty states.
 *
 * @see plans/web-refactor/elastic-primitives.md
 */

import { forwardRef, type ReactNode } from 'react';
import { cn } from '@/lib/utils';

export type ElasticLayout = 'flow' | 'grid' | 'masonry' | 'stack-v' | 'stack-h';
export type ElasticOverflow = 'scroll' | 'wrap' | 'collapse' | 'truncate';
export type ElasticTransition = 'none' | 'fast' | 'smooth' | 'spring';
export type ElasticGap = 'xs' | 'sm' | 'md' | 'lg' | 'xl' | 'none';

export interface ElasticContainerProps {
  /** Layout strategy */
  layout?: ElasticLayout;

  /** How to handle overflow */
  overflow?: ElasticOverflow;

  /** Gap between children */
  gap?: ElasticGap;

  /** Padding around content */
  padding?: ElasticGap;

  /** What to show when empty */
  emptyState?: ReactNode;

  /** Animation config for layout changes */
  transition?: ElasticTransition;

  /** Additional class names */
  className?: string;

  /** Child elements */
  children?: ReactNode;
}

const layoutClasses: Record<ElasticLayout, string> = {
  flow: 'elastic-flow',
  grid: 'elastic-grid',
  masonry: 'elastic-masonry',
  'stack-v': 'elastic-stack-v',
  'stack-h': 'elastic-stack-h',
};

const overflowClasses: Record<ElasticOverflow, string> = {
  scroll: 'overflow-auto',
  wrap: 'flex-wrap',
  collapse: 'overflow-hidden',
  truncate: 'overflow-hidden text-ellipsis whitespace-nowrap',
};

const gapClasses: Record<ElasticGap, string> = {
  none: 'gap-0',
  xs: 'gap-1',
  sm: 'gap-2',
  md: 'gap-4',
  lg: 'gap-6',
  xl: 'gap-8',
};

const paddingClasses: Record<ElasticGap, string> = {
  none: 'p-0',
  xs: 'p-1',
  sm: 'p-2',
  md: 'p-4',
  lg: 'p-6',
  xl: 'p-8',
};

const transitionClasses: Record<ElasticTransition, string> = {
  none: '',
  fast: 'transition-all duration-150 ease-out',
  smooth: 'transition-all duration-250 ease-in-out',
  spring: 'transition-all duration-400',
};

/**
 * Checks if children are empty (null, undefined, empty array, or only whitespace)
 */
function isEmpty(children: ReactNode): boolean {
  if (children === null || children === undefined) return true;
  if (Array.isArray(children)) return children.length === 0;
  if (typeof children === 'string') return children.trim() === '';
  return false;
}

export const ElasticContainer = forwardRef<HTMLDivElement, ElasticContainerProps>(
  function ElasticContainer(
    {
      layout = 'stack-v',
      overflow = 'wrap',
      gap = 'md',
      padding = 'none',
      emptyState,
      transition = 'fast',
      className,
      children,
    },
    ref
  ) {
    const isChildrenEmpty = isEmpty(children);

    if (isChildrenEmpty && emptyState) {
      return (
        <div
          ref={ref}
          className={cn(
            paddingClasses[padding],
            transitionClasses[transition],
            'flex items-center justify-center min-h-[100px]',
            className
          )}
        >
          {emptyState}
        </div>
      );
    }

    return (
      <div
        ref={ref}
        className={cn(
          layoutClasses[layout],
          overflowClasses[overflow],
          gapClasses[gap],
          paddingClasses[padding],
          transitionClasses[transition],
          className
        )}
      >
        {children}
      </div>
    );
  }
);

export default ElasticContainer;
