/**
 * UploadStatusBadge — Visual indicator for file upload/analysis status
 *
 * Shows the current state of an uploaded document:
 * - uploading: File being sent to server
 * - processing: Server analyzing the document
 * - ready: Analysis complete (badge hidden)
 * - failed: Upload or processing failed
 *
 * "The proof IS the decision. The mark IS the witness."
 */

import './UploadStatusBadge.css';

/**
 * Upload status states - mirrors the type in useFileUpload.ts
 */
export type UploadStatus = 'uploading' | 'processing' | 'ready' | 'failed';

interface UploadStatusBadgeProps {
  status?: UploadStatus;
  className?: string;
}

/**
 * Displays a status badge for file upload/analysis progress.
 * Returns null when status is 'ready' or undefined (no visual indicator needed).
 */
export function UploadStatusBadge({ status, className = '' }: UploadStatusBadgeProps) {
  // No badge needed when ready or undefined
  if (!status || status === 'ready') {
    return null;
  }

  const statusText: Record<Exclude<UploadStatus, 'ready'>, string> = {
    uploading: 'Uploading...',
    processing: 'Analyzing...',
    failed: 'Failed',
  };

  return (
    <span
      className={`upload-status-badge ${className}`.trim()}
      data-status={status}
      role="status"
      aria-live="polite"
    >
      {statusText[status]}
    </span>
  );
}

export default UploadStatusBadge;
