/**
 * Projection Registry
 *
 * Maps AGENTESE response types and path patterns to React components.
 *
 * Resolution priority:
 * 1. Exact response type match (from contracts)
 * 2. Path pattern match (most specific first)
 * 3. Generic fallback (ConceptHome)
 *
 * @see spec/protocols/agentese-as-route.md
 */

import { lazy } from 'react';
import type { ProjectionProps, ProjectionComponent, ProjectionContext } from './types';
import { matchPathPattern } from '@/utils/parseAgentesePath';

// === Lazy-loaded projection components ===
// These will be code-split for better initial load

// ConceptHomeProjection is the universal fallback (AD-010: Habitat Guarantee)
// GenericProjection is exported for pure JSON viewing when explicitly needed
const ConceptHomeProjection = lazy(() => import('./ConceptHomeProjection'));
export const GenericProjection = lazy(() => import('./GenericProjection'));

// Crown Jewel projections (lazy-loaded)
// These wrap existing page components as projections

const BrainProjection = lazy(() =>
  import('@/pages/Brain').then((m) => ({
    default: (_props: ProjectionProps) => {
      const Page = m.default;
      return <Page />;
    },
  }))
);

// Gallery - world.gallery showcase
const GalleryProjection = lazy(() =>
  import('@/pages/GalleryPage').then((m) => ({
    default: (_props: ProjectionProps) => {
      const Page = m.default;
      return <Page />;
    },
  }))
);

// === Registry Types ===

interface RegistryEntry {
  component: ProjectionComponent;
  priority: number;
}

// === Response Type Registry ===
// Maps contract response type names to components
// Priority: 100 (exact type match is highest priority)

const TYPE_REGISTRY = new Map<string, RegistryEntry>([
  // Brain
  ['MemoryCrystal', { component: BrainProjection, priority: 100 }],
  ['CrystalCartography', { component: BrainProjection, priority: 100 }],
  ['BrainManifest', { component: BrainProjection, priority: 100 }],
]);

// === Path Pattern Registry ===
// Maps AGENTESE path patterns to components
// Priority: based on specificity (more segments = higher priority)

const PATH_REGISTRY = new Map<string, RegistryEntry>([
  // Brain (self.memory.*) - core memory crown jewel
  ['self.memory.*', { component: BrainProjection, priority: 50 }],
  ['self.memory', { component: BrainProjection, priority: 40 }],

  // Gallery (world.gallery.*) - categorical showcase
  ['world.gallery.*', { component: GalleryProjection, priority: 50 }],
  ['world.gallery', { component: GalleryProjection, priority: 40 }],
]);

/**
 * Resolve the projection component for a given context
 *
 * @param context - Projection context with path, aspect, and response data
 * @returns The most appropriate projection component
 */
export function resolveProjection(context: ProjectionContext): ProjectionComponent {
  const { path, responseType } = context;

  // Collect all candidate matches with priorities
  const candidates: RegistryEntry[] = [];

  // 1. Check response type registry
  if (responseType) {
    const typeEntry = TYPE_REGISTRY.get(responseType);
    if (typeEntry) {
      candidates.push(typeEntry);
    }
  }

  // 2. Check path pattern registry
  for (const [pattern, entry] of PATH_REGISTRY) {
    if (matchPathPattern(pattern, path)) {
      candidates.push(entry);
    }
  }

  // 3. Return highest priority match or ConceptHome fallback
  // ConceptHomeProjection implements AD-010: The Habitat Guarantee
  // Every path gets a home, not just a JSON dump
  if (candidates.length === 0) {
    return ConceptHomeProjection;
  }

  const bestMatch = candidates.reduce((best, current) =>
    current.priority > best.priority ? current : best
  );

  return bestMatch.component;
}

/**
 * Register a custom projection for a response type
 *
 * @param responseType - Contract response type name
 * @param component - React component to render
 * @param priority - Resolution priority (default: 100)
 */
export function registerTypeProjection(
  responseType: string,
  component: ProjectionComponent,
  priority = 100
): void {
  TYPE_REGISTRY.set(responseType, { component, priority });
}

/**
 * Register a custom projection for a path pattern
 *
 * @param pattern - AGENTESE path pattern (e.g., "self.memory.*")
 * @param component - React component to render
 * @param priority - Resolution priority (higher = more specific)
 */
export function registerPathProjection(
  pattern: string,
  component: ProjectionComponent,
  priority?: number
): void {
  // Auto-calculate priority based on pattern specificity
  const calculatedPriority = priority ?? pattern.split('.').length * 10 + (pattern.includes('*') ? 0 : 5);
  PATH_REGISTRY.set(pattern, { component, priority: calculatedPriority });
}

/**
 * Get all registered path patterns
 */
export function getRegisteredPatterns(): string[] {
  return [...PATH_REGISTRY.keys()];
}

/**
 * Get all registered response types
 */
export function getRegisteredTypes(): string[] {
  return [...TYPE_REGISTRY.keys()];
}
