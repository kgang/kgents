/**
 * Barrel exports for Zustand stores.
 *
 * Import stores from this module for cleaner imports:
 * ```ts
 * import { useUIStore, useUserStore, useWorkshopStore, showSuccess } from '@/stores';
 * ```
 */

// UI Store - panels, modals, notifications, loading states
export { useUIStore, showSuccess, showError, showInfo } from './uiStore';

// User Store - auth, subscription, credits
export {
  useUserStore,
  selectCanAfford,
  selectIsLODIncluded,
  selectCanInhabit,
  selectCanForce,
} from './userStore';

// Workshop Store - builders, events, artifacts, replay
export {
  useWorkshopStore,
  selectActiveBuilder,
  selectSelectedBuilderData,
  selectPhaseProgress,
} from './workshopStore';
