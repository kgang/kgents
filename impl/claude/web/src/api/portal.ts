/**
 * Portal Token API - AGENTESE Universal Protocol
 *
 * "You don't go to the document. The document comes to you."
 *
 * Routes:
 *   self.portal.manifest - Get portal tree for a file
 *   self.portal.expand - Expand a portal node
 *   self.portal.collapse - Collapse a portal node
 *
 * @see spec/protocols/portal-token.md Phase 5
 */

import { useCallback, useState } from 'react';
import { apiClient, AgenteseError } from './client';

// =============================================================================
// Types
// =============================================================================

/**
 * Portal token states.
 * From spec/protocols/portal-token.md Section 4.1
 */
export type PortalState = 'collapsed' | 'loading' | 'expanded' | 'error';

/**
 * A node in the portal expansion tree.
 */
export interface PortalNode {
  /** Path of this node (file path or AGENTESE path) */
  path: string;
  /** Edge type that led here (null for root) */
  edge_type: string | null;
  /** Whether this node is expanded */
  expanded: boolean;
  /** Child nodes */
  children: PortalNode[];
  /** Nesting depth */
  depth: number;
  /** Current loading state */
  state?: PortalState;
  /** Error message if state is 'error' */
  error?: string;
  /** Note/description for this edge */
  note?: string | null;
  /** Content when expanded */
  content?: string | null;
}

/**
 * Portal tree response from self.portal.manifest.
 */
export interface PortalTree {
  /** Root node of the tree */
  root: PortalNode;
  /** Maximum depth allowed */
  max_depth: number;
}

/**
 * Response wrapper from AGENTESE gateway.
 */
interface AgenteseResponse<T> {
  path: string;
  aspect: string;
  result: T;
  error?: string;
}

/**
 * Error codes for portal expansion failures.
 * Matches: protocols/file_operad/portal.py::ExpandErrorCode
 */
export type PortalErrorCode =
  | 'path_not_found'
  | 'depth_limit_reached'
  | 'file_not_found'
  | 'file_not_readable'
  | 'no_portals_discovered'
  | 'expansion_failed'
  | 'collapse_failed';

/**
 * Canonical PortalResponse from backend.
 *
 * This is the CONTRACT between frontend and backend.
 * Matches: protocols/agentese/contexts/portal_response.py
 *
 * @see plans/portal-fullstack-integration.md Phase 1
 */
export interface PortalResponse {
  /** Whether the operation succeeded */
  success: boolean;
  /** AGENTESE path that was invoked */
  path: string;
  /** Which aspect was called */
  aspect: string;
  /** Portal tree state (when available) */
  tree?: PortalTree;
  /** For expand: which path was expanded */
  expanded_path?: string;
  /** For collapse: which path was collapsed */
  collapsed_path?: string;
  /** Trail ID if trail was recorded */
  trail_id?: string;
  /** Witness mark ID if evidence was captured (Phase 2) */
  evidence_id?: string;
  /** Error message if success=false */
  error?: string;
  /** Machine-readable error code */
  error_code?: PortalErrorCode;
  /** Additional metadata */
  metadata?: {
    portal_path?: string;
    /** Current depth when depth_limit_reached */
    depth?: number;
    /** Max allowed depth when depth_limit_reached */
    max_depth?: number;
    /** Helpful suggestion for what to do next */
    suggestion?: string;
    [key: string]: unknown;
  };
}

/**
 * Request to expand a portal.
 */
export interface PortalExpandRequest {
  /** File path to expand portals for */
  file_path: string;
  /** Portal path to expand (e.g., ["imports", "pathlib"]) */
  portal_path: string[];
  /** Edge type to expand */
  edge_type?: string;
  /** Response format (json for frontend) */
  response_format?: 'cli' | 'json';
}

/**
 * Response from portal expansion.
 * @deprecated Use PortalResponse instead
 */
export interface PortalExpandResponse {
  /** Whether expansion succeeded */
  success: boolean;
  /** Updated tree (or subtree) */
  tree?: PortalTree;
  /** Error message if failed */
  error?: string;
}

/**
 * Edge type visual configuration.
 */
