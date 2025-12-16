/**
 * ElasticSplit: Two-pane layout that collapses gracefully.
 *
 * A responsive split view that adapts to screen size. Below a threshold,
 * it stacks vertically with one pane collapsible.
 *
 * @see plans/web-refactor/elastic-primitives.md
 */

import { useState, type ReactNode } from 'react';
import { cn } from '@/lib/utils';

export type SplitDirection = 'horizontal' | 'vertical';
export type CollapsePriority = 'primary' | 'secondary';

export interface ElasticSplitProps {
  /** Split direction */
  direction?: SplitDirection;

  /** Initial split ratio (0-1, where 0.5 is 50/50) */
  defaultRatio?: number;

  /** Below this width (px), stack instead of split */
  collapseAt?: number;

  /** Which pane collapses first when stacking */
  collapsePriority?: CollapsePriority;

  /** Whether the collapsible pane is currently collapsed (mobile) */
  collapsed?: boolean;

  /** Callback when collapsed state changes */
  onCollapsedChange?: (collapsed: boolean) => void;

  /** Primary pane content */
  primary: ReactNode;

  /** Secondary pane content */
  secondary: ReactNode;

  /** Additional class names */
  className?: string;
}

export function ElasticSplit({
  direction = 'horizontal',
  defaultRatio = 0.7,
  collapseAt = 768,
  collapsePriority = 'secondary',
  collapsed = false,
  onCollapsedChange,
  primary,
  secondary,
  className,
}: ElasticSplitProps) {
  const [isCollapsed, setIsCollapsed] = useState(collapsed);

  const handleToggleCollapse = () => {
    const newCollapsed = !isCollapsed;
    setIsCollapsed(newCollapsed);
    onCollapsedChange?.(newCollapsed);
  };

  // Calculate flex basis for split ratio
  const primaryBasis = `${defaultRatio * 100}%`;
  const secondaryBasis = `${(1 - defaultRatio) * 100}%`;

  // Which pane gets collapsed
  const collapsiblePane = collapsePriority === 'secondary' ? secondary : primary;
  const fixedPane = collapsePriority === 'secondary' ? primary : secondary;

  return (
    <div
      className={cn(
        'flex h-full',
        direction === 'horizontal' ? 'flex-row' : 'flex-col',
        className
      )}
      style={{
        // Use CSS container query for responsive behavior
        containerType: 'inline-size',
      }}
    >
      {/* Desktop: Side-by-side layout */}
      <style>{`
        @container (min-width: ${collapseAt}px) {
          .elastic-split-desktop { display: flex !important; }
          .elastic-split-mobile { display: none !important; }
        }
        @container (max-width: ${collapseAt - 1}px) {
          .elastic-split-desktop { display: none !important; }
          .elastic-split-mobile { display: flex !important; }
        }
      `}</style>

      {/* Desktop layout */}
      <div
        className={cn(
          'elastic-split-desktop h-full',
          direction === 'horizontal' ? 'flex-row' : 'flex-col'
        )}
        style={{ display: 'flex' }}
      >
        <div
          className="overflow-hidden"
          style={{ flexBasis: primaryBasis, flexShrink: 1, flexGrow: 0 }}
        >
          {primary}
        </div>
        <div
          className={cn(
            'overflow-hidden border-town-accent/30',
            direction === 'horizontal' ? 'border-l' : 'border-t'
          )}
          style={{ flexBasis: secondaryBasis, flexShrink: 1, flexGrow: 0 }}
        >
          {secondary}
        </div>
      </div>

      {/* Mobile layout - stacked with collapse */}
      <div
        className="elastic-split-mobile flex-col h-full"
        style={{ display: 'none' }}
      >
        <div className="flex-1 overflow-hidden">{fixedPane}</div>

        {/* Collapse toggle */}
        <button
          onClick={handleToggleCollapse}
          className={cn(
            'w-full py-2 flex items-center justify-center gap-2',
            'bg-town-surface/50 border-t border-town-accent/30',
            'hover:bg-town-surface/70 transition-colors text-sm'
          )}
        >
          <span>{isCollapsed ? 'Show' : 'Hide'} {collapsePriority}</span>
          <span className="transition-transform" style={{ transform: isCollapsed ? 'rotate(180deg)' : 'none' }}>
            ▼
          </span>
        </button>

        {/* Collapsible pane */}
        <div
          className={cn(
            'overflow-hidden transition-all duration-300',
            isCollapsed ? 'h-0' : 'h-64'
          )}
        >
          {collapsiblePane}
        </div>
      </div>
    </div>
  );
}

export default ElasticSplit;
