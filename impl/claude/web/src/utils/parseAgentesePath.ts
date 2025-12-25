/**
 * AGENTESE Path Parser
 *
 * Parses URLs into AGENTESE invocation components.
 *
 * URL Format: /{context}.{entity}.{sub}...[:aspect][?params]
 *
 * Examples:
 *   /world.town.citizen.kent_001           → { path: "world.town.citizen.kent_001", aspect: "manifest" }
 *   /self.memory.crystal.abc123:heritage   → { path: "self.memory.crystal.abc123", aspect: "heritage" }
 *   /time.differance.recent?limit=20       → { path: "time.differance.recent", params: { limit: "20" } }
 *
 * @see spec/protocols/projection-web.md
 */

/**
 * Valid AGENTESE contexts (the five ontological domains)
 */
export const AGENTESE_CONTEXTS = ['world', 'self', 'concept', 'void', 'time'] as const;
export type AgenteseContext = (typeof AGENTESE_CONTEXTS)[number];

/**
 * Parsed AGENTESE path components
 */
export interface ParsedAgentesePath {
  /** Full AGENTESE path (e.g., "world.town.citizen.kent_001") */
  path: string;
  /** Context (first segment: world, self, concept, void, time) */
  context: AgenteseContext | null;
  /** Aspect to invoke (default: "manifest") */
  aspect: string;
  /** Query parameters */
  params: Record<string, string>;
  /** Whether this is a valid AGENTESE path */
  isValid: boolean;
  /** Error message if invalid */
  error?: string;
}

/**
 * Reserved URL prefixes that are NOT AGENTESE paths
 */
const RESERVED_PREFIXES = ['_', 'api', 'static', 'assets', 'favicon'];

/**
 * Parse a URL pathname + search into AGENTESE components
 *
 * @param urlPath - The URL pathname (e.g., "/world.town.citizen.kent_001:manifest?limit=10")
 * @returns Parsed AGENTESE components
 *
 * @example
 * parseAgentesePath('/world.town.citizen.kent_001')
 * // { path: 'world.town.citizen.kent_001', context: 'world', aspect: 'manifest', params: {}, isValid: true }
 *
 * parseAgentesePath('/self.memory:capture?tags=work')
 * // { path: 'self.memory', context: 'self', aspect: 'capture', params: { tags: 'work' }, isValid: true }
 */
export function parseAgentesePath(urlPath: string): ParsedAgentesePath {
  // Remove leading slash
  const cleanPath = urlPath.startsWith('/') ? urlPath.slice(1) : urlPath;

  // Check for reserved prefixes
  const firstSegment = cleanPath.split(/[.?:]/)[0];
  if (RESERVED_PREFIXES.some((prefix) => firstSegment.startsWith(prefix))) {
    return {
      path: '',
      context: null,
      aspect: 'manifest',
      params: {},
      isValid: false,
      error: `Reserved prefix: ${firstSegment}`,
    };
  }

  // Split query params
  const [pathWithAspect, queryString] = cleanPath.split('?');

  // Parse query params
  const params: Record<string, string> = {};
  if (queryString) {
    const searchParams = new URLSearchParams(queryString);
    searchParams.forEach((value, key) => {
      params[key] = value;
    });
  }

  // Split aspect (colon separator)
  const [basePath, aspect = 'manifest'] = pathWithAspect.split(':');

  // Validate path structure
  if (!basePath || basePath.length === 0) {
    return {
      path: '',
      context: null,
      aspect: 'manifest',
      params,
      isValid: false,
      error: 'Empty path',
    };
  }

  // Extract context (first segment)
  const segments = basePath.split('.');
  const context = segments[0] as AgenteseContext;

  // Validate context
  if (!AGENTESE_CONTEXTS.includes(context)) {
    return {
      path: basePath,
      context: null,
      aspect,
      params,
      isValid: false,
      error: `Invalid context: ${context}. Valid contexts: ${AGENTESE_CONTEXTS.join(', ')}`,
    };
  }

  // Validate segment format (lowercase alphanumeric + underscore)
  const invalidSegment = segments.find((s) => !/^[a-z][a-z0-9_]*$/.test(s));
  if (invalidSegment) {
    return {
      path: basePath,
      context,
      aspect,
      params,
      isValid: false,
      error: `Invalid segment: ${invalidSegment}. Segments must be lowercase alphanumeric with underscores.`,
    };
  }

  return {
    path: basePath,
    context,
    aspect,
    params,
    isValid: true,
  };
}

