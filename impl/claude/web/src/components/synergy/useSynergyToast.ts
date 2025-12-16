/**
 * useSynergyToast - Hook for showing synergy notifications
 *
 * This hook provides a convenient interface for showing cross-jewel
 * synergy notifications from any component.
 *
 * Usage:
 * ```tsx
 * const { showToast, gestaltToBrain, crystalFormed } = useSynergyToast();
 *
 * // After Gestalt analysis completes:
 * gestaltToBrain('impl/claude/', 'A+');
 *
 * // After Brain captures a crystal:
 * crystalFormed('Architecture Snapshot 2025-12-16');
 * ```
 */

import { useCallback } from 'react';
import { useSynergyToastStore, synergyToast, showSynergyToast } from './store';
import type { Jewel, SynergyEventType } from './types';

export interface UseSynergyToastReturn {
  /** Show a generic synergy toast */
  showToast: typeof showSynergyToast;

  /** Clear all toasts */
  clearAll: () => void;

  /** Count of active toasts */
  toastCount: number;

  // Quick helpers for common synergy patterns
  gestaltToBrain: typeof synergyToast.gestaltToBrain;
  crystalFormed: typeof synergyToast.crystalFormed;
  sessionComplete: typeof synergyToast.sessionComplete;
  pieceCreated: typeof synergyToast.pieceCreated;
  taskComplete: typeof synergyToast.taskComplete;
  scenarioComplete: typeof synergyToast.scenarioComplete;
  drillComplete: typeof synergyToast.drillComplete;
  seasonChanged: typeof synergyToast.seasonChanged;
  driftDetected: typeof synergyToast.driftDetected;
  timerWarning: typeof synergyToast.timerWarning;
  serendipityInjected: typeof synergyToast.serendipityInjected;
}

/**
 * Hook for showing synergy toast notifications.
 */
export function useSynergyToast(): UseSynergyToastReturn {
  const { toasts, clearAll } = useSynergyToastStore();

  // Wrap in useCallback for stable references
  const showToast = useCallback(
    (
      sourceJewel: Jewel,
      targetJewel: Jewel | '*',
      eventType: SynergyEventType,
      description?: string,
      action?: { label: string; href: string },
    ) => {
      showSynergyToast(sourceJewel, targetJewel, eventType, description, action);
    },
    [],
  );

  return {
    showToast,
    clearAll,
    toastCount: toasts.length,

    // Quick helpers
    gestaltToBrain: synergyToast.gestaltToBrain,
    crystalFormed: synergyToast.crystalFormed,
    sessionComplete: synergyToast.sessionComplete,
    pieceCreated: synergyToast.pieceCreated,
    taskComplete: synergyToast.taskComplete,
    scenarioComplete: synergyToast.scenarioComplete,
    drillComplete: synergyToast.drillComplete,
    seasonChanged: synergyToast.seasonChanged,
    driftDetected: synergyToast.driftDetected,
    timerWarning: synergyToast.timerWarning,
    serendipityInjected: synergyToast.serendipityInjected,
  };
}
