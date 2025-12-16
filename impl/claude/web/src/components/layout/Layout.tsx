import { Outlet, Link } from 'react-router-dom';
import { useUserStore } from '@/stores/userStore';
import { UpgradeModal } from '@/components/paywall/UpgradeModal';
import { ToastContainer } from '@/components/feedback/ToastContainer';
import { useOnlineStatus } from '@/hooks/useOnlineStatus';

export function Layout() {
  const { isAuthenticated, tier, credits, logout } = useUserStore();

  // Track online status (shows toasts on connectivity changes)
  useOnlineStatus();

  return (
    <div className="min-h-screen bg-town-bg flex flex-col">
      {/* Header */}
      <header className="border-b border-town-accent/30 bg-town-surface/50 backdrop-blur-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 py-3 flex items-center justify-between">
          <Link to="/" className="flex items-center gap-2 hover:opacity-80 transition-opacity">
            <span className="text-2xl">🏘️</span>
            <span className="font-semibold text-lg">Agent Town</span>
          </Link>

          <nav className="flex items-center gap-6">
            {isAuthenticated ? (
              <>
                <Link
                  to="/dashboard"
                  className="text-gray-300 hover:text-white transition-colors"
                >
                  Dashboard
                </Link>
                <div className="flex items-center gap-4">
                  <span className="px-3 py-1 bg-town-accent/30 rounded-full text-sm">
                    {tier}
                  </span>
                  <span className="text-sm text-gray-400">
                    {credits} credits
                  </span>
                  <button
                    onClick={logout}
                    className="text-gray-400 hover:text-white text-sm transition-colors"
                  >
                    Logout
                  </button>
                </div>
              </>
            ) : (
              <Link
                to="/"
                className="px-4 py-2 bg-town-highlight hover:bg-town-highlight/80 rounded-lg font-medium transition-colors"
              >
                Get Started
              </Link>
            )}
          </nav>
        </div>
      </header>

      {/* Main content */}
      <main className="flex-1">
        <Outlet />
      </main>

      {/* Footer */}
      <footer className="border-t border-town-accent/30 bg-town-surface/30 py-4">
        <div className="max-w-7xl mx-auto px-4 text-center text-sm text-gray-500">
          <p>Agent Town - Civilizations that dream</p>
        </div>
      </footer>

      {/* Global Modals */}
      <UpgradeModal />

      {/* Toast Notifications */}
      <ToastContainer />
    </div>
  );
}
