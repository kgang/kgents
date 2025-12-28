/**
 * WASM Survivors - Debug Controls Hook
 *
 * Keyboard shortcuts for debug mode during manual testing.
 * Only active when ?debug=true is in the URL.
 *
 * Key Bindings:
 * - 1: Spawn basic enemy at center
 * - 2: Spawn fast enemy at center
 * - 3: Spawn tank enemy at center
 * - 4: Spawn spitter enemy at center
 * - 5: Spawn boss enemy at center
 * - i/I: Toggle invincibility
 * - n/N: Skip to next wave
 * - k/K: Kill all enemies
 * - l/L: Instant level up
 *
 * @see pilots/wasm-survivors-game/PROTO_SPEC.md
 */

import { useEffect, useState, useCallback } from 'react';

// =============================================================================
// Types
// =============================================================================

export interface UseDebugControlsResult {
  invincible: boolean;
  isDebugMode: boolean;
}

// =============================================================================
// Helpers
// =============================================================================

function isDebugMode(): boolean {
  if (typeof window === 'undefined') return false;
  return new URLSearchParams(window.location.search).get('debug') === 'true';
}

// =============================================================================
// Hook
// =============================================================================

/**
 * Debug controls hook - keyboard shortcuts for debug functions
 *
 * Call this hook in the main game component to enable keyboard shortcuts
 * that trigger DEBUG_* functions on the window object.
 */
export function useDebugControls(): UseDebugControlsResult {
  const [invincible, setInvincible] = useState(false);
  const debugMode = isDebugMode();

  const handleKeyDown = useCallback((e: KeyboardEvent) => {
    // Don't capture if typing in input/textarea
    if (e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement) {
      return;
    }

    // Canvas center coordinates (default game size)
    const centerX = 400;
    const centerY = 300;

    switch (e.key) {
      case '1':
        window.DEBUG_SPAWN?.('basic', { x: centerX, y: centerY });
        console.log('[DEBUG] Spawned basic enemy');
        break;

      case '2':
        window.DEBUG_SPAWN?.('fast', { x: centerX, y: centerY });
        console.log('[DEBUG] Spawned fast enemy');
        break;

      case '3':
        window.DEBUG_SPAWN?.('tank', { x: centerX, y: centerY });
        console.log('[DEBUG] Spawned tank enemy');
        break;

      case '4':
        window.DEBUG_SPAWN?.('spitter', { x: centerX, y: centerY });
        console.log('[DEBUG] Spawned spitter enemy');
        break;

      case '5':
        window.DEBUG_SPAWN?.('boss', { x: centerX, y: centerY });
        console.log('[DEBUG] Spawned boss enemy');
        break;

      case 'i':
      case 'I':
        setInvincible(prev => {
          const newInvincible = !prev;
          window.DEBUG_SET_INVINCIBLE?.(newInvincible);
          console.log(`[DEBUG] Invincibility: ${newInvincible ? 'ON' : 'OFF'}`);
          return newInvincible;
        });
        break;

      case 'n':
      case 'N':
        window.DEBUG_SKIP_WAVE?.();
        console.log('[DEBUG] Skipped to next wave');
        break;

      case 'k':
      case 'K':
        window.DEBUG_KILL_ALL_ENEMIES?.();
        console.log('[DEBUG] Killed all enemies');
        break;

      case 'l':
      case 'L':
        window.DEBUG_LEVEL_UP?.();
        console.log('[DEBUG] Triggered level up');
        break;

      default:
        // Not a debug key, ignore
        break;
    }
  }, []);

  useEffect(() => {
    if (!debugMode) return;

    // Log available keyboard shortcuts
    console.log('[DEBUG CONTROLS] Keyboard shortcuts enabled:');
    console.log('  1: Spawn basic enemy');
    console.log('  2: Spawn fast enemy');
    console.log('  3: Spawn tank enemy');
    console.log('  4: Spawn spitter enemy');
    console.log('  5: Spawn boss enemy');
    console.log('  i: Toggle invincibility');
    console.log('  n: Skip to next wave');
    console.log('  k: Kill all enemies');
    console.log('  l: Instant level up');

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [debugMode, handleKeyDown]);

  return {
    invincible,
    isDebugMode: debugMode,
  };
}

export default useDebugControls;
