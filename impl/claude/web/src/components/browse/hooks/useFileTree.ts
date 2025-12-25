/**
 * useFileTree — State management for FileTree component
 *
 * Manages:
 * - Tree node expansion/collapse
 * - Lazy loading of directory contents via graphApi.neighbors
 * - Keyboard navigation (j/k, Enter, h/l)
 * - Search filtering
 */

import { useState, useEffect, useCallback, useMemo } from 'react';
import { graphApi } from '../../../api/client';
import type { TreeNode } from '../types';
import { getFileKind, getFileName, isDirectory } from '../types';

export interface UseFileTreeOptions {
  rootPaths?: string[];
  searchQuery?: string;
  onSelectFile: (path: string) => void;
  currentFile?: string;
}

export interface UseFileTreeReturn {
  nodes: TreeNode[];
  expandedPaths: Set<string>;
  toggleExpand: (path: string) => void;
  loadChildren: (path: string) => Promise<void>;
  selectFile: (path: string) => void;
  selectedIndex: number;
  setSelectedIndex: (index: number) => void;
  visibleNodes: TreeNode[];
  loading: boolean;
}

/**
 * Build initial tree structure from root paths.
 */
function buildInitialTree(rootPaths: string[]): TreeNode[] {
  return rootPaths.map((path) => ({
    path,
    name: getFileName(path),
    type: isDirectory(path) ? 'directory' : 'file',
    kind: getFileKind(path),
    depth: 0,
    expanded: false,
    children: undefined,
  }));
}

/**
 * Flatten tree into visible nodes (respecting expanded state).
 */
function flattenTree(nodes: TreeNode[], expandedPaths: Set<string>): TreeNode[] {
  const result: TreeNode[] = [];

  function traverse(node: TreeNode) {
    result.push(node);

    if (node.type === 'directory' && expandedPaths.has(node.path) && node.children) {
      node.children.forEach(traverse);
    }
  }

  nodes.forEach(traverse);
  return result;
}

/**
 * Filter tree nodes by search query.
 */
function filterTree(nodes: TreeNode[], query: string): TreeNode[] {
  if (!query.trim()) return nodes;

  const lowerQuery = query.toLowerCase();

  function matchesQuery(node: TreeNode): boolean {
    return node.name.toLowerCase().includes(lowerQuery) || node.path.toLowerCase().includes(lowerQuery);
  }

  function filterNode(node: TreeNode): TreeNode | null {
    if (matchesQuery(node)) {
      return node; // Include this node and all children
    }

    if (node.children) {
      const filteredChildren = node.children.map(filterNode).filter((n): n is TreeNode => n !== null);
      if (filteredChildren.length > 0) {
        return { ...node, children: filteredChildren };
      }
    }

    return null;
  }

  return nodes.map(filterNode).filter((n): n is TreeNode => n !== null);
}

