/**
 * HypergraphEditor — The main editor component
 *
 * "The file is a lie. There is only the graph."
 * "The buffer is a lie. There is only the node."
 *
 * Layout:
 * ┌────────────────────────────────────────────────────────────────────────┐
 * │ ◀ Parent edges │ Current Node Title │ ▶ Child edges count              │
 * ├────────────────────────────────────────────────────────────────────────┤
 * │ TRAIL: node1 → node2 → current                                   [N]  │
 * ├───────┬────────────────────────────────────────────────────────┬───────┤
 * │       │                                                        │       │
 * │ Left  │              Content Pane                              │ Right │
 * │Gutter │              (Node text)                               │Gutter │
 * │       │                                                        │       │
 * ├───────┴────────────────────────────────────────────────────────┴───────┤
 * │ [MODE] | breadcrumb                                    path | 42,7     │
 * └────────────────────────────────────────────────────────────────────────┘
 */

import React, { memo, useCallback, useEffect, useRef, useState } from 'react';

import { useNavigation } from './useNavigation';
import { useKeyHandler } from './useKeyHandler';
import { StatusLine } from './StatusLine';
import { CommandLine } from './CommandLine';
import type { GraphNode, Edge, EdgeType } from './types';

import './HypergraphEditor.css';

// =============================================================================
// Types
// =============================================================================

interface HypergraphEditorProps {
  /** Initial node to focus (path) */
  initialPath?: string;

  /** Callback when node is focused */
  onNodeFocus?: (node: GraphNode) => void;

  /** Callback when navigation occurs */
  onNavigate?: (path: string) => void;

  /** External function to load a node by path */
  loadNode?: (path: string) => Promise<GraphNode | null>;

  /** External function to load siblings */
  loadSiblings?: (node: GraphNode) => Promise<GraphNode[]>;
}

// =============================================================================
// Gutter Components
// =============================================================================

interface GutterProps {
  edges: Edge[];
  side: 'left' | 'right';
  onEdgeClick?: (edge: Edge) => void;
}

const EdgeGutter = memo(function EdgeGutter({ edges, side, onEdgeClick }: GutterProps) {
  // Group edges by type
  const grouped = edges.reduce(
    (acc, edge) => {
      if (!acc[edge.type]) acc[edge.type] = [];
      acc[edge.type].push(edge);
      return acc;
    },
    {} as Record<EdgeType, Edge[]>
  );

  const types = Object.keys(grouped) as EdgeType[];

  if (types.length === 0) {
    return <div className={`edge-gutter edge-gutter--${side} edge-gutter--empty`} />;
  }

  return (
    <div className={`edge-gutter edge-gutter--${side}`}>
      {types.map((type) => {
        const typeEdges = grouped[type];
        const count = typeEdges.length;
        const abbrev = getEdgeAbbreviation(type);

        return (
          <button
            key={type}
            className="edge-gutter__badge"
            data-edge-type={type}
            onClick={() => onEdgeClick?.(typeEdges[0])}
            title={`${type}: ${count} edge${count > 1 ? 's' : ''}`}
          >
            <span className="edge-gutter__abbrev">{abbrev}</span>
            {count > 1 && <span className="edge-gutter__count">{count}</span>}
          </button>
        );
      })}
    </div>
  );
});

function getEdgeAbbreviation(type: EdgeType): string {
  const abbrevs: Record<EdgeType, string> = {
    implements: 'imp',
    tests: 'tst',
    extends: 'ext',
    derives_from: 'der',
    references: 'ref',
    contradicts: '!!!',
    contains: 'con',
    uses: 'use',
    defines: 'def',
  };
  return abbrevs[type] || type.slice(0, 3);
}

// =============================================================================
// Header Component
// =============================================================================

interface HeaderProps {
  node: GraphNode | null;
}

