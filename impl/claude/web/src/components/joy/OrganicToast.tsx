/**
 * OrganicToast - Growing notification component
 *
 * Implements "Growing" from Crown Jewels Genesis Moodboard.
 * Notifications grow like seeds → sprout → bloom → full, not pop in.
 *
 * @see plans/crown-jewels-genesis.md - Phase 1: Foundation
 * @see hooks/useGrowing.ts - Animation hook
 */

import { useEffect, useCallback, useRef, type ReactNode, type CSSProperties } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useGrowing, type GrowthStage } from '@/hooks';
import { LIVING_EARTH, GROWING_ANIMATION } from '@/constants';
import { useMotionPreferences } from './useMotionPreferences';

// =============================================================================
// Types
// =============================================================================

export type ToastType = 'success' | 'info' | 'warning' | 'error' | 'token';

export interface OrganicToastProps {
  /** Toast unique identifier */
  id: string;

  /** Toast type determines accent color */
  type?: ToastType;

  /** Toast title */
  title: string;

  /** Optional description text */
  description?: ReactNode;

  /** Optional icon element */
  icon?: ReactNode;

  /** Duration in ms before auto-dismiss (0 = no auto-dismiss) */
  duration?: number;

  /** Whether toast is visible */
  isVisible: boolean;

  /** Callback when toast should be dismissed */
  onDismiss?: (id: string) => void;

  /** Position of toast */
  position?: 'top-right' | 'top-left' | 'bottom-right' | 'bottom-left' | 'top-center' | 'bottom-center';

  /** Custom class name */
  className?: string;

  /** Custom styles */
  style?: CSSProperties;
}

// =============================================================================
// Color Configuration
// =============================================================================

const TOAST_COLORS: Record<ToastType, { border: string; glow: string; icon: string }> = {
  success: {
    border: '#22C55E',
    glow: 'rgba(34, 197, 94, 0.3)',
    icon: '#22C55E',
  },
  info: {
    border: '#06B6D4',
    glow: 'rgba(6, 182, 212, 0.3)',
    icon: '#06B6D4',
  },
  warning: {
    border: '#F59E0B',
    glow: 'rgba(245, 158, 11, 0.3)',
    icon: '#F59E0B',
  },
  error: {
    border: '#EF4444',
    glow: 'rgba(239, 68, 68, 0.3)',
    icon: '#EF4444',
  },
  token: {
    border: LIVING_EARTH.amber,
    glow: 'rgba(212, 165, 116, 0.4)',
    icon: LIVING_EARTH.amber,
  },
};

// =============================================================================
// Component
// =============================================================================

/**
 * OrganicToast
 *
 * A notification that grows organically rather than popping in.
 * Perfect for token-earned notifications, system alerts, and user feedback.
 *
 * @example
 * ```tsx
 * <OrganicToast
 *   id="token-earned"
 *   type="token"
 *   title="Token Earned!"
 *   description="You influenced the direction"
 *   icon={<TokenIcon />}
 *   isVisible={showToast}
 *   onDismiss={(id) => setShowToast(false)}
 * />
 * ```
 */
