/**
 * UniversalProjection - The URL IS the API call
 *
 * This is the heart of AGENTESE-as-Route. It:
 * 1. Parses the current URL into AGENTESE path components
 * 2. Invokes the path via useAgentese hook
 * 3. Resolves the appropriate projection component
 * 4. Renders with loading/error states
 *
 * @see spec/protocols/agentese-as-route.md
 */

import { Suspense, useMemo } from 'react';
import { useLocation, Navigate } from 'react-router-dom';
import { parseAgentesePath } from '@/utils/parseAgentesePath';
import { useAgentese } from '@/hooks/useAgentesePath';
import { resolveProjection } from './registry';
import { ProjectionLoading } from './ProjectionLoading';
import { ProjectionError } from './ProjectionError';
import type { ProjectionContext, UniversalProjectionOptions } from './types';

// === LEGACY_REDIRECTS REMOVED ===
// Phase 3 complete: The URL IS the AGENTESE path.
// Legacy routes like /brain, /town, /gardener no longer redirect.
// Visitors to old paths see ConceptHome or ProjectionError.
// See spec/protocols/agentese-as-route.md

/**
 * UniversalProjection component
 *
 * Catches all AGENTESE paths and renders the appropriate projection.
 *
 * @example
 * // In App.tsx
 * <Routes>
 *   <Route path="/_/*" element={<SystemRoutes />} />
 *   <Route path="/*" element={<UniversalProjection />} />
 * </Routes>
 */
export function UniversalProjection({ skip = false }: UniversalProjectionOptions = {}) {
  const location = useLocation();
  const pathname = location.pathname;
  const search = location.search;

  // Determine if this is a root path redirect
  const isRoot = pathname === '/' || pathname === '';

  // Parse the AGENTESE path from URL
  const parsed = useMemo(() => parseAgentesePath(pathname + search), [pathname, search]);

  // Invoke AGENTESE - must be called unconditionally (rules of hooks)
  // Skip invocation for root redirects or invalid paths
  const shouldSkip = skip || isRoot || !parsed.isValid;
  const { data, responseType, isLoading, error } = useAgentese(
    parsed.isValid ? parsed.path : 'self.cockpit',
    {
      aspect: parsed.isValid ? parsed.aspect : 'manifest',
      params: parsed.isValid ? parsed.params : {},
      skip: shouldSkip,
    }
  );

  // Handle root path -> Cockpit
  if (isRoot) {
    return <Navigate to="/self.cockpit" replace />;
  }

  // Invalid AGENTESE path
  if (!parsed.isValid) {
    return (
      <ProjectionError
        path={pathname}
        aspect="manifest"
        error={new Error(parsed.error || 'Invalid AGENTESE path')}
      />
    );
  }

  // Loading state
  if (isLoading) {
    return <ProjectionLoading path={parsed.path} aspect={parsed.aspect} />;
  }

  // Error state
  if (error) {
    return <ProjectionError path={parsed.path} aspect={parsed.aspect} error={error} />;
  }

  // Build projection context
  const context: ProjectionContext = {
    path: parsed.path,
    context: parsed.context,
    aspect: parsed.aspect,
    params: parsed.params,
    response: data,
    responseType: responseType || 'unknown',
  };

  // Resolve and render projection
  const Projection = resolveProjection(context);

  return (
    <Suspense fallback={<ProjectionLoading path={parsed.path} aspect={parsed.aspect} />}>
      <Projection context={context} />
    </Suspense>
  );
}

/**
 * Hook to get the current AGENTESE path context
 *
 * Useful for components that need to know their AGENTESE context
 * without re-parsing the URL.
 */
export function useProjectionContext(): ProjectionContext | null {
  const location = useLocation();
  const parsed = useMemo(
    () => parseAgentesePath(location.pathname + location.search),
    [location.pathname, location.search]
  );

  if (!parsed.isValid) return null;

  // Note: response and responseType won't be available here
  // as this hook doesn't fetch data
  return {
    path: parsed.path,
    context: parsed.context,
    aspect: parsed.aspect,
    params: parsed.params,
    response: null,
    responseType: 'unknown',
  };
}

export default UniversalProjection;
