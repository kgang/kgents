/**
 * EditPane — Raw markdown editing for specs
 *
 * The editing membrane: Kent types, K-Block captures, Witness observes.
 *
 * "The proof IS the decision. The mark IS the witness."
 */

import { useCallback, useEffect, useRef } from 'react';

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
}

// =============================================================================
// Component
// =============================================================================

export function EditPane({ content, onChange, onSave, onCancel, isSaving, path }: EditPaneProps) {
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Focus textarea on mount
  useEffect(() => {
    textareaRef.current?.focus();
  }, []);

  // Handle keyboard shortcuts
  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
      // Cmd/Ctrl + S to save
      if ((e.metaKey || e.ctrlKey) && e.key === 's') {
        e.preventDefault();
        onSave();
      }
      // Escape to cancel
      if (e.key === 'Escape') {
        e.preventDefault();
        onCancel();
      }
    },
    [onSave, onCancel]
  );

  const fileName = path?.split('/').pop() || 'Untitled';

  return (
    <div className="edit-pane">
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
        <textarea
          ref={textareaRef}
          className="edit-pane__editor"
          value={content}
          onChange={(e) => onChange(e.target.value)}
          onKeyDown={handleKeyDown}
          spellCheck={false}
          placeholder="Enter markdown content..."
        />
      </div>

      <footer className="edit-pane__footer">
        <span className="edit-pane__hint">
          <kbd>Cmd+S</kbd> to apply changes &middot; <kbd>Esc</kbd> to cancel
        </span>
      </footer>
    </div>
  );
}
