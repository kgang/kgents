/**
 * Synergy Components - Cross-Jewel Notification System
 *
 * Foundation 4 of the Enlightened Crown strategy.
 * Makes synergies visible so the 7 jewels feel like ONE crown.
 *
 * Usage:
 * ```tsx
 * // In App.tsx, add the toaster
 * import { SynergyToaster } from './components/synergy';
 *
 * function App() {
 *   return (
 *     <>
 *       <Routes>...</Routes>
 *       <SynergyToaster />
 *     </>
 *   );
 * }
 *
 * // In any component, use the hook
 * import { useSynergyToast } from './components/synergy';
 *
 * function GestaltPage() {
 *   const { gestaltToBrain } = useSynergyToast();
 *
 *   const onAnalysisComplete = (path: string, grade: string) => {
 *     gestaltToBrain(path, grade);
 *   };
 * }
 * ```
 */

// Types
export type {
  Jewel,
  SynergyEventType,
  SynergyEvent,
  SynergyResult,
  SynergyToast,
  SynergyToastType,
  JewelInfo,
} from './types';
export { JEWEL_INFO } from './types';

// Components
export { SynergyToaster } from './SynergyToaster';

// Hooks
export { useSynergyToast, type UseSynergyToastReturn } from './useSynergyToast';

// Store (for direct access if needed)
export { useSynergyToastStore, synergyToast, showSynergyToast } from './store';
