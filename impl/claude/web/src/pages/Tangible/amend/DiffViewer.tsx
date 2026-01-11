/**
 * DiffViewer - Unified diff viewer component
 *
 * Features:
 * - Red for deletions, green for additions
 * - Line numbers
 * - Context lines
 * - Expandable hunks
 *
 * STARK BIOME aesthetic: 90% steel, 10% earned glow.
 */

import { memo, useState, useMemo } from 'react';
import { ChevronDown, ChevronRight, Plus, Minus } from 'lucide-react';

// =============================================================================
// Types
// =============================================================================

interface DiffLine {
  type: 'context' | 'addition' | 'deletion' | 'hunk-header';
  content: string;
  oldLineNum?: number;
  newLineNum?: number;
}

interface DiffHunk {
  header: string;
  oldStart: number;
  oldCount: number;
  newStart: number;
  newCount: number;
  lines: DiffLine[];
}

export interface DiffViewerProps {
  /** The unified diff string */
  diff: string;
  /** Original content (for split view) */
  originalContent?: string;
  /** Proposed content (for split view) */
  proposedContent?: string;
  /** View mode: unified or split */
  viewMode?: 'unified' | 'split';
  /** Whether to show line numbers */
  showLineNumbers?: boolean;
  /** Number of context lines to show around changes */
  contextLines?: number;
  /** Whether to allow expanding collapsed hunks */
  expandable?: boolean;
  /** Whether hunks start collapsed */
  startCollapsed?: boolean;
  /** File name for header display */
  fileName?: string;
}

// =============================================================================
// Diff Parsing
// =============================================================================

function parseDiff(diff: string): DiffHunk[] {
  if (!diff || diff.trim() === '') {
    return [];
  }

  const lines = diff.split('\n');
  const hunks: DiffHunk[] = [];
  let currentHunk: DiffHunk | null = null;
  let oldLineNum = 0;
  let newLineNum = 0;

  for (const line of lines) {
    // Skip file headers
    if (line.startsWith('---') || line.startsWith('+++') || line.startsWith('diff ')) {
      continue;
    }

    // Hunk header
    const hunkMatch = line.match(/^@@\s+-(\d+)(?:,(\d+))?\s+\+(\d+)(?:,(\d+))?\s+@@(.*)$/);
    if (hunkMatch) {
      if (currentHunk) {
        hunks.push(currentHunk);
      }
      oldLineNum = parseInt(hunkMatch[1], 10);
      newLineNum = parseInt(hunkMatch[3], 10);
      currentHunk = {
        header: line,
        oldStart: oldLineNum,
        oldCount: parseInt(hunkMatch[2] || '1', 10),
        newStart: newLineNum,
        newCount: parseInt(hunkMatch[4] || '1', 10),
        lines: [
          {
            type: 'hunk-header',
            content: hunkMatch[5]?.trim() || '',
          },
        ],
      };
      continue;
    }

    if (!currentHunk) continue;

    if (line.startsWith('+')) {
      currentHunk.lines.push({
        type: 'addition',
        content: line.slice(1),
        newLineNum: newLineNum++,
      });
    } else if (line.startsWith('-')) {
      currentHunk.lines.push({
        type: 'deletion',
        content: line.slice(1),
        oldLineNum: oldLineNum++,
      });
    } else if (line.startsWith(' ') || line === '') {
      currentHunk.lines.push({
        type: 'context',
        content: line.slice(1) || '',
        oldLineNum: oldLineNum++,
        newLineNum: newLineNum++,
      });
    }
  }

  if (currentHunk) {
    hunks.push(currentHunk);
  }

  return hunks;
}

// =============================================================================
// Subcomponents
// =============================================================================

interface DiffLineRowProps {
  line: DiffLine;
  showLineNumbers: boolean;
}

const DiffLineRow = memo(function DiffLineRow({ line, showLineNumbers }: DiffLineRowProps) {
  const getLineClass = () => {
    switch (line.type) {
      case 'addition':
        return 'diff-viewer__line--addition';
      case 'deletion':
        return 'diff-viewer__line--deletion';
      case 'hunk-header':
        return 'diff-viewer__line--hunk-header';
      default:
        return '';
    }
  };

  const getIcon = () => {
    switch (line.type) {
      case 'addition':
        return <Plus size={12} className="diff-viewer__icon diff-viewer__icon--add" />;
      case 'deletion':
        return <Minus size={12} className="diff-viewer__icon diff-viewer__icon--del" />;
      default:
        return <span className="diff-viewer__icon" />;
    }
  };

  if (line.type === 'hunk-header') {
    return (
      <div className={`diff-viewer__line ${getLineClass()}`}>
        {showLineNumbers && (
          <>
            <span className="diff-viewer__line-num diff-viewer__line-num--hunk">...</span>
            <span className="diff-viewer__line-num diff-viewer__line-num--hunk">...</span>
          </>
        )}
        <span className="diff-viewer__icon" />
        <span className="diff-viewer__content diff-viewer__content--hunk">{line.content}</span>
      </div>
    );
  }

  return (
    <div className={`diff-viewer__line ${getLineClass()}`}>
      {showLineNumbers && (
        <>
          <span className="diff-viewer__line-num">{line.oldLineNum ?? ''}</span>
          <span className="diff-viewer__line-num">{line.newLineNum ?? ''}</span>
        </>
      )}
      {getIcon()}
      <code className="diff-viewer__content">{line.content || ' '}</code>
    </div>
  );
});

interface DiffHunkViewProps {
  hunk: DiffHunk;
  index: number;
  showLineNumbers: boolean;
  expandable: boolean;
  startCollapsed: boolean;
}

