/**
 * TEMPORAL DEBT - Helper Functions
 * "Borrow from the future. Pay it back."
 *
 * These functions help integrate TEMPORAL DEBT with the game loop.
 * The actual state management is in juice.ts JuiceSystem.
 */

import type { JuiceSystem } from './juice';
import { getEffectiveTimeScale, TEMPORAL_DEBT } from './juice';

// Re-export for convenient access
export { TEMPORAL_DEBT };

/**
 * Get the effective time scale for ENEMY updates only.
 * This is separate from the main time scale to allow:
 * - Player to move normally during temporal freeze
 * - Enemies to freeze (0x) or accelerate (2x) based on temporal debt phase
 *
 * TEMPORAL DEBT mechanic:
 * - During frozen phase: enemies at 0x (stopped), player at 1x (normal)
 * - During debt phase: enemies at 2x (fast), player at 1x (normal)
 *
 * @returns Time scale multiplier for enemy updates (0, 1, or 2)
 */
export function getEffectiveEnemyTimeScale(juice: JuiceSystem): number {
  // If temporal debt is active, use its time scale for enemies
  const temporalScale = juice.getTemporalEnemyTimeScale();
  if (temporalScale !== 1) {
    // During freeze (0x) or debt (2x), return the temporal scale
    return temporalScale;
  }

  // Otherwise, use the standard time scale (for clutch moments, freeze frames, etc.)
  return getEffectiveTimeScale(juice);
}

/**
 * Check if temporal debt freeze is currently active.
 * When active, enemies should not move or attack, but player can act freely.
 */
export function isTemporalDebtFreezeActive(juice: JuiceSystem): boolean {
  return juice.isTemporalFreezeActive();
}

/**
 * Process temporal debt input and state updates.
 * Call this at the start of each game loop frame.
 *
 * @param juice - The juice system
 * @param deltaTime - Time since last frame in ms
 * @param playerPos - Current player position
 * @param temporalDebtPressed - Whether Q key was just pressed
 * @returns true if temporal debt was just activated
 */
export function processTemporalDebtInput(
  juice: JuiceSystem,
  deltaTime: number,
  playerPos: { x: number; y: number },
  temporalDebtPressed: boolean
): boolean {
  // Update temporal debt state (handles phase transitions)
  juice.updateTemporalDebt(deltaTime, playerPos);

  // Check for activation
  if (temporalDebtPressed && juice.temporalDebt.active && juice.temporalDebt.phase === 'ready') {
    juice.activateTemporalDebt(playerPos);
    return true;
  }

  return false;
}

/**
 * Enable the temporal debt upgrade.
 * Call this when the player acquires the TEMPORAL_DEBT wild upgrade.
 */
export function enableTemporalDebt(juice: JuiceSystem): void {
  juice.temporalDebt.active = true;
  juice.temporalDebt.phase = 'ready';
  juice.temporalDebt.cooldownRemaining = 0;
  console.log('[TEMPORAL DEBT] Upgrade acquired! Press Q to freeze time.');
}

/**
 * Check if temporal debt can be activated right now.
 */
export function canActivateTemporalDebt(juice: JuiceSystem): boolean {
  return (
    juice.temporalDebt.active &&
    juice.temporalDebt.phase === 'ready' &&
    juice.temporalDebt.cooldownRemaining <= 0
  );
}

/**
 * Get current temporal debt phase for UI display.
 */
export function getTemporalDebtPhase(juice: JuiceSystem): 'ready' | 'frozen' | 'debt' | 'cooldown' | 'inactive' {
  if (!juice.temporalDebt.active) return 'inactive';
  return juice.temporalDebt.phase;
}

/**
 * Get cooldown progress (0-1) for UI display.
 */
export function getTemporalDebtCooldownProgress(juice: JuiceSystem): number {
  if (juice.temporalDebt.cooldownRemaining <= 0) return 1;
  return 1 - (juice.temporalDebt.cooldownRemaining / TEMPORAL_DEBT.COOLDOWN);
}

/**
 * Get phase progress (0-1) for UI display.
 */
export function getTemporalDebtPhaseProgress(juice: JuiceSystem): number {
  if (juice.temporalDebt.phase === 'frozen') {
    return 1 - (juice.temporalDebt.phaseTimeRemaining / TEMPORAL_DEBT.FREEZE_DURATION);
  }
  if (juice.temporalDebt.phase === 'debt') {
    return 1 - (juice.temporalDebt.phaseTimeRemaining / TEMPORAL_DEBT.DEBT_DURATION);
  }
  return 0;
}
