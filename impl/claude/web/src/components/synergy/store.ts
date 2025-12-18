/**
 * Synergy Toast Store
 *
 * Zustand store for managing cross-jewel synergy notifications.
 * Toasts automatically dismiss after their duration.
 */

import { create } from 'zustand';
import type { Jewel, SynergyEventType, SynergyToast, SynergyToastType } from './types';

const DEFAULT_DURATION = 5000;
const MAX_TOASTS = 5;

interface SynergyToastStore {
  /** Active toasts, newest first */
  toasts: SynergyToast[];

  /** Add a new toast */
  addToast: (toast: Omit<SynergyToast, 'id' | 'createdAt'>) => void;

  /** Remove a toast by ID */
  removeToast: (id: string) => void;

  /** Clear all toasts */
  clearAll: () => void;

  /** Get count of toasts from a specific jewel */
  countByJewel: (jewel: Jewel) => number;
}

/**
 * Generate unique toast ID.
 */
function generateId(): string {
  return `toast-${Date.now()}-${Math.random().toString(36).slice(2, 9)}`;
}

/**
 * Synergy toast store.
 * Manages the queue of active toast notifications.
 */
export const useSynergyToastStore = create<SynergyToastStore>((set, get) => ({
  toasts: [],

  addToast: (toastData) => {
    const id = generateId();
    const toast: SynergyToast = {
      ...toastData,
      id,
      createdAt: new Date(),
      duration: toastData.duration ?? DEFAULT_DURATION,
    };

    set((state) => ({
      // Add new toast at beginning, limit to max
      toasts: [toast, ...state.toasts].slice(0, MAX_TOASTS),
    }));

    // Auto-dismiss after duration
    if (toast.duration && toast.duration > 0) {
      setTimeout(() => {
        get().removeToast(id);
      }, toast.duration);
    }
  },

  removeToast: (id) => {
    set((state) => ({
      toasts: state.toasts.filter((t) => t.id !== id),
    }));
  },

  clearAll: () => {
    set({ toasts: [] });
  },

  countByJewel: (jewel) => {
    return get().toasts.filter((t) => t.sourceJewel === jewel).length;
  },
}));

/**
 * Event type to toast type mapping.
 * Determines the visual style of the toast.
 */
function getToastType(eventType: SynergyEventType): SynergyToastType {
  switch (eventType) {
    // Success events
    case 'crystal_formed':
    case 'analysis_complete':
    case 'session_complete':
    case 'piece_created':
    case 'drill_complete':
    case 'scenario_complete':
    case 'coalition_formed':
    case 'data_stored':
    case 'data_upgraded':
      return 'success';

    // Warning events
    case 'timer_warning':
    case 'consent_debt_high':
    case 'drift_detected':
    case 'data_degraded':
      return 'warning';

    // Error events
    case 'timer_critical':
    case 'timer_expired':
      return 'error';

    // Info events (default)
    default:
      return 'info';
  }
}

/**
 * Generate human-readable toast title from event type.
 */
function getToastTitle(eventType: SynergyEventType): string {
  const titles: Record<SynergyEventType, string> = {
    // Gestalt
    analysis_complete: 'Analysis Complete',
    health_computed: 'Health Grade Updated',
    drift_detected: 'Drift Detected',
    // Brain
    crystal_formed: 'Crystal Formed',
    memory_surfaced: 'Memory Surfaced',
    vault_imported: 'Vault Imported',
    // Gardener
    session_started: 'Session Started',
    session_complete: 'Session Complete',
    artifact_created: 'Artifact Created',
    learning_recorded: 'Learning Recorded',
    season_changed: 'Season Changed',
    gesture_applied: 'Gesture Applied',
    plot_progress_updated: 'Progress Updated',
    // Atelier
    piece_created: 'Piece Created',
    bid_accepted: 'Bid Accepted',
    // Coalition
    coalition_formed: 'Coalition Formed',
    task_assigned: 'Task Complete',
    // Domain
    drill_started: 'Drill Started',
    drill_complete: 'Drill Complete',
    timer_warning: 'Timer Warning',
    timer_critical: 'Timer Critical',
    timer_expired: 'Timer Expired',
    // Park
    scenario_started: 'Scenario Started',
    scenario_complete: 'Scenario Complete',
    serendipity_injected: 'Serendipity!',
    consent_debt_high: 'High Consent Debt',
    force_used: 'Force Used',
    // D-gent
    data_stored: 'Data Stored',
    data_deleted: 'Data Deleted',
    data_upgraded: 'Data Upgraded',
    data_degraded: 'Data Degraded',
  };
  return titles[eventType] || 'Event';
}

