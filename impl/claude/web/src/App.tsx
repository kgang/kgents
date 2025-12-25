import { Routes, Route, useLocation } from 'react-router-dom';
import { Suspense, lazy } from 'react';
import { AnimatePresence } from 'framer-motion';
import { ErrorBoundary } from './components/error/ErrorBoundary';
import { PageTransition, PersonalityLoading } from './components/joy';
import { TelescopeShell } from './components/layout/TelescopeShell';
import { WelcomeView } from './pages/WelcomePage';

/**
 * kgents Web — The Cathedral Navigation Experience
 *
 * Five surfaces, one coherent experience:
 * - Editor: Hypergraph Emacs for spec navigation/editing
 * - Docs: Living document canvas (Document Director)
 * - Chart: Astronomical visualization
 * - Feed: Memory exploration (crystals, teaching, wisdom)
 * - Zero Seed: Epistemic graph navigation (axioms, proofs, health, telescope)
 *
 * TelescopeShell wraps AppShell, providing:
 * - Focal distance ruler (vertical navigation)
 * - Loss threshold filtering
 * - Derivation trail (proof breadcrumbs)
 * - Telescope context for all children
 */

// Main surfaces
const DirectorPage = lazy(() => import('./pages/DirectorPage'));
const HypergraphEditorPage = lazy(() =>
  import('./pages/HypergraphEditorPage').then((m) => ({ default: m.HypergraphEditorPage }))
);
const ChartPage = lazy(() => import('./pages/ChartPage'));
const FeedPage = lazy(() => import('./pages/FeedPage'));
const ZeroSeedPage = lazy(() => import('./pages/ZeroSeedPage'));

function LoadingFallback() {
  return (
    <div className="flex items-center justify-center min-h-screen bg-surface-canvas">
      <PersonalityLoading jewel="brain" size="lg" action="connect" />
    </div>
  );
}

/**
 * Welcome screen — the landing page
 */
function WelcomeScreen() {
  return (
    <div className="membrane membrane--comfortable">
      <WelcomeView />
    </div>
  );
}

function App() {
  const location = useLocation();

  // Main app surfaces use TelescopeShell (which wraps AppShell)
  const isAppSurface =
    location.pathname.startsWith('/editor') ||
    location.pathname.startsWith('/director') ||
    location.pathname.startsWith('/chart') ||
    location.pathname.startsWith('/brain') ||
    location.pathname.startsWith('/zero-seed');

  return (
    <ErrorBoundary resetKeys={[location.pathname]}>
      {isAppSurface ? (
        // Main surfaces — wrapped in TelescopeShell (which contains AppShell)
        <TelescopeShell>
          <Suspense fallback={<LoadingFallback />}>
            <AnimatePresence mode="wait" initial={false}>
              <PageTransition key={location.pathname} variant="fade">
                <Routes location={location}>
                  <Route path="/editor/*" element={<HypergraphEditorPage />} />
                  <Route path="/director" element={<DirectorPage />} />
                  <Route path="/chart" element={<ChartPage />} />
                  <Route path="/brain" element={<FeedPage />} />
                  <Route path="/zero-seed" element={<ZeroSeedPage />} />
                </Routes>
              </PageTransition>
            </AnimatePresence>
          </Suspense>
        </TelescopeShell>
      ) : (
        // Welcome screen — no shell
        <WelcomeScreen />
      )}
    </ErrorBoundary>
  );
}

export default App;
