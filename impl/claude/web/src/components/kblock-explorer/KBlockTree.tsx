/**
 * KBlockTree — Tree view renderer for K-Block Explorer
 *
 * "Tree view with Constitutional section (22 genesis K-Blocks) and User section"
 *
 * Renders the full K-Block tree with two main sections:
 * 1. Constitutional (L0-L3): Read-only genesis K-Blocks
 * 2. User (L1-L7): Editable user K-Blocks
 * 3. Orphans: K-Blocks without layer assignment
 *
 * Supports derivation-based tree structure and keyboard navigation.
 *
 * @see spec/agents/k-block.md
 */

import { memo, useCallback } from 'react';
import { Layers, FileQuestion } from 'lucide-react';
import { ConstitutionalSection } from './ConstitutionalSection';
import { LayerGroup } from './LayerGroup';
import type { KBlockTreeProps, KBlockExplorerItem, FocusTarget } from './types';
import './KBlockTree.css';

// =============================================================================
// Sub-components
// =============================================================================

interface UserSectionProps {
  groups: {
    config: { layer: number; name: string; description: string; color: string; icon: string };
    items: KBlockExplorerItem[];
    expanded: boolean;
  }[];
  selectedId?: string;
  focusTarget: FocusTarget | null;
  onSelect: (item: KBlockExplorerItem) => void;
  onToggleLayer: (layer: number) => void;
  onFocusChange: (target: FocusTarget | null) => void;
}

const UserSection = memo(function UserSection({
  groups,
  selectedId,
  focusTarget,
  onSelect,
  onToggleLayer,
  onFocusChange,
}: UserSectionProps) {
  const totalItems = groups.reduce((sum, g) => sum + g.items.length, 0);

  const handleItemFocus = useCallback(
    (id: string) => {
      onFocusChange({ id, type: 'kblock' });
    },
    [onFocusChange]
  );

  const isLayerFocused = (layer: number) =>
    focusTarget?.type === 'layer' && focusTarget.id === `user-${layer}`;

  return (
    <section className="kbe-user" aria-label="User K-Blocks">
      {/* Section Header */}
      <header className="kbe-user__header">
        <div className="kbe-user__title-row">
          <Layers size={14} className="kbe-user__icon" />
          <h3 className="kbe-user__title">User K-Blocks</h3>
        </div>
        <div className="kbe-user__meta">
          <span className="kbe-user__count">{totalItems} K-Blocks</span>
        </div>
      </header>

      {/* Layer Groups */}
      <div className="kbe-user__layers">
        {groups.map((group) => (
          <LayerGroup
            key={group.config.layer}
            config={group.config}
            items={group.items}
            expanded={group.expanded}
            isConstitutional={false}
            selectedId={selectedId}
            isFocused={isLayerFocused(group.config.layer)}
            onToggle={onToggleLayer}
            onSelect={onSelect}
            onItemFocus={handleItemFocus}
          />
        ))}
      </div>

      {/* Empty state */}
      {totalItems === 0 && (
        <div className="kbe-user__empty">
          <p className="kbe-user__empty-text">No user K-Blocks yet.</p>
          <p className="kbe-user__empty-hint">Create K-Blocks to build your knowledge graph.</p>
        </div>
      )}
    </section>
  );
});

interface OrphansSectionProps {
  items: KBlockExplorerItem[];
  selectedId?: string;
  focusTarget: FocusTarget | null;
  onSelect: (item: KBlockExplorerItem) => void;
  onFocusChange: (target: FocusTarget | null) => void;
}

const OrphansSection = memo(function OrphansSection({
  items,
  selectedId,
  focusTarget,
  onSelect,
  onFocusChange,
}: OrphansSectionProps) {
  if (items.length === 0) return null;

  return (
    <section className="kbe-orphans" aria-label="Orphan K-Blocks">
      {/* Section Header */}
      <header className="kbe-orphans__header">
        <div className="kbe-orphans__title-row">
          <FileQuestion size={14} className="kbe-orphans__icon" />
          <h3 className="kbe-orphans__title">Orphans</h3>
          <span className="kbe-orphans__count">{items.length}</span>
        </div>
        <p className="kbe-orphans__hint">K-Blocks without layer assignment</p>
      </header>

      {/* Orphan Items */}
      <div className="kbe-orphans__list">
        {items.map((item) => (
          <OrphanItem
            key={item.id}
            item={item}
            isSelected={selectedId === item.id}
            isFocused={focusTarget?.type === 'kblock' && focusTarget.id === item.id}
            onSelect={onSelect}
            onFocus={onFocusChange}
          />
        ))}
      </div>
    </section>
  );
});

interface OrphanItemProps {
  item: KBlockExplorerItem;
  isSelected: boolean;
  isFocused: boolean;
  onSelect: (item: KBlockExplorerItem) => void;
  onFocus: (target: FocusTarget) => void;
}

const OrphanItem = memo(function OrphanItem({
  item,
  isSelected,
  isFocused,
  onSelect,
  onFocus,
}: OrphanItemProps) {
  // Handlers that use item from props - stable references
  const handleClick = useCallback(() => {
    onSelect(item);
  }, [onSelect, item]);

  const handleFocus = useCallback(() => {
    onFocus({ id: item.id, type: 'kblock' });
  }, [onFocus, item.id]);

  return (
    <button
      className={`kbe-orphan-item ${isSelected ? 'kbe-orphan-item--selected' : ''} ${isFocused ? 'kbe-orphan-item--focused' : ''}`}
      onClick={handleClick}
      onFocus={handleFocus}
      title={item.path}
    >
      <span className="kbe-orphan-item__icon">?</span>
      <span className="kbe-orphan-item__title">{item.title}</span>
      <span className="kbe-orphan-item__loss" title={`Loss: ${item.galoisLoss.toFixed(3)}`}>
        L={item.galoisLoss.toFixed(2)}
      </span>
    </button>
  );
});

// =============================================================================
// Main Component
// =============================================================================

export const KBlockTree = memo(function KBlockTree({
  constitutionalGroups,
  userGroups,
  orphans,
  selectedId,
  focusTarget,
  onSelect,
  onToggleLayer,
  onFocusChange,
}: KBlockTreeProps) {
  const handleConstitutionalToggle = useCallback(
    (layer: number) => {
      onToggleLayer('constitutional', layer);
    },
    [onToggleLayer]
  );

  const handleUserToggle = useCallback(
    (layer: number) => {
      onToggleLayer('user', layer);
    },
    [onToggleLayer]
  );

  return (
    <div className="kbe-tree">
      {/* Constitutional Section */}
      <ConstitutionalSection
        groups={constitutionalGroups}
        selectedId={selectedId}
        focusTarget={focusTarget}
        onSelect={onSelect}
        onToggleLayer={handleConstitutionalToggle}
        onFocusChange={onFocusChange}
      />

      {/* User Section */}
      <UserSection
        groups={userGroups}
        selectedId={selectedId}
        focusTarget={focusTarget}
        onSelect={onSelect}
        onToggleLayer={handleUserToggle}
        onFocusChange={onFocusChange}
      />

      {/* Orphans Section */}
      <OrphansSection
        items={orphans}
        selectedId={selectedId}
        focusTarget={focusTarget}
        onSelect={onSelect}
        onFocusChange={onFocusChange}
      />
    </div>
  );
});

export default KBlockTree;
