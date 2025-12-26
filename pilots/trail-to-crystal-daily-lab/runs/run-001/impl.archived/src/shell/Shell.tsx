/**
 * Shell
 *
 * Main application shell with header, sidebar, footer, and content area.
 * Responsive design with collapsible sidebar and mobile hamburger menu.
 */

import { Outlet, Link, useLocation } from 'react-router-dom';
import { useState, useEffect } from 'react';
import { useTheme } from './ThemeProvider';
import { useLayout } from './LayoutProvider';

// =============================================================================
// Version
// =============================================================================

const VERSION = '0.1.0';

// =============================================================================
// Pilot Info (for breadcrumb)
// =============================================================================

interface PilotInfo {
  name: string;
  path: string;
}

const PILOT_MAP: Record<string, PilotInfo> = {
  'daily-lab': { name: 'Daily Lab', path: '/daily-lab' },
};

// =============================================================================
// Shell Component
// =============================================================================

export function Shell() {
  const { mode, toggleMode } = useTheme();
  const { isMobile, sidebarCollapsed, toggleSidebar } = useLayout();
  const location = useLocation();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  // Get current pilot for breadcrumb
  const currentPilot = Object.entries(PILOT_MAP).find(
    ([key]) => location.pathname.startsWith(`/${key}`)
  );

  // Close mobile menu on route change
  useEffect(() => {
    setMobileMenuOpen(false);
  }, [location.pathname]);

  // Close mobile menu on escape key
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        setMobileMenuOpen(false);
      }
    };
    window.addEventListener('keydown', handleEscape);
    return () => window.removeEventListener('keydown', handleEscape);
  }, []);

  return (
    <div className="min-h-screen bg-bark flex flex-col">
      {/* Header */}
      <header className="border-b border-sage/20 px-4 md:px-6 py-3 md:py-4 sticky top-0 bg-bark/95 backdrop-blur-sm z-40">
        <nav className="flex items-center justify-between max-w-7xl mx-auto">
          {/* Left section: Menu + Logo + Breadcrumb */}
          <div className="flex items-center gap-3">
            {/* Hamburger menu (mobile) or Sidebar toggle (desktop) */}
            <button
              onClick={isMobile ? () => setMobileMenuOpen(!mobileMenuOpen) : toggleSidebar}
              className="p-2 rounded-lg text-sand hover:text-lantern hover:bg-sage/10 transition-colors focus:outline-none focus:ring-2 focus:ring-sage/40"
              aria-label={isMobile ? 'Toggle menu' : 'Toggle sidebar'}
            >
              <HamburgerIcon className="w-5 h-5" />
            </button>

            {/* Logo */}
            <Link
              to="/"
              className="text-lantern font-semibold text-lg hover:text-sage transition-colors duration-200"
            >
              kgents pilots
            </Link>

            {/* Breadcrumb separator + current pilot */}
            {currentPilot && (
              <>
                <ChevronIcon className="w-4 h-4 text-clay" />
                <Link
                  to={currentPilot[1].path}
                  className="text-sand hover:text-lantern transition-colors duration-200"
                >
                  {currentPilot[1].name}
                </Link>
              </>
            )}
          </div>

          {/* Right section: Theme toggle + tagline */}
          <div className="flex items-center gap-4">
            <span className="hidden md:block text-sand text-sm italic">
              "Turn your day into proof of intention"
            </span>
            <button
              onClick={toggleMode}
              className="p-2 rounded-lg text-sand hover:text-lantern hover:bg-sage/10 transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-sage/40"
              aria-label={`Switch to ${mode === 'dark' ? 'light' : 'dark'} mode`}
            >
              {mode === 'dark' ? (
                <SunIcon className="w-5 h-5" />
              ) : (
                <MoonIcon className="w-5 h-5" />
              )}
            </button>
          </div>
        </nav>
      </header>

      {/* Main content area with optional sidebar */}
      <div className="flex-1 flex overflow-hidden">
        {/* Sidebar (desktop) */}
        {!isMobile && !sidebarCollapsed && (
          <aside className="w-64 border-r border-sage/20 bg-bark/50 flex-shrink-0 overflow-y-auto transition-all duration-300">
            <SidebarContent onNavigate={() => {}} />
          </aside>
        )}

        {/* Mobile menu overlay */}
        {isMobile && mobileMenuOpen && (
          <>
            {/* Backdrop */}
            <div
              className="fixed inset-0 bg-bark/80 backdrop-blur-sm z-40 transition-opacity duration-200"
              onClick={() => setMobileMenuOpen(false)}
            />
            {/* Slide-in menu */}
            <aside className="fixed left-0 top-0 bottom-0 w-72 bg-bark border-r border-sage/20 z-50 overflow-y-auto transform transition-transform duration-300">
              <div className="p-4 border-b border-sage/20 flex items-center justify-between">
                <span className="text-lantern font-semibold">Navigation</span>
                <button
                  onClick={() => setMobileMenuOpen(false)}
                  className="p-2 rounded-lg text-sand hover:text-lantern hover:bg-sage/10 transition-colors"
                  aria-label="Close menu"
                >
                  <CloseIcon className="w-5 h-5" />
                </button>
              </div>
              <SidebarContent onNavigate={() => setMobileMenuOpen(false)} />
            </aside>
          </>
        )}

        {/* Main content */}
        <main className="flex-1 overflow-y-auto">
          <div className="max-w-6xl mx-auto px-4 md:px-6 py-6 md:py-8">
            <Outlet />
          </div>
        </main>
      </div>

      {/* Footer */}
      <footer className="border-t border-sage/20 px-4 md:px-6 py-4 bg-bark/50">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-2 text-sm">
          <div className="flex items-center gap-2 text-sand">
            <span>Powered by</span>
            <span className="text-sage font-medium">kgents</span>
          </div>
          <div className="text-clay">
            v{VERSION}
          </div>
        </div>
      </footer>
    </div>
  );
}

