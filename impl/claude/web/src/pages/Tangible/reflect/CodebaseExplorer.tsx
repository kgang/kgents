/**
 * CodebaseExplorer - Left panel file tree for entire codebase
 *
 * Features:
 * - File tree for spec/ and impl/
 * - Visual indicators: K-Block coverage, drift status, last modified
 * - Expandable folders with lazy loading
 * - Search/filter by name, type, layer
 * - Keyboard navigation (vim-style: j/k, Enter, h/l)
 *
 * STARK BIOME aesthetic: 90% steel, 10% earned glow.
 */

import { memo, useState, useCallback, useMemo, useEffect, useRef } from 'react';
import {
  Search,
  Folder,
  FolderOpen,
  FileText,
  FileCode,
  File,
  Filter,
  ChevronRight,
  AlertTriangle,
  Layers,
  Clock,
} from 'lucide-react';
import type { CodebaseFile, CodebaseFilter, FileType } from './types';
import { LAYER_COLORS } from './types';

// =============================================================================
// Types
// =============================================================================

export interface CodebaseExplorerProps {
  onFileSelect: (path: string) => void;
  selectedPath: string | null;
  filter?: CodebaseFilter;
  onFilterChange?: (filter: CodebaseFilter) => void;
}

// =============================================================================
// Mock Data (until wired to backend)
// =============================================================================

const MOCK_CODEBASE: CodebaseFile[] = [
  {
    path: 'spec/',
    name: 'spec',
    type: 'directory',
    fileType: 'spec',
    children: [
      {
        path: 'spec/agents/',
        name: 'agents',
        type: 'directory',
        fileType: 'spec',
        children: [
          {
            path: 'spec/agents/d-gent.md',
            name: 'd-gent.md',
            type: 'file',
            fileType: 'spec',
            kblockId: 'kb-1',
            layer: 2,
          },
          {
            path: 'spec/agents/k-gent.md',
            name: 'k-gent.md',
            type: 'file',
            fileType: 'spec',
            kblockId: 'kb-2',
            layer: 2,
          },
          {
            path: 'spec/agents/m-gent.md',
            name: 'm-gent.md',
            type: 'file',
            fileType: 'spec',
            kblockId: 'kb-3',
            layer: 2,
          },
        ],
      },
      {
        path: 'spec/protocols/',
        name: 'protocols',
        type: 'directory',
        fileType: 'spec',
        children: [
          {
            path: 'spec/protocols/witness.md',
            name: 'witness.md',
            type: 'file',
            fileType: 'spec',
            kblockId: 'kb-4',
            layer: 2,
            hasDrift: true,
          },
          {
            path: 'spec/protocols/agentese.md',
            name: 'agentese.md',
            type: 'file',
            fileType: 'spec',
            kblockId: 'kb-5',
            layer: 2,
          },
        ],
      },
      {
        path: 'spec/principles/',
        name: 'principles',
        type: 'directory',
        fileType: 'spec',
        children: [
          {
            path: 'spec/principles/composable.md',
            name: 'composable.md',
            type: 'file',
            fileType: 'spec',
            kblockId: 'kb-6',
            layer: 0,
          },
          {
            path: 'spec/principles/ethical.md',
            name: 'ethical.md',
            type: 'file',
            fileType: 'spec',
            kblockId: 'kb-7',
            layer: 0,
          },
          {
            path: 'spec/principles/tasteful.md',
            name: 'tasteful.md',
            type: 'file',
            fileType: 'spec',
            kblockId: 'kb-8',
            layer: 0,
          },
        ],
      },
    ],
  },
  {
    path: 'impl/',
    name: 'impl',
    type: 'directory',
    fileType: 'impl',
    children: [
      {
        path: 'impl/claude/',
        name: 'claude',
        type: 'directory',
        fileType: 'impl',
        children: [
          {
            path: 'impl/claude/services/',
            name: 'services',
            type: 'directory',
            fileType: 'impl',
            children: [
              {
                path: 'impl/claude/services/witness/',
                name: 'witness',
                type: 'directory',
                fileType: 'impl',
                kblockId: 'kb-9',
                layer: 3,
              },
              {
                path: 'impl/claude/services/brain/',
                name: 'brain',
                type: 'directory',
                fileType: 'impl',
                kblockId: 'kb-10',
                layer: 3,
              },
            ],
          },
          {
            path: 'impl/claude/web/',
            name: 'web',
            type: 'directory',
            fileType: 'impl',
            children: [
              { path: 'impl/claude/web/src/', name: 'src', type: 'directory', fileType: 'impl' },
            ],
          },
        ],
      },
    ],
  },
  {
    path: 'docs/',
    name: 'docs',
    type: 'directory',
    fileType: 'docs',
    children: [
      {
        path: 'docs/skills/',
        name: 'skills',
        type: 'directory',
        fileType: 'docs',
        children: [
          {
            path: 'docs/skills/metaphysical-fullstack.md',
            name: 'metaphysical-fullstack.md',
            type: 'file',
            fileType: 'docs',
          },
          {
            path: 'docs/skills/polynomial-agent.md',
            name: 'polynomial-agent.md',
            type: 'file',
            fileType: 'docs',
          },
        ],
      },
    ],
  },
];

