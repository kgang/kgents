import { Routes, Route, useLocation, Navigate } from 'react-router-dom';
import { Suspense, lazy } from 'react';
import { Layout } from './components/layout/Layout';
import { ErrorBoundary } from './components/error/ErrorBoundary';

// Essential pages only
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
const NotFound = lazy(() => import('./pages/NotFound'));

function LoadingFallback() {
  return (
    <div className="flex items-center justify-center min-h-screen bg-town-bg">
      <div className="text-center">
        <div className="animate-pulse-slow text-4xl mb-4">🏘️</div>
        <p className="text-gray-400">Loading...</p>
      </div>
    </div>
  );
}

function App() {
  const location = useLocation();

  return (
    <ErrorBoundary resetKeys={[location.pathname]}>
      <Suspense fallback={<LoadingFallback />}>
        <Routes>
          {/* Redirect root to Town with default town */}
          <Route path="/" element={<Navigate to="/town/default" replace />} />
          <Route element={<Layout />}>
            <Route path="/town/:townId" element={<Town />} />
            <Route path="/atelier" element={<Atelier />} />
            <Route path="/gallery" element={<GalleryPage />} />
            <Route path="/gallery/layout" element={<LayoutGallery />} />
            <Route path="/brain" element={<Brain />} />
            <Route path="/workshop" element={<Workshop />} />
            <Route path="/inhabit/:citizenId?" element={<Inhabit />} />
            <Route path="/gestalt" element={<Gestalt />} />
            <Route path="/gestalt/live" element={<GestaltLive />} />
            <Route path="/gardener" element={<Gardener />} />
          </Route>
          {/* 404 catch-all */}
          <Route path="*" element={<NotFound />} />
        </Routes>
      </Suspense>
    </ErrorBoundary>
  );
}

export default App;
