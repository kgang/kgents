/**
 * UnifiedEventCard — Polymorphic card for Brain stream events
 *
 * "The proof IS the decision. The mark IS the witness."
 *
 * Renders any entity type with appropriate visual treatment:
 * - 🔖 Mark: Action, author, principles
 * - 💎 Crystal: Summary, access count, tags
 * - 🛤️ Trail: Name, steps, evidence strength
 * - ✓ Evidence: Status, agent path
 * - 📜 Teaching: Insight, severity, source
 * - 🧪 Lemma: Statement, checker, usage
 */

import { formatDistanceToNow } from 'date-fns';

import type {
  CrystalMetadata,
  EntityType,
  EvidenceMetadata,
  LemmaMetadata,
  MarkMetadata,
  TeachingMetadata,
  TrailMetadata,
  UnifiedEvent,
} from '../types';
import {
  ENTITY_BADGES,
  isCrystalMetadata,
  isEvidenceMetadata,
  isLemmaMetadata,
  isMarkMetadata,
  isTeachingMetadata,
  isTrailMetadata,
} from '../types';

import './UnifiedEventCard.css';

// =============================================================================
// Types
// =============================================================================

export interface UnifiedEventCardProps {
  /** The event to render */
  event: UnifiedEvent;

  /** Whether this card is selected */
  selected?: boolean;

  /** Click handler */
  onClick?: (event: UnifiedEvent) => void;

  /** Keyboard handler for accessibility */
  onKeyDown?: (e: React.KeyboardEvent, event: UnifiedEvent) => void;
}

// =============================================================================
// Component
// =============================================================================

export function UnifiedEventCard({
  event,
  selected = false,
  onClick,
  onKeyDown,
}: UnifiedEventCardProps) {
  const badge = ENTITY_BADGES[event.type];
  const timeAgo = formatDistanceToNow(new Date(event.timestamp), { addSuffix: true });

  const handleClick = () => onClick?.(event);
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      onClick?.(event);
    }
    onKeyDown?.(e, event);
  };

  return (
    <article
      className={`unified-event-card ${selected ? 'unified-event-card--selected' : ''}`}
      data-type={event.type}
      onClick={handleClick}
      onKeyDown={handleKeyDown}
      tabIndex={0}
      role="button"
      aria-pressed={selected}
    >
      {/* Type badge */}
      <span className="unified-event-card__badge" title={badge.label}>
        {badge.emoji}
      </span>

      {/* Main content */}
      <div className="unified-event-card__content">
        {/* Title row */}
        <div className="unified-event-card__header">
          <span className="unified-event-card__type">{badge.label}:</span>
          <span className="unified-event-card__title">{event.title}</span>
        </div>

        {/* Type-specific metadata */}
        <div className="unified-event-card__meta">
          <EventMetaRenderer type={event.type} metadata={event.metadata} />
          <span className="unified-event-card__time">{timeAgo}</span>
        </div>
      </div>
    </article>
  );
}

// =============================================================================
// Type-Specific Metadata Renderers
// =============================================================================

interface EventMetaRendererProps {
  type: EntityType;
  metadata: UnifiedEvent['metadata'];
}

function EventMetaRenderer({ type, metadata }: EventMetaRendererProps) {
  switch (type) {
    case 'mark':
      return isMarkMetadata(metadata) ? <MarkMeta {...metadata} /> : null;
    case 'crystal':
      return isCrystalMetadata(metadata) ? <CrystalMeta {...metadata} /> : null;
    case 'trail':
      return isTrailMetadata(metadata) ? <TrailMeta {...metadata} /> : null;
    case 'evidence':
      return isEvidenceMetadata(metadata) ? <EvidenceMeta {...metadata} /> : null;
    case 'teaching':
      return isTeachingMetadata(metadata) ? <TeachingMeta {...metadata} /> : null;
    case 'lemma':
      return isLemmaMetadata(metadata) ? <LemmaMeta {...metadata} /> : null;
    default:
      return null;
  }
}

// -----------------------------------------------------------------------------
// Mark
// -----------------------------------------------------------------------------

function MarkMeta({ author, principles }: MarkMetadata) {
  return (
    <>
      <span className="unified-event-card__author">by {author}</span>
      {principles.length > 0 && (
        <span className="unified-event-card__principles">
          {principles.slice(0, 2).map((p) => (
            <span key={p} className="unified-event-card__principle">
              {p}
            </span>
          ))}
          {principles.length > 2 && (
            <span className="unified-event-card__principle-more">+{principles.length - 2}</span>
          )}
        </span>
      )}
    </>
  );
}

// -----------------------------------------------------------------------------
// Crystal
// -----------------------------------------------------------------------------

function CrystalMeta({ access_count, tags }: CrystalMetadata) {
  return (
    <>
      <span className="unified-event-card__access">
        accessed {access_count}×
      </span>
      {tags.length > 0 && (
        <span className="unified-event-card__tags">
          {tags.slice(0, 2).map((t) => (
            <span key={t} className="unified-event-card__tag">
              {t}
            </span>
          ))}
          {tags.length > 2 && (
            <span className="unified-event-card__tag-more">+{tags.length - 2}</span>
          )}
        </span>
      )}
    </>
  );
}

// -----------------------------------------------------------------------------
// Trail
// -----------------------------------------------------------------------------

function TrailMeta({ step_count, evidence_strength }: TrailMetadata) {
  return (
    <>
      <span className="unified-event-card__steps">{step_count} steps</span>
      <span
        className="unified-event-card__evidence"
        data-strength={evidence_strength}
      >
        {evidence_strength}
      </span>
    </>
  );
}

// -----------------------------------------------------------------------------
// Evidence
// -----------------------------------------------------------------------------

function EvidenceMeta({ subtype, status }: EvidenceMetadata) {
  const subtypeLabels: Record<string, string> = {
    trace_witness: 'TraceWitness',
    verification_graph: 'VerificationGraph',
    categorical_violation: 'Violation',
  };

  return (
    <>
      <span className="unified-event-card__subtype">{subtypeLabels[subtype] ?? subtype}</span>
      <span className="unified-event-card__status" data-status={status}>
        {status}
      </span>
    </>
  );
}

// -----------------------------------------------------------------------------
// Teaching
// -----------------------------------------------------------------------------

function TeachingMeta({ severity, source_module, is_alive }: TeachingMetadata) {
  // Shorten module path for display
  const shortModule = source_module.split('.').slice(-2).join('.');

  return (
    <>
      <span className="unified-event-card__severity" data-severity={severity}>
        {severity}
      </span>
      <span className="unified-event-card__source">from {shortModule}</span>
      {!is_alive && <span className="unified-event-card__extinct">extinct</span>}
    </>
  );
}

// -----------------------------------------------------------------------------
// Lemma
// -----------------------------------------------------------------------------

function LemmaMeta({ usage_count, checker }: LemmaMetadata) {
  return (
    <>
      <span className="unified-event-card__usage">usage: {usage_count}</span>
      <span className="unified-event-card__checker">{checker}</span>
    </>
  );
}

// =============================================================================
// Export
// =============================================================================

export default UnifiedEventCard;