export const PORTAL_EDGE_CONFIG: Record<string, { color: string; icon: string }> = {
  imports: { color: '#3b82f6', icon: 'arrow-down' },
  tests: { color: '#22c55e', icon: 'test-tube' },
  implements: { color: '#8b5cf6', icon: 'scroll' },
  contains: { color: '#f59e0b', icon: 'folder' },
  calls: { color: '#ec4899', icon: 'phone' },
  related: { color: '#6b7280', icon: 'link' },
  default: { color: '#64748b', icon: 'arrow-right' },
};

// =============================================================================
// Error Message Helpers
// =============================================================================

/**
 * Get a user-friendly error message for a portal error.
 * These messages are sympathetic - they explain what happened and what to try.
 */
function getPortalErrorMessage(response: PortalResponse): string {
  const { error_code, error, metadata } = response;

  switch (error_code) {
    case 'depth_limit_reached':
      return `You've explored ${metadata?.depth ?? '?'} levels deep (max: ${metadata?.max_depth ?? 40}). ` +
        'Try collapsing some branches to explore other paths.';

    case 'path_not_found':
      return 'This portal path could not be found. ' +
        'The tree may have changed - try refreshing the view.';

    case 'file_not_found':
      return 'The file no longer exists at this location. ' +
        'It may have been moved, renamed, or deleted.';

    case 'file_not_readable':
      return 'The file exists but could not be read. ' +
        'It may have syntax errors or encoding issues.';

    case 'no_portals_discovered':
      return 'This file has no discoverable connections. ' +
        'It may be a standalone utility or configuration file.';

    default:
      return error || 'Expansion failed for an unknown reason.';
  }
}

/**
 * Get the suggestion text from a portal error response.
 */
function getPortalErrorSuggestion(response: PortalResponse): string | null {
  return response.metadata?.suggestion ?? null;
}

/**
 * Check if an error is specifically a depth limit error.
 * Useful for showing a distinct UI treatment.
 */
function isDepthLimitError(response: PortalResponse): boolean {
  return response.error_code === 'depth_limit_reached';
}

// =============================================================================
// API Functions
// =============================================================================

/**
 * Unwrap AGENTESE gateway response.
 */
function unwrapAgentese<T>(response: { data: AgenteseResponse<T> }): T {
  if (!response.data) {
    throw new AgenteseError('Portal response missing data envelope', 'self.portal', undefined);
  }
  if (response.data.error) {
    throw new AgenteseError(response.data.error, response.data.path, response.data.aspect);
  }
  return response.data.result;
}

/**
 * Get portal tree for a file path.
 *
 * @param filePath - Path to the source file
 * @param maxDepth - Maximum expansion depth (default: 5)
 * @param expandAll - Whether to expand all portals immediately
 */
async function getPortalTree(
  filePath: string,
  maxDepth = 5,
  expandAll = false
): Promise<PortalTree> {
  const response = await apiClient.post<AgenteseResponse<PortalResponse>>(
    '/agentese/self/portal/manifest',
    {
      file_path: filePath,
      max_depth: maxDepth,
      expand_all: expandAll,
      response_format: 'json', // Use canonical PortalResponse shape
    }
  );
  const portalResponse = unwrapAgentese(response);
  if (!portalResponse.tree) {
    throw new AgenteseError('Portal response missing tree', 'self.portal', 'manifest');
  }
  return portalResponse.tree;
}

/**
 * Expand a portal at the given path.
 *
 * @param filePath - Path to the root source file
 * @param portalPath - Path through the tree to the portal to expand
 * @param edgeType - Optional edge type being expanded
 * @returns PortalResponse with tree and evidence_id (Phase 2)
 */
async function expandPortal(
  filePath: string,
  portalPath: string[],
  edgeType?: string
): Promise<PortalResponse> {
  const response = await apiClient.post<AgenteseResponse<PortalResponse>>(
    '/agentese/self/portal/expand',
    {
      file_path: filePath,
      portal_path: JSON.stringify(portalPath), // JSON-encoded array (path segments may contain '/')
      edge_type: edgeType,
      response_format: 'json', // Use canonical PortalResponse shape
    }
  );
  return unwrapAgentese(response);
}

