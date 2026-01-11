/**
 * MomentDetail - Expanded View of a Constitutional Moment
 *
 * Shows full details of a selected moment including:
 * - Full description and reasoning
 * - Diff view for amendments
 * - Link to git commit
 * - Related witnesses
 *
 * STARK BIOME: 90% steel, 10% earned amber glow.
 */

import { memo, useState } from 'react';
import {
  X,
  GitCommit,
  FileText,
  Link as LinkIcon,
  User,
  Clock,
  AlertTriangle,
  ChevronDown,
  ChevronRight,
  ExternalLink,
  Bookmark,
} from 'lucide-react';

import type { ConstitutionalMoment } from './types';
import {
  HISTORY_LAYER_COLORS,
  HISTORY_LAYER_NAMES,
  MOMENT_TYPE_LABELS,
  IMPACT_COLORS,
} from './types';

// =============================================================================
// Types
// =============================================================================

interface MomentDetailProps {
  moment: ConstitutionalMoment;
  onClose: () => void;
  onNavigateToKBlock: (path: string) => void;
  onNavigateToCommit: (sha: string) => void;
}

// =============================================================================
// Helpers
// =============================================================================

function formatDateTime(timestamp: string): string {
  const date = new Date(timestamp);
  return date.toLocaleDateString('en-US', {
    weekday: 'short',
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

// =============================================================================
// Diff View Component (mock for now)
// =============================================================================

interface DiffViewProps {
  before: string;
  after: string;
}

const DiffView = memo(function DiffView({ before, after }: DiffViewProps) {
  return (
    <div className="moment-diff">
      <div className="moment-diff__side moment-diff__side--before">
        <div className="moment-diff__header">Before</div>
        <pre className="moment-diff__content">{before}</pre>
      </div>
      <div className="moment-diff__side moment-diff__side--after">
        <div className="moment-diff__header">After</div>
        <pre className="moment-diff__content">{after}</pre>
      </div>
    </div>
  );
});

// =============================================================================
// Main Component
// =============================================================================

export const MomentDetail = memo(function MomentDetail({
  moment,
  onClose,
  onNavigateToKBlock,
  onNavigateToCommit,
}: MomentDetailProps) {
  const [showDiff, setShowDiff] = useState(false);
  const [showWitnesses, setShowWitnesses] = useState(false);

  const layerColor =
    HISTORY_LAYER_COLORS[moment.layer as keyof typeof HISTORY_LAYER_COLORS] ||
    HISTORY_LAYER_COLORS[4];
  const layerName =
    HISTORY_LAYER_NAMES[moment.layer as keyof typeof HISTORY_LAYER_NAMES] || 'IMPLEMENTATION';
  const impactColor = IMPACT_COLORS[moment.impact];

  // Mock diff data for amendments
  const mockDiff =
    moment.type === 'amendment'
      ? {
          before: `# ${moment.title}\n\nOriginal content before the amendment...`,
          after: `# ${moment.title}\n\nUpdated content after the amendment.\n\nNew section added.`,
        }
      : null;

  return (
    <div className="moment-detail">
      {/* Header */}
      <div className="moment-detail__header">
        <div className="moment-detail__header-left">
          <span
            className="moment-detail__layer-badge"
            style={{ color: layerColor, borderColor: layerColor }}
          >
            L{moment.layer} {layerName}
          </span>
          <span className="moment-detail__type">{MOMENT_TYPE_LABELS[moment.type]}</span>
        </div>
        <button className="moment-detail__close" onClick={onClose} aria-label="Close detail">
          <X size={16} />
        </button>
      </div>

      {/* Title and Impact */}
      <div className="moment-detail__title-area">
        <h2 className="moment-detail__title">{moment.title}</h2>
        <span
          className="moment-detail__impact"
          style={{ color: impactColor, borderColor: impactColor }}
        >
          {moment.impact === 'constitutional' && <AlertTriangle size={12} />}
          {moment.impact}
        </span>
      </div>

      {/* Metadata */}
      <div className="moment-detail__meta">
        <div className="moment-detail__meta-item">
          <Clock size={12} />
          <span>{formatDateTime(moment.timestamp)}</span>
        </div>
        {moment.author && (
          <div className="moment-detail__meta-item">
            <User size={12} />
            <span>{moment.author}</span>
          </div>
        )}
        {moment.commitSha && (
          <button
            className="moment-detail__meta-item moment-detail__meta-link"
            onClick={() => onNavigateToCommit(moment.commitSha!)}
          >
            <GitCommit size={12} />
            <span>{moment.commitSha.slice(0, 7)}</span>
            <ExternalLink size={10} />
          </button>
        )}
      </div>

      {/* K-Block Path */}
      <button
        className="moment-detail__kblock-link"
        onClick={() => onNavigateToKBlock(moment.kblockPath)}
      >
        <FileText size={14} />
        <span>{moment.kblockPath}</span>
        <LinkIcon size={10} />
      </button>

      {/* Description */}
      <div className="moment-detail__section">
        <h3 className="moment-detail__section-title">Description</h3>
        <p className="moment-detail__description">{moment.description}</p>
      </div>

      {/* Reasoning */}
      {moment.reasoning && (
        <div className="moment-detail__section">
          <h3 className="moment-detail__section-title">Reasoning</h3>
          <p className="moment-detail__reasoning">{moment.reasoning}</p>
        </div>
      )}

      {/* Amendment Diff (collapsible) */}
      {mockDiff && (
        <div className="moment-detail__section moment-detail__section--collapsible">
          <button className="moment-detail__section-toggle" onClick={() => setShowDiff(!showDiff)}>
            {showDiff ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
            <span>View Diff</span>
          </button>
          {showDiff && <DiffView before={mockDiff.before} after={mockDiff.after} />}
        </div>
      )}

      {/* Related Witnesses (collapsible) */}
      {moment.relatedMarks && moment.relatedMarks.length > 0 && (
        <div className="moment-detail__section moment-detail__section--collapsible">
          <button
            className="moment-detail__section-toggle"
            onClick={() => setShowWitnesses(!showWitnesses)}
          >
            {showWitnesses ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
            <span>Related Witnesses ({moment.relatedMarks.length})</span>
          </button>
          {showWitnesses && (
            <div className="moment-detail__witnesses">
              {moment.relatedMarks.map((markId) => (
                <div key={markId} className="moment-detail__witness">
                  <Bookmark size={12} />
                  <span className="moment-detail__witness-id">{markId}</span>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Amendment ID */}
      {moment.amendmentId && (
        <div className="moment-detail__amendment-id">
          Amendment ID: <code>{moment.amendmentId}</code>
        </div>
      )}
    </div>
  );
});
