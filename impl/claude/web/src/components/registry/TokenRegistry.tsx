/**
 * TokenRegistry - Main virtualized grid container
 *
 * Utilitarian flat grid for navigating 100s of specs,
 * dozens of principles, and 1000s of implementations.
 *
 * Features:
 * - Virtualized rendering (handles 1000s of items at 60fps)
 * - Responsive grid (auto-columns based on width)
 * - Vim-style keyboard navigation
 * - Slide-out detail panel
 *
 * "The frame is humble. The content glows."
 */

import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { useVirtualizer } from '@tanstack/react-virtual';

import { useTokenRegistry } from './useTokenRegistry';
import { useTokenKeyboard } from './useTokenKeyboard';
import { TokenFilters } from './TokenFilters';
import { TokenTile } from './TokenTile';
import { TokenDetailPanel } from './TokenDetailPanel';

import './TokenRegistry.css';

// =============================================================================
// Constants
// =============================================================================

const TILE_WIDTH = 160;
const TILE_HEIGHT = 32;
const TILE_GAP = 8;

// =============================================================================
// Types
// =============================================================================

interface TokenRegistryProps {
  onOpenEditor?: (path: string) => void;
}

// =============================================================================
// Component
// =============================================================================

export function TokenRegistry({ onOpenEditor }: TokenRegistryProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const gridRef = useRef<HTMLDivElement>(null);
  const [containerWidth, setContainerWidth] = useState(800);
  const [detailPath, setDetailPath] = useState<string | null>(null);
  const [searchFocused, setSearchFocused] = useState(false);

  // Registry hook
  const registry = useTokenRegistry();

  // Calculate columns based on container width
  const columns = useMemo(() => {
    return Math.max(1, Math.floor((containerWidth + TILE_GAP) / (TILE_WIDTH + TILE_GAP)));
  }, [containerWidth]);

  // Calculate rows
  const rowCount = useMemo(() => {
    return Math.ceil(registry.filteredTokens.length / columns);
  }, [registry.filteredTokens.length, columns]);

  // Virtualizer
  const rowVirtualizer = useVirtualizer({
    count: rowCount,
    getScrollElement: () => gridRef.current,
    estimateSize: () => TILE_HEIGHT + TILE_GAP,
    overscan: 5,
  });

  // Resize observer for responsive columns
  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    const observer = new ResizeObserver((entries) => {
      const entry = entries[0];
      if (entry) {
        setContainerWidth(entry.contentRect.width);
      }
    });

    observer.observe(container);
    return () => observer.disconnect();
  }, []);

  // Keyboard navigation
  const handleOpenDetail = useCallback((id: string) => {
    setDetailPath(id);
  }, []);

  const handleCloseDetail = useCallback(() => {
    setDetailPath(null);
  }, []);

  const handleOpenInEditor = useCallback(
    (path: string) => {
      onOpenEditor?.(path);
    },
    [onOpenEditor]
  );

  // Note: focusSearch can be exposed if needed for external triggers
  useTokenKeyboard({
    enabled: !searchFocused && !detailPath,
    columns,
    selectedId: registry.selectedId,
    filteredTokens: registry.filteredTokens,
    onSelectNext: registry.selectNext,
    onSelectPrev: registry.selectPrev,
    onSelectNextRow: () => registry.selectNextRow(columns),
    onSelectPrevRow: () => registry.selectPrevRow(columns),
    onOpenDetail: handleOpenDetail,
    onOpenEditor: handleOpenInEditor,
    onCloseDetail: handleCloseDetail,
  });

  // Handle tile click
  const handleTileClick = useCallback(
    (id: string) => {
      registry.setSelectedId(id);
    },
    [registry]
  );

  const handleTileDoubleClick = useCallback(
    (id: string) => {
      setDetailPath(id);
    },
    []
  );

  // Scroll selected into view
  useEffect(() => {
    if (!registry.selectedId || !gridRef.current) return;

    const index = registry.filteredTokens.findIndex((t) => t.id === registry.selectedId);
    if (index === -1) return;

    const rowIndex = Math.floor(index / columns);
    rowVirtualizer.scrollToIndex(rowIndex, { align: 'auto' });
  }, [registry.selectedId, registry.filteredTokens, columns, rowVirtualizer]);

  // ==========================================================================
  // Render
  // ==========================================================================

  if (registry.loading) {
    return (
      <div className="token-registry token-registry--loading">
        <div className="token-registry__loader">
          <span className="token-registry__loader-icon">◈</span>
          <span>Loading registry...</span>
        </div>
      </div>
    );
  }

  if (registry.error) {
    return (
      <div className="token-registry token-registry--error">
        <div className="token-registry__error">
          <p>{registry.error}</p>
          <button onClick={registry.refresh}>Retry</button>
        </div>
      </div>
    );
  }

  return (
    <div className="token-registry" ref={containerRef}>
      {/* Filters */}
      <TokenFilters
        filters={registry.filters}
        totalCount={registry.totalCount}
        filteredCount={registry.filteredCount}
        onSearchChange={registry.setSearch}
        onToggleType={registry.toggleType}
        onToggleStatus={registry.toggleStatus}
        onToggleTier={registry.toggleTier}
        onToggleEvidence={registry.toggleEvidence}
        onClear={registry.clearFilters}
        searchFocused={searchFocused}
        onSearchFocus={() => setSearchFocused(true)}
        onSearchBlur={() => setSearchFocused(false)}
      />

      {/* Grid */}
      <div className="token-registry__grid" ref={gridRef}>
        {registry.filteredTokens.length === 0 ? (
          <div className="token-registry__empty">
            <span className="token-registry__empty-icon">○</span>
            <p>No tokens match your filters</p>
            <button onClick={registry.clearFilters}>Clear Filters</button>
          </div>
        ) : (
          <div
            className="token-registry__grid-inner"
            style={{
              height: `${rowVirtualizer.getTotalSize()}px`,
              position: 'relative',
            }}
          >
            {rowVirtualizer.getVirtualItems().map((virtualRow) => {
              const startIndex = virtualRow.index * columns;
              const rowTokens = registry.filteredTokens.slice(startIndex, startIndex + columns);

              return (
                <div
                  key={virtualRow.key}
                  className="token-registry__row"
                  style={{
                    position: 'absolute',
                    top: 0,
                    left: 0,
                    width: '100%',
                    height: `${virtualRow.size}px`,
                    transform: `translateY(${virtualRow.start}px)`,
                  }}
                >
                  {rowTokens.map((token) => (
                    <TokenTile
                      key={token.id}
                      token={token}
                      selected={token.id === registry.selectedId}
                      onClick={() => handleTileClick(token.id)}
                      onDoubleClick={() => handleTileDoubleClick(token.id)}
                    />
                  ))}
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Keyboard Hints */}
      <div className="token-registry__hints">
        <span>
          <kbd>j</kbd>/<kbd>k</kbd> nav
        </span>
        <span>
          <kbd>Enter</kbd> details
        </span>
        <span>
          <kbd>e</kbd> edit
        </span>
        <span>
          <kbd>/</kbd> search
        </span>
        <span>
          <kbd>?</kbd> help
        </span>
      </div>

      {/* Detail Panel */}
      {detailPath && (
        <TokenDetailPanel
          path={detailPath}
          onClose={handleCloseDetail}
          onOpenEditor={handleOpenInEditor}
        />
      )}
    </div>
  );
}
