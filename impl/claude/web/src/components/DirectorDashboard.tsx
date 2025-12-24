/**
 * DirectorDashboard — Documents (Living Document Canvas)
 *
 * A radical, calm power-user interface for document lifecycle management.
 *
 * Philosophy:
 *   "The canvas breathes. Documents arrive, analyze, become ready."
 *   "90% steel, 10% earned glow"
 *   "Functional by construction, not decoration"
 *
 * Layout: Three-column master-detail with keyboard-first navigation
 *   [Sidebar: Stats & Filters] | [Main: Document List] | [Detail: Selected Doc]
 *
 * No "Scan Corpus" button. Auto-analyze on upload. SSE real-time updates.
 */

import { useCallback, useEffect, useMemo, useRef, useState } from 'react';

import {
  listDocuments,
  getMetrics,
  getRefCount,
  deleteDocument,
  renameDocument,
  type DocumentEntry,
  type DocumentStatus,
  type MetricsSummary,
} from '../api/director';
import { useWitnessStream } from '../hooks/useWitnessStream';
import { DirectorSidebar, type StatusFilter } from './DirectorSidebar';

import './DirectorDashboard.css';

// =============================================================================
// Types
// =============================================================================

type SortField = 'path' | 'status' | 'claims' | 'analyzed_at';
type SortDir = 'asc' | 'desc';

export interface DirectorDashboardProps {
  onSelectDocument?: (path: string) => void;
  onUpload?: () => void;
  onNavigateToDocuments?: () => void;
}

// Status configuration for visual consistency
const STATUS_CONFIG: Record<
  DocumentStatus | 'all',
  { label: string; key: string; accent?: string }
> = {
  all: { label: 'All', key: 'a' },
  uploaded: { label: 'Uploaded', key: 'u', accent: 'var(--status-normal)' },
  processing: { label: 'Processing', key: 'p', accent: 'var(--status-edge)' },
  ready: { label: 'Ready', key: 'r', accent: 'var(--status-insert)' },
  executed: { label: 'Executed', key: 'x', accent: 'var(--status-visual)' },
  stale: { label: 'Stale', key: 's', accent: 'var(--steel-500)' },
  failed: { label: 'Failed', key: 'f', accent: 'var(--status-error)' },
};

// =============================================================================
// Component
// =============================================================================

