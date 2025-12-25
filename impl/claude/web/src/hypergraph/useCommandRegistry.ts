/**
 * useCommandRegistry — The universal command list
 *
 * "Cmd+K is not a shortcut. It's a philosophy."
 *
 * Architecture:
 * - Centralized registry of all commands
 * - Categories: navigation, witness, graph, agentese, actions
 * - Recency tracking (localStorage persistence)
 * - Fuzzy matching handled by cmdk
 */

import { useCallback, useEffect, useState } from 'react';

// =============================================================================
// Types
// =============================================================================

export interface Command {
  /** Unique command identifier */
  id: string;

  /** Display label */
  label: string;

  /** Category for grouping */
  category: 'navigation' | 'witness' | 'graph' | 'agentese' | 'actions' | 'files';

  /** Optional keyboard shortcut hint */
  shortcut?: string;

  /** Icon glyph (mathematical notation) */
  icon?: string;

  /** Execute the command */
  execute: () => void | Promise<void>;

  /** Search keywords (beyond label) */
  keywords?: string[];
}

const RECENT_COMMANDS_KEY = 'kgents:command-palette:recent';
const MAX_RECENT_COMMANDS = 5;

// =============================================================================
// Hook
// =============================================================================

interface UseCommandRegistryOptions {
  /** Callback to navigate to a file/spec */
  onNavigate?: (path: string) => void;

  /** Callback to open witness panel */
  onWitnessMode?: () => void;

  /** Callback to save current document */
  onSave?: () => void;

  /** Callback to re-analyze document */
  onReanalyze?: () => void;

  /** Callback to enter graph mode */
  onGraphMode?: () => void;

  /** Callback to open analysis quadrant */
  onAnalysisQuadrant?: () => void;

  /** Callback to invoke AGENTESE path */
  onAgentese?: (path: string) => void;

  /** Callback to navigate to Zero Seed */
  onZeroSeed?: (tab?: string) => void;
}

