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
 *
 * UX TRANSFORMATION (2025-12-25):
 * "The Hypergraph Editor IS the app. Everything else is a sidebar."
 *
 * Deleted pages: WelcomePage, ZeroSeedPage, ChartPage, FeedPage, ValueCompassTestPage
 * ChatPage and DirectorPage are now EMBEDDED as sidebars in the Workspace.
 *
 * The only remaining page is HypergraphEditorPage (the Workspace with sidebars).
 *
 * GENESIS FTUE (2025-12-25):
 * First-time user experience for witnessing Genesis and creating first K-Block.
 */
const HypergraphEditorPage = React.lazy(() =>
  import('../pages/HypergraphEditorPage').then((m) => ({ default: m.HypergraphEditorPage }))
);

// Genesis FTUE pages (full flow)
const GenesisPage = React.lazy(() =>
  import('../pages/Genesis').then((m) => ({ default: m.GenesisPage }))
);
const FirstQuestion = React.lazy(() =>
  import('../pages/Genesis').then((m) => ({ default: m.FirstQuestion }))
);
const WelcomeToStudio = React.lazy(() =>
  import('../pages/Genesis').then((m) => ({ default: m.WelcomeToStudio }))
);
const JudgmentExperience = React.lazy(() =>
  import('../pages/Genesis').then((m) => ({ default: m.JudgmentExperience }))
);
const GrowthWitness = React.lazy(() =>
  import('../pages/Genesis').then((m) => ({ default: m.GrowthWitness }))
);

// Genesis Experience - NEW unified Constitutional Graph-first experience (2026-01)
// This is the canonical /genesis route - unified 5-phase experience
const GenesisExperience = React.lazy(() =>
  import('../pages/Genesis/GenesisExperience').then((m) => ({ default: m.GenesisExperience }))
);

// FeedPage (full-screen chronological truth stream)
const FeedPage = React.lazy(() =>
  import('../pages/FeedPage').then((m) => ({ default: m.FeedPage }))
);

// Meta page (Journey 5: Watching Yourself Grow)
const MetaPage = React.lazy(() =>
  import('../pages/MetaPage').then((m) => ({ default: m.MetaPage }))
);

// Contradiction Workspace (focused dialectical resolution)
const ContradictionWorkspacePage = React.lazy(() =>
  import('../pages/ContradictionWorkspacePage').then((m) => ({
    default: m.ContradictionWorkspacePage,
  }))
);

// TangibleSurface (Self-Reflective OS interface)
const TangibleSurface = React.lazy(() =>
  import('../pages/Tangible').then((m) => ({ default: m.TangibleSurface }))
);

/**
 * AGENTESE path mappings.
 *
 * Order matters: first match wins.
 *
 * UX LAW: "The Hypergraph Editor IS the app."
 * - world.document is THE route (the Workspace with sidebars)
 * - self.chat and self.director are now embedded sidebars (redirect to editor)
 * - Deleted: self.memory (FeedPage), world.chart (ChartPage), void.telescope (ZeroSeedPage)
 */
const PATH_MAPPINGS: PathMapping[] = [
  // World context — THE APP (Workspace with Chat and Files sidebars)
  {
    pattern: /^world\.document/,
    component: HypergraphEditorPage,
    shell: 'app',
    description: 'Hypergraph Editor — THE application (with Chat and Files sidebars)',
  },

  // Self context — Meta reflection
  {
    pattern: /^self\.meta/,
    component: MetaPage,
    shell: 'app',
    description: 'Meta — Journey 5: Watching Yourself Grow (coherence timeline)',
  },

  // Self context — Tangible surface (Self-Reflective OS)
  {
    pattern: /^self\.tangible/,
    component: TangibleSurface,
    shell: 'app',
    description:
      'Tangible — Self-Reflective OS: Constitutional introspection and decision tracking',
  },

  // World context — Contradiction workspace
  {
    pattern: /^world\.contradiction/,
    component: ContradictionWorkspacePage,
    shell: 'app',
    description: 'Contradiction Workspace — Focused dialectical resolution',
  },

  // Deleted routes (no longer mapped):
  // - self.memory (FeedPage deleted)
  // - world.chart (ChartPage deleted)
  // - void.telescope (ZeroSeedPage deleted)
  // - self.chat (now embedded as right sidebar in Workspace)
  // - self.director (now embedded as left sidebar in Workspace)
];

/**
 * Legacy route redirects for backward compatibility.
 *
 * UX TRANSFORMATION (2025-12-25):
 * "The Hypergraph Editor IS the app. Everything else is a sidebar."
 *
 * ALL legacy routes now redirect to /world.document (the Workspace).
 * Chat and Director are now sidebars in the Workspace, not separate pages.
 *
 * DEPRECATION NOTICE: These routes are deprecated and will be removed in a future release.
 * Please update all bookmarks and links to use AGENTESE paths directly.
 */
interface LegacyRedirectConfig {
  to: string;
  hint?: string; // Keyboard shortcut hint for sidebar features
}

