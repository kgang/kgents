/**
 * AppShell — The cathedral navigation experience
 *
 * Wraps all surfaces with:
 * - Top navbar for surface switching (Editor, Docs, Chart, Feed)
 * - Bottom WitnessFooter (always-on compact stream)
 * - CommandPalette (Ctrl+K universal gateway)
 *
 * "Stop documenting agents. Become the agent."
 */

import { ReactNode, useCallback } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';

import { useRouteAwareModeReset } from '@/hooks/useRouteAwareModeReset';
import { WitnessFooter } from './WitnessFooter';
import { CommandPalette } from '@/components/navigation/CommandPalette';

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

/**
 * Navigation items.
 *
 * UX Simplification (2025-12-25):
 * "The Hypergraph Editor IS the app."
 *
 * Chat and Files are sidebars toggled with Ctrl+J / Ctrl+B, not separate routes.
 * Top-level pages: Editor (main), Studio (workspace), Feed (truth stream), Genesis (FTUE demo).
 *
 * STARK BIOME aesthetic: Subtle glyphs, minimal labels, not flashy.
 */
const NAV_ITEMS: NavItem[] = [
  { path: '/world.document', label: 'Editor', shortcut: 'E', icon: '⎔' },
  { path: '/studio', label: 'Studio', shortcut: 'S', icon: '⊞' },
  { path: '/self.feed', label: 'Feed', shortcut: 'F', icon: '≡' },
  { path: '/genesis/showcase', label: 'Genesis', shortcut: 'G', icon: '✦' },
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

  // Reset mode to NORMAL on route changes
  useRouteAwareModeReset();

  // Determine active surface
  const activePath = NAV_ITEMS.find((item) => location.pathname.startsWith(item.path))?.path;

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

        {/* Right side: sidebar toggles + help */}
        <div className="app-shell__actions">
          <span className="app-shell__sidebar-hints">
            <kbd>Ctrl+K</kbd> Commands
            <kbd>Ctrl+B</kbd> Files
            <kbd>Ctrl+J</kbd> Chat
          </span>
          <button
            className="app-shell__help"
            title="Keyboard shortcuts"
            onClick={() => {
              console.info(
                'Shortcuts: Ctrl+K: Command Palette | Ctrl+B: Toggle Files sidebar | Ctrl+J: Toggle Chat sidebar | Shift+E: Editor'
              );
            }}
          >
            <kbd>?</kbd>
          </button>
        </div>
      </nav>

      {/* Main content area */}
      <main className="app-shell__content">{children}</main>

      {/* Always-on witness footer */}
      <WitnessFooter />

      {/* Command Palette (Ctrl+K) */}
      <CommandPalette />
    </div>
  );
}
