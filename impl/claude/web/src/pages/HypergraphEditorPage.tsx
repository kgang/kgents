/**
 * HypergraphEditorPage — Demo/test page for Hypergraph Emacs
 *
 * "The file is a lie. There is only the graph."
 *
 * URL Parameters:
 * - ?path=<spec-path> — Open directly to this path
 * - ?memory=<crystal-id> — Context from Brain (future)
 */

import { useCallback, useEffect, useRef, useState } from 'react';
import { useSearchParams } from 'react-router-dom';

import { HypergraphEditor, FileExplorer, useGraphNode, normalizePath } from '../hypergraph';
import type { GraphNode, UploadedFile } from '../hypergraph';
import { sovereignApi } from '../api/client';

import './HypergraphEditorPage.css';

export function HypergraphEditorPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const graphNode = useGraphNode();

  // Get initial path from URL (no default - show FileExplorer if none)
  const rawPath = searchParams.get('path');
  const initialPath = rawPath ? normalizePath(rawPath) : null;
  // Future: const memoryContext = searchParams.get('memory'); // Show relevant Brain context

  const [currentPath, setCurrentPath] = useState<string | null>(initialPath);
  const [focusedNode, setFocusedNode] = useState<GraphNode | null>(null);

  // Local file cache for uploaded files
  const localFilesRef = useRef<Map<string, GraphNode>>(new Map());

  // Update path when URL changes
  useEffect(() => {
    const urlPath = searchParams.get('path');
    if (urlPath) {
      const normalized = normalizePath(urlPath);
      if (normalized !== currentPath) {
        setCurrentPath(normalized);
      }
    } else {
      // No path in URL - reset to file explorer
      setCurrentPath(null);
    }
  }, [searchParams, currentPath]);

  // Handle opening a file from FileExplorer
  const handleOpenFile = useCallback(
    (path: string) => {
      const normalized = normalizePath(path);
      setCurrentPath(normalized);
      setSearchParams({ path: normalized });
    },
    [setSearchParams]
  );

  // Handle file upload - ingest into sovereign store
  const handleUploadFile = useCallback(
    async (file: UploadedFile) => {
      console.info(
        '[HypergraphEditor] File uploaded:',
        file.name,
        `(${file.content.length} bytes)`
      );

      try {
        // Ingest into sovereign store via AGENTESE
        // This creates a witnessed, versioned copy with edge extraction
        const ingestResult = await sovereignApi.ingest({
          path: `uploads/${file.name}`, // Prefix with 'uploads/' namespace
          content: file.content,
          source: 'file-upload',
        });

        console.info(
          '[HypergraphEditor] Ingested to sovereign store:',
          ingestResult.path,
          `v${ingestResult.version}`,
          `(${ingestResult.edge_count} edges, mark: ${ingestResult.ingest_mark_id})`
        );

        // Store in local cache so content is available for rendering
        // (graphNode.loadNode doesn't fetch content - it comes via K-Block)
        const ext = file.name.split('.').pop()?.toLowerCase() || '';
        const kind: GraphNode['kind'] =
          ext === 'md'
            ? 'doc'
            : ext === 'py' || ext === 'ts' || ext === 'tsx'
              ? 'implementation'
              : 'unknown';

        const localNode: GraphNode = {
          path: ingestResult.path,
          title: file.name.replace(/\.[^.]+$/, ''),
          kind,
          confidence: 1.0,
          content: file.content,
          outgoingEdges: [],
          incomingEdges: [],
        };

        localFilesRef.current.set(ingestResult.path, localNode);

        // Navigate to the ingested file
        handleOpenFile(ingestResult.path);
      } catch (err) {
        console.error('[HypergraphEditor] Failed to ingest file:', err);

        // Fallback: store locally in cache if ingest fails
        // This ensures the UI remains usable even if backend is down
        const ext = file.name.split('.').pop()?.toLowerCase() || '';
        const kind: GraphNode['kind'] =
          ext === 'md'
            ? 'doc'
            : ext === 'py' || ext === 'ts' || ext === 'tsx'
              ? 'implementation'
              : 'unknown';

        const localNode: GraphNode = {
          path: `uploads/${file.name}`,
          title: file.name.replace(/\.[^.]+$/, ''),
          kind,
          confidence: 1.0,
          content: file.content,
          outgoingEdges: [],
          incomingEdges: [],
        };

        localFilesRef.current.set(`uploads/${file.name}`, localNode);
        handleOpenFile(`uploads/${file.name}`);
      }
    },
    [handleOpenFile]
  );

  // Custom loadNode that checks local cache first
  const loadNode = useCallback(
    async (path: string): Promise<GraphNode | null> => {
      // Check local cache first (for uploaded files)
      const localNode = localFilesRef.current.get(path);
      if (localNode) {
        console.info('[HypergraphEditor] Loading from local cache:', path);
        return localNode;
      }

      // Fall back to API
      return graphNode.loadNode(path);
    },
    [graphNode.loadNode]
  );

  const handleNodeFocus = useCallback((node: GraphNode) => {
    setFocusedNode(node);
    setCurrentPath(node.path);
  }, []);

  const handleNavigate = useCallback(
    (path: string) => {
      const normalized = normalizePath(path);
      setCurrentPath(normalized);
      setSearchParams({ path: normalized });
    },
    [setSearchParams]
  );

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
            value={currentPath || ''}
            onChange={(e) => setCurrentPath(e.target.value || null)}
            placeholder="No file selected"
            className="hypergraph-editor-page__input"
          />
          {currentPath && (
            <button
              className="hypergraph-editor-page__back-btn"
              onClick={() => {
                setCurrentPath(null);
                setSearchParams({});
              }}
            >
              Back to Explorer
            </button>
          )}
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

      {/* Main editor or file explorer */}
      <main className="hypergraph-editor-page__main">
        {currentPath ? (
          <HypergraphEditor
            initialPath={currentPath}
            onNodeFocus={handleNodeFocus}
            onNavigate={handleNavigate}
            loadNode={loadNode}
            loadSiblings={graphNode.loadSiblings}
          />
        ) : (
          <FileExplorer
            onOpenFile={handleOpenFile}
            onUploadFile={handleUploadFile}
            uploadEnabled={true}
          />
        )}
      </main>
    </div>
  );
}
