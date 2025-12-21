/**
 * Shell - Unified Layout Wrapper
 *
 * The Shell transforms the web interface into an "operating system for autopoiesis"
 * with three persistent layers:
 * 1. Observer Drawer (top) - Who is looking / trace visibility
 * 2. Navigation Tree (sidebar) - AGENTESE-discovered paths
 * 3. Terminal (bottom) - AGENTESE CLI
 *
 * This replaces the previous Layout.tsx component.
 *
 * @see spec/protocols/os-shell.md
 *
 * @example
 * ```tsx
 * // In App.tsx
 * <Route element={<Shell />}>
 *   <Route path="/" element={<Crown />} />
 *   ...
 * </Route>
 * ```
 */

import { useState, useCallback } from 'react';
import { Outlet, Link, useLocation } from 'react-router-dom';
import { Menu } from 'lucide-react';
import { ShellProvider, useShell } from './ShellProvider';
import { ObserverDrawer } from './ObserverDrawer';
import { NavigationTree } from './NavigationTree';
import { Terminal } from './Terminal';
import { KeyboardHints } from './KeyboardHints';
import { CommandPalette } from './CommandPalette';
import { PathSearch } from './PathSearch';
import { ObserverDebugPanel } from '../components/dev';
import { useKeyboardShortcuts } from './useKeyboardShortcuts';
import {
  ObserverErrorBoundary,
  NavigationErrorBoundary,
  TerminalErrorBoundary,
  ProjectionErrorBoundary,
} from './ShellErrorBoundary';
import { JEWEL_ICONS, JEWEL_COLORS, type JewelName } from '@/constants/jewels';

// =============================================================================
// Types
// =============================================================================

interface ShellLayoutProps {
  /** Show the footer */
  showFooter?: boolean;
}

// =============================================================================
// Crown Context Component (from old Layout)
// =============================================================================

/**
 * Crown context indicator for the header.
 * Shows the current jewel focus based on route.
 */
function CrownContext() {
  const location = useLocation();

  // Determine active jewel from AGENTESE path
  const getActiveJewel = (): JewelName | null => {
    const path = location.pathname;
    // AGENTESE paths: context.holon.aspect
    if (path.startsWith('/self.memory')) return 'brain';
    if (path.startsWith('/world.codebase')) return 'gestalt';
    if (path.startsWith('/world.forge')) return 'forge';
    if (path.startsWith('/world.town')) return 'coalition';
    if (path.startsWith('/world.park')) return 'park';
    if (path.startsWith('/world.domain')) return 'domain';
    if (path.startsWith('/time.differance')) return 'gestalt'; // Différance related to visualization
    return null;
  };

  const activeJewel = getActiveJewel();

  if (!activeJewel) {
    return (
      <div className="flex items-center gap-2 text-sm text-gray-400">
        <span>Crown Jewels</span>
      </div>
    );
  }

  const Icon = JEWEL_ICONS[activeJewel];
  const colors = JEWEL_COLORS[activeJewel];

  return (
    <div className="flex items-center gap-2">
      <Icon className="w-4 h-4" style={{ color: colors.primary }} />
      <span className="text-sm font-medium capitalize" style={{ color: colors.primary }}>
        {activeJewel}
      </span>
    </div>
  );
}

// =============================================================================
// Navigation Header (Compact mode)
// =============================================================================

/**
 * Quick navigation for jewels - visible in compact/comfortable density.
 */
function QuickNav() {
  const location = useLocation();
  const { density } = useShell();

  // AGENTESE paths for jewels
  const jewels: Array<{ name: JewelName; route: string }> = [
    { name: 'brain', route: '/self.memory' },
    { name: 'gestalt', route: '/world.codebase' },
    { name: 'forge', route: '/world.forge' },
    { name: 'coalition', route: '/world.town' },
    { name: 'park', route: '/world.park' },
  ];

  // In spacious mode, navigation is in sidebar
  if (density === 'spacious') {
    return null;
  }

  return (
    <nav className="flex items-center gap-1 overflow-x-auto px-2 py-1 bg-gray-800/50 border-b border-gray-700/50">
      {jewels.map((jewel) => {
        const Icon = JEWEL_ICONS[jewel.name];
        const colors = JEWEL_COLORS[jewel.name];
        const isActive = location.pathname.startsWith(jewel.route);

        return (
          <Link
            key={jewel.name}
            to={jewel.route}
            className={`
              flex items-center gap-1.5 px-2 py-1 rounded text-xs
              transition-colors
              ${isActive ? 'bg-gray-700/70' : 'hover:bg-gray-700/50'}
            `}
          >
            <Icon
              className="w-4 h-4"
              style={{ color: isActive ? colors.primary : 'rgb(156, 163, 175)' }}
            />
            {density === 'comfortable' && (
              <span style={{ color: isActive ? colors.primary : 'rgb(156, 163, 175)' }}>
                {jewel.name.charAt(0).toUpperCase() + jewel.name.slice(1)}
              </span>
            )}
          </Link>
        );
      })}
    </nav>
  );
}

