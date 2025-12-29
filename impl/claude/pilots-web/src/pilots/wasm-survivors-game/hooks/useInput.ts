/**
 * WASM Survivors - Input Hook
 *
 * Handles WASD keyboard input with < 1ms latency.
 * Uses event-driven approach (no polling) for responsiveness.
 *
 * @see DD-5: Fun Floor - Input < 16ms
 * @see DD-10: Dash - Space key triggers dash
 * @see Apex Strike - Space hold for lock phase, WASD for aim direction
 */

import { useRef, useEffect, useCallback } from 'react';
import type { InputState } from '../types';

// =============================================================================
// Types
// =============================================================================

// Extended input state with dash and Apex Strike support
export interface ExtendedInputState extends InputState {
  dashPressed: boolean;
  dashConsumed: boolean; // True after dash triggered, false on space release

  // Apex Strike support
  spaceDown: boolean;           // Is space currently held?
  spaceJustPressed: boolean;    // Did space just go down this frame?
  spaceJustReleased: boolean;   // Did space just come up this frame?
  spaceHoldDuration: number;    // How long has space been held (ms)
  spaceDownTimestamp: number;   // When space was pressed (for duration calc)
  aimDirection: { x: number; y: number }; // Current WASD aim direction
}

export interface UseInputOptions {
  /** Enable arrow keys as alternative to WASD */
  enableArrows?: boolean;
  /** Callback when input changes (optional) */
  onInputChange?: (input: InputState) => void;
}

export interface UseInputReturn {
  /** Ref to current input state */
  inputRef: React.RefObject<ExtendedInputState>;
  /**
   * Clear frame-specific flags (spaceJustPressed, spaceJustReleased).
   * Call this at the end of each game loop frame.
   */
  clearFrameFlags: () => void;
  /**
   * Update space hold duration. Call this each frame while processing input.
   * Only updates if space is currently held.
   */
  updateSpaceHoldDuration: () => void;
}

// =============================================================================
// Hook
// =============================================================================

