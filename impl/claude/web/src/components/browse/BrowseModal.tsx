/**
 * BrowseModal — Full-screen content browser
 *
 * Triggered by Ctrl+O. Exhaustive browser for all content types:
 * files, docs, specs, k-blocks, conversations.
 *
 * Features:
 * - Real-time search filtering
 * - Category tabs with counts
 * - Keyboard-first navigation (j/k, 1-5, Enter, Escape)
 * - Sidebar filters (modified today, has annotations)
 * - Result preview with metadata
 *
 * Philosophy:
 * - "Tasteful > feature-complete"
 * - STARK BIOME: 90% steel, 10% earned glow
 * - Keyboard navigation beats clicking
 */

import { memo, useCallback, useEffect, useRef } from 'react';
import type { BrowseCategory, BrowseItem } from './types';
import { useBrowse } from './hooks/useBrowse';

import './BrowseModal.css';

// =============================================================================
// Category Config
// =============================================================================

const CATEGORY_CONFIG: Record<
  BrowseCategory,
  { label: string; icon: string; shortcut: string }
> = {
  all: { label: 'All', icon: '📚', shortcut: '1' },
  files: { label: 'Files', icon: '📄', shortcut: '2' },
  docs: { label: 'Docs', icon: '📖', shortcut: '3' },
  specs: { label: 'Specs', icon: '📋', shortcut: '4' },
  kblocks: { label: 'K-Blocks', icon: '📦', shortcut: '5' },
  convos: { label: 'Convos', icon: '💬', shortcut: '6' },
};

// =============================================================================
// Props
// =============================================================================

export interface BrowseModalProps {
  open: boolean;
  onClose: () => void;
  onSelectItem: (item: BrowseItem) => void;
  /** Items to display in the browser */
  items?: BrowseItem[];
  /** Loading state */
  loading?: boolean;
  initialCategory?: BrowseCategory;
  initialQuery?: string;
}

// =============================================================================
// Component
// =============================================================================