// =============================================================================
// Helper Functions
// =============================================================================

function getFileIcon(file: CodebaseFile, expanded: boolean) {
  if (file.type === 'directory') {
    return expanded ? <FolderOpen size={14} /> : <Folder size={14} />;
  }

  switch (file.fileType) {
    case 'spec':
      return <FileText size={14} />;
    case 'impl':
      return <FileCode size={14} />;
    case 'docs':
      return <FileText size={14} />;
    default:
      return <File size={14} />;
  }
}

function flattenTree(
  files: CodebaseFile[],
  expandedPaths: Set<string>,
  depth: number = 0
): Array<{ file: CodebaseFile; depth: number }> {
  const result: Array<{ file: CodebaseFile; depth: number }> = [];

  for (const file of files) {
    result.push({ file, depth });

    if (file.type === 'directory' && expandedPaths.has(file.path) && file.children) {
      result.push(...flattenTree(file.children, expandedPaths, depth + 1));
    }
  }

  return result;
}

function filterFiles(files: CodebaseFile[], filter: CodebaseFilter): CodebaseFile[] {
  const filterFile = (file: CodebaseFile): CodebaseFile | null => {
    // Check type filter
    if (filter.type && filter.type !== 'all') {
      if (file.type === 'file' && file.fileType !== filter.type) {
        return null;
      }
    }

    // Check K-Block filter
    if (filter.hasKBlock !== undefined) {
      if (file.type === 'file' && filter.hasKBlock && !file.kblockId) {
        return null;
      }
    }

    // Check drift filter
    if (filter.hasDrift !== undefined) {
      if (file.type === 'file' && filter.hasDrift && !file.hasDrift) {
        return null;
      }
    }

    // Check search query
    if (filter.searchQuery) {
      const query = filter.searchQuery.toLowerCase();
      if (!file.name.toLowerCase().includes(query) && !file.path.toLowerCase().includes(query)) {
        // If directory, check if any children match
        if (file.type === 'directory' && file.children) {
          const filteredChildren = filterFiles(file.children, filter);
          if (filteredChildren.length > 0) {
            return { ...file, children: filteredChildren };
          }
        }
        return null;
      }
    }

    // Recursively filter children
    if (file.type === 'directory' && file.children) {
      const filteredChildren = filterFiles(file.children, filter);
      return { ...file, children: filteredChildren };
    }

    return file;
  };

  return files.map(filterFile).filter((f): f is CodebaseFile => f !== null);
}

// =============================================================================
// Component
// =============================================================================

