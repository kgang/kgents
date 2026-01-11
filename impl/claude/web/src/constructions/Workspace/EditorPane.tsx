/**
 * EditorPane — The center content area that subscribes to navigation state
 *
 * "Only the editor should re-render when the path changes."
 *
 * This component is the ONLY part of the Workspace that subscribes to navigation
 * state changes via useNavigationPath(). When a user clicks a K-Block in the
 * sidebar, only this component re-renders - the sidebars remain stable.
 *
 * Architecture:
 * - Uses useNavigationPath() to subscribe to path changes
 * - Uses useNavigateInternal() for edge clicks (doesn't trigger sidebar re-renders)
 * - Renders HypergraphEditor when a path is selected
 * - Shows empty state when no path is selected
 */

import { memo, useCallback } from 'react';
import { useNavigationPath, useNavigateInternal } from '../../hooks/useNavigationState';
import { useFileUpload } from '../../hypergraph/useFileUpload';
import { HypergraphEditor } from '../../hypergraph/HypergraphEditor';
import type { GraphNode } from '../../hypergraph/state/types';

export const EditorPane = memo(function EditorPane() {
  // Subscribe to navigation state - this component re-renders on path change
  const currentPath = useNavigationPath();
  const navigateInternal = useNavigateInternal();

  // File upload hook for loading nodes
  const { loadNode: rawLoadNode } = useFileUpload({});

  // Wrap loadNode to handle errors
  const loadNode = useCallback(
    async (path: string): Promise<GraphNode | null> => {
      try {
        const node = await rawLoadNode(path);
        return node;
      } catch (error) {
        console.warn('[EditorPane] Load failed:', path, error);
        return null;
      }
    },
    [rawLoadNode]
  );

  // Handle editor navigation (edge clicks, etc.)
  // Uses navigateInternal to update URL without triggering full re-render
  const handleEditorNavigate = useCallback(
    (path: string) => {
      navigateInternal(path);
    },
    [navigateInternal]
  );

  // Handle node focus events
  const handleNodeFocus = useCallback((node: GraphNode) => {
    console.info('[EditorPane] Node focused:', node.path);
  }, []);

  if (!currentPath) {
    return (
      <div className="workspace__empty-state">
        <div className="workspace__empty-state-icon">◇</div>
        <p className="workspace__empty-state-text">
          Open a file from the sidebar
          <br />
          <kbd>Ctrl+B</kbd> files • <kbd>Ctrl+O</kbd> browse all
        </p>
      </div>
    );
  }

  return (
    <HypergraphEditor
      initialPath={currentPath}
      onNavigate={handleEditorNavigate}
      loadNode={loadNode}
      onNodeFocus={handleNodeFocus}
    />
  );
});