/**
 * Helper to create and show a synergy toast.
 */
export function showSynergyToast(
  sourceJewel: Jewel,
  targetJewel: Jewel | '*',
  eventType: SynergyEventType,
  description?: string,
  action?: { label: string; href: string },
): void {
  useSynergyToastStore.getState().addToast({
    type: getToastType(eventType),
    sourceJewel,
    targetJewel,
    eventType,
    title: getToastTitle(eventType),
    description,
    action,
  });
}

/**
 * Quick helper for common synergy patterns.
 */
export const synergyToast = {
  /** Gestalt → Brain: Architecture captured */
  gestaltToBrain: (modulePath: string, healthGrade: string) => {
    showSynergyToast(
      'gestalt',
      'brain',
      'analysis_complete',
      `${modulePath} health: ${healthGrade}`,
      { label: 'View Crystal', href: '/brain' },
    );
  },

  /** Brain: New crystal formed */
  crystalFormed: (title: string) => {
    showSynergyToast('brain', '*', 'crystal_formed', `"${title}"`, {
      label: 'View',
      href: '/brain',
    });
  },

  /** Gardener: Session complete */
  sessionComplete: (sessionName: string, artifactCount: number) => {
    showSynergyToast(
      'gardener',
      'brain',
      'session_complete',
      `${sessionName}: ${artifactCount} artifacts`,
      { label: 'View Learnings', href: '/brain' },
    );
  },

  /** Atelier → Brain: Piece created */
  pieceCreated: (title: string) => {
    showSynergyToast('forge', 'brain', 'piece_created', `"${title}"`, {
      label: 'View Crystal',
      href: '/brain',
    });
  },

  /** Coalition → Brain: Task complete */
  taskComplete: (coalitionSize: number, duration: string) => {
    showSynergyToast(
      'coalition',
      'brain',
      'task_assigned',
      `${coalitionSize} agents, ${duration}`,
      { label: 'View Crystal', href: '/brain' },
    );
  },

  /** Park → Brain: Scenario complete */
  scenarioComplete: (scenarioName: string, forcesUsed: number) => {
    showSynergyToast(
      'park',
      'brain',
      'scenario_complete',
      `${scenarioName} (${forcesUsed} forces used)`,
      { label: 'View Crystal', href: '/brain' },
    );
  },

  /** Domain → Brain: Drill complete */
  drillComplete: (drillName: string, grade: string) => {
    showSynergyToast('domain', 'brain', 'drill_complete', `${drillName}: Grade ${grade}`, {
      label: 'View Report',
      href: '/brain',
    });
  },

  /** Garden: Season changed */
  seasonChanged: (newSeason: string) => {
    showSynergyToast('gardener', '*', 'season_changed', `Garden entering ${newSeason}`, {
      label: 'View Garden',
      href: '/garden',
    });
  },

  /** Warning: Drift detected */
  driftDetected: (modulePath: string, violationCount: number) => {
    showSynergyToast(
      'gestalt',
      '*',
      'drift_detected',
      `${modulePath}: ${violationCount} violations`,
      { label: 'View Details', href: '/gestalt' },
    );
  },

  /** Warning: Timer approaching */
  timerWarning: (timerName: string, remainingSeconds: number) => {
    const mins = Math.ceil(remainingSeconds / 60);
    showSynergyToast('domain', '*', 'timer_warning', `${timerName}: ${mins}m remaining`);
  },

  /** Park: Serendipity injection */
  serendipityInjected: (description: string) => {
    showSynergyToast('park', '*', 'serendipity_injected', description);
  },
};
