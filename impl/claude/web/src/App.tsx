import { Routes, Route, useLocation, Link } from 'react-router-dom';
import { Suspense, lazy } from 'react';
import { AnimatePresence } from 'framer-motion';
import { ErrorBoundary } from './components/error/ErrorBoundary';
import { PageTransition, PersonalityLoading } from './components/joy';
import { WelcomeView } from './membrane/views/WelcomeView';

import './membrane/Membrane.css'; // For CSS variables

/**
 * kgents Web — Simplified
 *
 * Welcome screen + Galleries only.
 * The Membrane infrastructure remains for future use.
 */

// Gallery pages
const GalleryPage = lazy(() => import('./pages/GalleryPage'));
const LayoutGallery = lazy(() => import('./pages/LayoutGallery'));
const InteractiveTextGallery = lazy(() => import('./pages/InteractiveTextGallery'));

// Spec Ledger
const SpecLedgerPage = lazy(() => import('./pages/SpecLedgerPage'));

// Hypergraph Emacs
const HypergraphEditorPage = lazy(() =>
  import('./pages/HypergraphEditorPage').then((m) => ({ default: m.HypergraphEditorPage }))
);

// Graph Test
const GraphTestPage = lazy(() => import('./pages/GraphTestPage'));

function LoadingFallback() {
  return (
    <div className="flex items-center justify-center min-h-screen bg-surface-canvas">
      <PersonalityLoading jewel="brain" size="lg" action="connect" />
    </div>
  );
}

/**
 * Welcome screen wrapper with gallery links
 */
function WelcomeScreen() {
  return (
    <div className="membrane membrane--comfortable">
      <WelcomeView />

      {/* Navigation links — bottom corner */}
      <nav className="fixed bottom-4 right-4 flex gap-2 text-xs opacity-50 hover:opacity-100 transition-opacity">
        <Link
          to="/editor"
          className="px-2 py-1 rounded bg-surface-2 text-text-secondary hover:text-text-primary"
        >
          Editor
        </Link>
        <Link
          to="/ledger"
          className="px-2 py-1 rounded bg-surface-2 text-text-secondary hover:text-text-primary"
        >
          Spec Ledger
        </Link>
        <Link
          to="/graph"
          className="px-2 py-1 rounded bg-surface-2 text-text-secondary hover:text-text-primary"
        >
          Graph
        </Link>
        <Link
          to="/_/gallery"
          className="px-2 py-1 rounded bg-surface-2 text-text-secondary hover:text-text-primary"
        >
          Gallery
        </Link>
        <Link
          to="/_/gallery/layout"
          className="px-2 py-1 rounded bg-surface-2 text-text-secondary hover:text-text-primary"
        >
          Layout
        </Link>
        <Link
          to="/_/gallery/interactive-text"
          className="px-2 py-1 rounded bg-surface-2 text-text-secondary hover:text-text-primary"
        >
          Tokens
        </Link>
      </nav>
    </div>
  );
}

function App() {
  const location = useLocation();

  // Special routes (galleries, ledger, editor)
  const isSpecialRoute =
    location.pathname.startsWith('/_/') ||
    location.pathname.startsWith('/ledger') ||
    location.pathname.startsWith('/editor') ||
    location.pathname.startsWith('/graph');

  return (
    <ErrorBoundary resetKeys={[location.pathname]}>
      {isSpecialRoute ? (
        // Special routes (galleries, ledger)
        <Suspense fallback={<LoadingFallback />}>
          <AnimatePresence mode="wait" initial={false}>
            <PageTransition key={location.pathname} variant="fade">
              <Routes location={location}>
                <Route path="/_/gallery" element={<GalleryPage />} />
                <Route path="/_/gallery/layout" element={<LayoutGallery />} />
                <Route path="/_/gallery/interactive-text" element={<InteractiveTextGallery />} />
                <Route path="/ledger" element={<SpecLedgerPage />} />
                <Route path="/editor" element={<HypergraphEditorPage />} />
                <Route path="/graph" element={<GraphTestPage />} />
              </Routes>
            </PageTransition>
          </AnimatePresence>
        </Suspense>
      ) : (
        // Welcome screen
        <WelcomeScreen />
      )}
    </ErrorBoundary>
  );
}

export default App;
