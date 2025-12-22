import { Routes, Route, useLocation, Navigate } from 'react-router-dom';
import { Suspense, lazy } from 'react';
import { AnimatePresence } from 'framer-motion';
import { ErrorBoundary } from './components/error/ErrorBoundary';
import { SynergyToaster } from './components/synergy';
import { PageTransition, PersonalityLoading } from './components/joy';

/**
 * kgents Web - Surgical Refactor 2025-12-22
 *
 * Transformed from AGENTESE explorer to:
 * 1. Timeline/Stream File Explorer (coming)
 * 2. Swarm/Stigmergy Agent Lab (coming)
 *
 * For now, simple gallery routes while we build new features.
 */

// Gallery pages (kept for dev/testing)
const GalleryPage = lazy(() => import('./pages/GalleryPage'));
const LayoutGallery = lazy(() => import('./pages/LayoutGallery'));
const InteractiveTextGallery = lazy(() => import('./pages/InteractiveTextGallery'));
const NotFound = lazy(() => import('./pages/NotFound'));

function LoadingFallback() {
  return (
    <div className="flex items-center justify-center min-h-screen bg-surface-canvas">
      <PersonalityLoading jewel="brain" size="lg" action="connect" />
    </div>
  );
}

function App() {
  const location = useLocation();

  return (
    <ErrorBoundary resetKeys={[location.pathname]}>
      <Suspense fallback={<LoadingFallback />}>
        <AnimatePresence mode="wait" initial={false}>
          <PageTransition key={location.pathname} variant="fade">
            <Routes location={location}>
              {/* Redirect root to gallery for now */}
              <Route path="/" element={<Navigate to="/_/gallery" replace />} />

              {/* Developer Galleries */}
              <Route path="/_/gallery" element={<GalleryPage />} />
              <Route path="/_/gallery/layout" element={<LayoutGallery />} />
              <Route path="/_/gallery/interactive-text" element={<InteractiveTextGallery />} />

              {/* Future: Timeline Explorer */}
              {/* <Route path="/timeline/:id?" element={<TimelineExplorer />} /> */}

              {/* Future: Swarm Lab */}
              {/* <Route path="/lab/:outlineId?" element={<SwarmLab />} /> */}

              {/* 404 */}
              <Route path="*" element={<NotFound />} />
            </Routes>
          </PageTransition>
        </AnimatePresence>
      </Suspense>

      {/* Cross-jewel synergy notifications */}
      <SynergyToaster />
    </ErrorBoundary>
  );
}

export default App;