// =============================================================================
// Sidebar Content
// =============================================================================

interface SidebarContentProps {
  onNavigate: () => void;
}

function SidebarContent({ onNavigate }: SidebarContentProps) {
  const location = useLocation();

  const navItems = [
    { path: '/', label: 'Home', exact: true },
    { path: '/daily-lab', label: 'Daily Lab', exact: false },
  ];

  return (
    <nav className="p-4 space-y-2">
      <div className="text-xs uppercase tracking-wider text-clay mb-4 px-3">
        Pilots
      </div>
      {navItems.map(({ path, label, exact }) => {
        const isActive = exact
          ? location.pathname === path
          : location.pathname.startsWith(path) && path !== '/';

        return (
          <Link
            key={path}
            to={path}
            onClick={onNavigate}
            className={`
              block px-3 py-2 rounded-lg transition-colors duration-200
              ${isActive
                ? 'bg-sage/20 text-sage'
                : 'text-sand hover:text-lantern hover:bg-sage/10'
              }
            `}
          >
            {label}
          </Link>
        );
      })}
    </nav>
  );
}

// =============================================================================
// Icons
// =============================================================================

function HamburgerIcon({ className }: { className?: string }) {
  return (
    <svg
      className={className}
      fill="none"
      viewBox="0 0 24 24"
      stroke="currentColor"
      strokeWidth={2}
    >
      <path strokeLinecap="round" strokeLinejoin="round" d="M4 6h16M4 12h16M4 18h16" />
    </svg>
  );
}

function CloseIcon({ className }: { className?: string }) {
  return (
    <svg
      className={className}
      fill="none"
      viewBox="0 0 24 24"
      stroke="currentColor"
      strokeWidth={2}
    >
      <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
    </svg>
  );
}

function ChevronIcon({ className }: { className?: string }) {
  return (
    <svg
      className={className}
      fill="none"
      viewBox="0 0 24 24"
      stroke="currentColor"
      strokeWidth={2}
    >
      <path strokeLinecap="round" strokeLinejoin="round" d="M9 5l7 7-7 7" />
    </svg>
  );
}

function SunIcon({ className }: { className?: string }) {
  return (
    <svg
      className={className}
      fill="none"
      viewBox="0 0 24 24"
      stroke="currentColor"
      strokeWidth={2}
    >
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z"
      />
    </svg>
  );
}

function MoonIcon({ className }: { className?: string }) {
  return (
    <svg
      className={className}
      fill="none"
      viewBox="0 0 24 24"
      stroke="currentColor"
      strokeWidth={2}
    >
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z"
      />
    </svg>
  );
}

export default Shell;
