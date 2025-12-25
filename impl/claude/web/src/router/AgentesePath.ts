/**
 * AGENTESE Path Parsing & URL Generation
 *
 * Philosophy:
 * "The URL IS the AGENTESE invocation."
 *
 * Traditional: `/chat?session=abc123`
 * AGENTESE:   `/self.chat.session.abc123`
 *
 * This module handles:
 * - Parsing URLs to AGENTESE paths
 * - Generating URLs from AGENTESE paths
 * - Observer context extraction
 * - Parameter handling
 */

/**
 * The five ontological contexts of AGENTESE.
 * Every path must begin with one.
 */
export type AgenteseContext = 'world' | 'self' | 'concept' | 'void' | 'time';

/**
 * Aspect categories from AGENTESE spec.
 * Aspects are ACTIONS you DO, not places you GO TO.
 */
export type AspectCategory =
  | 'perception'    // manifest, witness, sense
  | 'mutation'      // transform, renovate, evolve
  | 'composition'   // compose, merge, split
  | 'introspection' // affordances, constraints
  | 'generation'    // define, spawn, fork
  | 'entropy';      // sip, pour, tithe

/**
 * Parsed AGENTESE path from URL.
 *
 * Example: `/self.chat.session.abc123:stream?limit=20`
 * {
 *   context: 'self',
 *   path: ['chat', 'session', 'abc123'],
 *   aspect: 'stream',
 *   params: { limit: '20' }
 * }
 */
export interface AgentesePath {
  /** Ontological domain */
  context: AgenteseContext;

  /** Path segments after context */
  path: string[];

  /** Optional aspect (the action/verb) */
  aspect?: string;

  /** Query parameters */
  params?: Record<string, string>;

  /** Full reconstructed path for invocation */
  fullPath: string;
}

/**
 * Error when parsing invalid AGENTESE URL.
 */
export class AgentesePathError extends Error {
  constructor(message: string, public url: string) {
    super(message);
    this.name = 'AgentesePathError';
  }
}

/**
 * Valid AGENTESE contexts.
 */
const CONTEXTS = new Set<AgenteseContext>(['world', 'self', 'concept', 'void', 'time']);

/**
 * Reserved URL prefixes that are NOT AGENTESE paths.
 */
const RESERVED_PREFIXES = ['_', 'api', 'static', 'assets'];

/**
 * Parse a URL pathname to an AGENTESE path.
 *
 * Grammar:
 *   /{context}.{segments}...[:aspect][?params]
 *
 * Examples:
 *   /self.chat                     → { context: 'self', path: ['chat'] }
 *   /world.town.citizen.kent_001   → { context: 'world', path: ['town', 'citizen', 'kent_001'] }
 *   /self.memory.crystal:heritage  → { context: 'self', path: ['memory', 'crystal'], aspect: 'heritage' }
 *
 * @throws {AgentesePathError} If URL is malformed or invalid
 */
export function parseAgentesePath(url: string): AgentesePath {
  // Remove leading slash
  const pathname = url.startsWith('/') ? url.slice(1) : url;

  // Empty path
  if (!pathname) {
    throw new AgentesePathError('Empty AGENTESE path', url);
  }

  // Check for reserved prefixes
  const firstSegment = pathname.split(/[/.?:]/)[0];
  if (RESERVED_PREFIXES.includes(firstSegment)) {
    throw new AgentesePathError(`Reserved prefix: ${firstSegment}`, url);
  }

  // Split into path and query params
  const [pathWithAspect, query] = pathname.split('?');

  // Split aspect from path
  const [pathPart, aspect] = pathWithAspect.split(':');

  // Split path into segments
  const segments = pathPart.split('.');

  if (segments.length < 2) {
    throw new AgentesePathError(
      'AGENTESE path must have at least context.entity (e.g., self.chat)',
      url
    );
  }

  // Extract context
  const context = segments[0] as AgenteseContext;
  if (!CONTEXTS.has(context)) {
    throw new AgentesePathError(
      `Invalid context: ${context}. Must be one of: ${Array.from(CONTEXTS).join(', ')}`,
      url
    );
  }

  // Extract remaining path segments
  const path = segments.slice(1);

  // Parse query parameters
  const params: Record<string, string> = {};
  if (query) {
    const searchParams = new URLSearchParams(query);
    searchParams.forEach((value, key) => {
      params[key] = value;
    });
  }

  // Reconstruct full path for backend invocation
  const fullPath = segments.join('.');

  return {
    context,
    path,
    aspect: aspect || undefined,
    params: Object.keys(params).length > 0 ? params : undefined,
    fullPath,
  };
}

