/**
 * UniversalProjection - The URL IS the API call
 *
 * This is the heart of AGENTESE-as-Route. It:
 * 1. Parses the current URL into AGENTESE path components
 * 2. Detects context-level paths (e.g., /self) and renders ContextOverviewProjection
 * 3. Invokes the path via useAgentese hook for registered nodes
 * 4. Resolves the appropriate projection component
 * 5. Renders with loading/error states
 *
 * @see spec/protocols/agentese-as-route.md
 */

import { Suspense, useMemo } from 'react';
import { useLocation, Navigate } from 'react-router-dom';
import { parseAgentesePath, AGENTESE_CONTEXTS } from '@/utils/parseAgentesePath';
import type { AgenteseContext } from '@/utils/parseAgentesePath';
import { useAgentese } from '@/hooks/useAgentesePath';
import { resolveProjection } from './registry';
import { ProjectionLoading } from './ProjectionLoading';
import { ProjectionError } from './ProjectionError';
import { ContextOverviewProjection } from './ContextOverviewProjection';
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
/**
 * Check if a path is a context-level path (single segment, no registered node)
 * e.g., "self", "world", "concept", "void", "time"
 */
function isContextLevelPath(path: string): boolean {
  const segments = path.split('.');
  return segments.length === 1 && AGENTESE_CONTEXTS.includes(segments[0] as AgenteseContext);
}

export function UniversalProjection({ skip = false }: UniversalProjectionOptions = {}) {
  const location = useLocation();
  const pathname = location.pathname;
  const search = location.search;

  // Determine if this is a root path redirect
  const isRoot = pathname === '/' || pathname === '';

  // Parse the AGENTESE path from URL
  const parsed = useMemo(() => parseAgentesePath(pathname + search), [pathname, search]);

  // Check if this is a context-level path (e.g., /self, /world)
  // These should show ContextOverviewProjection, not invoke the backend
  const isContextPath = useMemo(
    () => parsed.isValid && isContextLevelPath(parsed.path),
    [parsed.isValid, parsed.path]
  );

  // Invoke AGENTESE - must be called unconditionally (rules of hooks)
  // Skip invocation for root redirects, invalid paths, or context-level paths
  const shouldSkip = skip || isRoot || !parsed.isValid || isContextPath;
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

  // Context-level path -> Show Context Overview
  // This is like arriving at a garden's main gate - you see all paths you can explore
  if (isContextPath) {
    return <ContextOverviewProjection context={parsed.context as AgenteseContext} />;
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
