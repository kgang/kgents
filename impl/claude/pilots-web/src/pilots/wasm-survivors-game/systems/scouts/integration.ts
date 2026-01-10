/**
 * Scout Coordination System - Game Loop Integration
 *
 * Provides a clean interface for integrating the scout coordination system
 * into the main game loop alongside other systems (physics, formation, etc.)
 *
 * Usage in useGameLoop.ts:
 * 1. Create manager: scoutCoordRef.current = createScoutCoordinationManager()
 * 2. Each frame: const result = processScoutCoordination(...)
 * 3. Apply result: update enemies and emit events
 */

import type { Enemy, Vector2 } from '../../types';
import type {
  ScoutCoordinationManager,
  ScoutEvent,
  SoloFlankTelegraph,
  CoordinatedTelegraph,
} from './types';
import {
  updateScoutCoordinationSystem,
} from './coordination';

// Re-export for convenience
export { createScoutCoordinationManager } from './coordination';
export type { ScoutCoordinationManager, ScoutEvent, SoloFlankTelegraph, CoordinatedTelegraph };

// =============================================================================
// Integration Types
// =============================================================================

export interface ScoutCoordinationResult {
  /** Updated manager state (store in ref) */
  manager: ScoutCoordinationManager;

  /** Enemies modified by coordination (merge back into enemies array) */
  modifiedEnemies: Map<string, Enemy>;

  /** Total damage dealt to player this frame */
  damageToPlayer: number;

  /** Events emitted (for sound, juice, witness) */
  events: ScoutEvent[];

  /** Telegraph data for rendering */
  telegraphs: {
    solo: SoloFlankTelegraph[];
    coordinated: CoordinatedTelegraph[];
  };

  /** IDs of scouts currently under coordination control */
  coordinatedScoutIds: Set<string>;
}

// =============================================================================
// Main Integration Function
// =============================================================================

/**
 * Process scout coordination for the current frame
 *
 * Call this AFTER physics update but BEFORE formation update,
 * so scouts can choose between solo behavior and joining THE BALL.
 *
 * @param manager - Current scout coordination manager state
 * @param enemies - All enemies in the game
 * @param playerPos - Current player position
 * @param playerVelocity - Current player velocity (for flank angle calculation)
 * @param gameTime - Current game time in ms
 * @param deltaTime - Frame delta in ms
 * @param wave - Current wave number
 * @returns Result with updated state and effects
 */
export function processScoutCoordination(
  manager: ScoutCoordinationManager,
  enemies: Enemy[],
  playerPos: Vector2,
  playerVelocity: Vector2,
  gameTime: number,
  deltaTime: number,
  wave: number
): ScoutCoordinationResult {
  // Run the coordination system
  const result = updateScoutCoordinationSystem(
    manager,
    enemies,
    playerPos,
    playerVelocity,
    gameTime,
    deltaTime,
    wave
  );

  // Collect all scout IDs that are under coordination control
  const coordinatedScoutIds = new Set<string>();

  // Solo scouts
  for (const [scoutId] of result.manager.soloStates) {
    coordinatedScoutIds.add(scoutId);
  }

  // Coordinated scouts (in groups)
  for (const group of result.manager.groups.values()) {
    for (const scoutId of group.memberIds) {
      coordinatedScoutIds.add(scoutId);
    }
  }

  return {
    manager: result.manager,
    modifiedEnemies: result.modifiedScouts,
    damageToPlayer: result.totalDamage,
    events: result.events,
    telegraphs: result.telegraphs,
    coordinatedScoutIds,
  };
}

/**
 * Apply coordination results to the enemies array
 *
 * @param enemies - Current enemies array
 * @param modifiedEnemies - Modified enemies from coordination
 * @returns Updated enemies array
 */
export function applyScoutCoordinationToEnemies(
  enemies: Enemy[],
  modifiedEnemies: Map<string, Enemy>
): Enemy[] {
  if (modifiedEnemies.size === 0) return enemies;

  return enemies.map(enemy => {
    const modified = modifiedEnemies.get(enemy.id);
    return modified ?? enemy;
  });
}

/**
 * Check if a scout is currently under coordination control
 * (Used by physics system to skip default behavior)
 *
 * @param scoutId - ID of the scout to check
 * @param manager - Current coordination manager
 * @returns true if scout is being coordinated
 */
export function isScoutCoordinated(
  scoutId: string,
  manager: ScoutCoordinationManager
): boolean {
  // Check solo state
  if (manager.soloStates.has(scoutId)) {
    return true;
  }

  // Check if in any group
  for (const group of manager.groups.values()) {
    if (group.memberIds.includes(scoutId)) {
      return true;
    }
  }

  return false;
}

/**
 * Clean up coordination state for dead scouts
 *
 * @param manager - Current coordination manager
 * @param aliveScoutIds - Set of scout IDs that are still alive
 */
export function cleanupDeadScouts(
  manager: ScoutCoordinationManager,
  aliveScoutIds: Set<string>
): void {
  // Clean solo states
  for (const scoutId of manager.soloStates.keys()) {
    if (!aliveScoutIds.has(scoutId)) {
      manager.soloStates.delete(scoutId);
      manager.scoutStates.delete(scoutId);
      manager.scoutCooldowns.delete(scoutId);
    }
  }

  // Clean groups with dead members
  for (const [groupId, group] of manager.groups) {
    const aliveMembers = group.memberIds.filter(id => aliveScoutIds.has(id));

    if (aliveMembers.length < 3) {
      // Group no longer viable, dissolve
      manager.groups.delete(groupId);

      // Clear group references from scout states
      for (const scoutId of group.memberIds) {
        const state = manager.scoutStates.get(scoutId);
        if (state) {
          state.coordinationGroupId = null;
        }
      }
    } else {
      // Update group membership
      group.memberIds = aliveMembers;
    }
  }
}

// =============================================================================
// Event Handlers (for game loop)
// =============================================================================

/**
 * Process scout events for sound/juice effects
 *
 * @param events - Events from coordination system
 * @param callbacks - Callback functions for effects
 */
export function processScoutEvents(
  events: ScoutEvent[],
  callbacks: {
    onSoloAttack?: (scoutId: string, damage: number, position: Vector2) => void;
    onGroupForming?: (groupId: string, memberCount: number) => void;
    onGroupTelegraph?: (groupId: string, center: Vector2) => void;
    onArcAttack?: (groupId: string, scoutId: string, attackIndex: number) => void;
    onPlayerMarked?: (duration: number, damageBonus: number) => void;
    onGroupComplete?: (groupId: string) => void;
    onGroupDisrupted?: (groupId: string, reason: string) => void;
  }
): void {
  for (const event of events) {
    switch (event.type) {
      case 'solo_attack':
        callbacks.onSoloAttack?.(event.scoutId, event.damage, event.position);
        break;
      case 'group_forming':
        callbacks.onGroupForming?.(event.groupId, event.memberCount);
        break;
      case 'group_telegraph':
        callbacks.onGroupTelegraph?.(event.groupId, event.targetCenter);
        break;
      case 'arc_attack_wave':
        callbacks.onArcAttack?.(event.groupId, event.scoutId, event.attackIndex);
        break;
      case 'player_marked':
        callbacks.onPlayerMarked?.(event.duration, event.damageBonus);
        break;
      case 'group_complete':
        callbacks.onGroupComplete?.(event.groupId);
        break;
      case 'group_disrupted':
        callbacks.onGroupDisrupted?.(event.groupId, event.reason);
        break;
    }
  }
}
