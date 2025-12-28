/**
 * WASM Survivors - Input Hook
 *
 * Handles WASD keyboard input with < 1ms latency.
 * Uses event-driven approach (no polling) for responsiveness.
 *
 * @see DD-5: Fun Floor - Input < 16ms
 * @see DD-10: Dash - Space key triggers dash
 */

import { useRef, useEffect, useCallback } from 'react';
import type { InputState } from '@kgents/shared-primitives';

// =============================================================================
// Types
// =============================================================================

// Extended input state with dash support
export interface ExtendedInputState extends InputState {
  dashPressed: boolean;
  dashConsumed: boolean; // True after dash triggered, false on space release
}

export interface UseInputOptions {
  /** Enable arrow keys as alternative to WASD */
  enableArrows?: boolean;
  /** Callback when input changes (optional) */
  onInputChange?: (input: InputState) => void;
}

// =============================================================================
// Hook
// =============================================================================

export function useInput(options: UseInputOptions = {}): React.RefObject<ExtendedInputState> {
  const { enableArrows = true, onInputChange } = options;

  // Using a ref to avoid re-renders on every keypress
  // This keeps input handling at < 1ms
  const inputRef = useRef<ExtendedInputState>({
    up: false,
    down: false,
    left: false,
    right: false,
    dashPressed: false,
    dashConsumed: false,
  });

  // Handle key down
  const handleKeyDown = useCallback(
    (event: KeyboardEvent) => {
      // Prevent default for game keys to avoid scrolling
      const key = event.key.toLowerCase();
      let changed = false;

      switch (key) {
        case 'w':
          if (!inputRef.current.up) {
            inputRef.current.up = true;
            changed = true;
          }
          event.preventDefault();
          break;
        case 's':
          if (!inputRef.current.down) {
            inputRef.current.down = true;
            changed = true;
          }
          event.preventDefault();
          break;
        case 'a':
          if (!inputRef.current.left) {
            inputRef.current.left = true;
            changed = true;
          }
          event.preventDefault();
          break;
        case 'd':
          if (!inputRef.current.right) {
            inputRef.current.right = true;
            changed = true;
          }
          event.preventDefault();
          break;
        case ' ':
          // DD-10: Dash - space key triggers dash (only if not already consumed)
          if (!inputRef.current.dashPressed && !inputRef.current.dashConsumed) {
            inputRef.current.dashPressed = true;
            changed = true;
          }
          event.preventDefault();
          break;
      }

      // Arrow key support
      if (enableArrows) {
        switch (event.key) {
          case 'ArrowUp':
            if (!inputRef.current.up) {
              inputRef.current.up = true;
              changed = true;
            }
            event.preventDefault();
            break;
          case 'ArrowDown':
            if (!inputRef.current.down) {
              inputRef.current.down = true;
              changed = true;
            }
            event.preventDefault();
            break;
          case 'ArrowLeft':
            if (!inputRef.current.left) {
              inputRef.current.left = true;
              changed = true;
            }
            event.preventDefault();
            break;
          case 'ArrowRight':
            if (!inputRef.current.right) {
              inputRef.current.right = true;
              changed = true;
            }
            event.preventDefault();
            break;
        }
      }

      if (changed && onInputChange) {
        onInputChange({ ...inputRef.current });
      }
    },
    [enableArrows, onInputChange]
  );

  // Handle key up
  const handleKeyUp = useCallback(
    (event: KeyboardEvent) => {
      const key = event.key.toLowerCase();
      let changed = false;

      switch (key) {
        case 'w':
          if (inputRef.current.up) {
            inputRef.current.up = false;
            changed = true;
          }
          break;
        case 's':
          if (inputRef.current.down) {
            inputRef.current.down = false;
            changed = true;
          }
          break;
        case 'a':
          if (inputRef.current.left) {
            inputRef.current.left = false;
            changed = true;
          }
          break;
        case 'd':
          if (inputRef.current.right) {
            inputRef.current.right = false;
            changed = true;
          }
          break;
        case ' ':
          // DD-10: Reset dash state on release
          inputRef.current.dashPressed = false;
          inputRef.current.dashConsumed = false;
          break;
      }

      // Arrow key support
      if (enableArrows) {
        switch (event.key) {
          case 'ArrowUp':
            if (inputRef.current.up) {
              inputRef.current.up = false;
              changed = true;
            }
            break;
          case 'ArrowDown':
            if (inputRef.current.down) {
              inputRef.current.down = false;
              changed = true;
            }
            break;
          case 'ArrowLeft':
            if (inputRef.current.left) {
              inputRef.current.left = false;
              changed = true;
            }
            break;
          case 'ArrowRight':
            if (inputRef.current.right) {
              inputRef.current.right = false;
              changed = true;
            }
            break;
        }
      }

      if (changed && onInputChange) {
        onInputChange({ ...inputRef.current });
      }
    },
    [enableArrows, onInputChange]
  );

  // Handle blur (reset all keys when window loses focus)
  const handleBlur = useCallback(() => {
    inputRef.current = {
      up: false,
      down: false,
      left: false,
      right: false,
      dashPressed: false,
      dashConsumed: false,
    };
    if (onInputChange) {
      onInputChange({ ...inputRef.current });
    }
  }, [onInputChange]);

  // Set up event listeners
  useEffect(() => {
    window.addEventListener('keydown', handleKeyDown);
    window.addEventListener('keyup', handleKeyUp);
    window.addEventListener('blur', handleBlur);

    return () => {
      window.removeEventListener('keydown', handleKeyDown);
      window.removeEventListener('keyup', handleKeyUp);
      window.removeEventListener('blur', handleBlur);
    };
  }, [handleKeyDown, handleKeyUp, handleBlur]);

  return inputRef;
}

export default useInput;
