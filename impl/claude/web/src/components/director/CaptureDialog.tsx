/**
 * CaptureDialog - Modal for capturing execution results
 *
 * Features:
 * - File upload via drag & drop or file picker
 * - Test results input (passed/failed)
 * - Preview of what will be captured
 * - Calls captureExecution API
 * - Shows success state with evidence marks created
 *
 * Philosophy:
 *   "Upload → Analyze → Generate → Execute → **Capture** → Verify"
 */

import { useCallback, useState, type DragEvent, type ChangeEvent } from 'react';

import { captureExecution, type CaptureRequest, type CaptureResponse } from '../../api/director';

import './CaptureDialog.css';

// =============================================================================
// Types
// =============================================================================

interface CaptureDialogProps {
  specPath: string;
  onClose: () => void;
  onSuccess?: () => void;
}

interface UploadedFile {
  targetPath: string;
  content: string;
  size: number;
}

// =============================================================================
// Component
// =============================================================================

export function CaptureDialog({ specPath, onClose, onSuccess }: CaptureDialogProps) {
  // File state
  const [files, setFiles] = useState<UploadedFile[]>([]);
  const [dragActive, setDragActive] = useState(false);

  // Test results state
  const [passedTests, setPassedTests] = useState('');
  const [failedTests, setFailedTests] = useState('');

  // UI state
  const [capturing, setCapturing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<CaptureResponse | null>(null);

  // ============================================================================
  // File handling
  // ============================================================================

  const handleDrag = useCallback((e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();

    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  }, []);

  const handleDrop = useCallback(
    (e: DragEvent<HTMLDivElement>) => {
      e.preventDefault();
      e.stopPropagation();
      setDragActive(false);

      if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
        handleFiles(e.dataTransfer.files);
      }
    },
    [files]
  );

  const handleFileInput = useCallback(
    (e: ChangeEvent<HTMLInputElement>) => {
      if (e.target.files && e.target.files.length > 0) {
        handleFiles(e.target.files);
      }
    },
    [files]
  );

  const handleFiles = useCallback(
    async (fileList: FileList) => {
      const newFiles: UploadedFile[] = [];

      for (let i = 0; i < fileList.length; i++) {
        const file = fileList[i];

        try {
          const content = await file.text();
          newFiles.push({
            targetPath: file.name, // User can edit this
            content,
            size: file.size,
          });
        } catch (err) {
          console.error('Failed to read file:', file.name, err);
        }
      }

      setFiles((prev) => [...prev, ...newFiles]);
    },
    [files]
  );

  const removeFile = useCallback((index: number) => {
    setFiles((prev) => prev.filter((_, i) => i !== index));
  }, []);

  const updateFilePath = useCallback((index: number, newPath: string) => {
    setFiles((prev) =>
      prev.map((file, i) => (i === index ? { ...file, targetPath: newPath } : file))
    );
  }, []);

  // ============================================================================
  // Test results parsing
  // ============================================================================

  const parseTestList = (input: string): string[] => {
    if (!input.trim()) return [];

    // Handle comma-separated or newline-separated
    const lines = input.split(/[\n,]/).map((s) => s.trim());
    return lines.filter((s) => s.length > 0);
  };

  // ============================================================================
  // Capture logic
  // ============================================================================

  const handleCapture = useCallback(async () => {
    setCapturing(true);
    setError(null);

    try {
      // Build generated_files map
      const generatedFiles: Record<string, string> = {};
      for (const file of files) {
        generatedFiles[file.targetPath] = file.content;
      }

      // Parse test results
      const passed = parseTestList(passedTests);
      const failed = parseTestList(failedTests);

      // Build test_results.by_file (simple heuristic: group by filename prefix)
      const byFile: Record<string, { passed: number; failed: number }> = {};

      // For now, just aggregate totals — backend will parse intelligently
      if (files.length > 0) {
        for (const file of files) {
          byFile[file.targetPath] = { passed: 0, failed: 0 };
        }

        // Distribute test counts (simple: all passed, all failed)
        const firstFile = files[0].targetPath;
        if (byFile[firstFile]) {
          byFile[firstFile].passed = passed.length;
          byFile[firstFile].failed = failed.length;
        }
      }

      const request: CaptureRequest = {
        spec_path: specPath,
        generated_files: generatedFiles,
        test_results: {
          passed,
          failed,
          by_file: byFile,
        },
      };

      const response = await captureExecution(request);
      setSuccess(response);

      // Call onSuccess after short delay
      if (onSuccess) {
        setTimeout(() => {
          onSuccess();
        }, 1500);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to capture execution');
    } finally {
      setCapturing(false);
    }
  }, [specPath, files, passedTests, failedTests, onSuccess]);

  // ============================================================================
  // Validation
  // ============================================================================

  const canCapture = files.length > 0 && !capturing && !success;

  // ============================================================================
  // Render
  // ============================================================================

  return (
    <div className="capture-dialog__overlay" onClick={onClose}>
      <div className="capture-dialog" onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <header className="capture-dialog__header">
          <h2 className="capture-dialog__title">CAPTURE EXECUTION RESULTS</h2>
          <button className="capture-dialog__close" onClick={onClose} aria-label="Close">
            ×
          </button>
        </header>

        {/* Success State */}
        {success && (
          <div className="capture-dialog__success">
            <div className="capture-dialog__success-icon">✓</div>
            <h3 className="capture-dialog__success-title">Captured Successfully</h3>
            <div className="capture-dialog__success-stats">
              <div className="capture-dialog__success-stat">
                <span className="capture-dialog__success-stat-value">
                  {success.captured_count}
                </span>
                <span className="capture-dialog__success-stat-label">Files Captured</span>
              </div>
              <div className="capture-dialog__success-stat">
                <span className="capture-dialog__success-stat-value">
                  {success.evidence_marks_created}
                </span>
                <span className="capture-dialog__success-stat-label">Evidence Marks Created</span>
              </div>
            </div>
            <p className="capture-dialog__success-message">
              Results for <code>{success.spec_path}</code> have been captured.
            </p>
          </div>
        )}

        {/* Form State */}
        {!success && (
          <>
            <div className="capture-dialog__body">
              {/* Spec Path */}
              <div className="capture-dialog__field">
                <label className="capture-dialog__label">Spec Path</label>
                <div className="capture-dialog__spec-path">{specPath}</div>
              </div>

              {/* File Upload */}
              <div className="capture-dialog__field">
                <label className="capture-dialog__label">Generated Files</label>
                <div
                  className={`capture-dialog__dropzone ${dragActive ? 'capture-dialog__dropzone--active' : ''}`}
                  onDragEnter={handleDrag}
                  onDragLeave={handleDrag}
                  onDragOver={handleDrag}
                  onDrop={handleDrop}
                >
                  <div className="capture-dialog__dropzone-content">
                    <span className="capture-dialog__dropzone-icon">📁</span>
                    <p className="capture-dialog__dropzone-text">
                      Drag & drop files here, or{' '}
                      <label className="capture-dialog__dropzone-browse">
                        browse
                        <input
                          type="file"
                          multiple
                          onChange={handleFileInput}
                          className="capture-dialog__file-input"
                        />
                      </label>
                    </p>
                  </div>
                </div>

                {/* File List */}
                {files.length > 0 && (
                  <ul className="capture-dialog__file-list">
                    {files.map((file, index) => (
                      <li key={index} className="capture-dialog__file-item">
                        <input
                          type="text"
                          className="capture-dialog__file-path"
                          value={file.targetPath}
                          onChange={(e) => updateFilePath(index, e.target.value)}
                          placeholder="target/path/file.py"
                        />
                        <span className="capture-dialog__file-size">
                          {(file.size / 1024).toFixed(1)} KB
                        </span>
                        <button
                          className="capture-dialog__file-remove"
                          onClick={() => removeFile(index)}
                          aria-label="Remove file"
                        >
                          ×
                        </button>
                      </li>
                    ))}
                  </ul>
                )}
              </div>

              {/* Test Results */}
              <div className="capture-dialog__field">
                <label className="capture-dialog__label">Passed Tests</label>
                <textarea
                  className="capture-dialog__textarea"
                  value={passedTests}
                  onChange={(e) => setPassedTests(e.target.value)}
                  placeholder="test_basic_functionality, test_edge_cases&#10;or comma-separated: test_one, test_two"
                  rows={3}
                />
              </div>

              <div className="capture-dialog__field">
                <label className="capture-dialog__label">Failed Tests</label>
                <textarea
                  className="capture-dialog__textarea"
                  value={failedTests}
                  onChange={(e) => setFailedTests(e.target.value)}
                  placeholder="test_broken_feature&#10;(leave empty if all tests passed)"
                  rows={3}
                />
              </div>

              {/* Preview */}
              {files.length > 0 && (
                <div className="capture-dialog__preview">
                  <h3 className="capture-dialog__preview-title">Preview</h3>
                  <div className="capture-dialog__preview-content">
                    <p>
                      <strong>{files.length}</strong> file{files.length > 1 ? 's' : ''} will be
                      captured
                    </p>
                    <p>
                      <strong>{parseTestList(passedTests).length}</strong> passed test
                      {parseTestList(passedTests).length !== 1 ? 's' : ''}
                    </p>
                    <p>
                      <strong>{parseTestList(failedTests).length}</strong> failed test
                      {parseTestList(failedTests).length !== 1 ? 's' : ''}
                    </p>
                  </div>
                </div>
              )}
            </div>

            {/* Error */}
            {error && <div className="capture-dialog__error">{error}</div>}

            {/* Actions */}
            <footer className="capture-dialog__actions">
              <button className="capture-dialog__btn" onClick={onClose} disabled={capturing}>
                Cancel
              </button>
              <button
                className="capture-dialog__btn capture-dialog__btn--primary"
                onClick={handleCapture}
                disabled={!canCapture}
              >
                {capturing ? 'Capturing...' : 'Capture'}
              </button>
            </footer>
          </>
        )}
      </div>
    </div>
  );
}
