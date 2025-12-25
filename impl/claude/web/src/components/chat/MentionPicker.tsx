/**
 * MentionPicker — Autocomplete for @mentions in chat
 *
 * "Vim and iterm as primitives. Fuzzy finding like fzf/telescope.nvim"
 *
 * Triggers on `@` character in textarea. Supports:
 * - @file:path/to/file.py → File contents
 * - @symbol:ClassName.method → Definition + docstring
 * - @spec:protocols/chat-web.md → Spec file
 * - @witness:recent → Recent marks
 * - @web:https://example.com → Fetched page
 * - @terminal:last → Last command output
 * - @project:files → Project file tree
 *
 * Key behaviors:
 * - Fuzzy search powered by Fuse.js
 * - Match highlighting for better visibility
 * - Keyboard navigation: j/k for up/down (vim-like)
 * - Arrow keys also work (for non-vim users)
 * - Enter to select, Escape to dismiss
 * - Position relative to cursor in textarea
 * - Show recently used @mentions at top
 * - Debounced search (300ms)
 *
 * STARK BIOME styling: steel frame, earned glow on selection
 *
 * @see spec/protocols/chat-web.md Part VI
 */

import { memo, useState, useEffect, useCallback, useRef, useMemo } from 'react';
import { FileText, Code, BookOpen, Eye, Globe, Terminal, FolderTree, Clock } from 'lucide-react';
import Fuse, { type FuseResultMatch } from 'fuse.js';
import './MentionPicker.css';

// =============================================================================
// Types
// =============================================================================

export type MentionType = 'file' | 'symbol' | 'spec' | 'witness' | 'web' | 'terminal' | 'project';

export interface MentionSuggestion {
  type: MentionType;
  value: string;
  label: string;
  description?: string;
  recent?: boolean;
  /** Fuse.js match indices for highlighting */
  matches?: readonly FuseResultMatch[];
  /** Fuse.js search score (lower is better) */
  score?: number;
}

export interface MentionPickerProps {
  /** Whether the picker is open */
  isOpen: boolean;

  /** Current search query (after @ trigger) */
  query: string;

  /** Callback when a mention is selected */
  onSelect: (suggestion: MentionSuggestion) => void;

  /** Callback to close the picker */
  onClose: () => void;

  /** Position relative to textarea cursor */
  position?: { top: number; left: number };

  /** Recently used mentions (shown at top) */
  recentMentions?: MentionSuggestion[];

  /** Available file paths for @file: */
  availableFiles?: string[];

  /** Available symbols for @symbol: */
  availableSymbols?: string[];

  /** Available specs for @spec: */
  availableSpecs?: string[];
}

// =============================================================================
// Icons
// =============================================================================

const MENTION_ICONS: Record<MentionType, typeof FileText> = {
  file: FileText,
  symbol: Code,
  spec: BookOpen,
  witness: Eye,
  web: Globe,
  terminal: Terminal,
  project: FolderTree,
};

const MENTION_LABELS: Record<MentionType, string> = {
  file: 'File',
  symbol: 'Symbol',
  spec: 'Spec',
  witness: 'Witness',
  web: 'Web',
  terminal: 'Terminal',
  project: 'Project',
};

// =============================================================================
// Mention Type Detection
// =============================================================================

function detectMentionType(query: string): MentionType | null {
  if (query.startsWith('file:')) return 'file';
  if (query.startsWith('symbol:')) return 'symbol';
  if (query.startsWith('spec:')) return 'spec';
  if (query.startsWith('witness:')) return 'witness';
  if (query.startsWith('web:')) return 'web';
  if (query.startsWith('terminal:')) return 'terminal';
  if (query.startsWith('project:')) return 'project';
  return null;
}

// =============================================================================
// Fuzzy Search with Fuse.js
// =============================================================================

interface SearchableItem {
  value: string;
  description?: string;
}

/** Create a Fuse.js instance for a given list of items */
function createFuse<T>(items: T[], keys: string[]) {
  return new Fuse(items, {
    keys,
    threshold: 0.4, // 0 = perfect match, 1 = match anything
    includeScore: true,
    includeMatches: true,
    minMatchCharLength: 1,
    ignoreLocation: true, // Match anywhere in the string
    findAllMatches: true,
  });
}