export const BrowseModal = memo(function BrowseModal({
  open,
  onClose,
  onSelectItem,
  items = [],
  loading = false,
  initialCategory = 'all',
  initialQuery = '',
}: BrowseModalProps) {
  const searchRef = useRef<HTMLInputElement>(null);
  const resultsRef = useRef<HTMLDivElement>(null);

  // Browse state management
  const {
    query,
    setQuery,
    category,
    setCategory,
    filters,
    toggleFilter,
    filteredItems,
    selectedIndex,
    setSelectedIndex,
    selectedItem,
    categoryCounts,
    handleKeyDown,
  } = useBrowse({
    initialCategory,
    initialQuery,
    items,
  });

  // Focus search on open
  useEffect(() => {
    if (open) {
      requestAnimationFrame(() => {
        searchRef.current?.focus();
      });
    }
  }, [open]);

  // Keyboard navigation
  useEffect(() => {
    if (!open) return;

    const handleKey = (e: KeyboardEvent) => {
      // Escape closes modal
      if (e.key === 'Escape') {
        e.preventDefault();
        onClose();
        return;
      }

      // Enter selects current item
      if (e.key === 'Enter' && selectedItem) {
        e.preventDefault();
        onSelectItem(selectedItem);
        onClose();
        return;
      }

      // Slash focuses search
      if (e.key === '/' && document.activeElement !== searchRef.current) {
        e.preventDefault();
        searchRef.current?.focus();
        return;
      }

      // Delegate other keys to browse hook
      handleKeyDown(e);
    };

    window.addEventListener('keydown', handleKey);
    return () => window.removeEventListener('keydown', handleKey);
  }, [open, selectedItem, onSelectItem, onClose, handleKeyDown]);

  // Scroll selected item into view
  useEffect(() => {
    if (!resultsRef.current) return;
    const selected = resultsRef.current.querySelector(`[data-index="${selectedIndex}"]`);
    if (selected) {
      selected.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
    }
  }, [selectedIndex]);

  // Handle backdrop click
  const handleBackdropClick = useCallback(
    (e: React.MouseEvent) => {
      if (e.target === e.currentTarget) {
        onClose();
      }
    },
    [onClose]
  );

  // Handle item click
  const handleItemClick = useCallback(
    (_item: BrowseItem, index: number) => {
      setSelectedIndex(index);
    },
    [setSelectedIndex]
  );

  // Handle item double-click
  const handleItemDoubleClick = useCallback(
    (item: BrowseItem) => {
      onSelectItem(item);
      onClose();
    },
    [onSelectItem, onClose]
  );

  if (!open) return null;

  return (
    <div className="browse-modal__overlay" onClick={handleBackdropClick}>
      <div className="browse-modal" onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className="browse-modal__header">
          <span className="browse-modal__title">Browse All</span>
          <button
            className="browse-modal__close"
            onClick={onClose}
            aria-label="Close"
          >
            ×
          </button>
        </div>

        {/* Search bar */}
        <div className="browse-modal__search">
          <span className="browse-modal__search-icon">🔍</span>
          <input
            ref={searchRef}
            type="text"
            className="browse-modal__search-input"
            placeholder="Search everything..."
            value={query}
            onChange={(e) => {
              setQuery(e.target.value);
              setSelectedIndex(0);
            }}
            autoComplete="off"
            autoCorrect="off"
            autoCapitalize="off"
            spellCheck={false}
          />
        </div>

        {/* Main content area */}
        <div className="browse-modal__body">
          {/* Sidebar: Categories & Filters */}
          <aside className="browse-modal__sidebar">
            <div className="browse-modal__section">
              <div className="browse-modal__section-title">CATEGORIES</div>
              {(Object.keys(CATEGORY_CONFIG) as BrowseCategory[]).map((cat) => {
                const config = CATEGORY_CONFIG[cat];
                const count = categoryCounts[cat];
                const isActive = category === cat;

                return (
                  <button
                    key={cat}
                    className={`browse-modal__category ${isActive ? 'browse-modal__category--active' : ''}`}
                    onClick={() => {
                      setCategory(cat);
                      setSelectedIndex(0);
                    }}
                  >
                    <span className="browse-modal__category-icon">{config.icon}</span>
                    <span className="browse-modal__category-label">{config.label}</span>
                    <span className="browse-modal__category-count">{count}</span>
                    <kbd className="browse-modal__category-shortcut">{config.shortcut}</kbd>
                  </button>
                );
              })}
            </div>

            <div className="browse-modal__section">
              <div className="browse-modal__section-title">FILTERS</div>
              <label className="browse-modal__filter">
                <input
                  type="checkbox"
                  checked={filters.modifiedToday}
                  onChange={() => toggleFilter('modifiedToday')}
                />
                <span>Modified today</span>
              </label>
              <label className="browse-modal__filter">
                <input
                  type="checkbox"
                  checked={filters.hasAnnotations}
                  onChange={() => toggleFilter('hasAnnotations')}
                />
                <span>Has annotations</span>
              </label>
            </div>
          </aside>

          {/* Main: Results list */}
          <main className="browse-modal__main">
            <div className="browse-modal__results-header">
              <span className="browse-modal__results-count">
                {loading ? 'Loading...' : `Showing ${filteredItems.length} of ${items.length} results`}
              </span>
            </div>

            <div className="browse-modal__results" ref={resultsRef}>
              {loading ? (
                <div className="browse-modal__loading">
                  <div className="browse-modal__spinner" />
                  <span>Loading files...</span>
                </div>
              ) : filteredItems.length === 0 ? (
                <div className="browse-modal__empty">
                  {items.length === 0 ? (
                    <>
                      <p>No files indexed yet</p>
                      <span className="browse-modal__empty-hint">
                        Open files to populate the browser
                      </span>
                    </>
                  ) : (
                    <>
                      <p>No results found</p>
                      <span className="browse-modal__empty-hint">
                        Try a different search or category
                      </span>
                    </>
                  )}
                </div>
              ) : (
                filteredItems.map((item, index) => {
                  const isSelected = index === selectedIndex;
                  const icon = CATEGORY_CONFIG[item.category]?.icon ?? '📄';

                  return (
                    <div
                      key={item.id}
                      data-index={index}
                      className={`browse-modal__item ${isSelected ? 'browse-modal__item--selected' : ''}`}
                      onClick={() => handleItemClick(item, index)}
                      onDoubleClick={() => handleItemDoubleClick(item)}
                    >
                      <div className="browse-modal__item-header">
                        <span className="browse-modal__item-icon">{icon}</span>
                        <span className="browse-modal__item-title">{item.title}</span>
                        {item.directory && (
                          <span className="browse-modal__item-directory">
                            {item.directory}
                          </span>
                        )}
                        {item.annotations && item.annotations > 0 && (
                          <span className="browse-modal__item-badge">
                            {item.annotations} notes
                          </span>
                        )}
                      </div>
                      {item.preview && (
                        <div className="browse-modal__item-preview">{item.preview}</div>
                      )}
                    </div>
                  );
                })
              )}
            </div>
          </main>
        </div>

        {/* Footer: Keyboard hints */}
        <div className="browse-modal__footer">
          <div className="browse-modal__hints">
            <span>
              <kbd>j</kbd>/<kbd>k</kbd> navigate
            </span>
            <span className="browse-modal__separator">•</span>
            <span>
              <kbd>1-5</kbd> categories
            </span>
            <span className="browse-modal__separator">•</span>
            <span>
              <kbd>Enter</kbd> select
            </span>
            <span className="browse-modal__separator">•</span>
            <span>
              <kbd>Esc</kbd> close
            </span>
          </div>
        </div>
      </div>
    </div>
  );
});

export default BrowseModal;
