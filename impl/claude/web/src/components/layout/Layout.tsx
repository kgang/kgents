import { Outlet, Link, useLocation } from 'react-router-dom';
import { CrownContext } from './CrownContext';
import { JEWEL_INFO, type Jewel } from '../synergy/types';

/**
 * Navigation item with jewel styling.
 */
function NavLink({
  to,
  jewel,
  label,
  currentPath,
}: {
  to: string;
  jewel: Jewel;
  label: string;
  currentPath: string;
}) {
  const info = JEWEL_INFO[jewel];
  const isActive = currentPath.startsWith(to);

  return (
    <Link
      to={to}
      className={`
        flex items-center gap-1.5
        text-sm font-medium
        transition-all duration-200
        ${
          isActive
            ? `${info.color} scale-105`
            : 'text-gray-400 hover:text-gray-200 hover:scale-102'
        }
      `}
    >
      <span className="text-base">{info.icon}</span>
      <span className="hidden lg:inline">{label}</span>
    </Link>
  );
}

export function Layout() {
  const location = useLocation();

  return (
    <div className="min-h-screen bg-town-bg flex flex-col">
      {/* Header */}
      <header className="border-b border-town-accent/30 bg-town-surface/50 backdrop-blur-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 py-3">
          {/* Top row: Logo + Nav */}
          <div className="flex items-center justify-between">
            <Link to="/" className="flex items-center gap-2 hover:opacity-80 transition-opacity">
              <span className="text-2xl">👑</span>
              <span className="font-semibold text-lg">kgents</span>
            </Link>

            {/* Jewel Navigation */}
            <nav className="flex items-center gap-4">
              <NavLink to="/brain" jewel="brain" label="Brain" currentPath={location.pathname} />
              <NavLink
                to="/gestalt"
                jewel="gestalt"
                label="Gestalt"
                currentPath={location.pathname}
              />
              <NavLink
                to="/gardener"
                jewel="gardener"
                label="Gardener"
                currentPath={location.pathname}
              />
              <span className="text-gray-600">│</span>
              <NavLink
                to="/atelier"
                jewel="atelier"
                label="Atelier"
                currentPath={location.pathname}
              />
              <NavLink
                to="/town/demo"
                jewel="coalition"
                label="Coalition"
                currentPath={location.pathname}
              />
              <span className="text-gray-600">│</span>
              <NavLink to="/park" jewel="park" label="Park" currentPath={location.pathname} />
            </nav>
          </div>

          {/* Bottom row: Crown context */}
          <div className="mt-2 flex items-center justify-between">
            <CrownContext />
            <div className="text-xs text-gray-500">
              <span className="font-mono">7 jewels, 1 crown</span>
            </div>
          </div>
        </div>
      </header>

      {/* Main content */}
      <main className="flex-1">
        <Outlet />
      </main>

      {/* Footer */}
      <footer className="border-t border-town-accent/30 bg-town-surface/30 py-4">
        <div className="max-w-7xl mx-auto px-4 text-center text-sm text-gray-500">
          <p>kgents - Tasteful, curated, ethical, joy-inducing agents</p>
        </div>
      </footer>
    </div>
  );
}
