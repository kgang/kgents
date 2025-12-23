/**
 * EditPane — Raw markdown editing for specs
 *
 * The editing membrane: Kent types, K-Block captures, Witness observes.
 * Uses CodeMirror 6 with STARK BIOME theming.
 *
 * "The proof IS the decision. The mark IS the witness."
 */

import { useCallback, useEffect, useRef } from 'react';
import { MarkdownEditor, MarkdownEditorRef } from '../../components/editor';

import './EditPane.css';

// =============================================================================
// Types
// =============================================================================

interface EditPaneProps {
  content: string;
  onChange: (content: string) => void;
  onSave: () => void;
  onCancel: () => void;
  isSaving?: boolean;
  path?: string;
  /** Enable vim mode in editor */
  vimMode?: boolean;
}

// =============================================================================
// Component
// =============================================================================

export function EditPane({
  content,
  onChange,
  onSave,
  onCancel,
  isSaving,
  path,
  vimMode = false,
}: EditPaneProps) {
  const editorRef = useRef<MarkdownEditorRef>(null);

  // Focus editor on mount
  useEffect(() => {
    editorRef.current?.focus();
  }, []);

  // Handle keyboard shortcuts at the container level
  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent<HTMLDivElement>) => {
      // Cmd/Ctrl + S to save
      if ((e.metaKey || e.ctrlKey) && e.key === 's') {
        e.preventDefault();
        onSave();
      }
      // Escape to cancel (only if not in vim mode - vim handles Escape)
      if (e.key === 'Escape' && !vimMode) {
        e.preventDefault();
        onCancel();
      }
    },
    [onSave, onCancel, vimMode]
  );

  const fileName = path?.split('/').pop() || 'Untitled';

  return (
    <div className="edit-pane" onKeyDown={handleKeyDown}>
      <header className="edit-pane__header">
        <h3 className="edit-pane__title">Editing: {fileName}</h3>
        <div className="edit-pane__actions">
          <button
            className="edit-pane__btn edit-pane__btn--cancel"
            onClick={onCancel}
            disabled={isSaving}
            title="Cancel (Escape)"
          >
            Cancel
          </button>
          <button
            className="edit-pane__btn edit-pane__btn--save"
            onClick={onSave}
            disabled={isSaving}
            title="Apply changes (Cmd+S)"
          >
            {isSaving ? 'Applying...' : 'Apply'}
          </button>
        </div>
      </header>

      <div className="edit-pane__editor-wrapper">
        <MarkdownEditor
          ref={editorRef}
          value={content}
          onChange={onChange}
          vimMode={vimMode}
          placeholder="Enter markdown content..."
          fillHeight
          autoFocus
        />
      </div>

      <footer className="edit-pane__footer">
        <span className="edit-pane__hint">
          <kbd>Cmd+S</kbd> to apply changes{' '}
          {vimMode ? (
            <>
              &middot; <kbd>:wq</kbd> to save and close
            </>
          ) : (
            <>
              &middot; <kbd>Esc</kbd> to cancel
            </>
          )}
        </span>
      </footer>
    </div>
  );
}
