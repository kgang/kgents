/**
 * SpecTable — Sortable, filterable table of all specs
 *
 * Accounting-style ledger table showing:
 * - Path, Status, Claims, Impl, Tests, Refs
 * - Filter by status
 * - Sort by any column
 * - Pagination
 *
 * Philosophy:
 *   "Every spec is an asset or a liability."
 */

import { useCallback, useEffect, useRef, useState } from 'react';

import { getLedger, type SpecEntry } from '../api/specLedger';
import { listDocuments, type DocumentStatus } from '../api/director';
import { useWitnessStream } from '../hooks/useWitnessStream';
import { DocumentStatusBadge } from './director';

import './SpecTable.css';

// =============================================================================
// Types
// =============================================================================

type SortField = 'path' | 'status' | 'claims' | 'impl' | 'tests' | 'refs';
type SortDir = 'asc' | 'desc';
type StatusFilter = 'all' | 'active' | 'orphan' | 'deprecated' | 'archived';

interface SpecTableProps {
  onSelectSpec?: (path: string) => void;
  initialFilter?: StatusFilter;
}

/**
 * Type guard to check if response needs computation (AD-015)
 */
function isNeedsComputation(response: unknown): response is { needs_scan: true; message: string } {
  return (
    typeof response === 'object' &&
    response !== null &&
    'needs_scan' in response &&
    (response as { needs_scan: boolean }).needs_scan === true
  );
}

// =============================================================================
// Component
// =============================================================================