/** Search items using Fuse.js */
function fuseSearch<T>(
  fuse: Fuse<T>,
  query: string,
  limit: number = 5
): Array<T & { matches?: readonly FuseResultMatch[]; score?: number }> {
  if (!query) return [];

  const results = fuse.search(query, { limit });

  return results.map((result) => ({
    ...result.item,
    matches: result.matches,
    score: result.score,
  }));
}

// =============================================================================
// Match Highlighting
// =============================================================================

interface HighlightedTextProps {
  text: string;
  matches?: readonly FuseResultMatch[];
  className?: string;
}

/**
 * Render text with highlighted matches from Fuse.js
 * Matches are shown with glow-spore color
 */
function HighlightedText({ text, matches, className }: HighlightedTextProps) {
  if (!matches || matches.length === 0) {
    return <span className={className}>{text}</span>;
  }

  // Get match indices for this text
  const matchIndices: Array<[number, number]> = [];
  for (const match of matches) {
    if (match.indices) {
      matchIndices.push(...match.indices);
    }
  }

  // If no indices, return plain text
  if (matchIndices.length === 0) {
    return <span className={className}>{text}</span>;
  }

  // Sort and merge overlapping indices
  const sortedIndices = matchIndices.sort((a, b) => a[0] - b[0]);
  const mergedIndices: Array<[number, number]> = [];
  let current = sortedIndices[0];

  for (let i = 1; i < sortedIndices.length; i++) {
    const next = sortedIndices[i];
    if (next[0] <= current[1] + 1) {
      // Merge overlapping/adjacent ranges
      current = [current[0], Math.max(current[1], next[1])];
    } else {
      mergedIndices.push(current);
      current = next;
    }
  }
  mergedIndices.push(current);

  // Build highlighted text
  const parts: React.ReactNode[] = [];
  let lastIndex = 0;

  for (const [start, end] of mergedIndices) {
    // Add text before match
    if (start > lastIndex) {
      parts.push(text.substring(lastIndex, start));
    }

    // Add highlighted match
    parts.push(
      <mark key={start} className="mention-picker__highlight">
        {text.substring(start, end + 1)}
      </mark>
    );

    lastIndex = end + 1;
  }

  // Add remaining text
  if (lastIndex < text.length) {
    parts.push(text.substring(lastIndex));
  }

  return <span className={className}>{parts}</span>;
}

// =============================================================================
// Generate Suggestions
// =============================================================================

