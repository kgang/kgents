/**
 * FileTree — Traditional file/folder tree for sidebar
 *
 * Features:
 * - Lazy-load directory contents on expand (via graphApi.neighbors)
 * - Toggle expand/collapse with click on folder
 * - File type icons based on extension
 * - Current file highlighting
 * - Filter tree based on searchQuery
 * - Keyboard navigation: j/k to move, Enter to open, h/l to collapse/expand
 *
 * Philosophy: "Tasteful > feature-complete" — compact sidebar tree with visual clarity
 */

import { useEffect, useRef } from 'react';
import {
  ChevronRight,
  Folder,
  FolderOpen,
  FileText,
  FileCode,
  File,
} from 'lucide-react';
import { useFileTree } from './hooks/useFileTree';
import type { FileTreeProps, TreeNode } from './types';
import './FileTree.css';

/**
 * Get icon for tree node based on type and kind.
 */
function getNodeIcon(node: TreeNode, expanded: boolean) {
  if (node.type === 'directory') {
    return expanded ? <FolderOpen size={16} /> : <Folder size={16} />;
  }

  // File icons by kind
  switch (node.kind) {
    case 'doc':
      return <FileText size={16} />;
    case 'code':
      return <FileCode size={16} />;
    case 'spec':
      return <FileText size={16} />;
    default:
      return <File size={16} />;
  }
}

/**
 * FileTree component.
 */
export function FileTree({
  rootPaths,
  onSelectFile,
  currentFile,
  searchQuery,
  maxHeight = '400px',
}: FileTreeProps) {
  const treeRef = useRef<HTMLDivElement>(null);

  const {
    expandedPaths,
    toggleExpand,
    loadChildren,
    selectFile,
    selectedIndex,
    visibleNodes,
    loading,
  } = useFileTree({
    rootPaths,
    searchQuery,
    onSelectFile,
    currentFile,
  });

  // Scroll selected node into view
  useEffect(() => {
    if (treeRef.current) {
      const selectedElement = treeRef.current.querySelector('[data-selected="true"]');
      if (selectedElement) {
        selectedElement.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
      }
    }
  }, [selectedIndex]);

  // Handle node click
  function handleNodeClick(node: TreeNode) {
    if (node.type === 'file') {
      selectFile(node.path);
    } else {
      // Directory: toggle expand and load children if needed
      const isExpanded = expandedPaths.has(node.path);
      toggleExpand(node.path);

      if (!isExpanded && !node.children) {
        loadChildren(node.path);
      }
    }
  }

  // Empty state
  if (visibleNodes.length === 0 && !loading) {
    return (
      <div className="file-tree" style={{ '--max-height': maxHeight } as React.CSSProperties}>
        <div className="file-tree__empty">
          {searchQuery ? `No files matching "${searchQuery}"` : 'No files'}
        </div>
      </div>
    );
  }

  return (
    <div
      ref={treeRef}
      className="file-tree"
      style={{ '--max-height': maxHeight } as React.CSSProperties}
      tabIndex={0}
    >
      {loading && visibleNodes.length === 0 && (
        <div className="file-tree__loading">
          <div className="file-tree__spinner" />
          Loading...
        </div>
      )}

      {visibleNodes.map((node, index) => {
        const isExpanded = expandedPaths.has(node.path);
        const isSelected = index === selectedIndex;
        const isCurrent = node.path === currentFile;

        return (
          <button
            key={node.path}
            className="file-tree__node"
            data-selected={isSelected}
            data-current={isCurrent}
            onClick={() => handleNodeClick(node)}
            style={{ '--depth': node.depth } as React.CSSProperties}
            title={node.path}
          >
            {/* Indentation spacer */}
            <div className="file-tree__indent" />

            {/* Chevron for directories */}
            {node.type === 'directory' && (
              <div className="file-tree__chevron" data-expanded={isExpanded}>
                <ChevronRight size={12} />
              </div>
            )}

            {/* Icon */}
            <div
              className="file-tree__icon"
              data-kind={node.type === 'directory' ? 'directory' : node.kind}
            >
              {getNodeIcon(node, isExpanded)}
            </div>

            {/* Label */}
            <div className="file-tree__label">{node.name}</div>
          </button>
        );
      })}
    </div>
  );
}
