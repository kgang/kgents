import { Routes, Route, useLocation } from 'react-router-dom';
import { Suspense, lazy } from 'react';
import { AnimatePresence } from 'framer-motion';
import { Shell, UniversalProjection } from './shell';
import { ErrorBoundary } from './components/error/ErrorBoundary';
import { SynergyToaster } from './components/synergy';
import { PageTransition, PersonalityLoading } from './components/joy';

/**
 * AGENTESE-as-Route Architecture (AD-009 Phase 3 Complete)
 *
 * The URL IS the AGENTESE invocation. UniversalProjection catches all paths,
 * parses them as AGENTESE, invokes via the gateway, and renders projections.
 *
 * All legacy routes have been removed - the URL IS the AGENTESE path.
 *
 * @see spec/protocols/agentese-as-route.md
 */

// Gallery pages (kept as explicit routes - not AGENTESE paths)
const GalleryPage = lazy(() => import('./pages/GalleryPage'));
const LayoutGallery = lazy(() => import('./pages/LayoutGallery'));
const InteractiveTextGallery = lazy(() => import('./pages/InteractiveTextGallery'));
const CanvasPage = lazy(() => import('./pages/Canvas'));
const AgenteseDocs = lazy(() => import('./pages/AgenteseDocs'));

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
        {/* AnimatePresence enables exit animations between routes */}
        <AnimatePresence mode="wait" initial={false}>
          <PageTransition key={location.pathname} variant="fade">
            <Routes location={location}>
              {/* OS Shell - Unified layout with three persistent layers */}
              <Route element={<Shell />}>
                {/*
                 * Explicit routes (non-AGENTESE paths)
                 * Developer galleries use /_/ prefix (not part of AGENTESE ontology)
                 */}

                {/* Developer Galleries - system routes (/_/) not AGENTESE ontology */}
                <Route path="/_/gallery" element={<GalleryPage />} />
                <Route path="/_/gallery/layout" element={<LayoutGallery />} />
                <Route path="/_/gallery/interactive-text" element={<InteractiveTextGallery />} />
                <Route path="/_/canvas" element={<CanvasPage />} />
                <Route path="/_/docs/agentese" element={<AgenteseDocs />} />

                {/*
                 * Universal AGENTESE Projection (catch-all)
                 *
                 * All paths are parsed as AGENTESE invocations:
                 *   /self.memory → logos.invoke("self.memory")
                 *   /self.memory:capture → logos.invoke("self.memory", aspect="capture")
                 *
                 * Root (/) redirects to /self.memory (Brain).
                 * Unknown paths show ConceptHome fallback.
                 *
                 * @see spec/protocols/agentese-as-route.md
                 */}
                <Route path="/*" element={<UniversalProjection />} />
              </Route>
            </Routes>
          </PageTransition>
        </AnimatePresence>
      </Suspense>

      {/* Cross-jewel synergy notifications - Foundation 4 */}
      <SynergyToaster />
    </ErrorBoundary>
  );
}

export default App;
