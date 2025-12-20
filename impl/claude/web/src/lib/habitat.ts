/**
 * Concept Home Protocol (AD-010) - Frontend Tier Determination
 *
 * The Habitat Guarantee: Every AGENTESE path deserves a home.
 * Tier is computed at render time from existing AGENTESE metadata.
 *
 * "The seams disappear when every path has somewhere to go."
 *
 * @see spec/principles.md - AD-010: The Habitat Guarantee
 * @see plans/concept-home-implementation.md
 */

// =============================================================================
// Types
// =============================================================================

/**
 * Habitat tiers determine the experience level for each path.
 * - minimal: Path only - warm "cultivating" copy + REPL input
 * - standard: Description + aspects - Reference Panel + seeded REPL
 * - rich: Custom playground - Full bespoke visualization (Crown Jewels)
 */
export type HabitatTier = 'minimal' | 'standard' | 'rich';

/**
 * AGENTESE contexts - the five ontological domains.
 * @see spec/protocols/agentese.md
 */
export type AGENTESEContext = 'world' | 'self' | 'concept' | 'void' | 'time';

// =============================================================================
// Rich Path Registry
// =============================================================================

/**
 * Paths with custom playground components (rich tier).
 * Maps AGENTESE path → playground component name.
 *
 * These paths have dedicated visualizations in the Crown Jewel pages.
 * AGENTESE-as-Route: The URL IS the AGENTESE path.
 */
export const RICH_PATHS: Record<string, { component: string; route: string }> = {
  'self.memory': { component: 'CrystalViewer', route: '/self.memory' },
  'self.chat': { component: 'ChatPanel', route: '/self.memory' },
  'world.codebase': { component: 'GestaltTree', route: '/world.codebase' },
  'world.town': { component: 'TownVisualization', route: '/world.town' },
  'world.town.citizen': { component: 'CitizenBrowser', route: '/world.town.citizen' },
  'world.town.coalition': { component: 'CoalitionGraph', route: '/world.town.coalition' },
  'world.town.simulation': { component: 'TownSimulation', route: '/world.town.simulation' },
  'world.park': { component: 'ParkVisualization', route: '/world.park' },
  'world.forge': { component: 'ForgeVisualization', route: '/world.forge' },
  'concept.gardener': { component: 'GardenerVisualization', route: '/concept.gardener' },
  'concept.gardener.session': { component: 'GardenVisualization', route: '/self.garden' },
  'time.differance': { component: 'DifferanceGraph', route: '/time.differance' },
};

// =============================================================================
// Helper Functions
// =============================================================================

/**
 * Extract context from an AGENTESE path.
 * The context is always the first segment.
 *
 * @example
 * extractContext('world.town.citizen') // → 'world'
 * extractContext('self.memory.capture') // → 'self'
 */
export function extractContext(path: string): AGENTESEContext {
  const first = path.split('.')[0];
  if (['world', 'self', 'concept', 'void', 'time'].includes(first)) {
    return first as AGENTESEContext;
  }
  // Default to 'world' for unknown contexts
  return 'world';
}

/**
 * Determine habitat tier from node metadata.
 * Tier is a projection concern - computed at render time, not stored.
 *
 * The algorithm:
 * 1. If path has custom visualization (RICH_PATHS) → rich
 * 2. If path has description AND aspects → standard
 * 3. Otherwise → minimal
 *
 * @example
 * determineTier('self.memory', 'Memory crystal storage', ['capture', 'recall']) // → 'rich'
 * determineTier('world.tool.new', 'A new tool', ['invoke']) // → 'standard'
 * determineTier('void.entropy.sip', null, []) // → 'minimal'
 */
export function determineTier(
  path: string,
  description?: string | null,
  aspects?: string[]
): HabitatTier {
  // Rich tier: has custom playground
  if (RICH_PATHS[path]) {
    return 'rich';
  }

  // Standard tier: has meaningful metadata
  if (description && aspects && aspects.length > 0) {
    return 'standard';
  }

  // Minimal tier: path is being cultivated
  return 'minimal';
}

/**
 * Get custom playground info for a rich-tier path.
 * Returns null if path doesn't have a custom visualization.
 *
 * @example
 * getPlayground('self.memory') // → { component: 'CrystalViewer', route: '/self.memory' }
 * getPlayground('void.entropy') // → null
 */
export function getPlayground(path: string): { component: string; route: string } | null {
  return RICH_PATHS[path] ?? null;
}

/**
 * Check if a path has a custom visualization (is rich tier).
 */
export function hasCustomPlayground(path: string): boolean {
  return path in RICH_PATHS;
}

/**
 * Get the route for a rich-tier path.
 * Returns the home route if not a rich path.
 */
export function getRouteForPath(path: string): string {
  const playground = RICH_PATHS[path];
  if (playground) {
    return playground.route;
  }
  // Convert AGENTESE path to URL path for ConceptHome
  // world.town.citizen → /home/world/town/citizen
  return `/home/${path.replace(/\./g, '/')}`;
}

/**
 * Convert a URL path segment back to AGENTESE path.
 * /home/world/town/citizen → world.town.citizen
 */
export function urlToAgentesePath(urlPath: string): string {
  // Remove /home/ prefix if present
  const withoutPrefix = urlPath.replace(/^\/home\//, '');
  // Convert / to .
  return withoutPrefix.replace(/\//g, '.');
}

// =============================================================================
// Warm Copy for Minimal Tier
// =============================================================================

/**
 * Warm, cultivating copy for paths without documentation.
 * These messages make minimal-tier paths feel intentional, not broken.
 *
 * "Minimal tier feels like 'arriving' not 'hitting a wall'"
 * — AD-010: The Habitat Guarantee
 */
export const MINIMAL_TIER_COPY = {
  heading: 'This path is being cultivated',
  body: `Every kgents path grows from a seed. This one is young—its documentation and visualizations are still forming.

You can still explore it directly via the REPL below.`,
  cta: 'Try invoking it',
} as const;

/**
 * Get context-specific cultivation message.
 * Each context has its own metaphor for growth.
 */
export function getCultivationMessage(context: AGENTESEContext): string {
  const messages: Record<AGENTESEContext, string> = {
    world: 'This worldly path is still taking shape in the external realm.',
    self: 'This internal capability is being refined.',
    concept: 'This abstract definition is crystallizing.',
    void: 'This entropic corner welcomes exploration.',
    time: 'This temporal trace is being woven.',
  };
  return messages[context];
}
