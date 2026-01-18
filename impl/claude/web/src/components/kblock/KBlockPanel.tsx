/**
 * KBlockPanel — K-Block content viewer/editor
 *
 * Grounded in: spec/ui/axioms.md, spec/ui/design-decisions.md
 * "K-Blocks are the atomic unit of knowledge."
 *
 * Features:
 * - Content display with provenance indicators
 * - Lifecycle stage badge
 * - Collapsing function status
 * - Edit mode with container awareness
 */

import type { Provenance, LifecycleState, CollapseState } from '../../types';
import { useContainer } from '../containers/ContainerProvider';
import { ProvenanceIndicator } from '../provenance/ProvenanceIndicator';
import { LIFECYCLE_COLORS, LIFECYCLE_ICONS, LIFECYCLE_DESCRIPTIONS } from '../../types';

interface KBlock {
  /** K-Block ID */
  id: string;

  /** AGENTESE path */
  path: string;

  /** Display title */
  title: string;

  /** Content (markdown) */
  content: string;

  /** Provenance information */
  provenance: Provenance;

  /** Lifecycle state */
  lifecycle: LifecycleState;

  /** Created timestamp */
  createdAt: string;

  /** Updated timestamp */
  updatedAt: string;
}

interface KBlockPanelProps {
  /** K-Block to display */
  kblock: KBlock;

  /** Collapse state (if available) */
  collapseState?: CollapseState;

  /** Whether in edit mode */
  isEditing?: boolean;

  /** Handler for content changes */
  onContentChange?: (content: string) => void;

  /** Handler for save */
  onSave?: () => void;

  /** Handler for cancel */
  onCancel?: () => void;

  /** Handler for tend action */
  onTend?: () => void;
}

/**
 * K-Block content panel with provenance and lifecycle.
 */
export function KBlockPanel({
  kblock,
  collapseState,
  isEditing = false,
  onContentChange,
  onSave,
  onCancel,
  onTend,
}: KBlockPanelProps) {
  const container = useContainer();
  const canEdit = container.editable;
  const { lifecycle } = kblock;

  return (
    <article className="kblock-panel panel-severe">
      {/* Header */}
      <header className="kblock-panel__header">
        <div className="kblock-panel__title-row">
          <h2 className="kblock-panel__title text-md">{kblock.title}</h2>
          <ProvenanceIndicator provenance={kblock.provenance} />
        </div>

        <div className="kblock-panel__meta text-xs text-secondary">
          <span className="kblock-panel__path">{kblock.path}</span>
          <span className="kblock-panel__divider">|</span>
          <LifecycleBadge stage={lifecycle.stage} />
          {lifecycle.daysSinceActivity > 0 && (
            <>
              <span className="kblock-panel__divider">|</span>
              <span className="kblock-panel__days">
                {lifecycle.daysSinceActivity}d since activity
              </span>
            </>
          )}
        </div>
      </header>

      {/* Content */}
      <div className="kblock-panel__content">
        {isEditing && canEdit ? (
          <EditableContent content={kblock.content} onChange={onContentChange} />
        ) : (
          <ReadOnlyContent content={kblock.content} />
        )}
      </div>

      {/* Footer with actions */}
      <footer className="kblock-panel__footer">
        {isEditing ? (
          <EditActions onSave={onSave} onCancel={onCancel} />
        ) : (
          <ViewActions canEdit={canEdit} canTend={lifecycle.stage !== 'compost'} onTend={onTend} />
        )}

        {/* Collapse summary */}
        {collapseState && <CollapseSummary state={collapseState} />}
      </footer>
    </article>
  );
}

/**
 * Lifecycle stage badge.
 */
function LifecycleBadge({ stage }: { stage: string }) {
  const color = LIFECYCLE_COLORS[stage as keyof typeof LIFECYCLE_COLORS];
  const icon = LIFECYCLE_ICONS[stage as keyof typeof LIFECYCLE_ICONS];
  const description = LIFECYCLE_DESCRIPTIONS[stage as keyof typeof LIFECYCLE_DESCRIPTIONS];

  return (
    <span className="lifecycle-badge" style={{ color }} title={description}>
      {icon} {stage}
    </span>
  );
}

