/**
 * CommandLine — Vim-style command input
 *
 * ":" enters command mode. Execute AGENTESE or ex commands.
 */

import React, { forwardRef, memo, useCallback, useEffect, useState } from 'react';

import './CommandLine.css';

// =============================================================================
// Types
// =============================================================================

interface CommandLineProps {
  /** Called when command is submitted */
  onSubmit: (command: string) => void;

  /** Called when command is cancelled (Escape) */
  onCancel: () => void;

  /** Placeholder text */
  placeholder?: string;
}

// =============================================================================
// Helpers
// =============================================================================

/**
 * Parse command and extract prefix for completion
 * Returns { cmdPrefix: 'e' | 'edit' | 'ag', partial: 'world.h' }
 */
function parseCommandForCompletion(value: string): {
  cmdPrefix: string;
  partial: string;
} | null {
  const trimmed = value.trim();

  // Match ":e " or ":edit " followed by partial path
  const editMatch = trimmed.match(/^(e|edit)\s+(.*)$/);
  if (editMatch) {
    return { cmdPrefix: editMatch[1], partial: editMatch[2] };
  }

  // Match ":ag " followed by partial AGENTESE path
  const agMatch = trimmed.match(/^ag\s+(.*)$/);
  if (agMatch) {
    return { cmdPrefix: 'ag', partial: agMatch[1] };
  }

  return null;
}

/**
 * Fetch completions from backend
 */
async function fetchCompletions(
  cmdPrefix: string,
  partial: string
): Promise<string[]> {
  try {
    if (cmdPrefix === 'e' || cmdPrefix === 'edit') {
      const res = await fetch(
        `/api/files/complete?prefix=${encodeURIComponent(partial)}`
      );
      return res.ok ? await res.json() : [];
    } else if (cmdPrefix === 'ag') {
      const res = await fetch(
        `/api/agentese/complete?prefix=${encodeURIComponent(partial)}`
      );
      return res.ok ? await res.json() : [];
    }
  } catch (err) {
    console.warn('Completion fetch failed:', err);
  }
  return [];
}

// =============================================================================
// Component
// =============================================================================

export const CommandLine = memo(
  forwardRef<HTMLInputElement, CommandLineProps>(function CommandLine(
    { onSubmit, onCancel, placeholder = 'Enter command...' },
    ref
  ) {
    const [value, setValue] = useState('');
    const [completions, setCompletions] = useState<string[]>([]);
    const [completionIndex, setCompletionIndex] = useState(-1);
    const [lastCompletionValue, setLastCompletionValue] = useState('');

    // Clear completions when input changes (unless we're cycling through completions)
    useEffect(() => {
      if (value !== lastCompletionValue) {
        setCompletions([]);
        setCompletionIndex(-1);
      }
    }, [value, lastCompletionValue]);

    const handleKeyDown = useCallback(
      async (e: React.KeyboardEvent<HTMLInputElement>) => {
        if (e.key === 'Enter') {
          e.preventDefault();
          if (value.trim()) {
            onSubmit(value.trim());
          }
          setValue('');
          setCompletions([]);
          setCompletionIndex(-1);
        } else if (e.key === 'Escape') {
          e.preventDefault();
          setValue('');
          setCompletions([]);
          setCompletionIndex(-1);
          onCancel();
        } else if (e.key === 'Tab') {
          e.preventDefault();

          const parsed = parseCommandForCompletion(value);
          if (!parsed) return;

          const { cmdPrefix, partial } = parsed;

          // Fetch completions if we don't have any
          if (completions.length === 0) {
            const newCompletions = await fetchCompletions(cmdPrefix, partial);
            if (newCompletions.length > 0) {
              setCompletions(newCompletions);
              setCompletionIndex(0);
              const completed = `${cmdPrefix} ${newCompletions[0]}`;
              setValue(completed);
              setLastCompletionValue(completed);
            }
          } else {
            // Cycle through existing completions
            const direction = e.shiftKey ? -1 : 1;
            const newIndex =
              (completionIndex + direction + completions.length) %
              completions.length;
            setCompletionIndex(newIndex);
            const completed = `${cmdPrefix} ${completions[newIndex]}`;
            setValue(completed);
            setLastCompletionValue(completed);
          }
        }
      },
      [value, completions, completionIndex, onSubmit, onCancel]
    );

    return (
      <div className="command-line">
        <span className="command-line__prompt">:</span>
        <input
          ref={ref}
          type="text"
          className="command-line__input"
          value={value}
          onChange={(e) => setValue(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          autoComplete="off"
          autoCorrect="off"
          autoCapitalize="off"
          spellCheck={false}
        />
        {completions.length > 0 && (
          <div className="command-line__completions">
            {completions.slice(0, 5).map((completion, idx) => (
              <div
                key={completion}
                className={`command-line__completion-item ${
                  idx === completionIndex ? 'active' : ''
                }`}
              >
                {completion}
              </div>
            ))}
            {completions.length > 5 && (
              <div className="command-line__completion-item muted">
                ... {completions.length - 5} more
              </div>
            )}
          </div>
        )}
      </div>
    );
  })
);