/**
 * Collapse a portal at the given path.
 *
 * @param filePath - Path to the root source file
 * @param portalPath - Path through the tree to the portal to collapse
 */
async function collapsePortal(
  filePath: string,
  portalPath: string[]
): Promise<PortalResponse> {
  const response = await apiClient.post<AgenteseResponse<PortalResponse>>(
    '/agentese/self/portal/collapse',
    {
      file_path: filePath,
      portal_path: JSON.stringify(portalPath), // JSON-encoded array (path segments may contain '/')
      response_format: 'json', // Use canonical PortalResponse shape
    }
  );
  return unwrapAgentese(response);
}

// =============================================================================
// React Hooks
// =============================================================================

/**
 * State for the usePortalTree hook.
 */
export interface PortalTreeState {
  tree: PortalTree | null;
  loading: boolean;
  error: string | null;
  /** Paths of nodes currently being expanded */
  expandingPaths: Set<string>;
  /** Evidence IDs for witnessed portal expansions (path -> evidence_id) */
  evidenceIds: Map<string, string>;
}

/**
 * Hook for managing a portal tree.
 *
 * @param initialPath - Initial file path to load (null to skip initial fetch)
 *
 * @example
 * ```tsx
 * const { tree, loading, error, loadTree, expand, collapse } = usePortalTree();
 *
 * // Load a file's portals
 * await loadTree("impl/claude/services/brain/core.py");
 *
 * // Expand a portal
 * await expand(["imports"]);
 * ```
 */
export function usePortalTree(_initialPath: string | null = null) {
  const [state, setState] = useState<PortalTreeState>({
    tree: null,
    loading: false,
    error: null,
    expandingPaths: new Set(),
    evidenceIds: new Map(),
  });

  /**
   * Load portal tree for a file.
   */
  const loadTree = useCallback(async (filePath: string, expandAll = false) => {
    setState((prev) => ({ ...prev, loading: true, error: null }));

    try {
      const tree = await getPortalTree(filePath, 40, expandAll);  // Allow deep exploration
      setState((prev) => ({ ...prev, tree, loading: false }));
      return tree;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to load portal tree';
      setState((prev) => ({ ...prev, loading: false, error: message }));
      return null;
    }
  }, []);

  /**
   * Expand a portal at the given path.
   */
  const expand = useCallback(
    async (portalPath: string[], edgeType?: string) => {
      if (!state.tree) return false;

      const pathKey = portalPath.join('/');

      // Mark as expanding
      setState((prev) => ({
        ...prev,
        expandingPaths: new Set([...prev.expandingPaths, pathKey]),
      }));

      try {
        // Get root file path from tree
        const filePath = state.tree.root.path;

        // Optimistic update: mark node as expanded
        const optimisticTree = updateNodeState(state.tree, portalPath, {
          expanded: true,
          state: 'loading',
        });
        setState((prev) => ({ ...prev, tree: optimisticTree }));

        // Fetch actual expansion (returns PortalResponse)
        const response = await expandPortal(filePath, portalPath, edgeType);

        if (response.success && response.tree) {
          // Merge response tree into our tree
          const mergedTree = mergeSubtree(state.tree, portalPath, {
            root: response.tree.root,
            max_depth: response.tree.max_depth,
          });

          // Phase 2: Track evidence_id for witnessed expansions
          const updatedEvidenceIds = new Map(state.evidenceIds);
          if (response.evidence_id) {
            updatedEvidenceIds.set(pathKey, response.evidence_id);
            console.debug('[Portal] Expansion witnessed:', response.evidence_id);
          }

          setState((prev) => ({
            ...prev,
            tree: mergedTree,
            expandingPaths: new Set([...prev.expandingPaths].filter((p) => p !== pathKey)),
            evidenceIds: updatedEvidenceIds,
          }));

          return true;
        }
        // Revert on failure - use sympathetic error message
        const errorMessage = getPortalErrorMessage(response);
        const revertedTree = updateNodeState(state.tree, portalPath, {
          expanded: false,
          state: 'error',
          error: errorMessage,
        });
        setState((prev) => ({
          ...prev,
          tree: revertedTree,
          error: isDepthLimitError(response)
            ? `⚠️ ${errorMessage}` // Depth limit gets special treatment
            : errorMessage,
          expandingPaths: new Set([...prev.expandingPaths].filter((p) => p !== pathKey)),
        }));
        return false;
      } catch (err) {
        const message = err instanceof Error ? err.message : 'Expansion failed';
        const errorTree = updateNodeState(state.tree, portalPath, {
          expanded: false,
          state: 'error',
          error: message,
        });
        setState((prev) => ({
          ...prev,
          tree: errorTree,
          expandingPaths: new Set([...prev.expandingPaths].filter((p) => p !== pathKey)),
        }));
        return false;
      }
    },
    [state.tree]
  );

  /**
   * Collapse a portal at the given path.
   */
  const collapse = useCallback(
    async (portalPath: string[]) => {
      if (!state.tree) return false;

      // Optimistic update
      const updatedTree = updateNodeState(state.tree, portalPath, {
        expanded: false,
        state: 'collapsed',
      });
      setState((prev) => ({ ...prev, tree: updatedTree }));

      // Optionally sync with backend
      // await collapsePortal(state.tree.root.path, portalPath);

      return true;
    },
    [state.tree]
  );

  /**
   * Check if a path is currently expanding.
   */
  const isExpanding = useCallback(
    (portalPath: string[]) => {
      const pathKey = portalPath.join('/');
      return state.expandingPaths.has(pathKey);
    },
    [state.expandingPaths]
  );

  /**
   * Get evidence_id for a portal path (if witnessed).
   */
  const getEvidenceId = useCallback(
    (portalPath: string[]) => {
      const pathKey = portalPath.join('/');
      return state.evidenceIds.get(pathKey);
    },
    [state.evidenceIds]
  );

  return {
    tree: state.tree,
    loading: state.loading,
    error: state.error,
    loadTree,
    expand,
    collapse,
    isExpanding,
    getEvidenceId,
  };
}

