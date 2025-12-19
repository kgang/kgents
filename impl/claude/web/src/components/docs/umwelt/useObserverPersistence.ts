/**
 * useObserverPersistence - Persist observer choice across page refreshes
 *
 * "The noun is a lie. There is only the rate of change."
 *
 * This hook persists the current observer to sessionStorage, so users
 * don't lose their selected perspective on page refresh.
 *
 * Features:
 * - Version-aware storage for graceful migration
 * - Corrupted storage recovery
 * - Session-scoped (per-tab) persistence
 *
 * @see plans/umwelt-v2-expansion.md (1C. Observer Session Persistence)
 */

import { useState, useCallback } from 'react';
import type { Observer } from '../ObserverPicker';

// =============================================================================
// Constants
// =============================================================================

const STORAGE_KEY = 'umwelt:observer';
const STORAGE_VERSION = 1;

// =============================================================================
// Types
// =============================================================================

interface StoredObserver {
  version: number;
  observer: Observer;
  timestamp: number;
}

// =============================================================================
// Hook
// =============================================================================

/**
 * Hook for persisting observer state to sessionStorage.
 *
 * @param defaultObserver - Default observer if no stored value
 * @returns [observer, setObserver] tuple
 *
 * @example
 * ```tsx
 * const [observer, setObserver] = useObserverPersistence({
 *   archetype: 'developer',
 *   capabilities: ['read', 'write'],
 * });
 * ```
 */
export function useObserverPersistence(
  defaultObserver: Observer
): readonly [Observer, (o: Observer) => void] {
  const [observer, setObserverState] = useState<Observer>(() => {
    // Try to restore from sessionStorage
    try {
      const stored = sessionStorage.getItem(STORAGE_KEY);
      if (stored) {
        const parsed: StoredObserver = JSON.parse(stored);

        // Version migration check
        if (parsed.version === STORAGE_VERSION) {
          // Validate the stored observer has required fields
          if (parsed.observer?.archetype && Array.isArray(parsed.observer?.capabilities)) {
            return parsed.observer;
          }
        }

        // Version mismatch or invalid data: clear and use default
        sessionStorage.removeItem(STORAGE_KEY);
      }
    } catch {
      // Corrupted storage: clear and use default
      try {
        sessionStorage.removeItem(STORAGE_KEY);
      } catch {
        // sessionStorage not available (SSR, etc.)
      }
    }

    return defaultObserver;
  });

  const setObserver = useCallback((newObserver: Observer) => {
    setObserverState(newObserver);

    // Persist to sessionStorage
    try {
      const toStore: StoredObserver = {
        version: STORAGE_VERSION,
        observer: newObserver,
        timestamp: Date.now(),
      };
      sessionStorage.setItem(STORAGE_KEY, JSON.stringify(toStore));
    } catch {
      // sessionStorage not available or quota exceeded
      // Silent failure - persistence is nice-to-have
    }
  }, []);

  return [observer, setObserver] as const;
}

/**
 * Clear the stored observer (useful for "Reset to default" action).
 */
export function clearStoredObserver(): void {
  try {
    sessionStorage.removeItem(STORAGE_KEY);
  } catch {
    // Ignore
  }
}

export default useObserverPersistence;