const DiffHunkView = memo(function DiffHunkView({
  hunk,
  index,
  showLineNumbers,
  expandable,
  startCollapsed,
}: DiffHunkViewProps) {
  const [isCollapsed, setIsCollapsed] = useState(startCollapsed);

  const additions = hunk.lines.filter((l) => l.type === 'addition').length;
  const deletions = hunk.lines.filter((l) => l.type === 'deletion').length;

  return (
    <div className="diff-viewer__hunk">
      <div className="diff-viewer__hunk-header">
        {expandable && (
          <button
            className="diff-viewer__hunk-toggle"
            onClick={() => setIsCollapsed(!isCollapsed)}
            aria-label={isCollapsed ? 'Expand hunk' : 'Collapse hunk'}
          >
            {isCollapsed ? <ChevronRight size={14} /> : <ChevronDown size={14} />}
          </button>
        )}
        <span className="diff-viewer__hunk-location">
          @@ -{hunk.oldStart},{hunk.oldCount} +{hunk.newStart},{hunk.newCount} @@
        </span>
        <span className="diff-viewer__hunk-stats">
          <span className="diff-viewer__hunk-stat diff-viewer__hunk-stat--add">+{additions}</span>
          <span className="diff-viewer__hunk-stat diff-viewer__hunk-stat--del">-{deletions}</span>
        </span>
        {hunk.lines[0]?.type === 'hunk-header' && hunk.lines[0].content && (
          <span className="diff-viewer__hunk-context">{hunk.lines[0].content}</span>
        )}
      </div>

      {!isCollapsed && (
        <div className="diff-viewer__hunk-content">
          {hunk.lines.slice(1).map((line, lineIndex) => (
            <DiffLineRow
              key={`hunk-${index}-line-${lineIndex}`}
              line={line}
              showLineNumbers={showLineNumbers}
            />
          ))}
        </div>
      )}
    </div>
  );
});

// =============================================================================
// Split View Components
// =============================================================================

interface SplitViewProps {
  originalContent: string;
  proposedContent: string;
}

const SplitView = memo(function SplitView({ originalContent, proposedContent }: SplitViewProps) {
  const originalLines = originalContent.split('\n');
  const proposedLines = proposedContent.split('\n');

  return (
    <div className="diff-viewer__split">
      <div className="diff-viewer__split-pane diff-viewer__split-pane--original">
        <div className="diff-viewer__split-header">
          <span className="diff-viewer__split-label">Original</span>
        </div>
        <div className="diff-viewer__split-content">
          {originalLines.map((line, index) => (
            <div key={`original-${index}`} className="diff-viewer__split-line">
              <span className="diff-viewer__line-num">{index + 1}</span>
              <code className="diff-viewer__content">{line || ' '}</code>
            </div>
          ))}
        </div>
      </div>

      <div className="diff-viewer__split-divider" />

      <div className="diff-viewer__split-pane diff-viewer__split-pane--proposed">
        <div className="diff-viewer__split-header">
          <span className="diff-viewer__split-label">Proposed</span>
        </div>
        <div className="diff-viewer__split-content">
          {proposedLines.map((line, index) => (
            <div key={`proposed-${index}`} className="diff-viewer__split-line">
              <span className="diff-viewer__line-num">{index + 1}</span>
              <code className="diff-viewer__content">{line || ' '}</code>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
});

// =============================================================================
// Main Component
// =============================================================================

export const DiffViewer = memo(function DiffViewer({
  diff,
  originalContent,
  proposedContent,
  viewMode = 'unified',
  showLineNumbers = true,
  contextLines: _contextLines = 3,
  expandable = true,
  startCollapsed = false,
  fileName,
}: DiffViewerProps) {
  const hunks = useMemo(() => parseDiff(diff), [diff]);

  // Calculate totals
  const totalAdditions = hunks.reduce(
    (sum, hunk) => sum + hunk.lines.filter((l) => l.type === 'addition').length,
    0
  );
  const totalDeletions = hunks.reduce(
    (sum, hunk) => sum + hunk.lines.filter((l) => l.type === 'deletion').length,
    0
  );

  // If split view and we have both contents, show split
  if (viewMode === 'split' && originalContent && proposedContent) {
    return (
      <div className="diff-viewer diff-viewer--split">
        {fileName && (
          <div className="diff-viewer__file-header">
            <span className="diff-viewer__file-name">{fileName}</span>
            <span className="diff-viewer__file-stats">
              <span className="diff-viewer__file-stat diff-viewer__file-stat--add">
                +{totalAdditions}
              </span>
              <span className="diff-viewer__file-stat diff-viewer__file-stat--del">
                -{totalDeletions}
              </span>
            </span>
          </div>
        )}
        <SplitView originalContent={originalContent} proposedContent={proposedContent} />
      </div>
    );
  }

  // Default: unified view
  if (hunks.length === 0) {
    return (
      <div className="diff-viewer diff-viewer--empty">
        <p className="diff-viewer__empty-text">No changes to display</p>
      </div>
    );
  }

  return (
    <div className="diff-viewer">
      {fileName && (
        <div className="diff-viewer__file-header">
          <span className="diff-viewer__file-name">{fileName}</span>
          <span className="diff-viewer__file-stats">
            <span className="diff-viewer__file-stat diff-viewer__file-stat--add">
              +{totalAdditions}
            </span>
            <span className="diff-viewer__file-stat diff-viewer__file-stat--del">
              -{totalDeletions}
            </span>
          </span>
        </div>
      )}

      <div className="diff-viewer__hunks">
        {hunks.map((hunk, index) => (
          <DiffHunkView
            key={`hunk-${index}`}
            hunk={hunk}
            index={index}
            showLineNumbers={showLineNumbers}
            expandable={expandable}
            startCollapsed={startCollapsed}
          />
        ))}
      </div>
    </div>
  );
});

export default DiffViewer;
