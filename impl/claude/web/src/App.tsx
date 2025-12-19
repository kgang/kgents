import { Routes, Route, useLocation, Navigate } from 'react-router-dom';
import { Suspense, lazy } from 'react';
import { AnimatePresence } from 'framer-motion';
import { Shell } from './shell';
import { ErrorBoundary } from './components/error/ErrorBoundary';
import { SynergyToaster } from './components/synergy';
import { PageTransition, PersonalityLoading } from './components/joy';

// Essential pages only
const Cockpit = lazy(() => import('./pages/Cockpit'));
const Town = lazy(() => import('./pages/Town'));
const Forge = lazy(() => import('./pages/Forge'));
const GalleryPage = lazy(() => import('./pages/GalleryPage'));
const LayoutGallery = lazy(() => import('./pages/LayoutGallery'));
const Brain = lazy(() => import('./pages/Brain'));
const Workshop = lazy(() => import('./pages/Workshop'));
const Inhabit = lazy(() => import('./pages/Inhabit'));
const Gestalt = lazy(() => import('./pages/Gestalt'));
// GestaltLive mothballed - three.js eliminated for performance
const Gardener = lazy(() => import('./pages/Gardener'));
const Garden = lazy(() => import('./pages/Garden'));
const ParkScenario = lazy(() => import('./pages/ParkScenario'));
// EmergenceDemo mothballed - three.js eliminated for performance
const Differance = lazy(() => import('./pages/Differance'));
const NotFound = lazy(() => import('./pages/NotFound'));

// Town sub-pages (Contract-Driven)
const TownOverviewPage = lazy(() => import('./pages/TownOverviewPage'));
const TownCitizensPage = lazy(() => import('./pages/TownCitizensPage'));
const TownCoalitionsPage = lazy(() => import('./pages/TownCoalitionsPage'));

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
                {/* Cockpit — Kent's developer portal (Anti-Sausage Protocol manifest) */}
                <Route path="/" element={<Cockpit />} />

                {/* Crown Jewels */}
                <Route path="/brain" element={<Brain />} />
                <Route path="/gestalt" element={<Gestalt />} />
                {/* /gestalt/live mothballed - three.js eliminated */}
                <Route path="/gardener" element={<Gardener />} />
                <Route path="/garden" element={<Garden />} />
                <Route path="/forge" element={<Forge />} />
                {/* Town - Coalition Crown Jewel */}
                <Route path="/town" element={<TownOverviewPage />} />
                <Route path="/town/overview" element={<TownOverviewPage />} />
                <Route path="/town/citizens" element={<TownCitizensPage />} />
                <Route path="/town/citizens/:citizenId" element={<TownCitizensPage />} />
                <Route path="/town/coalitions" element={<TownCoalitionsPage />} />
                <Route path="/town/coalitions/:coalitionId" element={<TownCoalitionsPage />} />
                <Route
                  path="/town/simulation"
                  element={<Navigate to="/town/simulation/demo" replace />}
                />
                <Route path="/town/simulation/:townId" element={<Town />} />
                <Route path="/inhabit/:citizenId?" element={<Inhabit />} />
                <Route path="/park" element={<ParkScenario />} />
                <Route path="/workshop" element={<Workshop />} />

                {/* Galleries */}
                <Route path="/gallery" element={<GalleryPage />} />
                <Route path="/gallery/layout" element={<LayoutGallery />} />

                {/* Différance Engine — Ghost Heritage Graph Explorer */}
                <Route path="/differance" element={<Differance />} />

                {/* /emergence mothballed - three.js eliminated */}
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
