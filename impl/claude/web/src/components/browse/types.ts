/**
 * Shared types for browse components.
 *
 * Three-tier browsing system:
 * 1. FileSidebar (quick actions + file tree)
 * 2. FileTree (tree view component)
 * 3. BrowseModal (exhaustive browser)
 */

// =============================================================================
// File Operations
// =============================================================================

/** Uploaded file with content */
export interface UploadedFile {
  name: string;
  content: string;
  type: string;
}

// =============================================================================
// FileTree Types
// =============================================================================

/** File kinds for traditional file types */
export type FileKind = 'doc' | 'code' | 'spec' | 'unknown';

/** Edge kinds for K-Block relationships */
export type EdgeKind =
  | 'derives_from'  // Zero Seed derivation (child -> parent axiom)
  | 'implements'    // Implementation of a specification
  | 'tests'         // Test coverage relationship
  | 'references'    // Cross-references between documents
  | 'contradicts';  // Logical contradiction

/** Extended node kind including Zero Seed content types, Witness marks, and Edges */
export type NodeKind =
  | FileKind
  | 'upload'       // User uploaded content
  | 'axiom'        // L1: Zero Seed axiom
  | 'value'        // L2: Zero Seed value
  | 'goal'         // L3-L4: Zero Seed goal/spec
  | 'action'       // L5: Zero Seed action
  | 'reflection'   // L6: Zero Seed reflection
  | 'representation' // L7: Zero Seed representation
  // Witness mark types
  | 'mark'         // Generic witness mark
  | 'decision'     // Decision/synthesis mark
  | 'eureka'       // Insight/discovery mark
  | 'gotcha'       // Warning/trap mark
  // Edge types
  | 'edge'               // Generic edge (folder icon)
  | 'edge_derives_from'  // Zero Seed derivation edge
  | 'edge_implements'    // Implementation edge
  | 'edge_tests'         // Test coverage edge
  | 'edge_references'    // Reference edge
  | 'edge_contradicts';  // Contradiction edge

export type NodeType = 'file' | 'directory';

/** Edge metadata stored in tree node for edge display */
export interface TreeNodeEdgeData {
  id: string;
  sourceId: string;
  targetId: string;
  sourcePath: string;
  targetPath: string;
  confidence: number;
  context: string | null;
  markId: string | null;
}

/** Mark metadata stored in tree node for witness mark display */
export interface TreeNodeMarkData {
  id: string;
  action: string;
  reasoning: string | null;
  principles: string[];
  author: string;
  timestamp: string;
  retracted: boolean;
}

export interface TreeNode {
  path: string;
  name: string;
  type: NodeType;
  children?: TreeNode[];
  expanded?: boolean;
  kind?: NodeKind;
  depth: number;
  /** Zero Seed layer (1-7) if applicable */
  layer?: number;
  /** Galois loss (0-1) for coherence indicator */
  galoisLoss?: number;
  /** Edge metadata if this node represents an edge */
  edgeData?: TreeNodeEdgeData;
  /** Mark metadata if this node represents a witness mark */
  markData?: TreeNodeMarkData;
  /** Timestamp for breathing animation (recent modifications) */
  modifiedAt?: string;
}

export interface FileTreeProps {
  rootPaths?: string[];
  onSelectFile: (path: string) => void;
  currentFile?: string;
  searchQuery?: string;
  maxHeight?: string;
}

// =============================================================================
// File Kind Detection
// =============================================================================

/**
 * Determine file kind from extension.
 */
export function getFileKind(path: string): FileKind {
  const ext = path.split('.').pop()?.toLowerCase() || '';

  // Documentation
  if (ext === 'md' || ext === 'mdx' || ext === 'txt') {
    return 'doc';
  }

  // Code files
  if (['ts', 'tsx', 'js', 'jsx', 'py', 'css', 'json', 'yaml', 'yml'].includes(ext)) {
    return 'code';
  }

  // Spec files (check path contains 'spec')
  if (path.includes('/spec/') || path.startsWith('spec/')) {
    return 'spec';
  }

  return 'unknown';
}

/**
 * Get file extension.
 */
export function getExtension(path: string): string {
  return path.split('.').pop()?.toLowerCase() || '';
}

/**
 * Get file name from path.
 */
export function getFileName(path: string): string {
  return path.split('/').pop() || path;
}

/**
 * Check if path is directory (heuristic: no extension or ends with /).
 */
export function isDirectory(path: string): boolean {
  return path.endsWith('/') || !path.split('/').pop()?.includes('.');
}

// =============================================================================
// BrowseModal Types (Phase 2)
// =============================================================================

export type BrowseCategory = 'all' | 'files' | 'docs' | 'specs' | 'kblocks' | 'convos' | 'uploads' | 'zero-seed';

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

export interface BrowseItem {
  id: string;
  path: string;
  title: string;
  category: BrowseCategory;
  preview?: string;
  directory?: string;
  modifiedAt?: Date;
  annotations?: number;
  /** Zero Seed layer (1-7) if applicable */
  layer?: number;
  /** Content kind for visual distinction */
  kind?: ContentKind;
  /** Galois loss (0-1) for coherence indicator */
  galoisLoss?: number;
}

export interface BrowseFilter {
  modifiedToday: boolean;
  hasAnnotations: boolean;
  unread: boolean;
}

export interface BrowseFilters {
  modifiedToday?: boolean;
  hasAnnotations?: boolean;
  unread?: boolean;
}

export interface BrowseResponse {
  items: BrowseItem[];
  total: number;
  categories: Record<BrowseCategory, number>;
}

// =============================================================================
// Witness Mark Types (for FileTree integration)
// =============================================================================

/** Single witness mark from API */
export interface WitnessMark {
  id: string;
  action: string;
  reasoning: string | null;
  principles: string[];
  author: string;
  session_id: string | null;
  timestamp: string;
  parent_mark_id: string | null;
  retracted: boolean;
  retraction_reason: string | null;
}

/** Category of marks for browsing */
export interface MarkBrowseCategory {
  name: string;
  count: number;
  marks: WitnessMark[];
}

/** Response from /api/witness/marks/browse */
export interface MarkBrowseResponse {
  today: MarkBrowseCategory;
  decisions: MarkBrowseCategory;
  eurekas: MarkBrowseCategory;
  gotchas: MarkBrowseCategory;
  all_marks: MarkBrowseCategory;
  total: number;
}
