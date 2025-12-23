/**
 * FileExplorer — Default view when no file is selected
 *
 * STARK BIOME: "Stillness, then life" — 90% calm, 10% delight.
 * "The frame is humble. The content glows."
 *
 * A minimal, tasteful invitation to:
 * - Open an existing file by path
 * - Upload a new file
 * - Select from recent files (if any)
 */

import { memo, useCallback, useRef, useState } from 'react';
import { Upload, FileText, FolderOpen, ArrowRight } from 'lucide-react';

import './FileExplorer.css';

// =============================================================================
// Types
// =============================================================================

/** Uploaded file with content */
export interface UploadedFile {
  name: string;
  content: string;
  type: string;
}

interface FileExplorerProps {
  /** Called when user wants to open a file by path */
  onOpenFile: (path: string) => void;
  /** Called when user uploads a file (with content) */
  onUploadFile?: (file: UploadedFile) => void;
  /** Recent files to display (optional) */
  recentFiles?: string[];
  /** Whether file upload is enabled */
  uploadEnabled?: boolean;
}

// =============================================================================
// Main Component
// =============================================================================

export const FileExplorer = memo(function FileExplorer({
  onOpenFile,
  onUploadFile,
  recentFiles = [],
  uploadEnabled = true,
}: FileExplorerProps) {
  const [pathInput, setPathInput] = useState('');
  const [isDragging, setIsDragging] = useState(false);
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
        console.warn('[FileExplorer] Failed to read file:', file.name);
      };
      reader.readAsText(file);
    },
    [onUploadFile]
  );

  // Handle file drop
  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setIsDragging(false);

      if (!uploadEnabled || !onUploadFile) return;

      const files = Array.from(e.dataTransfer.files);
      if (files.length > 0) {
        readFileContent(files[0]);
      }
    },
    [uploadEnabled, onUploadFile, readFileContent]
  );

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  // Handle path submission
  const handleSubmit = useCallback(
    (e: React.FormEvent) => {
      e.preventDefault();
      if (pathInput.trim()) {
        onOpenFile(pathInput.trim());
      }
    },
    [pathInput, onOpenFile]
  );

  // Handle file input change
  const handleFileSelect = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      if (!onUploadFile || !e.target.files?.length) return;
      readFileContent(e.target.files[0]);
    },
    [onUploadFile, readFileContent]
  );

  // Trigger file input click
  const handleUploadClick = useCallback(() => {
    fileInputRef.current?.click();
  }, []);

  return (
    <div
      className={`file-explorer ${isDragging ? 'file-explorer--dragging' : ''}`}
      onDrop={handleDrop}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
    >
      {/* Header */}
      <header className="file-explorer__header">
        <div className="file-explorer__icon">
          <FolderOpen size={32} strokeWidth={1.5} />
        </div>
        <h2 className="file-explorer__title">Open a File</h2>
        <p className="file-explorer__subtitle">Navigate into the graph by opening a file</p>
      </header>

      {/* Path Input */}
      <form className="file-explorer__form" onSubmit={handleSubmit}>
        <div className="file-explorer__input-group">
          <input
            type="text"
            className="file-explorer__input"
            placeholder="Enter file path..."
            value={pathInput}
            onChange={(e) => setPathInput(e.target.value)}
            autoFocus
          />
          <button
            type="submit"
            className="file-explorer__button file-explorer__button--primary"
            disabled={!pathInput.trim()}
          >
            <ArrowRight size={18} />
            <span>Open</span>
          </button>
        </div>
        <p className="file-explorer__hint">
          <kbd>:e</kbd> path or paste a file path above
        </p>
      </form>

      {/* Upload Zone */}
      {uploadEnabled && onUploadFile && (
        <div className="file-explorer__upload-zone">
          <input
            ref={fileInputRef}
            type="file"
            className="file-explorer__file-input"
            onChange={handleFileSelect}
            accept=".md,.txt,.py,.ts,.tsx,.js,.jsx,.json,.yaml,.yml"
          />
          <button
            className="file-explorer__upload-button"
            onClick={handleUploadClick}
            type="button"
          >
            <Upload size={20} strokeWidth={1.5} />
            <span>Upload File</span>
          </button>
          <p className="file-explorer__upload-hint">or drag and drop</p>
        </div>
      )}

      {/* Recent Files */}
      {recentFiles.length > 0 && (
        <div className="file-explorer__recent">
          <h3 className="file-explorer__recent-title">Recent</h3>
          <ul className="file-explorer__recent-list">
            {recentFiles.slice(0, 5).map((path) => (
              <li key={path}>
                <button className="file-explorer__recent-item" onClick={() => onOpenFile(path)}>
                  <FileText size={16} strokeWidth={1.5} />
                  <span className="file-explorer__recent-path">{path.split('/').pop()}</span>
                  <span className="file-explorer__recent-dir">
                    {path.split('/').slice(0, -1).join('/')}
                  </span>
                </button>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Empty State - shown when no recent files */}
      {recentFiles.length === 0 && (
        <div className="file-explorer__empty">
          <p className="file-explorer__empty-text">No recent files</p>
          <p className="file-explorer__empty-hint">Files you open will appear here</p>
        </div>
      )}

      {/* Keyboard Hints */}
      <footer className="file-explorer__footer">
        <div className="file-explorer__shortcuts">
          <span>
            <kbd>:e</kbd> open
          </span>
          <span>
            <kbd>Esc</kbd> cancel
          </span>
        </div>
      </footer>

      {/* Drag overlay */}
      {isDragging && (
        <div className="file-explorer__drag-overlay">
          <Upload size={48} strokeWidth={1} />
          <span>Drop to upload</span>
        </div>
      )}
    </div>
  );
});
