/**
 * Projection Registry
 *
 * Maps AGENTESE response types and path patterns to React components.
 *
 * Resolution priority:
 * 1. Exact response type match (from contracts)
 * 2. Path pattern match (most specific first)
 * 3. Generic fallback (JSON viewer)
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

const GardenerProjection = lazy(() =>
  import('@/pages/Gardener').then((m) => ({
    default: (_props: ProjectionProps) => {
      const Page = m.default;
      return <Page />;
    },
  }))
);

const ForgeProjection = lazy(() =>
  import('@/pages/Forge').then((m) => ({
    default: (_props: ProjectionProps) => {
      const Page = m.default;
      return <Page />;
    },
  }))
);

const DifferanceProjection = lazy(() =>
  import('@/pages/Differance').then((m) => ({
    default: (_props: ProjectionProps) => {
      const Page = m.default;
      return <Page />;
    },
  }))
);

const GestaltProjection = lazy(() =>
  import('@/pages/Gestalt').then((m) => ({
    default: (_props: ProjectionProps) => {
      const Page = m.default;
      return <Page />;
    },
  }))
);

const TownProjection = lazy(() =>
  import('@/pages/TownOverviewPage').then((m) => ({
    default: (_props: ProjectionProps) => {
      const Page = m.default;
      return <Page />;
    },
  }))
);

const TownCitizensProjection = lazy(() =>
  import('@/pages/TownCitizensPage').then((m) => ({
    default: (_props: ProjectionProps) => {
      const Page = m.default;
      return <Page />;
    },
  }))
);

const TownCoalitionsProjection = lazy(() =>
  import('@/pages/TownCoalitionsPage').then((m) => ({
    default: (_props: ProjectionProps) => {
      const Page = m.default;
      return <Page />;
    },
  }))
);

// Town Simulation - uses query params (townId)
const TownSimulationProjection = lazy(() =>
  import('@/pages/Town').then((m) => ({
    default: (_props: ProjectionProps) => {
      const Page = m.default;
      return <Page />;
    },
  }))
);

// Inhabit - uses query params (citizenId)
const InhabitProjection = lazy(() =>
  import('@/pages/Inhabit').then((m) => ({
    default: (_props: ProjectionProps) => {
      const Page = m.default;
      return <Page />;
    },
  }))
);

const ParkProjection = lazy(() =>
  import('@/pages/ParkScenario').then((m) => ({
    default: (_props: ProjectionProps) => {
      const Page = m.default;
      return <Page />;
    },
  }))
);

// Cockpit - Kent's developer portal
const CockpitProjection = lazy(() =>
  import('@/pages/Cockpit').then((m) => ({
    default: (_props: ProjectionProps) => {
      const Page = m.default;
      return <Page />;
    },
  }))
);

// Garden - self.garden state manager (complementary to Gardener orchestrator)
const GardenProjection = lazy(() =>
  import('@/pages/Garden').then((m) => ({
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

// Workshop - world.workshop event-driven builder
const WorkshopProjection = lazy(() =>
  import('@/pages/Workshop').then((m) => ({
    default: (_props: ProjectionProps) => {
      const Page = m.default;
      return <Page />;
    },
  }))
);

// Chat - self.chat conversational interface
const ChatProjection = lazy(() =>
  import('@/pages/ChatPage').then((m) => ({
    default: (_props: ProjectionProps) => {
      const Page = m.default;
      return <Page />;
    },
  }))
);

// Soul - self.soul K-gent personality and dialogue
const SoulProjection = lazy(() =>
  import('@/pages/Soul').then((m) => ({
    default: (_props: ProjectionProps) => {
      const Page = m.default;
      return <Page />;
    },
  }))
);

// Design System - concept.design categorical design language
const DesignSystemProjection = lazy(() =>
  import('@/pages/DesignSystem').then((m) => ({
    default: (_props: ProjectionProps) => {
      const Page = m.default;
      return <Page />;
    },
  }))
);

// Emergence - world.emergence Cymatics Design Experience
const EmergenceProjection = lazy(() =>
  import('@/pages/Emergence').then((m) => ({
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

  // Gardener
  ['GardenerSession', { component: GardenerProjection, priority: 100 }],
  ['GardenerPlot', { component: GardenerProjection, priority: 100 }],

  // Forge
  ['ForgeCommission', { component: ForgeProjection, priority: 100 }],
  ['ForgeArtisan', { component: ForgeProjection, priority: 100 }],

  // Differance
  ['DifferanceTrace', { component: DifferanceProjection, priority: 100 }],
  ['GhostHeritageDAG', { component: DifferanceProjection, priority: 100 }],

  // Town
  ['CitizenManifest', { component: TownCitizensProjection, priority: 100 }],
  ['CitizenList', { component: TownCitizensProjection, priority: 100 }],
  ['CoalitionManifest', { component: TownCoalitionsProjection, priority: 100 }],
  ['TownManifest', { component: TownProjection, priority: 100 }],

  // Gestalt
  ['GestaltTopology', { component: GestaltProjection, priority: 100 }],
  ['GestaltLayer', { component: GestaltProjection, priority: 100 }],

  // Soul
  ['SoulManifestResponse', { component: SoulProjection, priority: 100 }],
  ['EigenvectorsResponse', { component: SoulProjection, priority: 100 }],
  ['DialogueResponse', { component: SoulProjection, priority: 100 }],
  ['StartersResponse', { component: SoulProjection, priority: 100 }],

  // Design System
  ['LayoutOperadManifest', { component: DesignSystemProjection, priority: 100 }],
  ['ContentOperadManifest', { component: DesignSystemProjection, priority: 100 }],
  ['MotionOperadManifest', { component: DesignSystemProjection, priority: 100 }],
  ['DesignOperadManifest', { component: DesignSystemProjection, priority: 100 }],

  // Emergence
  ['EmergenceManifest', { component: EmergenceProjection, priority: 100 }],
  ['EmergenceQualia', { component: EmergenceProjection, priority: 100 }],
  ['EmergenceCircadian', { component: EmergenceProjection, priority: 100 }],
]);

// === Path Pattern Registry ===
// Maps AGENTESE path patterns to components
// Priority: based on specificity (more segments = higher priority)

const PATH_REGISTRY = new Map<string, RegistryEntry>([
  // Cockpit (self.cockpit) - Kent's developer portal
  ['self.cockpit', { component: CockpitProjection, priority: 60 }],

  // Brain (self.memory.*)
  ['self.memory.*', { component: BrainProjection, priority: 50 }],
  ['self.memory', { component: BrainProjection, priority: 40 }],

  // Gardener (concept.gardener.*)
  ['concept.gardener.*', { component: GardenerProjection, priority: 50 }],
  ['concept.gardener', { component: GardenerProjection, priority: 40 }],

  // Forge (world.forge.*)
  ['world.forge.*', { component: ForgeProjection, priority: 50 }],
  ['world.forge', { component: ForgeProjection, priority: 40 }],

  // Differance (time.differance.*)
  ['time.differance.*', { component: DifferanceProjection, priority: 50 }],
  ['time.differance', { component: DifferanceProjection, priority: 40 }],

  // Gestalt (world.codebase.*)
  ['world.codebase.*', { component: GestaltProjection, priority: 50 }],
  ['world.codebase', { component: GestaltProjection, priority: 40 }],

  // Town (world.town.*)
  // Simulation and Inhabit get highest priority (specific paths with query params)
  ['world.town.simulation', { component: TownSimulationProjection, priority: 65 }],
  ['world.town.inhabit', { component: InhabitProjection, priority: 65 }],
  // Entity paths
  ['world.town.citizen.*', { component: TownCitizensProjection, priority: 60 }],
  ['world.town.citizen', { component: TownCitizensProjection, priority: 55 }],
  ['world.town.coalition.*', { component: TownCoalitionsProjection, priority: 60 }],
  ['world.town.coalition', { component: TownCoalitionsProjection, priority: 55 }],
  ['world.town.*', { component: TownProjection, priority: 50 }],
  ['world.town', { component: TownProjection, priority: 40 }],

  // Park (world.park.*)
  ['world.park.*', { component: ParkProjection, priority: 50 }],
  ['world.park', { component: ParkProjection, priority: 40 }],

  // Garden (self.garden.*) - state manager for garden lifecycle
  ['self.garden.*', { component: GardenProjection, priority: 50 }],
  ['self.garden', { component: GardenProjection, priority: 40 }],

  // Forest (self.forest.*) - project health, plans, sessions (Garden Protocol)
  ['self.forest.plan.**', { component: GardenerProjection, priority: 60 }],
  ['self.forest.session.**', { component: GardenerProjection, priority: 60 }],
  ['self.forest.*', { component: GardenerProjection, priority: 50 }],
  ['self.forest', { component: GardenerProjection, priority: 40 }],

  // Differance (self.differance.*) - self-context différance traces
  ['self.differance.*', { component: DifferanceProjection, priority: 50 }],
  ['self.differance', { component: DifferanceProjection, priority: 40 }],

  // Gallery (world.gallery.*) - categorical showcase
  ['world.gallery.*', { component: GalleryProjection, priority: 50 }],
  ['world.gallery', { component: GalleryProjection, priority: 40 }],

  // Workshop (world.workshop.*) - event-driven builder
  ['world.workshop.*', { component: WorkshopProjection, priority: 50 }],
  ['world.workshop', { component: WorkshopProjection, priority: 40 }],

  // Chat (self.chat.*) - conversational interface
  ['self.chat.*', { component: ChatProjection, priority: 50 }],
  ['self.chat', { component: ChatProjection, priority: 40 }],

  // Soul (self.soul.*) - K-gent personality and dialogue
  ['self.soul.*', { component: SoulProjection, priority: 50 }],
  ['self.soul', { component: SoulProjection, priority: 40 }],

  // Design System (concept.design.*) - categorical design language
  ['concept.design.*', { component: DesignSystemProjection, priority: 50 }],
  ['concept.design', { component: DesignSystemProjection, priority: 40 }],
  ['concept.design.layout', { component: DesignSystemProjection, priority: 55 }],
  ['concept.design.content', { component: DesignSystemProjection, priority: 55 }],
  ['concept.design.motion', { component: DesignSystemProjection, priority: 55 }],
  ['concept.design.operad', { component: DesignSystemProjection, priority: 55 }],

  // Emergence (world.emergence.*) - Cymatics Design Experience
  ['world.emergence.*', { component: EmergenceProjection, priority: 50 }],
  ['world.emergence', { component: EmergenceProjection, priority: 40 }],
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
 * @param pattern - AGENTESE path pattern (e.g., "world.town.citizen.*")
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
