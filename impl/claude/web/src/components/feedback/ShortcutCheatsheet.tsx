/**
 * Keyboard Shortcut Cheatsheet
 *
 * Modal showing all available shortcuts, triggered by '?' key.
 * Organized by context/category for easy discovery.
 *
 * @see plans/web-refactor/phase5-continuation.md
 */

import { useState, useEffect, useCallback } from 'react';
import { createPortal } from 'react-dom';

// =============================================================================
// Types
// =============================================================================

interface ShortcutItem {
  key: string;
  description: string;
}

interface ShortcutCategory {
  name: string;
  items: ShortcutItem[];
}

interface ShortcutCheatsheetProps {
  /** Whether the cheatsheet is visible */
  isOpen: boolean;
  /** Callback to close the cheatsheet */
  onClose: () => void;
  /** Additional shortcuts to show (context-specific) */
  additionalShortcuts?: ShortcutCategory[];
}

// =============================================================================
// Default Shortcuts
// =============================================================================

const DEFAULT_SHORTCUTS: ShortcutCategory[] = [
  {
    name: 'Navigation',
    items: [
      { key: 'g t', description: 'Go to Town' },
      { key: 'g w', description: 'Go to Workshop' },
      { key: 'g d', description: 'Go to Dashboard' },
      { key: 'Esc', description: 'Close modal / exit mode' },
    ],
  },
  {
    name: 'Town',
    items: [
      { key: 'Space', description: 'Play/Pause simulation' },
      { key: '1-4', description: 'Set speed (0.5x-4x)' },
      { key: 'n', description: 'Toggle N-Phase view' },
      { key: 'h', description: 'Toggle historical mode' },
    ],
  },
  {
    name: 'Workshop',
    items: [
      { key: 'Enter', description: 'Submit task' },
      { key: 'r', description: 'Reset workshop' },
    ],
  },
  {
    name: 'Build Mode',
    items: [
      { key: 'b', description: 'Toggle build mode' },
      { key: '\u2318/Ctrl + Z', description: 'Undo' },
      { key: '\u2318/Ctrl + Shift + Z', description: 'Redo' },
      { key: '\u2318/Ctrl + S', description: 'Save pipeline' },
      { key: 'Delete', description: 'Delete selected' },
    ],
  },
  {
    name: 'Historical Mode',
    items: [
      { key: '\u2190', description: 'Step backward' },
      { key: '\u2192', description: 'Step forward' },
    ],
  },
  {
    name: 'General',
    items: [
      { key: '?', description: 'Show this cheatsheet' },
      { key: '\u2318/Ctrl + K', description: 'Command palette (coming soon)' },
    ],
  },
];

// =============================================================================
// Components
// =============================================================================

/**
 * Keyboard shortcut indicator.
 */
function KeyBadge({ children }: { children: string }) {
  // Split by + for modifier combinations
  const parts = children.split(' ');

  return (
    <span className="inline-flex items-center gap-1">
      {parts.map((part, i) => (
        <kbd
          key={i}
          className="min-w-[1.5rem] px-1.5 py-0.5 bg-town-bg text-gray-300 text-xs font-mono rounded border border-town-accent text-center"
        >
          {part}
        </kbd>
      ))}
    </span>
  );
}

/**
 * Shortcut category section.
 */
function CategorySection({ category }: { category: ShortcutCategory }) {
  return (
    <div>
      <h3 className="text-xs font-semibold text-town-highlight uppercase tracking-wider mb-2">
        {category.name}
      </h3>
      <ul className="space-y-2">
        {category.items.map((item) => (
          <li
            key={item.key}
            className="flex items-center justify-between text-sm"
          >
            <span className="text-gray-300">{item.description}</span>
            <KeyBadge>{item.key}</KeyBadge>
          </li>
        ))}
      </ul>
    </div>
  );
}

/**
 * Keyboard shortcut cheatsheet modal.
 *
 * @example
 * ```tsx
 * const [showShortcuts, setShowShortcuts] = useState(false);
 *
 * <ShortcutCheatsheet
 *   isOpen={showShortcuts}
 *   onClose={() => setShowShortcuts(false)}
 * />
 * ```
 */
export function ShortcutCheatsheet({
  isOpen,
  onClose,
  additionalShortcuts = [],
}: ShortcutCheatsheetProps) {
  // Close on Escape
  const handleKeyDown = useCallback(
    (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose();
      }
    },
    [onClose]
  );

  useEffect(() => {
    if (!isOpen) return;

    document.addEventListener('keydown', handleKeyDown);
    // Prevent body scroll while modal is open
    document.body.style.overflow = 'hidden';

    return () => {
      document.removeEventListener('keydown', handleKeyDown);
      document.body.style.overflow = '';
    };
  }, [isOpen, handleKeyDown]);

  if (!isOpen) return null;

  const allShortcuts = [...DEFAULT_SHORTCUTS, ...additionalShortcuts];

  return createPortal(
    <div
      className="fixed inset-0 z-50 flex items-center justify-center"
      role="dialog"
      aria-modal="true"
      aria-labelledby="shortcuts-title"
    >
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/60 backdrop-blur-sm backdrop-appear"
        onClick={onClose}
        aria-hidden="true"
      />

      {/* Modal */}
      <div className="relative bg-town-surface rounded-xl shadow-2xl max-w-2xl w-full mx-4 max-h-[80vh] overflow-hidden modal-appear">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-town-accent">
          <h2 id="shortcuts-title" className="text-lg font-semibold text-white">
            Keyboard Shortcuts
          </h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-white transition-colors p-1"
            aria-label="Close"
          >
            <svg
              width="20"
              height="20"
              viewBox="0 0 20 20"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
            >
              <path d="M4 4L16 16M4 16L16 4" />
            </svg>
          </button>
        </div>

        {/* Content */}
        <div className="px-6 py-4 overflow-y-auto max-h-[calc(80vh-80px)]">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {allShortcuts.map((category) => (
              <CategorySection key={category.name} category={category} />
            ))}
          </div>
        </div>

        {/* Footer */}
        <div className="px-6 py-3 border-t border-town-accent bg-town-bg/50 text-center">
          <p className="text-xs text-gray-500">
            Press <KeyBadge>Esc</KeyBadge> to close
          </p>
        </div>
      </div>
    </div>,
    document.body
  );
}

// =============================================================================
// Hook for triggering cheatsheet
// =============================================================================

/**
 * Hook to handle '?' key to open shortcut cheatsheet.
 */
export function useShortcutCheatsheet() {
  const [isOpen, setIsOpen] = useState(false);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Ignore if in input
      const target = e.target as HTMLElement;
      if (
        target.tagName === 'INPUT' ||
        target.tagName === 'TEXTAREA' ||
        target.isContentEditable
      ) {
        return;
      }

      if (e.key === '?') {
        e.preventDefault();
        setIsOpen((prev) => !prev);
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, []);

  return {
    isOpen,
    open: () => setIsOpen(true),
    close: () => setIsOpen(false),
    toggle: () => setIsOpen((prev) => !prev),
  };
}

export default ShortcutCheatsheet;
