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

export type FileKind = 'doc' | 'code' | 'spec' | 'unknown';
export type NodeType = 'file' | 'directory';

export interface TreeNode {
  path: string;
  name: string;
  type: NodeType;
  children?: TreeNode[];
  expanded?: boolean;
  kind?: FileKind;
  depth: number;
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

export type BrowseCategory = 'all' | 'files' | 'docs' | 'specs' | 'kblocks' | 'convos';

export interface BrowseItem {
  id: string;
  path: string;
  title: string;
  category: BrowseCategory;
  preview?: string;
  directory?: string;
  modifiedAt?: Date;
  annotations?: number;
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