function generateSuggestions(
  query: string,
  availableFiles: string[] = [],
  availableSymbols: string[] = [],
  availableSpecs: string[] = [],
  recentMentions: MentionSuggestion[] = []
): MentionSuggestion[] {
  const suggestions: MentionSuggestion[] = [];

  // If no query, show all types
  if (!query) {
    return [
      { type: 'file', value: '', label: '@file:', description: 'Inject file contents' },
      { type: 'symbol', value: '', label: '@symbol:', description: 'Inject symbol definition' },
      { type: 'spec', value: '', label: '@spec:', description: 'Inject spec file' },
      { type: 'witness', value: '', label: '@witness:', description: 'Inject witness marks' },
      { type: 'web', value: '', label: '@web:', description: 'Inject web page' },
      { type: 'terminal', value: '', label: '@terminal:', description: 'Inject terminal output' },
      { type: 'project', value: '', label: '@project:', description: 'Inject project file tree' },
    ];
  }

  const mentionType = detectMentionType(query);
  const searchTerm = mentionType ? query.split(':')[1] || '' : query;

  // Recent mentions at top (if they match)
  if (recentMentions.length > 0 && searchTerm) {
    const recentFuse = createFuse(recentMentions, ['value', 'label', 'description']);
    const matchingRecent = fuseSearch(recentFuse, searchTerm, 3);
    suggestions.push(...matchingRecent.map((m) => ({ ...m, recent: true })));
  }

  // File mentions
  if (!mentionType || mentionType === 'file') {
    if (searchTerm && availableFiles.length > 0) {
      const fileItems = availableFiles.map((f) => ({ value: f }));
      const fileFuse = createFuse(fileItems, ['value']);
      const matchingFiles = fuseSearch(fileFuse, searchTerm, 5);

      suggestions.push(
        ...matchingFiles.map((item) => ({
          type: 'file' as MentionType,
          value: item.value,
          label: '@file:' + item.value,
          description: 'File contents',
          matches: item.matches,
          score: item.score,
        }))
      );
    }
  }

  // Symbol mentions
  if (!mentionType || mentionType === 'symbol') {
    if (searchTerm && availableSymbols.length > 0) {
      const symbolItems = availableSymbols.map((s) => ({ value: s }));
      const symbolFuse = createFuse(symbolItems, ['value']);
      const matchingSymbols = fuseSearch(symbolFuse, searchTerm, 5);

      suggestions.push(
        ...matchingSymbols.map((item) => ({
          type: 'symbol' as MentionType,
          value: item.value,
          label: '@symbol:' + item.value,
          description: 'Definition + docstring',
          matches: item.matches,
          score: item.score,
        }))
      );
    }
  }

  // Spec mentions
  if (!mentionType || mentionType === 'spec') {
    if (searchTerm && availableSpecs.length > 0) {
      const specItems = availableSpecs.map((s) => ({ value: s }));
      const specFuse = createFuse(specItems, ['value']);
      const matchingSpecs = fuseSearch(specFuse, searchTerm, 5);

      suggestions.push(
        ...matchingSpecs.map((item) => ({
          type: 'spec' as MentionType,
          value: item.value,
          label: '@spec:' + item.value,
          description: 'Spec file',
          matches: item.matches,
          score: item.score,
        }))
      );
    }
  }

  // Witness mentions (predefined options)
  if (!mentionType || mentionType === 'witness') {
    const witnessOptions: SearchableItem[] = [
      { value: 'recent', description: 'Last 10 marks' },
      { value: 'today', description: "Today's marks" },
      { value: 'week', description: 'This week' },
    ];

    if (searchTerm) {
      const witnessFuse = createFuse(witnessOptions, ['value', 'description']);
      const matchingWitness = fuseSearch(witnessFuse, searchTerm, 3);

      suggestions.push(
        ...matchingWitness.map((item) => ({
          type: 'witness' as MentionType,
          value: item.value,
          label: '@witness:' + item.value,
          description: item.description,
          matches: item.matches,
          score: item.score,
        }))
      );
    } else {
      // Show all if no search term
      suggestions.push(
        ...witnessOptions.map((w) => ({
          type: 'witness' as MentionType,
          value: w.value,
          label: '@witness:' + w.value,
          description: w.description,
        }))
      );
    }
  }

  // Terminal mentions (predefined options)
  if (!mentionType || mentionType === 'terminal') {
    const terminalOptions: SearchableItem[] = [
      { value: 'last', description: 'Last command output' },
      { value: 'history', description: 'Command history' },
    ];

    if (searchTerm) {
      const terminalFuse = createFuse(terminalOptions, ['value', 'description']);
      const matchingTerminal = fuseSearch(terminalFuse, searchTerm, 2);

      suggestions.push(
        ...matchingTerminal.map((item) => ({
          type: 'terminal' as MentionType,
          value: item.value,
          label: '@terminal:' + item.value,
          description: item.description,
          matches: item.matches,
          score: item.score,
        }))
      );
    } else {
      // Show all if no search term
      suggestions.push(
        ...terminalOptions.map((t) => ({
          type: 'terminal' as MentionType,
          value: t.value,
          label: '@terminal:' + t.value,
          description: t.description,
        }))
      );
    }
  }

  // Web mentions (manual input)
  if (mentionType === 'web' && searchTerm) {
    suggestions.push({
      type: 'web',
      value: searchTerm,
      label: '@web:' + searchTerm,
      description: 'Fetch web page',
    });
  }

  // Project mentions (predefined options)
  if (!mentionType || mentionType === 'project') {
    const projectOptions: SearchableItem[] = [
      { value: 'files', description: 'Project file tree' },
      { value: 'structure', description: 'Directory structure' },
    ];

    if (searchTerm) {
      const projectFuse = createFuse(projectOptions, ['value', 'description']);
      const matchingProject = fuseSearch(projectFuse, searchTerm, 2);

      suggestions.push(
        ...matchingProject.map((item) => ({
          type: 'project' as MentionType,
          value: item.value,
          label: '@project:' + item.value,
          description: item.description,
          matches: item.matches,
          score: item.score,
        }))
      );
    } else {
      // Show all if no search term
      suggestions.push(
        ...projectOptions.map((p) => ({
          type: 'project' as MentionType,
          value: p.value,
          label: '@project:' + p.value,
          description: p.description,
        }))
      );
    }
  }

  return suggestions;
}

