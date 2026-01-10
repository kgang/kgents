/**
 * Workspace — Three-panel IDE-like layout for kgents
 *
 * "The Hypergraph Editor IS the app. Everything else is a sidebar."
 *
 * Layout:
 * ┌────────────┬─────────────────────────┬────────────────┐
 * │            │                         │                │
 * │   FILES    │         GRAPH           │      CHAT      │
 * │   (Left)   │         (Center)        │      (Right)   │
 * │            │                         │                │
 * │  Ctrl+B    │       THE EDITOR        │     Ctrl+J     │
 * │  to toggle │       always visible    │     to toggle  │
 * │            │                         │                │
 * └────────────┴─────────────────────────┴────────────────┘
 *
 * Follows UX-LAWS.md:
 * - The App IS the Editor
 * - Graph-first Navigation
 * - Everything Must Be Real
 */

import { memo, useCallback, useEffect, useRef, useState } from 'react';
import { useSidebarState } from '../../hooks/useSidebarState';
import { HypergraphEditor } from '../../hypergraph/HypergraphEditor';
import {
  FileSidebar,
  FileTree,
  BrowseModal,
  type UploadedFile,
  type BrowseItem,
} from '../../components/browse';
import { useBrowseItems } from '../../components/browse/hooks/useBrowseItems';
import { ChatSidebar } from '../../components/chat/ChatSidebar';
import { KBlockExplorer, type KBlockExplorerItem } from '../../components/kblock-explorer';
import type { GraphNode } from '../../hypergraph/state/types';
import './Workspace.css';

// =============================================================================
// Types for Left Sidebar View
// =============================================================================

type LeftSidebarView = 'files' | 'kblocks';

// =============================================================================
// Types
// =============================================================================

export interface WorkspaceProps {
  /** Current document path (null = no file open) */
  currentPath: string | null;

  /** Recent files list */
  recentFiles: string[];

  /** Callback when a file is opened */
  onNavigate: (path: string) => void;

  /** Callback to upload a file */
  onUploadFile?: (file: UploadedFile) => Promise<void>;

  /** Callback when recent files are cleared */
  onClearRecent?: () => void;

  /** External function to load a node by path */
  loadNode?: (path: string) => Promise<GraphNode | null>;

  /** External function to load siblings */
  loadSiblings?: (node: GraphNode) => Promise<GraphNode[]>;

  /** Callback when node is focused */
  onNodeFocus?: (node: GraphNode) => void;
}

// =============================================================================
// Main Component
// =============================================================================

