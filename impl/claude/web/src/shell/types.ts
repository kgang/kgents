/**
 * OS Shell Types
 *
 * Type definitions for the unified shell layout system.
 * See: spec/protocols/os-shell.md
 *
 * @module shell/types
 */

// =============================================================================
// Density (from projection.md)
// =============================================================================

/**
 * Layout density based on viewport width.
 * Determines how content is arranged and compressed.
 *
 * - compact: <768px (mobile) - drawers, floating actions
 * - comfortable: 768-1024px (tablet) - collapsible panels
 * - spacious: >1024px (desktop) - full panels, resizable dividers
 */
export type Density = 'compact' | 'comfortable' | 'spacious';

// =============================================================================
// Observer (from agentese.md)
// =============================================================================

/**
 * Observer archetype - who is looking shapes what is seen.
 */
export type ObserverArchetype =
  | 'developer'
  | 'architect'
  | 'operator'
  | 'reviewer'
  | 'newcomer'
  | 'guest'
  | 'technical'
  | 'casual'
  | 'security'
  | 'creative'
  | 'strategic'
  | 'tactical'
  | 'reflective';

/**
 * Capability flags for observer-based affordances.
 */
export type Capability = 'read' | 'write' | 'admin' | 'stream' | 'delete';

/**
 * Observer umwelt - the complete context of who is perceiving.
 */
export interface Observer {
  /** Unique session identifier */
  sessionId: string;
  /** User identifier (if authenticated) */
  userId?: string;
  /** Tenant identifier (for multi-tenant) */
  tenantId?: string;
  /** Observer archetype */
  archetype: ObserverArchetype;
  /** Current capabilities */
  capabilities: Set<Capability>;
  /** Optional intent description */
  intent?: string;
  /** Preferred jewel (for personalization) */
  preferredJewel?: CrownJewel;
}

// =============================================================================
// Trace (for devex visibility)
// =============================================================================

/**
 * Trace status for AGENTESE invocations.
 */
export type TraceStatus = 'pending' | 'success' | 'error' | 'refused';

/**
 * Individual trace entry for an AGENTESE invocation.
 */
export interface Trace {
  /** Unique trace identifier */
  id: string;
  /** Timestamp of invocation */
  timestamp: Date;
  /** AGENTESE path invoked */
  path: string;
  /** Aspect called */
  aspect: string;
  /** Duration in milliseconds */
  duration: number;
  /** Invocation status */
  status: TraceStatus;
  /** Result (if success) */
  result?: unknown;
  /** Error message (if error) */
  error?: string;
}

// =============================================================================
// Crown Jewels
// =============================================================================

/**
 * Crown Jewel identifiers.
 */
export type CrownJewel =
  | 'brain'
  | 'gestalt'
  | 'gardener'
  | 'atelier'
  | 'coalition'
  | 'park'
  | 'domain';

// =============================================================================
// Shell Context
// =============================================================================

/**
 * Complete shell context available to all children.
 */
export interface ShellContext {
  // Layout
  density: Density;
  width: number;
  height: number;
  isMobile: boolean;
  isTablet: boolean;
  isDesktop: boolean;

  // Observer
  observer: Observer;
  setArchetype: (archetype: ObserverArchetype) => void;
  setIntent: (intent: string) => void;

  // Capabilities
  capabilities: Set<Capability>;
  hasCapability: (cap: Capability) => boolean;

  // Traces
  traces: Trace[];
  addTrace: (trace: Omit<Trace, 'id'>) => void;
  clearTraces: () => void;

  // Shell state
  observerDrawerExpanded: boolean;
  setObserverDrawerExpanded: (expanded: boolean) => void;
  navigationTreeExpanded: boolean;
  setNavigationTreeExpanded: (expanded: boolean) => void;
  terminalExpanded: boolean;
  setTerminalExpanded: (expanded: boolean) => void;
}

// =============================================================================
// AGENTESE Discovery
// =============================================================================

/**
 * Path info from /agentese/discover endpoint.
 */
export interface PathInfo {
  /** Full AGENTESE path (e.g., "world.town.citizens") */
  path: string;
  /** Human-readable description */
  description?: string;
  /** Available aspects for this path */
  aspects: string[];
  /** Context (world, self, concept, void, time) */
  context: 'world' | 'self' | 'concept' | 'void' | 'time';
}

/**
 * Discovery response from gateway.
 */
export interface DiscoveryResponse {
  paths: PathInfo[];
  version: string;
}

// =============================================================================
// Terminal Types
// =============================================================================

/**
 * Terminal history entry status.
 */
export type HistoryStatus = 'success' | 'error' | 'pending';

/**
 * Terminal history entry for persisted commands.
 */
export interface HistoryEntry {
  /** Unique entry identifier */
  id: string;
  /** The command/path that was executed */
  input: string;
  /** Execution timestamp */
  timestamp: Date;
  /** Duration in milliseconds */
  duration: number;
  /** Execution status */
  status: HistoryStatus;
  /** Result output (if success) */
  output?: unknown;
  /** Error message (if error) */
  error?: string;
}

/**
 * Saved collection of terminal commands.
 */
export interface TerminalCollection {
  /** Collection name */
  name: string;
  /** Description */
  description?: string;
  /** Saved command inputs */
  commands: string[];
  /** Created timestamp */
  createdAt: Date;
  /** Last modified timestamp */
  updatedAt: Date;
}

/**
 * Completion suggestion from registry.
 */
export interface CompletionSuggestion {
  /** The completed text */
  text: string;
  /** Type of suggestion (path, aspect, command) */
  type: 'path' | 'aspect' | 'command' | 'alias';
  /** Optional description */
  description?: string;
}

/**
 * Terminal output line for display.
 */
export interface TerminalLine {
  /** Unique line identifier */
  id: string;
  /** Line type for styling */
  type: 'input' | 'output' | 'error' | 'info' | 'system';
  /** Content to display */
  content: string;
  /** Optional JSON data for structured output */
  data?: unknown;
  /** Timestamp */
  timestamp: Date;
}

/**
 * Terminal service interface for execution and discovery.
 */
export interface TerminalServiceInterface {
  // Execution
  execute(input: string): Promise<TerminalLine[]>;

  // History
  history: HistoryEntry[];
  searchHistory(query: string): HistoryEntry[];
  clearHistory(): void;

  // Collections
  collections: TerminalCollection[];
  saveCollection(name: string, commands: string[]): void;
  loadCollection(name: string): string[];
  deleteCollection(name: string): void;

  // Discovery
  discover(context?: string): Promise<PathInfo[]>;
  affordances(path: string): Promise<string[]>;
  help(path: string): Promise<string>;

  // Completion
  complete(partial: string): Promise<CompletionSuggestion[]>;

  // Aliases
  aliases: Record<string, string>;
  setAlias(name: string, path: string): void;
  removeAlias(name: string): void;
}

// =============================================================================
// Projection Context (for PathProjection)
// =============================================================================

/**
 * Context provided to PathProjection children.
 * Contains everything needed to render density-aware, observer-dependent content.
 *
 * @see spec/protocols/os-shell.md - Part III: Projection-First Rendering
 * @see spec/protocols/projection.md
 */
export interface ProjectionContext {
  /** Current layout density */
  density: Density;
  /** Current observer (who is looking) */
  observer: Observer;
  /** Loading state */
  loading: boolean;
  /** Error if any */
  error: Error | null;
  /** Refetch data */
  refetch: () => void;
  /** Whether streaming is active (future) */
  streaming: boolean;
  /** The AGENTESE path that was invoked */
  path: string;
  /** The aspect that was invoked */
  aspect: string;
}
