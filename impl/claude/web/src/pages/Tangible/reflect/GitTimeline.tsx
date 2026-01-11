/**
 * GitTimeline - Right panel git history viewer
 *
 * Features:
 * - Full commit history with filtering
 * - Commit details: message, author, date, files changed
 * - Click to see diff
 * - Search commits
 * - Filter by file, author, date range
 *
 * STARK BIOME aesthetic: 90% steel, 10% earned glow.
 */

import { memo, useState, useCallback, useMemo } from 'react';
import {
  GitCommit,
  Search,
  Filter,
  User,
  Calendar,
  FileText,
  Plus,
  Minus,
  ChevronDown,
  ChevronRight,
} from 'lucide-react';
import type { CommitInfo, CommitDetail, CommitFilter, CommitFile } from './types';

// =============================================================================
// Types
// =============================================================================

export interface GitTimelineProps {
  commits?: CommitInfo[];
  onCommitSelect: (sha: string) => void;
  selectedCommit: string | null;
  filter?: CommitFilter;
  onFilterChange?: (filter: CommitFilter) => void;
}

// =============================================================================
// Mock Data
// =============================================================================

const MOCK_COMMITS: CommitInfo[] = [
  {
    sha: 'abc123def456',
    shortSha: 'abc123d',
    message: 'feat(witness): Add evidence ladder computation',
    author: 'Claude',
    authorEmail: 'claude@anthropic.com',
    date: '2025-12-21T14:30:00Z',
    filesChanged: 5,
    insertions: 234,
    deletions: 45,
  },
  {
    sha: 'def456abc789',
    shortSha: 'def456a',
    message: 'fix(town): Resolve citizen phase transition bug',
    author: 'Kent',
    authorEmail: 'kent@kgents.dev',
    date: '2025-12-21T10:15:00Z',
    filesChanged: 2,
    insertions: 18,
    deletions: 12,
  },
  {
    sha: 'ghi789jkl012',
    shortSha: 'ghi789j',
    message: 'refactor(agentese): Simplify path resolution',
    author: 'Claude',
    authorEmail: 'claude@anthropic.com',
    date: '2025-12-20T16:45:00Z',
    filesChanged: 8,
    insertions: 156,
    deletions: 203,
  },
  {
    sha: 'jkl012mno345',
    shortSha: 'jkl012m',
    message: 'docs: Update CLAUDE.md with new skills',
    author: 'Kent',
    authorEmail: 'kent@kgents.dev',
    date: '2025-12-20T09:00:00Z',
    filesChanged: 1,
    insertions: 87,
    deletions: 23,
  },
  {
    sha: 'mno345pqr678',
    shortSha: 'mno345p',
    message: 'feat(brain): Implement dual-track storage',
    author: 'Claude',
    authorEmail: 'claude@anthropic.com',
    date: '2025-12-19T15:20:00Z',
    filesChanged: 12,
    insertions: 456,
    deletions: 89,
  },
  {
    sha: 'pqr678stu901',
    shortSha: 'pqr678s',
    message: 'test: Add property-based tests for PolyAgent',
    author: 'Claude',
    authorEmail: 'claude@anthropic.com',
    date: '2025-12-19T11:00:00Z',
    filesChanged: 3,
    insertions: 189,
    deletions: 0,
  },
];

const MOCK_COMMIT_DETAIL: CommitDetail = {
  ...MOCK_COMMITS[0],
  files: [
    {
      path: 'impl/claude/services/witness/ladder.py',
      status: 'added',
      insertions: 145,
      deletions: 0,
    },
    {
      path: 'impl/claude/services/witness/store.py',
      status: 'modified',
      insertions: 34,
      deletions: 12,
    },
    { path: 'spec/protocols/witness.md', status: 'modified', insertions: 45, deletions: 23 },
    { path: 'impl/claude/web/src/api/witness.ts', status: 'modified', insertions: 8, deletions: 8 },
    { path: 'tests/test_ladder.py', status: 'added', insertions: 2, deletions: 2 },
  ],
  parentSha: 'def456abc789',
};

