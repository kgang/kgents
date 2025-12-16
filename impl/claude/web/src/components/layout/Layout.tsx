import { Outlet, Link } from 'react-router-dom';

export function Layout() {
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
            <Link to="/town/default" className="text-gray-300 hover:text-white transition-colors">
              Town
            </Link>
            <Link to="/atelier" className="text-gray-300 hover:text-white transition-colors">
              Atelier
            </Link>
            <Link to="/gallery" className="text-gray-300 hover:text-white transition-colors">
              Gallery
            </Link>
            <Link to="/brain" className="text-gray-300 hover:text-white transition-colors">
              Brain
            </Link>
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
    </div>
  );
}
