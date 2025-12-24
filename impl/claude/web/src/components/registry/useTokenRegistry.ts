/**
 * useTokenRegistry Hook
 *
 * Fetches spec ledger data and transforms to TokenItems.
 * Provides filtering, sorting, and selection state.
 *
 * "The frame is humble. The content glows."
 */

import { useCallback, useEffect, useMemo, useState } from 'react';
import { getLedger, type SpecEntry, type LedgerSummary } from '../../api/specLedger';
import {
  type TokenItem,
  type TokenType,
  type TokenStatus,
  type FilterState,
  DEFAULT_FILTERS,
  detectTier,
  detectType,
  getTierIcon,
} from './types';

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
// Transform Functions
// =============================================================================

/**
 * Extract display name from path.
 * e.g., "spec/protocols/witness.md" → "witness"
 */
function extractName(path: string): string {
  const filename = path.split('/').pop() || path;
  return filename.replace(/\.(md|py|ts|tsx|js|jsx)$/, '');
}

/**
 * Transform SpecEntry → TokenItem.
 */
function transformSpec(spec: SpecEntry): TokenItem {
  const tier = detectTier(spec.path) as 0 | 1 | 2 | 3 | 4;
  const type = detectType(spec.path);

  return {
    id: spec.path,
    name: extractName(spec.path),
    type,
    tier,
    status: spec.status,
    icon: getTierIcon(tier),
    hasEvidence: spec.impl_count > 0 || spec.test_count > 0,
    claimCount: spec.claim_count,
    implCount: spec.impl_count,
    testCount: spec.test_count,
    wordCount: spec.word_count,
  };
}

// =============================================================================
// Filter Functions
// =============================================================================

/**
 * Apply filters to token list.
 */
function applyFilters(tokens: TokenItem[], filters: FilterState): TokenItem[] {
  return tokens.filter((token) => {
    // Search filter (case-insensitive)
    if (filters.search) {
      const query = filters.search.toLowerCase();
      const matchesName = token.name.toLowerCase().includes(query);
      const matchesId = token.id.toLowerCase().includes(query);
      if (!matchesName && !matchesId) return false;
    }

    // Type filter (OR within types)
    if (filters.types.length > 0 && !filters.types.includes(token.type)) {
      return false;
    }

    // Status filter (OR within statuses)
    if (filters.statuses.length > 0 && !filters.statuses.includes(token.status)) {
      return false;
    }

    // Tier filter (OR within tiers)
    if (filters.tiers.length > 0 && !filters.tiers.includes(token.tier)) {
      return false;
    }

    // Evidence filter
    if (filters.hasEvidence !== null && token.hasEvidence !== filters.hasEvidence) {
      return false;
    }

    return true;
  });
}

/**
 * Sort tokens by tier, then name.
 */
function sortTokens(tokens: TokenItem[]): TokenItem[] {
  return [...tokens].sort((a, b) => {
    // Primary: tier ascending (principles first)
    if (a.tier !== b.tier) return a.tier - b.tier;
    // Secondary: name alphabetically
    return a.name.localeCompare(b.name);
  });
}

// =============================================================================
// Hook
// =============================================================================

export function useTokenRegistry(): UseTokenRegistryResult {
  // Core state
  const [tokens, setTokens] = useState<TokenItem[]>([]);
  const [summary, setSummary] = useState<LedgerSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Filter state
  const [filters, setFilters] = useState<FilterState>(DEFAULT_FILTERS);

  // Selection state
  const [selectedId, setSelectedId] = useState<string | null>(null);

  // Fetch data
  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      // Fetch specs (API max is 500, pagination can be added later)
      const response = await getLedger({ limit: 500 });
      const transformed = response.specs.map(transformSpec);
      const sorted = sortTokens(transformed);

      setTokens(sorted);
      setSummary(response.summary);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to load registry';
      setError(message);
      console.error('[TokenRegistry] Fetch error:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  // Initial fetch
  useEffect(() => {
    fetchData();
  }, [fetchData]);

  // Filtered tokens (memoized)
  const filteredTokens = useMemo(() => {
    return applyFilters(tokens, filters);
  }, [tokens, filters]);

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
    totalCount: tokens.length,
    filteredCount: filteredTokens.length,

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
    refresh: fetchData,
  };
}
