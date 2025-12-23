import { Routes, Route, useLocation } from 'react-router-dom';
import { Suspense, lazy } from 'react';
import { AnimatePresence } from 'framer-motion';
import { ErrorBoundary } from './components/error/ErrorBoundary';
import { PageTransition, PersonalityLoading } from './components/joy';
import { AppShell } from './components/layout';
import { WelcomeView } from './membrane/views/WelcomeView';

import './membrane/Membrane.css'; // For CSS variables

/**
 * kgents Web — The Cathedral Navigation Experience
 *
 * Four surfaces, one coherent experience:
 * - Editor: Hypergraph Emacs for spec navigation/editing
 * - Ledger: Spec corpus health dashboard
 * - Chart: Astronomical visualization
 * - Brain: Memory exploration (crystals, teaching, wisdom)
 *
 * AppShell provides navbar + WitnessFooter (always-on)
 */

// Gallery pages
const GalleryPage = lazy(() => import('./pages/GalleryPage'));
const LayoutGallery = lazy(() => import('./pages/LayoutGallery'));
const InteractiveTextGallery = lazy(() => import('./pages/InteractiveTextGallery'));

// Main surfaces
const SpecLedgerPage = lazy(() => import('./pages/SpecLedgerPage'));
const HypergraphEditorPage = lazy(() =>
  import('./pages/HypergraphEditorPage').then((m) => ({ default: m.HypergraphEditorPage }))
);
const ChartPage = lazy(() => import('./pages/ChartPage'));
const BrainPage = lazy(() => import('./pages/BrainPage'));

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

  // Galleries don't use AppShell (standalone dev tools)
  const isGallery = location.pathname.startsWith('/_/');

  // Welcome screen is special (no AppShell) - handled by the final else branch

  // Main app surfaces use AppShell
  const isAppSurface =
    location.pathname.startsWith('/editor') ||
    location.pathname.startsWith('/ledger') ||
    location.pathname.startsWith('/chart') ||
    location.pathname.startsWith('/brain');

  return (
    <ErrorBoundary resetKeys={[location.pathname]}>
      {isGallery ? (
        // Galleries — standalone dev tools
        <Suspense fallback={<LoadingFallback />}>
          <AnimatePresence mode="wait" initial={false}>
            <PageTransition key={location.pathname} variant="fade">
              <Routes location={location}>
                <Route path="/_/gallery" element={<GalleryPage />} />
                <Route path="/_/gallery/layout" element={<LayoutGallery />} />
                <Route path="/_/gallery/interactive-text" element={<InteractiveTextGallery />} />
              </Routes>
            </PageTransition>
          </AnimatePresence>
        </Suspense>
      ) : isAppSurface ? (
        // Main surfaces — wrapped in AppShell with navbar + witness footer
        <AppShell>
          <Suspense fallback={<LoadingFallback />}>
            <AnimatePresence mode="wait" initial={false}>
              <PageTransition key={location.pathname} variant="fade">
                <Routes location={location}>
                  <Route path="/editor" element={<HypergraphEditorPage />} />
                  <Route path="/ledger" element={<SpecLedgerPage />} />
                  <Route path="/chart" element={<ChartPage />} />
                  <Route path="/brain" element={<BrainPage />} />
                </Routes>
              </PageTransition>
            </AnimatePresence>
          </Suspense>
        </AppShell>
      ) : (
        // Welcome screen — no shell
        <WelcomeScreen />
      )}
    </ErrorBoundary>
  );
}

export default App;