/**
 * Format AGENTESE path components back into a URL
 *
 * @param path - AGENTESE path (e.g., "world.town.citizen.kent_001")
 * @param aspect - Aspect (default: "manifest", omitted from URL)
 * @param params - Query parameters
 * @returns Formatted URL pathname
 *
 * @example
 * formatAgentesePath('world.town.citizen.kent_001')
 * // '/world.town.citizen.kent_001'
 *
 * formatAgentesePath('world.town.citizen.kent_001', 'polynomial')
 * // '/world.town.citizen.kent_001:polynomial'
 *
 * formatAgentesePath('time.differance.recent', 'manifest', { limit: '20' })
 * // '/time.differance.recent?limit=20'
 */
export function formatAgentesePath(
  path: string,
  aspect?: string,
  params?: Record<string, string>
): string {
  let url = `/${path}`;

  // Add aspect if not default
  if (aspect && aspect !== 'manifest') {
    url += `:${aspect}`;
  }

  // Add query params
  if (params && Object.keys(params).length > 0) {
    url += '?' + new URLSearchParams(params).toString();
  }

  return url;
}

/**
 * Check if a URL is an AGENTESE path (not a system route)
 */
export function isAgentesePath(urlPath: string): boolean {
  const parsed = parseAgentesePath(urlPath);
  return parsed.isValid;
}

/**
 * Extract the holon (entity) from a path
 *
 * @example
 * getHolon('world.town.citizen.kent_001') // 'town'
 * getHolon('self.memory.crystal.abc123')  // 'memory'
 */
export function getHolon(path: string): string | null {
  const segments = path.split('.');
  return segments.length >= 2 ? segments[1] : null;
}

/**
 * Get the entity ID from a path (if present)
 *
 * Entity IDs follow the pattern: identifier_id (e.g., kent_001, abc123)
 *
 * @example
 * getEntityId('world.town.citizen.kent_001') // 'kent_001'
 * getEntityId('self.memory.crystal')         // null
 */
export function getEntityId(path: string): string | null {
  const segments = path.split('.');
  // Entity IDs are typically the last segment and contain an underscore followed by alphanumeric
  const lastSegment = segments[segments.length - 1];
  if (lastSegment && /_[a-z0-9]+$/.test(lastSegment)) {
    return lastSegment;
  }
  return null;
}

/**
 * Get the parent path (one level up)
 *
 * @example
 * getParentPath('world.town.citizen.kent_001') // 'world.town.citizen'
 * getParentPath('world.town')                   // 'world'
 * getParentPath('world')                        // null
 */
export function getParentPath(path: string): string | null {
  const segments = path.split('.');
  if (segments.length <= 1) return null;
  return segments.slice(0, -1).join('.');
}

/**
 * Format a path segment as a human-readable label
 *
 * @example
 * formatPathLabel('world.town.citizen') // 'Citizen'
 * formatPathLabel('self.memory')         // 'Memory'
 */
export function formatPathLabel(path: string): string {
  const segments = path.split('.');
  const lastSegment = segments[segments.length - 1];

  // Remove entity ID suffix if present
  const cleanSegment = lastSegment.replace(/_[a-z0-9]+$/, '');

  // Capitalize first letter
  return cleanSegment.charAt(0).toUpperCase() + cleanSegment.slice(1);
}

/**
 * Match a path against a pattern with wildcards
 *
 * Matching rules:
 * - Exact patterns require exact match: 'world.park' only matches 'world.park'
 * - Single wildcard '*' matches exactly ONE segment: 'world.park.*' matches 'world.park.host' but NOT 'world.park.host.list'
 * - Double wildcard '**' matches any remaining segments (unlimited depth)
 *
 * @example
 * matchPathPattern('world.town', 'world.town')                // true (exact)
 * matchPathPattern('world.town', 'world.town.citizen')        // false (no wildcard)
 * matchPathPattern('world.town.*', 'world.town.citizen')      // true (single wildcard)
 * matchPathPattern('world.town.*', 'world.town.citizen.kent') // false (single wildcard only matches one level)
 * matchPathPattern('world.town.**', 'world.town.citizen.kent') // true (double wildcard matches any depth)
 * matchPathPattern('self.*', 'world.town')                    // false (context mismatch)
 */
export function matchPathPattern(pattern: string, path: string): boolean {
  const patternParts = pattern.split('.');
  const pathParts = path.split('.');

  for (let i = 0; i < patternParts.length; i++) {
    const patternPart = patternParts[i];

    // Double wildcard '**' matches any remaining segments (unlimited depth)
    if (patternPart === '**') {
      return true;
    }

    // Single wildcard '*' matches exactly ONE segment
    if (patternPart === '*') {
      // Must have exactly one more segment in path
      return pathParts.length === i + 1;
    }

    // No more path segments to match
    if (i >= pathParts.length) {
      return false;
    }

    // Exact match required
    if (patternPart !== pathParts[i]) {
      return false;
    }
  }

  // Pattern fully matched - path must have same number of segments (exact match)
  return patternParts.length === pathParts.length;
}
