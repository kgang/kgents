/**
 * ElasticCard: Priority-aware card that adapts to available space.
 *
 * Uses layout context to determine available space and collapses
 * gracefully based on priority and minContent settings.
 *
 * STARK BIOME: Steel frame, content earns glow
 * - Border: steel-gunmetal (default) → glow-spore (selected)
 * - Text: steel-zinc (muted) → glow-light (emphasis)
 * - Background: steel-carbon with transparency
 *
 * @see plans/web-refactor/elastic-primitives.md
 */

import { useMemo, type ReactNode, type CSSProperties } from 'react';
import { useLayoutContext } from '@/hooks/useLayoutContext';

export type MinContentLevel = 'icon' | 'title' | 'summary' | 'full';
export type ShrinkBehavior = 'truncate' | 'collapse' | 'stack' | 'hide';

export interface ElasticCardProps {
  /** Content priority (higher = survives truncation) */
  priority?: number;

  /** Minimum content to show when constrained */
  minContent?: MinContentLevel;

  /** How card responds to tight space */
  shrinkBehavior?: ShrinkBehavior;

  /** Enable drag handle */
  draggable?: boolean;

  /** Icon element (shown in icon/title modes) */
  icon?: ReactNode;

  /** Title text (shown in title/summary/full modes) */
  title?: ReactNode;

  /** Summary text (shown in summary/full modes) */
  summary?: ReactNode;

  /** Click handler */
  onClick?: () => void;

  /** Selection state */
  isSelected?: boolean;

  /** Hover state (controlled) */
  isHovered?: boolean;

  /** Custom class name */
  className?: string;

  /** Custom styles */
  style?: CSSProperties;

  /** Full content (children) */
  children?: ReactNode;
}

/**
 * Determine content level based on width and settings
 */
function determineContentLevel(
  availableWidth: number,
  isConstrained: boolean,
  minContent: MinContentLevel
): MinContentLevel {
  // Width thresholds for content levels
  const THRESHOLDS = {
    icon: 60,
    title: 150,
    summary: 280,
    full: 400,
  };

  // Find appropriate level based on width
  if (availableWidth < THRESHOLDS.icon) {
    return 'icon';
  } else if (availableWidth < THRESHOLDS.title || isConstrained) {
    return Math.max(getContentLevelOrder(minContent), getContentLevelOrder('title')) ===
      getContentLevelOrder(minContent)
      ? minContent
      : 'title';
  } else if (availableWidth < THRESHOLDS.summary) {
    return Math.max(getContentLevelOrder(minContent), getContentLevelOrder('summary')) ===
      getContentLevelOrder(minContent)
      ? minContent
      : 'summary';
  }
  return 'full';
}

function getContentLevelOrder(level: MinContentLevel): number {
  const order = { icon: 0, title: 1, summary: 2, full: 3 };
  return order[level];
}

export function ElasticCard({
  priority = 1,
  minContent = 'title',
  shrinkBehavior = 'truncate',
  draggable = false,
  icon,
  title,
  summary,
  onClick,
  isSelected = false,
  isHovered,
  className = '',
  style,
  children,
}: ElasticCardProps) {
  const context = useLayoutContext();

  // Determine current content level
  const contentLevel = useMemo(() => {
    return determineContentLevel(context.availableWidth, context.isConstrained, minContent);
  }, [context.availableWidth, context.isConstrained, minContent]);

  // Should this card be hidden?
  const shouldHide = useMemo(() => {
    if (shrinkBehavior !== 'hide') return false;
    // Hide low-priority cards when very constrained
    return context.isConstrained && priority < 5 && contentLevel === 'icon';
  }, [shrinkBehavior, context.isConstrained, priority, contentLevel]);

  if (shouldHide) {
    return null;
  }

  // Build class list — Stark Biome: steel frame, earned glow
  const cardClasses = [
    'elastic-card',
    'rounded-bare', // Stark: bare edge system
    'border',
    'transition-all',
    'duration-quick',
    isSelected ? 'border-glow-spore ring-2 ring-glow-spore/30' : 'border-steel-gunmetal/30',
    onClick ? 'cursor-pointer' : '',
    isHovered !== undefined ? '' : 'hover:border-steel-gunmetal/60',
    draggable ? 'cursor-grab active:cursor-grabbing' : '',
    shrinkBehavior === 'stack' && context.isConstrained ? 'flex-col' : '',
    className,
  ]
    .filter(Boolean)
    .join(' ');

  // Build inline styles with priority as CSS var (for potential styling hooks)
  // Stark Biome: steel-carbon base, glow-spore accent when selected
  const cardStyle: CSSProperties = {
    '--card-priority': priority,
    backgroundColor: isSelected
      ? 'rgba(196, 167, 125, 0.1)' // glow-spore at 10%
      : 'rgba(20, 20, 24, 0.8)', // steel-carbon at 80%
    ...style,
  } as CSSProperties;

  // Render based on content level
  const renderContent = () => {
    switch (contentLevel) {
      case 'icon':
        return (
          <div className="flex items-center justify-center p-2">
            {icon || <span className="text-lg text-steel-zinc">?</span>}
          </div>
        );

      case 'title':
        return (
          <div className="flex items-center gap-2 p-3">
            {icon && <span className="flex-shrink-0">{icon}</span>}
            {title && (
              <span className="font-medium text-glow-light truncate" title={String(title)}>
                {title}
              </span>
            )}
          </div>
        );

      case 'summary':
        return (
          <div className="p-3">
            <div className="flex items-center gap-2 mb-1">
              {icon && <span className="flex-shrink-0">{icon}</span>}
              {title && <span className="font-medium text-glow-light">{title}</span>}
            </div>
            {summary && <div className="text-sm text-steel-zinc line-clamp-2">{summary}</div>}
          </div>
        );

      case 'full':
      default:
        return (
          <div className="p-4">
            <div className="flex items-center gap-2 mb-2">
              {icon && <span className="flex-shrink-0">{icon}</span>}
              {title && <span className="font-medium text-glow-light">{title}</span>}
            </div>
            {summary && <div className="text-sm text-steel-zinc mb-3">{summary}</div>}
            {children}
          </div>
        );
    }
  };

  return (
    <div
      className={cardClasses}
      style={cardStyle}
      onClick={onClick}
      draggable={draggable}
      data-priority={priority}
      data-content-level={contentLevel}
      role={onClick ? 'button' : 'article'}
      tabIndex={onClick ? 0 : undefined}
      onKeyDown={
        onClick
          ? (e) => {
              if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                onClick();
              }
            }
          : undefined
      }
    >
      {renderContent()}
    </div>
  );
}

export default ElasticCard;
