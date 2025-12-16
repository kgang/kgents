/**
 * useKeyboardShortcuts: Global keyboard shortcut handler.
 *
 * Registers and manages keyboard shortcuts across the application.
 * Supports different shortcut contexts (global, build mode, etc.)
 * and handles modifier keys.
 *
 * @see plans/web-refactor/interaction-patterns.md
 */

import { useEffect, useCallback, useRef } from 'react';

// =============================================================================
// Types
// =============================================================================

/**
 * Shortcut context determines which shortcuts are active.
 */
export type ShortcutContext = 'global' | 'build' | 'historical' | 'inhabit';

/**
 * Modifier keys that can be combined with shortcuts.
 */
export interface Modifiers {
  ctrl?: boolean;
  alt?: boolean;
  shift?: boolean;
  meta?: boolean;
}

/**
 * Definition of a keyboard shortcut.
 */
export interface ShortcutDefinition {
  /** Primary key (e.g., 'Space', 'b', 'Delete') */
  key: string;

  /** Required modifier keys */
  modifiers?: Modifiers;

  /** Contexts in which this shortcut is active */
  contexts: ShortcutContext[];

  /** Human-readable description */
  description: string;

  /** Callback to execute */
  handler: (event: KeyboardEvent) => void;

  /** Whether to prevent default browser behavior */
  preventDefault?: boolean;
}

/**
 * Options for the hook.
 */
export interface UseKeyboardShortcutsOptions {
  /** Current active context */
  context?: ShortcutContext;

  /** Whether shortcuts are enabled */
  enabled?: boolean;

  /** Element to attach listeners to (defaults to document) */
  target?: EventTarget;
}

/**
 * Return value from the hook.
 */
export interface UseKeyboardShortcutsReturn {
  /** Register a new shortcut */
  register: (shortcut: ShortcutDefinition) => () => void;

  /** Unregister a shortcut by key */
  unregister: (key: string, modifiers?: Modifiers) => void;

  /** Get all registered shortcuts for current context */
  getActiveShortcuts: () => ShortcutDefinition[];

  /** Get all registered shortcuts */
  getAllShortcuts: () => ShortcutDefinition[];
}

// =============================================================================
// Default Shortcuts
// =============================================================================

/**
 * Creates default shortcuts for common actions.
 */
export function createDefaultShortcuts(handlers: {
  onTogglePlay?: () => void;
  onToggleBuildMode?: () => void;
  onToggleHistoricalMode?: () => void;
  onUndo?: () => void;
  onRedo?: () => void;
  onDelete?: () => void;
  onSave?: () => void;
  onShowHelp?: () => void;
  onEscape?: () => void;
  onSelectAgent?: (index: number) => void;
  onStepForward?: () => void;
  onStepBackward?: () => void;
}): ShortcutDefinition[] {
  const shortcuts: ShortcutDefinition[] = [];

  // Global shortcuts
  if (handlers.onTogglePlay) {
    shortcuts.push({
      key: ' ',
      contexts: ['global', 'historical'],
      description: 'Play/Pause simulation',
      handler: handlers.onTogglePlay,
      preventDefault: true,
    });
  }

  if (handlers.onToggleBuildMode) {
    shortcuts.push({
      key: 'b',
      contexts: ['global'],
      description: 'Toggle build mode',
      handler: handlers.onToggleBuildMode,
    });
  }

  if (handlers.onToggleHistoricalMode) {
    shortcuts.push({
      key: 'h',
      contexts: ['global'],
      description: 'Toggle historical mode',
      handler: handlers.onToggleHistoricalMode,
    });
  }

  if (handlers.onShowHelp) {
    shortcuts.push({
      key: '?',
      contexts: ['global', 'build', 'historical', 'inhabit'],
      description: 'Show keyboard shortcuts',
      handler: handlers.onShowHelp,
    });
  }

  if (handlers.onEscape) {
    shortcuts.push({
      key: 'Escape',
      contexts: ['global', 'build', 'historical', 'inhabit'],
      description: 'Close modal / exit mode',
      handler: handlers.onEscape,
    });
  }

  // Build mode shortcuts
  if (handlers.onUndo) {
    shortcuts.push({
      key: 'z',
      modifiers: { ctrl: true },
      contexts: ['build'],
      description: 'Undo',
      handler: handlers.onUndo,
      preventDefault: true,
    });
    shortcuts.push({
      key: 'z',
      modifiers: { meta: true },
      contexts: ['build'],
      description: 'Undo',
      handler: handlers.onUndo,
      preventDefault: true,
    });
  }

  if (handlers.onRedo) {
    shortcuts.push({
      key: 'z',
      modifiers: { ctrl: true, shift: true },
      contexts: ['build'],
      description: 'Redo',
      handler: handlers.onRedo,
      preventDefault: true,
    });
    shortcuts.push({
      key: 'z',
      modifiers: { meta: true, shift: true },
      contexts: ['build'],
      description: 'Redo',
      handler: handlers.onRedo,
      preventDefault: true,
    });
  }

  if (handlers.onDelete) {
    shortcuts.push({
      key: 'Delete',
      contexts: ['build'],
      description: 'Delete selected',
      handler: handlers.onDelete,
    });
    shortcuts.push({
      key: 'Backspace',
      contexts: ['build'],
      description: 'Delete selected',
      handler: handlers.onDelete,
    });
  }

  if (handlers.onSave) {
    shortcuts.push({
      key: 's',
      modifiers: { ctrl: true },
      contexts: ['build'],
      description: 'Save pipeline',
      handler: handlers.onSave,
      preventDefault: true,
    });
    shortcuts.push({
      key: 's',
      modifiers: { meta: true },
      contexts: ['build'],
      description: 'Save pipeline',
      handler: handlers.onSave,
      preventDefault: true,
    });
  }

  // Historical mode shortcuts
  if (handlers.onStepForward) {
    shortcuts.push({
      key: 'ArrowRight',
      contexts: ['historical'],
      description: 'Step forward',
      handler: handlers.onStepForward,
    });
  }

  if (handlers.onStepBackward) {
    shortcuts.push({
      key: 'ArrowLeft',
      contexts: ['historical'],
      description: 'Step backward',
      handler: handlers.onStepBackward,
    });
  }

  // Number keys for agent selection
  if (handlers.onSelectAgent) {
    for (let i = 1; i <= 9; i++) {
      shortcuts.push({
        key: String(i),
        contexts: ['global'],
        description: `Select agent ${i}`,
        handler: () => handlers.onSelectAgent!(i - 1),
      });
    }
  }

  return shortcuts;
}

