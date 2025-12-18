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

import { Outlet, Link, useLocation } from 'react-router-dom';
import { Menu } from 'lucide-react';
import { ShellProvider, useShell } from './ShellProvider';
import { ObserverDrawer } from './ObserverDrawer';
import { NavigationTree } from './NavigationTree';
import { Terminal } from './Terminal';
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

  // Determine active jewel from route
  const getActiveJewel = (): JewelName | null => {
    const path = location.pathname;
    if (path.startsWith('/brain')) return 'brain';
    if (path.startsWith('/gestalt')) return 'gestalt';
    if (path.startsWith('/gardener') || path.startsWith('/garden')) return 'gardener';
    if (path.startsWith('/forge')) return 'forge';
    if (path.startsWith('/town') || path.startsWith('/inhabit')) return 'coalition';
    if (path.startsWith('/park')) return 'park';
    if (path.startsWith('/workshop')) return 'domain';
    if (path.startsWith('/emergence')) return 'gestalt'; // Emergence is related to visualization
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

  const jewels: Array<{ name: JewelName; route: string }> = [
    { name: 'brain', route: '/brain' },
    { name: 'gestalt', route: '/gestalt' },
    { name: 'gardener', route: '/gardener' },
    { name: 'forge', route: '/forge' },
    { name: 'coalition', route: '/town' },
    { name: 'park', route: '/park' },
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
    isAnimating,
  } = useShell();

  // Main content positioning uses animated offsets for smooth coordination
  // When observer collapses: main slides up
  // When terminal expands: main shrinks from bottom
  // When navigation expands: main slides right
  //
  // Mobile layout fixed elements:
  // - ObserverDrawer: 40px (collapsed)
  // - Header: ~44px (py-2 + content)
  // Total: ~84px top offset needed
  const MOBILE_HEADER_HEIGHT = 44;
  const mainStyle: React.CSSProperties = density === 'compact'
    ? {
        // Mobile: account for fixed ObserverDrawer + Header at top
        paddingTop: `${observerHeight + MOBILE_HEADER_HEIGHT}px`,
        paddingBottom: '5rem', // Space for FAB/bottom toolbar
      }
    : {
        // Desktop: use animated offsets
        marginTop: `${observerHeight}px`,
        marginBottom: `${terminalHeight}px`,
        marginLeft: navigationTreeExpanded ? `${navigationWidth}px` : 0,
        // Disable CSS transitions when JS is animating to avoid double-animation
        transition: isAnimating ? 'none' : 'margin 0.25s cubic-bezier(0.4, 0, 0.2, 1)',
      };

  return (
    <div className="min-h-screen bg-gray-900 flex flex-col relative">
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
      <div className="flex-1 flex overflow-hidden relative">
        {/* Navigation Tree - Floating overlay sidebar */}
        <NavigationErrorBoundary>
          <NavigationTree />
        </NavigationErrorBoundary>

        {/* Content Canvas - uses coordinated offsets */}
        <main
          className="flex-1 overflow-auto absolute inset-0"
          style={mainStyle}
        >
          <ProjectionErrorBoundary>
            <Outlet />
          </ProjectionErrorBoundary>
        </main>
      </div>

      {/* Terminal Layer - Fixed at bottom */}
      <TerminalErrorBoundary>
        <Terminal />
      </TerminalErrorBoundary>

      {/* Optional Footer */}
      {showFooter && (
        <footer className="border-t border-gray-700/50 bg-gray-800/30 py-3 px-4 text-center text-xs text-gray-500">
          kgents - Tasteful, curated, ethical, joy-inducing agents
        </footer>
      )}
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
