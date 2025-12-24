/**
 * MarkdownTableToken — Interactive table display with hover info.
 *
 * Renders GFM-style markdown tables with column alignment.
 * Shows hover info with row/column count.
 *
 * "Structured data display with interactive editing."
 */

import { memo } from 'react';

import './tokens.css';

interface TableColumn {
  header: string;
  alignment: 'left' | 'center' | 'right';
  index: number;
}

interface MarkdownTableTokenProps {
  columns: TableColumn[];
  rows: string[][];
  sourceText: string;
  className?: string;
}

export const MarkdownTableToken = memo(function MarkdownTableToken({
  columns,
  rows,
  sourceText: _sourceText,
  className,
}: MarkdownTableTokenProps) {
  const getAlignStyle = (alignment: string): React.CSSProperties => {
    return { textAlign: alignment as 'left' | 'center' | 'right' };
  };

  return (
    <div
      className={`markdown-table-token ${className ?? ''}`}
      data-rows={rows.length}
      data-cols={columns.length}
    >
      {/* INVARIANT: Badge always in DOM, CSS controls visibility (no layout shift) */}
      <div className="markdown-table-token__badge">
        {rows.length} rows × {columns.length} cols
      </div>

      <table className="markdown-table-token__table">
        <thead>
          <tr>
            {columns.map((col, i) => (
              <th key={i} style={getAlignStyle(col.alignment)}>
                {col.header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, rowIdx) => (
            <tr key={rowIdx}>
              {row.map((cell, cellIdx) => (
                <td key={cellIdx} style={getAlignStyle(columns[cellIdx]?.alignment || 'left')}>
                  {cell}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
});