const Header = memo(function Header({ node }: HeaderProps) {
  if (!node) {
    return (
      <header className="hypergraph-header hypergraph-header--empty">
        <div className="hypergraph-header__title">No node focused</div>
        <div className="hypergraph-header__hint">
          Use <kbd>:e</kbd> to open a node
        </div>
      </header>
    );
  }

  const parentEdges = node.incomingEdges.filter(
    (e) => e.type === 'derives_from' || e.type === 'extends'
  );
  const childCount = node.outgoingEdges.length;

  return (
    <header className="hypergraph-header">
      {/* Parent indicator */}
      <div className="hypergraph-header__parent">
        {parentEdges.length > 0 ? (
          <>
            <span className="hypergraph-header__arrow">◀</span>
            <span className="hypergraph-header__parent-label">
              {parentEdges[0].type}: {parentEdges[0].source.split('/').pop()}
            </span>
          </>
        ) : (
          <span className="hypergraph-header__arrow hypergraph-header__arrow--dim">◀</span>
        )}
      </div>

      {/* Title */}
      <div className="hypergraph-header__title">
        {node.title || node.path.split('/').pop()}
        {node.tier && (
          <span className="hypergraph-header__tier" data-tier={node.tier}>
            {node.tier}
          </span>
        )}
      </div>

      {/* Child indicator */}
      <div className="hypergraph-header__child">
        {childCount > 0 ? (
          <>
            <span className="hypergraph-header__child-label">
              ▶ {childCount} edge{childCount > 1 ? 's' : ''}
            </span>
          </>
        ) : (
          <span className="hypergraph-header__arrow hypergraph-header__arrow--dim">▶</span>
        )}
      </div>
    </header>
  );
});

// =============================================================================
// Trail Bar Component
// =============================================================================

interface TrailBarProps {
  trail: string;
  mode: string;
}

const TrailBar = memo(function TrailBar({ trail, mode }: TrailBarProps) {
  return (
    <div className="hypergraph-trail">
      <span className="hypergraph-trail__label">TRAIL:</span>
      <span className="hypergraph-trail__path">{trail || '(root)'}</span>
      <span className="hypergraph-trail__mode">[{mode.charAt(0)}]</span>
    </div>
  );
});

// =============================================================================
// Content Pane Component
// =============================================================================

interface ContentPaneProps {
  node: GraphNode | null;
  mode: string;
  cursor: { line: number; column: number };
  onContentChange?: (content: string) => void;
}

