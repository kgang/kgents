import { memo } from 'react';
import type { GraphNode } from './state/types';
import './AffordancePanel.css';

type EditorMode = 'NORMAL' | 'INSERT' | 'EDGE' | 'VISUAL' | 'COMMAND' | 'WITNESS';

interface AffordanceAction {
  key: string;
  label: string;
  category: 'navigate' | 'edit' | 'analyze' | 'witness';
}

interface AffordancePanelProps {
  node: GraphNode | null;
  mode: EditorMode;
  isVisible: boolean;
  onClose: () => void;
  derivationInfo?: {
    parentCount: number;
    childCount: number;
    siblingCount: number;
    layer: number;
  };
}

// Define actions per mode
const NORMAL_ACTIONS: AffordanceAction[] = [
  // Navigate
  { key: 'gh', label: 'Go to parent', category: 'navigate' },
  { key: 'gl', label: 'Go to child', category: 'navigate' },
  { key: 'gj', label: 'Next sibling', category: 'navigate' },
  { key: 'gk', label: 'Prev sibling', category: 'navigate' },
  { key: 'gG', label: 'Trace to genesis', category: 'navigate' },
  { key: 'gd', label: 'Go to definition', category: 'navigate' },
  { key: 'gr', label: 'Go to references', category: 'navigate' },
  // Edit
  { key: 'i', label: 'Enter INSERT mode', category: 'edit' },
  { key: ':', label: 'Command mode', category: 'edit' },
  { key: 'ge', label: 'Enter EDGE mode', category: 'edit' },
  // Analyze
  { key: '\\a', label: 'Analysis quadrant', category: 'analyze' },
  { key: 'gE', label: 'Toggle edge panel', category: 'analyze' },
  // Witness
  { key: 'gw', label: 'Enter WITNESS mode', category: 'witness' },
  { key: 'gm', label: 'View marks', category: 'witness' },
  { key: 'gf', label: 'View decisions', category: 'witness' },
];

const INSERT_ACTIONS: AffordanceAction[] = [
  { key: 'Esc', label: 'Exit to NORMAL', category: 'edit' },
  { key: ':w', label: 'Save with witness', category: 'edit' },
  { key: ':wq', label: 'Save and quit', category: 'edit' },
  { key: ':q!', label: 'Discard changes', category: 'edit' },
];

const EDGE_ACTIONS: AffordanceAction[] = [
  { key: 'Esc', label: 'Exit to NORMAL', category: 'edit' },
  { key: 'Enter', label: 'Confirm edge', category: 'edit' },
  { key: 'Tab', label: 'Cycle edge type', category: 'edit' },
  { key: 'j/k', label: 'Select target', category: 'navigate' },
];

const VISUAL_ACTIONS: AffordanceAction[] = [
  { key: 'Esc', label: 'Exit to NORMAL', category: 'edit' },
  { key: 'd', label: 'Delete selection', category: 'edit' },
  { key: 'y', label: 'Yank selection', category: 'edit' },
  { key: 'ge', label: 'Create edges from selection', category: 'edit' },
];

const WITNESS_ACTIONS: AffordanceAction[] = [
  { key: 'Esc', label: 'Exit to NORMAL', category: 'edit' },
  { key: 'm', label: 'Create mark', category: 'witness' },
  { key: 'd', label: 'Record decision', category: 'witness' },
  { key: 'c', label: 'Crystallize moment', category: 'witness' },
  { key: 'j/k', label: 'Navigate marks', category: 'navigate' },
];

const COMMAND_ACTIONS: AffordanceAction[] = [
  { key: 'Esc', label: 'Cancel command', category: 'edit' },
  { key: 'Enter', label: 'Execute command', category: 'edit' },
  { key: 'Tab', label: 'Autocomplete', category: 'edit' },
];

function getActionsForMode(mode: EditorMode): AffordanceAction[] {
  switch (mode) {
    case 'INSERT':
      return INSERT_ACTIONS;
    case 'EDGE':
      return EDGE_ACTIONS;
    case 'VISUAL':
      return VISUAL_ACTIONS;
    case 'WITNESS':
      return WITNESS_ACTIONS;
    case 'COMMAND':
      return COMMAND_ACTIONS;
    case 'NORMAL':
    default:
      return NORMAL_ACTIONS;
  }
}

const categoryLabels: Record<string, string> = {
  navigate: 'NAVIGATE',
  edit: 'EDIT',
  analyze: 'ANALYZE',
  witness: 'WITNESS',
};

export const AffordancePanel = memo(function AffordancePanel({
  node,
  mode,
  isVisible,
  onClose,
  derivationInfo,
}: AffordancePanelProps) {
  if (!isVisible) return null;

  const actions = getActionsForMode(mode);

  // Group by category
  const grouped = actions.reduce(
    (acc, action) => {
      if (!acc[action.category]) acc[action.category] = [];
      acc[action.category].push(action);
      return acc;
    },
    {} as Record<string, AffordanceAction[]>
  );

  return (
    <div className="affordance-panel" role="dialog" aria-label="Keyboard shortcuts">
      <div className="affordance-panel__header">
        <span className="affordance-panel__mode">{mode}</span>
        <span className="affordance-panel__title">
          {node ? node.path.split('/').pop() : 'No node selected'}
        </span>
        <button className="affordance-panel__close" onClick={onClose} aria-label="Close">
          ×
        </button>
      </div>

      {derivationInfo && (
        <div className="affordance-panel__context">
          <span title="Layer">L{derivationInfo.layer}</span>
          <span title="Parents">↑{derivationInfo.parentCount}</span>
          <span title="Children">↓{derivationInfo.childCount}</span>
          <span title="Siblings">↔{derivationInfo.siblingCount}</span>
        </div>
      )}

      <div className="affordance-panel__content">
        {Object.entries(grouped).map(([category, categoryActions]) => (
          <div key={category} className="affordance-panel__section">
            <div className="affordance-panel__category">{categoryLabels[category]}</div>
            {categoryActions.map((action) => (
              <div key={action.key} className="affordance-panel__action">
                <kbd className="affordance-panel__key">{action.key}</kbd>
                <span className="affordance-panel__label">{action.label}</span>
              </div>
            ))}
          </div>
        ))}
      </div>

      <div className="affordance-panel__footer">
        <span>
          Press <kbd>?</kbd> to toggle • <kbd>Esc</kbd> to close
        </span>
      </div>
    </div>
  );
});

export type { AffordancePanelProps, EditorMode, AffordanceAction };
