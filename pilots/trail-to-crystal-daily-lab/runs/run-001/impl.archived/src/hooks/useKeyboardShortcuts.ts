/**
 * useKeyboardShortcuts Hook
 *
 * React hook for managing global keyboard shortcuts.
 * Supports cross-platform modifier keys (Cmd on Mac, Ctrl on Windows/Linux).
 *
 * @example
 * ```tsx
 * useKeyboardShortcuts({
 *   'mod+1': () => navigate('/daily-lab'),
 *   'mod+2': () => navigate('/daily-lab/trail'),
 *   'mod+enter': () => handleSubmit(),
 *   'escape': () => clearInput(),
 * });
 * ```
 */

import { useEffect, useCallback, useRef } from 'react';

// =============================================================================
// Types
// =============================================================================

/** Shortcut handler function */
export type ShortcutHandler = (event: KeyboardEvent) => void;

/** Map of shortcut patterns to handlers */
export type ShortcutMap = Record<string, ShortcutHandler>;

/** Options for the hook */
export interface UseKeyboardShortcutsOptions {
  /** Whether shortcuts are enabled (default: true) */
  enabled?: boolean;
  /** Prevent default browser behavior for matched shortcuts (default: true) */
  preventDefault?: boolean;
  /** Stop propagation for matched shortcuts (default: true) */
  stopPropagation?: boolean;
  /** Target element (default: document) */
  target?: EventTarget | null;
}

// =============================================================================
// Platform Detection
// =============================================================================

/**
 * Check if the current platform is macOS.
 * Uses navigator.platform with userAgentData fallback.
 */
export function isMacOS(): boolean {
  if (typeof navigator === 'undefined') return false;

  // Modern API
  if ('userAgentData' in navigator) {
    const uaData = navigator.userAgentData as { platform?: string };
    if (uaData.platform) {
      return uaData.platform.toLowerCase().includes('mac');
    }
  }

  // Fallback to platform
  return navigator.platform?.toLowerCase().includes('mac') ?? false;
}

/**
 * Get the modifier key symbol for the current platform.
 * Returns command symbol for Mac, "Ctrl" for others.
 */
export function getModifierSymbol(): string {
  return isMacOS() ? '\u2318' : 'Ctrl';
}

/**
 * Get the modifier key name for the current platform.
 */
export function getModifierName(): string {
  return isMacOS() ? 'Cmd' : 'Ctrl';
}

// =============================================================================
// Shortcut Parsing
// =============================================================================

interface ParsedShortcut {
  key: string;
  mod: boolean;   // Cmd on Mac, Ctrl on Windows/Linux
  ctrl: boolean;  // Explicit Ctrl
  alt: boolean;
  shift: boolean;
}

/**
 * Parse a shortcut string into its components.
 * Supports: mod, ctrl, alt, shift modifiers.
 *
 * @example
 * parseShortcut('mod+1') // { key: '1', mod: true, ... }
 * parseShortcut('shift+enter') // { key: 'enter', shift: true, ... }
 */
function parseShortcut(shortcut: string): ParsedShortcut {
  const parts = shortcut.toLowerCase().split('+');
  const key = parts[parts.length - 1];

  return {
    key,
    mod: parts.includes('mod'),
    ctrl: parts.includes('ctrl'),
    alt: parts.includes('alt'),
    shift: parts.includes('shift'),
  };
}

/**
 * Check if a keyboard event matches a parsed shortcut.
 */
function matchesShortcut(event: KeyboardEvent, parsed: ParsedShortcut): boolean {
  // Check key (normalize common aliases)
  const eventKey = event.key.toLowerCase();
  const targetKey = parsed.key;

  // Handle special key aliases
  const keyMatches =
    eventKey === targetKey ||
    (targetKey === 'enter' && eventKey === 'enter') ||
    (targetKey === 'escape' && (eventKey === 'escape' || eventKey === 'esc')) ||
    (targetKey === 'space' && eventKey === ' ');

  if (!keyMatches) return false;

  // Check modifiers
  const isMac = isMacOS();

  // 'mod' means Cmd on Mac, Ctrl on Windows/Linux
  if (parsed.mod) {
    const modPressed = isMac ? event.metaKey : event.ctrlKey;
    if (!modPressed) return false;
  }

  // Explicit ctrl check (separate from mod)
  if (parsed.ctrl && !event.ctrlKey) return false;

  // Alt/Option check
  if (parsed.alt && !event.altKey) return false;

  // Shift check
  if (parsed.shift && !event.shiftKey) return false;

  // Ensure we're not matching if extra modifiers are pressed that weren't specified
  // (unless mod is specified, which covers the platform-specific modifier)
  if (!parsed.mod && !parsed.ctrl && (isMac ? event.metaKey : event.ctrlKey)) {
    // Allow if no modifiers were specified at all
    if (!parsed.alt && !parsed.shift) {
      // No modifiers specified but modifier pressed - skip this shortcut
      // to allow browser defaults through
    }
  }

  return true;
}

// =============================================================================
// Hook
// =============================================================================

/**
 * useKeyboardShortcuts
 *
 * Registers global keyboard shortcuts with automatic cleanup.
 * Handles cross-platform modifier differences (Cmd/Ctrl).
 *
 * @param shortcuts - Map of shortcut patterns to handler functions
 * @param options - Optional configuration
 */
export function useKeyboardShortcuts(
  shortcuts: ShortcutMap,
  options: UseKeyboardShortcutsOptions = {}
): void {
  const {
    enabled = true,
    preventDefault = true,
    stopPropagation = true,
    target = typeof document !== 'undefined' ? document : null,
  } = options;

  // Keep shortcuts stable via ref to avoid re-attaching listeners
  const shortcutsRef = useRef(shortcuts);
  shortcutsRef.current = shortcuts;

  // Parse shortcuts once
  const parsedShortcutsRef = useRef<Map<string, ParsedShortcut>>(new Map());

  // Update parsed shortcuts when shortcuts change
  useEffect(() => {
    const parsed = new Map<string, ParsedShortcut>();
    for (const key of Object.keys(shortcuts)) {
      parsed.set(key, parseShortcut(key));
    }
    parsedShortcutsRef.current = parsed;
  }, [shortcuts]);

  // Event handler
  const handleKeyDown = useCallback(
    (event: Event) => {
      if (!enabled) return;

      const keyEvent = event as KeyboardEvent;

      // Skip if focus is in an input/textarea/contenteditable
      const target = keyEvent.target as HTMLElement;
      if (
        target.tagName === 'INPUT' ||
        target.tagName === 'TEXTAREA' ||
        target.isContentEditable
      ) {
        // Allow escape to work in inputs
        if (keyEvent.key.toLowerCase() !== 'escape') {
          return;
        }
      }

      // Check each shortcut
      for (const [pattern, parsed] of parsedShortcutsRef.current.entries()) {
        if (matchesShortcut(keyEvent, parsed)) {
          const handler = shortcutsRef.current[pattern];
          if (handler) {
            if (preventDefault) {
              keyEvent.preventDefault();
            }
            if (stopPropagation) {
              keyEvent.stopPropagation();
            }
            handler(keyEvent);
            return;
          }
        }
      }
    },
    [enabled, preventDefault, stopPropagation]
  );

  // Attach/detach event listener
  useEffect(() => {
    if (!target || !enabled) return;

    target.addEventListener('keydown', handleKeyDown);

    return () => {
      target.removeEventListener('keydown', handleKeyDown);
    };
  }, [target, enabled, handleKeyDown]);
}

export default useKeyboardShortcuts;
