/**
 * useSimpleToast - Simple toast notifications for general feedback
 *
 * A thin wrapper over the synergy toast system for general-purpose
 * notifications that don't need jewel-to-jewel semantics.
 *
 * @example
 * ```tsx
 * const { toast } = useSimpleToast();
 *
 * // Simple usage
 * toast.success('Settings saved');
 * toast.error('Failed to save');
 * toast.info('Processing...');
 *
 * // With description
 * toast.success('File uploaded', 'myfile.txt (2.3 MB)');
 * ```
 */

import { useSynergyToastStore } from '@/components/synergy/store';
import type { SynergyToastType } from '@/components/synergy/types';

// =============================================================================
// Types
// =============================================================================

export interface SimpleToastOptions {
  /** Toast duration in milliseconds (default: 4000) */
  duration?: number;
  /** Optional action button */
  action?: {
    label: string;
    href: string;
  };
}

export interface UseSimpleToastReturn {
  toast: {
    /** Show success toast */
    success: (title: string, description?: string, options?: SimpleToastOptions) => void;
    /** Show error toast */
    error: (title: string, description?: string, options?: SimpleToastOptions) => void;
    /** Show info toast */
    info: (title: string, description?: string, options?: SimpleToastOptions) => void;
    /** Show warning toast */
    warning: (title: string, description?: string, options?: SimpleToastOptions) => void;
  };
  /** Clear all toasts */
  clearAll: () => void;
}

// =============================================================================
// Constants
// =============================================================================

const DEFAULT_DURATION = 4000;

// =============================================================================
// Hook
// =============================================================================

/**
 * Hook for showing simple toast notifications.
 *
 * Uses the synergy toast infrastructure with a simpler API
 * for general-purpose feedback.
 */
export function useSimpleToast(): UseSimpleToastReturn {
  const { addToast, clearAll } = useSynergyToastStore();

  const showToast = (
    type: SynergyToastType,
    title: string,
    description?: string,
    options?: SimpleToastOptions
  ) => {
    addToast({
      type,
      // Use 'gestalt' as a neutral source jewel for system toasts
      sourceJewel: 'gestalt',
      targetJewel: '*',
      eventType: 'analysis_complete', // Neutral event type
      title,
      description,
      duration: options?.duration ?? DEFAULT_DURATION,
      action: options?.action,
    });
  };

  return {
    toast: {
      success: (title, description, options) =>
        showToast('success', title, description, options),
      error: (title, description, options) =>
        showToast('error', title, description, options),
      info: (title, description, options) =>
        showToast('info', title, description, options),
      warning: (title, description, options) =>
        showToast('warning', title, description, options),
    },
    clearAll,
  };
}

// =============================================================================
// Standalone functions (for use outside React)
// =============================================================================

/**
 * Show a toast without needing the hook.
 * Useful for async operations or outside components.
 */
export const simpleToast = {
  success: (title: string, description?: string, options?: SimpleToastOptions) => {
    useSynergyToastStore.getState().addToast({
      type: 'success',
      sourceJewel: 'gestalt',
      targetJewel: '*',
      eventType: 'analysis_complete',
      title,
      description,
      duration: options?.duration ?? DEFAULT_DURATION,
      action: options?.action,
    });
  },
  error: (title: string, description?: string, options?: SimpleToastOptions) => {
    useSynergyToastStore.getState().addToast({
      type: 'error',
      sourceJewel: 'gestalt',
      targetJewel: '*',
      eventType: 'analysis_complete',
      title,
      description,
      duration: options?.duration ?? DEFAULT_DURATION,
      action: options?.action,
    });
  },
  info: (title: string, description?: string, options?: SimpleToastOptions) => {
    useSynergyToastStore.getState().addToast({
      type: 'info',
      sourceJewel: 'gestalt',
      targetJewel: '*',
      eventType: 'analysis_complete',
      title,
      description,
      duration: options?.duration ?? DEFAULT_DURATION,
      action: options?.action,
    });
  },
  warning: (title: string, description?: string, options?: SimpleToastOptions) => {
    useSynergyToastStore.getState().addToast({
      type: 'warning',
      sourceJewel: 'gestalt',
      targetJewel: '*',
      eventType: 'analysis_complete',
      title,
      description,
      duration: options?.duration ?? DEFAULT_DURATION,
      action: options?.action,
    });
  },
};

export default useSimpleToast;
