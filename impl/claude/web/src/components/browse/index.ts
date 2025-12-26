/**
 * Browse System Exports
 *
 * Three-tier browsing:
 * 1. FileSidebar (quick actions + file tree) ✅ IMPLEMENTED
 * 2. FileTree (tree view component) ✅ IMPLEMENTED
 * 3. BrowseModal (exhaustive browser) ✅ IMPLEMENTED
 * 4. EdgeViewer (K-Block edge display) ✅ IMPLEMENTED
 */

// Main components
export { FileSidebar } from './FileSidebar';
export type { FileSidebarProps } from './FileSidebar';

export { FileTree } from './FileTree';
export type { FileTreeProps } from './types';

export { BrowseModal } from './BrowseModal';
export type { BrowseModalProps } from './BrowseModal';

export { EdgeViewer } from './EdgeViewer';

// Hooks
export { useFileTree } from './hooks/useFileTree';
export { useBrowse } from './hooks/useBrowse';
export { useBrowseItems } from './hooks/useBrowseItems';

// Shared types
export type {
  UploadedFile,
  TreeNode,
  TreeNodeEdgeData,
  TreeNodeMarkData,
  FileKind,
  NodeKind,
  NodeType,
  EdgeKind,
  BrowseCategory,
  BrowseItem,
  BrowseFilter,
  BrowseFilters,
  BrowseResponse,
  ContentKind,
  // Witness mark types
  WitnessMark,
  MarkBrowseCategory,
  MarkBrowseResponse,
} from './types';
