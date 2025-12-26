/**
 * StudioPage — The Garden Workspace
 *
 * "90% Steel, 10% Earned Glow"
 *
 * Three-panel layout:
 * ┌──────────┬──────────────────────────────┬───────────────┐
 * │ FEED     │    HYPERGRAPH EDITOR         │ WITNESS TRAIL │
 * │          │                              │               │
 * │ K-Blocks │    [Current Node]            │ Recent marks  │
 * │ by       │                              │               │
 * │ coherence│    vim-style editing         │ Principles    │
 * │          │    modal navigation          │ scored        │
 * │ Loss     │    portal expansion          │               │
 * │ badges   │                              │               │
 * ├──────────┼──────────────────────────────┼───────────────┤
 * │ Filters  │ [NORMAL] path.md   42,7      │ Session stats │
 * └──────────┴──────────────────────────────┴───────────────┘
 *
 * Keyboard shortcuts:
 * - Ctrl+B: Toggle feed sidebar
 * - Ctrl+J: Toggle witness trail
 * - Ctrl+\: Focus editor
 *
 * @see docs/skills/elastic-ui-patterns.md
 */

import { useState, useCallback, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Workspace } from '../constructions/Workspace';
import { Feed } from '../primitives/Feed';
import { WitnessTrailComponent, type WitnessMark } from '../primitives/Witness';
import type { KBlock } from '../primitives/Feed';
import { useFileUpload, useRecentFiles, normalizePath, isValidFilePath } from '../hypergraph';
import './StudioPage.css';

// =============================================================================
// Types
// =============================================================================

interface SessionStats {
  markCount: number;
  sessionStart: Date;
  lastActivity: Date;
}

// =============================================================================
// Component
// =============================================================================