export const Workspace = memo(function Workspace({
  currentPath,
  recentFiles,
  onNavigate,
  onUploadFile,
  onClearRecent,
  loadNode,
  loadSiblings,
  onNodeFocus,
}: WorkspaceProps) {
  const sidebar = useSidebarState();
  const workspaceRef = useRef<HTMLDivElement>(null);
  const [chatHasUnread, setChatHasUnread] = useState(false);
  const [browseModalOpen, setBrowseModalOpen] = useState(false);
  const [leftSidebarView, setLeftSidebarView] = useState<LeftSidebarView>('kblocks');

  // Fetch K-Blocks from PostgreSQL for BrowseModal
  const {
    items: browseItems,
    loading: browseLoading,
    refresh: refreshBrowseItems,
  } = useBrowseItems();

  // ==========================================================================
  // Keyboard Shortcuts (Ctrl+B, Ctrl+J, Ctrl+O)
  // ==========================================================================

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Skip if in input/textarea (except for Ctrl+O which should work anywhere)
      const target = e.target as HTMLElement;
      const isInInput =
        target.tagName === 'INPUT' || target.tagName === 'TEXTAREA' || target.isContentEditable;

      // Ctrl+O: Open browse modal (works even in inputs)
      if (e.ctrlKey && e.key === 'o') {
        e.preventDefault();
        setBrowseModalOpen(true);
        // Refresh items when modal opens to get latest K-Blocks
        void refreshBrowseItems();
        return;
      }

      // Skip other shortcuts if in input/textarea
      if (isInInput) {
        return;
      }

      // Ctrl+B: Toggle left sidebar (Files)
      if (e.ctrlKey && e.key === 'b') {
        e.preventDefault();
        sidebar.toggleLeft();
      }

      // Ctrl+J: Toggle right sidebar (Chat)
      if (e.ctrlKey && e.key === 'j') {
        e.preventDefault();
        sidebar.toggleRight();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [sidebar, refreshBrowseItems]);

  // ==========================================================================
  // Handlers
  // ==========================================================================

  // Wrap async upload handler for FileSidebar (which expects sync)
  const handleUploadFileSync = useCallback(
    (file: UploadedFile) => {
      if (onUploadFile) {
        // Fire and forget - the hook handles loading state
        void onUploadFile(file);
      }
    },
    [onUploadFile]
  );

  // Handle selection from BrowseModal
  const handleBrowseSelect = useCallback(
    (item: BrowseItem) => {
      onNavigate(item.path);
      setBrowseModalOpen(false);
    },
    [onNavigate]
  );

  // Open browse modal from sidebar
  const handleOpenBrowseModal = useCallback(() => {
    setBrowseModalOpen(true);
    // Refresh items when modal opens to get latest K-Blocks
    void refreshBrowseItems();
  }, [refreshBrowseItems]);

  // Handle K-Block selection from explorer
  const handleKBlockSelect = useCallback(
    (item: KBlockExplorerItem) => {
      // Navigate to K-Block path (may be kblock:// URI or file path)
      onNavigate(item.path);
    },
    [onNavigate]
  );

  // ==========================================================================
  // CSS Variables for dynamic widths
  // ==========================================================================

  const workspaceStyle = {
    '--workspace-left-width': `${sidebar.state.leftWidth}px`,
    '--workspace-right-width': `${sidebar.state.rightWidth}px`,
  } as React.CSSProperties;

  // ==========================================================================
  // Render
  // ==========================================================================

  return (
    <div ref={workspaceRef} className="workspace" style={workspaceStyle}>
      {/* =================================================================
          Left Sidebar (Files/Director)
          ================================================================= */}
      <aside
        className={`workspace__left ${sidebar.state.leftOpen ? '' : 'workspace__left--collapsed'}`}
        aria-label="Files sidebar"
      >
        {/* Toggle button */}
        <button
          className="workspace__sidebar-toggle"
          onClick={sidebar.toggleLeft}
          aria-expanded={sidebar.state.leftOpen}
          aria-label={sidebar.state.leftOpen ? 'Close files sidebar' : 'Open files sidebar'}
          title={sidebar.state.leftOpen ? 'Close (Ctrl+B)' : 'Open (Ctrl+B)'}
        >
          <span className="workspace__sidebar-toggle-icon">
            {sidebar.state.leftOpen ? '◂' : '▸'}
          </span>
          <span className="workspace__sidebar-toggle-label">Files</span>
        </button>

        {/* Content */}
        <div className="workspace__sidebar-content">
          {/* Tab Switcher */}
          <div className="workspace__sidebar-tabs">
            <button
              className={`workspace__sidebar-tab ${leftSidebarView === 'kblocks' ? 'workspace__sidebar-tab--active' : ''}`}
              onClick={() => setLeftSidebarView('kblocks')}
              title="K-Block Explorer"
            >
              K-Blocks
            </button>
            <button
              className={`workspace__sidebar-tab ${leftSidebarView === 'files' ? 'workspace__sidebar-tab--active' : ''}`}
              onClick={() => setLeftSidebarView('files')}
              title="File Tree"
            >
              Files
            </button>
            <span className="workspace__sidebar-shortcut">Ctrl+B</span>
          </div>
          <div className="workspace__sidebar-body">
            {/* K-Block Explorer (default view) */}
            {leftSidebarView === 'kblocks' && (
              <KBlockExplorer onSelect={handleKBlockSelect} selectedId={currentPath ?? undefined} />
            )}
            {/* FileSidebar with FileTree for traditional file browsing */}
            {leftSidebarView === 'files' && (
              <FileSidebar
                onOpenFile={onNavigate}
                onUploadFile={handleUploadFileSync}
                recentFiles={recentFiles}
                onClearRecent={onClearRecent}
                onOpenBrowseModal={handleOpenBrowseModal}
              >
                <FileTree
                  rootPaths={['spec/', 'impl/', 'docs/']}
                  onSelectFile={onNavigate}
                  currentFile={currentPath ?? undefined}
                />
              </FileSidebar>
            )}
          </div>
        </div>
      </aside>

      {/* =================================================================
          Center Content (HypergraphEditor)
          ================================================================= */}
      <main className="workspace__center">
        {currentPath ? (
          <HypergraphEditor
            initialPath={currentPath}
            onNavigate={onNavigate}
            loadNode={loadNode}
            loadSiblings={loadSiblings}
            onNodeFocus={onNodeFocus}
          />
        ) : (
          <div className="workspace__empty-state">
            <div className="workspace__empty-state-icon">◇</div>
            <p className="workspace__empty-state-text">
              Open a file from the sidebar
              <br />
              <kbd>Ctrl+B</kbd> files • <kbd>Ctrl+O</kbd> browse all
            </p>
          </div>
        )}
      </main>

      {/* =================================================================
          Right Sidebar (Chat)
          ================================================================= */}
      <aside
        className={`workspace__right ${sidebar.state.rightOpen ? '' : 'workspace__right--collapsed'}`}
        aria-label="Chat sidebar"
      >
        {/* Toggle button */}
        <button
          className="workspace__sidebar-toggle"
          onClick={sidebar.toggleRight}
          aria-expanded={sidebar.state.rightOpen}
          aria-label={sidebar.state.rightOpen ? 'Close chat sidebar' : 'Open chat sidebar'}
          title={sidebar.state.rightOpen ? 'Close (Ctrl+J)' : 'Open (Ctrl+J)'}
        >
          {/* Unread indicator */}
          {chatHasUnread && !sidebar.state.rightOpen && (
            <span className="workspace__sidebar-unread" aria-label="Unread messages" />
          )}

          <span className="workspace__sidebar-toggle-icon">
            {sidebar.state.rightOpen ? '▸' : '◂'}
          </span>
          <span className="workspace__sidebar-toggle-label">Chat</span>
        </button>

        {/* Content */}
        <div className="workspace__sidebar-content">
          <div className="workspace__sidebar-header">
            <span className="workspace__sidebar-title">Chat</span>
            <span className="workspace__sidebar-shortcut">Ctrl+J</span>
          </div>
          <div className="workspace__sidebar-body">
            <ChatSidebar onUnreadChange={setChatHasUnread} />
          </div>
        </div>
      </aside>

      {/* =================================================================
          Browse Modal (Ctrl+O)
          ================================================================= */}
      <BrowseModal
        open={browseModalOpen}
        onClose={() => setBrowseModalOpen(false)}
        onSelectItem={handleBrowseSelect}
        items={browseItems}
        loading={browseLoading}
      />
    </div>
  );
});

export default Workspace;
