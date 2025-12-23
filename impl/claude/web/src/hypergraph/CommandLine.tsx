/**
 * CommandLine — Vim-style command input
 *
 * ":" enters command mode. Execute AGENTESE or ex commands.
 */

import React, { forwardRef, memo, useCallback, useState } from 'react';

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
// Component
// =============================================================================

export const CommandLine = memo(
  forwardRef<HTMLInputElement, CommandLineProps>(function CommandLine(
    { onSubmit, onCancel, placeholder = 'Enter command...' },
    ref
  ) {
    const [value, setValue] = useState('');

    const handleKeyDown = useCallback(
      (e: React.KeyboardEvent<HTMLInputElement>) => {
        if (e.key === 'Enter') {
          e.preventDefault();
          if (value.trim()) {
            onSubmit(value.trim());
          }
          setValue('');
        } else if (e.key === 'Escape') {
          e.preventDefault();
          setValue('');
          onCancel();
        }
      },
      [value, onSubmit, onCancel]
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
      </div>
    );
  })
);
