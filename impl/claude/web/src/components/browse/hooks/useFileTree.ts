/**
 * useFileTree — State management for FileTree component
 *
 * Manages:
 * - Tree node expansion/collapse
 * - Lazy loading of directory contents via graphApi.neighbors
 * - Virtual folders for edges, uploads, zero-seed, and witness marks
 * - Keyboard navigation (j/k, Enter, h/l)
 * - Search filtering
 */

import { useState, useEffect, useCallback, useMemo } from 'react';
import { graphApi, edgesApi, kblocksApi, witnessApi } from '../../../api/client';
import type { TreeNode, NodeKind, EdgeKind, WitnessMark } from '../types';
import { getFileKind, getFileName, isDirectory } from '../types';

/**
 * Virtual folder paths for edges, zero-seed, and other virtual content.
 */
const VIRTUAL_FOLDERS = {
  // Edge folders
  EDGES: 'edges/',
  EDGES_DERIVES_FROM: 'edges/derives_from/',
  EDGES_IMPLEMENTS: 'edges/implements/',
  EDGES_TESTS: 'edges/tests/',
  EDGES_REFERENCES: 'edges/references/',
  EDGES_CONTRADICTS: 'edges/contradicts/',
  // Zero Seed folders
  UPLOADS: 'uploads/',
  ZERO_SEED: 'zero-seed/',
  ZERO_SEED_AXIOMS: 'zero-seed/axioms/',
  ZERO_SEED_VALUES: 'zero-seed/values/',
  ZERO_SEED_GOALS: 'zero-seed/goals/',
  // Witness mark folders
  WITNESS: 'witness/',
  WITNESS_TODAY: 'witness/today/',
  WITNESS_DECISIONS: 'witness/decisions/',
  WITNESS_EUREKAS: 'witness/eurekas/',
  WITNESS_GOTCHAS: 'witness/gotchas/',
} as const;

/**
 * Valid edge kinds for the edges/ virtual folder.
 */
const EDGE_KINDS: EdgeKind[] = ['derives_from', 'implements', 'tests', 'references', 'contradicts'];

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
 * Includes virtual folders for edges.
 */
