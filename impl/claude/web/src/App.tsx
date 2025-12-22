import { Routes, Route, useLocation } from 'react-router-dom';
import { Suspense, lazy } from 'react';
import { AnimatePresence } from 'framer-motion';
import { ErrorBoundary } from './components/error/ErrorBoundary';
import { SynergyToaster } from './components/synergy';
import { PageTransition, PersonalityLoading } from './components/joy';
// Note: Membrane uses useWindowLayout internally for density detection
import { Membrane } from './membrane';

/**
 * kgents Web - THE MEMBRANE
 *
 * "Stop documenting agents. Become the agent."
 *
 * The Membrane is the entire app. No navigation, no routes (except dev escape hatch).
 * One surface that morphs: Focus + Witness + Dialogue.
 *
 * Decision: fuse-ccad81de (2025-12-22)
 */

// Gallery pages (kept for dev/testing - escape hatch)
const GalleryPage = lazy(() => import('./pages/GalleryPage'));
const LayoutGallery = lazy(() => import('./pages/LayoutGallery'));
const InteractiveTextGallery = lazy(() => import('./pages/InteractiveTextGallery'));

function LoadingFallback() {
  return (
    <div className="flex items-center justify-center min-h-screen bg-surface-canvas">
      <PersonalityLoading jewel="brain" size="lg" action="connect" />
    </div>
  );
}

function App() {
  const location = useLocation();

  // Dev escape hatch: /_/gallery routes bypass the Membrane
  const isDevRoute = location.pathname.startsWith('/_/');

  return (
    <ErrorBoundary resetKeys={[location.pathname]}>
      {isDevRoute ? (
        // Dev gallery routes
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
      ) : (
        // THE MEMBRANE — The entire app
        <Membrane />
      )}

      {/* Cross-jewel synergy notifications */}
      <SynergyToaster />
    </ErrorBoundary>
  );
}

export default App;
