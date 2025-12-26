/**
 * UploadZone — Drag-drop upload zone for uploads/ folder
 *
 * "Sovereignty before integration. The staging area is sacred."
 *
 * Features:
 * - Drag-drop file upload
 * - Visual feedback on drag over
 * - Upload progress indicator
 * - Click to browse fallback
 *
 * Philosophy: Files enter through uploads/ as sovereign entities.
 * They wait in the staging area until ready for integration.
 */

import { memo, useCallback, useState, useRef } from 'react';
import { Upload, File, CheckCircle, XCircle } from 'lucide-react';
import './FileExplorer.css';

// =============================================================================
// Types
// =============================================================================

interface UploadZoneProps {
  /** Called when upload completes */
  onUploadComplete?: (files: File[]) => void;
  /** Maximum file size in MB (default: 10) */
  maxSizeMB?: number;
  /** Allowed file extensions (default: all) */
  allowedExtensions?: string[];
}

interface UploadingFile {
  file: File;
  progress: number;
  status: 'uploading' | 'success' | 'error';
  error?: string;
}

// =============================================================================
// Component
// =============================================================================

export const UploadZone = memo(function UploadZone({
  onUploadComplete: _onUploadComplete,
  maxSizeMB = 10,
  allowedExtensions,
}: UploadZoneProps) {
  // TODO: Wire onUploadComplete when backend integration is ready
  void _onUploadComplete;
  const [isDragging, setIsDragging] = useState(false);
  const [uploadingFiles, setUploadingFiles] = useState<UploadingFile[]>([]);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // =============================================================================
  // Handlers
  // =============================================================================

  /**
   * Handle drag enter.
   */
  const handleDragEnter = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  }, []);

  /**
   * Handle drag over.
   */
  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    e.dataTransfer.dropEffect = 'copy';
  }, []);

  /**
   * Handle drag leave.
   */
  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  }, []);

  /**
   * Handle drop.
   */
  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      e.stopPropagation();
      setIsDragging(false);

      const files = Array.from(e.dataTransfer.files);
      handleFiles(files);
    },
    [maxSizeMB, allowedExtensions]
  );

  /**
   * Handle file input change.
   */
  const handleFileInputChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const files = Array.from(e.target.files || []);
      handleFiles(files);
    },
    [maxSizeMB, allowedExtensions]
  );

  /**
   * Handle files (validate and upload).
   */
  const handleFiles = useCallback(
    (files: File[]) => {
      const validFiles: File[] = [];
      const initialUploadingFiles: UploadingFile[] = [];

      for (const file of files) {
        // Validate file size
        if (file.size > maxSizeMB * 1024 * 1024) {
          initialUploadingFiles.push({
            file,
            progress: 0,
            status: 'error',
            error: `File too large (max ${maxSizeMB}MB)`,
          });
          continue;
        }

        // Validate file extension
        if (allowedExtensions) {
          const ext = file.name.split('.').pop()?.toLowerCase();
          if (!ext || !allowedExtensions.includes(ext)) {
            initialUploadingFiles.push({
              file,
              progress: 0,
              status: 'error',
              error: `Invalid file type (allowed: ${allowedExtensions.join(', ')})`,
            });
            continue;
          }
        }

        validFiles.push(file);
        initialUploadingFiles.push({
          file,
          progress: 0,
          status: 'uploading',
        });
      }

      setUploadingFiles(initialUploadingFiles);

      // Upload valid files
      validFiles.forEach((file, index) => {
        uploadFile(file, index);
      });
    },
    [maxSizeMB, allowedExtensions]
  );

  /**
   * Upload a single file.
   */
  const uploadFile = useCallback(
    async (file: File, index: number) => {
      try {
        // Create FormData with file
        const formData = new FormData();
        formData.append('file', file);

        // Upload to sovereign API
        const response = await fetch('/api/sovereign/upload', {
          method: 'POST',
          body: formData,
        });

        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.detail || 'Upload failed');
        }

        const result = await response.json();

        // Mark as success
        setUploadingFiles((prev) =>
          prev.map((uf, i) =>
            i === index ? { ...uf, status: 'success', progress: 100 } : uf
          )
        );

        console.log('[UploadZone] Upload complete:', {
          filename: file.name,
          path: result.path,
          version: result.version,
          mark_id: result.ingest_mark_id,
          edges: result.edge_count,
        });
      } catch (error) {
        console.error('[UploadZone] Upload failed:', error);
        setUploadingFiles((prev) =>
          prev.map((uf, i) =>
            i === index
              ? {
                  ...uf,
                  status: 'error',
                  error: error instanceof Error ? error.message : 'Upload failed',
                }
              : uf
          )
        );
      }
    },
    []
  );

  /**
   * Trigger file input click.
   */
  const handleClick = useCallback(() => {
    fileInputRef.current?.click();
  }, []);

  // =============================================================================
  // Render
  // =============================================================================

  const hasUploads = uploadingFiles.length > 0;

  return (
    <div className="upload-zone">
      {/* Drop zone */}
      <div
        className="upload-zone__drop-area"
        data-dragging={isDragging}
        onDragEnter={handleDragEnter}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={handleClick}
      >
        <div className="upload-zone__icon">
          <Upload size={24} />
        </div>
        <div className="upload-zone__text">
          {isDragging ? 'Drop files here' : 'Drop files or click to browse'}
        </div>
        <div className="upload-zone__hint">
          Sovereign staging area • Max {maxSizeMB}MB
        </div>
      </div>

      {/* Hidden file input */}
      <input
        ref={fileInputRef}
        type="file"
        multiple
        className="upload-zone__file-input"
        onChange={handleFileInputChange}
        accept={allowedExtensions ? allowedExtensions.map((ext) => `.${ext}`).join(',') : undefined}
      />

      {/* Upload progress list */}
      {hasUploads && (
        <div className="upload-zone__progress-list">
          {uploadingFiles.map((uf, index) => (
            <div
              key={index}
              className="upload-zone__progress-item"
              data-status={uf.status}
            >
              <div className="upload-zone__progress-icon">
                {uf.status === 'uploading' && <File size={16} />}
                {uf.status === 'success' && <CheckCircle size={16} />}
                {uf.status === 'error' && <XCircle size={16} />}
              </div>

              <div className="upload-zone__progress-info">
                <div className="upload-zone__progress-name">{uf.file.name}</div>
                {uf.status === 'uploading' && (
                  <div className="upload-zone__progress-bar">
                    <div
                      className="upload-zone__progress-bar-fill"
                      style={{ width: `${uf.progress}%` }}
                    />
                  </div>
                )}
                {uf.status === 'error' && (
                  <div className="upload-zone__progress-error">{uf.error}</div>
                )}
                {uf.status === 'success' && (
                  <div className="upload-zone__progress-success">Uploaded</div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
});
