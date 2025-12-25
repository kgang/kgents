/**
 * React hooks for AGENTESE path navigation.
 *
 * These hooks replace traditional React Router navigation
 * with AGENTESE-aware navigation.
 */

import { useNavigate, useLocation } from 'react-router-dom';
import { useCallback, useMemo } from 'react';
import {
  parseAgentesePath,
  toUrl,
  buildAgentesePath,
  type AgentesePath,
} from './AgentesePath';

/**
 * Hook to get the current AGENTESE path from URL.
 *
 * Returns parsed path or null if not a valid AGENTESE URL.
 *
 * Example:
 *   const path = useAgentesePath();
 *   if (path) {
 *     console.log(`Context: ${path.context}, Entity: ${path.path[0]}`);
 *   }
 */
export function useAgentesePath(): AgentesePath | null {
  const location = useLocation();

  return useMemo(() => {
    try {
      return parseAgentesePath(location.pathname);
    } catch {
      // Not an AGENTESE path (e.g., /_shell/settings)
      return null;
    }
  }, [location.pathname]);
}

/**
 * Hook for AGENTESE-aware navigation.
 *
 * Provides a function to navigate to AGENTESE paths.
 *
 * Example:
 *   const navigate = useAgenteseNavigate();
 *   navigate('self.chat.session', { id: 'abc123' }); // → /self.chat.session.abc123
 */
export function useAgenteseNavigate() {
  const navigate = useNavigate();

  return useCallback(
    (
      path: string,
      options?: {
        segments?: string[];
        aspect?: string;
        params?: Record<string, string>;
        replace?: boolean;
      }
    ) => {
      const url = buildAgentesePath(path, {
        segments: options?.segments,
        aspect: options?.aspect,
        params: options?.params,
      });

      navigate(url, { replace: options?.replace });
    },
    [navigate]
  );
}

/**
 * Hook to navigate to a simple AGENTESE path.
 *
 * Simpler than useAgenteseNavigate for basic navigation.
 *
 * Example:
 *   const goTo = useNavigateTo();
 *   goTo('world.town');           // → /world.town
 *   goTo('self.chat', 'stream');  // → /self.chat:stream
 */
export function useNavigateTo() {
  const navigate = useNavigate();

  return useCallback(
    (path: string, aspect?: string, replace?: boolean) => {
      const url = toUrl(path, { aspect });
      navigate(url, { replace });
    },
    [navigate]
  );
}

/**
 * Hook to check if current route matches an AGENTESE path pattern.
 *
 * Example:
 *   const isInChat = usePathMatch('self.chat');
 *   const isInTown = usePathMatch('world.town');
 */
export function usePathMatch(pattern: string): boolean {
  const currentPath = useAgentesePath();

  return useMemo(() => {
    if (!currentPath) {
      return false;
    }

    const patternSegments = pattern.split('.');
    const pathSegments = [currentPath.context, ...currentPath.path];

    // Match prefix
    if (patternSegments.length > pathSegments.length) {
      return false;
    }

    for (let i = 0; i < patternSegments.length; i++) {
      if (patternSegments[i] !== pathSegments[i]) {
        return false;
      }
    }

    return true;
  }, [currentPath, pattern]);
}

/**
 * Hook to extract parameters from current AGENTESE path.
 *
 * Example:
 *   // URL: /self.chat:stream?limit=20&offset=10
 *   const params = useAgenteseParams();
 *   console.log(params.limit);  // '20'
 *   console.log(params.offset); // '10'
 */
export function useAgenteseParams(): Record<string, string> {
  const currentPath = useAgentesePath();
  return currentPath?.params || {};
}

/**
 * Hook to extract current aspect from URL.
 *
 * Example:
 *   // URL: /self.chat:stream
 *   const aspect = useCurrentAspect();
 *   console.log(aspect); // 'stream'
 */
export function useCurrentAspect(): string | undefined {
  const currentPath = useAgentesePath();
  return currentPath?.aspect;
}

/**
 * Hook to get the entity ID from path (if present).
 *
 * Example:
 *   // URL: /world.town.citizen.kent_001
 *   const entityId = useEntityId();
 *   console.log(entityId); // 'kent_001'
 */
export function useEntityId(): string | null {
  const currentPath = useAgentesePath();

  if (!currentPath) {
    return null;
  }

  // Get last segment
  const lastSegment = currentPath.path[currentPath.path.length - 1];

  // Check if it's an entity ID (contains underscore)
  if (lastSegment && lastSegment.includes('_')) {
    return lastSegment;
  }

  return null;
}

/**
 * Hook to navigate back to parent path.
 *
 * Example:
 *   // Current: /world.town.citizen.kent_001
 *   const goBack = useNavigateUp();
 *   goBack(); // → /world.town.citizen
 */
export function useNavigateUp() {
  const currentPath = useAgentesePath();
  const navigate = useNavigate();

  return useCallback(() => {
    if (!currentPath || currentPath.path.length === 0) {
      // Already at top level, go to root
      navigate('/');
      return;
    }

    // Remove last segment
    const parentSegments = currentPath.path.slice(0, -1);

    if (parentSegments.length === 0) {
      // Go to context root
      navigate(`/${currentPath.context}`);
      return;
    }

    // Navigate to parent
    const parentPath = `${currentPath.context}.${parentSegments.join('.')}`;
    navigate(toUrl(parentPath));
  }, [currentPath, navigate]);
}

/**
 * Hook to get breadcrumb trail from current path.
 *
 * Example:
 *   // URL: /world.town.citizen.kent_001
 *   const breadcrumbs = useBreadcrumbs();
 *   // [
 *   //   { path: 'world', url: '/world' },
 *   //   { path: 'world.town', url: '/world.town' },
 *   //   { path: 'world.town.citizen', url: '/world.town.citizen' },
 *   //   { path: 'world.town.citizen.kent_001', url: '/world.town.citizen.kent_001' }
 *   // ]
 */
export function useBreadcrumbs(): Array<{ path: string; url: string; label: string }> {
  const currentPath = useAgentesePath();

  return useMemo(() => {
    if (!currentPath) {
      return [];
    }

    const breadcrumbs: Array<{ path: string; url: string; label: string }> = [];

    // Build breadcrumbs from context to current path
    let accumulated = currentPath.context;
    breadcrumbs.push({
      path: accumulated,
      url: `/${accumulated}`,
      label: currentPath.context,
    });

    for (let i = 0; i < currentPath.path.length; i++) {
      accumulated += `.${currentPath.path[i]}`;
      breadcrumbs.push({
        path: accumulated,
        url: `/${accumulated}`,
        label: currentPath.path[i],
      });
    }

    return breadcrumbs;
  }, [currentPath]);
}
