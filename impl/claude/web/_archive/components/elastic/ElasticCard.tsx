/**
 * ElasticCard: Self-sizing card with priority hints.
 *
 * Cards that gracefully adapt to available space. Higher priority cards
 * survive truncation/collapse scenarios. Supports draggable mode for
 * future pipeline interactions.
 *
 * @see plans/web-refactor/elastic-primitives.md
 */

import { forwardRef, type ReactNode, type MouseEvent } from 'react';
import { cn } from '@/lib/utils';

export type CardMinContent = 'icon' | 'title' | 'summary' | 'full';
export type CardShrinkBehavior = 'truncate' | 'collapse' | 'stack' | 'hide';

export interface ElasticCardProps {
  /** Content priority (higher = survives truncation) */
  priority?: number;

  /** Minimum content to show when space is constrained */
  minContent?: CardMinContent;

  /** How card responds to tight space */
  shrinkBehavior?: CardShrinkBehavior;

  /** Enable drag handle appearance */
  draggable?: boolean;

  /** Whether the card is selected */
  isSelected?: boolean;

  /** Click handler */
  onClick?: (e: MouseEvent<HTMLDivElement>) => void;

  /** Additional class names */
  className?: string;

  /** Inline styles (for drag transforms) */
  style?: React.CSSProperties;

  /** Card content */
  children: ReactNode;
}

/**
 * Determines the base styles for different shrink behaviors
 */
function getShrinkClasses(behavior: CardShrinkBehavior): string {
  switch (behavior) {
    case 'truncate':
      return 'min-w-0'; // Allow text truncation
    case 'collapse':
      return 'overflow-hidden';
    case 'stack':
      return 'flex-wrap';
    case 'hide':
      return ''; // Handled at container level
    default:
      return '';
  }
}

export const ElasticCard = forwardRef<HTMLDivElement, ElasticCardProps>(function ElasticCard(
  {
    priority = 1,
    minContent = 'full',
    shrinkBehavior = 'truncate',
    draggable = false,
    isSelected = false,
    onClick,
    className,
    style,
    children,
  },
  ref
) {
  return (
    <div
      ref={ref}
      onClick={onClick}
      style={style}
      role={onClick ? 'button' : undefined}
      tabIndex={onClick ? 0 : undefined}
      data-priority={priority}
      data-min-content={minContent}
      data-draggable={draggable}
      className={cn(
        // Base styles
        'elastic-card rounded-lg bg-town-surface/50 border border-town-accent/30',
        'p-4',

        // Interactive states
        onClick && 'cursor-pointer elastic-focus',
        isSelected && 'ring-2 ring-town-highlight border-town-highlight',

        // Draggable indicator
        draggable && 'relative',

        // Shrink behavior
        getShrinkClasses(shrinkBehavior),

        // Custom classes
        className
      )}
      onKeyDown={
        onClick
          ? (e) => {
              if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                onClick(e as unknown as MouseEvent<HTMLDivElement>);
              }
            }
          : undefined
      }
    >
      {/* Drag handle indicator */}
      {draggable && (
        <div className="absolute top-2 right-2 opacity-40 hover:opacity-70 cursor-grab active:cursor-grabbing">
          <svg
            className="w-4 h-4"
            fill="currentColor"
            viewBox="0 0 20 20"
            aria-hidden="true"
          >
            <path d="M7 2a2 2 0 1 0 0 4 2 2 0 0 0 0-4zM7 8a2 2 0 1 0 0 4 2 2 0 0 0 0-4zM7 14a2 2 0 1 0 0 4 2 2 0 0 0 0-4zM13 2a2 2 0 1 0 0 4 2 2 0 0 0 0-4zM13 8a2 2 0 1 0 0 4 2 2 0 0 0 0-4zM13 14a2 2 0 1 0 0 4 2 2 0 0 0 0-4z" />
          </svg>
        </div>
      )}

      {children}
    </div>
  );
});

/**
 * ElasticCardHeader: Standard header layout for cards
 */
export interface ElasticCardHeaderProps {
  icon?: ReactNode;
  title: string;
  subtitle?: string;
  action?: ReactNode;
  className?: string;
}

export function ElasticCardHeader({
  icon,
  title,
  subtitle,
  action,
  className,
}: ElasticCardHeaderProps) {
  return (
    <div className={cn('flex items-center gap-3', className)}>
      {icon && <div className="flex-shrink-0 text-xl">{icon}</div>}
      <div className="flex-1 min-w-0">
        <h3 className="font-semibold truncate">{title}</h3>
        {subtitle && <p className="text-sm text-gray-400 truncate">{subtitle}</p>}
      </div>
      {action && <div className="flex-shrink-0">{action}</div>}
    </div>
  );
}

/**
 * ElasticCardContent: Body content with optional padding control
 */
export interface ElasticCardContentProps {
  className?: string;
  children: ReactNode;
}

export function ElasticCardContent({ className, children }: ElasticCardContentProps) {
  return <div className={cn('mt-3', className)}>{children}</div>;
}

/**
 * ElasticCardFooter: Footer for actions or metadata
 */
export interface ElasticCardFooterProps {
  className?: string;
  children: ReactNode;
}

export function ElasticCardFooter({ className, children }: ElasticCardFooterProps) {
  return (
    <div
      className={cn(
        'mt-3 pt-3 border-t border-town-accent/20 flex items-center gap-2',
        className
      )}
    >
      {children}
    </div>
  );
}

export default ElasticCard;
