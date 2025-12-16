/**
 * ModuleSearch - Fuzzy search combobox for quick module navigation.
 *
 * Features:
 * - Fuzzy matching on module id and label
 * - Keyboard navigation (↑↓ Enter Esc)
 * - Recent searches (localStorage)
 * - Health grade indicators in results
 * - Preview on hover (onFocus callback)
 *
 * @see plans/gestalt-visual-showcase.md Chunk 1
 */

import { useState, useRef, useEffect, useCallback, useMemo } from 'react';
import type { CodebaseModule } from '../../api/types';
import { HEALTH_GRADE_CONFIG } from '../../api/types';
import { searchModules, type Density } from './types';

// =============================================================================
// Constants
// =============================================================================

const MAX_RESULTS = 8;
const MAX_RECENT = 5;
const RECENT_STORAGE_KEY = 'gestalt-recent-searches';

// =============================================================================
// Props
// =============================================================================

export interface ModuleSearchProps {
  /** All modules available for search */
  modules: CodebaseModule[];
  /** Callback when a module is selected */
  onSelect: (module: CodebaseModule) => void;
  /** Callback when hovering over a result (preview) */
  onFocus?: (module: CodebaseModule | null) => void;
  /** Density for responsive sizing */
  density: Density;
  /** Additional class names */
  className?: string;
}

// =============================================================================
// Hooks
// =============================================================================

/**
 * Hook to manage recent searches in localStorage.
 */
function useRecentSearches() {
  const [recent, setRecent] = useState<string[]>(() => {
    try {
      const stored = localStorage.getItem(RECENT_STORAGE_KEY);
      return stored ? JSON.parse(stored) : [];
    } catch {
      return [];
    }
  });

  const addRecent = useCallback((moduleId: string) => {
    setRecent((prev) => {
      const filtered = prev.filter((id) => id !== moduleId);
      const updated = [moduleId, ...filtered].slice(0, MAX_RECENT);
      try {
        localStorage.setItem(RECENT_STORAGE_KEY, JSON.stringify(updated));
      } catch {
        // Ignore localStorage errors
      }
      return updated;
    });
  }, []);

  const clearRecent = useCallback(() => {
    setRecent([]);
    try {
      localStorage.removeItem(RECENT_STORAGE_KEY);
    } catch {
      // Ignore
    }
  }, []);

  return { recent, addRecent, clearRecent };
}

// =============================================================================
// Component
// =============================================================================

