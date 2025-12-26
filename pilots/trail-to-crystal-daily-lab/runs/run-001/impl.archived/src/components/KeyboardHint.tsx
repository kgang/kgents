/**
 * KeyboardHint Component
 *
 * Displays subtle keyboard shortcut hints with platform-aware modifier symbols.
 * Uses LIVING_EARTH sage color for a muted, non-distracting appearance.
 *
 * @example
 * ```tsx
 * <KeyboardHint shortcut="1" /> // Shows "Cmd+1" on Mac, "Ctrl+1" on Windows
 * <KeyboardHint shortcut="Enter" showMod />
 * ```
 */

import { useMemo } from 'react';
import { isMacOS, getModifierSymbol } from '../hooks/useKeyboardShortcuts';

// =============================================================================
// Types
// =============================================================================

export interface KeyboardHintProps {
  /** The key to display (e.g., "1", "Enter", "Escape") */
  shortcut: string;
  /** Whether to show the modifier key (Cmd/Ctrl) prefix */
  showMod?: boolean;
  /** Size variant */
  size?: 'sm' | 'md';
  /** Additional CSS class */
  className?: string;
}

// =============================================================================
// Constants
// =============================================================================

/** Key display mappings for special keys */
const KEY_DISPLAY: Record<string, string> = {
  enter: '\u23CE',      // Return symbol
  escape: 'Esc',
  space: 'Space',
  arrowup: '\u2191',
  arrowdown: '\u2193',
  arrowleft: '\u2190',
  arrowright: '\u2192',
  backspace: '\u232B',
  delete: '\u2326',
  tab: '\u21E5',
};

// =============================================================================
// Component
// =============================================================================

/**
 * KeyboardHint
 *
 * Renders a subtle keyboard shortcut indicator.
 * Automatically uses platform-appropriate modifier symbols.
 */
export function KeyboardHint({
  shortcut,
  showMod = true,
  size = 'sm',
  className = '',
}: KeyboardHintProps) {
  // Get platform-aware display
  const display = useMemo(() => {
    const normalizedKey = shortcut.toLowerCase();
    const keyDisplay = KEY_DISPLAY[normalizedKey] || shortcut.toUpperCase();

    if (showMod) {
      const modSymbol = getModifierSymbol();
      const isMac = isMacOS();
      // Mac uses symbol directly, Windows uses "Ctrl+"
      return isMac ? `${modSymbol}${keyDisplay}` : `${modSymbol}+${keyDisplay}`;
    }

    return keyDisplay;
  }, [shortcut, showMod]);

  // Size-based styling
  const sizeClasses = size === 'sm'
    ? 'text-[10px] px-1 py-0.5'
    : 'text-xs px-1.5 py-0.5';

  return (
    <kbd
      className={`
        inline-flex items-center justify-center
        font-mono font-medium
        rounded
        bg-sage/10
        text-sage/60
        border border-sage/20
        select-none
        ${sizeClasses}
        ${className}
      `}
      aria-hidden="true"
    >
      {display}
    </kbd>
  );
}

export default KeyboardHint;
