import { Routes, Route, useLocation } from 'react-router-dom';
import { Suspense, lazy } from 'react';
import { Layout } from './components/layout/Layout';
import { ErrorBoundary } from './components/error/ErrorBoundary';

// Lazy load pages for code splitting
const Landing = lazy(() => import('./pages/Landing'));
const Town = lazy(() => import('./pages/Town'));
const Inhabit = lazy(() => import('./pages/Inhabit'));
const Dashboard = lazy(() => import('./pages/Dashboard'));
const CheckoutSuccess = lazy(() => import('./pages/CheckoutSuccess'));
const Workshop = lazy(() => import('./pages/Workshop'));
const Atelier = lazy(() => import('./pages/Atelier'));
const NotFound = lazy(() => import('./pages/NotFound'));

function LoadingFallback() {
  return (
    <div className="flex items-center justify-center min-h-screen bg-town-bg">
      <div className="text-center">
        <div className="animate-pulse-slow text-4xl mb-4">🏘️</div>
        <p className="text-gray-400">Loading Agent Town...</p>
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
          <Route path="/" element={<Landing />} />
          <Route element={<Layout />}>
            <Route path="/town/:townId" element={<Town />} />
            <Route path="/town/:townId/inhabit/:citizenId" element={<Inhabit />} />
            <Route path="/workshop" element={<Workshop />} />
            <Route path="/atelier" element={<Atelier />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/checkout/success" element={<CheckoutSuccess />} />
          </Route>
          {/* 404 catch-all */}
          <Route path="*" element={<NotFound />} />
        </Routes>
      </Suspense>
    </ErrorBoundary>
  );
}

export default App;