// =============================================================================
// Shell Layout Inner (wrapped by provider)
// =============================================================================

function ShellLayoutInner({ showFooter = false }: ShellLayoutProps) {
  const {
    density,
    observerHeight,
    terminalHeight,
    navigationWidth,
    navigationTreeExpanded,
    setNavigationTreeExpanded,
    observerDrawerExpanded,
    setObserverDrawerExpanded,
    terminalExpanded,
    setTerminalExpanded,
    isAnimating,
  } = useShell();

  // Keyboard overlay states
  const [keyboardHintsOpen, setKeyboardHintsOpen] = useState(false);
  const [commandPaletteOpen, setCommandPaletteOpen] = useState(false);
  const [pathSearchOpen, setPathSearchOpen] = useState(false);

  // Keyboard shortcut handlers
  const handleCloseAllPanels = useCallback(() => {
    // Close in order of priority: path search > command palette > keyboard hints > panels
    if (pathSearchOpen) {
      setPathSearchOpen(false);
      return;
    }
    if (commandPaletteOpen) {
      setCommandPaletteOpen(false);
      return;
    }
    if (keyboardHintsOpen) {
      setKeyboardHintsOpen(false);
      return;
    }
    // Close expanded panels
    if (observerDrawerExpanded) setObserverDrawerExpanded(false);
    if (navigationTreeExpanded) setNavigationTreeExpanded(false);
    if (terminalExpanded) setTerminalExpanded(false);
  }, [
    pathSearchOpen,
    commandPaletteOpen,
    keyboardHintsOpen,
    observerDrawerExpanded,
    navigationTreeExpanded,
    terminalExpanded,
    setObserverDrawerExpanded,
    setNavigationTreeExpanded,
    setTerminalExpanded,
  ]);

  const handleFocusTerminal = useCallback(() => {
    setTerminalExpanded(true);
    // Dispatch event to focus terminal input
    setTimeout(() => {
      document.dispatchEvent(new CustomEvent('shell:focus-terminal'));
    }, 100);
  }, [setTerminalExpanded]);

  const handleToggleTerminal = useCallback(() => {
    setTerminalExpanded(!terminalExpanded);
  }, [terminalExpanded, setTerminalExpanded]);

  const handleToggleNavTree = useCallback(() => {
    setNavigationTreeExpanded(!navigationTreeExpanded);
  }, [navigationTreeExpanded, setNavigationTreeExpanded]);

  const handleToggleObserver = useCallback(() => {
    setObserverDrawerExpanded(!observerDrawerExpanded);
  }, [observerDrawerExpanded, setObserverDrawerExpanded]);

  const handleTerminalCommand = useCallback(
    (command: string) => {
      setTerminalExpanded(true);
      // Dispatch event to run command in terminal
      setTimeout(() => {
        document.dispatchEvent(new CustomEvent('shell:terminal-command', { detail: { command } }));
      }, 100);
    },
    [setTerminalExpanded]
  );

  // Register keyboard shortcuts
  const { shortcuts } = useKeyboardShortcuts({
    onCloseAllPanels: handleCloseAllPanels,
    onFocusTerminal: handleFocusTerminal,
    onToggleTerminal: handleToggleTerminal,
    onToggleNavTree: handleToggleNavTree,
    onToggleObserver: handleToggleObserver,
    onOpenCommandPalette: () => setCommandPaletteOpen(true),
    onShowKeyboardHints: () => setKeyboardHintsOpen(true),
    onOpenPathSearch: () => setPathSearchOpen(true),
  });

  // Main content positioning uses animated offsets for smooth coordination
  // When observer collapses: main slides up
  // When terminal expands: main shrinks from bottom
  // When navigation expands: main slides right
  //
  // Mobile layout fixed elements:
  // Mobile layout constants
  // - ObserverDrawer: 40px (collapsed)
  // - Header: ~44px (py-2 + content)
  // Total: ~84px top offset needed
  const MOBILE_HEADER_HEIGHT = 44;

  return (
    <div className="h-screen bg-gray-900 flex flex-col relative overflow-hidden">
      {/* Observer Drawer - Always present at top */}
      <ObserverErrorBoundary>
        <ObserverDrawer />
      </ObserverErrorBoundary>

      {/* Header with logo (compact/comfortable) */}
      {density !== 'spacious' && (
        <header
          className="bg-gray-800/80 backdrop-blur-sm border-b border-gray-700/50 px-4 py-2 flex items-center justify-between fixed left-0 right-0 z-20"
          style={{ top: `${observerHeight}px` }}
        >
          <div className="flex items-center gap-3">
            {/* Hamburger menu for compact density */}
            {density === 'compact' && (
              <button
                type="button"
                onClick={() => setNavigationTreeExpanded(true)}
                className="p-2 hover:bg-gray-700/50 rounded transition-colors"
                aria-label="Open navigation"
              >
                <Menu className="w-6 h-6 text-gray-300" />
              </button>
            )}
            <Link to="/" className="flex items-center gap-2 hover:opacity-80 transition-opacity">
              <span className="font-semibold text-lg text-white">kgents</span>
            </Link>
          </div>
          <CrownContext />
        </header>
      )}

      {/* Quick nav for compact/comfortable */}
      <QuickNav />

      {/* Main layout area - Navigation floats over this */}
      <div className="flex-1 min-h-0 flex flex-col overflow-hidden relative">
        {/* Navigation Tree - Floating overlay sidebar */}
        <NavigationErrorBoundary>
          <NavigationTree />
        </NavigationErrorBoundary>

        {/* Content Canvas - flex child that fills available space */}
        <main
          className="flex-1 min-h-0 flex flex-col"
          style={{
            marginTop: density !== 'compact' ? `${observerHeight}px` : undefined,
            marginLeft: density !== 'compact' && navigationTreeExpanded ? `${navigationWidth}px` : 0,
            marginBottom: density !== 'compact' ? `${terminalHeight}px` : undefined,
            paddingTop: density === 'compact' ? `${observerHeight + MOBILE_HEADER_HEIGHT}px` : undefined,
            paddingBottom: density === 'compact' ? '5rem' : undefined,
            transition: isAnimating ? 'none' : 'margin 0.25s cubic-bezier(0.4, 0, 0.2, 1)',
          }}
        >
          <ProjectionErrorBoundary>
            <Outlet />
          </ProjectionErrorBoundary>
        </main>
      </div>

      {/* Terminal - In document flow at bottom */}
      <TerminalErrorBoundary>
        <Terminal />
      </TerminalErrorBoundary>

      {/* Optional Footer */}
      {showFooter && (
        <footer className="border-t border-gray-700/50 bg-gray-800/30 py-3 px-4 text-center text-xs text-gray-500">
          kgents - Tasteful, curated, ethical, joy-inducing agents
        </footer>
      )}

      {/* Keyboard Shortcuts Overlay */}
      <KeyboardHints
        isOpen={keyboardHintsOpen}
        onClose={() => setKeyboardHintsOpen(false)}
        shortcuts={shortcuts}
      />

      {/* Command Palette */}
      <CommandPalette
        isOpen={commandPaletteOpen}
        onClose={() => setCommandPaletteOpen(false)}
        onTerminalCommand={handleTerminalCommand}
      />

      {/* Path Search (press / to open) */}
      <PathSearch isOpen={pathSearchOpen} onClose={() => setPathSearchOpen(false)} />

      {/* Observer Debug Panel - Phase 8: Toggle with Ctrl+Shift+O */}
      <ObserverDebugPanel />
    </div>
  );
}

// =============================================================================
// Shell Component (with Provider)
// =============================================================================

/**
 * Shell - The unified OS-like layout wrapper.
 *
 * Wraps content in ShellProvider and provides the three persistent layers:
 * - ObserverDrawer (top)
 * - NavigationTree (sidebar)
 * - Terminal (bottom)
 *
 * @example
 * ```tsx
 * <Route element={<Shell />}>
 *   <Route path="/brain" element={<Brain />} />
 * </Route>
 * ```
 */
export function Shell(props: ShellLayoutProps = {}) {
  return (
    <ShellProvider>
      <ShellLayoutInner {...props} />
    </ShellProvider>
  );
}

export default Shell;
