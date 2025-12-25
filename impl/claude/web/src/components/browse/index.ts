/**
 * Browse System Exports
 *
 * Three-tier browsing:
 * 1. FileSidebar (quick actions + file tree) ✅ IMPLEMENTED
 * 2. FileTree (tree view component) ✅ IMPLEMENTED
 * 3. BrowseModal (exhaustive browser) ✅ IMPLEMENTED
 */

// Main components
export { FileSidebar } from './FileSidebar';
export type { FileSidebarProps } from './FileSidebar';

export { FileTree } from './FileTree';
export type { FileTreeProps } from './types';

export { BrowseModal } from './BrowseModal';
export type { BrowseModalProps } from './BrowseModal';

// Hooks
export { useFileTree } from './hooks/useFileTree';
export { useBrowse } from './hooks/useBrowse';

// Shared types
export type {
  UploadedFile,
  TreeNode,
  FileKind,
  NodeType,
  BrowseCategory,
  BrowseItem,
  BrowseFilter,
  BrowseFilters,
  BrowseResponse,
} from './types';
