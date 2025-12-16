/**
 * ToastContainer: Renders notifications from uiStore.
 *
 * Positioned fixed at bottom-right. Consumes notifications from
 * the global UI store and renders Toast components.
 *
 * @see plans/web-refactor/defensive-lifecycle.md
 * @see src/stores/uiStore.ts
 */

import { useUIStore } from '@/stores/uiStore';
import { Toast } from './Toast';

/**
 * Container for toast notifications.
 *
 * Add to Layout.tsx to enable global notifications.
 *
 * @example
 * ```tsx
 * // In Layout.tsx
 * <Layout>
 *   <main>{children}</main>
 *   <ToastContainer />
 * </Layout>
 *
 * // Anywhere in app
 * import { showSuccess, showError } from '@/stores/uiStore';
 * showSuccess('Done!', 'Your action completed.');
 * showError('Oops!', 'Something went wrong.');
 * ```
 */
export function ToastContainer() {
  const notifications = useUIStore((state) => state.notifications);
  const removeNotification = useUIStore((state) => state.removeNotification);

  // Don't render container if no notifications
  if (notifications.length === 0) {
    return null;
  }

  return (
    <div
      className="fixed bottom-4 right-4 z-50 space-y-2"
      aria-live="polite"
      aria-label="Notifications"
    >
      {notifications.map((notification) => (
        <Toast
          key={notification.id}
          notification={notification}
          onDismiss={() => removeNotification(notification.id)}
        />
      ))}
    </div>
  );
}

export default ToastContainer;
