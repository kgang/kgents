/**
 * useOnlineStatus: Track browser online/offline status.
 *
 * Shows toast notifications when connectivity changes.
 * Useful for graceful degradation when network is unavailable.
 *
 * @see plans/web-refactor/defensive-lifecycle.md
 */

import { useState, useEffect } from 'react';
import { showInfo, showError } from '@/stores/uiStore';

/**
 * Track browser online/offline status.
 *
 * Shows toast notifications on connectivity changes.
 *
 * @returns {boolean} Current online status
 *
 * @example
 * ```tsx
 * function Layout() {
 *   const isOnline = useOnlineStatus();
 *
 *   return (
 *     <div>
 *       {!isOnline && <OfflineBanner />}
 *       <main>{children}</main>
 *     </div>
 *   );
 * }
 * ```
 */
export function useOnlineStatus(): boolean {
  const [isOnline, setIsOnline] = useState(() =>
    typeof navigator !== 'undefined' ? navigator.onLine : true
  );

  useEffect(() => {
    const handleOnline = () => {
      setIsOnline(true);
      showInfo('Back Online', 'Connection restored');
    };

    const handleOffline = () => {
      setIsOnline(false);
      showError('Offline', 'Check your internet connection');
    };

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  return isOnline;
}

export default useOnlineStatus;
