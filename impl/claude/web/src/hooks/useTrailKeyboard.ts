/**
 * useTrailKeyboard - Keyboard navigation for trail graph.
 *
 * Visual Trail Graph Session 3: Intelligence
 *
 * Navigation:
 * - ArrowUp: Go to parent node
 * - ArrowDown: Go to first child node
 * - ArrowLeft/Right: Navigate between siblings
 * - b: Branch from current step
 * - d/Delete: Delete current step
 * - Escape: Deselect
 *
 * @see plans/visual-trail-graph-fullstack.md Session 3
 */

import { useCallback, useEffect, useMemo } from 'react';
import type { TrailGraphNode } from '../api/trail';

// =============================================================================
// Types
// =============================================================================

export interface UseTrailKeyboardOptions {
  /** Graph nodes */
  nodes: TrailGraphNode[];
  /** Currently selected step index */
  selectedStep: number | null;
  /** Callback to select a step */
  onSelectStep: (step: number | null) => void;
  /** Callback to branch from a step */
  onBranch?: (fromStep: number) => void;
  /** Callback to delete a step */
  onDelete?: (step: number) => void;
  /** Enable/disable keyboard navigation */
  enabled?: boolean;
}

export interface UseTrailKeyboardResult {
  /** Navigate to parent */
  goToParent: () => void;
  /** Navigate to first child */
  goToChild: () => void;
  /** Navigate to previous sibling */
  goToPrevSibling: () => void;
  /** Navigate to next sibling */
  goToNextSibling: () => void;
  /** Branch from current */
  branch: () => void;
  /** Delete current */
  deleteCurrent: () => void;
  /** Deselect */
  deselect: () => void;
}

// =============================================================================
// Hook
// =============================================================================

export function useTrailKeyboard({
  nodes,
  selectedStep,
  onSelectStep,
  onBranch,
  onDelete,
  enabled = true,
}: UseTrailKeyboardOptions): UseTrailKeyboardResult {
  // Build navigation maps for efficient traversal
  const { parentMap, childrenMap, siblingMap } = useMemo(() => {
    const parentMap = new Map<number, number | null>();
    const childrenMap = new Map<number, number[]>();

    // Build parent and children maps
    nodes.forEach((node) => {
      const idx = node.data.step_index;
      const parent = node.data.parent_index ?? null;
      parentMap.set(idx, parent);

      if (parent !== null) {
        const children = childrenMap.get(parent) || [];
        children.push(idx);
        childrenMap.set(
          parent,
          children.sort((a, b) => a - b)
        );
      }
    });

    // Build sibling map for left/right navigation
    const siblingMap = new Map<number, number[]>();
    childrenMap.forEach((children) => {
      children.forEach((child) => siblingMap.set(child, children));
    });

    return { parentMap, childrenMap, siblingMap };
  }, [nodes]);

  // Navigation actions
  const goToParent = useCallback(() => {
    if (selectedStep === null) return;
    const parent = parentMap.get(selectedStep);
    if (parent !== null && parent !== undefined) {
      onSelectStep(parent);
    }
  }, [selectedStep, parentMap, onSelectStep]);

  const goToChild = useCallback(() => {
    if (selectedStep === null) return;
    const children = childrenMap.get(selectedStep);
    if (children?.length) {
      onSelectStep(children[0]);
    }
  }, [selectedStep, childrenMap, onSelectStep]);

  const goToPrevSibling = useCallback(() => {
    if (selectedStep === null) return;
    const siblings = siblingMap.get(selectedStep);
    if (siblings && siblings.length > 1) {
      const currentIdx = siblings.indexOf(selectedStep);
      const newIdx = (currentIdx - 1 + siblings.length) % siblings.length;
      onSelectStep(siblings[newIdx]);
    }
  }, [selectedStep, siblingMap, onSelectStep]);

  const goToNextSibling = useCallback(() => {
    if (selectedStep === null) return;
    const siblings = siblingMap.get(selectedStep);
    if (siblings && siblings.length > 1) {
      const currentIdx = siblings.indexOf(selectedStep);
      const newIdx = (currentIdx + 1) % siblings.length;
      onSelectStep(siblings[newIdx]);
    }
  }, [selectedStep, siblingMap, onSelectStep]);

  const branch = useCallback(() => {
    if (selectedStep !== null && onBranch) {
      onBranch(selectedStep);
    }
  }, [selectedStep, onBranch]);

  const deleteCurrent = useCallback(() => {
    if (selectedStep !== null && onDelete) {
      onDelete(selectedStep);
    }
  }, [selectedStep, onDelete]);

  const deselect = useCallback(() => {
    onSelectStep(null);
  }, [onSelectStep]);

  // Keyboard event handler
  const handleKeyDown = useCallback(
    (e: KeyboardEvent) => {
      // Skip if disabled or no selection
      if (!enabled || selectedStep === null) return;

      // Skip if in input/textarea
      if (e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement) {
        return;
      }

      switch (e.key) {
        case 'ArrowUp': {
          e.preventDefault();
          goToParent();
          break;
        }
        case 'ArrowDown': {
          e.preventDefault();
          goToChild();
          break;
        }
        case 'ArrowLeft': {
          e.preventDefault();
          goToPrevSibling();
          break;
        }
        case 'ArrowRight': {
          e.preventDefault();
          goToNextSibling();
          break;
        }
        case 'b': {
          if (!e.metaKey && !e.ctrlKey) {
            branch();
          }
          break;
        }
        case 'd':
        case 'Delete': {
          if (!e.metaKey && !e.ctrlKey) {
            deleteCurrent();
          }
          break;
        }
        case 'Escape': {
          deselect();
          break;
        }
      }
    },
    [
      enabled,
      selectedStep,
      goToParent,
      goToChild,
      goToPrevSibling,
      goToNextSibling,
      branch,
      deleteCurrent,
      deselect,
    ]
  );

  // Register keyboard listener
  useEffect(() => {
    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [handleKeyDown]);

  return {
    goToParent,
    goToChild,
    goToPrevSibling,
    goToNextSibling,
    branch,
    deleteCurrent,
    deselect,
  };
}

export default useTrailKeyboard;
