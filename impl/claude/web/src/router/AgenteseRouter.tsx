/**
 * AGENTESE Router: The Universal Projection Handler
 *
 * Philosophy:
 * "There is no routing layer. There is only AGENTESE invocation and projection."
 *
 * This replaces traditional React Router with a single universal handler
 * that interprets AGENTESE paths and renders appropriate projections.
 */

import React, { Suspense } from 'react';
import { Routes, Route, useLocation, Navigate } from 'react-router-dom';
import { AnimatePresence } from 'framer-motion';
import { parseAgentesePath, type AgentesePath } from './AgentesePath';
import { ErrorBoundary } from '../components/error/ErrorBoundary';
import { PageTransition, PersonalityLoading } from '../components/joy';

/**
 * Path-to-component mapping.
 *
 * This is the ONLY place where we map AGENTESE paths to React components.
 * No duplicate route definitions, no manual URL mapping.
 */
interface PathMapping {
  /** Path pattern (supports wildcards) */
  pattern: string | RegExp;

  /** Component to render */
  component: React.LazyExoticComponent<React.ComponentType<any>>;

  /** Optional shell wrapper */
  shell?: 'telescope' | 'app' | 'none';

  /** Description for discovery */
  description?: string;
}

/**
 * Lazy-loaded page components.
 */
const ChatPage = React.lazy(() => import('../pages/ChatPage'));
const HypergraphEditorPage = React.lazy(() =>
  import('../pages/HypergraphEditorPage').then((m) => ({ default: m.HypergraphEditorPage }))
);
const ZeroSeedPage = React.lazy(() => import('../pages/ZeroSeedPage'));
const DirectorPage = React.lazy(() => import('../pages/DirectorPage'));
const FeedPage = React.lazy(() => import('../pages/FeedPage'));
const ChartPage = React.lazy(() => import('../pages/ChartPage'));
const WelcomePage = React.lazy(() => import('../pages/WelcomePage'));

/**
 * AGENTESE path mappings.
 *
 * Order matters: first match wins.
 */
const PATH_MAPPINGS: PathMapping[] = [
  // Self context (agent-internal)
  {
    pattern: /^self\.chat/,
    component: ChatPage,
    shell: 'app',
    description: 'Conversational interface with branching and tools',
  },
  {
    pattern: /^self\.memory/,
    component: FeedPage,
    shell: 'app',
    description: 'Memory exploration (crystals, teaching, wisdom)',
  },
  {
    pattern: /^self\.director/,
    component: DirectorPage,
    shell: 'app',
    description: 'Living document canvas (Document Director)',
  },

  // World context (external entities)
  {
    pattern: /^world\.document/,
    component: HypergraphEditorPage,
    shell: 'app',
    description: 'Hypergraph Emacs for spec navigation/editing',
  },
  {
    pattern: /^world\.chart/,
    component: ChartPage,
    shell: 'app',
    description: 'Astronomical visualization',
  },

  // Void context (accursed share)
  {
    pattern: /^void\.telescope/,
    component: ZeroSeedPage,
    shell: 'telescope',
    description: 'Epistemic graph navigation with telescope',
  },
];

/**
 * Legacy route redirects for backward compatibility.
 *
 * Phase 3: Pure AGENTESE - All legacy routes redirect with deprecation toast.
 */
const LEGACY_REDIRECTS: Record<string, string> = {
  '/brain': '/self.memory',
  '/chat': '/self.chat',
  '/director': '/self.director',
  '/editor': '/world.document',
  '/hypergraph-editor': '/world.document',
  '/chart': '/world.chart',
  '/feed': '/self.memory',
  '/proof-engine': '/void.telescope',
  '/zero-seed': '/void.telescope',
};

/**
 * Find matching component for AGENTESE path.
 */
function findPathMapping(path: AgentesePath): PathMapping | null {
  const fullPath = path.fullPath;

  for (const mapping of PATH_MAPPINGS) {
    if (typeof mapping.pattern === 'string') {
      if (fullPath.startsWith(mapping.pattern)) {
        return mapping;
      }
    } else {
      if (mapping.pattern.test(fullPath)) {
        return mapping;
      }
    }
  }

  return null;
}

/**
 * Universal projection handler.
 *
 * Parses AGENTESE path from URL and renders appropriate component.
 */
