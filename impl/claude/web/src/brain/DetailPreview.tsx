/**
 * DetailPreview — Temporary detail view for unified events
 *
 * Phase 2 will replace this with type-specific views:
 * - MarkDetail
 * - CrystalDetail
 * - TrailDetail
 * - EvidenceDetail
 */

import type { UnifiedEvent } from './types';
import './DetailPreview.css';

interface DetailPreviewProps {
  event: UnifiedEvent;
}

export function DetailPreview({ event }: DetailPreviewProps) {
  return (
    <div className="detail-preview">
      <div className="detail-preview__section">
        <h3 className="detail-preview__label">Type</h3>
        <p className="detail-preview__value">{event.type}</p>
      </div>

      <div className="detail-preview__section">
        <h3 className="detail-preview__label">Summary</h3>
        <p className="detail-preview__value">{event.summary}</p>
      </div>

      <div className="detail-preview__section">
        <h3 className="detail-preview__label">Timestamp</h3>
        <p className="detail-preview__value">{new Date(event.timestamp).toLocaleString()}</p>
      </div>

      <div className="detail-preview__section">
        <h3 className="detail-preview__label">Metadata</h3>
        <pre className="detail-preview__json">{JSON.stringify(event.metadata, null, 2)}</pre>
      </div>

      <div className="detail-preview__actions">
        <p className="detail-preview__hint">Full detail views coming in Phase 2</p>
      </div>
    </div>
  );
}
