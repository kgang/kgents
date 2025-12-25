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

/** Merge strategy (from spec Part IV.4) */
export type MergeStrategy = 'sequential' | 'interleave' | 'manual';

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
  useEffect(() => {
    const fetchBranches = async () => {
      try {
        setLoading(true);
        setError(null);

        // TODO: Replace with actual API call
        const response = await fetch(`/api/chat/sessions/${sessionId}/branches`);
        if (!response.ok) {
          throw new Error(`Failed to fetch branches: ${response.statusText}`);
        }

        const data = await response.json();
        setBranches(data.branches || []);

        // Find current branch
        const active = data.branches?.find((b: Branch) => b.is_active);
        if (active) {
          setCurrentBranch(active.id);
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error');
      } finally {
        setLoading(false);
      }
    };

    if (sessionId) {
      fetchBranches();
    }
  }, [sessionId]);

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

        // TODO: Replace with actual API call
        const response = await fetch(`/api/chat/${sessionId}/fork`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ branch_name: name }),
        });

        if (!response.ok) {
          throw new Error(`Fork failed: ${response.statusText}`);
        }

        const data = await response.json();
        const newBranchId = data.branch_id;

        // Refresh branches
        const branchesResponse = await fetch(`/api/chat/sessions/${sessionId}/branches`);
        const branchesData = await branchesResponse.json();
        setBranches(branchesData.branches || []);

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
    [sessionId, canFork, onBranchChange]
  );

  /**
   * Merge branch into current branch.
   *
   * Three strategies:
   * - sequential: Append branch turns after current
   * - interleave: Merge by timestamp
   * - manual: User selects turns
   *
   * TODO: Backend /merge endpoint not yet implemented.
   * This function is a placeholder for future merge functionality.
   */
  const merge = useCallback(
    async (branchId: string, strategy: MergeStrategy): Promise<void> => {
      try {
        setError(null);

        // TODO: Backend endpoint /api/chat/{session_id}/merge does not exist yet.
        // Need to implement merge endpoint in chat.py before this will work.
        const response = await fetch(`/api/chat/${currentBranch}/merge`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            source_branch_id: branchId,
            strategy,
          }),
        });

        if (!response.ok) {
          throw new Error(`Merge failed: ${response.statusText}`);
        }

        // Refresh branches
        const branchesResponse = await fetch(`/api/chat/sessions/${sessionId}/branches`);
        const branchesData = await branchesResponse.json();
        setBranches(branchesData.branches || []);
      } catch (err) {
        const message = err instanceof Error ? err.message : 'Merge failed';
        setError(message);
        throw err;
      }
    },
    [sessionId, currentBranch]
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

        // TODO: Replace with actual API call
        const response = await fetch(`/api/chat/${currentBranch}/rewind`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ turns }),
        });

        if (!response.ok) {
          throw new Error(`Rewind failed: ${response.statusText}`);
        }

        // Refresh branches to update turn counts
        const branchesResponse = await fetch(`/api/chat/sessions/${sessionId}/branches`);
        const branchesData = await branchesResponse.json();
        setBranches(branchesData.branches || []);
      } catch (err) {
        const message = err instanceof Error ? err.message : 'Rewind failed';
        setError(message);
        throw err;
      }
    },
    [sessionId, currentBranch]
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
