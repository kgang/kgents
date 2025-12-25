/**
 * FileSidebar — Left sidebar for file navigation
 *
 * "Daring, bold, creative, opinionated but not gaudy"
 * "STARK BIOME: 90% steel, 10% earned glow"
 *
 * Layout:
 * ┌──────────────────────────────────┐
 * │ [🔍 Search...        ] [⬆️] [📂] │  ← Search + Upload + Browse modal
 * ├──────────────────────────────────┤
 * │ RECENT                   [Clear] │
 * │ ┌──────────────────────────────┐ │
 * │ │ 📄 README.md              → │ │
 * │ │ 📄 App.tsx                → │ │
 * │ └──────────────────────────────┘ │
 * ├──────────────────────────────────┤
 * │ {children}                       │  ← FileTree component
 * ├──────────────────────────────────┤
 * │ <kbd>Ctrl+O</kbd> Browse all     │
 * └──────────────────────────────────┘
 */

import { memo, useCallback, useRef, useState } from 'react';
import { Search, Upload, FolderOpen, FileText } from 'lucide-react';
import type { UploadedFile } from './types';
import './FileSidebar.css';

// =============================================================================
// Types
// =============================================================================

export interface FileSidebarProps {
  /** Called when user opens a file */
  onOpenFile: (path: string) => void;

  /** Called when user uploads a file (optional) */
  onUploadFile?: (file: UploadedFile) => void;

  /** Recent files to display (optional) */
  recentFiles?: string[];

  /** Called when user clears recent files (optional) */
  onClearRecent?: () => void;

  /** Called when user clicks "Browse all" to open modal (optional) */
  onOpenBrowseModal?: () => void;

  /** FileTree component to render in the tree slot (optional) */
  children?: React.ReactNode;
}

// =============================================================================
// Helpers
// =============================================================================

/**
 * Extract filename from path
 */
function getFileName(path: string): string {
  return path.split('/').pop() || path;
}

// =============================================================================
// Main Component
// =============================================================================

export const FileSidebar = memo(function FileSidebar({
  onOpenFile,
  onUploadFile,
  recentFiles = [],
  onClearRecent,
  onOpenBrowseModal,
  children,
}: FileSidebarProps) {
  const [searchQuery, setSearchQuery] = useState('');
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Read file content and emit
  const readFileContent = useCallback(
    (file: File) => {
      if (!onUploadFile) return;

      const reader = new FileReader();
      reader.onload = (e) => {
        const content = e.target?.result as string;
        onUploadFile({
          name: file.name,
          content: content || '',
          type: file.type || 'text/plain',
        });
      };
      reader.onerror = () => {
        console.warn('[FileSidebar] Failed to read file:', file.name);
      };
      reader.readAsText(file);
    },
    [onUploadFile]
  );

  // Handle file input change
  const handleFileSelect = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      if (!onUploadFile || !e.target.files?.length) return;
      readFileContent(e.target.files[0]);
      // Reset input so same file can be uploaded again
      e.target.value = '';
    },
    [onUploadFile, readFileContent]
  );

  // Trigger file input click
  const handleUploadClick = useCallback(() => {
    fileInputRef.current?.click();
  }, []);

  // Handle drag and drop
  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      if (!onUploadFile) return;

      const files = Array.from(e.dataTransfer.files);
      if (files.length > 0) {
        readFileContent(files[0]);
      }
    },
    [onUploadFile, readFileContent]
  );

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
  }, []);

  return (
    <aside
      className="file-sidebar"
      onDrop={handleDrop}
      onDragOver={handleDragOver}
    >
      {/* Quick Actions Bar */}
      <div className="file-sidebar__actions">
        <div className="file-sidebar__search">
          <Search size={14} className="file-sidebar__search-icon" />
          <input
            type="text"
            className="file-sidebar__search-input"
            placeholder="Search..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>

        {/* Hidden file input */}
        {onUploadFile && (
          <input
            ref={fileInputRef}
            type="file"
            className="file-sidebar__file-input"
            onChange={handleFileSelect}
            accept=".md,.txt,.py,.ts,.tsx,.js,.jsx,.json,.yaml,.yml"
          />
        )}

        {/* Upload button */}
        {onUploadFile && (
          <button
            className="file-sidebar__action-btn"
            onClick={handleUploadClick}
            title="Upload file"
            aria-label="Upload file"
          >
            <Upload size={16} strokeWidth={1.5} />
          </button>
        )}

        {/* Browse modal trigger */}
        {onOpenBrowseModal && (
          <button
            className="file-sidebar__action-btn"
            onClick={onOpenBrowseModal}
            title="Browse all (Ctrl+O)"
            aria-label="Browse all files"
          >
            <FolderOpen size={16} strokeWidth={1.5} />
          </button>
        )}
      </div>

      {/* Recent Files */}
      {recentFiles.length > 0 && (
        <div className="file-sidebar__section">
          <div className="file-sidebar__section-header">
            <span className="file-sidebar__section-title">RECENT</span>
            {onClearRecent && (
              <button
                className="file-sidebar__clear-btn"
                onClick={onClearRecent}
                title="Clear recent files"
              >
                Clear
              </button>
            )}
          </div>
          <ul className="file-sidebar__file-list">
            {recentFiles.slice(0, 5).map((path) => (
              <li key={path}>
                <button
                  className="file-sidebar__file-item"
                  onClick={() => onOpenFile(path)}
                  title={path}
                >
                  <FileText size={14} className="file-sidebar__file-icon" strokeWidth={1.5} />
                  <span className="file-sidebar__file-name">{getFileName(path)}</span>
                  <span className="file-sidebar__file-arrow">→</span>
                </button>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* FileTree Slot */}
      {children && (
        <div className="file-sidebar__tree-slot">
          {children}
        </div>
      )}

      {/* Empty State - shown when no recent files and no tree */}
      {recentFiles.length === 0 && !children && (
        <div className="file-sidebar__empty">
          <p className="file-sidebar__empty-text">No recent files</p>
          <p className="file-sidebar__empty-hint">Files you open will appear here</p>
        </div>
      )}

      {/* Footer with Browse All hint */}
      {onOpenBrowseModal && (
        <div className="file-sidebar__footer">
          <button
            className="file-sidebar__browse-hint"
            onClick={onOpenBrowseModal}
          >
            <kbd>Ctrl+O</kbd> Browse all
          </button>
        </div>
      )}
    </aside>
  );
});