export function SpecTable({ onSelectSpec, initialFilter = 'all' }: SpecTableProps) {
  const [specs, setSpecs] = useState<SpecEntry[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [isEmpty, setIsEmpty] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Director status map (path → status)
  const [directorStatus, setDirectorStatus] = useState<Map<string, DocumentStatus>>(new Map());

  // Filters & Sorting
  const [statusFilter, setStatusFilter] = useState<StatusFilter>(initialFilter);
  const [sortField, setSortField] = useState<SortField>('path');
  const [sortDir, setSortDir] = useState<SortDir>('asc');
  const [searchQuery, setSearchQuery] = useState('');

  // Pagination
  const [page, setPage] = useState(0);
  const pageSize = 50;

  // Real-time witness stream for sovereign ingest events
  const { events: witnessEvents } = useWitnessStream();
  const lastProcessedEventRef = useRef<string | null>(null);

  // Load Director status
  const loadDirectorStatus = useCallback(async () => {
    try {
      const response = await listDocuments();
      const statusMap = new Map<string, DocumentStatus>();
      response.documents.forEach((doc) => {
        statusMap.set(doc.path, doc.status);
      });
      setDirectorStatus(statusMap);
    } catch (err) {
      console.warn('[SpecTable] Failed to load Director status:', err);
      // Don't show error to user - Director status is optional
    }
  }, []);

  // Load data
  const loadData = useCallback(async () => {
    setLoading(true);
    setError(null);
    setIsEmpty(false);

    try {
      const response = await getLedger({
        status: statusFilter === 'all' ? undefined : statusFilter,
        sortBy: sortField === 'claims' ? 'claims' : sortField === 'impl' ? 'impl' : 'path',
        limit: pageSize,
        offset: page * pageSize,
      });

      // AD-015: Handle case where data needs computation or is empty
      if (isNeedsComputation(response)) {
        setIsEmpty(true);
        setSpecs([]);
        setTotal(0);
        return;
      }

      // Safely access specs with fallback to empty array
      let filteredSpecs = response.specs ?? [];

      // Check if corpus is empty
      if (filteredSpecs.length === 0 && (response.total ?? 0) === 0) {
        setIsEmpty(true);
        setSpecs([]);
        setTotal(0);
        return;
      }

      // Client-side search filter
      if (searchQuery) {
        const query = searchQuery.toLowerCase();
        filteredSpecs = filteredSpecs.filter(
          (s) => s.path.toLowerCase().includes(query) || s.title.toLowerCase().includes(query)
        );
      }

      // Client-side sorting (for columns not supported by API)
      if (sortField === 'status') {
        filteredSpecs = [...filteredSpecs].sort((a, b) =>
          sortDir === 'asc' ? a.status.localeCompare(b.status) : b.status.localeCompare(a.status)
        );
      } else if (sortField === 'tests') {
        filteredSpecs = [...filteredSpecs].sort((a, b) =>
          sortDir === 'asc' ? a.test_count - b.test_count : b.test_count - a.test_count
        );
      } else if (sortField === 'refs') {
        filteredSpecs = [...filteredSpecs].sort((a, b) =>
          sortDir === 'asc' ? a.ref_count - b.ref_count : b.ref_count - a.ref_count
        );
      }

      setSpecs(filteredSpecs);
      setTotal(response.total ?? 0);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load specs');
    } finally {
      setLoading(false);
    }
  }, [statusFilter, sortField, sortDir, searchQuery, page]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  useEffect(() => {
    loadDirectorStatus();
  }, [loadDirectorStatus]);

  // Refresh when a sovereign ingest event for a .md file arrives
  useEffect(() => {
    const sovereignEvents = witnessEvents.filter((e) => e.type === 'sovereign');
    const latestSovereign = sovereignEvents[0];

    // Check if it's a new ingest of a markdown file
    if (latestSovereign?.path?.endsWith('.md')) {
      const eventKey = `${latestSovereign.id}-${latestSovereign.path}`;

      // Only refresh if this is a new event we haven't processed
      if (eventKey !== lastProcessedEventRef.current && !loading) {
        lastProcessedEventRef.current = eventKey;
        console.info('[SpecTable] Sovereign ingest detected, refreshing table:', latestSovereign.path);
        loadData();
      }
    }
  }, [witnessEvents, loading, loadData]);

  // Handle sort
  const handleSort = useCallback(
    (field: SortField) => {
      if (field === sortField) {
        setSortDir((d) => (d === 'asc' ? 'desc' : 'asc'));
      } else {
        setSortField(field);
        setSortDir('asc');
      }
    },
    [sortField]
  );

  // Render sort indicator
  const renderSortIndicator = (field: SortField) => {
    if (field !== sortField) return null;
    return <span className="spec-table__sort-indicator">{sortDir === 'asc' ? '▲' : '▼'}</span>;
  };

  const totalPages = Math.ceil(total / pageSize);

  return (
    <div className="spec-table">
      {/* Controls */}
      <div className="spec-table__controls">
        <div className="spec-table__filters">
          <select
            className="spec-table__filter-select"
            value={statusFilter}
            onChange={(e) => {
              setStatusFilter(e.target.value as StatusFilter);
              setPage(0);
            }}
          >
            <option value="all">All Specs</option>
            <option value="active">Active</option>
            <option value="orphan">Orphans</option>
            <option value="deprecated">Deprecated</option>
            <option value="archived">Archived</option>
          </select>

          <input
            type="text"
            className="spec-table__search"
            placeholder="Search specs..."
            value={searchQuery}
            onChange={(e) => {
              setSearchQuery(e.target.value);
              setPage(0);
            }}
          />
        </div>

        <div className="spec-table__info">
          Showing {specs.length} of {total} specs
        </div>
      </div>

      {/* Table */}
      {loading && specs.length === 0 ? (
        <div className="spec-table__loading">Loading...</div>
      ) : error ? (
        <div className="spec-table__error">{error}</div>
      ) : isEmpty ? (
        <div className="spec-table__empty">
          <div className="spec-table__empty-icon">📋</div>
          <h3 className="spec-table__empty-title">No specs yet</h3>
          <p className="spec-table__empty-message">
            Upload spec files to get started, or use the Hypergraph Editor to create new specs.
          </p>
          <a href="/editor" className="spec-table__empty-link">
            Open Editor →
          </a>
        </div>
      ) : (
        <div className="spec-table__wrapper">
          <table className="spec-table__table">
            <thead>
              <tr>
                <th onClick={() => handleSort('path')} className="spec-table__th--sortable">
                  Path {renderSortIndicator('path')}
                </th>
                <th onClick={() => handleSort('status')} className="spec-table__th--sortable">
                  Status {renderSortIndicator('status')}
                </th>
                <th className="spec-table__th--director">Director</th>
                <th
                  onClick={() => handleSort('claims')}
                  className="spec-table__th--sortable spec-table__th--num"
                >
                  Claims {renderSortIndicator('claims')}
                </th>
                <th
                  onClick={() => handleSort('impl')}
                  className="spec-table__th--sortable spec-table__th--num"
                >
                  Impl {renderSortIndicator('impl')}
                </th>
                <th
                  onClick={() => handleSort('tests')}
                  className="spec-table__th--sortable spec-table__th--num"
                >
                  Tests {renderSortIndicator('tests')}
                </th>
                <th
                  onClick={() => handleSort('refs')}
                  className="spec-table__th--sortable spec-table__th--num"
                >
                  Refs {renderSortIndicator('refs')}
                </th>
              </tr>
            </thead>
            <tbody>
              {specs.map((spec) => (
                <tr
                  key={spec.path}
                  className="spec-table__row"
                  onClick={() => onSelectSpec?.(spec.path)}
                  data-status={spec.status.toLowerCase()}
                >
                  <td className="spec-table__cell-path">
                    <span className="spec-table__path-text">{spec.path}</span>
                    {spec.title !== spec.path && (
                      <span className="spec-table__path-title">{spec.title}</span>
                    )}
                  </td>
                  <td>
                    <span className="spec-table__status" data-status={spec.status.toLowerCase()}>
                      {spec.status}
                    </span>
                  </td>
                  <td className="spec-table__cell-director">
                    {directorStatus.has(spec.path) ? (
                      <DocumentStatusBadge status={directorStatus.get(spec.path)!} />
                    ) : (
                      <span className="spec-table__director-empty">—</span>
                    )}
                  </td>
                  <td className="spec-table__cell-num">{spec.claim_count}</td>
                  <td className="spec-table__cell-num" data-has-evidence={spec.impl_count > 0}>
                    {spec.impl_count}
                  </td>
                  <td className="spec-table__cell-num" data-has-evidence={spec.test_count > 0}>
                    {spec.test_count}
                  </td>
                  <td className="spec-table__cell-num">{spec.ref_count}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="spec-table__pagination">
          <button
            className="spec-table__page-btn"
            onClick={() => setPage((p) => Math.max(0, p - 1))}
            disabled={page === 0}
          >
            ← Prev
          </button>
          <span className="spec-table__page-info">
            Page {page + 1} of {totalPages}
          </span>
          <button
            className="spec-table__page-btn"
            onClick={() => setPage((p) => Math.min(totalPages - 1, p + 1))}
            disabled={page >= totalPages - 1}
          >
            Next →
          </button>
        </div>
      )}
    </div>
  );
}