export function ModuleSearch({ modules, onSelect, onFocus, density, className }: ModuleSearchProps) {
  const [query, setQuery] = useState('');
  const [isOpen, setIsOpen] = useState(false);
  const [highlightedIndex, setHighlightedIndex] = useState(-1);
  const inputRef = useRef<HTMLInputElement>(null);
  const listRef = useRef<HTMLDivElement>(null);
  const { recent, addRecent } = useRecentSearches();

  const isCompact = density === 'compact';

  // Search results
  const results = useMemo(() => {
    if (!query.trim()) return [];
    return searchModules(modules, query).slice(0, MAX_RESULTS);
  }, [modules, query]);

  // Recent modules (when no query)
  const recentModules = useMemo(() => {
    if (query.trim()) return [];
    return recent
      .map((id) => modules.find((m) => m.id === id))
      .filter((m): m is CodebaseModule => m !== undefined);
  }, [recent, modules, query]);

  // Combined display items
  const displayItems = query.trim() ? results.map((r) => r.module) : recentModules;

  // Handlers
  const handleSelect = useCallback(
    (module: CodebaseModule) => {
      addRecent(module.id);
      onSelect(module);
      setQuery('');
      setIsOpen(false);
      inputRef.current?.blur();
    },
    [addRecent, onSelect]
  );

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      switch (e.key) {
        case 'ArrowDown':
          e.preventDefault();
          setHighlightedIndex((prev) => (prev < displayItems.length - 1 ? prev + 1 : prev));
          break;
        case 'ArrowUp':
          e.preventDefault();
          setHighlightedIndex((prev) => (prev > 0 ? prev - 1 : -1));
          break;
        case 'Enter':
          e.preventDefault();
          if (highlightedIndex >= 0 && displayItems[highlightedIndex]) {
            handleSelect(displayItems[highlightedIndex]);
          }
          break;
        case 'Escape':
          setIsOpen(false);
          setQuery('');
          inputRef.current?.blur();
          break;
      }
    },
    [displayItems, highlightedIndex, handleSelect]
  );

  // Focus handling for preview
  useEffect(() => {
    if (onFocus && highlightedIndex >= 0 && displayItems[highlightedIndex]) {
      onFocus(displayItems[highlightedIndex]);
    } else if (onFocus) {
      onFocus(null);
    }
  }, [highlightedIndex, displayItems, onFocus]);

  // Reset highlight when results change
  useEffect(() => {
    setHighlightedIndex(-1);
  }, [query]);

  // Close on outside click
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (
        inputRef.current &&
        !inputRef.current.contains(e.target as Node) &&
        listRef.current &&
        !listRef.current.contains(e.target as Node)
      ) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  return (
    <div className={`relative ${className}`}>
      {/* Search Input */}
      <div className="relative">
        <span className="absolute left-2 top-1/2 -translate-y-1/2 text-gray-500 pointer-events-none">
          🔍
        </span>
        <input
          ref={inputRef}
          type="text"
          value={query}
          onChange={(e) => {
            setQuery(e.target.value);
            setIsOpen(true);
          }}
          onFocus={() => setIsOpen(true)}
          onKeyDown={handleKeyDown}
          placeholder="Search modules..."
          className={`
            w-full bg-gray-700/80 border border-gray-600 rounded-lg
            text-white placeholder-gray-500
            focus:border-green-500 focus:ring-1 focus:ring-green-500 focus:outline-none
            ${isCompact ? 'pl-7 pr-8 py-1.5 text-xs' : 'pl-8 pr-10 py-2 text-sm'}
          `}
        />
        {query && (
          <button
            onClick={() => {
              setQuery('');
              inputRef.current?.focus();
            }}
            className="absolute right-2 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-300"
          >
            ×
          </button>
        )}
      </div>

      {/* Dropdown */}
      {isOpen && displayItems.length > 0 && (
        <div
          ref={listRef}
          className={`
            absolute z-50 w-full mt-1 bg-gray-800 border border-gray-700 rounded-lg shadow-xl
            overflow-hidden
            ${isCompact ? 'max-h-48' : 'max-h-64'}
          `}
        >
          {/* Section header */}
          <div className={`px-2 py-1 bg-gray-750 text-gray-500 ${isCompact ? 'text-[9px]' : 'text-[10px]'} uppercase`}>
            {query.trim() ? `Matches (${results.length})` : 'Recent'}
          </div>

          {/* Results list */}
          <div className="overflow-y-auto max-h-56">
            {displayItems.map((module, index) => {
              const gradeConfig = HEALTH_GRADE_CONFIG[module.health_grade] || HEALTH_GRADE_CONFIG['?'];
              const isHighlighted = index === highlightedIndex;

              return (
                <button
                  key={module.id}
                  onClick={() => handleSelect(module)}
                  onMouseEnter={() => setHighlightedIndex(index)}
                  className={`
                    w-full text-left flex items-center justify-between gap-2
                    ${isCompact ? 'px-2 py-1.5' : 'px-3 py-2'}
                    ${isHighlighted ? 'bg-gray-700' : 'hover:bg-gray-700/50'}
                    transition-colors
                  `}
                >
                  <div className="flex-1 min-w-0">
                    <div className={`text-white truncate ${isCompact ? 'text-xs' : 'text-sm'}`}>
                      {module.label}
                    </div>
                    <div className={`text-gray-500 font-mono truncate ${isCompact ? 'text-[10px]' : 'text-xs'}`}>
                      {module.id}
                    </div>
                  </div>
                  <div className="flex items-center gap-2 flex-shrink-0">
                    <span
                      className={`font-bold ${isCompact ? 'text-[10px]' : 'text-xs'}`}
                      style={{ color: gradeConfig.color }}
                    >
                      {module.health_grade}
                    </span>
                    {module.layer && (
                      <span className={`text-gray-500 ${isCompact ? 'text-[9px]' : 'text-[10px]'}`}>
                        {module.layer}
                      </span>
                    )}
                  </div>
                </button>
              );
            })}
          </div>

          {/* Keyboard hints */}
          {!isCompact && (
            <div className="px-2 py-1.5 bg-gray-750 border-t border-gray-700 flex gap-3 text-[10px] text-gray-500">
              <span>↑↓ navigate</span>
              <span>Enter select</span>
              <span>Esc close</span>
            </div>
          )}
        </div>
      )}

      {/* No results */}
      {isOpen && query.trim() && results.length === 0 && (
        <div className="absolute z-50 w-full mt-1 bg-gray-800 border border-gray-700 rounded-lg shadow-xl p-4 text-center">
          <span className="text-gray-500 text-sm">No modules match "{query}"</span>
        </div>
      )}
    </div>
  );
}

export default ModuleSearch;
