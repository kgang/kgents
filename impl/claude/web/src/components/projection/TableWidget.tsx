/**
 * TableWidget: Data table with sorting and pagination.
 *
 * Features:
 * - Column sorting
 * - Pagination
 * - Row selection
 * - Responsive layout
 */

import { useState, useMemo } from 'react';

export interface TableColumn {
  key: string;
  label: string;
  sortable?: boolean;
  width?: string;
  align?: 'left' | 'center' | 'right';
}

export interface TableWidgetProps {
  columns: TableColumn[];
  rows: Record<string, unknown>[];
  /** Initial sort column */
  sortBy?: string;
  /** Sort direction */
  sortDirection?: 'asc' | 'desc';
  /** Rows per page (0 = no pagination) */
  pageSize?: number;
  /** Enable row selection */
  selectable?: boolean;
  /** Selected row keys */
  selectedKeys?: string[];
  /** Key field for row identity */
  rowKey?: string;
  /** Selection change callback */
  onSelectionChange?: (keys: string[]) => void;
  /** Row click callback */
  onRowClick?: (row: Record<string, unknown>) => void;
}

export function TableWidget({
  columns,
  rows,
  sortBy: initialSortBy,
  sortDirection: initialSortDirection = 'asc',
  pageSize = 10,
  selectable = false,
  selectedKeys = [],
  rowKey = 'id',
  onSelectionChange,
  onRowClick,
}: TableWidgetProps) {
  const [sortBy, setSortBy] = useState(initialSortBy);
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>(initialSortDirection);
  const [currentPage, setCurrentPage] = useState(0);
  const [selected, setSelected] = useState<Set<string>>(new Set(selectedKeys));

  // Sort rows
  const sortedRows = useMemo(() => {
    if (!sortBy) return rows;

    return [...rows].sort((a, b) => {
      const aVal = a[sortBy];
      const bVal = b[sortBy];

      if (aVal === bVal) return 0;
      if (aVal == null) return 1;
      if (bVal == null) return -1;

      const comparison = aVal < bVal ? -1 : 1;
      return sortDirection === 'asc' ? comparison : -comparison;
    });
  }, [rows, sortBy, sortDirection]);

  // Paginate rows
  const paginatedRows = useMemo(() => {
    if (pageSize <= 0) return sortedRows;
    const start = currentPage * pageSize;
    return sortedRows.slice(start, start + pageSize);
  }, [sortedRows, currentPage, pageSize]);

  const totalPages = pageSize > 0 ? Math.ceil(rows.length / pageSize) : 1;

  const handleSort = (columnKey: string) => {
    if (sortBy === columnKey) {
      setSortDirection((d) => (d === 'asc' ? 'desc' : 'asc'));
    } else {
      setSortBy(columnKey);
      setSortDirection('asc');
    }
  };

  const handleSelectAll = () => {
    if (selected.size === rows.length) {
      setSelected(new Set());
      onSelectionChange?.([]);
    } else {
      const allKeys = rows.map((r) => String(r[rowKey]));
      setSelected(new Set(allKeys));
      onSelectionChange?.(allKeys);
    }
  };

  const handleSelectRow = (key: string) => {
    const newSelected = new Set(selected);
    if (newSelected.has(key)) {
      newSelected.delete(key);
    } else {
      newSelected.add(key);
    }
    setSelected(newSelected);
    onSelectionChange?.(Array.from(newSelected));
  };

  return (
    <div className="kgents-table-widget">
      <table
        style={{
          width: '100%',
          borderCollapse: 'collapse',
          fontSize: '14px',
        }}
      >
        <thead>
          <tr style={{ borderBottom: '2px solid #e5e7eb' }}>
            {selectable && (
              <th style={{ padding: '12px 8px', width: '40px' }}>
                <input
                  type="checkbox"
                  checked={selected.size === rows.length && rows.length > 0}
                  onChange={handleSelectAll}
                  aria-label="Select all rows"
                />
              </th>
            )}
            {columns.map((col) => (
              <th
                key={col.key}
                style={{
                  padding: '12px 8px',
                  textAlign: col.align || 'left',
                  width: col.width,
                  cursor: col.sortable ? 'pointer' : 'default',
                  userSelect: 'none',
                }}
                onClick={() => col.sortable && handleSort(col.key)}
              >
                <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                  {col.label}
                  {col.sortable && sortBy === col.key && (
                    <span style={{ fontSize: '10px' }}>
                      {sortDirection === 'asc' ? '▲' : '▼'}
                    </span>
                  )}
                </span>
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {paginatedRows.map((row, i) => {
            const key = String(row[rowKey] ?? i);
            const isSelected = selected.has(key);

            return (
              <tr
                key={key}
                style={{
                  borderBottom: '1px solid #e5e7eb',
                  backgroundColor: isSelected ? '#eff6ff' : 'transparent',
                  cursor: onRowClick ? 'pointer' : 'default',
                }}
                onClick={() => onRowClick?.(row)}
              >
                {selectable && (
                  <td style={{ padding: '12px 8px' }}>
                    <input
                      type="checkbox"
                      checked={isSelected}
                      onChange={() => handleSelectRow(key)}
                      onClick={(e) => e.stopPropagation()}
                      aria-label={`Select row ${key}`}
                    />
                  </td>
                )}
                {columns.map((col) => (
                  <td
                    key={col.key}
                    style={{
                      padding: '12px 8px',
                      textAlign: col.align || 'left',
                    }}
                  >
                    {String(row[col.key] ?? '')}
                  </td>
                ))}
              </tr>
            );
          })}
        </tbody>
      </table>

      {/* Pagination */}
      {pageSize > 0 && totalPages > 1 && (
        <div
          style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            padding: '12px 8px',
            borderTop: '1px solid #e5e7eb',
          }}
        >
          <span style={{ fontSize: '14px', color: '#6b7280' }}>
            Showing {currentPage * pageSize + 1}-
            {Math.min((currentPage + 1) * pageSize, rows.length)} of {rows.length}
          </span>
          <div style={{ display: 'flex', gap: '4px' }}>
            <button
              onClick={() => setCurrentPage((p) => Math.max(0, p - 1))}
              disabled={currentPage === 0}
              style={{
                padding: '4px 12px',
                border: '1px solid #d1d5db',
                borderRadius: '4px',
                backgroundColor: currentPage === 0 ? '#f3f4f6' : 'white',
                cursor: currentPage === 0 ? 'not-allowed' : 'pointer',
              }}
            >
              Previous
            </button>
            <button
              onClick={() => setCurrentPage((p) => Math.min(totalPages - 1, p + 1))}
              disabled={currentPage >= totalPages - 1}
              style={{
                padding: '4px 12px',
                border: '1px solid #d1d5db',
                borderRadius: '4px',
                backgroundColor: currentPage >= totalPages - 1 ? '#f3f4f6' : 'white',
                cursor: currentPage >= totalPages - 1 ? 'not-allowed' : 'pointer',
              }}
            >
              Next
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

export default TableWidget;
