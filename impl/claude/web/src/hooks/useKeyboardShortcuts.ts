/**
 * useKeyboardShortcuts — Kent's Decision #6
 *
 * Single-letter keyboard shortcuts for the workspace.
 * Modal editing inspired by vim: navigate, edit, witness modes.
 *
 * Keys:
 * - m = manifest (show K-Block manifest)
 * - w = witness (show witness trail)
 * - t = tithe (pay attention / tend)
 * - f = refine (edit mode)
 * - d = define (new K-Block)
 * - s = sip (quick view / peek)
 * - ? = show help
 * - Escape = cancel / exit mode
 */

import { useEffect, useCallback, useMemo } from 'react';

interface KeyboardShortcuts {
  onManifest?: () => void;
  onWitness?: () => void;
  onTithe?: () => void;
  onRefine?: () => void;
  onDefine?: () => void;
  onSip?: () => void;
  onHelp?: () => void;
  onEscape?: () => void;
}

/** Key mapping for single-letter shortcuts */
type ShortcutKey = 'm' | 'w' | 't' | 'f' | 'd' | 's' | '?' | 'escape';

/**
 * Check if target is an input element where shortcuts should be suppressed.
 */
function isInputElement(target: EventTarget | null): boolean {
  if (!target) return false;
  if (target instanceof HTMLInputElement) return true;
  if (target instanceof HTMLTextAreaElement) return true;
  if (target instanceof HTMLElement && target.isContentEditable) return true;
  return false;
}

export function useKeyboardShortcuts(shortcuts: KeyboardShortcuts) {
  // Build key -> handler map
  const keyMap = useMemo(
    (): Record<ShortcutKey, (() => void) | undefined> => ({
      m: shortcuts.onManifest,
      w: shortcuts.onWitness,
      t: shortcuts.onTithe,
      f: shortcuts.onRefine,
      d: shortcuts.onDefine,
      s: shortcuts.onSip,
      '?': shortcuts.onHelp,
      escape: shortcuts.onEscape,
    }),
    [shortcuts]
  );

  const handleKeyDown = useCallback(
    (e: KeyboardEvent) => {
      const inInput = isInputElement(e.target);

      // Always allow Escape in input fields
      if (inInput) {
        if (e.key === 'Escape') {
          shortcuts.onEscape?.();
        }
        return;
      }

      // Don't trigger with modifiers (except for ?)
      if (e.ctrlKey || e.altKey || e.metaKey) {
        return;
      }

      const key = e.key.toLowerCase() as ShortcutKey;
      const handler = keyMap[key];

      if (handler) {
        if (key === '?') e.preventDefault();
        handler();
      }
    },
    [keyMap, shortcuts]
  );

  useEffect(() => {
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [handleKeyDown]);
}
