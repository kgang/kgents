/**
 * CommandPalette — Fullscreen Cmd+K command interface
 *
 * "Power through keystrokes, not IDE heaviness."
 * "Cmd+K is not a shortcut. It's a philosophy."
 *
 * Architecture:
 * - Fullscreen modal triggered by Cmd+K
 * - Built on cmdk (Pacocoursey's battle-tested command palette)
 * - Fuzzy search with command-score (built into cmdk)
 * - Categories: Files, Actions, AGENTESE paths
 * - STARK BIOME styling (dark theme)
 * - Recency tracking via useCommandRegistry
 *
 * Key Behaviors:
 * - Cmd+K opens palette (prevents default Meta+K!)
 * - Type to fuzzy search
 * - Up/Down or j/k to navigate
 * - Enter to execute, Esc to dismiss
 * - Results grouped by category
 * - Recent commands at top
 */

import { memo, useEffect, useState } from 'react';
import { Command } from 'cmdk';

import { useCommandRegistry } from './useCommandRegistry';
import type { Command as CommandType } from './useCommandRegistry';

import './CommandPalette.css';

// =============================================================================
// Types
// =============================================================================

interface CommandPaletteProps {
  /** Whether the palette is open */
  open: boolean;

  /** Called when the palette should close */
  onClose: () => void;

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

  /** Callback to invoke AGENTESE path */
  onAgentese?: (path: string) => void;

  /** Callback to navigate to Zero Seed */
  onZeroSeed?: (tab?: string) => void;
}

// =============================================================================
// Component
// =============================================================================

export const CommandPalette = memo(function CommandPalette({
  open,
  onClose,
  onNavigate,
  onWitnessMode,
  onSave,
  onReanalyze,
  onGraphMode,
  onAgentese,
  onZeroSeed,
}: CommandPaletteProps) {
  const [search, setSearch] = useState('');

  const { commands } = useCommandRegistry({
    onNavigate,
    onWitnessMode,
    onSave,
    onReanalyze,
    onGraphMode,
    onAgentese,
    onZeroSeed,
  });

  // Reset search when opening
  useEffect(() => {
    if (open) {
      setSearch('');
    }
  }, [open]);

  // Handle command execution
  const handleSelect = (commandId: string) => {
    const command = commands.find((c) => c.id === commandId);
    if (command) {
      command.execute();
      onClose();
    }
  };

  // Group commands by category
  const groupedCommands = commands.reduce(
    (acc, cmd) => {
      if (!acc[cmd.category]) {
        acc[cmd.category] = [];
      }
      acc[cmd.category].push(cmd);
      return acc;
    },
    {} as Record<string, CommandType[]>
  );

  // Category display order and labels
  const categories = [
    { key: 'actions', label: 'Actions', icon: '⚡' },
    { key: 'files', label: 'Files', icon: '📁' },
    { key: 'agentese', label: 'AGENTESE', icon: '🔮' },
    { key: 'navigation', label: 'Navigation', icon: '🧭' },
    { key: 'witness', label: 'Witness', icon: '👁️' },
    { key: 'graph', label: 'Graph', icon: '🕸️' },
  ] as const;

  if (!open) return null;

  return (
    <div className="command-palette" onClick={onClose}>
      <Command
        className="command-palette__dialog"
        shouldFilter={false} // We handle filtering via search state
        loop
        onKeyDown={(e) => {
          if (e.key === 'Escape') {
            e.preventDefault();
            onClose();
          }
        }}
        onClick={(e) => e.stopPropagation()}
      >
        <div className="command-palette__header">
          <Command.Input
            className="command-palette__input"
            placeholder="Type a command or search..."
            value={search}
            onValueChange={setSearch}
            autoFocus
          />
        </div>

        <Command.List className="command-palette__list">
          <Command.Empty className="command-palette__empty">
            No commands found.
          </Command.Empty>

          {categories.map(({ key, label, icon }) => {
            const categoryCommands = groupedCommands[key];
            if (!categoryCommands || categoryCommands.length === 0) return null;

            // Filter commands by search
            const filteredCommands = categoryCommands.filter((cmd) => {
              if (!search) return true;
              const searchLower = search.toLowerCase();
              const labelMatch = cmd.label.toLowerCase().includes(searchLower);
              const keywordMatch = cmd.keywords?.some((kw) =>
                kw.toLowerCase().includes(searchLower)
              );
              return labelMatch || keywordMatch;
            });

            if (filteredCommands.length === 0) return null;

            return (
              <Command.Group
                key={key}
                heading={`${icon} ${label}`}
                className="command-palette__group"
              >
                {filteredCommands.map((cmd) => (
                  <Command.Item
                    key={cmd.id}
                    value={cmd.id}
                    onSelect={handleSelect}
                    className="command-palette__item"
                  >
                    <span className="command-palette__item-icon">{cmd.icon}</span>
                    <span className="command-palette__item-label">{cmd.label}</span>
                    {cmd.shortcut && (
                      <kbd className="command-palette__item-shortcut">{cmd.shortcut}</kbd>
                    )}
                  </Command.Item>
                ))}
              </Command.Group>
            );
          })}
        </Command.List>

        <div className="command-palette__footer">
          <span className="command-palette__hint">
            <kbd>↑↓</kbd> Navigate • <kbd>Enter</kbd> Execute • <kbd>Esc</kbd> Close
          </span>
        </div>
      </Command>
    </div>
  );
});