function UniversalProjection() {
  const location = useLocation();

  // Try to parse as AGENTESE path
  try {
    const path = parseAgentesePath(location.pathname);
    const mapping = findPathMapping(path);

    if (!mapping) {
      return (
        <div className="flex items-center justify-center min-h-screen bg-surface-canvas">
          <div className="text-center">
            <h1 className="text-2xl font-bold mb-4">Path Not Found</h1>
            <code className="bg-surface-overlay px-3 py-1 rounded text-sm">
              {path.fullPath}
            </code>
            <p className="mt-4 text-text-secondary">
              This AGENTESE path doesn't have a projection yet.
            </p>
            <p className="mt-2 text-sm text-text-tertiary">
              Context: <span className="font-mono">{path.context}</span>
            </p>
          </div>
        </div>
      );
    }

    const Component = mapping.component;

    return (
      <Suspense fallback={<LoadingFallback />}>
        <Component agenteseContext={path} />
      </Suspense>
    );
  } catch (error) {
    // Not a valid AGENTESE path
    return (
      <div className="flex items-center justify-center min-h-screen bg-surface-canvas">
        <div className="text-center">
          <h1 className="text-2xl font-bold mb-4">Invalid Path</h1>
          <code className="bg-surface-overlay px-3 py-1 rounded text-sm">
            {location.pathname}
          </code>
          <p className="mt-4 text-text-secondary">
            This URL is not a valid AGENTESE path.
          </p>
          <p className="mt-2 text-sm text-text-tertiary">
            AGENTESE paths must start with a context: world, self, concept, void, or time
          </p>
        </div>
      </div>
    );
  }
}

/**
 * Loading fallback with personality.
 */
function LoadingFallback() {
  return (
    <div className="flex items-center justify-center min-h-screen bg-surface-canvas">
      <PersonalityLoading jewel="brain" size="lg" action="connect" />
    </div>
  );
}

/**
 * Legacy redirect component with deprecation warning and toast.
 * Preserves query parameters during redirect.
 */
function LegacyRedirect({ from, to }: { from: string; to: string }) {
  const location = useLocation();

  React.useEffect(() => {
    console.warn(`[Deprecated Route] ${from} → ${to}`);
    console.warn('Legacy routes are deprecated. Please update your bookmarks to use AGENTESE paths.');

    // Show deprecation toast (if toast system available)
    const message = `Redirected from deprecated route ${from} to ${to}. Please update your bookmarks.`;
    console.info(message);
  }, [from, to]);

  // Preserve query parameters
  const targetPath = location.search ? `${to}${location.search}` : to;

  return <Navigate to={targetPath} replace />;
}

/**
 * Welcome screen (root path).
 */
function WelcomeScreen() {
  return (
    <div className="membrane membrane--comfortable">
      <Suspense fallback={<LoadingFallback />}>
        <WelcomePage />
      </Suspense>
    </div>
  );
}

/**
 * Main AGENTESE Router component.
 *
 * Replaces traditional <Routes> with AGENTESE-aware routing.
 */
export function AgenteseRouter() {
  const location = useLocation();

  return (
    <ErrorBoundary resetKeys={[location.pathname]}>
      <AnimatePresence mode="wait" initial={false}>
        <PageTransition key={location.pathname} variant="fade">
          <Routes location={location}>
            {/* Root - Welcome screen */}
            <Route path="/" element={<WelcomeScreen />} />

            {/* Legacy redirects (Phase 3: Pure AGENTESE - all redirect) */}
            {Object.entries(LEGACY_REDIRECTS).map(([from, to]) => (
              <Route
                key={from}
                path={from}
                element={<LegacyRedirect from={from} to={to} />}
              />
            ))}

            {/* Special route for world.document with file paths */}
            {/* This bypasses AGENTESE parsing since file paths use slashes, not dots */}
            <Route
              path="/world.document/*"
              element={
                <Suspense fallback={<LoadingFallback />}>
                  <HypergraphEditorPage />
                </Suspense>
              }
            />
            <Route
              path="/world.document"
              element={
                <Suspense fallback={<LoadingFallback />}>
                  <HypergraphEditorPage />
                </Suspense>
              }
            />

            {/* Universal AGENTESE handler */}
            <Route path="/*" element={<UniversalProjection />} />
          </Routes>
        </PageTransition>
      </AnimatePresence>
    </ErrorBoundary>
  );
}

/**
 * Export path mappings for discovery/documentation.
 */
export function getPathMappings(): PathMapping[] {
  return PATH_MAPPINGS;
}

/**
 * Check if a URL is a legacy route.
 */
export function isLegacyRoute(pathname: string): boolean {
  return pathname in LEGACY_REDIRECTS;
}

/**
 * Get AGENTESE path for legacy route.
 */
export function getLegacyRedirect(pathname: string): string | null {
  return LEGACY_REDIRECTS[pathname] || null;
}
