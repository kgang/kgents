/**
 * useRouteAwareModeReset: Reset mode to NORMAL on route changes
 *
 * This ensures users always start fresh in NORMAL mode when navigating
 * between pages, preventing mode state from persisting unexpectedly.
 *
 * @example
 * ```tsx
 * function MyPage() {
 *   useRouteAwareModeReset();
 *   return <div>...</div>;
 * }
 * ```
 */

import { useEffect, useRef } from 'react';
import { useLocation } from 'react-router-dom';
import { useModeContextSafe } from '@/context/ModeContext';

/**
 * Reset mode to NORMAL whenever the route changes.
 *
 * Safe to use anywhere—gracefully handles missing ModeProvider.
 */
export function useRouteAwareModeReset(): void {
  const location = useLocation();
  const modeContext = useModeContextSafe();
  const previousPathRef = useRef(location.pathname);

  useEffect(() => {
    // Skip if mode context isn't available (outside ModeProvider)
    if (!modeContext) return;

    // Skip if this is the initial mount (same path)
    if (previousPathRef.current === location.pathname) return;

    // Route changed - reset to NORMAL
    const { currentMode, setMode } = modeContext;
    if (currentMode !== 'NORMAL') {
      setMode('NORMAL', 'route-change');
    }

    // Update ref for next comparison
    previousPathRef.current = location.pathname;
  }, [location.pathname, modeContext]);
}

export default useRouteAwareModeReset;