/**
 * Generate a URL from AGENTESE path components.
 *
 * Examples:
 *   toUrl('self.chat', { aspect: 'stream' })
 *     → /self.chat:stream
 *
 *   toUrl('world.town.citizen.kent_001', { params: { view: 'polynomial' } })
 *     → /world.town.citizen.kent_001?view=polynomial
 *
 * @param path - Full AGENTESE path (e.g., 'self.chat.session.abc123')
 * @param options - Optional aspect and params
 */
export function toUrl(
  path: string,
  options?: {
    aspect?: string;
    params?: Record<string, string>;
  }
): string {
  let url = `/${path}`;

  // Add aspect (if not 'manifest', which is the default)
  if (options?.aspect && options.aspect !== 'manifest') {
    url += `:${options.aspect}`;
  }

  // Add query parameters
  if (options?.params && Object.keys(options.params).length > 0) {
    const searchParams = new URLSearchParams(options.params);
    url += `?${searchParams.toString()}`;
  }

  return url;
}

/**
 * Check if a URL is a valid AGENTESE path.
 * Returns true if parseable, false otherwise.
 */
export function isAgentesePath(url: string): boolean {
  try {
    parseAgentesePath(url);
    return true;
  } catch {
    return false;
  }
}

/**
 * Format an AGENTESE path for display.
 *
 * Examples:
 *   formatPathLabel('world.town.citizen.kent_001')
 *     → 'Citizen: kent_001'
 *
 *   formatPathLabel('self.memory.crystal')
 *     → 'Memory Crystal'
 */
export function formatPathLabel(path: string): string {
  const segments = path.split('.');

  if (segments.length < 2) {
    return path;
  }

  // Get last segment (entity or ID)
  const lastSegment = segments[segments.length - 1];

  // If it's an entity ID (contains underscore), format it
  if (lastSegment.includes('_')) {
    const [entity, id] = lastSegment.split('_');
    return `${capitalize(entity)}: ${id}`;
  }

  // Otherwise, capitalize and humanize
  return segments.slice(1).map(capitalize).join(' ');
}

/**
 * Extract entity type from AGENTESE path.
 *
 * Examples:
 *   getEntityType('world.town.citizen.kent_001') → 'citizen'
 *   getEntityType('self.memory.crystal')         → 'crystal'
 */
export function getEntityType(path: string): string | null {
  const segments = path.split('.');

  // Path too short to have entity
  if (segments.length < 2) {
    return null;
  }

  // Get second-to-last segment (entity type)
  const entitySegment = segments[segments.length - 1];

  // If it's an ID, get the entity before it
  if (entitySegment.includes('_')) {
    return segments.length >= 3 ? segments[segments.length - 2] : null;
  }

  // Otherwise it's the entity itself
  return entitySegment;
}

/**
 * Capitalize first letter.
 */
function capitalize(str: string): string {
  return str.charAt(0).toUpperCase() + str.slice(1);
}

/**
 * Navigation helper: Build AGENTESE URL with type safety.
 *
 * Example:
 *   navigateTo('self.chat.session', { id: 'abc123' })
 *     → /self.chat.session.abc123
 */
export function buildAgentesePath(
  basePath: string,
  options?: {
    segments?: string[];
    aspect?: string;
    params?: Record<string, string>;
  }
): string {
  let fullPath = basePath;

  // Append additional segments
  if (options?.segments && options.segments.length > 0) {
    fullPath += '.' + options.segments.join('.');
  }

  return toUrl(fullPath, {
    aspect: options?.aspect,
    params: options?.params,
  });
}

/**
 * Composition helper: Create piped AGENTESE path.
 *
 * Example:
 *   composePaths(['world.doc.manifest', 'concept.summary.refine', 'self.memory.engram'])
 *     → /world.doc.manifest>>concept.summary.refine>>self.memory.engram
 */
export function composePaths(paths: string[]): string {
  return '/' + paths.join('>>');
}
