/**
 * Ghost Text CodeMirror Extension
 *
 * Inline AI completions that appear as ghost text while typing.
 * The AI isn't a separate entity you talk to. The AI is in your fingers.
 *
 * Features:
 * - Debounced triggering (200ms after typing pause)
 * - Tab to accept, Esc to dismiss
 * - 40% opacity ghost text (suggests, never demands)
 * - Only active in editable mode
 *
 * Architecture:
 * - StateField tracks current ghost text and position
 * - StateEffect for setting/accepting/dismissing ghost text
 * - ViewPlugin handles debounced completion fetching
 * - DecorationSet renders ghost text as inline widgets
 */

import {
  Extension,
  StateField,
  StateEffect,
  EditorState,
} from '@codemirror/state';
import {
  EditorView,
  Decoration,
  WidgetType,
  ViewPlugin,
  ViewUpdate,
  PluginValue,
} from '@codemirror/view';
import { keymap } from '@codemirror/view';
import { GhostTextCompletion } from './useGhostTextSources';

// --- Ghost Text Widget ---

/**
 * Widget that renders ghost text inline
 */
class GhostTextWidget extends WidgetType {
  constructor(readonly text: string, readonly accepting: boolean = false) {
    super();
  }

  toDOM(): HTMLElement {
    const span = document.createElement('span');
    span.className = this.accepting ? 'ghost-text ghost-text--accepting' : 'ghost-text';
    span.textContent = this.text;
    return span;
  }

  eq(other: GhostTextWidget): boolean {
    return this.text === other.text && this.accepting === other.accepting;
  }

  ignoreEvent(): boolean {
    return true;
  }
}

// --- State Effects ---

/** Set ghost text at a position (or null to clear) */
const setGhostText = StateEffect.define<{ text: string; pos: number } | null>();

/** Mark ghost text as accepting (triggers flash animation) */
const acceptingGhostText = StateEffect.define<void>();

/** Clear ghost text */
const clearGhostText = StateEffect.define<void>();

// --- State Field ---

interface GhostTextState {
  /** Current ghost text */
  text: string | null;
  /** Position where ghost text should appear */
  pos: number;
  /** Whether ghost text is being accepted (for animation) */
  accepting: boolean;
}

const ghostTextField = StateField.define<GhostTextState>({
  create(): GhostTextState {
    return { text: null, pos: 0, accepting: false };
  },

  update(value, tr): GhostTextState {
    // Process effects
    for (const effect of tr.effects) {
      if (effect.is(setGhostText)) {
        if (effect.value === null) {
          return { text: null, pos: 0, accepting: false };
        }
        return {
          text: effect.value.text,
          pos: effect.value.pos,
          accepting: false,
        };
      }

      if (effect.is(acceptingGhostText)) {
        return { ...value, accepting: true };
      }

      if (effect.is(clearGhostText)) {
        return { text: null, pos: 0, accepting: false };
      }
    }

    // Clear ghost text if:
    // - Document changed (user typed/deleted)
    // - Selection changed (cursor moved)
    if (value.text !== null && (tr.docChanged || tr.selection)) {
      // Exception: if cursor is still at ghost text position, keep it
      const cursorPos = tr.state.selection.main.head;
      if (cursorPos !== value.pos) {
        return { text: null, pos: 0, accepting: false };
      }
    }

    return value;
  },

  provide(field): Extension {
    return EditorView.decorations.from(field, state => {
      if (state.text === null) {
        return Decoration.none;
      }

      const widget = Decoration.widget({
        widget: new GhostTextWidget(state.text, state.accepting),
        side: 1, // Appear after cursor
      });

      return Decoration.set([widget.range(state.pos)]);
    });
  },
});

// --- Keybindings ---

const ghostTextKeymap = keymap.of([
  {
    key: 'Tab',
    run: (view: EditorView): boolean => {
      const ghost = view.state.field(ghostTextField);
      if (!ghost.text) return false;

      // Mark as accepting (triggers flash animation)
      view.dispatch({
        effects: acceptingGhostText.of(),
      });

      // Insert the ghost text after a brief delay (for animation)
      setTimeout(() => {
        view.dispatch({
          changes: { from: ghost.pos, insert: ghost.text! },
          effects: clearGhostText.of(),
          selection: { anchor: ghost.pos + ghost.text!.length },
        });
      }, 50);

      return true;
    },
  },
  {
    key: 'Escape',
    run: (view: EditorView): boolean => {
      const ghost = view.state.field(ghostTextField);
      if (!ghost.text) return false;

      view.dispatch({ effects: clearGhostText.of() });
      return true;
    },
  },
]);

