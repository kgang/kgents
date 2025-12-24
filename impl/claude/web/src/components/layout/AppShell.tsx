/**
 * AppShell — The cathedral navigation experience
 *
 * Wraps all surfaces with:
 * - Top navbar for surface switching (Editor, Ledger, Chart, Brain)
 * - Bottom WitnessFooter (always-on compact stream)
 *
 * "Stop documenting agents. Become the agent."
 */

import { ReactNode, useCallback, useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';

import { WitnessFooter } from './WitnessFooter';
import { NavigationSidebar, type Surface } from '../navigation';

import './AppShell.css';

// =============================================================================
// Types
// =============================================================================

interface AppShellProps {
  children: ReactNode;
}

interface NavItem {
  path: string;
  label: string;
  shortcut: string;
  icon: string;
}

// =============================================================================
// Constants
// =============================================================================

const NAV_ITEMS: NavItem[] = [
  { path: '/editor', label: 'Editor', shortcut: 'E', icon: '⌨' },
  { path: '/ledger', label: 'Ledger', shortcut: 'L', icon: '📊' },
  { path: '/chart', label: 'Chart', shortcut: 'C', icon: '✦' },
  { path: '/brain', label: 'Brain', shortcut: 'B', icon: '🧠' },
];

// =============================================================================
// NavLink Component
// =============================================================================

interface NavLinkProps {
  item: NavItem;
  isActive: boolean;
}

function NavLink({ item, isActive }: NavLinkProps) {
  return (
    <Link
      to={item.path}
      className={`app-shell__nav-link ${isActive ? 'app-shell__nav-link--active' : ''}`}
      title={`${item.label} (${item.shortcut})`}
    >
      <span className="app-shell__nav-icon">{item.icon}</span>
      <span className="app-shell__nav-label">{item.label}</span>
      <kbd className="app-shell__nav-shortcut">{item.shortcut}</kbd>
    </Link>
  );
}

// =============================================================================
// Main Component
// =============================================================================

export function AppShell({ children }: AppShellProps) {
  const location = useLocation();
  const navigate = useNavigate();
  const [sidebarExpanded, setSidebarExpanded] = useState(false);

  // Determine active surface
  const activePath = NAV_ITEMS.find((item) => location.pathname.startsWith(item.path))?.path;

  // Map path to surface type
  const getSurface = (): Surface => {
    if (location.pathname.startsWith('/editor')) return 'editor';
    if (location.pathname.startsWith('/ledger')) return 'ledger';
    if (location.pathname.startsWith('/chart')) return 'chart';
    if (location.pathname.startsWith('/brain')) return 'brain';
    return 'editor';
  };

  // Global keyboard shortcuts
  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      // Only handle if not in an input
      if (
        e.target instanceof HTMLInputElement ||
        e.target instanceof HTMLTextAreaElement ||
        (e.target as HTMLElement).isContentEditable
      ) {
        return;
      }

      // Ctrl+b or Cmd+b: Toggle sidebar
      if ((e.ctrlKey || e.metaKey) && e.key === 'b') {
        e.preventDefault();
        setSidebarExpanded((prev) => !prev);
        return;
      }

      // Shift + letter for navigation
      if (e.shiftKey && !e.ctrlKey && !e.metaKey) {
        const key = e.key.toUpperCase();
        const item = NAV_ITEMS.find((i) => i.shortcut === key);
        if (item) {
          e.preventDefault();
          navigate(item.path);
        }
      }
    },
    [navigate]
  );

  return (
    <div className="app-shell" onKeyDown={handleKeyDown} tabIndex={-1}>
      {/* Top Navbar */}
      <nav className="app-shell__navbar">
        {/* Logo / Home */}
        <Link to="/" className="app-shell__logo">
          <span className="app-shell__logo-glyph">◇</span>
          <span className="app-shell__logo-text">kgents</span>
        </Link>

        {/* Navigation links */}
        <div className="app-shell__nav">
          {NAV_ITEMS.map((item) => (
            <NavLink key={item.path} item={item} isActive={activePath === item.path} />
          ))}
        </div>

        {/* Right side: help/settings placeholder */}
        <div className="app-shell__actions">
          <button
            className="app-shell__help"
            title="Keyboard shortcuts"
            onClick={() => {
              console.info(
                'Shortcuts: Shift+E: Editor | Shift+L: Ledger | Shift+C: Chart | Shift+B: Brain'
              );
            }}
          >
            <kbd>?</kbd>
          </button>
        </div>
      </nav>

      {/* Navigation sidebar */}
      <NavigationSidebar
        surface={getSurface()}
        isExpanded={sidebarExpanded}
        onToggle={() => setSidebarExpanded((prev) => !prev)}
        topOffset="48px" /* navbar height */
        bottomOffset="40px" /* witness footer height */
      />

      {/* Main content area */}
      <main className="app-shell__content">{children}</main>

      {/* Always-on witness footer */}
      <WitnessFooter />
    </div>
  );
}
