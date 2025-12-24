/**
 * useChartInteraction — Centralized interaction state
 *
 * Manages hover, selection, search, and keyboard navigation.
 * Vim-inspired: j/k to cycle, / to search, Enter to select.
 *
 * "The file is a lie. There is only the graph."
 */

import { useState, useCallback, useEffect, useMemo } from 'react';
import type { StarData } from './useAstronomicalData';

// =============================================================================
// Types
// =============================================================================

export interface InteractionState {
  /** Currently hovered star */
  hovered: StarData | null;
  /** Currently selected star */
  selected: StarData | null;
  /** Search query */
  searchQuery: string;
  /** Search results (matching star IDs) */
  searchResults: string[];
  /** Index of focused result in search */
  focusedResultIndex: number;
  /** Whether search input is focused */
  searchFocused: boolean;
}

export interface InteractionActions {
  setHovered: (star: StarData | null) => void;
  setSelected: (star: StarData | null) => void;
  clearSelection: () => void;
  search: (query: string) => void;
  clearSearch: () => void;
  nextResult: () => void;
  prevResult: () => void;
  selectFocusedResult: () => void;
  setSearchFocused: (focused: boolean) => void;
  /** Cycle through all stars (vim j/k) */
  cycleNext: () => void;
  cyclePrev: () => void;
}

export interface UseChartInteractionOptions {
  /** All stars for cycling and searching */
  stars: StarData[];
  /** Callback when selection changes */
  onSelectionChange?: (star: StarData | null) => void;
}

export interface UseChartInteractionReturn {
  state: InteractionState;
  actions: InteractionActions;
  /** Get keyboard event handler for chart container */
  keyboardHandler: (e: KeyboardEvent) => void;
}

// =============================================================================
// Hook
// =============================================================================

export function useChartInteraction(
  options: UseChartInteractionOptions
): UseChartInteractionReturn {
  const { stars, onSelectionChange } = options;

  // State
  const [hovered, setHoveredState] = useState<StarData | null>(null);
  const [selected, setSelectedState] = useState<StarData | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [focusedResultIndex, setFocusedResultIndex] = useState(0);
  const [searchFocused, setSearchFocused] = useState(false);

  // Compute search results
  const searchResults = useMemo(() => {
    if (!searchQuery.trim()) return [];

    const query = searchQuery.toLowerCase();
    return stars
      .filter(
        (star) =>
          star.label.toLowerCase().includes(query) || star.path.toLowerCase().includes(query)
      )
      .map((star) => star.id);
  }, [stars, searchQuery]);

  // Reset focused index when results change
  useEffect(() => {
    setFocusedResultIndex(0);
  }, [searchResults.length]);

  // Notify on selection change
  useEffect(() => {
    onSelectionChange?.(selected);
  }, [selected, onSelectionChange]);

  // Star lookup for cycling
  const starById = useMemo(() => {
    const map = new Map<string, StarData>();
    stars.forEach((s) => map.set(s.id, s));
    return map;
  }, [stars]);

  // Actions
  const setHovered = useCallback((star: StarData | null) => {
    setHoveredState(star);
  }, []);

  const setSelected = useCallback((star: StarData | null) => {
    setSelectedState(star);
  }, []);

  const clearSelection = useCallback(() => {
    setSelectedState(null);
  }, []);

  const search = useCallback((query: string) => {
    setSearchQuery(query);
  }, []);

  const clearSearch = useCallback(() => {
    setSearchQuery('');
    setFocusedResultIndex(0);
  }, []);

  const nextResult = useCallback(() => {
    if (searchResults.length === 0) return;
    setFocusedResultIndex((prev) => (prev + 1) % searchResults.length);
  }, [searchResults.length]);

  const prevResult = useCallback(() => {
    if (searchResults.length === 0) return;
    setFocusedResultIndex((prev) => (prev === 0 ? searchResults.length - 1 : prev - 1));
  }, [searchResults.length]);

  const selectFocusedResult = useCallback(() => {
    if (searchResults.length === 0) return;
    const id = searchResults[focusedResultIndex];
    const star = starById.get(id);
    if (star) {
      setSelectedState(star);
      setHoveredState(star);
    }
  }, [searchResults, focusedResultIndex, starById]);

  // Cycle through all stars (vim j/k style)
  const cycleNext = useCallback(() => {
    if (stars.length === 0) return;

    const currentIndex = selected ? stars.findIndex((s) => s.id === selected.id) : -1;
    const nextIndex = (currentIndex + 1) % stars.length;
    const nextStar = stars[nextIndex];
    setSelectedState(nextStar);
    setHoveredState(nextStar);
  }, [stars, selected]);

  const cyclePrev = useCallback(() => {
    if (stars.length === 0) return;

    const currentIndex = selected ? stars.findIndex((s) => s.id === selected.id) : 0;
    const prevIndex = currentIndex === 0 ? stars.length - 1 : currentIndex - 1;
    const prevStar = stars[prevIndex];
    setSelectedState(prevStar);
    setHoveredState(prevStar);
  }, [stars, selected]);

  // Keyboard handler
  const keyboardHandler = useCallback(
    (e: KeyboardEvent) => {
      // Don't handle if typing in search input
      if (searchFocused && e.key !== 'Escape' && e.key !== 'Enter') {
        return;
      }

      switch (e.key) {
        case 'j':
          e.preventDefault();
          if (searchResults.length > 0) {
            nextResult();
          } else {
            cycleNext();
          }
          break;

        case 'k':
          e.preventDefault();
          if (searchResults.length > 0) {
            prevResult();
          } else {
            cyclePrev();
          }
          break;

        case '/':
          e.preventDefault();
          setSearchFocused(true);
          break;

        case 'Enter':
          e.preventDefault();
          if (searchResults.length > 0) {
            selectFocusedResult();
          }
          break;

        case 'Escape':
          e.preventDefault();
          if (searchFocused) {
            setSearchFocused(false);
            clearSearch();
          } else if (selected) {
            clearSelection();
          }
          break;

        case 'n':
          // Next search result (vim-style)
          if (searchResults.length > 0) {
            e.preventDefault();
            nextResult();
          }
          break;

        case 'N':
          // Previous search result (vim-style)
          if (searchResults.length > 0) {
            e.preventDefault();
            prevResult();
          }
          break;
      }
    },
    [
      searchFocused,
      searchResults.length,
      nextResult,
      prevResult,
      cycleNext,
      cyclePrev,
      selectFocusedResult,
      clearSearch,
      clearSelection,
      selected,
    ]
  );

  // Build state object
  const state: InteractionState = {
    hovered,
    selected,
    searchQuery,
    searchResults,
    focusedResultIndex,
    searchFocused,
  };

  // Build actions object
  const actions: InteractionActions = {
    setHovered,
    setSelected,
    clearSelection,
    search,
    clearSearch,
    nextResult,
    prevResult,
    selectFocusedResult,
    setSearchFocused,
    cycleNext,
    cyclePrev,
  };

  return {
    state,
    actions,
    keyboardHandler,
  };
}

export default useChartInteraction;