// =============================================================================
// Subcomponents
// =============================================================================

interface CommitFilesProps {
  files: CommitFile[];
  onFileClick?: (path: string) => void;
}

const CommitFiles = memo(function CommitFiles({ files, onFileClick }: CommitFilesProps) {
  return (
    <div className="git-timeline__files">
      {files.map((file) => (
        <button
          key={file.path}
          className="git-timeline__file"
          data-status={file.status}
          onClick={() => onFileClick?.(file.path)}
        >
          <div className="git-timeline__file-status">
            {file.status === 'added' && <Plus size={10} />}
            {file.status === 'deleted' && <Minus size={10} />}
            {file.status === 'modified' && <FileText size={10} />}
          </div>
          <span className="git-timeline__file-path">{file.path}</span>
          <span className="git-timeline__file-stats">
            <span className="git-timeline__file-add">+{file.insertions}</span>
            <span className="git-timeline__file-del">-{file.deletions}</span>
          </span>
        </button>
      ))}
    </div>
  );
});

// =============================================================================
// Main Component
// =============================================================================

export const GitTimeline = memo(function GitTimeline({
  commits = MOCK_COMMITS,
  onCommitSelect,
  selectedCommit,
  filter = {},
  onFilterChange,
}: GitTimelineProps) {
  const [searchQuery, setSearchQuery] = useState('');
  const [showFilters, setShowFilters] = useState(false);
  const [expandedCommits, setExpandedCommits] = useState<Set<string>>(new Set());

  // Filter commits
  const filteredCommits = useMemo(() => {
    let result = commits;

    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      result = result.filter(
        (c) =>
          c.message.toLowerCase().includes(query) ||
          c.author.toLowerCase().includes(query) ||
          c.sha.includes(query)
      );
    }

    if (filter.author) {
      result = result.filter((c) => c.author.toLowerCase() === filter.author!.toLowerCase());
    }

    if (filter.path) {
      // In real implementation, filter by files touched
      result = result.filter((c) => c.message.toLowerCase().includes(filter.path!.toLowerCase()));
    }

    if (filter.dateRange) {
      const start = filter.dateRange.start.getTime();
      const end = filter.dateRange.end.getTime();
      result = result.filter((c) => {
        const date = new Date(c.date).getTime();
        return date >= start && date <= end;
      });
    }

    return result;
  }, [commits, searchQuery, filter]);

  // Group commits by date
  const groupedCommits = useMemo(() => {
    const groups: Map<string, CommitInfo[]> = new Map();

    for (const commit of filteredCommits) {
      const date = new Date(commit.date).toLocaleDateString('en-US', {
        weekday: 'short',
        month: 'short',
        day: 'numeric',
      });

      const existing = groups.get(date) || [];
      existing.push(commit);
      groups.set(date, existing);
    }

    return groups;
  }, [filteredCommits]);

  // Toggle commit expansion
  const toggleCommit = useCallback((sha: string) => {
    setExpandedCommits((prev) => {
      const next = new Set(prev);
      if (next.has(sha)) {
        next.delete(sha);
      } else {
        next.add(sha);
      }
      return next;
    });
  }, []);

  // Format relative time
  const formatTime = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  // Get unique authors for filter
  const authors = useMemo(() => {
    const set = new Set(commits.map((c) => c.author));
    return Array.from(set);
  }, [commits]);

  return (
    <div className="git-timeline">
      {/* Header */}
      <div className="git-timeline__header">
        <GitCommit size={14} className="git-timeline__icon" />
        <span className="git-timeline__title">Git History</span>
        <span className="git-timeline__count">{filteredCommits.length}</span>
        <button
          className="git-timeline__filter-btn"
          onClick={() => setShowFilters(!showFilters)}
          aria-label="Toggle filters"
        >
          <Filter size={12} />
        </button>
      </div>

      {/* Search */}
      <div className="git-timeline__search">
        <Search size={12} className="git-timeline__search-icon" />
        <input
          type="text"
          className="git-timeline__search-input"
          placeholder="Search commits..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
        />
      </div>

      {/* Filters */}
      {showFilters && (
        <div className="git-timeline__filters">
          <div className="git-timeline__filter-group">
            <label className="git-timeline__filter-label">
              <User size={12} />
              Author
            </label>
            <select
              className="git-timeline__filter-select"
              value={filter.author || ''}
              onChange={(e) => onFilterChange?.({ ...filter, author: e.target.value || undefined })}
            >
              <option value="">All authors</option>
              {authors.map((author) => (
                <option key={author} value={author}>
                  {author}
                </option>
              ))}
            </select>
          </div>

          <div className="git-timeline__filter-group">
            <label className="git-timeline__filter-label">
              <FileText size={12} />
              Path
            </label>
            <input
              type="text"
              className="git-timeline__filter-input"
              placeholder="Filter by path..."
              value={filter.path || ''}
              onChange={(e) => onFilterChange?.({ ...filter, path: e.target.value || undefined })}
            />
          </div>
        </div>
      )}

      {/* Commit list */}
      <div className="git-timeline__commits">
        {filteredCommits.length === 0 ? (
          <div className="git-timeline__empty">
            {searchQuery ? `No commits matching "${searchQuery}"` : 'No commits'}
          </div>
        ) : (
          Array.from(groupedCommits.entries()).map(([date, dateCommits]) => (
            <div key={date} className="git-timeline__group">
              <div className="git-timeline__group-header">
                <Calendar size={10} />
                <span>{date}</span>
                <span className="git-timeline__group-count">{dateCommits.length}</span>
              </div>

              {dateCommits.map((commit) => {
                const isSelected = commit.sha === selectedCommit;
                const isExpanded = expandedCommits.has(commit.sha);

                return (
                  <div key={commit.sha} className="git-timeline__commit-wrapper">
                    <button
                      className="git-timeline__commit"
                      data-selected={isSelected}
                      onClick={() => onCommitSelect(commit.sha)}
                    >
                      {/* Timeline dot */}
                      <div className="git-timeline__dot" />

                      {/* Commit info */}
                      <div className="git-timeline__commit-info">
                        <div className="git-timeline__commit-header">
                          <span className="git-timeline__commit-sha">{commit.shortSha}</span>
                          <span className="git-timeline__commit-time">
                            {formatTime(commit.date)}
                          </span>
                        </div>
                        <div className="git-timeline__commit-message">{commit.message}</div>
                        <div className="git-timeline__commit-meta">
                          <span className="git-timeline__commit-author">{commit.author}</span>
                          <span className="git-timeline__commit-stats">
                            <span className="git-timeline__stat-files">
                              {commit.filesChanged} file{commit.filesChanged !== 1 ? 's' : ''}
                            </span>
                            {commit.insertions !== undefined && (
                              <span className="git-timeline__stat-add">+{commit.insertions}</span>
                            )}
                            {commit.deletions !== undefined && (
                              <span className="git-timeline__stat-del">-{commit.deletions}</span>
                            )}
                          </span>
                        </div>
                      </div>

                      {/* Expand button */}
                      <button
                        className="git-timeline__expand-btn"
                        onClick={(e) => {
                          e.stopPropagation();
                          toggleCommit(commit.sha);
                        }}
                        aria-label={isExpanded ? 'Collapse' : 'Expand'}
                      >
                        {isExpanded ? <ChevronDown size={12} /> : <ChevronRight size={12} />}
                      </button>
                    </button>

                    {/* Expanded files */}
                    {isExpanded && (
                      <CommitFiles
                        files={MOCK_COMMIT_DETAIL.files}
                        onFileClick={(path) => console.log('Navigate to', path)}
                      />
                    )}
                  </div>
                );
              })}
            </div>
          ))
        )}
      </div>
    </div>
  );
});

export default GitTimeline;
