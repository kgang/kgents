/**
 * HypergraphEditorPage — Demo/test page for Hypergraph Emacs
 *
 * "The file is a lie. There is only the graph."
 *
 * URL Parameters:
 * - ?path=<spec-path> — Open directly to this path
 * - ?memory=<crystal-id> — Context from Brain (future)
 */

import { useCallback, useEffect, useState } from 'react';
import { useSearchParams } from 'react-router-dom';

import { HypergraphEditor, useGraphNode, normalizePath } from '../hypergraph';
import type { GraphNode } from '../hypergraph';

import './HypergraphEditorPage.css';

export function HypergraphEditorPage() {
  const [searchParams] = useSearchParams();
  const graphNode = useGraphNode();

  // Get initial path from URL or use default, normalizing to strip repo prefix if present
  const rawPath = searchParams.get('path') || 'spec/protocols/k-block.md';
  const initialPath = normalizePath(rawPath);
  // Future: const memoryContext = searchParams.get('memory'); // Show relevant Brain context

  const [currentPath, setCurrentPath] = useState<string>(initialPath);
  const [focusedNode, setFocusedNode] = useState<GraphNode | null>(null);

  // Update path when URL changes
  useEffect(() => {
    const urlPath = searchParams.get('path');
    if (urlPath) {
      const normalized = normalizePath(urlPath);
      if (normalized !== currentPath) {
        setCurrentPath(normalized);
      }
    }
  }, [searchParams, currentPath]);

  const handleNodeFocus = useCallback((node: GraphNode) => {
    setFocusedNode(node);
    setCurrentPath(node.path);
  }, []);

  const handleNavigate = useCallback((path: string) => {
    setCurrentPath(path);
  }, []);

  return (
    <div className="hypergraph-editor-page">
      {/* Debug panel */}
      <aside className="hypergraph-editor-page__debug">
        <h3>Hypergraph Emacs — Phase 1</h3>
        <p>Core Navigation Test</p>

        <div className="hypergraph-editor-page__section">
          <h4>Current Path</h4>
          <input
            type="text"
            value={currentPath}
            onChange={(e) => setCurrentPath(e.target.value)}
            className="hypergraph-editor-page__input"
          />
        </div>

        {focusedNode && (
          <div className="hypergraph-editor-page__section">
            <h4>Focused Node</h4>
            <pre className="hypergraph-editor-page__json">
              {JSON.stringify(
                {
                  path: focusedNode.path,
                  title: focusedNode.title,
                  tier: focusedNode.tier,
                  kind: focusedNode.kind,
                  outgoing: focusedNode.outgoingEdges.length,
                  incoming: focusedNode.incomingEdges.length,
                },
                null,
                2
              )}
            </pre>
          </div>
        )}

        <div className="hypergraph-editor-page__section">
          <h4>Keybindings</h4>
          <ul className="hypergraph-editor-page__keys">
            <li>
              <kbd>j/k</kbd> Move line down/up
            </li>
            <li>
              <kbd>h/l</kbd> Move column left/right
            </li>
            <li>
              <kbd>gg</kbd> Go to start
            </li>
            <li>
              <kbd>G</kbd> Go to end
            </li>
            <li>
              <kbd>gh</kbd> Go to parent
            </li>
            <li>
              <kbd>gl</kbd> Go to child
            </li>
            <li>
              <kbd>gj/gk</kbd> Next/prev sibling
            </li>
            <li>
              <kbd>gd</kbd> Go to definition
            </li>
            <li>
              <kbd>gr</kbd> Go to references
            </li>
            <li>
              <kbd>gt</kbd> Go to tests
            </li>
            <li>
              <kbd>ge</kbd> Enter edge mode
            </li>
            <li>
              <kbd>gw</kbd> Enter witness mode
            </li>
            <li>
              <kbd>i</kbd> Enter insert mode
            </li>
            <li>
              <kbd>:</kbd> Command mode
            </li>
            <li>
              <kbd>Esc</kbd> Return to normal
            </li>
            <li>
              <kbd>Ctrl+o</kbd> Go back
            </li>
          </ul>
        </div>

        <div className="hypergraph-editor-page__section">
          <h4>Commands</h4>
          <ul className="hypergraph-editor-page__keys">
            <li>
              <kbd>:e &lt;path&gt;</kbd> Open node
            </li>
            <li>
              <kbd>:w</kbd> Write (commit)
            </li>
            <li>
              <kbd>:q</kbd> Quit
            </li>
          </ul>
        </div>

        {graphNode.error && (
          <div className="hypergraph-editor-page__error">Error: {graphNode.error}</div>
        )}
      </aside>

      {/* Main editor */}
      <main className="hypergraph-editor-page__main">
        <HypergraphEditor
          initialPath={currentPath}
          onNodeFocus={handleNodeFocus}
          onNavigate={handleNavigate}
          loadNode={graphNode.loadNode}
          loadSiblings={graphNode.loadSiblings}
        />
      </main>
    </div>
  );
}