export function useFileTree(options: UseFileTreeOptions): UseFileTreeReturn {
  const { rootPaths = ['spec/', 'impl/', 'docs/'], searchQuery = '', onSelectFile } = options;

  const [nodes, setNodes] = useState<TreeNode[]>(() => buildInitialTree(rootPaths));
  const [expandedPaths, setExpandedPaths] = useState<Set<string>>(new Set());
  const [selectedIndex, setSelectedIndex] = useState(0);
  const [loading, setLoading] = useState(false);

  // Filter nodes based on search query
  const filteredNodes = useMemo(() => filterTree(nodes, searchQuery), [nodes, searchQuery]);

  // Flatten filtered tree into visible nodes
  const visibleNodes = useMemo(
    () => flattenTree(filteredNodes, expandedPaths),
    [filteredNodes, expandedPaths]
  );

  // Toggle expand/collapse
  const toggleExpand = useCallback((path: string) => {
    setExpandedPaths((prev) => {
      const next = new Set(prev);
      if (next.has(path)) {
        next.delete(path);
      } else {
        next.add(path);
      }
      return next;
    });
  }, []);

  // Load children for a directory
  const loadChildren = useCallback(async (path: string) => {
    setLoading(true);
    try {
      // Use graphApi.neighbors to get connected nodes (directory contents)
      const response = await graphApi.neighbors(path);

      // Extract file paths from edges
      const childPaths = new Set<string>();

      // Collect all unique paths from incoming and outgoing edges
      response.incoming.forEach((edge) => {
        childPaths.add(edge.source_path);
      });
      response.outgoing.forEach((edge) => {
        childPaths.add(edge.target_path);
      });

      // Filter out the parent path itself and build child nodes
      const children: TreeNode[] = Array.from(childPaths)
        .filter((p) => p !== path && p.startsWith(path))
        .map((childPath) => ({
          path: childPath,
          name: getFileName(childPath),
          type: (isDirectory(childPath) ? 'directory' : 'file') as 'directory' | 'file',
          kind: getFileKind(childPath),
          depth: path.split('/').filter(Boolean).length,
          expanded: false,
          children: undefined,
        }))
        .sort((a, b) => {
          // Directories first, then alphabetical
          if (a.type !== b.type) {
            return a.type === 'directory' ? -1 : 1;
          }
          return a.name.localeCompare(b.name);
        });

      // Update node with children
      setNodes((prev) => updateNodeChildren(prev, path, children));
    } catch (error) {
      console.error('Failed to load children for', path, error);
    } finally {
      setLoading(false);
    }
  }, []);

  // Helper to update a node's children
  function updateNodeChildren(nodes: TreeNode[], targetPath: string, children: TreeNode[]): TreeNode[] {
    return nodes.map((node) => {
      if (node.path === targetPath) {
        return { ...node, children };
      }
      if (node.children) {
        return { ...node, children: updateNodeChildren(node.children, targetPath, children) };
      }
      return node;
    });
  }

  // Select file
  const selectFile = useCallback(
    (path: string) => {
      onSelectFile(path);
    },
    [onSelectFile]
  );

  // Keyboard navigation
  useEffect(() => {
    function handleKeyDown(e: KeyboardEvent) {
      // Only handle if FileTree is focused
      if (!document.activeElement?.closest('.file-tree')) return;

      switch (e.key) {
        case 'j':
        case 'ArrowDown':
          e.preventDefault();
          setSelectedIndex((prev) => Math.min(prev + 1, visibleNodes.length - 1));
          break;

        case 'k':
        case 'ArrowUp':
          e.preventDefault();
          setSelectedIndex((prev) => Math.max(prev - 1, 0));
          break;

        case 'Enter':
          e.preventDefault();
          if (visibleNodes[selectedIndex]) {
            const node = visibleNodes[selectedIndex];
            if (node.type === 'file') {
              selectFile(node.path);
            } else {
              // Expand/collapse directory
              toggleExpand(node.path);
              if (!expandedPaths.has(node.path) && !node.children) {
                loadChildren(node.path);
              }
            }
          }
          break;

        case 'h':
        case 'ArrowLeft':
          e.preventDefault();
          if (visibleNodes[selectedIndex]) {
            const node = visibleNodes[selectedIndex];
            if (node.type === 'directory' && expandedPaths.has(node.path)) {
              toggleExpand(node.path);
            }
          }
          break;

        case 'l':
        case 'ArrowRight':
          e.preventDefault();
          if (visibleNodes[selectedIndex]) {
            const node = visibleNodes[selectedIndex];
            if (node.type === 'directory') {
              if (!expandedPaths.has(node.path)) {
                toggleExpand(node.path);
                if (!node.children) {
                  loadChildren(node.path);
                }
              }
            }
          }
          break;
      }
    }

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [visibleNodes, selectedIndex, expandedPaths, selectFile, toggleExpand, loadChildren]);

  // Auto-expand root directories on mount
  useEffect(() => {
    rootPaths.forEach((path) => {
      if (isDirectory(path)) {
        setExpandedPaths((prev) => new Set(prev).add(path));
        loadChildren(path);
      }
    });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return {
    nodes: filteredNodes,
    expandedPaths,
    toggleExpand,
    loadChildren,
    selectFile,
    selectedIndex,
    setSelectedIndex,
    visibleNodes,
    loading,
  };
}