export function DirectorDashboard({ onSelectDocument, onUpload }: DirectorDashboardProps) {
  // Data state
  const [documents, setDocuments] = useState<DocumentEntry[]>([]);
  const [metrics, setMetrics] = useState<MetricsSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // UI state
  const [statusFilter, setStatusFilter] = useState<StatusFilter>('all');
  const [sortField, setSortField] = useState<SortField>('analyzed_at');
  const [sortDir, setSortDir] = useState<SortDir>('desc');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedIndex, setSelectedIndex] = useState(0);
  // Future: enable pane focus switching with Tab
  // const [focusedPane, setFocusedPane] = useState<'list' | 'detail'>('list');

  // Delete/Rename state
  const [deleteConfirm, setDeleteConfirm] = useState<string | null>(null);
  const [renameMode, setRenameMode] = useState<string | null>(null);
  const [renameValue, setRenameValue] = useState('');

  // Refs
  const containerRef = useRef<HTMLDivElement>(null);
  const listRef = useRef<HTMLDivElement>(null);
  const searchRef = useRef<HTMLInputElement>(null);
  const lastEventRef = useRef<string | null>(null);

  // Real-time stream
  const { events: witnessEvents, connected: streamConnected } = useWitnessStream();

  // ==========================================================================
  // Data Loading
  // ==========================================================================

  const loadData = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const [docsResponse, metricsData] = await Promise.all([
        listDocuments({
          status: statusFilter === 'all' ? undefined : statusFilter,
          limit: 200,
          offset: 0,
        }),
        getMetrics(),
      ]);

      setDocuments(docsResponse.documents);
      setMetrics(metricsData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load documents');
    } finally {
      setLoading(false);
    }
  }, [statusFilter]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  // SSE listener for real-time updates
  useEffect(() => {
    const directorEvents = witnessEvents.filter(
      (e) =>
        e.action?.startsWith('document.') ||
        e.tags?.some((t) => t.startsWith('director.') || t === 'ingest' || t === 'analysis')
    );

    const latest = directorEvents[0];
    if (!latest) return;

    const eventKey = `${latest.id}-${latest.timestamp}`;
    if (eventKey !== lastEventRef.current && !loading) {
      lastEventRef.current = eventKey;
      loadData();
    }
  }, [witnessEvents, loading, loadData]);

  // ==========================================================================
  // Filtering & Sorting
  // ==========================================================================

  const filteredDocuments = useMemo(() => {
    let result = [...documents];

    // Search filter
    if (searchQuery) {
      const q = searchQuery.toLowerCase();
      result = result.filter(
        (doc) =>
          doc.path.toLowerCase().includes(q) || doc.title.toLowerCase().includes(q)
      );
    }

    // Sort
    result.sort((a, b) => {
      let cmp = 0;
      switch (sortField) {
        case 'path':
          cmp = a.path.localeCompare(b.path);
          break;
        case 'status':
          cmp = a.status.localeCompare(b.status);
          break;
        case 'claims':
          cmp = (a.claim_count ?? 0) - (b.claim_count ?? 0);
          break;
        case 'analyzed_at': {
          const at = a.analyzed_at ? new Date(a.analyzed_at).getTime() : 0;
          const bt = b.analyzed_at ? new Date(b.analyzed_at).getTime() : 0;
          cmp = at - bt;
          break;
        }
      }
      return sortDir === 'asc' ? cmp : -cmp;
    });

    return result;
  }, [documents, searchQuery, sortField, sortDir]);

  const selectedDoc = filteredDocuments[selectedIndex] || null;

  // ==========================================================================
  // Document Actions
  // ==========================================================================

  const handleDelete = useCallback(async (path: string) => {
    try {
      await deleteDocument(path);
      setDeleteConfirm(null);
      await loadData();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete document');
    }
  }, [loadData]);

  const handleRename = useCallback(async (oldPath: string, newPath: string) => {
    try {
      await renameDocument(oldPath, newPath);
      setRenameMode(null);
      setRenameValue('');
      await loadData();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to rename document');
    }
  }, [loadData]);

  // ==========================================================================
  // Keyboard Navigation (Vim-inspired)
  // ==========================================================================

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Ignore if typing in search or rename input
      if (e.target === searchRef.current || renameMode) {
        if (e.key === 'Escape') {
          searchRef.current?.blur();
          setSearchQuery('');
          setRenameMode(null);
          setRenameValue('');
        }
        return;
      }

      // Handle delete confirmation
      if (deleteConfirm) {
        if (e.key === 'y' || e.key === 'Y') {
          e.preventDefault();
          handleDelete(deleteConfirm);
        } else if (e.key === 'n' || e.key === 'N' || e.key === 'Escape') {
          e.preventDefault();
          setDeleteConfirm(null);
        }
        return;
      }

      const maxIdx = filteredDocuments.length - 1;

      switch (e.key) {
        case 'j':
        case 'ArrowDown':
          e.preventDefault();
          setSelectedIndex((i) => Math.min(i + 1, maxIdx));
          break;
        case 'k':
        case 'ArrowUp':
          e.preventDefault();
          setSelectedIndex((i) => Math.max(i - 1, 0));
          break;
        case 'g':
          if (e.shiftKey) {
            e.preventDefault();
            setSelectedIndex(maxIdx); // G = go to end
          } else {
            e.preventDefault();
            setSelectedIndex(0); // g = go to start
          }
          break;
        case 'Enter':
        case 'l':
        case 'ArrowRight':
          if (selectedDoc && onSelectDocument) {
            e.preventDefault();
            onSelectDocument(selectedDoc.path);
          }
          break;
        case '/':
          e.preventDefault();
          searchRef.current?.focus();
          break;
        case 'r':
          e.preventDefault();
          loadData();
          break;
        case 'u':
          if (onUpload && !e.metaKey && !e.ctrlKey) {
            e.preventDefault();
            onUpload();
          }
          break;
        case 'd':
          // Delete current document (with confirmation)
          if (selectedDoc && !e.metaKey && !e.ctrlKey) {
            e.preventDefault();
            setDeleteConfirm(selectedDoc.path);
          }
          break;
        case 'R':
          // Rename current document (Shift+R)
          if (selectedDoc && !e.metaKey && !e.ctrlKey) {
            e.preventDefault();
            setRenameMode(selectedDoc.path);
            setRenameValue(selectedDoc.path);
          }
          break;
        // Quick status filters
        case '1':
          e.preventDefault();
          setStatusFilter('all');
          break;
        case '2':
          e.preventDefault();
          setStatusFilter('ready');
          break;
        case '3':
          e.preventDefault();
          setStatusFilter('processing');
          break;
        case '4':
          e.preventDefault();
          setStatusFilter('uploaded');
          break;
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [filteredDocuments.length, selectedDoc, onSelectDocument, loadData, onUpload, deleteConfirm, renameMode, handleDelete]);

  // Scroll selected into view
  useEffect(() => {
    const list = listRef.current;
    if (!list) return;
    const row = list.querySelector(`[data-index="${selectedIndex}"]`) as HTMLElement;
    if (row) {
      row.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
    }
  }, [selectedIndex]);

  // ==========================================================================
  // Helpers
  // ==========================================================================

  const formatDate = (dateStr: string | null) => {
    if (!dateStr) return '—';
    const d = new Date(dateStr);
    const now = new Date();
    const diff = now.getTime() - d.getTime();
    const mins = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);
    const days = Math.floor(diff / 86400000);

    if (mins < 1) return 'just now';
    if (mins < 60) return `${mins}m ago`;
    if (hours < 24) return `${hours}h ago`;
    if (days < 7) return `${days}d ago`;
    return d.toLocaleDateString();
  };

  const getStatusAccent = (status: DocumentStatus) => {
    return STATUS_CONFIG[status]?.accent || 'var(--steel-600)';
  };

  // ==========================================================================
  // Render
  // ==========================================================================

  if (loading && !metrics) {
    return (
      <div className="flex items-center justify-center h-full bg-steel-950" ref={containerRef}>
        <div className="flex flex-col items-center gap-4">
          <span className="text-sm text-steel-500 tracking-wider">Loading documents...</span>
        </div>
      </div>
    );
  }

  if (error && !metrics) {
    return (
      <div className="flex items-center justify-center h-full bg-steel-950" ref={containerRef}>
        <div className="text-center p-8">
          <p className="text-sm text-red-400 mb-4">{error}</p>
          <button
            className="px-4 py-2 bg-steel-800 border border-steel-700 rounded text-steel-100 text-sm font-mono hover:bg-steel-700 hover:border-steel-600 transition-colors"
            onClick={loadData}
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="director" ref={containerRef}>
      {/* === SIDEBAR: Stats & Filters === */}
      <DirectorSidebar
        metrics={metrics}
        statusFilter={statusFilter}
        onStatusFilterChange={setStatusFilter}
        streamConnected={streamConnected}
        onUpload={onUpload}
        onRefresh={loadData}
      />

      {/* === MAIN: Document List === */}
      <main className="flex flex-col min-w-0 overflow-hidden">
        {/* Search bar */}
        <div className="flex items-center gap-2 px-4 py-2 bg-steel-900 border-b border-steel-800">
          <span className="text-sm text-steel-500 font-semibold">/</span>
          <input
            ref={searchRef}
            type="text"
            className="input-base input-sm flex-1"
            placeholder="Search documents..."
            value={searchQuery}
            onChange={(e) => {
              setSearchQuery(e.target.value);
              setSelectedIndex(0);
            }}
          />
          <span className="text-xs text-steel-500 whitespace-nowrap">
            {filteredDocuments.length} / {documents.length}
          </span>
        </div>

        {/* Column headers */}
        <div className="grid grid-cols-[1fr_100px_80px_100px] gap-2 px-4 py-1 bg-steel-850 border-b border-steel-800">
          <button
            className={`p-1 bg-transparent border-none font-mono text-xs font-semibold uppercase tracking-wider text-left select-none transition-colors hover:text-steel-300 ${
              sortField === 'path' ? 'text-steel-100' : 'text-steel-500'
            }`}
            onClick={() => {
              if (sortField === 'path') setSortDir((d) => (d === 'asc' ? 'desc' : 'asc'));
              else {
                setSortField('path');
                setSortDir('asc');
              }
            }}
          >
            Path {sortField === 'path' && (sortDir === 'asc' ? '▲' : '▼')}
          </button>
          <button
            className={`p-1 bg-transparent border-none font-mono text-xs font-semibold uppercase tracking-wider text-left select-none transition-colors hover:text-steel-300 ${
              sortField === 'status' ? 'text-steel-100' : 'text-steel-500'
            }`}
            onClick={() => {
              if (sortField === 'status') setSortDir((d) => (d === 'asc' ? 'desc' : 'asc'));
              else {
                setSortField('status');
                setSortDir('asc');
              }
            }}
          >
            Status {sortField === 'status' && (sortDir === 'asc' ? '▲' : '▼')}
          </button>
          <button
            className={`p-1 bg-transparent border-none font-mono text-xs font-semibold uppercase tracking-wider text-right select-none transition-colors hover:text-steel-300 ${
              sortField === 'claims' ? 'text-steel-100' : 'text-steel-500'
            }`}
            onClick={() => {
              if (sortField === 'claims') setSortDir((d) => (d === 'asc' ? 'desc' : 'asc'));
              else {
                setSortField('claims');
                setSortDir('desc');
              }
            }}
          >
            Claims {sortField === 'claims' && (sortDir === 'asc' ? '▲' : '▼')}
          </button>
          <button
            className={`p-1 bg-transparent border-none font-mono text-xs font-semibold uppercase tracking-wider text-right select-none transition-colors hover:text-steel-300 ${
              sortField === 'analyzed_at' ? 'text-steel-100' : 'text-steel-500'
            }`}
            onClick={() => {
              if (sortField === 'analyzed_at') setSortDir((d) => (d === 'asc' ? 'desc' : 'asc'));
              else {
                setSortField('analyzed_at');
                setSortDir('desc');
              }
            }}
          >
            Analyzed {sortField === 'analyzed_at' && (sortDir === 'asc' ? '▲' : '▼')}
          </button>
        </div>

        {/* Document list */}
        <div className="flex-1 overflow-y-auto overflow-x-hidden" ref={listRef}>
          {filteredDocuments.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full px-8 text-center">
              {documents.length === 0 ? (
                <>
                  <p className="mb-2 text-lg font-semibold text-steel-300">No documents yet</p>
                  <p className="mb-6 text-sm text-steel-500 max-w-xs leading-relaxed">
                    Upload spec files to begin. Documents auto-analyze on upload.
                  </p>
                  {onUpload && (
                    <button
                      className="px-6 py-2 bg-green-600 border-none rounded text-steel-950 font-mono text-sm font-semibold transition-all hover:brightness-110"
                      onClick={onUpload}
                    >
                      Upload First Document
                    </button>
                  )}
                </>
              ) : (
                <>
                  <p className="mb-2 text-lg font-semibold text-steel-300">No matches</p>
                  <p className="text-sm text-steel-500">Try a different search or filter.</p>
                </>
              )}
            </div>
          ) : (
            filteredDocuments.map((doc, idx) => {
              const accentColor = getStatusAccent(doc.status);
              return (
                <div
                  key={doc.path}
                  className={`grid grid-cols-[1fr_100px_80px_100px] gap-2 px-4 py-2 border-b border-steel-900 border-l-2 transition-colors cursor-pointer hover:bg-steel-900 ${
                    idx === selectedIndex ? 'bg-steel-850' : 'border-l-transparent'
                  }`}
                  style={idx === selectedIndex ? { borderLeftColor: accentColor } : undefined}
                  data-index={idx}
                  onClick={() => setSelectedIndex(idx)}
                  onDoubleClick={() => onSelectDocument?.(doc.path)}
                >
                  <div className="flex flex-col gap-0.5 min-w-0 overflow-hidden">
                    <span className="text-sm font-medium text-steel-100 whitespace-nowrap overflow-hidden text-ellipsis">
                      {doc.title || doc.path}
                    </span>
                    {doc.title && doc.title !== doc.path && (
                      <span className="text-xs text-steel-500 whitespace-nowrap overflow-hidden text-ellipsis">
                        {doc.path}
                      </span>
                    )}
                  </div>
                  <div className="flex items-center">
                    <span
                      className="px-1.5 py-0.5 bg-steel-800 rounded-full text-xs font-medium uppercase tracking-wide"
                      style={{ borderColor: accentColor, color: accentColor, borderWidth: '1px' }}
                    >
                      {doc.status}
                    </span>
                  </div>
                  <div className="flex items-center justify-end gap-1">
                    <span className="text-sm font-semibold text-steel-200 tabular-nums">
                      {doc.claim_count ?? 0}
                    </span>
                    {getRefCount(doc) > 0 && (
                      <span className="text-xs text-green-500" title="Impl refs">
                        +{getRefCount(doc)}
                      </span>
                    )}
                  </div>
                  <div className="text-xs text-steel-500 text-right whitespace-nowrap">
                    {formatDate(doc.analyzed_at)}
                  </div>
                </div>
              );
            })
          )}
        </div>
      </main>

      {/* === DETAIL: Selected Document === */}
      <aside className="flex flex-col p-4 bg-steel-900 border-l border-steel-800 overflow-y-auto min-h-0">
        {selectedDoc ? (
          <>
            <div className="flex items-start justify-between gap-2 mb-4">
              <h2 className="m-0 text-base font-semibold text-steel-100 leading-tight break-words">
                {selectedDoc.title || selectedDoc.path}
              </h2>
              <span
                className="flex-shrink-0 px-2 py-0.5 bg-steel-800 rounded-full text-xs font-semibold uppercase tracking-wide"
                style={{
                  borderColor: getStatusAccent(selectedDoc.status),
                  color: getStatusAccent(selectedDoc.status),
                  borderWidth: '1px',
                }}
              >
                {selectedDoc.status}
              </span>
            </div>

            {/* Path - editable if rename mode */}
            {renameMode === selectedDoc.path ? (
              <div className="mb-4">
                <input
                  type="text"
                  className="input-base input-sm input-accent"
                  value={renameValue}
                  onChange={(e) => setRenameValue(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') {
                      e.preventDefault();
                      handleRename(selectedDoc.path, renameValue);
                    } else if (e.key === 'Escape') {
                      setRenameMode(null);
                      setRenameValue('');
                    }
                  }}
                  autoFocus
                />
                <div className="flex gap-1 mt-1">
                  <button
                    className="flex-1 px-2 py-1 bg-purple-600 border-none rounded text-white text-xs font-medium transition-all hover:brightness-110"
                    onClick={() => handleRename(selectedDoc.path, renameValue)}
                  >
                    Save
                  </button>
                  <button
                    className="flex-1 px-2 py-1 bg-steel-800 border border-steel-700 rounded text-steel-300 text-xs font-medium transition-all hover:bg-steel-700"
                    onClick={() => {
                      setRenameMode(null);
                      setRenameValue('');
                    }}
                  >
                    Cancel
                  </button>
                </div>
              </div>
            ) : (
              <div className="px-2 py-2 bg-steel-850 rounded text-xs text-steel-400 break-all mb-4">
                {selectedDoc.path}
              </div>
            )}

            <div className="grid grid-cols-2 gap-2 mb-4">
              <div className="flex flex-col items-center px-2 py-2 bg-steel-850 border border-steel-800 rounded">
                <span className="text-lg font-semibold text-steel-100 leading-none">
                  {selectedDoc.claim_count ?? 0}
                </span>
                <span className="text-xs text-steel-500 uppercase tracking-wide mt-1">Claims</span>
              </div>
              <div className="flex flex-col items-center px-2 py-2 bg-steel-850 border border-steel-800 rounded">
                <span className="text-lg font-semibold text-steel-100 leading-none">
                  {selectedDoc.impl_count ?? 0}
                </span>
                <span className="text-xs text-steel-500 uppercase tracking-wide mt-1">Impls</span>
              </div>
              <div className="flex flex-col items-center px-2 py-2 bg-steel-850 border border-steel-800 rounded">
                <span className="text-lg font-semibold text-steel-100 leading-none">
                  {selectedDoc.test_count ?? 0}
                </span>
                <span className="text-xs text-steel-500 uppercase tracking-wide mt-1">Tests</span>
              </div>
              <div className="flex flex-col items-center px-2 py-2 bg-steel-850 border border-steel-800 rounded">
                <span className="text-lg font-semibold text-steel-100 leading-none">
                  {selectedDoc.placeholder_count ?? 0}
                </span>
                <span className="text-xs text-steel-500 uppercase tracking-wide mt-1">Placeholders</span>
              </div>
            </div>

            {selectedDoc.analyzed_at && (
              <div className="text-xs text-steel-500 mb-4">
                Analyzed: {new Date(selectedDoc.analyzed_at).toLocaleString()}
              </div>
            )}

            {/* Delete confirmation */}
            {deleteConfirm === selectedDoc.path && (
              <div className="p-3 mb-4 bg-red-950 border border-red-800 rounded">
                <p className="text-sm font-semibold text-red-200 mb-2">Delete document?</p>
                <p className="text-xs text-red-300 mb-3">
                  This will permanently delete <span className="font-mono">{selectedDoc.path}</span> and cannot be undone.
                </p>
                <div className="flex gap-2">
                  <button
                    className="flex-1 px-3 py-1.5 bg-red-600 border-none rounded text-white text-sm font-medium transition-all hover:brightness-110"
                    onClick={() => handleDelete(selectedDoc.path)}
                  >
                    Yes, Delete
                  </button>
                  <button
                    className="flex-1 px-3 py-1.5 bg-steel-800 border border-steel-700 rounded text-steel-300 text-sm font-medium transition-all hover:bg-steel-700"
                    onClick={() => setDeleteConfirm(null)}
                  >
                    Cancel
                  </button>
                </div>
                <p className="text-xs text-steel-500 mt-2 text-center">or press <kbd className="px-1 py-0.5 bg-steel-800 rounded text-xs">y</kbd> / <kbd className="px-1 py-0.5 bg-steel-800 rounded text-xs">n</kbd></p>
              </div>
            )}

            <div className="mt-auto flex flex-col gap-2">
              <button
                className="w-full px-4 py-2 bg-purple-600 border border-purple-600 rounded text-white font-mono text-sm font-medium transition-all hover:brightness-110"
                onClick={() => onSelectDocument?.(selectedDoc.path)}
              >
                Open Document →
              </button>

              {!deleteConfirm && (
                <div className="grid grid-cols-2 gap-2">
                  <button
                    className="px-3 py-1.5 bg-steel-800 border border-steel-700 rounded text-steel-300 text-xs font-medium transition-all hover:bg-steel-700 hover:border-purple-600 hover:text-purple-300"
                    onClick={() => {
                      setRenameMode(selectedDoc.path);
                      setRenameValue(selectedDoc.path);
                    }}
                    title="Rename document (Shift+R)"
                  >
                    <kbd className="text-xs">R</kbd> Rename
                  </button>
                  <button
                    className="px-3 py-1.5 bg-steel-800 border border-steel-700 rounded text-steel-300 text-xs font-medium transition-all hover:bg-steel-700 hover:border-red-600 hover:text-red-300"
                    onClick={() => setDeleteConfirm(selectedDoc.path)}
                    title="Delete document (d)"
                  >
                    <kbd className="text-xs">d</kbd> Delete
                  </button>
                </div>
              )}
            </div>
          </>
        ) : (
          <div className="flex items-center justify-center h-full text-steel-500 text-sm text-center">
            <p>Select a document to view details</p>
          </div>
        )}
      </aside>

      {/* Global delete confirmation overlay (keyboard-only) */}
      {deleteConfirm && (
        <div className="fixed inset-0 bg-steel-950/80 flex items-center justify-center z-50" onClick={() => setDeleteConfirm(null)}>
          <div className="bg-steel-900 border border-steel-700 rounded-lg p-6 max-w-md" onClick={(e) => e.stopPropagation()}>
            <h3 className="text-lg font-semibold text-steel-100 mb-2">Delete document?</h3>
            <p className="text-sm text-steel-300 mb-4">
              Permanently delete <span className="font-mono text-purple-400">{deleteConfirm}</span>?
            </p>
            <p className="text-xs text-steel-500 mb-4">This action cannot be undone.</p>
            <div className="flex gap-2">
              <button
                className="flex-1 px-4 py-2 bg-red-600 border-none rounded text-white text-sm font-medium transition-all hover:brightness-110"
                onClick={() => handleDelete(deleteConfirm)}
              >
                Yes, Delete (y)
              </button>
              <button
                className="flex-1 px-4 py-2 bg-steel-800 border border-steel-700 rounded text-steel-300 text-sm font-medium transition-all hover:bg-steel-700"
                onClick={() => setDeleteConfirm(null)}
              >
                Cancel (n)
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
