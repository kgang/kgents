/**
 * GardenPanel — Shows lifecycle state of the garden
 *
 * Grounded in: spec/ui/axioms.md — A4 (No-Shipping Axiom)
 * "There is no shipping. Only continuous iteration and evolution."
 *
 * The garden metaphor is literal:
 * SEED → SPROUT → BLOOM → WITHER → COMPOST
 */

import type { GardenState, GardenItem, LifecycleStage } from '../../types';
import { LIFECYCLE_COLORS, LIFECYCLE_ICONS, LIFECYCLE_DESCRIPTIONS } from '../../types';

interface GardenPanelProps {
  /** Current garden state */
  state: GardenState;

  /** Handler for item selection */
  onSelectItem?: (item: GardenItem) => void;

  /** Handler for tending an item */
  onTendItem?: (item: GardenItem) => void;

  /** Handler for composting an item */
  onCompostItem?: (item: GardenItem) => void;
}

/**
 * Panel showing garden state and attention items.
 */
export function GardenPanel({ state, onSelectItem, onTendItem, onCompostItem }: GardenPanelProps) {
  return (
    <div className="garden-panel panel-severe">
      <h3 className="text-xs text-secondary">GARDEN</h3>

      {/* Summary counts */}
      <GardenSummary state={state} />

      {/* Health indicator */}
      <GardenHealth health={state.health} />

      {/* Attention needed */}
      {state.attention.length > 0 && (
        <AttentionList
          items={state.attention}
          onSelect={onSelectItem}
          onTend={onTendItem}
          onCompost={onCompostItem}
        />
      )}
    </div>
  );
}

/**
 * Summary showing counts for each lifecycle stage.
 */
export function GardenSummary({ state }: { state: GardenState }) {
  return (
    <div className="garden-summary">
      <StageCount stage="seed" count={state.seeds} />
      <StageCount stage="sprout" count={state.sprouts} />
      <StageCount stage="bloom" count={state.blooms} />
      <StageCount stage="wither" count={state.withering} />
      {state.compostedToday > 0 && (
        <span className="garden-summary__composted text-xs text-muted">
          +{state.compostedToday} composted
        </span>
      )}
    </div>
  );
}

/**
 * Individual stage count.
 */
function StageCount({ stage, count }: { stage: LifecycleStage; count: number }) {
  const color = LIFECYCLE_COLORS[stage];
  const icon = LIFECYCLE_ICONS[stage];

  return (
    <span className="garden-summary__stage" style={{ color }} title={LIFECYCLE_DESCRIPTIONS[stage]}>
      <span className="garden-summary__icon">{icon}</span>
      <span className="garden-summary__count">{count}</span>
    </span>
  );
}

/**
 * Overall garden health indicator.
 */
function GardenHealth({ health }: { health: number }) {
  const percentage = Math.round(health * 100);
  const color =
    health >= 0.8
      ? 'var(--collapse-pass)'
      : health >= 0.5
        ? 'var(--collapse-partial)'
        : 'var(--collapse-fail)';

  return (
    <div className="garden-health">
      <span className="text-xs text-secondary">Health:</span>
      <div className="garden-health__bar">
        <div
          className="garden-health__fill"
          style={{ width: `${percentage}%`, backgroundColor: color }}
        />
      </div>
      <span className="garden-health__value" style={{ color }}>
        {percentage}%
      </span>
    </div>
  );
}

/**
 * List of items needing attention.
 */
function AttentionList({
  items,
  onSelect,
  onTend,
  onCompost,
}: {
  items: GardenItem[];
  onSelect?: (item: GardenItem) => void;
  onTend?: (item: GardenItem) => void;
  onCompost?: (item: GardenItem) => void;
}) {
  return (
    <div className="garden-attention">
      <h4 className="text-xs text-secondary">ATTENTION NEEDED:</h4>
      <ul className="list-dense">
        {items.map((item) => (
          <AttentionItem
            key={item.path}
            item={item}
            onSelect={onSelect}
            onTend={onTend}
            onCompost={onCompost}
          />
        ))}
      </ul>
    </div>
  );
}

/**
 * Individual attention item.
 */
function AttentionItem({
  item,
  onSelect,
  onTend,
  onCompost,
}: {
  item: GardenItem;
  onSelect?: (item: GardenItem) => void;
  onTend?: (item: GardenItem) => void;
  onCompost?: (item: GardenItem) => void;
}) {
  const { lifecycle } = item;
  const color = LIFECYCLE_COLORS[lifecycle.stage];
  const icon = LIFECYCLE_ICONS[lifecycle.stage];

  return (
    <li className="garden-attention__item">
      <button className="garden-attention__link" onClick={() => onSelect?.(item)} style={{ color }}>
        <span className="garden-attention__icon">{icon}</span>
        <span className="garden-attention__title">{item.title}</span>
        <span className="garden-attention__days text-xs text-muted">
          {lifecycle.daysSinceActivity}d
        </span>
      </button>
      <div className="garden-attention__actions">
        {lifecycle.stage !== 'compost' && onTend && (
          <button
            className="garden-attention__action text-xs"
            onClick={() => onTend(item)}
            title="Mark as tended"
          >
            tend
          </button>
        )}
        {lifecycle.stage === 'wither' && onCompost && (
          <button
            className="garden-attention__action garden-attention__action--compost text-xs"
            onClick={() => onCompost(item)}
            title="Mark for composting"
          >
            compost
          </button>
        )}
      </div>
    </li>
  );
}

/**
 * Compact garden indicator for status line.
 */
export function GardenIndicator({ state }: { state: GardenState }) {
  const healthPercent = Math.round(state.health * 100);
  const attentionCount = state.attention.length;

  const color =
    state.health >= 0.8
      ? 'var(--collapse-pass)'
      : state.health >= 0.5
        ? 'var(--collapse-partial)'
        : 'var(--collapse-fail)';

  return (
    <span className="garden-indicator" style={{ color }}>
      garden:{healthPercent}%
      {attentionCount > 0 && (
        <span className="garden-indicator__attention">({attentionCount}!)</span>
      )}
    </span>
  );
}

export default GardenPanel;