/**
 * Read-only content display.
 */
function ReadOnlyContent({ content }: { content: string }) {
  // Simple markdown-like rendering
  const paragraphs = content.split('\n\n');

  return (
    <div className="kblock-content kblock-content--readonly">
      {paragraphs.map((p, i) => {
        if (p.startsWith('# ')) {
          return (
            <h1 key={i} className="text-xl">
              {p.slice(2)}
            </h1>
          );
        }
        if (p.startsWith('## ')) {
          return (
            <h2 key={i} className="text-lg">
              {p.slice(3)}
            </h2>
          );
        }
        if (p.startsWith('### ')) {
          return (
            <h3 key={i} className="text-md">
              {p.slice(4)}
            </h3>
          );
        }
        if (p.startsWith('- ') || p.startsWith('* ')) {
          const items = p.split('\n').map((line) => line.slice(2));
          return (
            <ul key={i} className="list-dense">
              {items.map((item, j) => (
                <li key={j}>{item}</li>
              ))}
            </ul>
          );
        }
        if (p.startsWith('```')) {
          const code = p.replace(/```\w*\n?/, '').replace(/```$/, '');
          return (
            <pre key={i} className="kblock-code">
              {code}
            </pre>
          );
        }
        return <p key={i}>{p}</p>;
      })}
    </div>
  );
}

/**
 * Editable content textarea.
 */
function EditableContent({
  content,
  onChange,
}: {
  content: string;
  onChange?: (content: string) => void;
}) {
  return (
    <textarea
      className="kblock-content kblock-content--editable"
      value={content}
      onChange={(e) => onChange?.(e.target.value)}
      placeholder="Enter content..."
    />
  );
}

/**
 * Edit mode actions.
 */
function EditActions({ onSave, onCancel }: { onSave?: () => void; onCancel?: () => void }) {
  return (
    <div className="kblock-actions">
      <button className="kblock-actions__btn kblock-actions__btn--primary" onClick={onSave}>
        Save
      </button>
      <button className="kblock-actions__btn" onClick={onCancel}>
        Cancel
      </button>
    </div>
  );
}

/**
 * View mode actions.
 */
function ViewActions({
  canEdit,
  canTend,
  onTend,
}: {
  canEdit: boolean;
  canTend: boolean;
  onTend?: () => void;
}) {
  return (
    <div className="kblock-actions">
      {canTend && onTend && (
        <button className="kblock-actions__btn text-xs" onClick={onTend}>
          tend
        </button>
      )}
      {!canEdit && (
        <span className="kblock-actions__hint text-xs text-muted">
          (read-only in this container)
        </span>
      )}
    </div>
  );
}

/**
 * Compact collapse state summary.
 */
function CollapseSummary({ state }: { state: CollapseState }) {
  const slopColor =
    state.overallSlop === 'low'
      ? 'var(--collapse-pass)'
      : state.overallSlop === 'medium'
        ? 'var(--collapse-partial)'
        : 'var(--collapse-fail)';

  const constitutionPercent = Math.round((state.constitution.score / 7) * 100);
  const galoisPercent = Math.round((1 - state.galois.loss) * 100);

  return (
    <div className="kblock-collapse text-xs text-secondary">
      <span style={{ color: slopColor }}>slop:{state.overallSlop}</span>
      <span className="kblock-collapse__divider">|</span>
      <span>constitution:{constitutionPercent}%</span>
      <span className="kblock-collapse__divider">|</span>
      <span>galois:{galoisPercent}%</span>
    </div>
  );
}

/**
 * Empty state for when no K-Block is selected.
 */
export function KBlockEmptyState() {
  return (
    <div className="kblock-panel kblock-panel--empty panel-severe">
      <p className="text-secondary">Select a K-Block to view</p>
    </div>
  );
}

export default KBlockPanel;
