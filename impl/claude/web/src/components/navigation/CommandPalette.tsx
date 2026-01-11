/**
 * CommandPalette — VS Code-style command palette for kgents
 *
 * Philosophy: "Ctrl+K is the universal gateway to action."
 *
 * Features:
 * - Global Ctrl+K shortcut
 * - Fuzzy search across all commands
 * - Grouped results (navigation, action, agentese, recent)
 * - Keyboard navigation (j/k, arrows, Enter, Esc)
 * - Shortcuts displayed next to items
 * - AGENTESE path invocation support
 *
 * STARK BIOME: 90% steel, 10% earned glow
 */

import { useCallback, useEffect, useRef, KeyboardEvent } from 'react';
import { createPortal } from 'react-dom';

import { useCommandPalette, type Command, type CommandCategory } from '@/hooks/useCommandPalette';

import './CommandPalette.css';

// =============================================================================
// Types
// =============================================================================

export interface CommandPaletteProps {
  /** Custom commands to add */
  customCommands?: Command[];
  /** Callback when command is executed */
  onExecute?: (command: Command) => void;
}

// =============================================================================
// Category Labels
// =============================================================================

const CATEGORY_LABELS: Record<CommandCategory, string> = {
  recent: 'Recent',
  navigation: 'Navigate',
  action: 'Actions',
  workflow: 'Workflow',
  agentese: 'AGENTESE',
};

const CATEGORY_ICONS: Record<CommandCategory, string> = {
  recent: '\u23F0', // ⏰
  navigation: '\u2630', // ☰
  action: '\u26A1', // ⚡
  workflow: '\u2699', // ⚙
  agentese: '\u25C7', // ◇
};

// =============================================================================
// Command Item Component
// =============================================================================

interface CommandItemProps {
  command: Command;
  isSelected: boolean;
  onClick: () => void;
  onMouseEnter: () => void;
}

function CommandItem({ command, isSelected, onClick, onMouseEnter }: CommandItemProps) {
  const itemRef = useRef<HTMLDivElement>(null);

  // Scroll into view when selected
  useEffect(() => {
    if (isSelected && itemRef.current) {
      itemRef.current.scrollIntoView({ block: 'nearest' });
    }
  }, [isSelected]);

  return (
    <div
      ref={itemRef}
      className={`command-palette__item ${isSelected ? 'command-palette__item--selected' : ''}`}
      onClick={onClick}
      onMouseEnter={onMouseEnter}
      role="option"
      aria-selected={isSelected}
    >
      <span className="command-palette__item-icon">{command.icon || '\u25CF'}</span>
      <div className="command-palette__item-content">
        <span className="command-palette__item-label">{command.label}</span>
        {command.description && (
          <span className="command-palette__item-description">{command.description}</span>
        )}
      </div>
      {command.shortcut && <kbd className="command-palette__item-shortcut">{command.shortcut}</kbd>}
    </div>
  );
}

// =============================================================================
// Command Group Component
// =============================================================================

interface CommandGroupProps {
  category: CommandCategory;
  commands: Command[];
  selectedIndex: number;
  startIndex: number;
  onSelect: (command: Command) => void;
  onHover: (index: number) => void;
}

function CommandGroup({
  category,
  commands,
  selectedIndex,
  startIndex,
  onSelect,
  onHover,
}: CommandGroupProps) {
  if (commands.length === 0) return null;

  return (
    <div className="command-palette__group">
      <div className="command-palette__group-header">
        <span className="command-palette__group-icon">{CATEGORY_ICONS[category]}</span>
        <span className="command-palette__group-label">{CATEGORY_LABELS[category]}</span>
        <span className="command-palette__group-count">{commands.length}</span>
      </div>
      <div className="command-palette__group-items" role="listbox">
        {commands.map((cmd, idx) => (
          <CommandItem
            key={cmd.id}
            command={cmd}
            isSelected={selectedIndex === startIndex + idx}
            onClick={() => onSelect(cmd)}
            onMouseEnter={() => onHover(startIndex + idx)}
          />
        ))}
      </div>
    </div>
  );
}

// =============================================================================
// Main Component
// =============================================================================

