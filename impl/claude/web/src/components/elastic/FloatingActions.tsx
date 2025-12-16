/**
 * FloatingActions: Mobile-friendly floating action button cluster.
 *
 * Part of the Layout Projection Functor's Actions primitive.
 * In compact mode, toolbars project to floating action button clusters.
 *
 * Physical constraints enforced:
 * - Button touch target: 48px x 48px minimum
 * - Spacing between buttons: 8px minimum
 *
 * @see spec/protocols/projection.md (Layout Projection section)
 * @see plans/web-refactor/layout-projection-functor.md
 */

import { type CSSProperties, type ReactNode } from 'react';
import { PHYSICAL_CONSTRAINTS } from './types';

/**
 * Individual action button definition.
 */
export interface FloatingAction {
  /** Unique identifier for the action */
  id: string;

  /** Icon or emoji to display */
  icon: ReactNode;

  /** Accessible label */
  label: string;

  /** Click handler */
  onClick: () => void;

  /** Whether action is currently active/pressed */
  isActive?: boolean;

  /** Whether action is disabled */
  disabled?: boolean;

  /** Whether action is in loading state */
  loading?: boolean;

  /** Button variant for styling */
  variant?: 'default' | 'primary' | 'danger';
}

export interface FloatingActionsProps {
  /** Array of action buttons to display */
  actions: FloatingAction[];

  /** Position on screen */
  position?: 'bottom-right' | 'bottom-left' | 'top-right' | 'top-left';

  /** Gap between buttons (default: 8px, enforced minimum) */
  gap?: number;

  /** Custom class name for the container */
  className?: string;

  /** Orientation of the button stack */
  direction?: 'vertical' | 'horizontal';

  /** Button size (default: 48px to meet touch target minimum) */
  buttonSize?: number;
}

/**
 * Get variant-specific classes for a button.
 */
function getVariantClasses(variant: FloatingAction['variant'], isActive: boolean): string {
  const base = 'rounded-full shadow-lg flex items-center justify-center transition-colors';

  if (isActive) {
    return `${base} bg-indigo-600 text-white`;
  }

  switch (variant) {
    case 'primary':
      return `${base} bg-green-600 hover:bg-green-700 disabled:bg-gray-700 text-white`;
    case 'danger':
      return `${base} bg-red-600 hover:bg-red-700 disabled:bg-gray-700 text-white`;
    default:
      return `${base} bg-gray-700 hover:bg-gray-600 disabled:bg-gray-800 text-white`;
  }
}

/**
 * Get position-specific classes for the container.
 */
function getPositionClasses(position: FloatingActionsProps['position']): string {
  switch (position) {
    case 'bottom-left':
      return 'bottom-4 left-4';
    case 'top-right':
      return 'top-4 right-4';
    case 'top-left':
      return 'top-4 left-4';
    case 'bottom-right':
    default:
      return 'bottom-4 right-4';
  }
}

/**
 * FloatingActions component for mobile action projection.
 *
 * Usage:
 * ```tsx
 * <FloatingActions
 *   actions={[
 *     { id: 'scan', icon: '🔄', label: 'Rescan', onClick: handleScan, variant: 'primary' },
 *     { id: 'settings', icon: '⚙️', label: 'Settings', onClick: toggleSettings, isActive: settingsOpen },
 *     { id: 'details', icon: '📋', label: 'Details', onClick: toggleDetails, disabled: !hasSelection },
 *   ]}
 *   position="bottom-right"
 * />
 * ```
 */
export function FloatingActions({
  actions,
  position = 'bottom-right',
  gap,
  className = '',
  direction = 'vertical',
  buttonSize,
}: FloatingActionsProps) {
  // Enforce minimum physical constraints
  const effectiveGap = Math.max(gap ?? PHYSICAL_CONSTRAINTS.minTapSpacing, PHYSICAL_CONSTRAINTS.minTapSpacing);
  const effectiveButtonSize = Math.max(
    buttonSize ?? PHYSICAL_CONSTRAINTS.minTouchTarget,
    PHYSICAL_CONSTRAINTS.minTouchTarget
  );

  const containerStyle: CSSProperties = {
    gap: effectiveGap,
  };

  const buttonStyle: CSSProperties = {
    width: effectiveButtonSize,
    height: effectiveButtonSize,
    minWidth: effectiveButtonSize,
    minHeight: effectiveButtonSize,
  };

  const positionClasses = getPositionClasses(position);
  const directionClasses = direction === 'horizontal' ? 'flex-row' : 'flex-col';

  return (
    <div
      className={`absolute ${positionClasses} flex ${directionClasses} ${className}`}
      style={containerStyle}
      role="toolbar"
      aria-label="Quick actions"
    >
      {actions.map((action) => (
        <button
          key={action.id}
          onClick={action.onClick}
          disabled={action.disabled || action.loading}
          className={getVariantClasses(action.variant, action.isActive ?? false)}
          style={buttonStyle}
          title={action.label}
          aria-label={action.label}
          aria-pressed={action.isActive}
        >
          {action.loading ? (
            <span className="animate-spin">{action.icon}</span>
          ) : (
            <span className="text-xl">{action.icon}</span>
          )}
        </button>
      ))}
    </div>
  );
}

export default FloatingActions;
