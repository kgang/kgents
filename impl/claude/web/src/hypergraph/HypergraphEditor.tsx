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

import { memo, useCallback, useEffect, useRef, useState } from 'react';

import { useNavigation } from './useNavigation';
import { useKeyHandler } from './useKeyHandler';
import { useKBlock } from './useKBlock';
import { StatusLine } from './StatusLine';
import { CommandLine } from './CommandLine';
import { EdgePanel } from './EdgePanel';
import { WitnessPanel } from './WitnessPanel';
import { MarkdownEditor, MarkdownEditorRef } from '../components/editor';
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

/**
 * Calculate average confidence for a group of edges.
 * Returns undefined if no edges have confidence values.
 */
function getAverageConfidence(edges: Edge[]): number | undefined {
  const withConfidence = edges.filter((e) => e.confidence !== undefined);
  if (withConfidence.length === 0) return undefined;
  return withConfidence.reduce((sum, e) => sum + e.confidence!, 0) / withConfidence.length;
}

/**
 * Get CSS class for confidence level.
 * Maps 0-1 confidence to visual indicator.
 */
function getConfidenceClass(confidence: number | undefined): string {
  if (confidence === undefined) return 'edge-gutter__badge--unknown';
  if (confidence >= 0.8) return 'edge-gutter__badge--high';
  if (confidence >= 0.5) return 'edge-gutter__badge--medium';
  return 'edge-gutter__badge--low';
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
        const avgConfidence = getAverageConfidence(typeEdges);
        const confidenceClass = getConfidenceClass(avgConfidence);

        // Collect unique origins for tooltip
        const origins = [...new Set(typeEdges.map((e) => e.origin).filter(Boolean))];
        const hasWitness = typeEdges.some((e) => e.markId);

        // Build rich tooltip
        const tooltip = [
          `${type}: ${count} edge${count > 1 ? 's' : ''}`,
          avgConfidence !== undefined ? `Confidence: ${Math.round(avgConfidence * 100)}%` : null,
          origins.length > 0 ? `Sources: ${origins.join(', ')}` : null,
          hasWitness ? '📜 Has witness marks' : null,
        ]
          .filter(Boolean)
          .join('\n');

        return (
          <button
            key={type}
            className={`edge-gutter__badge ${confidenceClass}`}
            data-edge-type={type}
            data-has-witness={hasWitness}
            onClick={() => onEdgeClick?.(typeEdges[0])}
            title={tooltip}
          >
            <span className="edge-gutter__abbrev">{abbrev}</span>
            {count > 1 && <span className="edge-gutter__count">{count}</span>}
            {hasWitness && <span className="edge-gutter__witness">📜</span>}
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
  onCursorChange: _onCursorChange, // Reserved for future cursor sync
}: ContentPaneProps & { onCursorChange?: (line: number, column: number) => void }) {
  const editorRef = useRef<MarkdownEditorRef>(null);
  const currentLineRef = useRef<HTMLDivElement>(null);
  const [localContent, setLocalContent] = useState('');
  const prevModeRef = useRef(mode);

  // Sync content when node changes
  useEffect(() => {
    if (node?.content) {
      setLocalContent(node.content);
    }
  }, [node?.content]);

  // Focus editor when entering INSERT mode
  useEffect(() => {
    if (mode === 'INSERT' && prevModeRef.current !== 'INSERT') {
      // Small delay to ensure editor is mounted
      requestAnimationFrame(() => {
        editorRef.current?.focus();
      });
    }
    prevModeRef.current = mode;
  }, [mode]);

  // Scroll current line into view when cursor moves in NORMAL mode
  useEffect(() => {
    if (currentLineRef.current && mode === 'NORMAL') {
      requestAnimationFrame(() => {
        currentLineRef.current?.scrollIntoView({
          behavior: 'smooth',
          block: 'center',
        });
      });
    }
  }, [cursor.line, mode]);

  // Handle content changes from CodeMirror
  const handleContentChange = useCallback(
    (newContent: string) => {
      setLocalContent(newContent);
      onContentChange?.(newContent);
    },
    [onContentChange]
  );

  // Handle blur - extract cursor position when leaving INSERT mode
  const handleBlur = useCallback(() => {
    // Note: Cursor extraction from CodeMirror would need the view instance
    // For now, we'll reset to start of line when exiting INSERT mode
    // This can be enhanced later with proper cursor tracking
  }, []);

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

  // In INSERT mode, show CodeMirror editor
  if (mode === 'INSERT') {
    return (
      <div className="content-pane content-pane--insert">
        <MarkdownEditor
          ref={editorRef}
          value={localContent}
          onChange={handleContentChange}
          onBlur={handleBlur}
          vimMode={false} // Use our own modal editing, not vim's
          placeholder="Enter content..."
          fillHeight
          autoFocus
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
  const {
    state,
    dispatch,
    focusNode,
    goParent,
    goChild,
    goDefinition,
    goReferences,
    goTests,
    // Portal operations
    openPortal,
    closePortal,
    togglePortal,
    openAllPortals,
    closeAllPortals,
  } = navigation;

  // K-Block integration
  const kblockHook = useKBlock();

  const commandLineRef = useRef<HTMLInputElement>(null);
  const [commandLineVisible, setCommandLineVisible] = useState(false);
  const [witnessLoading, setWitnessLoading] = useState(false);

  // Handle INSERT mode entry - create K-Block
  const handleEnterInsert = useCallback(async () => {
    if (!state.currentNode) return;

    // Create K-Block for the current node's path
    const kblock = await kblockHook.create(state.currentNode.path);

    if (kblock) {
      // Update reducer state with K-Block info
      dispatch({ type: 'KBLOCK_CREATED', blockId: kblock.blockId, content: kblock.content });
      dispatch({ type: 'ENTER_INSERT' });
      console.info('[HypergraphEditor] Entering INSERT with K-Block:', kblock.blockId);
    } else {
      // Still enter INSERT mode but log error
      console.warn('[HypergraphEditor] K-Block creation failed, entering INSERT anyway');
      dispatch({ type: 'ENTER_INSERT' });
    }
  }, [state.currentNode, kblockHook, dispatch]);

  // Handle witness mark save
  const handleWitnessSave = useCallback(
    async (action: string, reasoning?: string, tags?: string[]) => {
      setWitnessLoading(true);
      try {
        await fetch('/api/witness/marks', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            action,
            reasoning: reasoning || null,
            principles: tags || [],
            author: 'kent',
          }),
        });
        dispatch({ type: 'EXIT_WITNESS' });
        console.info('[HypergraphEditor] Witness mark saved:', action);
      } catch (error) {
        console.error('[HypergraphEditor] Failed to save mark:', error);
      } finally {
        setWitnessLoading(false);
      }
    },
    [dispatch]
  );

  // Handle EDGE mode confirmation - create witness mark
  const handleEdgeConfirm = useCallback(async () => {
    if (!state.edgePending) return;

    const { sourceId, edgeType, targetId } = state.edgePending;

    try {
      await fetch('/api/witness/marks', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          action: `Created ${edgeType} edge: ${sourceId} → ${targetId}`,
          reasoning: null,
          principles: ['composable'],
          author: 'hypergraph-editor',
        }),
      });

      dispatch({ type: 'EDGE_CONFIRMED' });
    } catch (error) {
      console.error('[EdgeConfirm] Failed to create edge mark:', error);
      // Still exit edge mode on failure (user can retry)
      dispatch({ type: 'EDGE_CONFIRMED' });
    }
  }, [state.edgePending, dispatch]);

  // Key handler
  const { pendingSequence } = useKeyHandler({
    state,
    dispatch,
    goParent,
    goChild,
    goDefinition,
    goReferences,
    goTests,
    // Portal operations (zo/zc — vim fold-style)
    openPortal,
    closePortal,
    togglePortal,
    openAllPortals,
    closeAllPortals,
    onEnterCommand: () => {
      setCommandLineVisible(true);
      // Focus command line after state updates
      setTimeout(() => commandLineRef.current?.focus(), 0);
    },
    onEnterInsert: handleEnterInsert,
    onEdgeConfirm: handleEdgeConfirm,
    enabled: !commandLineVisible && state.mode !== 'WITNESS',
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

  // Handle witnessed :w save
  const handleWrite = useCallback(
    async (reasoning?: string) => {
      if (!kblockHook.kblock) {
        console.warn('[HypergraphEditor] :w - No K-Block to save');
        return false;
      }

      // Sync current content to hook before save
      if (state.kblock?.workingContent) {
        kblockHook.updateContent(state.kblock.workingContent);
      }

      const success = await kblockHook.save(reasoning || undefined);

      if (success) {
        // Clear reducer K-Block state
        dispatch({ type: 'KBLOCK_COMMITTED' });
        // Exit INSERT if we were in it
        if (state.mode === 'INSERT') {
          dispatch({ type: 'EXIT_INSERT' });
        }
        console.info('[HypergraphEditor] :w saved K-Block', reasoning ? `(${reasoning})` : '');
      }

      return success;
    },
    [kblockHook, state.kblock, state.mode, dispatch]
  );

  // Handle :q! discard
  const handleQuit = useCallback(
    async (force: boolean) => {
      if (kblockHook.kblock) {
        if (kblockHook.kblock.isDirty && !force) {
          console.warn('[HypergraphEditor] :q - K-Block has unsaved changes. Use :q! to force.');
          return false;
        }

        if (force) {
          await kblockHook.discard();
          dispatch({ type: 'KBLOCK_DISCARDED' });
          console.info('[HypergraphEditor] :q! - Discarded K-Block');
        }
      }

      // Exit INSERT mode if we were in it
      if (state.mode === 'INSERT') {
        dispatch({ type: 'EXIT_INSERT' });
      }

      return true;
    },
    [kblockHook, state.mode, dispatch]
  );

  // Handle command submission
  const handleCommand = useCallback(
    async (command: string) => {
      setCommandLineVisible(false);
      dispatch({ type: 'EXIT_COMMAND' });

      // Parse and execute command
      const rawCmd = command.trim();
      const [cmd, ...args] = rawCmd.split(/\s+/);

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
        // :w [message] - Save with optional witness message
        const message = args.join(' ') || undefined;
        await handleWrite(message);
      } else if (cmd === 'wq') {
        // :wq - Save and quit
        const success = await handleWrite();
        if (success) {
          await handleQuit(false);
        }
      } else if (cmd === 'q!' || rawCmd === 'q!') {
        // :q! - Force quit without saving
        await handleQuit(true);
      } else if (cmd === 'q' || cmd === 'quit') {
        // :q - Quit (warns if dirty)
        await handleQuit(false);
      } else if (cmd === 'checkpoint' || cmd === 'cp') {
        // :checkpoint [name] - Create named checkpoint
        const name = args.join(' ') || `checkpoint-${Date.now()}`;
        const cpId = await kblockHook.checkpoint(name);
        if (cpId) {
          dispatch({ type: 'KBLOCK_CHECKPOINT', id: cpId, message: name });
          console.info('[HypergraphEditor] Created checkpoint:', cpId, name);
        }
      } else if (cmd === 'rewind') {
        // :rewind <checkpoint_id> - Rewind to checkpoint
        const checkpointId = args[0];
        if (!checkpointId) {
          console.warn('[HypergraphEditor] :rewind requires checkpoint ID');
          return;
        }
        await kblockHook.rewind(checkpointId);
        console.info('[HypergraphEditor] Rewound to checkpoint:', checkpointId);
      }
    },
    [dispatch, loadNode, focusNode, onNavigate, onNodeFocus, handleWrite, handleQuit, kblockHook]
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
            // Update both reducer state and K-Block hook
            if (state.kblock) {
              dispatch({ type: 'KBLOCK_UPDATED', content });
            }
            kblockHook.updateContent(content);
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

      {/* Edge panel (when in EDGE mode) */}
      {state.mode === 'EDGE' && state.edgePending && <EdgePanel edgePending={state.edgePending} />}

      {/* Witness panel (when in WITNESS mode) */}
      {state.mode === 'WITNESS' && (
        <WitnessPanel
          onSave={handleWitnessSave}
          onCancel={() => dispatch({ type: 'EXIT_WITNESS' })}
          loading={witnessLoading}
        />
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