export function useInput(options: UseInputOptions = {}): UseInputReturn {
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
    // Apex Strike fields
    spaceDown: false,
    spaceJustPressed: false,
    spaceJustReleased: false,
    spaceHoldDuration: 0,
    spaceDownTimestamp: 0,
    aimDirection: { x: 1, y: 0 }, // Default: right
  });

  // Track last aim direction to persist when no WASD pressed
  const lastAimRef = useRef<{ x: number; y: number }>({ x: 1, y: 0 });

  // Helper: Update aim direction based on current WASD state
  const updateAimDirection = useCallback(() => {
    const input = inputRef.current;
    let x = 0;
    let y = 0;

    if (input.left) x -= 1;
    if (input.right) x += 1;
    if (input.up) y -= 1;
    if (input.down) y += 1;

    // If any direction pressed, normalize and update
    if (x !== 0 || y !== 0) {
      const len = Math.sqrt(x * x + y * y);
      const normalized = { x: x / len, y: y / len };
      input.aimDirection = normalized;
      lastAimRef.current = normalized;
    } else {
      // No direction pressed, keep last aim
      input.aimDirection = lastAimRef.current;
    }
  }, []);

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
            updateAimDirection();
          }
          event.preventDefault();
          break;
        case 's':
          if (!inputRef.current.down) {
            inputRef.current.down = true;
            changed = true;
            updateAimDirection();
          }
          event.preventDefault();
          break;
        case 'a':
          if (!inputRef.current.left) {
            inputRef.current.left = true;
            changed = true;
            updateAimDirection();
          }
          event.preventDefault();
          break;
        case 'd':
          if (!inputRef.current.right) {
            inputRef.current.right = true;
            changed = true;
            updateAimDirection();
          }
          event.preventDefault();
          break;
        case ' ':
          // DD-10: Dash - space key triggers dash (only if not already consumed)
          if (!inputRef.current.dashPressed && !inputRef.current.dashConsumed) {
            inputRef.current.dashPressed = true;
            changed = true;
          }
          // Apex Strike: Track space press for lock phase
          if (!inputRef.current.spaceDown) {
            inputRef.current.spaceDown = true;
            inputRef.current.spaceJustPressed = true;
            inputRef.current.spaceDownTimestamp = performance.now();
            inputRef.current.spaceHoldDuration = 0;
            // Capture initial aim direction
            updateAimDirection();
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
              updateAimDirection();
            }
            event.preventDefault();
            break;
          case 'ArrowDown':
            if (!inputRef.current.down) {
              inputRef.current.down = true;
              changed = true;
              updateAimDirection();
            }
            event.preventDefault();
            break;
          case 'ArrowLeft':
            if (!inputRef.current.left) {
              inputRef.current.left = true;
              changed = true;
              updateAimDirection();
            }
            event.preventDefault();
            break;
          case 'ArrowRight':
            if (!inputRef.current.right) {
              inputRef.current.right = true;
              changed = true;
              updateAimDirection();
            }
            event.preventDefault();
            break;
        }
      }

      if (changed && onInputChange) {
        onInputChange({ ...inputRef.current });
      }
    },
    [enableArrows, onInputChange, updateAimDirection]
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
            updateAimDirection();
          }
          break;
        case 's':
          if (inputRef.current.down) {
            inputRef.current.down = false;
            changed = true;
            updateAimDirection();
          }
          break;
        case 'a':
          if (inputRef.current.left) {
            inputRef.current.left = false;
            changed = true;
            updateAimDirection();
          }
          break;
        case 'd':
          if (inputRef.current.right) {
            inputRef.current.right = false;
            changed = true;
            updateAimDirection();
          }
          break;
        case ' ':
          // DD-10: Reset dash state on release
          inputRef.current.dashPressed = false;
          inputRef.current.dashConsumed = false;
          // Apex Strike: Track space release
          if (inputRef.current.spaceDown) {
            inputRef.current.spaceDown = false;
            inputRef.current.spaceJustReleased = true;
            // Calculate final hold duration
            inputRef.current.spaceHoldDuration =
              performance.now() - inputRef.current.spaceDownTimestamp;
          }
          break;
      }

      // Arrow key support
      if (enableArrows) {
        switch (event.key) {
          case 'ArrowUp':
            if (inputRef.current.up) {
              inputRef.current.up = false;
              changed = true;
              updateAimDirection();
            }
            break;
          case 'ArrowDown':
            if (inputRef.current.down) {
              inputRef.current.down = false;
              changed = true;
              updateAimDirection();
            }
            break;
          case 'ArrowLeft':
            if (inputRef.current.left) {
              inputRef.current.left = false;
              changed = true;
              updateAimDirection();
            }
            break;
          case 'ArrowRight':
            if (inputRef.current.right) {
              inputRef.current.right = false;
              changed = true;
              updateAimDirection();
            }
            break;
        }
      }

      if (changed && onInputChange) {
        onInputChange({ ...inputRef.current });
      }
    },
    [enableArrows, onInputChange, updateAimDirection]
  );

  // Handle blur (reset all keys when window loses focus)
  const handleBlur = useCallback(() => {
    // Note: We keep lastAimRef so aim persists across focus changes
    inputRef.current = {
      up: false,
      down: false,
      left: false,
      right: false,
      dashPressed: false,
      dashConsumed: false,
      // Apex Strike reset
      spaceDown: false,
      spaceJustPressed: false,
      spaceJustReleased: false,
      spaceHoldDuration: 0,
      spaceDownTimestamp: 0,
      aimDirection: lastAimRef.current, // Preserve last aim
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

  // Clear frame-specific flags (call at end of each game loop frame)
  const clearFrameFlags = useCallback(() => {
    inputRef.current.spaceJustPressed = false;
    inputRef.current.spaceJustReleased = false;
  }, []);

  // Update space hold duration (call each frame while processing input)
  const updateSpaceHoldDuration = useCallback(() => {
    if (inputRef.current.spaceDown) {
      inputRef.current.spaceHoldDuration =
        performance.now() - inputRef.current.spaceDownTimestamp;
    }
  }, []);

  return {
    inputRef,
    clearFrameFlags,
    updateSpaceHoldDuration,
  };
}

export default useInput;
