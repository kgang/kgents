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

import { memo, useEffect, useRef } from 'react';
import {
  ChevronRight,
  Folder,
  FolderOpen,
  FileText,
  FileCode,
  File,
  Upload,
  Sparkles,
  Target,
  Zap,
  Eye,
  Image,
  Gem,
  MapPin,
  // Witness mark icons
  Bookmark,
  GitBranch,
  Lightbulb,
  AlertTriangle,
  // Edge icons
  Link,
  ArrowRight,
  GitMerge,
  FlaskConical,
  FileSymlink,
  Ban,
} from 'lucide-react';
import { useFileTree } from './hooks/useFileTree';
import type { FileTreeProps, TreeNode } from './types';
import './FileTree.css';

/**
 * Check if a node was modified within the last N seconds.
 * Used for breathing animation on recently modified items.
 */
function isRecentlyModified(node: TreeNode, thresholdSeconds = 60): boolean {
  if (!node.modifiedAt) return false;
  const modifiedTime = new Date(node.modifiedAt).getTime();
  const now = Date.now();
  return now - modifiedTime < thresholdSeconds * 1000;
}

/**
 * Get confidence level for display ('high', 'medium', 'low').
 */
function getConfidenceLevel(confidence: number): 'high' | 'medium' | 'low' {
  if (confidence >= 0.8) return 'high';
  if (confidence >= 0.5) return 'medium';
  return 'low';
}

/**
 * Build tooltip text for a node based on its metadata.
 */
function getNodeTooltip(node: TreeNode): string {
  const parts: string[] = [node.path];

  // Mark metadata - show reasoning preview
  if (node.markData) {
    if (node.markData.reasoning) {
      const preview = node.markData.reasoning.slice(0, 100);
      parts.push(`Reasoning: ${preview}${node.markData.reasoning.length > 100 ? '...' : ''}`);
    }
    if (node.markData.principles.length > 0) {
      parts.push(`Principles: ${node.markData.principles.join(', ')}`);
    }
    if (node.markData.retracted) {
      parts.push('[RETRACTED]');
    }
  }

  // Edge metadata - show source/target paths and confidence
  if (node.edgeData) {
    parts.push(`From: ${node.edgeData.sourcePath}`);
    parts.push(`To: ${node.edgeData.targetPath}`);
    parts.push(`Confidence: ${Math.round(node.edgeData.confidence * 100)}%`);
    if (node.edgeData.context) {
      parts.push(`Context: ${node.edgeData.context}`);
    }
  }

  // K-Block metadata - show layer and galois loss
  if (node.layer !== undefined) {
    parts.push(`Layer: L${node.layer}`);
  }
  if (node.galoisLoss !== undefined) {
    parts.push(`Galois Loss: ${node.galoisLoss.toFixed(3)}`);
  }

  return parts.join('\n');
}

/**
 * Get icon for tree node based on type and kind.
 * Supports: files, directories, uploads, Zero Seed content kinds, Witness marks, and Edges.
 */
function getNodeIcon(node: TreeNode, expanded: boolean) {
  if (node.type === 'directory') {
    // Special folder icons for virtual folders
    if (node.path === 'uploads/') {
      return <Upload size={16} />;
    }
    if (node.path === 'zero-seed/') {
      return <Sparkles size={16} />;
    }
    // Witness folder icons
    if (node.path === 'witness/') {
      return <Bookmark size={16} />;
    }
    if (node.path === 'witness/decisions/') {
      return <GitBranch size={16} />;
    }
    if (node.path === 'witness/eurekas/') {
      return <Lightbulb size={16} />;
    }
    if (node.path === 'witness/gotchas/') {
      return <AlertTriangle size={16} />;
    }
    // Edge folder icons
    if (node.path === 'edges/') {
      return <Link size={16} />;
    }
    if (node.path === 'edges/derives_from/') {
      return <ArrowRight size={16} />;
    }
    if (node.path === 'edges/implements/') {
      return <GitMerge size={16} />;
    }
    if (node.path === 'edges/tests/') {
      return <FlaskConical size={16} />;
    }
    if (node.path === 'edges/references/') {
      return <FileSymlink size={16} />;
    }
    if (node.path === 'edges/contradicts/') {
      return <Ban size={16} />;
    }
    return expanded ? <FolderOpen size={16} /> : <Folder size={16} />;
  }

  // File icons by kind (includes Zero Seed content kinds and Witness marks)
  switch (node.kind) {
    // Document types
    case 'doc':
      return <FileText size={16} />;
    case 'code':
      return <FileCode size={16} />;
    case 'spec':
      return <FileText size={16} />;

    // Upload type
    case 'upload':
      return <Upload size={16} />;

    // Zero Seed content kinds (L1-L7)
    case 'axiom':
      return <MapPin size={16} />;
    case 'value':
      return <Gem size={16} />;
    case 'goal':
      return <Target size={16} />;
    case 'action':
      return <Zap size={16} />;
    case 'reflection':
      return <Eye size={16} />;
    case 'representation':
      return <Image size={16} />;

    // Witness mark types
    case 'mark':
      return <Bookmark size={16} />;
    case 'decision':
      return <GitBranch size={16} />;
    case 'eureka':
      return <Lightbulb size={16} />;
    case 'gotcha':
      return <AlertTriangle size={16} />;

    // Edge types (files representing K-Block edges)
    case 'edge':
      return <Link size={16} />;
    case 'edge_derives_from':
      return <ArrowRight size={16} />;
    case 'edge_implements':
      return <GitMerge size={16} />;
    case 'edge_tests':
      return <FlaskConical size={16} />;
    case 'edge_references':
      return <FileSymlink size={16} />;
    case 'edge_contradicts':
      return <Ban size={16} />;

    default:
      return <File size={16} />;
  }
}

/**
 * FileTree component.
 *
 * Wrapped in React.memo to prevent re-renders when parent state changes
 * (e.g., when navigating to a new document, the tree structure doesn't change).
 */
export const FileTree = memo(function FileTree({
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
        const isBreathing = isRecentlyModified(node);
        const isRetracted = node.markData?.retracted ?? false;

        return (
          <button
            key={node.path}
            className="file-tree__node"
            data-selected={isSelected}
            data-current={isCurrent}
            data-breathing={isBreathing}
            data-retracted={isRetracted}
            onClick={() => handleNodeClick(node)}
            style={{ '--depth': node.depth } as React.CSSProperties}
            title={getNodeTooltip(node)}
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

            {/* Badges container */}
            <div className="file-tree__badges">
              {/* Layer badge for K-Block nodes */}
              {node.layer !== undefined && (
                <span className="file-tree__badge file-tree__badge--layer" data-layer={node.layer}>
                  L{node.layer}
                </span>
              )}

              {/* Confidence badge for edge nodes */}
              {node.edgeData && (
                <span
                  className="file-tree__badge file-tree__badge--confidence"
                  data-confidence={getConfidenceLevel(node.edgeData.confidence)}
                >
                  {Math.round(node.edgeData.confidence * 100)}%
                </span>
              )}

              {/* Principles count badge for marks with principles */}
              {node.markData && node.markData.principles.length > 0 && (
                <span className="file-tree__badge file-tree__badge--principles">
                  {node.markData.principles.length}P
                </span>
              )}
            </div>
          </button>
        );
      })}
    </div>
  );
});
