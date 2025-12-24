/**
 * AGENTESE Path Registry
 *
 * Static list of all AGENTESE paths for ghost text completion.
 * Organized by context: world.*, self.*, concept.*, void.*, time.*
 *
 * The noun is a lie. There is only the rate of change.
 */

/**
 * All known AGENTESE paths in the system
 */
export const AGENTESE_PATHS = [
  // world.* - The External (entities, environments, tools)
  'world.house.manifest',
  'world.house.traverse',
  'world.house.enter',
  'world.house.map',
  'world.entity.create',
  'world.entity.query',
  'world.entity.update',
  'world.entity.delete',
  'world.tool.invoke',
  'world.tool.list',
  'world.environment.sense',
  'world.environment.act',

  // self.* - The Internal (memory, capability, state)
  'self.brain.capture',
  'self.brain.recall',
  'self.brain.query',
  'self.brain.status',
  'self.memory.crystallize',
  'self.memory.retrieve',
  'self.memory.cartography',
  'self.fusion.propose',
  'self.fusion.decide',
  'self.fusion.history',
  'self.capability.list',
  'self.capability.check',
  'self.state.get',
  'self.state.update',

  // concept.* - The Abstract (platonics, definitions, logic)
  'concept.derivation.edges',
  'concept.derivation.trace',
  'concept.document.analyze',
  'concept.document.structure',
  'concept.categorical.probe',
  'concept.categorical.compose',
  'concept.categorical.laws',
  'concept.definition.lookup',
  'concept.definition.relate',
  'concept.logic.prove',
  'concept.logic.check',

  // void.* - The Accursed Share (entropy, serendipity, gratitude)
  'void.entropy.sample',
  'void.entropy.inject',
  'void.serendipity.discover',
  'void.gratitude.emit',
  'void.gratitude.reflect',
  'void.offering.make',

  // time.* - The Temporal (traces, forecasts, schedules)
  'time.history.trail',
  'time.history.replay',
  'time.forecast.next',
  'time.forecast.horizon',
  'time.schedule.plan',
  'time.schedule.execute',
  'time.trace.capture',
  'time.trace.analyze',
] as const;

/**
 * Match AGENTESE paths by prefix
 *
 * @param prefix - The prefix to match (case-insensitive)
 * @returns Matching paths, sorted by relevance
 */
export function matchAgentesePath(prefix: string): string[] {
  if (!prefix || prefix.length === 0) {
    return [];
  }

  const lower = prefix.toLowerCase();

  // Exact prefix matches first, then fuzzy matches
  const exactMatches: string[] = [];
  const fuzzyMatches: string[] = [];

  for (const path of AGENTESE_PATHS) {
    const pathLower = path.toLowerCase();

    if (pathLower.startsWith(lower)) {
      exactMatches.push(path);
    } else if (pathLower.includes(lower)) {
      fuzzyMatches.push(path);
    }
  }

  return [...exactMatches, ...fuzzyMatches];
}

/**
 * Get path suggestions for a partial context (e.g., "world." → all world.* paths)
 *
 * @param context - The context prefix (e.g., "world", "self", "concept")
 * @returns All paths in that context
 */
export function getPathsByContext(context: string): string[] {
  const prefix = context.endsWith('.') ? context : `${context}.`;
  return AGENTESE_PATHS.filter(path => path.startsWith(prefix));
}

/**
 * Parse a partial path and suggest next segment
 *
 * Examples:
 * - "world" → ["house", "entity", "tool", "environment"]
 * - "world.house" → ["manifest", "traverse", "enter", "map"]
 * - "self.brain." → ["capture", "recall", "query", "status"]
 *
 * @param partial - Partial path to complete
 * @returns Unique next segments
 */
export function suggestNextSegment(partial: string): string[] {
  const segments = partial.split('.');
  const depth = segments.length;

  // Find all paths that match up to current depth
  const matchingPaths = AGENTESE_PATHS.filter(path => {
    const pathSegments = path.split('.');
    if (pathSegments.length <= depth) return false;

    // Check all segments before current position match
    for (let i = 0; i < depth - 1; i++) {
      if (pathSegments[i] !== segments[i]) return false;
    }

    // Last segment should start with partial
    const lastPartial = segments[depth - 1] || '';
    return pathSegments[depth - 1].startsWith(lastPartial);
  });

  // Extract unique next segments
  const nextSegments = new Set<string>();
  for (const path of matchingPaths) {
    const pathSegments = path.split('.');
    nextSegments.add(pathSegments[depth - 1]);
  }

  return Array.from(nextSegments).sort();
}
