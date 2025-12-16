import { Routes, Route, useLocation, Navigate } from 'react-router-dom';
import { Suspense, lazy } from 'react';
import { Layout } from './components/layout/Layout';
import { ErrorBoundary } from './components/error/ErrorBoundary';

// Essential pages only
const Town = lazy(() => import('./pages/Town'));
const Atelier = lazy(() => import('./pages/Atelier'));
const GalleryPage = lazy(() => import('./pages/GalleryPage'));
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
          </Route>
          {/* 404 catch-all */}
          <Route path="*" element={<NotFound />} />
        </Routes>
      </Suspense>
    </ErrorBoundary>
  );
}

export default App;