const LEGACY_REDIRECTS: Record<string, LegacyRedirectConfig> = {
  // Brain/Feed redirects
  '/brain': { to: '/self.feed' },
  '/feed': { to: '/self.feed' },

  // Chat redirects (now a sidebar)
  '/chat': { to: '/world.document', hint: 'Chat is now a sidebar. Use Ctrl+J to toggle.' },
  '/self.chat': { to: '/world.document', hint: 'Chat is now a sidebar. Use Ctrl+J to toggle.' },

  // Director/Files redirects (now a sidebar)
  '/director': {
    to: '/world.document',
    hint: 'Files browser is now a sidebar. Use Ctrl+B to toggle.',
  },
  '/self.director': {
    to: '/world.document',
    hint: 'Files browser is now a sidebar. Use Ctrl+B to toggle.',
  },

  // Editor redirects
  '/editor': { to: '/world.document' },
  '/hypergraph-editor': { to: '/world.document' },

  // Removed features → fallback
  '/chart': { to: '/world.document' },
  '/proof-engine': { to: '/genesis' },
  '/zero-seed': { to: '/genesis' },
  '/genesis/showcase': { to: '/genesis' },

  // Meta redirect (AGENTESE canonical)
  '/meta': { to: '/self.meta' },

  // Studio redirect (consolidated into Editor)
  '/studio': {
    to: '/world.document',
    hint: 'Studio has been unified with the Editor. Use /world.document for the full workspace experience.',
  },
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
            <code className="bg-surface-overlay px-3 py-1 rounded text-sm">{path.fullPath}</code>
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
          <code className="bg-surface-overlay px-3 py-1 rounded text-sm">{location.pathname}</code>
          <p className="mt-4 text-text-secondary">This URL is not a valid AGENTESE path.</p>
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
function LegacyRedirect({ from, config }: { from: string; config: LegacyRedirectConfig }) {
  const location = useLocation();
  const { to, hint } = config;

  React.useEffect(() => {
    // Group deprecation warnings for cleaner console
    console.groupCollapsed(`[DEPRECATED ROUTE] ${from} → ${to}`);
    console.warn('This route is deprecated and will be removed in a future release.');
    console.warn('Please update your bookmarks to use AGENTESE paths directly.');
    if (hint) {
      console.info(`TIP: ${hint}`);
    }
    console.groupEnd();
  }, [from, to, hint]);

  // Preserve query parameters
  const targetPath = location.search ? `${to}${location.search}` : to;

  return <Navigate to={targetPath} replace />;
}

// WelcomeScreen DELETED — UX LAW: "No welcome page. App opens directly to editor."

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
            {/* Root - Check onboarding status, redirect to Genesis or editor */}
            <Route path="/" element={<Navigate to="/world.document" replace />} />

            {/* Genesis Experience - NEW canonical /genesis route (2026-01) */}
            {/* Unified Constitutional Graph-first 5-phase experience */}
            <Route
              path="/genesis"
              element={
                <Suspense fallback={<LoadingFallback />}>
                  <GenesisExperience />
                </Suspense>
              }
            />

            {/* Legacy Genesis FTUE routes (redirect to new experience or showcase) */}
            <Route
              path="/genesis/legacy"
              element={
                <Suspense fallback={<LoadingFallback />}>
                  <GenesisPage />
                </Suspense>
              }
            />
            <Route
              path="/genesis/first-question"
              element={
                <Suspense fallback={<LoadingFallback />}>
                  <FirstQuestion />
                </Suspense>
              }
            />
            <Route
              path="/genesis/first-kblock"
              element={
                <Suspense fallback={<LoadingFallback />}>
                  <WelcomeToStudio />
                </Suspense>
              }
            />
            <Route
              path="/genesis/judgment"
              element={
                <Suspense fallback={<LoadingFallback />}>
                  <JudgmentExperience />
                </Suspense>
              }
            />
            <Route
              path="/genesis/growth-witness"
              element={
                <Suspense fallback={<LoadingFallback />}>
                  <GrowthWitness />
                </Suspense>
              }
            />

            {/* FeedPage - Full-screen chronological truth stream */}
            <Route
              path="/self.feed"
              element={
                <Suspense fallback={<LoadingFallback />}>
                  <FeedPage />
                </Suspense>
              }
            />

            {/* Legacy redirects (Phase 3: Pure AGENTESE - all redirect) */}
            {/* NOTE: /meta is included in LEGACY_REDIRECTS, no separate route needed */}
            {Object.entries(LEGACY_REDIRECTS).map(([from, config]) => (
              <Route
                key={from}
                path={from}
                element={<LegacyRedirect from={from} config={config} />}
              />
            ))}

            {/* Meta page (Journey 5: Watching Yourself Grow) */}
            <Route
              path="/self.meta"
              element={
                <Suspense fallback={<LoadingFallback />}>
                  <MetaPage />
                </Suspense>
              }
            />

            {/* Tangible Surface (Self-Reflective OS) */}
            <Route
              path="/self.tangible"
              element={
                <Suspense fallback={<LoadingFallback />}>
                  <TangibleSurface />
                </Suspense>
              }
            />

            {/* Contradiction Workspace (focused dialectical resolution) */}
            <Route
              path="/world.contradiction/:id"
              element={
                <Suspense fallback={<LoadingFallback />}>
                  <ContradictionWorkspacePage />
                </Suspense>
              }
            />
            <Route
              path="/world.contradiction"
              element={
                <Suspense fallback={<LoadingFallback />}>
                  <ContradictionWorkspacePage />
                </Suspense>
              }
            />

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
  const config = LEGACY_REDIRECTS[pathname];
  return config?.to || null;
}

/**
 * Get full redirect config for legacy route (includes hints).
 */
export function getLegacyRedirectConfig(pathname: string): LegacyRedirectConfig | null {
  return LEGACY_REDIRECTS[pathname] || null;
}
