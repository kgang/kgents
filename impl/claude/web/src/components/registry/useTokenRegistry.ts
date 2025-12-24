/**
 * useTokenRegistry Hook - STUB IMPLEMENTATION
 *
 * The old spec ledger backend has been removed. This hook now returns
 * empty data to prevent breaking components that still reference it.
 *
 * Use the Document Director (/director) for document management.
 */

import { useCallback, useMemo, useState } from 'react';
import {
  type TokenItem,
  type TokenType,
  type TokenStatus,
  type FilterState,
  DEFAULT_FILTERS,
} from './types';

// Stub type for removed LedgerSummary
interface LedgerSummary {
  total_specs: number;
  active: number;
  orphans: number;
  deprecated: number;
  archived: number;
  total_claims: number;
  contradictions: number;
  harmonies: number;
}

// =============================================================================
// Types
// =============================================================================

export interface RegistryState {
  tokens: TokenItem[];
  filteredTokens: TokenItem[];
  summary: LedgerSummary | null;
  loading: boolean;
  error: string | null;
  filters: FilterState;
  selectedId: string | null;
  totalCount: number;
  filteredCount: number;
}

export interface RegistryActions {
  setFilters: (filters: FilterState) => void;
  updateFilter: <K extends keyof FilterState>(key: K, value: FilterState[K]) => void;
  clearFilters: () => void;
  setSearch: (query: string) => void;
  toggleType: (type: TokenType) => void;
  toggleStatus: (status: TokenStatus) => void;
  toggleTier: (tier: number) => void;
  toggleEvidence: () => void;
  setSelectedId: (id: string | null) => void;
  selectNext: () => void;
  selectPrev: () => void;
  selectNextRow: (columns: number) => void;
  selectPrevRow: (columns: number) => void;
  refresh: () => Promise<void>;
}

export type UseTokenRegistryResult = RegistryState & RegistryActions;

// =============================================================================
// Stub Hook (Spec Ledger API removed)
// =============================================================================

export function useTokenRegistry(): UseTokenRegistryResult {
  // Core state - all stubbed to empty
  const [tokens] = useState<TokenItem[]>([]);
  const [summary] = useState<LedgerSummary | null>(null);
  const [loading] = useState(false);
  const [error] = useState<string | null>(null);

  // Filter state
  const [filters, setFilters] = useState<FilterState>(DEFAULT_FILTERS);

  // Selection state
  const [selectedId, setSelectedId] = useState<string | null>(null);

  // Filtered tokens (always empty)
  const filteredTokens = useMemo(() => [] as TokenItem[], []);

  // ==========================================================================
  // Filter Actions
  // ==========================================================================

  const updateFilter = useCallback(<K extends keyof FilterState>(key: K, value: FilterState[K]) => {
    setFilters((prev) => ({ ...prev, [key]: value }));
  }, []);

  const clearFilters = useCallback(() => {
    setFilters(DEFAULT_FILTERS);
  }, []);

  const setSearch = useCallback((query: string) => {
    setFilters((prev) => ({ ...prev, search: query }));
  }, []);

  const toggleType = useCallback((type: TokenType) => {
    setFilters((prev) => {
      const types = prev.types.includes(type)
        ? prev.types.filter((t) => t !== type)
        : [...prev.types, type];
      return { ...prev, types };
    });
  }, []);

  const toggleStatus = useCallback((status: TokenStatus) => {
    setFilters((prev) => {
      const statuses = prev.statuses.includes(status)
        ? prev.statuses.filter((s) => s !== status)
        : [...prev.statuses, status];
      return { ...prev, statuses };
    });
  }, []);

  const toggleTier = useCallback((tier: number) => {
    setFilters((prev) => {
      const tiers = prev.tiers.includes(tier)
        ? prev.tiers.filter((t) => t !== tier)
        : [...prev.tiers, tier];
      return { ...prev, tiers };
    });
  }, []);

  const toggleEvidence = useCallback(() => {
    setFilters((prev) => {
      // Cycle: null → true → false → null
      const nextValue =
        prev.hasEvidence === null ? true : prev.hasEvidence === true ? false : null;
      return { ...prev, hasEvidence: nextValue };
    });
  }, []);

  // ==========================================================================
  // Selection Actions
  // ==========================================================================

  const selectNext = useCallback(() => {
    if (filteredTokens.length === 0) return;

    if (selectedId === null) {
      setSelectedId(filteredTokens[0].id);
      return;
    }

    const currentIndex = filteredTokens.findIndex((t) => t.id === selectedId);
    const nextIndex = Math.min(currentIndex + 1, filteredTokens.length - 1);
    setSelectedId(filteredTokens[nextIndex].id);
  }, [filteredTokens, selectedId]);

  const selectPrev = useCallback(() => {
    if (filteredTokens.length === 0) return;

    if (selectedId === null) {
      setSelectedId(filteredTokens[filteredTokens.length - 1].id);
      return;
    }

    const currentIndex = filteredTokens.findIndex((t) => t.id === selectedId);
    const prevIndex = Math.max(currentIndex - 1, 0);
    setSelectedId(filteredTokens[prevIndex].id);
  }, [filteredTokens, selectedId]);

  const selectNextRow = useCallback(
    (columns: number) => {
      if (filteredTokens.length === 0) return;

      if (selectedId === null) {
        setSelectedId(filteredTokens[0].id);
        return;
      }

      const currentIndex = filteredTokens.findIndex((t) => t.id === selectedId);
      const nextIndex = Math.min(currentIndex + columns, filteredTokens.length - 1);
      setSelectedId(filteredTokens[nextIndex].id);
    },
    [filteredTokens, selectedId]
  );

  const selectPrevRow = useCallback(
    (columns: number) => {
      if (filteredTokens.length === 0) return;

      if (selectedId === null) {
        setSelectedId(filteredTokens[filteredTokens.length - 1].id);
        return;
      }

      const currentIndex = filteredTokens.findIndex((t) => t.id === selectedId);
      const prevIndex = Math.max(currentIndex - columns, 0);
      setSelectedId(filteredTokens[prevIndex].id);
    },
    [filteredTokens, selectedId]
  );

  // Stub refresh function
  const refresh = useCallback(async () => {
    console.warn('useTokenRegistry: Spec ledger backend removed. Use Document Director instead.');
  }, []);

  // ==========================================================================
  // Return
  // ==========================================================================

  return {
    // State
    tokens,
    filteredTokens,
    summary,
    loading,
    error,
    filters,
    selectedId,
    totalCount: 0,
    filteredCount: 0,

    // Actions
    setFilters,
    updateFilter,
    clearFilters,
    setSearch,
    toggleType,
    toggleStatus,
    toggleTier,
    toggleEvidence,
    setSelectedId,
    selectNext,
    selectPrev,
    selectNextRow,
    selectPrevRow,
    refresh,
  };
}