// =============================================================================
// Component
// =============================================================================

export const MentionPicker = memo(function MentionPicker({
  isOpen,
  query,
  onSelect,
  onClose,
  position = { top: 0, left: 0 },
  recentMentions = [],
  availableFiles = [],
  availableSymbols = [],
  availableSpecs = [],
}: MentionPickerProps) {
  const [selectedIndex, setSelectedIndex] = useState(0);
  const [debouncedQuery, setDebouncedQuery] = useState(query);
  const listRef = useRef<HTMLDivElement>(null);

  // Debounce search query (300ms)
  useEffect(() => {
    const timeout = setTimeout(() => {
      setDebouncedQuery(query);
    }, 300);

    return () => clearTimeout(timeout);
  }, [query]);

  // Generate suggestions
  const suggestions = useMemo(
    () =>
      generateSuggestions(
        debouncedQuery,
        availableFiles,
        availableSymbols,
        availableSpecs,
        recentMentions
      ),
    [debouncedQuery, availableFiles, availableSymbols, availableSpecs, recentMentions]
  );

  // Reset selected index when suggestions change
  useEffect(() => {
    setSelectedIndex(0);
  }, [suggestions]);

  // Scroll selected item into view
  useEffect(() => {
    if (listRef.current) {
      const selectedElement = listRef.current.children[selectedIndex] as HTMLElement;
      if (selectedElement) {
        selectedElement.scrollIntoView({ block: 'nearest' });
      }
    }
  }, [selectedIndex]);

  // Handle keyboard navigation
  const handleKeyDown = useCallback(
    (e: KeyboardEvent) => {
      if (!isOpen) return;

      switch (e.key) {
        case 'ArrowDown':
        case 'j': // vim-like down
          e.preventDefault();
          setSelectedIndex((i) => (i + 1) % suggestions.length);
          break;

        case 'ArrowUp':
        case 'k': // vim-like up
          e.preventDefault();
          setSelectedIndex((i) => (i - 1 + suggestions.length) % suggestions.length);
          break;

        case 'Enter':
          e.preventDefault();
          if (suggestions[selectedIndex]) {
            onSelect(suggestions[selectedIndex]);
          }
          break;

        case 'Escape':
          e.preventDefault();
          onClose();
          break;
      }
    },
    [isOpen, suggestions, selectedIndex, onSelect, onClose]
  );

  useEffect(() => {
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [handleKeyDown]);

  if (!isOpen || suggestions.length === 0) return null;

  return (
    <div
      className="mention-picker"
      style={{
        top: position.top,
        left: position.left,
      }}
    >
      <div className="mention-picker__header">
        <span className="mention-picker__title">@mentions</span>
        <span className="mention-picker__count">
          {suggestions.length} {suggestions.length === 1 ? 'result' : 'results'}
        </span>
      </div>

      <div ref={listRef} className="mention-picker__list">
        {suggestions.map((suggestion, index) => {
          const Icon = MENTION_ICONS[suggestion.type];
          const isSelected = index === selectedIndex;

          return (
            <button
              key={suggestion.type + '-' + suggestion.value + '-' + index}
              className={'mention-picker__item' + (isSelected ? ' mention-picker__item--selected' : '')}
              onClick={() => onSelect(suggestion)}
              onMouseEnter={() => setSelectedIndex(index)}
            >
              <Icon size={16} className="mention-picker__item-icon" />
              <div className="mention-picker__item-content">
                <div className="mention-picker__item-label">
                  {suggestion.recent && (
                    <Clock size={12} className="mention-picker__item-recent-icon" />
                  )}
                  <HighlightedText text={suggestion.label} matches={suggestion.matches} />
                </div>
                {suggestion.description && (
                  <div className="mention-picker__item-description">
                    <HighlightedText text={suggestion.description} matches={suggestion.matches} />
                  </div>
                )}
              </div>
              <span className="mention-picker__item-type">{MENTION_LABELS[suggestion.type]}</span>
            </button>
          );
        })}
      </div>

      <div className="mention-picker__footer">
        <kbd>↑↓</kbd> or <kbd>j/k</kbd> • <kbd>Enter</kbd> select • <kbd>Esc</kbd> close
      </div>
    </div>
  );
});

export default MentionPicker;
