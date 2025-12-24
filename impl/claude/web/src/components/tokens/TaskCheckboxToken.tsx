/**
 * TaskCheckboxToken — Toggleable task checkbox.
 *
 * Renders markdown task checkboxes as interactive elements:
 * - [ ] Unchecked task
 * - [x] Checked task
 *
 * Toggle calls self.document.task.toggle via AGENTESE.
 *
 * "The proof IS the decision. The mark IS the witness."
 */

import { memo, useCallback, useState } from 'react';

import './tokens.css';

interface TaskCheckboxTokenProps {
  checked: boolean;
  description: string;
  taskId?: string;
  onToggle?: (newState: boolean, taskId?: string) => void;
  className?: string;
}

export const TaskCheckboxToken = memo(function TaskCheckboxToken({
  checked: initialChecked,
  description,
  taskId,
  onToggle,
  className,
}: TaskCheckboxTokenProps) {
  // Optimistic local state for immediate feedback
  const [isChecked, setIsChecked] = useState(initialChecked);
  const [isToggling, setIsToggling] = useState(false);

  const handleToggle = useCallback(async () => {
    if (isToggling) return;

    const newState = !isChecked;

    // Optimistic update
    setIsChecked(newState);
    setIsToggling(true);

    try {
      await onToggle?.(newState, taskId);
    } catch {
      // Revert on error
      setIsChecked(!newState);
    } finally {
      setIsToggling(false);
    }
  }, [isChecked, isToggling, onToggle, taskId]);

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        handleToggle();
      }
    },
    [handleToggle]
  );

  return (
    <label
      className={`task-checkbox-token ${isChecked ? 'task-checkbox-token--checked' : ''} ${isToggling ? 'task-checkbox-token--toggling' : ''} ${className ?? ''}`}
    >
      <input
        type="checkbox"
        checked={isChecked}
        onChange={handleToggle}
        onKeyDown={handleKeyDown}
        disabled={isToggling}
        className="task-checkbox-token__input"
        aria-label={description}
      />
      <span className="task-checkbox-token__box" aria-hidden="true">
        {isChecked ? '\u2713' : ''}
      </span>
      <span className="task-checkbox-token__description">{description}</span>
    </label>
  );
});