export function CommandPalette({ customCommands, onExecute }: CommandPaletteProps) {
  const {
    state,
    close,
    setQuery,
    selectPrev,
    selectNext,
    executeSelected,
    executeCommand,
    setSelectedIndex,
  } = useCommandPalette({ customCommands, onExecute });

  const inputRef = useRef<HTMLInputElement>(null);
  const overlayRef = useRef<HTMLDivElement>(null);

  // Focus input when opened
  useEffect(() => {
    if (state.isOpen && inputRef.current) {
      inputRef.current.focus();
    }
  }, [state.isOpen]);

  // Handle keyboard navigation
  const handleKeyDown = useCallback(
    (e: KeyboardEvent<HTMLDivElement>) => {
      switch (e.key) {
        case 'ArrowDown':
        case 'j':
          if (!e.ctrlKey && !e.metaKey) {
            e.preventDefault();
            selectNext();
          }
          break;

        case 'ArrowUp':
        case 'k':
          if (!e.ctrlKey && !e.metaKey) {
            e.preventDefault();
            selectPrev();
          }
          break;

        case 'Enter':
          e.preventDefault();
          executeSelected();
          break;

        case 'Escape':
          e.preventDefault();
          close();
          break;

        case 'Tab':
          // Prevent tab from leaving the palette
          e.preventDefault();
          if (e.shiftKey) {
            selectPrev();
          } else {
            selectNext();
          }
          break;
      }
    },
    [selectNext, selectPrev, executeSelected, close]
  );

  // Handle overlay click (close on click outside)
  const handleOverlayClick = useCallback(
    (e: React.MouseEvent) => {
      if (e.target === overlayRef.current) {
        close();
      }
    },
    [close]
  );

  // Don't render if not open
  if (!state.isOpen) {
    return null;
  }

  // Calculate start indices for each group (for selection tracking)
  let currentIndex = 0;
  const groupStartIndices = new Map<CommandCategory, number>();
  for (const [category, commands] of state.groupedCommands) {
    groupStartIndices.set(category, currentIndex);
    currentIndex += commands.length;
  }

  const content = (
    <div
      ref={overlayRef}
      className="command-palette__overlay"
      onClick={handleOverlayClick}
      onKeyDown={handleKeyDown}
      role="dialog"
      aria-modal="true"
      aria-label="Command Palette"
    >
      <div className="command-palette">
        {/* Search Header */}
        <div className="command-palette__header">
          <span className="command-palette__search-icon">{'\u2315'}</span>
          <input
            ref={inputRef}
            type="text"
            className="command-palette__input"
            placeholder="Type a command or search..."
            value={state.query}
            onChange={(e) => setQuery(e.target.value)}
            aria-label="Search commands"
            aria-autocomplete="list"
            aria-controls="command-palette-results"
          />
          <kbd className="command-palette__hint">esc</kbd>
        </div>

        {/* Results */}
        <div className="command-palette__results" id="command-palette-results">
          {state.filteredCommands.length === 0 ? (
            <div className="command-palette__empty">
              <p>No commands found</p>
              <span className="command-palette__empty-hint">Try a different search term</span>
            </div>
          ) : (
            Array.from(state.groupedCommands.entries()).map(([category, commands]) => (
              <CommandGroup
                key={category}
                category={category}
                commands={commands}
                selectedIndex={state.selectedIndex}
                startIndex={groupStartIndices.get(category) || 0}
                onSelect={executeCommand}
                onHover={setSelectedIndex}
              />
            ))
          )}
        </div>

        {/* Footer with keyboard hints */}
        <div className="command-palette__footer">
          <div className="command-palette__hints">
            <span>
              <kbd>{'\u2191'}</kbd>
              <kbd>{'\u2193'}</kbd>
              or
              <kbd>j</kbd>
              <kbd>k</kbd>
              navigate
            </span>
            <span className="command-palette__separator">{'\u2022'}</span>
            <span>
              <kbd>Enter</kbd>
              select
            </span>
            <span className="command-palette__separator">{'\u2022'}</span>
            <span>
              <kbd>Esc</kbd>
              close
            </span>
          </div>
        </div>
      </div>
    </div>
  );

  // Render via portal to ensure it's above everything
  return createPortal(content, document.body);
}

export default CommandPalette;