const ContentPane = memo(function ContentPane({
  node,
  mode,
  cursor,
  onContentChange,
  onCursorChange,
}: ContentPaneProps & { onCursorChange?: (line: number, column: number) => void }) {
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const currentLineRef = useRef<HTMLDivElement>(null);
  const [localContent, setLocalContent] = useState('');
  const prevModeRef = useRef(mode);

  // Sync content when node changes
  useEffect(() => {
    if (node?.content) {
      setLocalContent(node.content);
    }
  }, [node?.content]);

  // Position textarea cursor when entering INSERT mode (only on mode change, not content change)
  useEffect(() => {
    if (mode === 'INSERT' && prevModeRef.current !== 'INSERT' && textareaRef.current) {
      textareaRef.current.focus();

      // Calculate character offset from line/column
      const lines = localContent.split('\n');
      let offset = 0;
      for (let i = 0; i < Math.min(cursor.line, lines.length); i++) {
        offset += lines[i].length + 1; // +1 for newline
      }
      offset += Math.min(cursor.column, lines[cursor.line]?.length || 0);

      textareaRef.current.setSelectionRange(offset, offset);
    }
    // Note: prevModeRef is updated in the exit effect below
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [mode]);

  // Read cursor position when exiting INSERT mode
  useEffect(() => {
    if (prevModeRef.current === 'INSERT' && mode === 'NORMAL' && textareaRef.current) {
      const textarea = textareaRef.current;
      const offset = textarea.selectionStart;
      const content = textarea.value;

      // Convert offset to line/column
      let line = 0;
      let remaining = offset;
      const lines = content.split('\n');

      for (let i = 0; i < lines.length; i++) {
        if (remaining <= lines[i].length) {
          line = i;
          break;
        }
        remaining -= lines[i].length + 1; // +1 for newline
        line = i + 1;
      }

      const column = Math.max(0, remaining);
      onCursorChange?.(line, column);
    }
    prevModeRef.current = mode;
  }, [mode, onCursorChange]);

  // Scroll current line into view when cursor moves
  useEffect(() => {
    if (currentLineRef.current && mode === 'NORMAL') {
      // Use a small delay to ensure the DOM has updated
      requestAnimationFrame(() => {
        currentLineRef.current?.scrollIntoView({
          behavior: 'smooth',
          block: 'center',
        });
      });
    }
  }, [cursor.line, mode]);

  const handleChange = useCallback(
    (e: React.ChangeEvent<HTMLTextAreaElement>) => {
      setLocalContent(e.target.value);
      onContentChange?.(e.target.value);
    },
    [onContentChange]
  );

  if (!node) {
    return (
      <div className="content-pane content-pane--empty">
        <div className="content-pane__welcome">
          <h2>Hypergraph Emacs</h2>
          <p>&quot;The file is a lie. There is only the graph.&quot;</p>
          <div className="content-pane__hints">
            <p>
              <kbd>:e &lt;path&gt;</kbd> Open a node
            </p>
            <p>
              <kbd>gh/gl</kbd> Navigate parent/child
            </p>
            <p>
              <kbd>gj/gk</kbd> Navigate siblings
            </p>
            <p>
              <kbd>gd</kbd> Go to definition
            </p>
            <p>
              <kbd>gr</kbd> Go to references
            </p>
          </div>
        </div>
      </div>
    );
  }

  // In INSERT mode, show editable textarea
  if (mode === 'INSERT') {
    return (
      <div className="content-pane content-pane--insert">
        <textarea
          ref={textareaRef}
          className="content-pane__editor"
          value={localContent}
          onChange={handleChange}
          spellCheck={false}
        />
      </div>
    );
  }

  // In NORMAL mode, show read-only content with line numbers
  const lines = (node.content || '').split('\n');

  // Clamp cursor to valid line range (handles Infinity from GOTO_END)
  const clampedLine = Math.min(cursor.line, lines.length - 1);

  return (
    <div className="content-pane content-pane--normal">
      <div className="content-pane__lines">
        {lines.map((line, i) => (
          <div
            key={i}
            ref={i === clampedLine ? currentLineRef : null}
            className={`content-pane__line ${i === clampedLine ? 'content-pane__line--current' : ''}`}
          >
            <span className="content-pane__line-number">{i + 1}</span>
            <span className="content-pane__line-content">{line || ' '}</span>
          </div>
        ))}
      </div>
    </div>
  );
});

// =============================================================================
// Main Component
// =============================================================================

export const HypergraphEditor = memo(function HypergraphEditor({
  initialPath,
  onNodeFocus,
  onNavigate,
  loadNode,
  loadSiblings,
}: HypergraphEditorProps) {
  const navigation = useNavigation();
  const { state, dispatch, focusNode, goParent, goChild, goDefinition, goReferences, goTests } =
    navigation;

  const commandLineRef = useRef<HTMLInputElement>(null);
  const [commandLineVisible, setCommandLineVisible] = useState(false);

  // Key handler
  const { pendingSequence } = useKeyHandler({
    state,
    dispatch,
    goParent,
    goChild,
    goDefinition,
    goReferences,
    goTests,
    onEnterCommand: () => {
      setCommandLineVisible(true);
      // Focus command line after state updates
      setTimeout(() => commandLineRef.current?.focus(), 0);
    },
    enabled: !commandLineVisible,
  });

  // Load initial node
  useEffect(() => {
    if (initialPath && loadNode) {
      loadNode(initialPath).then((node) => {
        if (node) {
          focusNode(node);
          onNodeFocus?.(node);
        }
      });
    }
  }, [initialPath, loadNode, focusNode, onNodeFocus]);

  // Load siblings when node changes
  useEffect(() => {
    if (state.currentNode && loadSiblings) {
      loadSiblings(state.currentNode).then((siblings) => {
        const index = siblings.findIndex((s) => s.path === state.currentNode?.path);
        dispatch({ type: 'SET_SIBLINGS', siblings, index: index >= 0 ? index : 0 });
      });
    }
  }, [state.currentNode, loadSiblings, dispatch]);

  // Handle edge click (navigate to connected node)
  const handleEdgeClick = useCallback(
    (edge: Edge) => {
      const targetPath = edge.target === state.currentNode?.path ? edge.source : edge.target;
      onNavigate?.(targetPath);

      if (loadNode) {
        loadNode(targetPath).then((node) => {
          if (node) {
            focusNode(node);
            onNodeFocus?.(node);
          }
        });
      }
    },
    [state.currentNode, onNavigate, loadNode, focusNode, onNodeFocus]
  );

  // Handle command submission
  const handleCommand = useCallback(
    (command: string) => {
      setCommandLineVisible(false);
      dispatch({ type: 'EXIT_COMMAND' });

      // Parse and execute command
      const [cmd, ...args] = command.trim().split(/\s+/);

      if (cmd === 'e' || cmd === 'edit') {
        const path = args.join(' ');
        if (path && loadNode) {
          onNavigate?.(path);
          loadNode(path).then((node) => {
            if (node) {
              focusNode(node);
              onNodeFocus?.(node);
            }
          });
        }
      } else if (cmd === 'w' || cmd === 'write') {
        // Would commit K-Block (Phase 2)
        console.log('[HypergraphEditor] :w - would commit K-Block');
      } else if (cmd === 'q' || cmd === 'quit') {
        // Would close node
        console.log('[HypergraphEditor] :q - would close node');
      }
    },
    [dispatch, loadNode, focusNode, onNavigate, onNodeFocus]
  );

  // Handle command cancel
  const handleCommandCancel = useCallback(() => {
    setCommandLineVisible(false);
    dispatch({ type: 'EXIT_COMMAND' });
  }, [dispatch]);

  // Get breadcrumb
  const breadcrumb = navigation.getTrailBreadcrumb();

  return (
    <div className="hypergraph-editor" data-mode={state.mode}>
      {/* Header */}
      <Header node={state.currentNode} />

      {/* Trail bar */}
      <TrailBar trail={breadcrumb} mode={state.mode} />

      {/* Main content area */}
      <div className="hypergraph-editor__main">
        {/* Left gutter (incoming edges) */}
        <EdgeGutter
          edges={state.currentNode?.incomingEdges || []}
          side="left"
          onEdgeClick={handleEdgeClick}
        />

        {/* Content pane */}
        <ContentPane
          node={state.currentNode}
          mode={state.mode}
          cursor={state.cursor}
          onContentChange={(content) => {
            if (state.kblock) {
              dispatch({ type: 'KBLOCK_UPDATED', content });
            }
          }}
          onCursorChange={(line, column) => {
            dispatch({ type: 'MOVE_CURSOR', position: { line, column } });
          }}
        />

        {/* Right gutter (outgoing edges) */}
        <EdgeGutter
          edges={state.currentNode?.outgoingEdges || []}
          side="right"
          onEdgeClick={handleEdgeClick}
        />
      </div>

      {/* Command line (when visible) */}
      {commandLineVisible && (
        <CommandLine ref={commandLineRef} onSubmit={handleCommand} onCancel={handleCommandCancel} />
      )}

      {/* Status line */}
      <StatusLine
        mode={state.mode}
        cursor={state.cursor}
        breadcrumb={breadcrumb}
        pendingSequence={pendingSequence}
        kblockStatus={state.kblock?.isolation}
        nodePath={state.currentNode?.path}
      />
    </div>
  );
});
