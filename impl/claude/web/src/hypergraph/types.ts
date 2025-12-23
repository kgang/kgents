/**
 * Hypergraph Emacs — Type Definitions
 *
 * "The file is a lie. There is only the graph."
 * "Navigation is not movement. Navigation is edge traversal."
 *
 * Core types for the conceptual editor where nodes replace buffers
 * and edges replace directory structure.
 */

// =============================================================================
// Modes
// =============================================================================

/**
 * The six modes of Hypergraph Emacs.
 *
 * Each mode changes what keystrokes do:
 * - NORMAL: Navigate the graph
 * - INSERT: Edit content (K-Block isolation)
 * - EDGE: Create/modify edges
 * - VISUAL: Select multiple nodes
 * - COMMAND: Execute AGENTESE/ex commands
 * - WITNESS: Mark moments
 */
export type EditorMode = 'NORMAL' | 'INSERT' | 'EDGE' | 'VISUAL' | 'COMMAND' | 'WITNESS';

// =============================================================================
// Graph Primitives
// =============================================================================

/**
 * Edge types in the hypergraph.
 * These are the relationships between concepts.
 */
export type EdgeType =
  | 'implements' // Spec → Implementation
  | 'tests' // Spec/Impl → Tests
  | 'extends' // Child → Parent
  | 'derives_from' // Spec → Prerequisite spec
  | 'references' // Generic reference
  | 'contradicts' // Conflict marker
  | 'contains' // Parent → Children (structural)
  | 'uses' // Dependency
  | 'defines'; // Definition relationship

/**
 * An edge in the hypergraph.
 * Edges are typed and bidirectional (we store both directions).
 */
export interface Edge {
  /** Unique identifier */
  id: string;

  /** Source node path */
  source: string;

  /** Target node path */
  target: string;

  /** Edge type */
  type: EdgeType;

  /** Optional context (why this edge exists) */
  context?: string;

  /** Whether this edge is stale (target may have changed) */
  stale?: boolean;
}

/**
 * A node in the hypergraph.
 * This is what we navigate to and edit.
 */
export interface GraphNode {
  /** File path (the canonical identifier) */
  path: string;

  /** Display title (from frontmatter or first heading) */
  title: string;

  /** AGENTESE path if this is a spec */
  agentesePath?: string;

  /** Node kind */
  kind: 'spec' | 'implementation' | 'test' | 'doc' | 'config' | 'unknown';

  /** Tier (for specs) */
  tier?: 'CANONICAL' | 'RICH' | 'STUB' | 'GHOST';

  /** Confidence score (0-1) */
  confidence?: number;

  /** Outgoing edges (from this node) */
  outgoingEdges: Edge[];

  /** Incoming edges (to this node) */
  incomingEdges: Edge[];

  /** Raw content (loaded lazily) */
  content?: string;
}

// =============================================================================
// Navigation
// =============================================================================

/**
 * Cursor position within a node.
 */
export interface Position {
  /** Line number (0-indexed) */
  line: number;

  /** Column number (0-indexed) */
  column: number;
}

/**
 * Viewport state (what's visible).
 */
export interface Viewport {
  /** First visible line */
  topLine: number;

  /** Number of visible lines */
  visibleLines: number;

  /** Scroll percentage (0-1) */
  scrollPercent: number;
}

/**
 * A step in the navigation trail.
 * Records HOW we got to a node, not just that we visited it.
 */
export interface TrailStep {
  /** The node we visited */
  node: GraphNode;

  /** The edge we traversed to get here (null for initial node) */
  viaEdge: Edge | null;

  /** Cursor position when we left this node */
  cursor: Position;

  /** Timestamp */
  timestamp: number;
}

/**
 * Navigation trail (breadcrumbs).
 * Semantic history of how we navigated through the graph.
 */
export interface Trail {
  /** Steps in the trail (oldest first) */
  steps: TrailStep[];

  /** Maximum trail length before we start dropping old entries */
  maxLength: number;
}

/**
 * K-Block state (when editing).
 */
export interface KBlockState {
  /** K-Block identifier */
  blockId: string | null;

  /** Isolation state */
  isolation: 'PRISTINE' | 'DIRTY' | 'STALE' | 'CONFLICTING';

  /** Whether there are uncommitted changes */
  isDirty: boolean;

  /** Original content (for diff) */
  baseContent: string;

  /** Current working content */
  workingContent: string;

  /** Checkpoints within this K-Block */
  checkpoints: Array<{
    id: string;
    content: string;
    timestamp: number;
    message?: string;
  }>;
}

/**
 * Complete navigation state.
 * This is the "where you are" in the hypergraph.
 */
export interface NavigationState {
  /** Current focused node */
  currentNode: GraphNode | null;

  /** Navigation trail (breadcrumbs) */
  trail: Trail;

  /** Cursor position within current node */
  cursor: Position;

  /** Viewport state */
  viewport: Viewport;

  /** Current editor mode */
  mode: EditorMode;

  /** K-Block state (when editing) */
  kblock: KBlockState | null;

  /** Siblings (nodes sharing same parent edge type) */
  siblings: GraphNode[];

  /** Current sibling index */
  siblingIndex: number;