// =============================================================================
// Tree Manipulation Helpers
// =============================================================================

/**
 * Update a node's state at the given path in the tree.
 */
function updateNodeState(
  tree: PortalTree,
  portalPath: string[],
  updates: Partial<PortalNode>
): PortalTree {
  const newRoot = updateNodeRecursive(tree.root, portalPath, 0, updates);
  return { ...tree, root: newRoot };
}

function updateNodeRecursive(
  node: PortalNode,
  path: string[],
  pathIndex: number,
  updates: Partial<PortalNode>
): PortalNode {
  // At target path
  if (pathIndex >= path.length) {
    return { ...node, ...updates };
  }

  // Find matching child
  const targetEdge = path[pathIndex];
  const updatedChildren = node.children.map((child) => {
    if (child.edge_type === targetEdge || child.path === targetEdge) {
      return updateNodeRecursive(child, path, pathIndex + 1, updates);
    }
    return child;
  });

  return { ...node, children: updatedChildren };
}

/**
 * Merge a response subtree into the main tree at the given path.
 */
function mergeSubtree(
  tree: PortalTree,
  portalPath: string[],
  subtree: PortalTree
): PortalTree {
  // Find the expanded node in the response tree by following the portal path
  // The response tree is rooted at the file, so we need to navigate to the
  // specific node that was expanded.
  let expandedNode = subtree.root;
  for (const segment of portalPath) {
    const child = expandedNode.children?.find(
      (c) => c.edge_type === segment || c.path === segment
    );
    if (child) {
      expandedNode = child;
    } else {
      // If we can't find the path, fall back to marking as expanded without children
      console.warn(`[mergeSubtree] Could not find segment "${segment}" in response tree`);
      return updateNodeState(tree, portalPath, {
        expanded: true,
        state: 'expanded',
      });
    }
  }

  // Now expandedNode points to the correct node in the response tree
  // Use its children (if any) and expanded state
  return updateNodeState(tree, portalPath, {
    expanded: true,
    state: 'expanded',
    children: expandedNode.children || [],
  });
}

// =============================================================================
// Exports
// =============================================================================

export {
  getPortalTree,
  expandPortal,
  collapsePortal,
  getPortalErrorMessage,
  getPortalErrorSuggestion,
  isDepthLimitError,
};
// Note: PortalResponse, PortalErrorCode are already exported as interfaces above
