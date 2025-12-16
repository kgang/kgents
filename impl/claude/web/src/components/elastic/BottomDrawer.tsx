/**
 * BottomDrawer: Mobile-friendly panel that slides up from the bottom.
 *
 * Part of the Layout Projection Functor's Panel primitive.
 * In compact mode, panels project to bottom drawers.
 *
 * Physical constraints enforced:
 * - Handle touch target: 48px x 48px (visual can be smaller)
 * - Drawer handle visual: 40px x 4px centered in 48px touch area
 *
 * @see spec/protocols/projection.md (Layout Projection section)
 * @see plans/web-refactor/layout-projection-functor.md
 */

import { type ReactNode, type CSSProperties, useCallback, useEffect } from 'react';
import { PHYSICAL_CONSTRAINTS } from './types';

export interface BottomDrawerProps {
  /** Whether the drawer is open */
  isOpen: boolean;

  /** Callback when drawer should close */
  onClose: () => void;

  /** Title shown in the drawer header */
  title: string;

  /** Drawer content */
  children: ReactNode;

  /** Maximum height as percentage of viewport (default: 70) */
  maxHeightPercent?: number;

  /** Whether to show backdrop overlay (default: true) */
  showBackdrop?: boolean;

  /** Custom class name for the drawer */
  className?: string;

  /** Custom class name for the content area */
  contentClassName?: string;

  /** Whether to allow drag-to-close (future enhancement) */
  dragToClose?: boolean;

  /** Z-index for the drawer (default: 50) */
  zIndex?: number;

  /** Accessible label for the drawer */
  ariaLabel?: string;
}

/**
 * BottomDrawer component for mobile panel projection.
 *
 * Usage:
 * ```tsx
 * <BottomDrawer
 *   isOpen={panelState.details}
 *   onClose={() => setPanelState(s => ({ ...s, details: false }))}
 *   title="Details"
 * >
 *   <DetailPanel />
 * </BottomDrawer>
 * ```
 */
export function BottomDrawer({
  isOpen,
  onClose,
  title,
  children,
  maxHeightPercent = 70,
  showBackdrop = true,
  className = '',
  contentClassName = '',
  zIndex = 50,
  ariaLabel,
}: BottomDrawerProps) {
  // Handle escape key to close
  useEffect(() => {
    if (!isOpen) return;

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose();
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  // Prevent body scroll when open
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = '';
    }

    return () => {
      document.body.style.overflow = '';
    };
  }, [isOpen]);

  const handleBackdropClick = useCallback(() => {
    onClose();
  }, [onClose]);

  if (!isOpen) return null;

  const drawerStyle: CSSProperties = {
    transform: isOpen ? 'translateY(0)' : 'translateY(100%)',
    maxHeight: `${maxHeightPercent}vh`,
    zIndex,
  };

  return (
    <>
      {/* Backdrop */}
      {showBackdrop && (
        <div
          className="fixed inset-0 bg-black/50"
          style={{ zIndex: zIndex - 1 }}
          onClick={handleBackdropClick}
          aria-hidden="true"
        />
      )}

      {/* Drawer */}
      <div
        role="dialog"
        aria-modal="true"
        aria-label={ariaLabel || title}
        className={`fixed bottom-0 left-0 right-0 bg-gray-800 rounded-t-xl shadow-2xl transform transition-transform duration-300 ${className}`}
        style={drawerStyle}
      >
        {/* Handle - 48px touch target with 40x4 visual handle */}
        <div
          className="flex justify-center items-center cursor-pointer"
          onClick={onClose}
          role="button"
          aria-label="Close drawer"
          tabIndex={0}
          onKeyDown={(e) => {
            if (e.key === 'Enter' || e.key === ' ') {
              e.preventDefault();
              onClose();
            }
          }}
          style={{
            height: PHYSICAL_CONSTRAINTS.minTouchTarget,
            minHeight: PHYSICAL_CONSTRAINTS.minTouchTarget,
          }}
        >
          {/* Visual handle indicator */}
          <div
            className="bg-gray-600 rounded-full"
            style={{
              width: PHYSICAL_CONSTRAINTS.drawerHandleVisual.width,
              height: PHYSICAL_CONSTRAINTS.drawerHandleVisual.height,
            }}
          />
        </div>

        {/* Header */}
        <div className="flex justify-between items-center px-4 pb-2 border-b border-gray-700">
          <h3 className="text-sm font-semibold text-white">{title}</h3>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-white text-lg p-1 rounded hover:bg-gray-700 transition-colors"
            style={{
              minWidth: PHYSICAL_CONSTRAINTS.minTouchTarget,
              minHeight: PHYSICAL_CONSTRAINTS.minTouchTarget,
            }}
            aria-label="Close"
          >
            ×
          </button>
        </div>

        {/* Content */}
        <div
          className={`overflow-y-auto ${contentClassName}`}
          style={{ maxHeight: `calc(${maxHeightPercent}vh - 60px)` }}
        >
          {children}
        </div>
      </div>
    </>
  );
}

export default BottomDrawer;
