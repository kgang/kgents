/**
 * useCommandPalette — Command palette state and fuzzy search
 *
 * Philosophy: "Ctrl+K is the universal gateway to action."
 *
 * Features:
 * - Fuzzy search across all commands
 * - Grouped results (navigation, action, agentese, recent)
 * - Keyboard navigation (j/k, arrows, Enter, Esc)
 * - Recent items tracking
 * - AGENTESE path invocation support
 */

import { useState, useCallback, useMemo, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';

// =============================================================================
// Types
// =============================================================================

export type CommandCategory = 'navigation' | 'action' | 'agentese' | 'recent';

export interface Command {
  /** Unique identifier */
  id: string;
  /** Display label */
  label: string;
  /** Category for grouping */
  category: CommandCategory;
  /** Optional keyboard shortcut display */
  shortcut?: string;
  /** Optional icon glyph */
  icon?: string;
  /** Optional description/subtitle */
  description?: string;
  /** Action to execute */
  action: () => void | Promise<void>;
  /** Search keywords (for fuzzy matching) */
  keywords?: string[];
}

export interface CommandPaletteState {
  /** Whether the palette is open */
  isOpen: boolean;
  /** Current search query */
  query: string;
  /** Currently selected index */
  selectedIndex: number;
  /** Filtered and grouped commands */
  filteredCommands: Command[];
  /** Commands grouped by category */
  groupedCommands: Map<CommandCategory, Command[]>;
}

export interface UseCommandPaletteOptions {
  /** Custom commands to add */
  customCommands?: Command[];
  /** Callback when command is executed */
  onExecute?: (command: Command) => void;
  /** Maximum recent items to track */
  maxRecent?: number;
}

export interface UseCommandPaletteReturn {
  /** Current state */
  state: CommandPaletteState;
  /** Open the palette */
  open: () => void;
  /** Close the palette */
  close: () => void;
  /** Toggle the palette */
  toggle: () => void;
  /** Set search query */
  setQuery: (query: string) => void;
  /** Move selection up */
  selectPrev: () => void;
  /** Move selection down */
  selectNext: () => void;
  /** Execute selected command */
  executeSelected: () => void;
  /** Execute specific command */
  executeCommand: (command: Command) => void;
  /** Set selected index */
  setSelectedIndex: (index: number) => void;
  /** All registered commands */
  commands: Command[];
}

// =============================================================================
// Fuzzy Search
// =============================================================================

/**
 * Simple fuzzy search scoring.
 * Returns a score (higher = better match), or -1 for no match.
 */
function fuzzyScore(query: string, target: string): number {
  if (!query) return 0;

  const q = query.toLowerCase();
  const t = target.toLowerCase();

  // Exact match is best
  if (t === q) return 100;

  // Starts with is very good
  if (t.startsWith(q)) return 90;

  // Contains is good
  if (t.includes(q)) return 70;

  // Character-by-character fuzzy match
  let queryIndex = 0;
  let score = 0;
  let lastMatchIndex = -1;

  for (let i = 0; i < t.length && queryIndex < q.length; i++) {
    if (t[i] === q[queryIndex]) {
      score += 10;
      // Bonus for consecutive matches
      if (lastMatchIndex === i - 1) {
        score += 5;
      }
      // Bonus for matching at word boundaries
      if (i === 0 || t[i - 1] === ' ' || t[i - 1] === '.' || t[i - 1] === '/') {
        score += 3;
      }
      lastMatchIndex = i;
      queryIndex++;
    }
  }

  // All query characters must be found
  return queryIndex === q.length ? score : -1;
}

/**
 * Search commands and return sorted by relevance.
 */
function searchCommands(commands: Command[], query: string): Command[] {
  if (!query.trim()) {
    return commands;
  }

  const scored = commands.map((cmd) => {
    // Score against label, description, and keywords
    const labelScore = fuzzyScore(query, cmd.label);
    const descScore = cmd.description ? fuzzyScore(query, cmd.description) * 0.8 : -1;
    const keywordScores = cmd.keywords?.map((k) => fuzzyScore(query, k) * 0.9) || [];

    const maxScore = Math.max(labelScore, descScore, ...keywordScores);

    return { cmd, score: maxScore };
  });

  return scored
    .filter(({ score }) => score > 0)
    .sort((a, b) => b.score - a.score)
    .map(({ cmd }) => cmd);
}

// =============================================================================
// Default Commands
// =============================================================================

const CATEGORY_ORDER: CommandCategory[] = ['recent', 'navigation', 'action', 'agentese'];

function createDefaultCommands(navigate: (path: string) => void): Command[] {
  return [
    // Navigation commands
    {
      id: 'nav-editor',
      label: 'Editor',
      category: 'navigation',
      shortcut: 'Shift+E',
      icon: '\u23D4', // ⎔
      description: 'Hypergraph Editor — the main workspace',
      action: () => navigate('/world.document'),
      keywords: ['document', 'hypergraph', 'workspace', 'edit'],
    },
    {
      id: 'nav-studio',
      label: 'Studio',
      category: 'navigation',
      shortcut: 'Shift+S',
      icon: '\u229E', // ⊞
      description: 'Three-panel workspace with Feed + Editor + Witness',
      action: () => navigate('/studio'),
      keywords: ['workspace', 'three', 'panel', 'feed', 'witness'],
    },
    {
      id: 'nav-feed',
      label: 'Feed',
      category: 'navigation',
      shortcut: 'Shift+F',
      icon: '\u2261', // ≡
      description: 'Chronological truth stream',
      action: () => navigate('/self.feed'),
      keywords: ['stream', 'truth', 'chronological', 'timeline'],
    },
    {
      id: 'nav-genesis',
      label: 'Genesis',
      category: 'navigation',
      shortcut: 'Shift+G',
      icon: '\u2726', // ✦
      description: 'First-time user experience showcase',
      action: () => navigate('/genesis/showcase'),
      keywords: ['ftue', 'onboarding', 'first', 'showcase', 'demo'],
    },
    {
      id: 'nav-meta',
      label: 'Meta',
      category: 'navigation',
      shortcut: 'Shift+M',
      icon: '\u25C7', // ◇
      description: 'Watching Yourself Grow — coherence timeline',
      action: () => navigate('/self.meta'),
      keywords: ['growth', 'coherence', 'timeline', 'reflection', 'journey'],
    },

    // Action commands
    {
      id: 'action-save',
      label: 'Save',
      category: 'action',
      shortcut: 'Ctrl+S',
      icon: '\u2193', // ↓
      description: 'Save current document',
      action: () => {
        // Dispatch save event
        window.dispatchEvent(new CustomEvent('kgents:save'));
      },
      keywords: ['save', 'persist', 'write'],
    },
    {
      id: 'action-witness-mark',
      label: 'Witness Mark',
      category: 'action',
      shortcut: 'gw',
      icon: '\u25CE', // ◎
      description: 'Create a witness mark for current context',
      action: () => {
        window.dispatchEvent(new CustomEvent('kgents:witness-mark'));
      },
      keywords: ['witness', 'mark', 'trace', 'record'],
    },
    {
      id: 'action-crystallize',
      label: 'Crystallize',
      category: 'action',
      icon: '\u2B22', // ⬢
      description: 'Crystallize current insight into memory',
      action: () => {
        window.dispatchEvent(new CustomEvent('kgents:crystallize'));
      },
      keywords: ['crystallize', 'memory', 'insight', 'capture'],
    },
    {
      id: 'action-reanalyze',
      label: 'Re-analyze',
      category: 'action',
      icon: '\u21BB', // ↻
      description: 'Re-analyze current document',
      action: () => {
        window.dispatchEvent(new CustomEvent('kgents:reanalyze'));
      },
      keywords: ['analyze', 'reanalyze', 'process', 'scan'],
    },
    {
      id: 'action-toggle-files',
      label: 'Toggle Files Sidebar',
      category: 'action',
      shortcut: 'Ctrl+B',
      icon: '\u2630', // ☰
      description: 'Show/hide the files sidebar',
      action: () => {
        window.dispatchEvent(new CustomEvent('kgents:toggle-files'));
      },
      keywords: ['files', 'sidebar', 'browse', 'toggle'],
    },
    {
      id: 'action-toggle-chat',
      label: 'Toggle Chat Sidebar',
      category: 'action',
      shortcut: 'Ctrl+J',
      icon: '\u2609', // ☉
      description: 'Show/hide the chat sidebar',
      action: () => {
        window.dispatchEvent(new CustomEvent('kgents:toggle-chat'));
      },
      keywords: ['chat', 'sidebar', 'conversation', 'toggle'],
    },

    // AGENTESE commands
    {
      id: 'agentese-brain-capture',
      label: 'self.brain.capture',
      category: 'agentese',
      icon: '\u2609', // ☉
      description: 'Capture thought to brain',
      action: () => {
        window.dispatchEvent(
          new CustomEvent('kgents:agentese', {
            detail: { path: 'self.brain.capture' },
          })
        );
      },
      keywords: ['brain', 'capture', 'thought', 'self'],
    },
    {
      id: 'agentese-witness-mark',
      label: 'self.witness.mark',
      category: 'agentese',
      icon: '\u25CE', // ◎
      description: 'Create witness mark',
      action: () => {
        window.dispatchEvent(
          new CustomEvent('kgents:agentese', {
            detail: { path: 'self.witness.mark' },
          })
        );
      },
      keywords: ['witness', 'mark', 'self', 'trace'],
    },
    {
      id: 'agentese-memory-crystallize',
      label: 'self.memory.crystallize',
      category: 'agentese',
      icon: '\u2B22', // ⬢
      description: 'Crystallize memory',
      action: () => {
        window.dispatchEvent(
          new CustomEvent('kgents:agentese', {
            detail: { path: 'self.memory.crystallize' },
          })
        );
      },
      keywords: ['memory', 'crystallize', 'self', 'persist'],
    },
    {
      id: 'agentese-world-document-analyze',
      label: 'world.document.analyze',
      category: 'agentese',
      icon: '\u2318', // ⌘
      description: 'Analyze current document',
      action: () => {
        window.dispatchEvent(
          new CustomEvent('kgents:agentese', {
            detail: { path: 'world.document.analyze' },
          })
        );
      },
      keywords: ['world', 'document', 'analyze', 'scan'],
    },
    {
      id: 'agentese-concept-define',
      label: 'concept.define',
      category: 'agentese',
      icon: '\u2229', // ∩
      description: 'Define a concept',
      action: () => {
        window.dispatchEvent(
          new CustomEvent('kgents:agentese', {
            detail: { path: 'concept.define' },
          })
        );
      },
      keywords: ['concept', 'define', 'definition', 'meaning'],
    },
    {
      id: 'agentese-time-schedule',
      label: 'time.schedule',
      category: 'agentese',
      icon: '\u23F0', // ⏰
      description: 'Schedule a future action',
      action: () => {
        window.dispatchEvent(
          new CustomEvent('kgents:agentese', {
            detail: { path: 'time.schedule' },
          })
        );
      },
      keywords: ['time', 'schedule', 'future', 'plan'],
    },
    {
      id: 'agentese-void-serendipity',
      label: 'void.serendipity',
      category: 'agentese',
      icon: '\u2605', // ★
      description: 'Invoke serendipitous discovery',
      action: () => {
        window.dispatchEvent(
          new CustomEvent('kgents:agentese', {
            detail: { path: 'void.serendipity' },
          })
        );
      },
      keywords: ['void', 'serendipity', 'random', 'discover'],
    },
  ];
}

// =============================================================================
// Local Storage for Recent Items
// =============================================================================

const RECENT_STORAGE_KEY = 'kgents:command-palette:recent';

function loadRecentIds(): string[] {
  try {
    const stored = localStorage.getItem(RECENT_STORAGE_KEY);
    return stored ? JSON.parse(stored) : [];
  } catch {
    return [];
  }
}

function saveRecentIds(ids: string[]): void {
  try {
    localStorage.setItem(RECENT_STORAGE_KEY, JSON.stringify(ids));
  } catch {
    // Ignore storage errors
  }
}

// =============================================================================
// Hook Implementation
// =============================================================================

export function useCommandPalette(options: UseCommandPaletteOptions = {}): UseCommandPaletteReturn {
  const { customCommands = [], onExecute, maxRecent = 5 } = options;
  const navigate = useNavigate();

  // State
  const [isOpen, setIsOpen] = useState(false);
  const [query, setQuery] = useState('');
  const [selectedIndex, setSelectedIndex] = useState(0);
  const [recentIds, setRecentIds] = useState<string[]>(loadRecentIds);

  // Refs for stable callbacks
  const commandsRef = useRef<Command[]>([]);

  // Build command list
  const commands = useMemo(() => {
    const defaultCmds = createDefaultCommands(navigate);
    return [...defaultCmds, ...customCommands];
  }, [navigate, customCommands]);

  // Update ref
  commandsRef.current = commands;

  // Build recent commands from IDs
  const recentCommands = useMemo(() => {
    return recentIds
      .map((id) => {
        const cmd = commands.find((c) => c.id === id);
        if (!cmd) return null;
        return { ...cmd, category: 'recent' as CommandCategory };
      })
      .filter((cmd): cmd is Command => cmd !== null);
  }, [commands, recentIds]);

  // Filter commands based on query
  const filteredCommands = useMemo(() => {
    const allCommands = query.trim()
      ? searchCommands(commands, query)
      : [...recentCommands, ...commands.filter((c) => !recentIds.includes(c.id))];

    return allCommands;
  }, [commands, recentCommands, recentIds, query]);

  // Group commands by category
  const groupedCommands = useMemo(() => {
    const groups = new Map<CommandCategory, Command[]>();

    for (const category of CATEGORY_ORDER) {
      groups.set(category, []);
    }

    for (const cmd of filteredCommands) {
      const group = groups.get(cmd.category);
      if (group) {
        group.push(cmd);
      }
    }

    // Remove empty groups
    for (const [category, cmds] of groups) {
      if (cmds.length === 0) {
        groups.delete(category);
      }
    }

    return groups;
  }, [filteredCommands]);

  // Reset selection when filter changes
  useEffect(() => {
    setSelectedIndex(0);
  }, [query]);

  // Global Ctrl+K handler
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Ctrl+K or Cmd+K to toggle palette
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        setIsOpen((prev) => !prev);
        if (!isOpen) {
          setQuery('');
          setSelectedIndex(0);
        }
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen]);

  // Actions
  const open = useCallback(() => {
    setIsOpen(true);
    setQuery('');
    setSelectedIndex(0);
  }, []);

  const close = useCallback(() => {
    setIsOpen(false);
  }, []);

  const toggle = useCallback(() => {
    setIsOpen((prev) => !prev);
    if (!isOpen) {
      setQuery('');
      setSelectedIndex(0);
    }
  }, [isOpen]);

  const selectPrev = useCallback(() => {
    setSelectedIndex((prev) => Math.max(0, prev - 1));
  }, []);

  const selectNext = useCallback(() => {
    setSelectedIndex((prev) => Math.min(filteredCommands.length - 1, prev + 1));
  }, [filteredCommands.length]);

  const executeCommand = useCallback(
    (command: Command) => {
      // Update recent
      setRecentIds((prev) => {
        const newRecent = [command.id, ...prev.filter((id) => id !== command.id)].slice(
          0,
          maxRecent
        );
        saveRecentIds(newRecent);
        return newRecent;
      });

      // Close palette
      setIsOpen(false);

      // Execute
      void command.action();
      onExecute?.(command);
    },
    [maxRecent, onExecute]
  );

  const executeSelected = useCallback(() => {
    const command = filteredCommands[selectedIndex];
    if (command) {
      executeCommand(command);
    }
  }, [filteredCommands, selectedIndex, executeCommand]);

  // Build state object
  const state: CommandPaletteState = {
    isOpen,
    query,
    selectedIndex,
    filteredCommands,
    groupedCommands,
  };

  return {
    state,
    open,
    close,
    toggle,
    setQuery,
    selectPrev,
    selectNext,
    executeSelected,
    executeCommand,
    setSelectedIndex,
    commands,
  };
}

export default useCommandPalette;
