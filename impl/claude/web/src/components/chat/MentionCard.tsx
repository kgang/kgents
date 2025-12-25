/**
 * MentionCard — Renders injected context from @mentions
 *
 * "Collapsed card by default (icon + title), click to expand full content"
 *
 * States:
 * - Collapsed: Icon + title + dismiss button
 * - Expanded: Full content preview + dismiss button
 *
 * STARK BIOME: Steel frame, earned glow on hover
 *
 * @see spec/protocols/chat-web.md Part VI.2
 */

import { memo, useState } from 'react';
import { FileText, Code, BookOpen, Eye, Globe, Terminal, FolderTree, X, ChevronDown, ChevronRight } from 'lucide-react';
import type { MentionType } from './MentionPicker';
import './MentionCard.css';

// =============================================================================
// Types
// =============================================================================

export interface Mention {
  id: string;
  type: MentionType;
  value: string;
  label: string;
  content?: string; // Resolved content
  error?: string; // Error message if resolution failed
}

export interface MentionCardProps {
  /** The mention to render */
  mention: Mention;

  /** Callback to remove this mention */
  onDismiss: (id: string) => void;

  /** Initially expanded state */
  defaultExpanded?: boolean;
}

// =============================================================================
// Icons
// =============================================================================

const MENTION_ICONS: Record<MentionType, typeof FileText> = {
  file: FileText,
  symbol: Code,
  spec: BookOpen,
  witness: Eye,
  web: Globe,
  terminal: Terminal,
  project: FolderTree,
};

const MENTION_LABELS: Record<MentionType, string> = {
  file: 'File',
  symbol: 'Symbol',
  spec: 'Spec',
  witness: 'Witness',
  web: 'Web',
  terminal: 'Terminal',
  project: 'Project',
};

// =============================================================================
// Component
// =============================================================================

export const MentionCard = memo(function MentionCard({
  mention,
  onDismiss,
  defaultExpanded = false,
}: MentionCardProps) {
  const [isExpanded, setIsExpanded] = useState(defaultExpanded);

  const Icon = MENTION_ICONS[mention.type];
  const typeLabel = MENTION_LABELS[mention.type];

  const handleToggle = () => {
    setIsExpanded(!isExpanded);
  };

  const handleDismiss = (e: React.MouseEvent) => {
    e.stopPropagation();
    onDismiss(mention.id);
  };

  // Truncate content for preview
  const truncateContent = (content: string, maxLength = 200): string => {
    if (content.length <= maxLength) return content;
    return content.slice(0, maxLength) + '...';
  };

  return (
    <div className={`mention-card ${isExpanded ? 'mention-card--expanded' : ''}`}>
      {/* Header (always visible) */}
      <div className="mention-card__header" onClick={handleToggle}>
        <button className="mention-card__toggle" aria-label={isExpanded ? 'Collapse' : 'Expand'}>
          {isExpanded ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
        </button>

        <Icon size={16} className="mention-card__icon" />

        <div className="mention-card__title">
          <span className="mention-card__type">{typeLabel}</span>
          <span className="mention-card__value">{mention.value}</span>
        </div>

        <button
          className="mention-card__dismiss"
          onClick={handleDismiss}
          aria-label="Remove mention"
          title="Remove this mention"
        >
          <X size={14} />
        </button>
      </div>

      {/* Expanded content */}
      {isExpanded && (
        <div className="mention-card__content">
          {mention.error ? (
            <div className="mention-card__error">
              <span className="mention-card__error-icon">◆</span>
              {mention.error}
            </div>
          ) : mention.content ? (
            <pre className="mention-card__code">{mention.content}</pre>
          ) : (
            <div className="mention-card__loading">Loading...</div>
          )}
        </div>
      )}

      {/* Preview (collapsed state, if content available) */}
      {!isExpanded && mention.content && !mention.error && (
        <div className="mention-card__preview">
          {truncateContent(mention.content)}
        </div>
      )}
    </div>
  );
});

export default MentionCard;
