/**
 * ConstitutionalSection — Genesis K-Blocks in K-Block Explorer
 *
 * "Constitutional section with 22 pre-seeded K-Blocks (read-only)"
 *
 * Displays the constitutional foundation of the kgents system:
 * - L0: Genesis (Zero Seed)
 * - L1: Axioms (Entity, Morphism, Galois Ground)
 * - L2: Values (Seven constitutional principles)
 * - L3: Specs (Design laws and constraints)
 *
 * All constitutional K-Blocks are read-only and form the derivation
 * foundation for all user K-Blocks.
 *
 * @see spec/agents/k-block.md
 */

import { memo, useCallback } from 'react';
import { Shield } from 'lucide-react';
import { LayerGroup } from './LayerGroup';
import type { ConstitutionalSectionProps, KBlockExplorerItem } from './types';
import './ConstitutionalSection.css';

// =============================================================================
// Main Component
// =============================================================================

export const ConstitutionalSection = memo(function ConstitutionalSection({
  groups,
  selectedId,
  focusTarget,
  onSelect,
  onToggleLayer,
  onFocusChange,
}: ConstitutionalSectionProps) {
  // Calculate totals
  const totalItems = groups.reduce((sum, g) => sum + g.items.length, 0);
  const avgLoss =
    totalItems > 0
      ? groups.reduce((sum, g) => sum + g.items.reduce((s, i) => s + i.galoisLoss, 0), 0) /
        totalItems
      : 0;

  const handleSelect = useCallback(
    (item: KBlockExplorerItem) => {
      onSelect(item);
    },
    [onSelect]
  );

  const handleToggle = useCallback(
    (layer: number) => {
      onToggleLayer(layer);
    },
    [onToggleLayer]
  );

  const handleItemFocus = useCallback(
    (id: string) => {
      onFocusChange({ id, type: 'kblock' });
    },
    [onFocusChange]
  );

  const isLayerFocused = (layer: number) =>
    focusTarget?.type === 'layer' && focusTarget.id === `constitutional-${layer}`;

  return (
    <section className="kbe-constitutional" aria-label="Constitutional K-Blocks">
      {/* Section Header */}
      <header className="kbe-constitutional__header">
        <div className="kbe-constitutional__title-row">
          <Shield size={14} className="kbe-constitutional__icon" />
          <h3 className="kbe-constitutional__title">Constitutional</h3>
          <span className="kbe-constitutional__badge">22 Genesis</span>
        </div>
        <div className="kbe-constitutional__meta">
          <span className="kbe-constitutional__count">{totalItems} K-Blocks</span>
          <span className="kbe-constitutional__separator">|</span>
          <span
            className="kbe-constitutional__health"
            title={`Avg. coherence: ${Math.round((1 - avgLoss) * 100)}%`}
          >
            {Math.round((1 - avgLoss) * 100)}% coherent
          </span>
        </div>
      </header>

      {/* Layer Groups */}
      <div className="kbe-constitutional__layers">
        {groups.map((group) => (
          <LayerGroup
            key={group.config.layer}
            config={group.config}
            items={group.items}
            expanded={group.expanded}
            isConstitutional={true}
            selectedId={selectedId}
            isFocused={isLayerFocused(group.config.layer)}
            onToggle={handleToggle}
            onSelect={handleSelect}
            onItemFocus={handleItemFocus}
          />
        ))}
      </div>

      {/* Empty state */}
      {totalItems === 0 && (
        <div className="kbe-constitutional__empty">
          <p className="kbe-constitutional__empty-text">No constitutional K-Blocks found.</p>
          <p className="kbe-constitutional__empty-hint">Run genesis to seed the foundation.</p>
        </div>
      )}
    </section>
  );
});

export default ConstitutionalSection;