// =============================================================================
// Hook
// =============================================================================

export function useKeyboardShortcuts({
  context = 'global',
  enabled = true,
  target,
}: UseKeyboardShortcutsOptions = {}): UseKeyboardShortcutsReturn {
  // Store shortcuts in a ref to avoid re-renders
  const shortcutsRef = useRef<Map<string, ShortcutDefinition>>(new Map());

  // Create a key for the shortcut map
  const getShortcutKey = useCallback((key: string, modifiers?: Modifiers): string => {
    const parts: string[] = [];
    if (modifiers?.ctrl) parts.push('ctrl');
    if (modifiers?.alt) parts.push('alt');
    if (modifiers?.shift) parts.push('shift');
    if (modifiers?.meta) parts.push('meta');
    parts.push(key.toLowerCase());
    return parts.join('+');
  }, []);

  // Register a shortcut
  const register = useCallback((shortcut: ShortcutDefinition) => {
    const key = getShortcutKey(shortcut.key, shortcut.modifiers);
    shortcutsRef.current.set(key, shortcut);

    // Return unregister function
    return () => {
      shortcutsRef.current.delete(key);
    };
  }, [getShortcutKey]);

  // Unregister a shortcut
  const unregister = useCallback((key: string, modifiers?: Modifiers) => {
    const mapKey = getShortcutKey(key, modifiers);
    shortcutsRef.current.delete(mapKey);
  }, [getShortcutKey]);

  // Get active shortcuts for current context
  const getActiveShortcuts = useCallback(() => {
    return Array.from(shortcutsRef.current.values())
      .filter((s) => s.contexts.includes(context));
  }, [context]);

  // Get all shortcuts
  const getAllShortcuts = useCallback(() => {
    return Array.from(shortcutsRef.current.values());
  }, []);

  // Handle keyboard events
  useEffect(() => {
    if (!enabled) return;

    const handleKeyDown = (event: Event) => {
      const e = event as KeyboardEvent;

      // Ignore events from input elements
      const target = e.target as HTMLElement;
      if (
        target.tagName === 'INPUT' ||
        target.tagName === 'TEXTAREA' ||
        target.isContentEditable
      ) {
        return;
      }

      // Build the key for lookup
      const modifiers: Modifiers = {
        ctrl: e.ctrlKey,
        alt: e.altKey,
        shift: e.shiftKey,
        meta: e.metaKey,
      };
      const key = getShortcutKey(e.key, modifiers);

      // Look up the shortcut
      const shortcut = shortcutsRef.current.get(key);
      if (!shortcut) return;

      // Check if shortcut is active in current context
      if (!shortcut.contexts.includes(context)) return;

      // Execute handler
      if (shortcut.preventDefault) {
        e.preventDefault();
      }
      shortcut.handler(e);
    };

    const eventTarget = target || document;
    eventTarget.addEventListener('keydown', handleKeyDown);

    return () => {
      eventTarget.removeEventListener('keydown', handleKeyDown);
    };
  }, [enabled, context, target, getShortcutKey]);

  return {
    register,
    unregister,
    getActiveShortcuts,
    getAllShortcuts,
  };
}

export default useKeyboardShortcuts;
