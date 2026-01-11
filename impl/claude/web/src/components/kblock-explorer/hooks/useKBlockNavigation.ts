/**
 * useKBlockNavigation — Keyboard navigation for K-Block Explorer
 *
 * "gh/gl/gj/gk navigation (parent/child/sibling)"
 *
 * Implements vim-style navigation through the K-Block tree:
 * - gh: Go to parent (up the derivation tree)
 * - gl: Go to first child (down the derivation tree)
 * - gj: Go to next sibling
 * - gk: Go to previous sibling
 * - j/k: Move focus down/up in the list
 * - Enter: Select focused item
 * - Space: Toggle expand/collapse
 *
 * @see spec/agents/k-block.md
 */

import { useCallback, useEffect, useRef, useState } from 'react';
import type { KBlockExplorerItem, KBlockLayerGroup, FocusTarget, ExplorerSection } from '../types';

// =============================================================================
// Types
// =============================================================================

export interface UseKBlockNavigationOptions {
  /** Constitutional layer groups */
  constitutionalGroups: KBlockLayerGroup[];
  /** User layer groups */
  userGroups: KBlockLayerGroup[];
  /** Orphan items */
  orphans: KBlockExplorerItem[];
  /** Current selected ID */
  selectedId?: string;
  /** Callback when selection changes */
  onSelect: (item: KBlockExplorerItem) => void;
  /** Callback when layer expand/collapse changes */
  onToggleLayer: (section: ExplorerSection, layer: number) => void;
  /** Whether navigation is enabled */
  enabled?: boolean;
}

export interface UseKBlockNavigationReturn {
  /** Current focus target */
  focusTarget: FocusTarget | null;
  /** Set focus target programmatically */
  setFocusTarget: (target: FocusTarget | null) => void;
  /** Handle key down event */
  handleKeyDown: (e: KeyboardEvent) => void;
  /** Whether 'g' prefix is active (waiting for second key) */
  isGPrefixActive: boolean;
}

// =============================================================================
// Hook Implementation
// =============================================================================

