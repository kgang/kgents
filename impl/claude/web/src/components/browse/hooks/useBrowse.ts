/**
 * useBrowse — Browse modal state management
 *
 * Manages search, filtering, and keyboard navigation for BrowseModal.
 * Follows keyboard-first philosophy (j/k nav, 1-5 category switching).
 */

import { useCallback, useEffect, useMemo, useState } from 'react';
import type { BrowseCategory, BrowseFilter, BrowseItem } from '../types';

// =============================================================================
// Types
// =============================================================================

interface UseBrowseOptions {
  initialCategory?: BrowseCategory;
  initialQuery?: string;
  items: BrowseItem[];
}

interface UseBrowseReturn {
  // Search & filters
  query: string;
  setQuery: (query: string) => void;
  category: BrowseCategory;
  setCategory: (category: BrowseCategory) => void;
  filters: BrowseFilter;
  toggleFilter: (key: keyof BrowseFilter) => void;

  // Results
  filteredItems: BrowseItem[];
  selectedIndex: number;
  setSelectedIndex: (index: number) => void;
  selectedItem: BrowseItem | null;

  // Category counts
  categoryCounts: Record<BrowseCategory, number>;

  // Navigation
  selectNext: () => void;
  selectPrevious: () => void;
  selectFirst: () => void;
  selectLast: () => void;

  // Keyboard handler (attach to window)
  handleKeyDown: (e: KeyboardEvent) => void;
}

// =============================================================================
// Hook
// =============================================================================

export function useBrowse({
  initialCategory = 'all',
  initialQuery = '',
  items,
}: UseBrowseOptions): UseBrowseReturn {
  // Search & filter state
  const [query, setQuery] = useState(initialQuery);
  const [category, setCategory] = useState<BrowseCategory>(initialCategory);
  const [filters, setFilters] = useState<BrowseFilter>({
    modifiedToday: false,
    hasAnnotations: false,
    unread: false,
  });

  // Selection state
  const [selectedIndex, setSelectedIndex] = useState(0);

  // Toggle filter
  const toggleFilter = useCallback((key: keyof BrowseFilter) => {
    setFilters((prev: BrowseFilter) => ({ ...prev, [key]: !prev[key] }));
    setSelectedIndex(0); // Reset selection when filters change
  }, []);

  // Category counts (for badges)
  const categoryCounts = useMemo(() => {
    const counts: Record<BrowseCategory, number> = {
      all: items.length,
      files: 0,
      docs: 0,
      specs: 0,
      kblocks: 0,
      uploads: 0,
      'zero-seed': 0,
      convos: 0,
    };

    for (const item of items) {
      if (item.category in counts) {
        counts[item.category] += 1;
      }
    }

    return counts;
  }, [items]);

  // Filtered & sorted items
  const filteredItems = useMemo(() => {
    let result = [...items];

    // Category filter
    if (category !== 'all') {
      result = result.filter((item) => item.category === category);
    }

    // Search filter
    if (query.trim()) {
      const q = query.toLowerCase();
      result = result.filter(
        (item) =>
          item.title.toLowerCase().includes(q) ||
          item.path.toLowerCase().includes(q) ||
          item.preview?.toLowerCase().includes(q)
      );
    }

    // Additional filters
    if (filters.modifiedToday) {
      const today = new Date();
      today.setHours(0, 0, 0, 0);
      result = result.filter(
        (item) => item.modifiedAt && new Date(item.modifiedAt) >= today
      );
    }

    if (filters.hasAnnotations) {
      result = result.filter((item) => (item.annotations ?? 0) > 0);
    }

    // Sort by modified date (most recent first)
    result.sort((a, b) => {
      const at = a.modifiedAt ? new Date(a.modifiedAt).getTime() : 0;
      const bt = b.modifiedAt ? new Date(b.modifiedAt).getTime() : 0;
      return bt - at;
    });

    return result;
  }, [items, category, query, filters]);

  // Selected item
  const selectedItem = filteredItems[selectedIndex] ?? null;

  // Navigation functions
  const selectNext = useCallback(() => {
    setSelectedIndex((i) => Math.min(i + 1, filteredItems.length - 1));
  }, [filteredItems.length]);

  const selectPrevious = useCallback(() => {
    setSelectedIndex((i) => Math.max(i - 1, 0));
  }, []);

  const selectFirst = useCallback(() => {
    setSelectedIndex(0);
  }, []);

  const selectLast = useCallback(() => {
    setSelectedIndex(filteredItems.length - 1);
  }, [filteredItems.length]);

  // Keyboard handler
  const handleKeyDown = useCallback(
    (e: KeyboardEvent) => {
      // Ignore if typing in input (handled by modal)
      if (
        e.target instanceof HTMLInputElement ||
        e.target instanceof HTMLTextAreaElement
      ) {
        return;
      }

      switch (e.key) {
        // Navigation (j/k or arrows)
        case 'j':
        case 'ArrowDown':
          e.preventDefault();
          selectNext();
          break;
        case 'k':
        case 'ArrowUp':
          e.preventDefault();
          selectPrevious();
          break;

        // Jump to start/end (g/G)
        case 'g':
          e.preventDefault();
          if (e.shiftKey) {
            selectLast(); // G
          } else {
            selectFirst(); // g
          }
          break;

        // Category switching (1-8)
        case '1':
          e.preventDefault();
          setCategory('all');
          setSelectedIndex(0);
          break;
        case '2':
          e.preventDefault();
          setCategory('files');
          setSelectedIndex(0);
          break;
        case '3':
          e.preventDefault();
          setCategory('docs');
          setSelectedIndex(0);
          break;
        case '4':
          e.preventDefault();
          setCategory('specs');
          setSelectedIndex(0);
          break;
        case '5':
          e.preventDefault();
          setCategory('kblocks');
          setSelectedIndex(0);
          break;
        case '6':
          e.preventDefault();
          setCategory('uploads');
          setSelectedIndex(0);
          break;
        case '7':
          e.preventDefault();
          setCategory('zero-seed');
          setSelectedIndex(0);
          break;
        case '8':
          e.preventDefault();
          setCategory('convos');
          setSelectedIndex(0);
          break;
      }
    },
    [selectNext, selectPrevious, selectFirst, selectLast]
  );

  // Reset selection when results change
  useEffect(() => {
    if (selectedIndex >= filteredItems.length) {
      setSelectedIndex(Math.max(0, filteredItems.length - 1));
    }
  }, [filteredItems.length, selectedIndex]);

  return {
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
    selectNext,
    selectPrevious,
    selectFirst,
    selectLast,
    handleKeyDown,
  };
}