export function StudioPage() {
  const { '*': rawPath } = useParams();
  const navigate = useNavigate();

  // Normalize and validate path
  const normalizedRawPath = rawPath ? normalizePath(rawPath) : null;
  const initialPath =
    normalizedRawPath && isValidFilePath(normalizedRawPath) ? normalizedRawPath : null;

  // Panel visibility state
  const [feedVisible, setFeedVisible] = useState(true);
  const [witnessVisible, setWitnessVisible] = useState(true);

  // Session marks
  const [sessionMarks, setSessionMarks] = useState<WitnessMark[]>([]);
  const [sessionStats, setSessionStats] = useState<SessionStats>({
    markCount: 0,
    sessionStart: new Date(),
    lastActivity: new Date(),
  });

  // File state
  const [currentPath, setCurrentPath] = useState<string | null>(initialPath);
  const { recentFiles, addRecentFile, removeRecentFile, clearRecentFiles } = useRecentFiles();

  // Refs
  const editorRef = useRef<HTMLDivElement>(null);

  // ==========================================================================
  // File Handlers
  // ==========================================================================

  const handleFileReady = useCallback(
    (path: string) => {
      const normalized = normalizePath(path);
      setCurrentPath(normalized);
      addRecentFile(normalized);
      navigate(`/world.studio/${normalized}`);
    },
    [addRecentFile, navigate]
  );

  const { loadNode: rawLoadNode, handleUploadFile } = useFileUpload({
    onFileReady: handleFileReady,
  });

  const loadNode = useCallback(
    async (path: string) => {
      try {
        const node = await rawLoadNode(path);
        if (!node) {
          console.info('[StudioPage] File not found, removing from recent:', path);
          removeRecentFile(path);
        }
        return node;
      } catch (error) {
        console.warn('[StudioPage] Load failed, removing from recent:', path, error);
        removeRecentFile(path);
        return null;
      }
    },
    [rawLoadNode, removeRecentFile]
  );

  // ==========================================================================
  // Keyboard Shortcuts (Ctrl+B, Ctrl+J, Ctrl+\)
  // ==========================================================================

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Skip if in input/textarea
      const target = e.target as HTMLElement;
      const isInInput =
        target.tagName === 'INPUT' ||
        target.tagName === 'TEXTAREA' ||
        target.isContentEditable;

      if (isInInput) {
        return;
      }

      // Ctrl+B: Toggle feed sidebar
      if (e.ctrlKey && e.key === 'b') {
        e.preventDefault();
        setFeedVisible((prev) => !prev);
      }

      // Ctrl+J: Toggle witness trail
      if (e.ctrlKey && e.key === 'j') {
        e.preventDefault();
        setWitnessVisible((prev) => !prev);
      }

      // Ctrl+\: Focus editor
      if (e.ctrlKey && e.key === '\\') {
        e.preventDefault();
        editorRef.current?.focus();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  // ==========================================================================
  // Fetch Session Marks
  // ==========================================================================

  useEffect(() => {
    const fetchMarks = async () => {
      try {
        const response = await fetch('/api/witness/marks?limit=20');
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}`);
        }
        const data = await response.json();
        const marks = (data.marks || []).map((m: any) => ({
          id: m.id || m.mark_id,
          action: m.action,
          reasoning: m.reasoning,
          principles: m.principles || [],
          author: m.author || 'system',
          timestamp: m.timestamp || m.created_at,
          parent_mark_id: m.parent_mark_id,
          automatic: m.automatic,
          metadata: m.metadata,
        }));
        setSessionMarks(marks);
        setSessionStats((prev) => ({
          ...prev,
          markCount: marks.length,
          lastActivity: new Date(),
        }));
      } catch (error) {
        console.error('[StudioPage] Failed to fetch marks:', error);
      }
    };

    fetchMarks();

    // Poll for updates every 30 seconds
    const interval = setInterval(fetchMarks, 30000);
    return () => clearInterval(interval);
  }, []);

  // ==========================================================================
  // Sync path with URL
  // ==========================================================================

  useEffect(() => {
    const normalized = rawPath ? normalizePath(rawPath) : null;
    if (normalized && isValidFilePath(normalized) && normalized !== currentPath) {
      setCurrentPath(normalized);
    } else if (!normalized && currentPath) {
      setCurrentPath(null);
    }
  }, [rawPath, currentPath]);

  // Validate path and redirect if invalid
  useEffect(() => {
    if (normalizedRawPath && !isValidFilePath(normalizedRawPath)) {
      console.warn('[StudioPage] Invalid path, redirecting:', normalizedRawPath);
      navigate('/world.studio', { replace: true });
    }
  }, [normalizedRawPath, navigate]);

  // ==========================================================================
  // Feed Item Click Handler
  // ==========================================================================

  const handleFeedItemClick = useCallback(
    (kblock: KBlock) => {
      // K-Blocks don't have metadata.source_path, so we log the click for now
      // Future: Navigate to the K-Block's detail view or editor
      console.log('[StudioPage] Feed item clicked:', kblock.title);
    },
    []
  );

  // ==========================================================================
  // Witness Mark Click Handler
  // ==========================================================================

  const handleMarkClick = useCallback(
    (mark: WitnessMark, _index: number) => {
      // Could navigate to the context of this mark
      console.log('[StudioPage] Mark clicked:', mark.action);
    },
    []
  );

  // ==========================================================================
  // Render
  // ==========================================================================

  return (
    <div className="studio-page">
      {/* Header */}
      <header className="studio-page__header">
        <h1 className="studio-page__title">K-gents Studio</h1>
        <div className="studio-page__marks-badge">{sessionStats.markCount} marks</div>
      </header>

      {/* Main Content */}
      <main className="studio-page__main">
        {/* Feed Sidebar (Left) */}
        <aside
          className={`studio-page__feed ${feedVisible ? '' : 'studio-page__feed--hidden'}`}
          aria-label="Feed sidebar"
        >
          <div className="studio-page__feed-header">
            <span className="studio-page__sidebar-title">Feed</span>
            <span className="studio-page__sidebar-shortcut">Ctrl+B</span>
          </div>
          <div className="studio-page__feed-content">
            <Feed
              feedId="coherent"
              onItemClick={handleFeedItemClick}
              initialFilters={[]}
              initialRanking="algorithmic"
              height={600}
            />
          </div>
        </aside>

        {/* Editor (Center) */}
        <section className="studio-page__editor" ref={editorRef} tabIndex={-1}>
          <Workspace
            currentPath={currentPath}
            recentFiles={recentFiles}
            onNavigate={handleFileReady}
            onUploadFile={handleUploadFile}
            onClearRecent={clearRecentFiles}
            loadNode={loadNode}
          />
        </section>

        {/* Witness Trail (Right) */}
        <aside
          className={`studio-page__witness ${witnessVisible ? '' : 'studio-page__witness--hidden'}`}
          aria-label="Witness trail sidebar"
        >
          <div className="studio-page__witness-header">
            <span className="studio-page__sidebar-title">Witness Trail</span>
            <span className="studio-page__sidebar-shortcut">Ctrl+J</span>
          </div>
          <div className="studio-page__witness-content">
            <WitnessTrailComponent
              marks={sessionMarks}
              maxVisible={10}
              orientation="vertical"
              showConnections={true}
              showPrinciples={true}
              showReasoning={false}
              onMarkClick={handleMarkClick}
            />
          </div>
          <div className="studio-page__session-stats">
            <div className="studio-page__stat">
              <span className="studio-page__stat-label">Session</span>
              <span className="studio-page__stat-value">
                {formatDuration(sessionStats.sessionStart, new Date())}
              </span>
            </div>
          </div>
        </aside>
      </main>
    </div>
  );
}

// =============================================================================
// Utility Functions
// =============================================================================

/**
 * Format duration between two dates.
 */
function formatDuration(start: Date, end: Date): string {
  const diffMs = end.getTime() - start.getTime();
  const diffMins = Math.floor(diffMs / 60000);

  if (diffMins < 1) {
    return 'Just started';
  }

  if (diffMins < 60) {
    return `${diffMins}m`;
  }

  const hours = Math.floor(diffMins / 60);
  const mins = diffMins % 60;
  return `${hours}h ${mins}m`;
}

export default StudioPage;