  /** Loading state */
  loading: boolean;

  /** Error state */
  error: string | null;
}

// =============================================================================
// Actions
// =============================================================================

/**
 * Navigation actions for the reducer.
 */
export type NavigationAction =
  // Focus operations
  | { type: 'FOCUS_NODE'; node: GraphNode }
  | { type: 'FOCUS_PATH'; path: string }

  // Graph navigation
  | { type: 'GO_PARENT' }
  | { type: 'GO_CHILD'; edgeType?: EdgeType }
  | { type: 'GO_SIBLING'; direction: 1 | -1 }
  | { type: 'GO_DEFINITION' }
  | { type: 'GO_REFERENCES' }
  | { type: 'GO_TESTS' }
  | { type: 'GO_BACK' } // Pop trail
  | { type: 'GO_FORWARD' } // Redo navigation

  // Cursor movement
  | { type: 'MOVE_CURSOR'; position: Position }
  | { type: 'MOVE_LINE'; delta: number }
  | { type: 'MOVE_COLUMN'; delta: number }
  | { type: 'GOTO_LINE'; line: number }
  | { type: 'GOTO_START' }
  | { type: 'GOTO_END' }

  // Mode changes
  | { type: 'SET_MODE'; mode: EditorMode }
  | {
      type: 'ENTER_INSERT';
      position?: 'before' | 'after' | 'line_start' | 'line_end' | 'below' | 'above';
    }
  | { type: 'EXIT_INSERT' }
  | { type: 'ENTER_COMMAND' }
  | { type: 'EXIT_COMMAND' }
  | { type: 'ENTER_EDGE' }
  | { type: 'EXIT_EDGE' }
  | { type: 'ENTER_WITNESS' }
  | { type: 'EXIT_WITNESS' }

  // K-Block operations
  | { type: 'KBLOCK_CREATED'; blockId: string; content: string }
  | { type: 'KBLOCK_UPDATED'; content: string }
  | { type: 'KBLOCK_CHECKPOINT'; id: string; message?: string }
  | { type: 'KBLOCK_COMMITTED' }
  | { type: 'KBLOCK_DISCARDED' }

  // Data loading
  | { type: 'SET_LOADING'; loading: boolean }
  | { type: 'SET_ERROR'; error: string | null }
  | { type: 'SET_SIBLINGS'; siblings: GraphNode[]; index: number }
  | { type: 'NODE_LOADED'; node: GraphNode };

// =============================================================================
// Key Bindings
// =============================================================================

/**
 * Key modifier flags.
 */
export interface KeyModifiers {
  ctrl: boolean;
  meta: boolean; // Cmd on Mac
  shift: boolean;
  alt: boolean;
}

/**
 * A key binding definition.
 */
export interface KeyBinding {
  /** The key (e.g., 'j', 'Enter', 'Escape') */
  key: string;

  /** Required modifiers */
  modifiers?: Partial<KeyModifiers>;

  /** Modes where this binding is active */
  modes: EditorMode[];

  /** Action to dispatch */
  action: NavigationAction | ((state: NavigationState) => NavigationAction | null);

  /** Description (for help) */
  description: string;

  /** Whether this binding should prevent default browser behavior */
  preventDefault?: boolean;
}

/**
 * Key sequence for multi-key bindings (like 'gg', 'gc', etc).
 */
export interface KeySequence {
  /** Keys in sequence */
  keys: string[];

  /** Timeout between keys (ms) */
  timeout: number;

  /** Current position in sequence */
  position: number;

  /** Timestamp of last key */
  lastKeyTime: number;
}

// =============================================================================
// Commands
// =============================================================================

/**
 * Command result from ex/AGENTESE commands.
 */
export interface CommandResult {
  /** Whether the command succeeded */
  success: boolean;

  /** Output to display */
  output?: string;

  /** Error message if failed */
  error?: string;

  /** Navigation action to dispatch */
  action?: NavigationAction;
}

/**
 * Command definition.
 */
export interface Command {
  /** Command name (e.g., 'e', 'w', 'ag') */
  name: string;

  /** Aliases */
  aliases?: string[];

  /** Execute the command */
  execute: (args: string, state: NavigationState) => Promise<CommandResult>;

  /** Tab completion */
  complete?: (partial: string, state: NavigationState) => Promise<string[]>;

  /** Description */
  description: string;
}

// =============================================================================
// Initial State Factory
// =============================================================================

/**
 * Create initial navigation state.
 */
export function createInitialState(): NavigationState {
  return {
    currentNode: null,
    trail: {
      steps: [],
      maxLength: 100,
    },
    cursor: { line: 0, column: 0 },
    viewport: {
      topLine: 0,
      visibleLines: 40,
      scrollPercent: 0,
    },
    mode: 'NORMAL',
    kblock: null,
    siblings: [],
    siblingIndex: -1,
    loading: false,
    error: null,
  };
}

/**
 * Create a trail step.
 */
export function createTrailStep(
  node: GraphNode,
  viaEdge: Edge | null = null,
  cursor: Position = { line: 0, column: 0 }
): TrailStep {
  return {
    node,
    viaEdge,
    cursor,
    timestamp: Date.now(),
  };
}
