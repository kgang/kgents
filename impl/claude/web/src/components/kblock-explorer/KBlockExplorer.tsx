/**
 * KBlockExplorer — Main component for K-Block navigation
 *
 * "K-Blocks organized by layer (L0-L3 for Constitutional, L1-L7 for user)"
 * "Click to navigate to K-Block in editor"
 * "Keyboard navigation (gh/gl/gj/gk)"
 *
 * Replaces the traditional file tree with a K-Block-centric view:
 * - Fetches K-Blocks from API (genesis/clean-slate/graph endpoint)
 * - Constitutional section with 22 pre-seeded K-Blocks (read-only)
 * - User section organized by layer
 * - Layer badges with colors from LAYER_CONFIG
 * - Loss gauge next to each K-Block
 *
 * Re-render Isolation (2025-01-10):
 * - Uses useSelectedId() from context for highlighting (subscribes to state)
 * - This is a lightweight subscription - only the selectedId changes
 * - The entire component doesn't re-render when navigation occurs
 * - Only the tree items that need highlighting update
 *
 * @see spec/agents/k-block.md
 * @see docs/skills/metaphysical-fullstack.md
 */

import { memo, useCallback, useEffect, useMemo, useState } from 'react';
import { RefreshCw, AlertTriangle, Search } from 'lucide-react';
import { KBlockTree } from './KBlockTree';
import { useKBlockNavigation } from './hooks/useKBlockNavigation';
import { useSelectedId } from '../../hooks/useNavigationState';
import { genesisApi } from '../../api/client';
import type {
  KBlockExplorerProps,
  KBlockExplorerItem,
  KBlockLayerGroup,
  ExplorerSection,
  DerivationGraphResponse,
} from './types';
import { CONSTITUTIONAL_LAYER_CONFIG, USER_LAYER_CONFIG, toExplorerItem } from './types';
import './KBlockExplorer.css';

// =============================================================================
// Hook: useKBlockData
// =============================================================================

interface UseKBlockDataReturn {
  constitutionalGroups: KBlockLayerGroup[];
  userGroups: KBlockLayerGroup[];
  orphans: KBlockExplorerItem[];
  loading: boolean;
  error: Error | null;
  hasData: boolean;
  refresh: () => Promise<void>;
  toggleLayer: (section: ExplorerSection, layer: number) => void;
}

function useKBlockData(): UseKBlockDataReturn {
  const [graphData, setGraphData] = useState<DerivationGraphResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);
  const [expandedLayers, setExpandedLayers] = useState<Record<string, Set<number>>>({
    constitutional: new Set([0, 1, 2]), // Expand first 3 layers by default
    user: new Set([1, 2, 3]),
  });

  // Fetch K-Blocks from API
  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      // Fetch derivation graph from genesis API
      const graph = await genesisApi.getDerivationGraph();
      setGraphData(graph);
    } catch (err) {
      console.error('[KBlockExplorer] Failed to fetch K-Blocks:', err);
      setError(err instanceof Error ? err : new Error(String(err)));
    } finally {
      setLoading(false);
    }
  }, []);

  // Initial fetch
  useEffect(() => {
    void fetchData();
  }, [fetchData]);

  // Transform graph data into grouped structure
  const { constitutionalGroups, userGroups, orphans } = useMemo(() => {
    if (!graphData) {
      return {
        constitutionalGroups: CONSTITUTIONAL_LAYER_CONFIG.map((config) => ({
          config,
          items: [],
          expanded: expandedLayers.constitutional.has(config.layer),
        })),
        userGroups: USER_LAYER_CONFIG.map((config) => ({
          config,
          items: [],
          expanded: expandedLayers.user.has(config.layer),
        })),
        orphans: [],
      };
    }

    // Categorize nodes
    const constitutionalItems: KBlockExplorerItem[] = [];
    const userItems: KBlockExplorerItem[] = [];
    const orphanItems: KBlockExplorerItem[] = [];

    graphData.nodes.forEach((node) => {
      // Determine if constitutional (L0-L3 from genesis)
      const isConstitutional = node.layer <= 3;
      const item = toExplorerItem(node, isConstitutional);

      if (isConstitutional) {
        constitutionalItems.push(item);
      } else if (node.layer !== null && node.layer >= 1 && node.layer <= 7) {
        userItems.push(item);
      } else {
        orphanItems.push(item);
      }
    });

    // Group constitutional by layer
    const constitutionalGrouped = CONSTITUTIONAL_LAYER_CONFIG.map((config) => ({
      config,
      items: constitutionalItems.filter((i) => i.layer === config.layer),
      expanded: expandedLayers.constitutional.has(config.layer),
    }));

    // Group user by layer
    const userGrouped = USER_LAYER_CONFIG.map((config) => ({
      config,
      items: userItems.filter((i) => i.layer === config.layer),
      expanded: expandedLayers.user.has(config.layer),
    }));

    return {
      constitutionalGroups: constitutionalGrouped,
      userGroups: userGrouped,
      orphans: orphanItems,
    };
  }, [graphData, expandedLayers]);

  // Toggle layer expansion
  const toggleLayer = useCallback((section: ExplorerSection, layer: number) => {
    setExpandedLayers((prev) => {
      const sectionSet = new Set(prev[section] || []);
      if (sectionSet.has(layer)) {
        sectionSet.delete(layer);
      } else {
        sectionSet.add(layer);
      }
      return {
        ...prev,
        [section]: sectionSet,
      };
    });
  }, []);

  return {
    constitutionalGroups,
    userGroups,
    orphans,
    loading,
    error,
    hasData: graphData !== null,
    refresh: fetchData,
    toggleLayer,
  };
}

