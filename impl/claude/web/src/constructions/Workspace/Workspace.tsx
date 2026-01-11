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
 *
 * Re-render Isolation (2025-01-10):
 * - Workspace no longer receives currentPath as a prop
 * - Sidebars use useNavigate() for dispatch (no subscription to state)
 * - Only EditorPane subscribes to navigation state via useNavigationPath()
 * - This prevents sidebar re-renders when navigating between K-Blocks
 */

import {
  memo,
  useCallback,
  useEffect,
  useRef,
  useState,
  type MouseEvent as ReactMouseEvent,
} from 'react';
import { useSidebarState } from '../../hooks/useSidebarState';
import {
  useNavigate,
  useNavigateInternal,
  useRecentFiles,
  useRecentFilesActions,
} from '../../hooks/useNavigationState';
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
import { Feed, type KBlock, type FeedFilter } from '../../primitives/Feed';
import { EditorPane } from './EditorPane';
import './Workspace.css';

// Stable empty array reference to prevent Feed re-renders
const EMPTY_FILTERS: FeedFilter[] = [];

// =============================================================================
// Types for Left Sidebar View
// =============================================================================

type LeftSidebarView = 'files' | 'kblocks' | 'feed';

// =============================================================================
// Types
// =============================================================================

export interface WorkspaceProps {
  /** Callback to upload a file */
  onUploadFile?: (file: UploadedFile) => Promise<void>;
}

// =============================================================================
// Main Component
// =============================================================================

export const Workspace = memo(function Workspace({ onUploadFile }: WorkspaceProps) {
  const sidebar = useSidebarState();
  const workspaceRef = useRef<HTMLDivElement>(null);
  const [chatHasUnread, setChatHasUnread] = useState(false);
  const [browseModalOpen, setBrowseModalOpen] = useState(false);
  const [leftSidebarView, setLeftSidebarView] = useState<LeftSidebarView>('kblocks');
  const [isDragging, setIsDragging] = useState<'left' | 'right' | null>(null);

  // Navigation hooks from context (these don't cause re-renders on path change)
  const navigate = useNavigate();
  const navigateInternal = useNavigateInternal();
  const recentFiles = useRecentFiles();
  const { clearRecent } = useRecentFilesActions();

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
  // Resize Handlers
  // ==========================================================================

  const handleResizeStart = useCallback(
    (side: 'left' | 'right') => (e: ReactMouseEvent) => {
      e.preventDefault();
      setIsDragging(side);
    },
    []
  );

  useEffect(() => {
    if (!isDragging) return;

    const handleMouseMove = (e: MouseEvent) => {
      if (isDragging === 'left') {
        const newWidth = Math.max(200, Math.min(500, e.clientX));
        sidebar.setLeftWidth(newWidth);
      } else if (isDragging === 'right') {
        const newWidth = Math.max(200, Math.min(500, window.innerWidth - e.clientX));
        sidebar.setRightWidth(newWidth);
      }
    };

    const handleMouseUp = () => {
      setIsDragging(null);
    };

    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseup', handleMouseUp);

    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };
  }, [isDragging, sidebar]);

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
      navigate(item.path);
      setBrowseModalOpen(false);
    },
    [navigate]
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
      // Navigate to K-Block path (kblock/{id} format)
      navigate(item.path);
    },
    [navigate]
  );

  // Stable callback for Feed item clicks to prevent re-renders
  const handleFeedItemClick = useCallback((kblock: KBlock) => {
    console.log('[Workspace] Feed item clicked:', kblock.title);
  }, []);

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

        {/* Resize handle */}
        {sidebar.state.leftOpen && (
          <div
            className={`workspace__resize-handle ${isDragging === 'left' ? 'workspace__resize-handle--active' : ''}`}
            onMouseDown={handleResizeStart('left')}
          />
        )}

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
            <button
              className={`workspace__sidebar-tab ${leftSidebarView === 'feed' ? 'workspace__sidebar-tab--active' : ''}`}
              onClick={() => setLeftSidebarView('feed')}
              title="Activity Feed"
            >
              Feed
            </button>
            <span className="workspace__sidebar-shortcut">Ctrl+B</span>
          </div>
          <div className="workspace__sidebar-body">
            {/* K-Block Explorer (default view) */}
            {leftSidebarView === 'kblocks' && <KBlockExplorer onSelect={handleKBlockSelect} />}
            {/* FileSidebar with FileTree for traditional file browsing */}
            {leftSidebarView === 'files' && (
              <FileSidebar
                onOpenFile={navigate}
                onUploadFile={handleUploadFileSync}
                recentFiles={recentFiles}
                onClearRecent={clearRecent}
                onOpenBrowseModal={handleOpenBrowseModal}
              >
                <FileTree rootPaths={['spec/', 'impl/', 'docs/']} onSelectFile={navigate} />
              </FileSidebar>
            )}
            {/* Feed view for activity stream */}
            {leftSidebarView === 'feed' && (
              <Feed
                feedId="coherent"
                onItemClick={handleFeedItemClick}
                initialFilters={EMPTY_FILTERS}
                initialRanking="algorithmic"
                height={600}
              />
            )}
          </div>
        </div>
      </aside>

      {/* =================================================================
          Center Content (EditorPane - subscribes to navigation state)
          ================================================================= */}
      <main className="workspace__center">
        <EditorPane />
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

        {/* Resize handle */}
        {sidebar.state.rightOpen && (
          <div
            className={`workspace__resize-handle ${isDragging === 'right' ? 'workspace__resize-handle--active' : ''}`}
            onMouseDown={handleResizeStart('right')}
          />
        )}

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
