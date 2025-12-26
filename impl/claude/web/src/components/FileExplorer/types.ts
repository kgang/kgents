/**
 * FileExplorer type definitions
 */

// =============================================================================
// Content Kind Types
// =============================================================================

/**
 * Content kinds for unified K-Block display.
 * Maps to zero_seed_kind from Feed API.
 */
export type ContentKind =
  | 'file'        // Regular file (spec, impl, docs)
  | 'upload'      // User uploaded content
  | 'axiom'       // L1: Zero Seed axiom
  | 'value'       // L2: Zero Seed value
  | 'goal'        // L3-L4: Zero Seed goal/spec
  | 'action'      // L5: Zero Seed action
  | 'reflection'  // L6: Zero Seed reflection
  | 'representation'; // L7: Zero Seed representation

// =============================================================================
// File Tree Types
// =============================================================================

export interface FileNode {
  /** Full path */
  path: string;
  /** Display name */
  name: string;
  /** Node type */
  type: 'file' | 'directory';
  /** Tree depth (for indentation) */
  depth: number;
  /** Children (for directories) */
  children?: FileNode[];
  /** K-Block metadata (for files) */
  kblock?: KBlockMetadata;
  /** Content kind for visual distinction */
  kind?: ContentKind;
}

export interface KBlockMetadata {
  /** Zero Seed layer (L1-L7) */
  layer?: string;
  /** Galois loss value (0-1) */
  loss?: number;
  /** Has Toulmin proof */
  hasProof?: boolean;
  /** Content kind */
  kind?: ContentKind;
}

// =============================================================================
// Integration Types
// =============================================================================

export interface IntegrationMetadata {
  /** Source file path (in uploads/) */
  sourcePath: string;
  /** Destination path */
  destinationPath: string;
  /** Detected Zero Seed layer */
  detectedLayer: string;
  /** Galois loss score (0-1) */
  galoisLoss: number;
  /** Discovered edges to existing K-Blocks */
  discoveredEdges: Edge[];
  /** Contradictions detected */
  contradictions: string[];
}

export interface Edge {
  /** Edge type (implements, tests, extends, etc.) */
  type: string;
  /** Target path */
  target: string;
}

// =============================================================================
// Context Menu Types
// =============================================================================

export type ContextMenuAction = 'open' | 'move' | 'split' | 'delete';