// =============================================================================
// Main Component
// =============================================================================

export const KBlockExplorer = memo(function KBlockExplorer({
  onSelect,
  selectedId: propsSelectedId,
  className = '',
}: KBlockExplorerProps) {
  const [searchQuery, setSearchQuery] = useState('');

  // Get selectedId from context (subscribes to navigation state)
  // Falls back to prop if provided (for backwards compatibility)
  const contextSelectedId = useSelectedId();
  const selectedId = propsSelectedId ?? contextSelectedId;
  const {
    constitutionalGroups,
    userGroups,
    orphans,
    loading,
    error,
    hasData,
    refresh,
    toggleLayer,
  } = useKBlockData();

  // Handle selection
  const handleSelect = useCallback(
    (item: KBlockExplorerItem) => {
      onSelect(item);
    },
    [onSelect]
  );

  // Filter items by search query
  const filteredGroups = useMemo(() => {
    if (!searchQuery.trim()) {
      return { constitutionalGroups, userGroups, orphans };
    }

    const query = searchQuery.toLowerCase();
    const filterItems = (items: KBlockExplorerItem[]) =>
      items.filter(
        (item) =>
          item.title.toLowerCase().includes(query) ||
          item.path.toLowerCase().includes(query) ||
          item.tags.some((tag) => tag.toLowerCase().includes(query))
      );

    return {
      constitutionalGroups: constitutionalGroups.map((g) => ({
        ...g,
        items: filterItems(g.items),
        expanded: searchQuery ? true : g.expanded, // Auto-expand when searching
      })),
      userGroups: userGroups.map((g) => ({
        ...g,
        items: filterItems(g.items),
        expanded: searchQuery ? true : g.expanded,
      })),
      orphans: filterItems(orphans),
    };
  }, [constitutionalGroups, userGroups, orphans, searchQuery]);

  // Navigation hook
  const { focusTarget, setFocusTarget, handleKeyDown, isGPrefixActive } = useKBlockNavigation({
    constitutionalGroups: filteredGroups.constitutionalGroups,
    userGroups: filteredGroups.userGroups,
    orphans: filteredGroups.orphans,
    selectedId,
    onSelect: handleSelect,
    onToggleLayer: toggleLayer,
    enabled: true,
  });

  // Attach keyboard handler
  useEffect(() => {
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [handleKeyDown]);

  return (
    <div className={`kbe ${className}`}>
      {/* Header */}
      <header className="kbe__header">
        <h2 className="kbe__title">K-Blocks</h2>
        <div className="kbe__actions">
          <button
            className="kbe__refresh-btn"
            onClick={() => void refresh()}
            disabled={loading}
            title="Refresh K-Blocks"
            aria-label="Refresh K-Blocks"
          >
            <RefreshCw size={14} className={loading ? 'kbe__refresh-icon--spinning' : ''} />
          </button>
        </div>
      </header>

      {/* Search */}
      <div className="kbe__search">
        <Search size={14} className="kbe__search-icon" />
        <input
          type="text"
          className="kbe__search-input"
          placeholder="Search K-Blocks..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
        />
        {isGPrefixActive && (
          <span className="kbe__nav-hint" title="Waiting for g+key (h/l/j/k)">
            g-
          </span>
        )}
      </div>

      {/* Content */}
      <div className="kbe__content">
        {/* Loading state */}
        {loading && !hasData && (
          <div className="kbe__loading">
            <RefreshCw size={20} className="kbe__refresh-icon--spinning" />
            <span className="kbe__loading-text">Loading K-Blocks...</span>
          </div>
        )}

        {/* Error state */}
        {error && (
          <div className="kbe__error">
            <AlertTriangle size={16} />
            <span className="kbe__error-text">Failed to load K-Blocks</span>
            <button className="kbe__retry-btn" onClick={() => void refresh()}>
              Retry
            </button>
          </div>
        )}

        {/* Tree view */}
        {!loading && !error && (
          <KBlockTree
            constitutionalGroups={filteredGroups.constitutionalGroups}
            userGroups={filteredGroups.userGroups}
            orphans={filteredGroups.orphans}
            selectedId={selectedId}
            focusTarget={focusTarget}
            onSelect={handleSelect}
            onToggleLayer={toggleLayer}
            onFocusChange={setFocusTarget}
          />
        )}
      </div>

      {/* Footer with navigation hints */}
      <footer className="kbe__footer">
        <span className="kbe__nav-keys">
          <kbd>j</kbd>/<kbd>k</kbd> move
        </span>
        <span className="kbe__nav-keys">
          <kbd>g</kbd>+<kbd>h</kbd>/<kbd>l</kbd> parent/child
        </span>
      </footer>
    </div>
  );
});

export default KBlockExplorer;
