/**
 * DocumentTable - Sortable, filterable table of all documents
 *
 * Shows:
 * - Path, Status, Claims, Refs, Placeholders
 * - Filter by status
 * - Sort by any column
 * - Row actions
 */

import { useCallback, useEffect, useState } from 'react';

import { listDocuments, type DocumentEntry, type DocumentStatus } from '../../api/director';

import { DocumentStatusBadge } from './DocumentStatus';

import './DocumentTable.css';

// =============================================================================
// Types
// =============================================================================

type SortField = 'path' | 'status' | 'claims' | 'refs' | 'placeholders';
type SortDir = 'asc' | 'desc';

interface DocumentTableProps {
  onSelectDocument?: (path: string) => void;
  onAnalyzeDocument?: (path: string) => void;
  onGeneratePrompt?: (path: string) => void;
}

// =============================================================================
// Component
// =============================================================================

export function DocumentTable({
  onSelectDocument,
  onAnalyzeDocument,
  onGeneratePrompt,
}: DocumentTableProps) {
  const [documents, setDocuments] = useState<DocumentEntry[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Filters & Sorting
  const [statusFilter, setStatusFilter] = useState<DocumentStatus | 'all'>('all');
  const [sortField, setSortField] = useState<SortField>('path');
  const [sortDir, setSortDir] = useState<SortDir>('asc');
  const [searchQuery, setSearchQuery] = useState('');

  // Pagination
  const [page, setPage] = useState(0);
  const pageSize = 50;

  // Load data
  const loadData = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await listDocuments({
        status: statusFilter === 'all' ? undefined : statusFilter,
        limit: pageSize,
        offset: page * pageSize,
      });

      let filteredDocs = response.documents;

      // Client-side search filter
      if (searchQuery) {
        const query = searchQuery.toLowerCase();
        filteredDocs = filteredDocs.filter(
          (d) => d.path.toLowerCase().includes(query) || d.title.toLowerCase().includes(query)
        );
      }

      // Client-side sorting
      filteredDocs = [...filteredDocs].sort((a, b) => {
        let aVal: string | number;
        let bVal: string | number;

        switch (sortField) {
          case 'path':
            aVal = a.path;
            bVal = b.path;
            break;
          case 'status':
            aVal = a.status;
            bVal = b.status;
            break;
          case 'claims':
            aVal = a.claim_count;
            bVal = b.claim_count;
            break;
          case 'refs':
            aVal = a.ref_count;
            bVal = b.ref_count;
            break;
          case 'placeholders':
            aVal = a.placeholder_count;
            bVal = b.placeholder_count;
            break;
        }

        if (typeof aVal === 'string' && typeof bVal === 'string') {
          return sortDir === 'asc'
            ? aVal.localeCompare(bVal)
            : bVal.localeCompare(aVal);
        }

        return sortDir === 'asc' ? (aVal as number) - (bVal as number) : (bVal as number) - (aVal as number);
      });

      setDocuments(filteredDocs);
      setTotal(response.total);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load documents');
    } finally {
      setLoading(false);
    }
  }, [statusFilter, sortField, sortDir, searchQuery, page]);

  useEffect(() => {
    loadData();
  }, [loadData]);

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
    return <span className="document-table__sort-indicator">{sortDir === 'asc' ? '▲' : '▼'}</span>;
  };

  const totalPages = Math.ceil(total / pageSize);

  return (
    <div className="document-table">
      {/* Controls */}
      <div className="document-table__controls">
        <div className="document-table__filters">
          <select
            className="document-table__filter-select"
            value={statusFilter}
            onChange={(e) => {
              setStatusFilter(e.target.value as DocumentStatus | 'all');
              setPage(0);
            }}
          >
            <option value="all">All Documents</option>
            <option value="uploaded">Uploaded</option>
            <option value="processing">Processing</option>
            <option value="ready">Ready</option>
            <option value="executed">Executed</option>
            <option value="stale">Stale</option>
            <option value="failed">Failed</option>
          </select>

          <input
            type="text"
            className="document-table__search"
            placeholder="Search documents..."
            value={searchQuery}
            onChange={(e) => {
              setSearchQuery(e.target.value);
              setPage(0);
            }}
          />
        </div>

        <div className="document-table__info">
          Showing {documents.length} of {total} documents
        </div>
      </div>

      {/* Table */}
      {loading && documents.length === 0 ? (
        <div className="document-table__loading">Loading...</div>
      ) : error ? (
        <div className="document-table__error">{error}</div>
      ) : documents.length === 0 ? (
        <div className="document-table__empty">
          <div className="document-table__empty-icon">📄</div>
          <h3 className="document-table__empty-title">No documents yet</h3>
          <p className="document-table__empty-message">Upload documents to get started.</p>
        </div>
      ) : (
        <div className="document-table__wrapper">
          <table className="document-table__table">
            <thead>
              <tr>
                <th onClick={() => handleSort('path')} className="document-table__th--sortable">
                  Path {renderSortIndicator('path')}
                </th>
                <th onClick={() => handleSort('status')} className="document-table__th--sortable">
                  Status {renderSortIndicator('status')}
                </th>
                <th
                  onClick={() => handleSort('claims')}
                  className="document-table__th--sortable document-table__th--num"
                >
                  Claims {renderSortIndicator('claims')}
                </th>
                <th
                  onClick={() => handleSort('refs')}
                  className="document-table__th--sortable document-table__th--num"
                >
                  Refs {renderSortIndicator('refs')}
                </th>
                <th
                  onClick={() => handleSort('placeholders')}
                  className="document-table__th--sortable document-table__th--num"
                >
                  Placeholders {renderSortIndicator('placeholders')}
                </th>
                <th className="document-table__th--actions">Actions</th>
              </tr>
            </thead>
            <tbody>
              {documents.map((doc) => (
                <tr
                  key={doc.path}
                  className="document-table__row"
                  data-status={doc.status}
                >
                  <td
                    className="document-table__cell-path"
                    onClick={() => onSelectDocument?.(doc.path)}
                  >
                    <span className="document-table__path-text">{doc.path}</span>
                    {doc.title !== doc.path && (
                      <span className="document-table__path-title">{doc.title}</span>
                    )}
                  </td>
                  <td>
                    <DocumentStatusBadge status={doc.status} />
                  </td>
                  <td className="document-table__cell-num">{doc.claim_count}</td>
                  <td className="document-table__cell-num">{doc.ref_count}</td>
                  <td className="document-table__cell-num">{doc.placeholder_count}</td>
                  <td className="document-table__cell-actions">
                    <button
                      className="document-table__action-btn"
                      onClick={() => onSelectDocument?.(doc.path)}
                      title="View details"
                    >
                      View
                    </button>
                    {(doc.status === 'uploaded' || doc.status === 'stale') && (
                      <button
                        className="document-table__action-btn"
                        onClick={() => onAnalyzeDocument?.(doc.path)}
                        title="Analyze document"
                      >
                        Analyze
                      </button>
                    )}
                    {doc.status === 'ready' && (
                      <button
                        className="document-table__action-btn"
                        onClick={() => onGeneratePrompt?.(doc.path)}
                        title="Generate execution prompt"
                      >
                        Generate
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="document-table__pagination">
          <button
            className="document-table__page-btn"
            onClick={() => setPage((p) => Math.max(0, p - 1))}
            disabled={page === 0}
          >
            ← Prev
          </button>
          <span className="document-table__page-info">
            Page {page + 1} of {totalPages}
          </span>
          <button
            className="document-table__page-btn"
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
