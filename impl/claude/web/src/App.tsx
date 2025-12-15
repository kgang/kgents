import { Routes, Route } from 'react-router-dom';
import { Suspense, lazy } from 'react';
import { Layout } from './components/layout/Layout';

// Lazy load pages for code splitting
const Landing = lazy(() => import('./pages/Landing'));
const Town = lazy(() => import('./pages/Town'));
const Inhabit = lazy(() => import('./pages/Inhabit'));
const Dashboard = lazy(() => import('./pages/Dashboard'));
const CheckoutSuccess = lazy(() => import('./pages/CheckoutSuccess'));

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
  return (
    <Suspense fallback={<LoadingFallback />}>
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route element={<Layout />}>
          <Route path="/town/:townId" element={<Town />} />
          <Route path="/town/:townId/inhabit/:citizenId" element={<Inhabit />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/checkout/success" element={<CheckoutSuccess />} />
        </Route>
      </Routes>
    </Suspense>
  );
}

export default App;
