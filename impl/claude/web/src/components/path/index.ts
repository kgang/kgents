/**
 * Path Components - Wave 0 Foundations
 *
 * Components for making AGENTESE visible and observer-dependent
 * perception accessible to users.
 *
 * Foundation 1: Path Visibility
 * - PathTrace: Shows the AGENTESE path being invoked
 *
 * Foundation 2: Observer Switching
 * - ObserverSwitcher: Switch between observer perspectives
 * - useObserverState: Hook for managing observer state
 *
 * @see plans/crown-jewels-enlightened.md
 */

export {
  ObserverSwitcher,
  PathTrace,
  useObserverState,
  DEFAULT_OBSERVERS,
  type Observer,
  type ObserverSwitcherProps,
  type PathTraceProps,
} from './ObserverSwitcher';