export function useCommandRegistry(options: UseCommandRegistryOptions) {
  const {
    onNavigate,
    onWitnessMode,
    onSave,
    onReanalyze,
    onGraphMode,
    onAnalysisQuadrant,
    onAgentese,
    onZeroSeed,
  } = options;

  const [recentCommands, setRecentCommands] = useState<string[]>([]);
  const [files, setFiles] = useState<string[]>([]);

  // Load recent commands from localStorage
  useEffect(() => {
    try {
      const stored = localStorage.getItem(RECENT_COMMANDS_KEY);
      if (stored) {
        setRecentCommands(JSON.parse(stored));
      }
    } catch (err) {
      console.warn('[useCommandRegistry] Failed to load recent commands:', err);
    }
  }, []);

  // Track command execution
  const trackCommand = useCallback((commandId: string) => {
    setRecentCommands((prev) => {
      // Add to front, remove duplicates, limit to MAX_RECENT_COMMANDS
      const updated = [commandId, ...prev.filter((id) => id !== commandId)].slice(
        0,
        MAX_RECENT_COMMANDS
      );

      // Persist to localStorage
      try {
        localStorage.setItem(RECENT_COMMANDS_KEY, JSON.stringify(updated));
      } catch (err) {
        console.warn('[useCommandRegistry] Failed to persist recent commands:', err);
      }

      return updated;
    });
  }, []);

  // Load files from API
  useEffect(() => {
    const fetchFiles = async () => {
      try {
        const res = await fetch('/api/files/list');
        if (res.ok) {
          const data = await res.json();
          setFiles(data.files || []);
        }
      } catch (err) {
        console.warn('[useCommandRegistry] Failed to load files:', err);
      }
    };

    void fetchFiles();
  }, []);

  // Build command registry
  const commands: Command[] = [
    // =============================================================================
    // ACTIONS
    // =============================================================================
    {
      id: 'action:save',
      label: 'Save current document',
      category: 'actions',
      shortcut: ':w',
      icon: '⊕',
      keywords: ['write', 'persist', 'commit'],
      execute: () => {
        trackCommand('action:save');
        onSave?.();
      },
    },
    {
      id: 'action:reanalyze',
      label: 'Re-analyze document',
      category: 'actions',
      icon: '⊛',
      keywords: ['analyze', 'llm', 'claude', 'parse'],
      execute: () => {
        trackCommand('action:reanalyze');
        onReanalyze?.();
      },
    },
    {
      id: 'action:witness',
      label: 'Add witness mark',
      category: 'actions',
      shortcut: 'gw',
      icon: '⊢',
      keywords: ['mark', 'trace', 'decision'],
      execute: () => {
        trackCommand('action:witness');
        onWitnessMode?.();
      },
    },
    {
      id: 'action:analysis',
      label: 'Show analysis quadrant',
      category: 'actions',
      shortcut: 'ga',
      icon: '⊛',
      keywords: ['analysis', 'categorical', 'epistemic', 'dialectical', 'generative', 'operad'],
      execute: () => {
        trackCommand('action:analysis');
        onAnalysisQuadrant?.();
      },
    },

    // =============================================================================
    // GRAPH NAVIGATION
    // =============================================================================
    {
      id: 'graph:toggle',
      label: 'Toggle graph view',
      category: 'graph',
      shortcut: 'future',
      icon: '⟡',
      keywords: ['hypergraph', 'visualization', 'network'],
      execute: () => {
        trackCommand('graph:toggle');
        onGraphMode?.();
      },
    },

    // =============================================================================
    // ZERO SEED NAVIGATION
    // =============================================================================
    {
      id: 'zeroseed:health',
      label: 'Zero Seed: View Graph Health',
      category: 'navigation',
      icon: '●',
      keywords: ['zero', 'seed', 'health', 'stability', 'contradictions'],
      execute: () => {
        trackCommand('zeroseed:health');
        onZeroSeed?.('health');
      },
    },
    {
      id: 'zeroseed:telescope',
      label: 'Zero Seed: Show Telescope',
      category: 'navigation',
      icon: '⌕',
      keywords: ['zero', 'seed', 'telescope', 'gradient', 'navigation'],
      execute: () => {
        trackCommand('zeroseed:telescope');
        onZeroSeed?.('telescope');
      },
    },
    {
      id: 'zeroseed:axioms',
      label: 'Zero Seed: Explore Axioms',
      category: 'navigation',
      icon: '◇',
      keywords: ['zero', 'seed', 'axioms', 'values', 'ground'],
      execute: () => {
        trackCommand('zeroseed:axioms');
        onZeroSeed?.();
      },
    },
    {
      id: 'zeroseed:proofs',
      label: 'Zero Seed: View Proofs',
      category: 'navigation',
      icon: '⊨',
      keywords: ['zero', 'seed', 'proofs', 'quality', 'toulmin'],
      execute: () => {
        trackCommand('zeroseed:proofs');
        onZeroSeed?.('proofs');
      },
    },

    // =============================================================================
    // AGENTESE PATHS
    // =============================================================================
    {
      id: 'agentese:world',
      label: 'world.* — The External',
      category: 'agentese',
      icon: '∴',
      keywords: ['entities', 'environment', 'tools', 'external'],
      execute: () => {
        trackCommand('agentese:world');
        onAgentese?.('world');
      },
    },
    {
      id: 'agentese:self',
      label: 'self.* — The Internal',
      category: 'agentese',
      icon: '∵',
      keywords: ['memory', 'capability', 'state', 'internal'],
      execute: () => {
        trackCommand('agentese:self');
        onAgentese?.('self');
      },
    },
    {
      id: 'agentese:concept',
      label: 'concept.* — The Abstract',
      category: 'agentese',
      icon: '⟨⟩',
      keywords: ['platonics', 'definitions', 'logic', 'abstract'],
      execute: () => {
        trackCommand('agentese:concept');
        onAgentese?.('concept');
      },
    },
    {
      id: 'agentese:void',
      label: 'void.* — The Accursed Share',
      category: 'agentese',
      icon: '∅',
      keywords: ['entropy', 'serendipity', 'gratitude', 'accursed'],
      execute: () => {
        trackCommand('agentese:void');
        onAgentese?.('void');
      },
    },
    {
      id: 'agentese:time',
      label: 'time.* — The Temporal',
      category: 'agentese',
      icon: '⟳',
      keywords: ['traces', 'forecasts', 'schedules', 'temporal'],
      execute: () => {
        trackCommand('agentese:time');
        onAgentese?.('time');
      },
    },

    // =============================================================================
    // FILES (dynamic from API)
    // =============================================================================
    ...files.map((path) => ({
      id: `file:${path}`,
      label: path,
      category: 'files' as const,
      icon: path.startsWith('spec/') ? '◈' : '▫',
      keywords: path.split('/'),
      execute: () => {
        trackCommand(`file:${path}`);
        onNavigate?.(path);
      },
    })),
  ];

  // Sort commands: recent first, then by category
  const sortedCommands = [...commands].sort((a, b) => {
    const aRecent = recentCommands.indexOf(a.id);
    const bRecent = recentCommands.indexOf(b.id);

    // Recent commands first
    if (aRecent !== -1 && bRecent === -1) return -1;
    if (aRecent === -1 && bRecent !== -1) return 1;
    if (aRecent !== -1 && bRecent !== -1) return aRecent - bRecent;

    // Then by category priority
    const categoryPriority = {
      actions: 0,
      files: 1,
      navigation: 2,
      agentese: 3,
      witness: 4,
      graph: 5,
    };

    return categoryPriority[a.category] - categoryPriority[b.category];
  });

  return {
    commands: sortedCommands,
    recentCommands,
    trackCommand,
  };
}