export function OrganicToast({
  id,
  type = 'info',
  title,
  description,
  icon,
  duration = 5000,
  isVisible,
  onDismiss,
  position = 'top-right',
  className = '',
  style,
}: OrganicToastProps) {
  const { shouldAnimate } = useMotionPreferences();
  const { scale, opacity, stage, trigger, reset } = useGrowing({
    duration: GROWING_ANIMATION.duration,
    respectReducedMotion: true,
  });

  const dismissTimeoutRef = useRef<number | null>(null);

  // Handle visibility changes
  useEffect(() => {
    if (isVisible) {
      trigger();

      // Set up auto-dismiss if duration > 0
      if (duration > 0 && onDismiss) {
        dismissTimeoutRef.current = window.setTimeout(() => {
          onDismiss(id);
        }, duration);
      }
    } else {
      reset();
    }

    return () => {
      if (dismissTimeoutRef.current) {
        clearTimeout(dismissTimeoutRef.current);
      }
    };
  }, [isVisible, trigger, reset, duration, onDismiss, id]);

  const handleDismiss = useCallback(() => {
    if (dismissTimeoutRef.current) {
      clearTimeout(dismissTimeoutRef.current);
    }
    onDismiss?.(id);
  }, [onDismiss, id]);

  const colors = TOAST_COLORS[type];

  // Position styles
  const positionStyles: Record<string, CSSProperties> = {
    'top-right': { top: 16, right: 16 },
    'top-left': { top: 16, left: 16 },
    'bottom-right': { bottom: 16, right: 16 },
    'bottom-left': { bottom: 16, left: 16 },
    'top-center': { top: 16, left: '50%', transform: 'translateX(-50%)' },
    'bottom-center': { bottom: 16, left: '50%', transform: 'translateX(-50%)' },
  };

  // Framer-motion variants for enter/exit
  const variants = {
    hidden: {
      scale: 0,
      opacity: 0,
      y: position.includes('bottom') ? 20 : -20,
    },
    visible: {
      scale: 1,
      opacity: 1,
      y: 0,
      transition: {
        type: 'spring',
        stiffness: 400,
        damping: 25,
      },
    },
    exit: {
      scale: 0.8,
      opacity: 0,
      y: position.includes('bottom') ? 20 : -20,
      transition: {
        duration: 0.2,
      },
    },
  };

  // If reduced motion, use simpler animation
  const reducedVariants = {
    hidden: { opacity: 0 },
    visible: { opacity: 1, transition: { duration: 0.15 } },
    exit: { opacity: 0, transition: { duration: 0.15 } },
  };

  return (
    <AnimatePresence>
      {isVisible && (
        <motion.div
          key={id}
          className={`fixed z-50 ${className}`}
          style={{
            ...positionStyles[position],
            ...style,
          }}
          variants={shouldAnimate ? variants : reducedVariants}
          initial="hidden"
          animate="visible"
          exit="exit"
        >
          <div
            className="flex items-start gap-3 p-4 rounded-lg shadow-lg cursor-pointer backdrop-blur-sm"
            style={{
              background: LIVING_EARTH.bark,
              border: `1px solid ${colors.border}`,
              boxShadow: `0 4px 12px rgba(0, 0, 0, 0.3), 0 0 20px ${colors.glow}`,
              maxWidth: 360,
            }}
            onClick={handleDismiss}
            role="alert"
            aria-live="polite"
          >
            {/* Icon */}
            {icon && (
              <div
                className="flex-shrink-0 mt-0.5"
                style={{ color: colors.icon }}
              >
                {icon}
              </div>
            )}

            {/* Content */}
            <div className="flex-1 min-w-0">
              <h4
                className="text-sm font-medium"
                style={{ color: LIVING_EARTH.lantern }}
              >
                {title}
              </h4>
              {description && (
                <p
                  className="mt-1 text-sm"
                  style={{ color: LIVING_EARTH.sand }}
                >
                  {description}
                </p>
              )}
            </div>

            {/* Dismiss button */}
            <button
              className="flex-shrink-0 ml-2 p-1 rounded hover:bg-white/10 transition-colors"
              onClick={(e) => {
                e.stopPropagation();
                handleDismiss();
              }}
              aria-label="Dismiss"
            >
              <svg
                className="w-4 h-4"
                style={{ color: LIVING_EARTH.clay }}
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
            </button>

            {/* Growth stage indicator (visible in teaching mode) */}
            <GrowthIndicator stage={stage} />
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}

/**
 * Growth stage indicator - shows current animation stage (for teaching mode)
 */
function GrowthIndicator({ stage }: { stage: GrowthStage }) {
  const stages: GrowthStage[] = ['seed', 'sprout', 'bloom', 'full'];
  const currentIndex = stages.indexOf(stage);

  return (
    <div
      className="absolute -bottom-1 left-1/2 -translate-x-1/2 flex gap-0.5"
      style={{ opacity: 0 }} // Hidden by default, can be enabled via CSS
    >
      {stages.map((s, i) => (
        <div
          key={s}
          className="w-1 h-1 rounded-full transition-colors"
          style={{
            backgroundColor: i <= currentIndex ? LIVING_EARTH.amber : LIVING_EARTH.clay,
          }}
        />
      ))}
    </div>
  );
}

// =============================================================================
// Toast Container
// =============================================================================

export interface ToastContainerProps {
  /** Array of toast items */
  toasts: OrganicToastProps[];

  /** Position of container */
  position?: OrganicToastProps['position'];
}

/**
 * ToastContainer
 *
 * Container for multiple toasts with staggered layout.
 */
export function ToastContainer({
  toasts,
  position = 'top-right',
}: ToastContainerProps) {
  return (
    <div className="fixed z-50 pointer-events-none" style={{ inset: 0 }}>
      <div
        className="flex flex-col gap-3 pointer-events-auto"
        style={{
          position: 'fixed',
          ...(position.includes('top') ? { top: 16 } : { bottom: 16 }),
          ...(position.includes('right') ? { right: 16 } : {}),
          ...(position.includes('left') ? { left: 16 } : {}),
          ...(position.includes('center') ? { left: '50%', transform: 'translateX(-50%)' } : {}),
        }}
      >
        {toasts.map((toast) => (
          <OrganicToast key={toast.id} {...toast} position={undefined} />
        ))}
      </div>
    </div>
  );
}

// =============================================================================
// Default Export
// =============================================================================

export default OrganicToast;