export const CodebaseExplorer = memo(function CodebaseExplorer({
  onFileSelect,
  selectedPath,
  filter = {},
  onFilterChange,
}: CodebaseExplorerProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [expandedPaths, setExpandedPaths] = useState<Set<string>>(
    new Set(['spec/', 'impl/', 'docs/'])
  );
  const [searchQuery, setSearchQuery] = useState(filter.searchQuery || '');
  const [showFilters, setShowFilters] = useState(false);
  const [selectedIndex, setSelectedIndex] = useState(0);

  // Combine local search with external filter
  const activeFilter: CodebaseFilter = useMemo(
    () => ({ ...filter, searchQuery }),
    [filter, searchQuery]
  );

  // Filter and flatten tree
  const filteredFiles = useMemo(() => filterFiles(MOCK_CODEBASE, activeFilter), [activeFilter]);

  const visibleNodes = useMemo(
    () => flattenTree(filteredFiles, expandedPaths),
    [filteredFiles, expandedPaths]
  );

  // Toggle expand/collapse
  const toggleExpand = useCallback((path: string) => {
    setExpandedPaths((prev) => {
      const next = new Set(prev);
      if (next.has(path)) {
        next.delete(path);
      } else {
        next.add(path);
      }
      return next;
    });
  }, []);

  // Handle node click
  const handleNodeClick = useCallback(
    (file: CodebaseFile) => {
      if (file.type === 'directory') {
        toggleExpand(file.path);
      } else {
        onFileSelect(file.path);
      }
    },
    [onFileSelect, toggleExpand]
  );

  // Keyboard navigation
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (!containerRef.current?.contains(document.activeElement)) return;

      const node = visibleNodes[selectedIndex];

      switch (e.key) {
        case 'j':
        case 'ArrowDown':
          e.preventDefault();
          setSelectedIndex((prev) => Math.min(prev + 1, visibleNodes.length - 1));
          break;

        case 'k':
        case 'ArrowUp':
          e.preventDefault();
          setSelectedIndex((prev) => Math.max(prev - 1, 0));
          break;

        case 'Enter':
          e.preventDefault();
          if (node) {
            handleNodeClick(node.file);
          }
          break;

        case 'h':
        case 'ArrowLeft':
          e.preventDefault();
          if (node?.file.type === 'directory' && expandedPaths.has(node.file.path)) {
            toggleExpand(node.file.path);
          }
          break;

        case 'l':
        case 'ArrowRight':
          e.preventDefault();
          if (node?.file.type === 'directory' && !expandedPaths.has(node.file.path)) {
            toggleExpand(node.file.path);
          }
          break;

        case '/': {
          e.preventDefault();
          const searchInput = containerRef.current?.querySelector('input');
          searchInput?.focus();
          break;
        }
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [visibleNodes, selectedIndex, expandedPaths, handleNodeClick, toggleExpand]);

  // Scroll selected into view
  useEffect(() => {
    const selectedEl = containerRef.current?.querySelector('[data-selected="true"]');
    selectedEl?.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
  }, [selectedIndex]);

  return (
    <div ref={containerRef} className="codebase-explorer" tabIndex={0}>
      {/* Header */}
      <div className="codebase-explorer__header">
        <Layers size={14} className="codebase-explorer__icon" />
        <span className="codebase-explorer__title">Codebase</span>
        <button
          className="codebase-explorer__filter-btn"
          onClick={() => setShowFilters(!showFilters)}
          aria-label="Toggle filters"
        >
          <Filter size={12} />
        </button>
      </div>

      {/* Search */}
      <div className="codebase-explorer__search">
        <Search size={12} className="codebase-explorer__search-icon" />
        <input
          type="text"
          className="codebase-explorer__search-input"
          placeholder="Search files... (press /)"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
        />
      </div>

      {/* Filters (collapsible) */}
      {showFilters && (
        <div className="codebase-explorer__filters">
          <label className="codebase-explorer__filter">
            <input
              type="checkbox"
              checked={filter.hasKBlock ?? false}
              onChange={(e) =>
                onFilterChange?.({ ...filter, hasKBlock: e.target.checked || undefined })
              }
            />
            <span>Has K-Block</span>
          </label>
          <label className="codebase-explorer__filter">
            <input
              type="checkbox"
              checked={filter.hasDrift ?? false}
              onChange={(e) =>
                onFilterChange?.({ ...filter, hasDrift: e.target.checked || undefined })
              }
            />
            <span>Has Drift</span>
          </label>
          <div className="codebase-explorer__filter-type">
            <button
              className={`codebase-explorer__type-btn ${!filter.type || filter.type === 'all' ? 'active' : ''}`}
              onClick={() => onFilterChange?.({ ...filter, type: 'all' })}
            >
              All
            </button>
            <button
              className={`codebase-explorer__type-btn ${filter.type === 'spec' ? 'active' : ''}`}
              onClick={() => onFilterChange?.({ ...filter, type: 'spec' })}
            >
              Spec
            </button>
            <button
              className={`codebase-explorer__type-btn ${filter.type === 'impl' ? 'active' : ''}`}
              onClick={() => onFilterChange?.({ ...filter, type: 'impl' })}
            >
              Impl
            </button>
          </div>
        </div>
      )}

      {/* File Tree */}
      <div className="codebase-explorer__tree">
        {visibleNodes.length === 0 ? (
          <div className="codebase-explorer__empty">
            {searchQuery ? `No files matching "${searchQuery}"` : 'No files'}
          </div>
        ) : (
          visibleNodes.map(({ file, depth }, index) => {
            const isExpanded = expandedPaths.has(file.path);
            const isSelected = index === selectedIndex;
            const isCurrent = file.path === selectedPath;

            return (
              <button
                key={file.path}
                className="codebase-explorer__node"
                data-selected={isSelected}
                data-current={isCurrent}
                data-type={file.type}
                onClick={() => handleNodeClick(file)}
                style={{ '--depth': depth } as React.CSSProperties}
              >
                {/* Indent */}
                <div className="codebase-explorer__indent" />

                {/* Chevron for directories */}
                {file.type === 'directory' && (
                  <div className="codebase-explorer__chevron" data-expanded={isExpanded}>
                    <ChevronRight size={10} />
                  </div>
                )}

                {/* Icon */}
                <div className="codebase-explorer__node-icon">{getFileIcon(file, isExpanded)}</div>

                {/* Name */}
                <span className="codebase-explorer__node-name">{file.name}</span>

                {/* Badges */}
                <div className="codebase-explorer__badges">
                  {/* Layer badge */}
                  {file.layer !== undefined && (
                    <span
                      className="codebase-explorer__badge codebase-explorer__badge--layer"
                      style={{ color: LAYER_COLORS[file.layer] }}
                    >
                      L{file.layer}
                    </span>
                  )}

                  {/* Drift indicator */}
                  {file.hasDrift && (
                    <span className="codebase-explorer__badge codebase-explorer__badge--drift">
                      <AlertTriangle size={10} />
                    </span>
                  )}

                  {/* Recently modified */}
                  {file.modifiedAt && (
                    <span className="codebase-explorer__badge codebase-explorer__badge--modified">
                      <Clock size={10} />
                    </span>
                  )}
                </div>
              </button>
            );
          })
        )}
      </div>
    </div>
  );
});

export default CodebaseExplorer;
