/**
 * AGENTESE Router: Minimal.
 *
 * SEVERE STARK: One page. Everything else is deleted.
 *
 * Post-deletion: 88% reduction. Rebuild from here.
 */

import { Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { ErrorBoundary } from '../components/error/ErrorBoundary';
import { WorkspacePage } from '../pages/WorkspacePage';

/**
 * Loading fallback — no joy, no animation.
 * Prefixed with underscore: kept for future lazy-loading support.
 */
function _LoadingFallback() {
  return (
    <div className="min-h-screen bg-[#0a0a0c] text-[#3a3a44] flex items-center justify-center font-mono text-[11px]">
      Loading...
    </div>
  );
}

/**
 * 404 — inline, no separate component.
 */
function NotFound() {
  const location = useLocation();
  return (
    <div className="min-h-screen bg-[#0a0a0c] text-[#8a8a94] p-4 font-mono text-[12px]">
      <h1 className="text-[#c4a77d] text-[14px] mb-2">404</h1>
      <code className="text-[#5a5a64] text-[10px]">{location.pathname}</code>
      <p className="mt-2 text-[#3a3a44]">Path not found.</p>
      <a href="/" className="text-[#8a8a94] hover:underline mt-4 inline-block">
        → workspace
      </a>
    </div>
  );
}

/**
 * Main Router — 3 routes only.
 */
export function AgenteseRouter() {
  const location = useLocation();

  return (
    <ErrorBoundary resetKeys={[location.pathname]}>
      <Routes location={location}>
        {/* Root → Workspace */}
        <Route path="/" element={<Navigate to="/workspace" replace />} />

        {/* THE page */}
        <Route path="/workspace" element={<WorkspacePage />} />
        <Route path="/workspace/*" element={<WorkspacePage />} />

        {/* Legacy AGENTESE paths → redirect to workspace for now */}
        <Route path="/world.document" element={<Navigate to="/workspace" replace />} />
        <Route path="/world.document/*" element={<Navigate to="/workspace" replace />} />

        {/* 404 */}
        <Route path="*" element={<NotFound />} />
      </Routes>
    </ErrorBoundary>
  );
}
