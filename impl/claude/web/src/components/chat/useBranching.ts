/**
 * Branching Hook
 *
 * Manages chat session branching operations: fork, merge, switch, rewind.
 * Follows chat-web spec Part X.2 and Part IV (Multi-Session Architecture).
 *
 * MAX_BRANCHES = 3 (cognitive limit)
 *
 * @see spec/protocols/chat-web.md §4.2, §4.4
 */

import { useState, useEffect, useCallback } from 'react';
import { chatApi } from '@/api/chatApi';
import type { MergeStrategy } from '@/types/chat';

/** Branch node in session tree */
export interface Branch {
  id: string;
  parent_id: string | null;
  fork_point: number; // Turn number where fork occurred
  branch_name: string;
  turn_count: number;
  created_at: string;
  last_active: string;
  is_merged: boolean;
  merged_into: string | null;
  is_active: boolean; // Current branch
}

/** Branch tree structure for visualization */
export interface BranchTreeNode {
  branch: Branch;
  children: BranchTreeNode[];
}

export interface UseBranchingResult {
  /** All branches in session */
  branches: Branch[];
  /** Current active branch ID */
  currentBranch: string;
  /** Can create new fork (under MAX_BRANCHES limit) */
  canFork: boolean;
  /** Fork current branch */
  fork: (name: string) => Promise<string>;
  /** Merge branch into current */
  merge: (branchId: string, strategy: MergeStrategy) => Promise<void>;
  /** Switch to different branch */
  switchBranch: (branchId: string) => void;
  /** Rewind current branch by N turns */
  rewind: (turns: number) => void;
  /** Branch tree for visualization */
  tree: BranchTreeNode | null;
  /** Loading state */
  loading: boolean;
  /** Error state */
  error: string | null;
}

export { MergeStrategy };

const MAX_BRANCHES = 3; // From spec §4.2

/**
 * Hook for branch operations.
 *
 * @param sessionId - Chat session ID
 * @param onBranchChange - Callback when branch changes
 *
 * @example
 * ```tsx
 * const { branches, canFork, fork, currentBranch } = useBranching(sessionId);
 *
 * const handleFork = async () => {
 *   if (!canFork) {
 *     toast.error('Maximum 3 branches reached');
 *     return;
 *   }
 *   await fork('explore-alternative');
 * };
 * ```
 */
export function useBranching(
  sessionId: string,
  onBranchChange?: (branchId: string) => void
): UseBranchingResult {
  const [branches, setBranches] = useState<Branch[]>([]);
  const [currentBranch, setCurrentBranch] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Fetch branches on mount and when session changes
  const fetchBranches = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      // Fetch branches via API
      const data = await chatApi.getBranches(sessionId);
      setBranches(data.branches || []);

      // Find current branch
      const active = data.branches?.find((b) => b.is_active);
      if (active) {
        setCurrentBranch(active.id);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  }, [sessionId]);

  useEffect(() => {
    if (sessionId) {
      fetchBranches();
    }
  }, [sessionId, fetchBranches]);

  // Build tree structure from flat branch list
  const tree = useBuildBranchTree(branches);

  // Count active (non-merged) branches
  const activeBranches = branches.filter((b) => !b.is_merged);
  const canFork = activeBranches.length < MAX_BRANCHES;

  /**
   * Fork current branch.
   *
   * Creates new branch at current turn with given name.
   * Auto-generates name if not provided.
   */
  const fork = useCallback(
    async (name: string): Promise<string> => {
      if (!canFork) {
        throw new Error(`Cannot fork: maximum ${MAX_BRANCHES} branches reached`);
      }

      try {
        setError(null);

        // Call fork API
        const result = await chatApi.fork(sessionId, {
          branch_name: name,
        });

        const newBranchId = result.session_id;

        // Refresh branches
        await fetchBranches();

        // Switch to new branch
        setCurrentBranch(newBranchId);
        onBranchChange?.(newBranchId);

        return newBranchId;
      } catch (err) {
        const message = err instanceof Error ? err.message : 'Fork failed';
        setError(message);
        throw err;
      }
    },
    [sessionId, canFork, onBranchChange, fetchBranches]
  );

  /**
   * Merge branch into current branch.
   *
   * Three strategies:
   * - sequential: Append branch turns after current
   * - interleave: Merge by timestamp
   * - manual: User selects turns
   */
  const merge = useCallback(
    async (branchId: string, strategy: MergeStrategy): Promise<void> => {
      try {
        setError(null);

        // Call merge API
        await chatApi.merge(currentBranch, {
          other_id: branchId,
          strategy,
        });

        // Refresh branches to reflect merge state
        await fetchBranches();
      } catch (err) {
        const message = err instanceof Error ? err.message : 'Merge failed';
        setError(message);
        throw err;
      }
    },
    [currentBranch, fetchBranches]
  );

  /**
   * Switch to different branch.
   *
   * Loads branch state and updates current.
   */
  const switchBranch = useCallback(
    (branchId: string) => {
      const branch = branches.find((b) => b.id === branchId);
      if (!branch) {
        setError(`Branch ${branchId} not found`);
        return;
      }

      setCurrentBranch(branchId);
      onBranchChange?.(branchId);
    },
    [branches, onBranchChange]
  );

  /**
   * Rewind current branch by N turns.
   *
   * Uses K-Block rewind operation.
   */
  const rewind = useCallback(
    async (turns: number) => {
      try {
        setError(null);

        // Call rewind API
        await chatApi.rewind(currentBranch, { turns });

        // Refresh branches to update turn counts
        await fetchBranches();
      } catch (err) {
        const message = err instanceof Error ? err.message : 'Rewind failed';
        setError(message);
        throw err;
      }
    },
    [currentBranch, fetchBranches]
  );

  return {
    branches,
    currentBranch,
    canFork,
    fork,
    merge,
    switchBranch,
    rewind,
    tree,
    loading,
    error,
  };
}

/**
 * Build hierarchical tree from flat branch list.
 *
 * Used for tree visualization.
 */
function useBuildBranchTree(branches: Branch[]): BranchTreeNode | null {
  return useMemo(() => {
    if (branches.length === 0) return null;

    // Find root (no parent)
    const root = branches.find((b) => b.parent_id === null);
    if (!root) return null;

    const buildNode = (branch: Branch): BranchTreeNode => {
      const children = branches.filter((b) => b.parent_id === branch.id);
      return {
        branch,
        children: children.map(buildNode),
      };
    };

    return buildNode(root);
  }, [branches]);
}

// Minimal useMemo polyfill for the tree builder
function useMemo<T>(factory: () => T, deps: unknown[]): T {
  const [state, setState] = useState<T>(factory);

  useEffect(() => {
    setState(factory());
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps);

  return state;
}

export default useBranching;
