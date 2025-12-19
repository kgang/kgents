/**
 * Synergy Toast Types
 *
 * Cross-jewel notification system for visible synergy events.
 * Foundation 4 of the Enlightened Crown strategy - make synergies visible.
 */

/**
 * Crown Jewel identifiers.
 * Must match the Python Jewel enum in protocols/synergy/events.py
 */
export type Jewel =
  | 'brain'
  | 'gestalt'
  | 'gardener'
  | 'forge'
  | 'coalition'
  | 'park'
  | 'domain'
  | 'dgent';

/**
 * Known synergy event types.
 * Each event type represents a significant jewel operation
 * that other jewels might want to respond to.
 */
export type SynergyEventType =
  // Gestalt events
  | 'analysis_complete'
  | 'health_computed'
  | 'drift_detected'
  // Brain events
  | 'crystal_formed'
  | 'memory_surfaced'
  | 'vault_imported'
  // Gardener events
  | 'session_started'
  | 'session_complete'
  | 'artifact_created'
  | 'learning_recorded'
  | 'season_changed'
  | 'gesture_applied'
  | 'plot_progress_updated'
  // Forge events
  | 'piece_created'
  | 'bid_accepted'
  // Coalition events
  | 'coalition_formed'
  | 'task_assigned'
  // Domain events
  | 'drill_started'
  | 'drill_complete'
  | 'timer_warning'
  | 'timer_critical'
  | 'timer_expired'
  // Park events
  | 'scenario_started'
  | 'scenario_complete'
  | 'serendipity_injected'
  | 'consent_debt_high'
  | 'force_used'
  // D-gent events (Data layer)
  | 'data_stored'
  | 'data_deleted'
  | 'data_upgraded'
  | 'data_degraded';

/**
 * Synergy event payload from API.
 */
export interface SynergyEvent {
  source_jewel: Jewel;
  target_jewel: Jewel | '*';
  event_type: SynergyEventType;
  source_id: string;
  payload: Record<string, unknown>;
  timestamp: string;
  correlation_id: string;
}

/**
 * Result of handling a synergy event.
 */
export interface SynergyResult {
  success: boolean;
  handler_name: string;
  message: string;
  artifact_id?: string;
  metadata?: Record<string, unknown>;
}

/**
 * Toast type for styling purposes.
 */
export type SynergyToastType = 'success' | 'info' | 'warning' | 'error';

/**
 * Synergy toast notification.
 */
export interface SynergyToast {
  id: string;
  type: SynergyToastType;
  sourceJewel: Jewel;
  targetJewel: Jewel | '*';
  eventType: SynergyEventType;
  title: string;
  description?: string;
  action?: {
    label: string;
    href: string;
  };
  createdAt: Date;
  duration?: number; // ms, default 5000
}

/**
 * Jewel metadata for display.
 */
export interface JewelInfo {
  name: string;
  icon: string;
  color: string;
  bgColor: string;
  borderColor: string;
  path: string;
}

/**
 * Map of jewel identifiers to display info.
 * AGENTESE paths: The URL IS the AGENTESE path.
 */
export const JEWEL_INFO: Record<Jewel, JewelInfo> = {
  brain: {
    name: 'Brain',
    icon: '🧠',
    color: 'text-purple-400',
    bgColor: 'bg-purple-500/10',
    borderColor: 'border-purple-500/30',
    path: '/self.memory',
  },
  gestalt: {
    name: 'Gestalt',
    icon: '🔮',
    color: 'text-blue-400',
    bgColor: 'bg-blue-500/10',
    borderColor: 'border-blue-500/30',
    path: '/world.codebase',
  },
  gardener: {
    name: 'Gardener',
    icon: '🌱',
    color: 'text-green-400',
    bgColor: 'bg-green-500/10',
    borderColor: 'border-green-500/30',
    path: '/concept.gardener',
  },
  forge: {
    name: 'Forge',
    icon: '🎨',
    color: 'text-amber-400',
    bgColor: 'bg-amber-500/10',
    borderColor: 'border-amber-500/30',
    path: '/world.forge',
  },
  coalition: {
    name: 'Coalition',
    icon: '🤝',
    color: 'text-cyan-400',
    bgColor: 'bg-cyan-500/10',
    borderColor: 'border-cyan-500/30',
    path: '/world.town',
  },
  park: {
    name: 'Park',
    icon: '🎭',
    color: 'text-pink-400',
    bgColor: 'bg-pink-500/10',
    borderColor: 'border-pink-500/30',
    path: '/world.park',
  },
  domain: {
    name: 'Domain',
    icon: '🏛️',
    color: 'text-orange-400',
    bgColor: 'bg-orange-500/10',
    borderColor: 'border-orange-500/30',
    path: '/world.domain',
  },
  dgent: {
    name: 'D-gent',
    icon: '💾',
    color: 'text-slate-400',
    bgColor: 'bg-slate-500/10',
    borderColor: 'border-slate-500/30',
    path: '/self.memory', // D-gent accessed via Brain for now
  },
};
