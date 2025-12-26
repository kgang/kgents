/**
 * DiffProjection — Content Diff View (VISUAL Mode)
 *
 * Renders side-by-side diff between content and baseContent.
 * Shows additions, deletions, and unchanged sections.
 */

import { memo, useMemo } from 'react';
import type { ProjectionComponentProps } from '../types';
import './DiffProjection.css';

export const DiffProjection = memo(function DiffProjection({
  kblock,
  className = '',
}: ProjectionComponentProps) {
  // Simple line-by-line diff (naive implementation)
  const diff = useMemo(() => {
    const baseLines = kblock.baseContent.split('\n');
    const currentLines = kblock.content.split('\n');

    const maxLines = Math.max(baseLines.length, currentLines.length);
    const diffLines: Array<{
      type: 'unchanged' | 'added' | 'removed' | 'changed';
      base: string;
      current: string;
    }> = [];

    for (let i = 0; i < maxLines; i++) {
      const baseLine = baseLines[i] ?? '';
      const currentLine = currentLines[i] ?? '';

      if (baseLine === currentLine) {
        diffLines.push({ type: 'unchanged', base: baseLine, current: currentLine });
      } else if (!baseLine && currentLine) {
        diffLines.push({ type: 'added', base: '', current: currentLine });
      } else if (baseLine && !currentLine) {
        diffLines.push({ type: 'removed', base: baseLine, current: '' });
      } else {
        diffLines.push({ type: 'changed', base: baseLine, current: currentLine });
      }
    }

    return diffLines;
  }, [kblock.baseContent, kblock.content]);

  return (
    <div className={`diff-projection ${className}`}>
      {/* Header */}
      <div className="diff-projection__header">
        <div className="diff-projection__title">
          Diff: {kblock.path}
        </div>
        <div className="diff-projection__stats">
          {diff.filter((d) => d.type === 'added').length} additions,{' '}
          {diff.filter((d) => d.type === 'removed').length} deletions,{' '}
          {diff.filter((d) => d.type === 'changed').length} changes
        </div>
      </div>

      {/* Side-by-side diff */}
      <div className="diff-projection__content">
        {/* Left: Base */}
        <div className="diff-projection__panel diff-projection__panel--base">
          <div className="diff-projection__panel-label">Base Content</div>
          <div className="diff-projection__lines">
            {diff.map((line, idx) => (
              <div
                key={idx}
                className={`diff-projection__line diff-projection__line--${line.type}`}
              >
                <span className="diff-projection__line-number">{idx + 1}</span>
                <span className="diff-projection__line-content">{line.base}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Right: Current */}
        <div className="diff-projection__panel diff-projection__panel--current">
          <div className="diff-projection__panel-label">Current Content</div>
          <div className="diff-projection__lines">
            {diff.map((line, idx) => (
              <div
                key={idx}
                className={`diff-projection__line diff-projection__line--${line.type}`}
              >
                <span className="diff-projection__line-number">{idx + 1}</span>
                <span className="diff-projection__line-content">{line.current}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
});