export function useKBlockNavigation({
  constitutionalGroups,
  userGroups,
  orphans,
  selectedId,
  onSelect,
  onToggleLayer,
  enabled = true,
}: UseKBlockNavigationOptions): UseKBlockNavigationReturn {
  const [focusTarget, setFocusTarget] = useState<FocusTarget | null>(null);
  const [isGPrefixActive, setIsGPrefixActive] = useState(false);
  const gPrefixTimeoutRef = useRef<number | null>(null);

  // Build flat list of all navigable items for j/k navigation
  const getAllItems = useCallback((): Array<{
    item: KBlockExplorerItem;
    section: ExplorerSection;
    layerIndex: number;
  }> => {
    const items: Array<{
      item: KBlockExplorerItem;
      section: ExplorerSection;
      layerIndex: number;
    }> = [];

    // Constitutional items (only from expanded layers)
    constitutionalGroups.forEach((group, idx) => {
      if (group.expanded) {
        group.items.forEach((item) => {
          items.push({ item, section: 'constitutional', layerIndex: idx });
        });
      }
    });

    // User items (only from expanded layers)
    userGroups.forEach((group, idx) => {
      if (group.expanded) {
        group.items.forEach((item) => {
          items.push({ item, section: 'user', layerIndex: idx });
        });
      }
    });

    // Orphan items
    orphans.forEach((item) => {
      items.push({ item, section: 'orphans', layerIndex: -1 });
    });

    return items;
  }, [constitutionalGroups, userGroups, orphans]);

  // Find current item index
  const findCurrentIndex = useCallback((): number => {
    if (!focusTarget || focusTarget.type !== 'kblock') return -1;
    const items = getAllItems();
    return items.findIndex((entry) => entry.item.id === focusTarget.id);
  }, [focusTarget, getAllItems]);

  // Find item by ID
  const findItemById = useCallback(
    (id: string): { item: KBlockExplorerItem; section: ExplorerSection } | null => {
      // Check constitutional
      for (const group of constitutionalGroups) {
        const item = group.items.find((i) => i.id === id);
        if (item) return { item, section: 'constitutional' };
      }

      // Check user
      for (const group of userGroups) {
        const item = group.items.find((i) => i.id === id);
        if (item) return { item, section: 'user' };
      }

      // Check orphans
      const orphan = orphans.find((i) => i.id === id);
      if (orphan) return { item: orphan, section: 'orphans' };

      return null;
    },
    [constitutionalGroups, userGroups, orphans]
  );

  // Navigate to next/previous sibling (j/k or gj/gk)
  const navigateSibling = useCallback(
    (direction: 'next' | 'prev') => {
      const items = getAllItems();
      if (items.length === 0) return;

      const currentIndex = findCurrentIndex();

      let nextIndex: number;
      if (currentIndex === -1) {
        // No current focus, start from beginning or end
        nextIndex = direction === 'next' ? 0 : items.length - 1;
      } else {
        nextIndex =
          direction === 'next'
            ? Math.min(currentIndex + 1, items.length - 1)
            : Math.max(currentIndex - 1, 0);
      }

      const entry = items[nextIndex];
      if (entry) {
        setFocusTarget({ id: entry.item.id, type: 'kblock' });
      }
    },
    [getAllItems, findCurrentIndex]
  );

  // Navigate to parent (gh)
  const navigateToParent = useCallback(() => {
    if (!focusTarget || focusTarget.type !== 'kblock') return;

    const found = findItemById(focusTarget.id);
    if (!found) return;

    const { item } = found;

    // Find parent from derivesFrom
    if (item.derivesFrom.length > 0) {
      const parentId = item.derivesFrom[0]; // First parent
      const parent = findItemById(parentId);
      if (parent) {
        // Ensure parent's layer is expanded
        const group =
          parent.section === 'constitutional'
            ? constitutionalGroups.find((g) => g.items.some((i) => i.id === parentId))
            : userGroups.find((g) => g.items.some((i) => i.id === parentId));

        if (group && !group.expanded) {
          onToggleLayer(parent.section, group.config.layer);
        }

        setFocusTarget({ id: parentId, type: 'kblock' });
      }
    }
  }, [focusTarget, findItemById, constitutionalGroups, userGroups, onToggleLayer]);

  // Navigate to first child (gl)
  const navigateToChild = useCallback(() => {
    if (!focusTarget || focusTarget.type !== 'kblock') return;

    const found = findItemById(focusTarget.id);
    if (!found) return;

    // Find children (items that derive from this one)
    const allItems = [
      ...constitutionalGroups.flatMap((g) => g.items),
      ...userGroups.flatMap((g) => g.items),
      ...orphans,
    ];

    const children = allItems.filter((item) => item.derivesFrom.includes(focusTarget.id));

    if (children.length > 0) {
      const child = children[0];
      const childFound = findItemById(child.id);
      if (childFound) {
        // Ensure child's layer is expanded
        const group =
          childFound.section === 'constitutional'
            ? constitutionalGroups.find((g) => g.items.some((i) => i.id === child.id))
            : userGroups.find((g) => g.items.some((i) => i.id === child.id));

        if (group && !group.expanded) {
          onToggleLayer(childFound.section, group.config.layer);
        }

        setFocusTarget({ id: child.id, type: 'kblock' });
      }
    }
  }, [focusTarget, findItemById, constitutionalGroups, userGroups, orphans, onToggleLayer]);

  // Select currently focused item
  const selectFocused = useCallback(() => {
    if (!focusTarget || focusTarget.type !== 'kblock') return;

    const found = findItemById(focusTarget.id);
    if (found) {
      onSelect(found.item);
    }
  }, [focusTarget, findItemById, onSelect]);

  // Toggle expand/collapse of focused layer
  const toggleFocusedLayer = useCallback(() => {
    if (!focusTarget) return;

    if (focusTarget.type === 'layer') {
      // Parse layer section and number from ID: "constitutional-0" or "user-1"
      const [section, layerStr] = focusTarget.id.split('-');
      const layer = parseInt(layerStr, 10);
      if (!isNaN(layer)) {
        onToggleLayer(section as ExplorerSection, layer);
      }
    } else if (focusTarget.type === 'kblock') {
      // Find the layer this item belongs to and toggle it
      const found = findItemById(focusTarget.id);
      if (found && found.item.layer !== null) {
        onToggleLayer(found.section, found.item.layer);
      }
    }
  }, [focusTarget, findItemById, onToggleLayer]);

  // Handle key down
  const handleKeyDown = useCallback(
    (e: KeyboardEvent) => {
      if (!enabled) return;

      // Skip if in input or textarea
      const target = e.target as HTMLElement;
      if (target.tagName === 'INPUT' || target.tagName === 'TEXTAREA' || target.isContentEditable) {
        return;
      }

      // Handle 'g' prefix mode
      if (isGPrefixActive) {
        // Clear timeout
        if (gPrefixTimeoutRef.current) {
          window.clearTimeout(gPrefixTimeoutRef.current);
          gPrefixTimeoutRef.current = null;
        }

        setIsGPrefixActive(false);

        switch (e.key) {
          case 'h':
            e.preventDefault();
            navigateToParent();
            return;
          case 'l':
            e.preventDefault();
            navigateToChild();
            return;
          case 'j':
            e.preventDefault();
            navigateSibling('next');
            return;
          case 'k':
            e.preventDefault();
            navigateSibling('prev');
            return;
          case 'g': {
            // gg = go to top
            e.preventDefault();
            const items = getAllItems();
            if (items.length > 0) {
              setFocusTarget({ id: items[0].item.id, type: 'kblock' });
            }
            return;
          }
        }
        // Any other key cancels g-prefix
        return;
      }

      // Normal mode
      switch (e.key) {
        case 'g':
          // Start g-prefix mode
          e.preventDefault();
          setIsGPrefixActive(true);
          // Auto-cancel after 1 second
          gPrefixTimeoutRef.current = window.setTimeout(() => {
            setIsGPrefixActive(false);
          }, 1000);
          break;

        case 'j':
        case 'ArrowDown':
          e.preventDefault();
          navigateSibling('next');
          break;

        case 'k':
        case 'ArrowUp':
          e.preventDefault();
          navigateSibling('prev');
          break;

        case 'Enter':
          e.preventDefault();
          selectFocused();
          break;

        case ' ':
          e.preventDefault();
          toggleFocusedLayer();
          break;

        case 'G': {
          // Shift+G = go to bottom
          e.preventDefault();
          const allItems = getAllItems();
          if (allItems.length > 0) {
            setFocusTarget({
              id: allItems[allItems.length - 1].item.id,
              type: 'kblock',
            });
          }
          break;
        }
      }
    },
    [
      enabled,
      isGPrefixActive,
      navigateToParent,
      navigateToChild,
      navigateSibling,
      selectFocused,
      toggleFocusedLayer,
      getAllItems,
    ]
  );

  // Cleanup timeout on unmount
  useEffect(() => {
    return () => {
      if (gPrefixTimeoutRef.current) {
        window.clearTimeout(gPrefixTimeoutRef.current);
      }
    };
  }, []);

  // Sync focus target with selectedId
  useEffect(() => {
    if (selectedId && (!focusTarget || focusTarget.id !== selectedId)) {
      setFocusTarget({ id: selectedId, type: 'kblock' });
    }
  }, [selectedId, focusTarget]);

  return {
    focusTarget,
    setFocusTarget,
    handleKeyDown,
    isGPrefixActive,
  };
}

export default useKBlockNavigation;