// --- Completion Fetcher ---

const DEBOUNCE_MS = 200;

interface CompletionFetcher {
  (prefix: string): Promise<GhostTextCompletion | null>;
}

/**
 * View plugin that fetches completions after typing pauses
 */
class GhostTextPluginValue implements PluginValue {
  private debounceTimer: ReturnType<typeof setTimeout> | null = null;

  constructor(private view: EditorView, private fetcher: CompletionFetcher) {}

  update(update: ViewUpdate): void {
    // Only trigger on document changes in editable mode
    if (!update.docChanged || update.state.readOnly) {
      return;
    }

    // Clear existing timer
    if (this.debounceTimer) {
      clearTimeout(this.debounceTimer);
      this.debounceTimer = null;
    }

    // Clear ghost text immediately on typing
    const ghost = update.state.field(ghostTextField);
    if (ghost.text) {
      this.view.dispatch({ effects: clearGhostText.of() });
    }

    // Set new debounce timer
    this.debounceTimer = setTimeout(() => {
      this.fetchCompletion(update.state);
    }, DEBOUNCE_MS);
  }

  destroy(): void {
    if (this.debounceTimer) {
      clearTimeout(this.debounceTimer);
    }
  }

  private async fetchCompletion(state: EditorState): Promise<void> {
    // Get text before cursor
    const cursorPos = state.selection.main.head;
    const line = state.doc.lineAt(cursorPos);
    const lineText = line.text;
    const cursorInLine = cursorPos - line.from;

    // Extract word/path before cursor
    const beforeCursor = lineText.slice(0, cursorInLine);
    const match = beforeCursor.match(/[\w.]+$/);

    if (!match) {
      return;
    }

    const prefix = match[0];

    // Minimum prefix length to trigger
    if (prefix.length < 2) {
      return;
    }

    // Fetch completion
    try {
      const completion = await this.fetcher(prefix);

      if (!completion || !completion.text) {
        return;
      }

      // Verify cursor hasn't moved
      if (this.view.state.selection.main.head !== cursorPos) {
        return;
      }

      // Set ghost text
      this.view.dispatch({
        effects: setGhostText.of({
          text: completion.text,
          pos: cursorPos,
        }),
      });
    } catch (error) {
      console.warn('Ghost text completion failed:', error);
    }
  }
}

function createGhostTextPlugin(fetcher: CompletionFetcher): Extension {
  return ViewPlugin.define(
    (view) => new GhostTextPluginValue(view, fetcher)
  );
}

// --- Public API ---

export interface GhostTextExtensionOptions {
  /** Function to fetch completions */
  fetcher: CompletionFetcher;
  /** Only enable in certain modes (default: always enabled if editable) */
  enableWhen?: (state: EditorState) => boolean;
}

/**
 * Create ghost text extension
 *
 * Usage:
 * ```ts
 * const extension = ghostTextExtension({
 *   fetcher: async (prefix) => {
 *     const completion = await getCompletion(prefix);
 *     return completion;
 *   }
 * });
 * ```
 */
export function ghostTextExtension(options: GhostTextExtensionOptions): Extension {
  const { fetcher } = options;

  return [
    ghostTextField,
    ghostTextKeymap,
    createGhostTextPlugin(fetcher),
  ];
}

// --- Utilities ---

/**
 * Get current ghost text state (for testing/debugging)
 */
export function getGhostTextState(state: EditorState): GhostTextState | null {
  try {
    return state.field(ghostTextField);
  } catch {
    return null;
  }
}

/**
 * Manually trigger ghost text (for testing)
 */
export function triggerGhostText(
  view: EditorView,
  text: string,
  pos?: number
): void {
  const cursorPos = pos ?? view.state.selection.main.head;
  view.dispatch({
    effects: setGhostText.of({ text, pos: cursorPos }),
  });
}

/**
 * Manually clear ghost text (for testing)
 */
export function clearGhostTextManual(view: EditorView): void {
  view.dispatch({
    effects: clearGhostText.of(),
  });
}
