/**
 * LayerGroup — Expandable layer section in K-Block Explorer
 *
 * "Layer badges with colors from LAYER_CONFIG"
 *
 * Displays a collapsible group of K-Blocks belonging to a single layer.
 * Each layer has:
 * - Colored badge with layer number
 * - Name and item count
 * - Chevron for expand/collapse
 * - K-Block items when expanded
 *
 * @see spec/agents/k-block.md
 */

import { memo, useCallback, useRef, useEffect } from 'react';
import { ChevronDown, ChevronRight, Lock, AlertCircle } from 'lucide-react';
import type { LayerGroupProps, KBlockExplorerItem } from './types';
import { getLossColor, getLossSeverity } from './types';
import './LayerGroup.css';

// =============================================================================
// Sub-components
// =============================================================================

interface KBlockItemProps {
  item: KBlockExplorerItem;
  isSelected: boolean;
  isFocused: boolean;
  isConstitutional: boolean;
  onSelect: (item: KBlockExplorerItem) => void;
  onFocus: (id: string) => void;
}

const KBlockItem = memo(function KBlockItem({
  item,
  isSelected,
  isFocused,
  isConstitutional,
  onSelect,
  onFocus,
}: KBlockItemProps) {
  const itemRef = useRef<HTMLButtonElement>(null);

  // Scroll into view when focused
  useEffect(() => {
    if (isFocused && itemRef.current) {
      itemRef.current.scrollIntoView({
        behavior: 'smooth',
        block: 'nearest',
      });
    }
  }, [isFocused]);

  const lossColor = getLossColor(item.galoisLoss);
  const lossSeverity = getLossSeverity(item.galoisLoss);
  const lossPercentage = Math.round((1 - item.galoisLoss) * 100);

  // Handlers that use item from props - stable references
  const handleClick = useCallback(() => {
    onSelect(item);
  }, [onSelect, item]);

  const handleFocus = useCallback(() => {
    onFocus(item.id);
  }, [onFocus, item.id]);

  return (
    <button
      ref={itemRef}
      className={`kbe-item ${isSelected ? 'kbe-item--selected' : ''} ${isFocused ? 'kbe-item--focused' : ''}`}
      onClick={handleClick}
      onFocus={handleFocus}
      title={item.path}
      aria-selected={isSelected}
    >
      {/* Derivation indicator */}
      <span className="kbe-item__derive-line" />

      {/* Title */}
      <span className="kbe-item__title">{item.title}</span>

      {/* Constitutional lock */}
      {isConstitutional && (
        <span className="kbe-item__lock" title="Constitutional (read-only)">
          <Lock size={10} />
        </span>
      )}

      {/* Proof badge */}
      {item.hasProof && (
        <span className="kbe-item__proof" title="Has Toulmin proof">
          P
        </span>
      )}

      {/* Loss gauge */}
      <span
        className={`kbe-item__loss kbe-item__loss--${lossSeverity}`}
        title={`Coherence: ${lossPercentage}% (loss: ${item.galoisLoss.toFixed(3)})`}
        style={{ '--loss-color': lossColor } as React.CSSProperties}
      >
        <span className="kbe-item__loss-fill" style={{ width: `${lossPercentage}%` }} />
        {lossSeverity !== 'healthy' && <AlertCircle size={10} className="kbe-item__loss-icon" />}
      </span>
    </button>
  );
});

// =============================================================================
// Main Component
// =============================================================================

export const LayerGroup = memo(function LayerGroup({
  config,
  items,
  expanded,
  isConstitutional,
  selectedId,
  isFocused,
  onToggle,
  onSelect,
  onItemFocus,
}: LayerGroupProps) {
  const headerRef = useRef<HTMLButtonElement>(null);

  // Scroll header into view when layer is focused
  useEffect(() => {
    if (isFocused && headerRef.current) {
      headerRef.current.scrollIntoView({
        behavior: 'smooth',
        block: 'nearest',
      });
    }
  }, [isFocused]);

  // Use stable callback references - the item is passed from the child
  const handleItemSelect = useCallback(
    (item: KBlockExplorerItem) => {
      onSelect(item);
    },
    [onSelect]
  );

  const handleItemFocus = useCallback(
    (id: string) => {
      onItemFocus(id);
    },
    [onItemFocus]
  );

  // Calculate aggregate loss for the layer
  const avgLoss =
    items.length > 0 ? items.reduce((sum, item) => sum + item.galoisLoss, 0) / items.length : 0;
  const avgLossColor = getLossColor(avgLoss);

  // Handle toggle with layer number - stable reference
  const handleToggleClick = useCallback(() => {
    onToggle(config.layer);
  }, [onToggle, config.layer]);

  return (
    <div
      className={`kbe-layer ${expanded ? 'kbe-layer--expanded' : ''} ${isFocused ? 'kbe-layer--focused' : ''}`}
      data-layer={config.layer}
    >
      {/* Layer Header */}
      <button
        ref={headerRef}
        className="kbe-layer__header"
        onClick={handleToggleClick}
        aria-expanded={expanded}
        aria-controls={`kbe-layer-content-${config.layer}`}
      >
        {/* Chevron */}
        <span className="kbe-layer__chevron">
          {expanded ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
        </span>

        {/* Layer badge */}
        <span
          className="kbe-layer__badge"
          style={{
            backgroundColor: config.color,
            color: getContrastColor(config.color),
          }}
        >
          L{config.layer}
        </span>

        {/* Layer name */}
        <span className="kbe-layer__name">{config.name}</span>

        {/* Item count */}
        <span className="kbe-layer__count">{items.length}</span>

        {/* Constitutional indicator */}
        {isConstitutional && (
          <span className="kbe-layer__constitutional" title="Constitutional layer">
            <Lock size={12} />
          </span>
        )}

        {/* Aggregate loss indicator */}
        {items.length > 0 && (
          <span
            className="kbe-layer__health"
            title={`Avg. coherence: ${Math.round((1 - avgLoss) * 100)}%`}
            style={{ backgroundColor: avgLossColor }}
          />
        )}
      </button>

      {/* Layer Content */}
      {expanded && items.length > 0 && (
        <div
          id={`kbe-layer-content-${config.layer}`}
          className="kbe-layer__content"
          role="group"
          aria-label={`${config.name} K-Blocks`}
        >
          {items.map((item) => (
            <KBlockItem
              key={item.id}
              item={item}
              isSelected={selectedId === item.id}
              isFocused={false} // Will be managed by parent
              isConstitutional={isConstitutional}
              onSelect={handleItemSelect}
              onFocus={handleItemFocus}
            />
          ))}
        </div>
      )}

      {/* Empty state */}
      {expanded && items.length === 0 && (
        <div className="kbe-layer__empty">
          <span className="kbe-layer__empty-text">No K-Blocks in this layer</span>
        </div>
      )}
    </div>
  );
});

// =============================================================================
// Helpers
// =============================================================================

/**
 * Get contrasting text color for a background color.
 */
function getContrastColor(hexColor: string): string {
  // Remove # if present
  const hex = hexColor.replace('#', '');

  // Parse RGB
  const r = parseInt(hex.substr(0, 2), 16);
  const g = parseInt(hex.substr(2, 2), 16);
  const b = parseInt(hex.substr(4, 2), 16);

  // Calculate relative luminance
  const luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255;

  // Return black or white based on luminance
  return luminance > 0.5 ? '#000000' : '#ffffff';
}

export default LayerGroup;
