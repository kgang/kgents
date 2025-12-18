import { Routes, Route, useLocation, Navigate } from 'react-router-dom';
import { Suspense, lazy } from 'react';
import { AnimatePresence } from 'framer-motion';
import { Shell } from './shell';
import { ErrorBoundary } from './components/error/ErrorBoundary';
import { SynergyToaster } from './components/synergy';
import { PageTransition, PersonalityLoading } from './components/joy';

// Essential pages only
const Crown = lazy(() => import('./pages/Crown'));
const Town = lazy(() => import('./pages/Town'));
const Atelier = lazy(() => import('./pages/Atelier'));
const GalleryPage = lazy(() => import('./pages/GalleryPage'));
const LayoutGallery = lazy(() => import('./pages/LayoutGallery'));
const Brain = lazy(() => import('./pages/Brain'));
const Workshop = lazy(() => import('./pages/Workshop'));
const Inhabit = lazy(() => import('./pages/Inhabit'));
const Gestalt = lazy(() => import('./pages/Gestalt'));
const GestaltLive = lazy(() => import('./pages/GestaltLive'));
const Gardener = lazy(() => import('./pages/Gardener'));
const Garden = lazy(() => import('./pages/Garden'));
const ParkScenario = lazy(() => import('./pages/ParkScenario'));
const EmergenceDemo = lazy(() => import('./pages/EmergenceDemo'));
const NotFound = lazy(() => import('./pages/NotFound'));

function LoadingFallback() {
  return (
    <div className="flex items-center justify-center min-h-screen bg-surface-canvas">
      <PersonalityLoading jewel="gestalt" size="lg" action="connect" />
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
                {/* Crown landing page - Hero Path entry point */}
                <Route path="/" element={<Crown />} />
                <Route path="/crown" element={<Crown />} />

                {/* Crown Jewels */}
                <Route path="/brain" element={<Brain />} />
                <Route path="/gestalt" element={<Gestalt />} />
                <Route path="/gestalt/live" element={<GestaltLive />} />
                <Route path="/gardener" element={<Gardener />} />
                <Route path="/garden" element={<Garden />} />
                <Route path="/atelier" element={<Atelier />} />
                <Route path="/town" element={<Navigate to="/town/demo" replace />} />
                <Route path="/town/:townId" element={<Town />} />
                <Route path="/inhabit/:citizenId?" element={<Inhabit />} />
                <Route path="/park" element={<ParkScenario />} />
                <Route path="/workshop" element={<Workshop />} />

                {/* Galleries */}
                <Route path="/gallery" element={<GalleryPage />} />
                <Route path="/gallery/layout" element={<LayoutGallery />} />

                {/* Other */}
                <Route path="/emergence" element={<EmergenceDemo />} />
              </Route>

              {/* 404 catch-all */}
              <Route path="*" element={<NotFound />} />
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