function buildInitialTree(rootPaths: string[]): TreeNode[] {
  const fileNodes: TreeNode[] = rootPaths.map((path) => ({
    path,
    name: getFileName(path),
    type: isDirectory(path) ? 'directory' : 'file',
    kind: getFileKind(path),
    depth: 0,
    expanded: false,
    children: undefined,
  }));

  // Add virtual folders for zero-seed, uploads, edges, and witness
  const virtualFolders: TreeNode[] = [
    // Zero Seed virtual folder - axioms, values, goals
    {
      path: VIRTUAL_FOLDERS.ZERO_SEED,
      name: 'zero-seed',
      type: 'directory',
      kind: 'axiom' as NodeKind,
      depth: 0,
      expanded: false,
      children: [
        {
          path: VIRTUAL_FOLDERS.ZERO_SEED_AXIOMS,
          name: 'axioms',
          type: 'directory',
          kind: 'axiom' as NodeKind,
          depth: 1,
          expanded: false,
          children: undefined,
        },
        {
          path: VIRTUAL_FOLDERS.ZERO_SEED_VALUES,
          name: 'values',
          type: 'directory',
          kind: 'value' as NodeKind,
          depth: 1,
          expanded: false,
          children: undefined,
        },
        {
          path: VIRTUAL_FOLDERS.ZERO_SEED_GOALS,
          name: 'goals',
          type: 'directory',
          kind: 'goal' as NodeKind,
          depth: 1,
          expanded: false,
          children: undefined,
        },
      ],
    },
    // Uploads virtual folder
    {
      path: VIRTUAL_FOLDERS.UPLOADS,
      name: 'uploads',
      type: 'directory',
      kind: 'upload' as NodeKind,
      depth: 0,
      expanded: false,
      children: undefined,
    },
    // Edges virtual folder - K-Block relationships as first-class entities
    {
      path: VIRTUAL_FOLDERS.EDGES,
      name: 'edges',
      type: 'directory',
      kind: 'edge' as NodeKind,
      depth: 0,
      expanded: false,
      children: [
        {
          path: VIRTUAL_FOLDERS.EDGES_DERIVES_FROM,
          name: 'derives_from',
          type: 'directory',
          kind: 'edge_derives_from' as NodeKind,
          depth: 1,
          expanded: false,
          children: undefined,
        },
        {
          path: VIRTUAL_FOLDERS.EDGES_IMPLEMENTS,
          name: 'implements',
          type: 'directory',
          kind: 'edge_implements' as NodeKind,
          depth: 1,
          expanded: false,
          children: undefined,
        },
        {
          path: VIRTUAL_FOLDERS.EDGES_TESTS,
          name: 'tests',
          type: 'directory',
          kind: 'edge_tests' as NodeKind,
          depth: 1,
          expanded: false,
          children: undefined,
        },
        {
          path: VIRTUAL_FOLDERS.EDGES_REFERENCES,
          name: 'references',
          type: 'directory',
          kind: 'edge_references' as NodeKind,
          depth: 1,
          expanded: false,
          children: undefined,
        },
        {
          path: VIRTUAL_FOLDERS.EDGES_CONTRADICTS,
          name: 'contradicts',
          type: 'directory',
          kind: 'edge_contradicts' as NodeKind,
          depth: 1,
          expanded: false,
          children: undefined,
        },
      ],
    },
    // Witness marks virtual folder
    {
      path: VIRTUAL_FOLDERS.WITNESS,
      name: 'witness',
      type: 'directory',
      kind: 'mark' as NodeKind,
      depth: 0,
      expanded: false,
      children: [
        {
          path: VIRTUAL_FOLDERS.WITNESS_TODAY,
          name: 'today',
          type: 'directory',
          kind: 'mark' as NodeKind,
          depth: 1,
          expanded: false,
          children: undefined,
        },
        {
          path: VIRTUAL_FOLDERS.WITNESS_DECISIONS,
          name: 'decisions',
          type: 'directory',
          kind: 'decision' as NodeKind,
          depth: 1,
          expanded: false,
          children: undefined,
        },
        {
          path: VIRTUAL_FOLDERS.WITNESS_EUREKAS,
          name: 'eurekas',
          type: 'directory',
          kind: 'eureka' as NodeKind,
          depth: 1,
          expanded: false,
          children: undefined,
        },
        {
          path: VIRTUAL_FOLDERS.WITNESS_GOTCHAS,
          name: 'gotchas',
          type: 'directory',
          kind: 'gotcha' as NodeKind,
          depth: 1,
          expanded: false,
          children: undefined,
        },
      ],
    },
  ];

  return [...fileNodes, ...virtualFolders];
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
      let children: TreeNode[] = [];

      // Check if this is an edges virtual folder
      if (path.startsWith(VIRTUAL_FOLDERS.EDGES)) {
        // Load from Edges API
        const browseResponse = await edgesApi.browse();
        const depth = path.split('/').filter(Boolean).length;

        // Determine which edge kind folder we're in
        const edgeKind = EDGE_KINDS.find((k) => path === `edges/${k}/`);

        if (edgeKind) {
          // Load edges of this kind
          const edges = browseResponse.by_kind[edgeKind] || [];
          children = edges.map((edge) => ({
            path: `edges/${edgeKind}/${edge.id}`,
            name: `${edge.source_title} -> ${edge.target_title}`,
            type: 'file' as const,
            kind: `edge_${edgeKind}` as NodeKind,
            depth,
            expanded: false,
            children: undefined,
            // Store edge metadata for display
            edgeData: {
              id: edge.id,
              sourceId: edge.source_id,
              targetId: edge.target_id,
              sourcePath: edge.source_path,
              targetPath: edge.target_path,
              confidence: edge.confidence,
              context: edge.context,
              markId: edge.mark_id,
            },
          }));
        } else if (path === VIRTUAL_FOLDERS.EDGES) {
          // Return child folders (already created in buildInitialTree)
          children = [];  // Let the parent expand show the static children
        }
      } else if (path === VIRTUAL_FOLDERS.UPLOADS || path.startsWith(VIRTUAL_FOLDERS.ZERO_SEED)) {
        // Load from unified K-Blocks API (PostgreSQL)
        const browseResponse = await kblocksApi.browse();
        const depth = path.split('/').filter(Boolean).length;

        if (path === VIRTUAL_FOLDERS.UPLOADS) {
          // Show uploaded content (user K-Blocks)
          children = browseResponse.user.map((kb) => ({
            path: kb.path,
            name: kb.title,
            type: 'file' as const,
            kind: 'upload' as NodeKind,
            depth,
            expanded: false,
            children: undefined,
          }));
        } else if (path === VIRTUAL_FOLDERS.ZERO_SEED_AXIOMS) {
          // Filter to axioms (L1 and ground)
          const axioms = browseResponse.zero_seed.axioms || [];
          children = axioms.map((kb) => ({
            // Use zero-seed/{category}/{id} format for loadNode compatibility
            path: `zero-seed/axioms/${kb.id}`,
            name: kb.title,
            type: 'file' as const,
            kind: 'axiom' as NodeKind,
            depth,
            layer: kb.layer ?? undefined,
            galoisLoss: kb.galois_loss,
            expanded: false,
            children: undefined,
          }));
        } else if (path === VIRTUAL_FOLDERS.ZERO_SEED_VALUES) {
          // Filter to values (L2)
          const values = browseResponse.zero_seed.values || [];
          children = values.map((kb) => ({
            // Use zero-seed/{category}/{id} format for loadNode compatibility
            path: `zero-seed/values/${kb.id}`,
            name: kb.title,
            type: 'file' as const,
            kind: 'value' as NodeKind,
            depth,
            layer: kb.layer ?? undefined,
            galoisLoss: kb.galois_loss,
            expanded: false,
            children: undefined,
          }));
        } else if (path === VIRTUAL_FOLDERS.ZERO_SEED_GOALS) {
          // Filter to goals (L3-L4)
          const goals = browseResponse.zero_seed.goals || [];
          const specs = browseResponse.zero_seed.specs || [];
          children = [...goals, ...specs].map((kb) => ({
            // Use zero-seed/{category}/{id} format for loadNode compatibility
            path: `zero-seed/goals/${kb.id}`,
            name: kb.title,
            type: 'file' as const,
            kind: 'goal' as NodeKind,
            depth,
            layer: kb.layer ?? undefined,
            galoisLoss: kb.galois_loss,
            expanded: false,
            children: undefined,
          }));
        } else if (path === VIRTUAL_FOLDERS.ZERO_SEED) {
          // Return child folders (already created in buildInitialTree)
          children = [];  // Let the parent expand show the static children
        }
      } else if (path.startsWith(VIRTUAL_FOLDERS.WITNESS)) {
        // Load from Witness API
        const browseResponse = await witnessApi.browse();
        const depth = path.split('/').filter(Boolean).length;

        /**
         * Convert witness marks to tree nodes with full metadata.
         * Includes reasoning preview for tooltips and principles for badges.
         */
        const marksToNodes = (marks: WitnessMark[], kind: NodeKind): TreeNode[] => {
          return marks.map((mark) => ({
            path: `witness/mark/${mark.id}`,
            name: mark.action.slice(0, 50) + (mark.action.length > 50 ? '...' : ''),
            type: 'file' as const,
            kind,
            depth,
            expanded: false,
            children: undefined,
            // Full mark metadata for display
            markData: {
              id: mark.id,
              action: mark.action,
              reasoning: mark.reasoning,
              principles: mark.principles || [],
              author: mark.author,
              timestamp: mark.timestamp,
              retracted: mark.retracted,
            },
            // Use timestamp for breathing animation (recent items glow)
            modifiedAt: mark.timestamp,
          }));
        };

        if (path === VIRTUAL_FOLDERS.WITNESS_TODAY) {
          children = marksToNodes(browseResponse.today.marks, 'mark');
        } else if (path === VIRTUAL_FOLDERS.WITNESS_DECISIONS) {
          children = marksToNodes(browseResponse.decisions.marks, 'decision');
        } else if (path === VIRTUAL_FOLDERS.WITNESS_EUREKAS) {
          children = marksToNodes(browseResponse.eurekas.marks, 'eureka');
        } else if (path === VIRTUAL_FOLDERS.WITNESS_GOTCHAS) {
          children = marksToNodes(browseResponse.gotchas.marks, 'gotcha');
        } else if (path === VIRTUAL_FOLDERS.WITNESS) {
          // Return child folders (already created in buildInitialTree)
          children = [];  // Let the parent expand show the static children
        }
      } else {
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
        children = Array.from(childPaths)
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
      }

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
