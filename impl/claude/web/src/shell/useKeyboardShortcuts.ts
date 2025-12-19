/**
 * useKeyboardShortcuts - Global keyboard shortcuts for the OS Shell
 *
 * Provides keyboard-driven navigation and control:
 * - Escape: Close panels (terminal, nav tree, observer drawer)
 * - Ctrl+`: Focus terminal
 * - Cmd/Ctrl+K: Open command palette
 * - ?: Show keyboard shortcut hints
 *
 * @see spec/protocols/os-shell.md
 */

import { useEffect, useCallback } from 'react';

// =============================================================================
// Types
// =============================================================================

export interface KeyboardShortcut {
  /** Unique identifier for the shortcut */
  id: string;
  /** Display label for the shortcut */
  label: string;
  /** Key combination description (for UI) */
  keys: string;
  /** Category for grouping in hints overlay */
  category: 'navigation' | 'panels' | 'actions' | 'terminal';
  /** Handler function */
  handler: () => void;
  /** Whether this shortcut is currently enabled */
  enabled?: boolean;
}

export interface UseKeyboardShortcutsOptions {
  /** Callback to close all panels */
  onCloseAllPanels: () => void;
  /** Callback to focus terminal */
  onFocusTerminal: () => void;
  /** Callback to toggle terminal */
  onToggleTerminal: () => void;
  /** Callback to toggle nav tree */
  onToggleNavTree: () => void;
  /** Callback to toggle observer drawer */
  onToggleObserver: () => void;
  /** Callback to open command palette */
  onOpenCommandPalette: () => void;
  /** Callback to show keyboard hints */
  onShowKeyboardHints: () => void;
  /** Callback to open path search (slash key) */
  onOpenPathSearch?: () => void;
  /** Whether shortcuts are enabled */
  enabled?: boolean;
}

export interface UseKeyboardShortcutsReturn {
  /** List of all registered shortcuts (for hints overlay) */
  shortcuts: KeyboardShortcut[];
}

// =============================================================================
// Constants
// =============================================================================

/** Check if we're on Mac */
const isMac = typeof navigator !== 'undefined' && /Mac|iPod|iPhone|iPad/.test(navigator.platform);

/** Modifier key name for display */
const MOD_KEY = isMac ? '⌘' : 'Ctrl';

// =============================================================================
// Hook
// =============================================================================

/**
 * Hook for global keyboard shortcuts in the OS Shell.
 *
 * @example
 * ```tsx
 * const { shortcuts } = useKeyboardShortcuts({
 *   onCloseAllPanels: () => { ... },
 *   onFocusTerminal: () => { ... },
 *   onOpenCommandPalette: () => { ... },
 *   onShowKeyboardHints: () => { ... },
 * });
 * ```
 */
export function useKeyboardShortcuts({
  onCloseAllPanels,
  onFocusTerminal,
  onToggleTerminal,
  onToggleNavTree,
  onToggleObserver,
  onOpenCommandPalette,
  onShowKeyboardHints,
  onOpenPathSearch,
  enabled = true,
}: UseKeyboardShortcutsOptions): UseKeyboardShortcutsReturn {

  // Build shortcuts list for hints overlay
  const shortcuts: KeyboardShortcut[] = [
    {
      id: 'close-panels',
      label: 'Close panels',
      keys: 'Esc',
      category: 'panels',
      handler: onCloseAllPanels,
    },
    {
      id: 'focus-terminal',
      label: 'Focus terminal',
      keys: 'Ctrl+`',
      category: 'terminal',
      handler: onFocusTerminal,
    },
    {
      id: 'toggle-terminal',
      label: 'Toggle terminal',
      keys: `${MOD_KEY}+J`,
      category: 'terminal',
      handler: onToggleTerminal,
    },
    {
      id: 'toggle-nav',
      label: 'Toggle navigation',
      keys: `${MOD_KEY}+B`,
      category: 'panels',
      handler: onToggleNavTree,
    },
    {
      id: 'toggle-observer',
      label: 'Toggle observer',
      keys: `${MOD_KEY}+O`,
      category: 'panels',
      handler: onToggleObserver,
    },
    {
      id: 'command-palette',
      label: 'Command palette',
      keys: `${MOD_KEY}+K`,
      category: 'actions',
      handler: onOpenCommandPalette,
    },
    {
      id: 'keyboard-hints',
      label: 'Keyboard shortcuts',
      keys: '?',
      category: 'actions',
      handler: onShowKeyboardHints,
    },
    ...(onOpenPathSearch ? [{
      id: 'path-search',
      label: 'Go to path',
      keys: '/',
      category: 'navigation' as const,
      handler: onOpenPathSearch,
    }] : []),
  ];

  // Check if the active element is an input
  const isInputActive = useCallback((): boolean => {
    const active = document.activeElement;
    if (!active) return false;
    const tagName = active.tagName.toLowerCase();
    return (
      tagName === 'input' ||
      tagName === 'textarea' ||
      tagName === 'select' ||
      (active as HTMLElement).isContentEditable
    );
  }, []);

  // Handle keydown events
  const handleKeyDown = useCallback(
    (event: KeyboardEvent) => {
      if (!enabled) return;

      const { key, ctrlKey, metaKey, shiftKey } = event;
      const modKey = isMac ? metaKey : ctrlKey;

      // Escape - close panels (works even in inputs)
      if (key === 'Escape') {
        event.preventDefault();
        onCloseAllPanels();
        return;
      }

      // Don't process other shortcuts if typing in an input
      // Exception: Cmd+K should work everywhere (standard pattern)
      if (isInputActive()) {
        // Cmd/Ctrl+K - command palette (works in inputs)
        if (modKey && key.toLowerCase() === 'k') {
          event.preventDefault();
          onOpenCommandPalette();
        }
        return;
      }

      // Ctrl+` - focus terminal
      if (ctrlKey && key === '`') {
        event.preventDefault();
        onFocusTerminal();
        return;
      }

      // Cmd/Ctrl+J - toggle terminal
      if (modKey && key.toLowerCase() === 'j') {
        event.preventDefault();
        onToggleTerminal();
        return;
      }

      // Cmd/Ctrl+B - toggle nav tree
      if (modKey && key.toLowerCase() === 'b') {
        event.preventDefault();
        onToggleNavTree();
        return;
      }

      // Cmd/Ctrl+O - toggle observer (prevent browser "Open file" dialog)
      if (modKey && key.toLowerCase() === 'o') {
        event.preventDefault();
        onToggleObserver();
        return;
      }

      // Cmd/Ctrl+K - command palette
      if (modKey && key.toLowerCase() === 'k') {
        event.preventDefault();
        onOpenCommandPalette();
        return;
      }

      // ? - show keyboard hints (only when shift is pressed for '?')
      if (key === '?' || (shiftKey && key === '/')) {
        event.preventDefault();
        onShowKeyboardHints();
        return;
      }

      // / - open path search (without shift - just forward slash)
      if (key === '/' && !shiftKey && onOpenPathSearch) {
        event.preventDefault();
        onOpenPathSearch();
        return;
      }
    },
    [
      enabled,
      isInputActive,
      onCloseAllPanels,
      onFocusTerminal,
      onToggleTerminal,
      onToggleNavTree,
      onToggleObserver,
      onOpenCommandPalette,
      onShowKeyboardHints,
      onOpenPathSearch,
    ]
  );

  // Register global keydown listener
  useEffect(() => {
    if (!enabled) return;

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [enabled, handleKeyDown]);

  return { shortcuts };
}

export default useKeyboardShortcuts;
