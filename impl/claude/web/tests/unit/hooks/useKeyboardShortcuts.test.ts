/**
 * Tests for useKeyboardShortcuts hook.
 *
 * Manages keyboard shortcut registration and handling:
 * - Shortcut registration/unregistration
 * - Context-based activation
 * - Modifier key support
 * - Default shortcut creation
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import {
  useKeyboardShortcuts,
  createDefaultShortcuts,
  type ShortcutDefinition,
} from '@/hooks/useKeyboardShortcuts';

// =============================================================================
// Test Setup
// =============================================================================

describe('useKeyboardShortcuts', () => {
  let addEventListenerSpy: ReturnType<typeof vi.spyOn>;
  let removeEventListenerSpy: ReturnType<typeof vi.spyOn>;

  beforeEach(() => {
    addEventListenerSpy = vi.spyOn(document, 'addEventListener');
    removeEventListenerSpy = vi.spyOn(document, 'removeEventListener');
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  // ===========================================================================
  // Initialization Tests
  // ===========================================================================

  describe('initialization', () => {
    it('adds keydown event listener', () => {
      renderHook(() => useKeyboardShortcuts());

      expect(addEventListenerSpy).toHaveBeenCalledWith(
        'keydown',
        expect.any(Function)
      );
    });

    it('removes event listener on unmount', () => {
      const { unmount } = renderHook(() => useKeyboardShortcuts());

      unmount();

      expect(removeEventListenerSpy).toHaveBeenCalledWith(
        'keydown',
        expect.any(Function)
      );
    });

    it('does not add listener when enabled=false', () => {
      renderHook(() => useKeyboardShortcuts({ enabled: false }));

      expect(addEventListenerSpy).not.toHaveBeenCalled();
    });

    it('starts with empty shortcuts', () => {
      const { result } = renderHook(() => useKeyboardShortcuts());

      expect(result.current.getAllShortcuts()).toEqual([]);
    });
  });

  // ===========================================================================
  // Registration Tests
  // ===========================================================================

  describe('registration', () => {
    it('register adds a shortcut', () => {
      const { result } = renderHook(() => useKeyboardShortcuts());

      const shortcut: ShortcutDefinition = {
        key: 'a',
        contexts: ['global'],
        description: 'Test shortcut',
        handler: vi.fn(),
      };

      act(() => {
        result.current.register(shortcut);
      });

      expect(result.current.getAllShortcuts()).toHaveLength(1);
      expect(result.current.getAllShortcuts()[0]).toEqual(shortcut);
    });

    it('register returns unregister function', () => {
      const { result } = renderHook(() => useKeyboardShortcuts());

      const shortcut: ShortcutDefinition = {
        key: 'a',
        contexts: ['global'],
        description: 'Test shortcut',
        handler: vi.fn(),
      };

      let unregister: () => void;
      act(() => {
        unregister = result.current.register(shortcut);
      });

      expect(result.current.getAllShortcuts()).toHaveLength(1);

      act(() => {
        unregister();
      });

      expect(result.current.getAllShortcuts()).toHaveLength(0);
    });

    it('unregister removes shortcut by key', () => {
      const { result } = renderHook(() => useKeyboardShortcuts());

      const shortcut: ShortcutDefinition = {
        key: 'b',
        contexts: ['global'],
        description: 'Test shortcut',
        handler: vi.fn(),
      };

      act(() => {
        result.current.register(shortcut);
      });

      expect(result.current.getAllShortcuts()).toHaveLength(1);

      act(() => {
        result.current.unregister('b');
      });

      expect(result.current.getAllShortcuts()).toHaveLength(0);
    });

    it('unregister handles modifiers in key lookup', () => {
      const { result } = renderHook(() => useKeyboardShortcuts());

      const shortcut: ShortcutDefinition = {
        key: 's',
        modifiers: { ctrl: true },
        contexts: ['global'],
        description: 'Save',
        handler: vi.fn(),
      };

      act(() => {
        result.current.register(shortcut);
      });

      act(() => {
        result.current.unregister('s', { ctrl: true });
      });

      expect(result.current.getAllShortcuts()).toHaveLength(0);
    });
  });

  // ===========================================================================
  // Context Filtering Tests
  // ===========================================================================

  describe('context filtering', () => {
    it('getActiveShortcuts returns only shortcuts for current context', () => {
      const { result } = renderHook(() =>
        useKeyboardShortcuts({ context: 'build' })
      );

      act(() => {
        result.current.register({
          key: 'a',
          contexts: ['global'],
          description: 'Global only',
          handler: vi.fn(),
        });
        result.current.register({
          key: 'b',
          contexts: ['build'],
          description: 'Build only',
          handler: vi.fn(),
        });
        result.current.register({
          key: 'c',
          contexts: ['global', 'build'],
          description: 'Both',
          handler: vi.fn(),
        });
      });

      const active = result.current.getActiveShortcuts();

      expect(active).toHaveLength(2);
      expect(active.map((s) => s.key)).toContain('b');
      expect(active.map((s) => s.key)).toContain('c');
      expect(active.map((s) => s.key)).not.toContain('a');
    });

    it('getAllShortcuts returns all shortcuts regardless of context', () => {
      const { result } = renderHook(() =>
        useKeyboardShortcuts({ context: 'build' })
      );

      act(() => {
        result.current.register({
          key: 'a',
          contexts: ['global'],
          description: 'Global only',
          handler: vi.fn(),
        });
        result.current.register({
          key: 'b',
          contexts: ['build'],
          description: 'Build only',
          handler: vi.fn(),
        });
      });

      expect(result.current.getAllShortcuts()).toHaveLength(2);
    });
  });

  // ===========================================================================
  // Event Handling Tests
  // ===========================================================================

  describe('event handling', () => {
    it('calls handler when matching key is pressed', () => {
      const handler = vi.fn();
      const { result } = renderHook(() => useKeyboardShortcuts());

      act(() => {
        result.current.register({
          key: 'a',
          contexts: ['global'],
          description: 'Test',
          handler,
        });
      });

      // Simulate keydown
      act(() => {
        document.dispatchEvent(
          new KeyboardEvent('keydown', {
            key: 'a',
            bubbles: true,
          })
        );
      });

      expect(handler).toHaveBeenCalledTimes(1);
    });

    it('respects modifier keys', () => {
      const handler = vi.fn();
      const { result } = renderHook(() => useKeyboardShortcuts());

      act(() => {
        result.current.register({
          key: 's',
          modifiers: { ctrl: true },
          contexts: ['global'],
          description: 'Save',
          handler,
        });
      });

      // Press s without ctrl - should not trigger
      act(() => {
        document.dispatchEvent(
          new KeyboardEvent('keydown', {
            key: 's',
            ctrlKey: false,
            bubbles: true,
          })
        );
      });

      expect(handler).not.toHaveBeenCalled();

      // Press s with ctrl - should trigger
      act(() => {
        document.dispatchEvent(
          new KeyboardEvent('keydown', {
            key: 's',
            ctrlKey: true,
            bubbles: true,
          })
        );
      });

      expect(handler).toHaveBeenCalledTimes(1);
    });

    it('ignores events from input elements', () => {
      const handler = vi.fn();
      const { result } = renderHook(() => useKeyboardShortcuts());

      act(() => {
        result.current.register({
          key: 'a',
          contexts: ['global'],
          description: 'Test',
          handler,
        });
      });

      // Create an input element as target
      const input = document.createElement('input');
      document.body.appendChild(input);

      // Simulate keydown on input
      act(() => {
        const event = new KeyboardEvent('keydown', {
          key: 'a',
          bubbles: true,
        });
        Object.defineProperty(event, 'target', {
          value: input,
          writable: false,
        });
        document.dispatchEvent(event);
      });

      expect(handler).not.toHaveBeenCalled();

      // Cleanup
      document.body.removeChild(input);
    });

    it('ignores events from textarea elements', () => {
      const handler = vi.fn();
      const { result } = renderHook(() => useKeyboardShortcuts());

      act(() => {
        result.current.register({
          key: 'a',
          contexts: ['global'],
          description: 'Test',
          handler,
        });
      });

      const textarea = document.createElement('textarea');
      document.body.appendChild(textarea);

      act(() => {
        const event = new KeyboardEvent('keydown', {
          key: 'a',
          bubbles: true,
        });
        Object.defineProperty(event, 'target', {
          value: textarea,
          writable: false,
        });
        document.dispatchEvent(event);
      });

      expect(handler).not.toHaveBeenCalled();

      document.body.removeChild(textarea);
    });

    it('prevents default when preventDefault=true', () => {
      const handler = vi.fn();
      const { result } = renderHook(() => useKeyboardShortcuts());

      act(() => {
        result.current.register({
          key: ' ',
          contexts: ['global'],
          description: 'Space',
          handler,
          preventDefault: true,
        });
      });

      const preventDefaultSpy = vi.fn();

      act(() => {
        const event = new KeyboardEvent('keydown', {
          key: ' ',
          bubbles: true,
        });
        event.preventDefault = preventDefaultSpy;
        document.dispatchEvent(event);
      });

      expect(preventDefaultSpy).toHaveBeenCalled();
    });

    it('only triggers handler when context matches', () => {
      const handler = vi.fn();
      const { result } = renderHook(() =>
        useKeyboardShortcuts({ context: 'build' })
      );

      act(() => {
        result.current.register({
          key: 'a',
          contexts: ['historical'],
          description: 'Historical only',
          handler,
        });
      });

      act(() => {
        document.dispatchEvent(
          new KeyboardEvent('keydown', {
            key: 'a',
            bubbles: true,
          })
        );
      });

      expect(handler).not.toHaveBeenCalled();
    });
  });

  // ===========================================================================
  // createDefaultShortcuts Tests
  // ===========================================================================

  describe('createDefaultShortcuts', () => {
    it('creates space shortcut for play/pause', () => {
      const onTogglePlay = vi.fn();
      const shortcuts = createDefaultShortcuts({ onTogglePlay });

      const spaceShortcut = shortcuts.find((s) => s.key === ' ');
      expect(spaceShortcut).toBeDefined();
      expect(spaceShortcut?.contexts).toContain('global');
      expect(spaceShortcut?.preventDefault).toBe(true);
    });

    it('creates b shortcut for build mode', () => {
      const onToggleBuildMode = vi.fn();
      const shortcuts = createDefaultShortcuts({ onToggleBuildMode });

      const bShortcut = shortcuts.find((s) => s.key === 'b');
      expect(bShortcut).toBeDefined();
      expect(bShortcut?.contexts).toContain('global');
    });

    it('creates undo shortcuts with ctrl and meta', () => {
      const onUndo = vi.fn();
      const shortcuts = createDefaultShortcuts({ onUndo });

      const undoShortcuts = shortcuts.filter(
        (s) => s.key === 'z' && s.description === 'Undo'
      );
      expect(undoShortcuts).toHaveLength(2);
      expect(undoShortcuts[0].modifiers?.ctrl).toBe(true);
      expect(undoShortcuts[1].modifiers?.meta).toBe(true);
    });

    it('creates redo shortcuts with shift modifier', () => {
      const onRedo = vi.fn();
      const shortcuts = createDefaultShortcuts({ onRedo });

      const redoShortcuts = shortcuts.filter(
        (s) => s.key === 'z' && s.description === 'Redo'
      );
      expect(redoShortcuts).toHaveLength(2);
      expect(redoShortcuts[0].modifiers?.shift).toBe(true);
      expect(redoShortcuts[1].modifiers?.shift).toBe(true);
    });

    it('creates delete shortcuts for both Delete and Backspace', () => {
      const onDelete = vi.fn();
      const shortcuts = createDefaultShortcuts({ onDelete });

      const deleteShortcuts = shortcuts.filter(
        (s) => s.key === 'Delete' || s.key === 'Backspace'
      );
      expect(deleteShortcuts).toHaveLength(2);
    });

    it('creates number shortcuts for agent selection', () => {
      const onSelectAgent = vi.fn();
      const shortcuts = createDefaultShortcuts({ onSelectAgent });

      const numberShortcuts = shortcuts.filter(
        (s) => s.key >= '1' && s.key <= '9'
      );
      expect(numberShortcuts).toHaveLength(9);
    });

    it('creates arrow shortcuts for historical mode', () => {
      const onStepForward = vi.fn();
      const onStepBackward = vi.fn();
      const shortcuts = createDefaultShortcuts({ onStepForward, onStepBackward });

      const arrowRight = shortcuts.find((s) => s.key === 'ArrowRight');
      const arrowLeft = shortcuts.find((s) => s.key === 'ArrowLeft');

      expect(arrowRight).toBeDefined();
      expect(arrowRight?.contexts).toContain('historical');
      expect(arrowLeft).toBeDefined();
      expect(arrowLeft?.contexts).toContain('historical');
    });

    it('creates Escape shortcut available in all contexts', () => {
      const onEscape = vi.fn();
      const shortcuts = createDefaultShortcuts({ onEscape });

      const escapeShortcut = shortcuts.find((s) => s.key === 'Escape');
      expect(escapeShortcut).toBeDefined();
      expect(escapeShortcut?.contexts).toContain('global');
      expect(escapeShortcut?.contexts).toContain('build');
      expect(escapeShortcut?.contexts).toContain('historical');
      expect(escapeShortcut?.contexts).toContain('inhabit');
    });

    it('creates help shortcut for ?', () => {
      const onShowHelp = vi.fn();
      const shortcuts = createDefaultShortcuts({ onShowHelp });

      const helpShortcut = shortcuts.find((s) => s.key === '?');
      expect(helpShortcut).toBeDefined();
    });

    it('only creates shortcuts for provided handlers', () => {
      const shortcuts = createDefaultShortcuts({});

      expect(shortcuts).toHaveLength(0);
    });
  });
});
